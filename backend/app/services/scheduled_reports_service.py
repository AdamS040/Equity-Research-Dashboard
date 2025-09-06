"""
Scheduled Reports Service

This module provides functionality for scheduling and managing automated
report generation with various triggers and delivery methods.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from sqlalchemy.orm import Session
from celery import Celery
from celery.schedules import crontab

from ..models.user import User
from ..services.report_engine import ReportEngine, ReportGenerationRequest, ReportType
from ..services.report_management_service import ReportManagementService
from ..services.export_service import ExportService, ExportFormat
from ..utils.cache_service import CacheService

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Schedule frequency enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class DeliveryMethod(Enum):
    """Delivery method enumeration"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    STORAGE = "storage"
    DASHBOARD = "dashboard"


class ScheduleStatus(Enum):
    """Schedule status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduleConfig:
    """Schedule configuration structure"""
    frequency: ScheduleFrequency
    time: time  # Time of day to run
    day_of_week: Optional[int] = None  # 0-6 (Monday-Sunday)
    day_of_month: Optional[int] = None  # 1-31
    month: Optional[int] = None  # 1-12
    custom_cron: Optional[str] = None  # Custom cron expression
    timezone: str = "UTC"


@dataclass
class DeliveryConfig:
    """Delivery configuration structure"""
    method: DeliveryMethod
    email_recipients: Optional[List[str]] = None
    webhook_url: Optional[str] = None
    storage_path: Optional[str] = None
    email_subject: Optional[str] = None
    email_template: Optional[str] = None
    include_attachments: bool = True
    export_formats: List[ExportFormat] = None


@dataclass
class ScheduledReport:
    """Scheduled report structure"""
    id: str
    name: str
    description: str
    template_id: str
    portfolio_id: Optional[str] = None
    symbol: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule_config: ScheduleConfig
    delivery_config: DeliveryConfig
    status: ScheduleStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    error_message: Optional[str] = None


@dataclass
class ScheduleExecution:
    """Schedule execution record"""
    id: str
    schedule_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    report_id: Optional[str] = None
    error_message: Optional[str] = None
    delivery_status: Optional[Dict[str, Any]] = None


class ScheduledReportsService:
    """Service for managing scheduled reports"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService()
        self.report_engine = ReportEngine(db)
        self.report_management_service = ReportManagementService(db)
        self.export_service = ExportService()
        
        # In-memory storage for demo purposes
        # In production, this would be replaced with database storage
        self._schedules = {}
        self._executions = {}
        
        # Initialize Celery for background tasks
        self.celery_app = Celery('scheduled_reports')
        self.celery_app.config_from_object({
            'broker_url': 'redis://localhost:6379/0',
            'result_backend': 'redis://localhost:6379/0',
            'task_serializer': 'json',
            'accept_content': ['json'],
            'result_serializer': 'json',
            'timezone': 'UTC',
            'enable_utc': True,
        })
        
        # Register periodic tasks
        self._register_periodic_tasks()
    
    async def create_scheduled_report(
        self,
        name: str,
        description: str,
        template_id: str,
        schedule_config: ScheduleConfig,
        delivery_config: DeliveryConfig,
        created_by: str,
        portfolio_id: Optional[str] = None,
        symbol: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ScheduledReport:
        """Create a new scheduled report"""
        try:
            schedule_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Calculate next run time
            next_run = self._calculate_next_run(schedule_config, now)
            
            scheduled_report = ScheduledReport(
                id=schedule_id,
                name=name,
                description=description,
                template_id=template_id,
                portfolio_id=portfolio_id,
                symbol=symbol,
                parameters=parameters,
                schedule_config=schedule_config,
                delivery_config=delivery_config,
                status=ScheduleStatus.ACTIVE,
                created_by=created_by,
                created_at=now,
                updated_at=now,
                next_run=next_run
            )
            
            # Store schedule
            self._schedules[schedule_id] = scheduled_report
            
            # Schedule the task
            await self._schedule_task(scheduled_report)
            
            logger.info(f"Created scheduled report: {schedule_id}")
            return scheduled_report
            
        except Exception as e:
            logger.error(f"Scheduled report creation failed: {str(e)}")
            raise
    
    async def update_scheduled_report(
        self,
        schedule_id: str,
        updates: Dict[str, Any],
        user_id: str
    ) -> Optional[ScheduledReport]:
        """Update a scheduled report"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule:
                return None
            
            # Check permissions
            if schedule.created_by != user_id:
                raise PermissionError("Insufficient permissions to update schedule")
            
            # Update fields
            if "name" in updates:
                schedule.name = updates["name"]
            if "description" in updates:
                schedule.description = updates["description"]
            if "template_id" in updates:
                schedule.template_id = updates["template_id"]
            if "portfolio_id" in updates:
                schedule.portfolio_id = updates["portfolio_id"]
            if "symbol" in updates:
                schedule.symbol = updates["symbol"]
            if "parameters" in updates:
                schedule.parameters = updates["parameters"]
            if "schedule_config" in updates:
                schedule.schedule_config = ScheduleConfig(**updates["schedule_config"])
            if "delivery_config" in updates:
                schedule.delivery_config = DeliveryConfig(**updates["delivery_config"])
            if "status" in updates:
                schedule.status = ScheduleStatus(updates["status"])
            
            schedule.updated_at = datetime.now()
            
            # Recalculate next run if schedule changed
            if "schedule_config" in updates or "status" in updates:
                if schedule.status == ScheduleStatus.ACTIVE:
                    schedule.next_run = self._calculate_next_run(schedule.schedule_config, datetime.now())
                    await self._schedule_task(schedule)
                else:
                    schedule.next_run = None
            
            logger.info(f"Updated scheduled report: {schedule_id}")
            return schedule
            
        except Exception as e:
            logger.error(f"Scheduled report update failed: {str(e)}")
            raise
    
    async def delete_scheduled_report(self, schedule_id: str, user_id: str) -> bool:
        """Delete a scheduled report"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule:
                return False
            
            # Check permissions
            if schedule.created_by != user_id:
                raise PermissionError("Insufficient permissions to delete schedule")
            
            # Cancel the task
            await self._cancel_task(schedule_id)
            
            # Delete schedule
            del self._schedules[schedule_id]
            
            # Delete executions
            if schedule_id in self._executions:
                del self._executions[schedule_id]
            
            logger.info(f"Deleted scheduled report: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Scheduled report deletion failed: {str(e)}")
            raise
    
    async def get_scheduled_report(self, schedule_id: str, user_id: str) -> Optional[ScheduledReport]:
        """Get a scheduled report by ID"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule:
                return None
            
            # Check permissions
            if schedule.created_by != user_id:
                return None
            
            return schedule
            
        except Exception as e:
            logger.error(f"Scheduled report retrieval failed: {str(e)}")
            raise
    
    async def list_scheduled_reports(
        self,
        user_id: str,
        status: Optional[ScheduleStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """List scheduled reports for a user"""
        try:
            # Filter user's schedules
            user_schedules = [
                schedule for schedule in self._schedules.values()
                if schedule.created_by == user_id
            ]
            
            # Apply status filter
            if status:
                user_schedules = [
                    schedule for schedule in user_schedules
                    if schedule.status == status
                ]
            
            # Sort by next run time
            user_schedules.sort(key=lambda x: x.next_run or datetime.max)
            
            # Paginate
            total = len(user_schedules)
            start = (page - 1) * limit
            end = start + limit
            paginated_schedules = user_schedules[start:end]
            
            return {
                "schedules": [asdict(schedule) for schedule in paginated_schedules],
                "total": total,
                "page": page,
                "limit": limit,
                "has_next": end < total,
                "has_prev": page > 1
            }
            
        except Exception as e:
            logger.error(f"Scheduled reports listing failed: {str(e)}")
            raise
    
    async def execute_scheduled_report(self, schedule_id: str) -> ScheduleExecution:
        """Execute a scheduled report"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule:
                raise ValueError("Schedule not found")
            
            execution_id = str(uuid.uuid4())
            started_at = datetime.now()
            
            execution = ScheduleExecution(
                id=execution_id,
                schedule_id=schedule_id,
                started_at=started_at,
                status=ScheduleStatus.ACTIVE
            )
            
            # Store execution
            if schedule_id not in self._executions:
                self._executions[schedule_id] = []
            self._executions[schedule_id].append(execution)
            
            try:
                # Generate report
                generation_request = ReportGenerationRequest(
                    template_id=schedule.template_id,
                    portfolio_id=schedule.portfolio_id,
                    symbol=schedule.symbol,
                    parameters=schedule.parameters,
                    scheduled=True
                )
                
                result = await self.report_engine.generate_report(generation_request)
                
                if result.status.value == "completed":
                    execution.report_id = result.report_id
                    execution.status = ScheduleStatus.COMPLETED
                    schedule.success_count += 1
                    
                    # Deliver report
                    delivery_status = await self._deliver_report(
                        schedule.delivery_config,
                        result.content,
                        schedule.name
                    )
                    execution.delivery_status = delivery_status
                else:
                    execution.status = ScheduleStatus.FAILED
                    execution.error_message = result.error_message
                    schedule.failure_count += 1
                
            except Exception as e:
                execution.status = ScheduleStatus.FAILED
                execution.error_message = str(e)
                schedule.failure_count += 1
                logger.error(f"Report execution failed: {str(e)}")
            
            execution.completed_at = datetime.now()
            schedule.last_run = started_at
            schedule.run_count += 1
            
            # Calculate next run
            if schedule.status == ScheduleStatus.ACTIVE:
                schedule.next_run = self._calculate_next_run(
                    schedule.schedule_config,
                    execution.completed_at
                )
                await self._schedule_task(schedule)
            
            logger.info(f"Executed scheduled report: {schedule_id}")
            return execution
            
        except Exception as e:
            logger.error(f"Scheduled report execution failed: {str(e)}")
            raise
    
    async def pause_scheduled_report(self, schedule_id: str, user_id: str) -> bool:
        """Pause a scheduled report"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule:
                return False
            
            # Check permissions
            if schedule.created_by != user_id:
                raise PermissionError("Insufficient permissions to pause schedule")
            
            schedule.status = ScheduleStatus.PAUSED
            schedule.next_run = None
            schedule.updated_at = datetime.now()
            
            # Cancel the task
            await self._cancel_task(schedule_id)
            
            logger.info(f"Paused scheduled report: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Scheduled report pause failed: {str(e)}")
            raise
    
    async def resume_scheduled_report(self, schedule_id: str, user_id: str) -> bool:
        """Resume a scheduled report"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule:
                return False
            
            # Check permissions
            if schedule.created_by != user_id:
                raise PermissionError("Insufficient permissions to resume schedule")
            
            schedule.status = ScheduleStatus.ACTIVE
            schedule.next_run = self._calculate_next_run(schedule.schedule_config, datetime.now())
            schedule.updated_at = datetime.now()
            
            # Schedule the task
            await self._schedule_task(schedule)
            
            logger.info(f"Resumed scheduled report: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Scheduled report resume failed: {str(e)}")
            raise
    
    async def get_schedule_executions(
        self,
        schedule_id: str,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get execution history for a schedule"""
        try:
            schedule = self._schedules.get(schedule_id)
            if not schedule or schedule.created_by != user_id:
                return {"executions": [], "total": 0, "page": 1, "limit": limit}
            
            executions = self._executions.get(schedule_id, [])
            executions.sort(key=lambda x: x.started_at, reverse=True)
            
            # Paginate
            total = len(executions)
            start = (page - 1) * limit
            end = start + limit
            paginated_executions = executions[start:end]
            
            return {
                "executions": [asdict(execution) for execution in paginated_executions],
                "total": total,
                "page": page,
                "limit": limit,
                "has_next": end < total,
                "has_prev": page > 1
            }
            
        except Exception as e:
            logger.error(f"Schedule executions retrieval failed: {str(e)}")
            raise
    
    # Private helper methods
    def _calculate_next_run(self, schedule_config: ScheduleConfig, from_time: datetime) -> datetime:
        """Calculate the next run time based on schedule configuration"""
        try:
            now = from_time
            
            if schedule_config.frequency == ScheduleFrequency.DAILY:
                next_run = now.replace(
                    hour=schedule_config.time.hour,
                    minute=schedule_config.time.minute,
                    second=0,
                    microsecond=0
                )
                if next_run <= now:
                    next_run += timedelta(days=1)
            
            elif schedule_config.frequency == ScheduleFrequency.WEEKLY:
                days_ahead = schedule_config.day_of_week - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(
                    hour=schedule_config.time.hour,
                    minute=schedule_config.time.minute,
                    second=0,
                    microsecond=0
                )
            
            elif schedule_config.frequency == ScheduleFrequency.MONTHLY:
                next_run = now.replace(
                    day=schedule_config.day_of_month,
                    hour=schedule_config.time.hour,
                    minute=schedule_config.time.minute,
                    second=0,
                    microsecond=0
                )
                if next_run <= now:
                    # Move to next month
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
            
            elif schedule_config.frequency == ScheduleFrequency.QUARTERLY:
                # Run on the first day of each quarter
                quarter = (now.month - 1) // 3 + 1
                next_quarter_month = quarter * 3 - 2
                next_run = now.replace(
                    month=next_quarter_month,
                    day=1,
                    hour=schedule_config.time.hour,
                    minute=schedule_config.time.minute,
                    second=0,
                    microsecond=0
                )
                if next_run <= now:
                    if next_quarter_month == 10:  # Q4 -> Q1 next year
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=next_quarter_month + 3)
            
            elif schedule_config.frequency == ScheduleFrequency.YEARLY:
                next_run = now.replace(
                    month=1,
                    day=1,
                    hour=schedule_config.time.hour,
                    minute=schedule_config.time.minute,
                    second=0,
                    microsecond=0
                )
                if next_run <= now:
                    next_run = next_run.replace(year=now.year + 1)
            
            else:
                # Custom cron - simplified implementation
                next_run = now + timedelta(hours=1)
            
            return next_run
            
        except Exception as e:
            logger.error(f"Next run calculation failed: {str(e)}")
            return now + timedelta(hours=1)
    
    async def _schedule_task(self, schedule: ScheduledReport):
        """Schedule a Celery task for the report"""
        try:
            # This would integrate with Celery to schedule the task
            # For demo purposes, we'll just log it
            logger.info(f"Scheduled task for report: {schedule.id} at {schedule.next_run}")
            
        except Exception as e:
            logger.error(f"Task scheduling failed: {str(e)}")
    
    async def _cancel_task(self, schedule_id: str):
        """Cancel a scheduled Celery task"""
        try:
            # This would cancel the Celery task
            # For demo purposes, we'll just log it
            logger.info(f"Cancelled task for schedule: {schedule_id}")
            
        except Exception as e:
            logger.error(f"Task cancellation failed: {str(e)}")
    
    async def _deliver_report(
        self,
        delivery_config: DeliveryConfig,
        report_content: Dict[str, Any],
        report_name: str
    ) -> Dict[str, Any]:
        """Deliver a report using the specified method"""
        try:
            delivery_status = {}
            
            if delivery_config.method == DeliveryMethod.EMAIL:
                delivery_status = await self._deliver_via_email(
                    delivery_config, report_content, report_name
                )
            elif delivery_config.method == DeliveryMethod.WEBHOOK:
                delivery_status = await self._deliver_via_webhook(
                    delivery_config, report_content, report_name
                )
            elif delivery_config.method == DeliveryMethod.STORAGE:
                delivery_status = await self._deliver_via_storage(
                    delivery_config, report_content, report_name
                )
            elif delivery_config.method == DeliveryMethod.DASHBOARD:
                delivery_status = await self._deliver_via_dashboard(
                    delivery_config, report_content, report_name
                )
            
            return delivery_status
            
        except Exception as e:
            logger.error(f"Report delivery failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_via_email(
        self,
        delivery_config: DeliveryConfig,
        report_content: Dict[str, Any],
        report_name: str
    ) -> Dict[str, Any]:
        """Deliver report via email"""
        try:
            # This would implement email delivery
            # For demo purposes, we'll just log it
            logger.info(f"Delivered report '{report_name}' via email to {delivery_config.email_recipients}")
            
            return {
                "status": "success",
                "method": "email",
                "recipients": delivery_config.email_recipients,
                "delivered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Email delivery failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_via_webhook(
        self,
        delivery_config: DeliveryConfig,
        report_content: Dict[str, Any],
        report_name: str
    ) -> Dict[str, Any]:
        """Deliver report via webhook"""
        try:
            # This would implement webhook delivery
            # For demo purposes, we'll just log it
            logger.info(f"Delivered report '{report_name}' via webhook to {delivery_config.webhook_url}")
            
            return {
                "status": "success",
                "method": "webhook",
                "url": delivery_config.webhook_url,
                "delivered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Webhook delivery failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_via_storage(
        self,
        delivery_config: DeliveryConfig,
        report_content: Dict[str, Any],
        report_name: str
    ) -> Dict[str, Any]:
        """Deliver report via storage"""
        try:
            # This would implement storage delivery
            # For demo purposes, we'll just log it
            logger.info(f"Delivered report '{report_name}' to storage at {delivery_config.storage_path}")
            
            return {
                "status": "success",
                "method": "storage",
                "path": delivery_config.storage_path,
                "delivered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Storage delivery failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_via_dashboard(
        self,
        delivery_config: DeliveryConfig,
        report_content: Dict[str, Any],
        report_name: str
    ) -> Dict[str, Any]:
        """Deliver report via dashboard"""
        try:
            # This would implement dashboard delivery
            # For demo purposes, we'll just log it
            logger.info(f"Delivered report '{report_name}' to dashboard")
            
            return {
                "status": "success",
                "method": "dashboard",
                "delivered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard delivery failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _register_periodic_tasks(self):
        """Register periodic tasks with Celery"""
        try:
            # This would register periodic tasks for scheduled reports
            # For demo purposes, we'll just log it
            logger.info("Registered periodic tasks for scheduled reports")
            
        except Exception as e:
            logger.error(f"Periodic task registration failed: {str(e)}")
    
    async def cleanup_old_executions(self, days_to_keep: int = 30):
        """Clean up old execution records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for schedule_id, executions in self._executions.items():
                self._executions[schedule_id] = [
                    execution for execution in executions
                    if execution.started_at > cutoff_date
                ]
            
            logger.info(f"Cleaned up execution records older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Execution cleanup failed: {str(e)}")
    
    async def get_schedule_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for user's scheduled reports"""
        try:
            user_schedules = [
                schedule for schedule in self._schedules.values()
                if schedule.created_by == user_id
            ]
            
            stats = {
                "total_schedules": len(user_schedules),
                "active_schedules": len([s for s in user_schedules if s.status == ScheduleStatus.ACTIVE]),
                "paused_schedules": len([s for s in user_schedules if s.status == ScheduleStatus.PAUSED]),
                "total_executions": sum(s.run_count for s in user_schedules),
                "successful_executions": sum(s.success_count for s in user_schedules),
                "failed_executions": sum(s.failure_count for s in user_schedules),
                "success_rate": 0.0,
                "schedules_by_frequency": {},
                "recent_executions": []
            }
            
            # Calculate success rate
            total_executions = stats["total_executions"]
            if total_executions > 0:
                stats["success_rate"] = stats["successful_executions"] / total_executions
            
            # Count by frequency
            for schedule in user_schedules:
                freq = schedule.schedule_config.frequency.value
                stats["schedules_by_frequency"][freq] = stats["schedules_by_frequency"].get(freq, 0) + 1
            
            # Recent executions (last 10)
            all_executions = []
            for executions in self._executions.values():
                all_executions.extend(executions)
            
            recent_executions = sorted(
                all_executions,
                key=lambda x: x.started_at,
                reverse=True
            )[:10]
            
            stats["recent_executions"] = [asdict(execution) for execution in recent_executions]
            
            return stats
            
        except Exception as e:
            logger.error(f"Schedule statistics failed: {str(e)}")
            raise
