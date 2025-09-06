"""
Report Management Service

This module provides comprehensive report lifecycle management including
storage, retrieval, versioning, sharing, and analytics.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from ..models.user import User
from ..utils.cache_service import CacheService
from .report_engine import ReportGenerationResult, ReportStatus, ReportType
from .export_service import ExportService, ExportFormat

logger = logging.getLogger(__name__)


class ReportAccessLevel(Enum):
    """Report access level enumeration"""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


class ReportShareType(Enum):
    """Report share type enumeration"""
    VIEW = "view"
    EDIT = "edit"
    COMMENT = "comment"


@dataclass
class ReportMetadata:
    """Report metadata structure"""
    id: str
    title: str
    description: str
    type: ReportType
    status: ReportStatus
    author_id: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    access_level: ReportAccessLevel = ReportAccessLevel.PRIVATE
    tags: List[str] = None
    version: str = "1.0"
    file_size: int = 0
    generation_time: float = 0.0
    export_count: int = 0
    view_count: int = 0
    share_count: int = 0


@dataclass
class ReportVersion:
    """Report version structure"""
    id: str
    report_id: str
    version: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    created_by: str
    change_summary: str
    is_current: bool = False


@dataclass
class ReportShare:
    """Report share structure"""
    id: str
    report_id: str
    share_token: str
    share_type: ReportShareType
    expires_at: Optional[datetime] = None
    password_protected: bool = False
    password_hash: Optional[str] = None
    allowed_recipients: List[str] = None
    created_at: datetime = None
    created_by: str = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class ReportComment:
    """Report comment structure"""
    id: str
    report_id: str
    user_id: str
    content: str
    section_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    is_resolved: bool = False
    parent_comment_id: Optional[str] = None


@dataclass
class ReportAnalytics:
    """Report analytics structure"""
    report_id: str
    total_views: int
    unique_viewers: int
    total_exports: int
    export_formats: Dict[str, int]
    view_duration_avg: float
    last_viewed: Optional[datetime] = None
    popular_sections: List[str] = None
    user_engagement: Dict[str, Any] = None


class ReportManagementService:
    """Service for managing report lifecycle"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService()
        self.export_service = ExportService()
        
        # In-memory storage for demo purposes
        # In production, this would be replaced with database storage
        self._reports = {}
        self._report_versions = {}
        self._report_shares = {}
        self._report_comments = {}
        self._report_analytics = {}
    
    async def create_report(
        self, 
        title: str, 
        description: str, 
        report_type: ReportType,
        author_id: str,
        content: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        access_level: ReportAccessLevel = ReportAccessLevel.PRIVATE
    ) -> ReportMetadata:
        """Create a new report"""
        try:
            report_id = str(uuid.uuid4())
            now = datetime.now()
            
            metadata = ReportMetadata(
                id=report_id,
                title=title,
                description=description,
                type=report_type,
                status=ReportStatus.DRAFT,
                author_id=author_id,
                created_at=now,
                updated_at=now,
                tags=tags or [],
                access_level=access_level
            )
            
            # Store report metadata
            self._reports[report_id] = metadata
            
            # Create initial version
            if content:
                await self._create_report_version(
                    report_id=report_id,
                    content=content,
                    created_by=author_id,
                    change_summary="Initial version"
                )
            
            logger.info(f"Created report: {report_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Report creation failed: {str(e)}")
            raise
    
    async def get_report(self, report_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a report by ID"""
        try:
            # Check cache first
            cache_key = f"report:{report_id}"
            cached_report = await self.cache_service.get(cache_key)
            if cached_report:
                return cached_report
            
            # Get from storage
            metadata = self._reports.get(report_id)
            if not metadata:
                return None
            
            # Check access permissions
            if not await self._check_report_access(metadata, user_id):
                return None
            
            # Get latest version
            latest_version = await self._get_latest_version(report_id)
            
            report_data = {
                "metadata": asdict(metadata),
                "content": latest_version.content if latest_version else {},
                "version": latest_version.version if latest_version else "1.0"
            }
            
            # Cache the result
            await self.cache_service.set(cache_key, report_data, ttl=3600)
            
            # Update analytics
            await self._update_view_analytics(report_id, user_id)
            
            return report_data
            
        except Exception as e:
            logger.error(f"Report retrieval failed: {str(e)}")
            raise
    
    async def update_report(
        self, 
        report_id: str, 
        updates: Dict[str, Any], 
        user_id: str,
        change_summary: str = "Updated report"
    ) -> Optional[ReportMetadata]:
        """Update a report"""
        try:
            metadata = self._reports.get(report_id)
            if not metadata:
                return None
            
            # Check permissions
            if not await self._check_edit_permissions(metadata, user_id):
                raise PermissionError("Insufficient permissions to edit report")
            
            # Update metadata
            if "title" in updates:
                metadata.title = updates["title"]
            if "description" in updates:
                metadata.description = updates["description"]
            if "tags" in updates:
                metadata.tags = updates["tags"]
            if "access_level" in updates:
                metadata.access_level = ReportAccessLevel(updates["access_level"])
            
            metadata.updated_at = datetime.now()
            
            # Update content if provided
            if "content" in updates:
                await self._create_report_version(
                    report_id=report_id,
                    content=updates["content"],
                    created_by=user_id,
                    change_summary=change_summary
                )
            
            # Clear cache
            cache_key = f"report:{report_id}"
            await self.cache_service.delete(cache_key)
            
            logger.info(f"Updated report: {report_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Report update failed: {str(e)}")
            raise
    
    async def delete_report(self, report_id: str, user_id: str) -> bool:
        """Delete a report"""
        try:
            metadata = self._reports.get(report_id)
            if not metadata:
                return False
            
            # Check permissions
            if not await self._check_delete_permissions(metadata, user_id):
                raise PermissionError("Insufficient permissions to delete report")
            
            # Delete report and related data
            del self._reports[report_id]
            
            # Delete versions
            if report_id in self._report_versions:
                del self._report_versions[report_id]
            
            # Delete shares
            if report_id in self._report_shares:
                del self._report_shares[report_id]
            
            # Delete comments
            if report_id in self._report_comments:
                del self._report_comments[report_id]
            
            # Delete analytics
            if report_id in self._report_analytics:
                del self._report_analytics[report_id]
            
            # Clear cache
            cache_key = f"report:{report_id}"
            await self.cache_service.delete(cache_key)
            
            logger.info(f"Deleted report: {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"Report deletion failed: {str(e)}")
            raise
    
    async def list_reports(
        self, 
        user_id: Optional[str] = None,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        access_level: Optional[ReportAccessLevel] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """List reports with filtering and pagination"""
        try:
            # Get all reports
            reports = list(self._reports.values())
            
            # Apply filters
            filtered_reports = []
            for report in reports:
                # Check access
                if not await self._check_report_access(report, user_id):
                    continue
                
                # Apply filters
                if report_type and report.type != report_type:
                    continue
                if status and report.status != status:
                    continue
                if access_level and report.access_level != access_level:
                    continue
                if tags and not any(tag in report.tags for tag in tags):
                    continue
                if search_query and search_query.lower() not in report.title.lower() and search_query.lower() not in report.description.lower():
                    continue
                
                filtered_reports.append(report)
            
            # Sort
            if sort_by == "title":
                filtered_reports.sort(key=lambda x: x.title, reverse=(sort_order == "desc"))
            elif sort_by == "created_at":
                filtered_reports.sort(key=lambda x: x.created_at, reverse=(sort_order == "desc"))
            elif sort_by == "updated_at":
                filtered_reports.sort(key=lambda x: x.updated_at, reverse=(sort_order == "desc"))
            elif sort_by == "view_count":
                filtered_reports.sort(key=lambda x: x.view_count, reverse=(sort_order == "desc"))
            
            # Paginate
            total = len(filtered_reports)
            start = (page - 1) * limit
            end = start + limit
            paginated_reports = filtered_reports[start:end]
            
            return {
                "reports": [asdict(report) for report in paginated_reports],
                "total": total,
                "page": page,
                "limit": limit,
                "has_next": end < total,
                "has_prev": page > 1
            }
            
        except Exception as e:
            logger.error(f"Report listing failed: {str(e)}")
            raise
    
    async def create_report_version(
        self, 
        report_id: str, 
        content: Dict[str, Any], 
        created_by: str,
        change_summary: str
    ) -> ReportVersion:
        """Create a new version of a report"""
        try:
            # Get current version
            current_version = await self._get_latest_version(report_id)
            new_version_number = "1.0"
            
            if current_version:
                # Increment version number
                version_parts = current_version.version.split('.')
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                new_version_number = f"{major}.{minor + 1}"
            
            version_id = str(uuid.uuid4())
            now = datetime.now()
            
            version = ReportVersion(
                id=version_id,
                report_id=report_id,
                version=new_version_number,
                content=content,
                metadata={},
                created_at=now,
                created_by=created_by,
                change_summary=change_summary,
                is_current=True
            )
            
            # Mark previous version as not current
            if current_version:
                current_version.is_current = False
            
            # Store new version
            if report_id not in self._report_versions:
                self._report_versions[report_id] = []
            self._report_versions[report_id].append(version)
            
            # Update report metadata
            metadata = self._reports.get(report_id)
            if metadata:
                metadata.version = new_version_number
                metadata.updated_at = now
            
            logger.info(f"Created report version: {version_id}")
            return version
            
        except Exception as e:
            logger.error(f"Report version creation failed: {str(e)}")
            raise
    
    async def get_report_versions(self, report_id: str) -> List[ReportVersion]:
        """Get all versions of a report"""
        try:
            return self._report_versions.get(report_id, [])
        except Exception as e:
            logger.error(f"Report versions retrieval failed: {str(e)}")
            raise
    
    async def restore_report_version(self, report_id: str, version_id: str, user_id: str) -> bool:
        """Restore a specific version of a report"""
        try:
            versions = self._report_versions.get(report_id, [])
            target_version = None
            
            for version in versions:
                if version.id == version_id:
                    target_version = version
                    break
            
            if not target_version:
                return False
            
            # Check permissions
            metadata = self._reports.get(report_id)
            if not metadata or not await self._check_edit_permissions(metadata, user_id):
                raise PermissionError("Insufficient permissions to restore version")
            
            # Create new version with restored content
            await self._create_report_version(
                report_id=report_id,
                content=target_version.content,
                created_by=user_id,
                change_summary=f"Restored from version {target_version.version}"
            )
            
            logger.info(f"Restored report version: {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Report version restoration failed: {str(e)}")
            raise
    
    async def share_report(
        self, 
        report_id: str, 
        share_type: ReportShareType,
        created_by: str,
        expires_at: Optional[datetime] = None,
        password_protected: bool = False,
        password: Optional[str] = None,
        allowed_recipients: Optional[List[str]] = None
    ) -> ReportShare:
        """Share a report"""
        try:
            # Check if report exists
            metadata = self._reports.get(report_id)
            if not metadata:
                raise ValueError("Report not found")
            
            # Check permissions
            if not await self._check_share_permissions(metadata, created_by):
                raise PermissionError("Insufficient permissions to share report")
            
            # Generate share token
            share_token = str(uuid.uuid4())
            
            share = ReportShare(
                id=str(uuid.uuid4()),
                report_id=report_id,
                share_token=share_token,
                share_type=share_type,
                expires_at=expires_at,
                password_protected=password_protected,
                password_hash=password,  # In production, hash the password
                allowed_recipients=allowed_recipients or [],
                created_at=datetime.now(),
                created_by=created_by
            )
            
            # Store share
            if report_id not in self._report_shares:
                self._report_shares[report_id] = []
            self._report_shares[report_id].append(share)
            
            # Update share count
            metadata.share_count += 1
            
            logger.info(f"Shared report: {report_id} with token: {share_token}")
            return share
            
        except Exception as e:
            logger.error(f"Report sharing failed: {str(e)}")
            raise
    
    async def get_shared_report(self, share_token: str, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a shared report by token"""
        try:
            # Find share
            share = None
            for report_id, shares in self._report_shares.items():
                for s in shares:
                    if s.share_token == share_token:
                        share = s
                        break
                if share:
                    break
            
            if not share:
                return None
            
            # Check expiration
            if share.expires_at and share.expires_at < datetime.now():
                return None
            
            # Check password
            if share.password_protected and share.password_hash != password:
                return None
            
            # Update access count
            share.access_count += 1
            share.last_accessed = datetime.now()
            
            # Get report
            report_data = await self.get_report(share.report_id)
            if report_data:
                report_data["share_info"] = asdict(share)
            
            return report_data
            
        except Exception as e:
            logger.error(f"Shared report retrieval failed: {str(e)}")
            raise
    
    async def add_report_comment(
        self, 
        report_id: str, 
        user_id: str, 
        content: str,
        section_id: Optional[str] = None,
        parent_comment_id: Optional[str] = None
    ) -> ReportComment:
        """Add a comment to a report"""
        try:
            # Check if report exists
            metadata = self._reports.get(report_id)
            if not metadata:
                raise ValueError("Report not found")
            
            comment = ReportComment(
                id=str(uuid.uuid4()),
                report_id=report_id,
                user_id=user_id,
                content=content,
                section_id=section_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                parent_comment_id=parent_comment_id
            )
            
            # Store comment
            if report_id not in self._report_comments:
                self._report_comments[report_id] = []
            self._report_comments[report_id].append(comment)
            
            logger.info(f"Added comment to report: {report_id}")
            return comment
            
        except Exception as e:
            logger.error(f"Report comment addition failed: {str(e)}")
            raise
    
    async def get_report_comments(self, report_id: str) -> List[ReportComment]:
        """Get all comments for a report"""
        try:
            return self._report_comments.get(report_id, [])
        except Exception as e:
            logger.error(f"Report comments retrieval failed: {str(e)}")
            raise
    
    async def get_report_analytics(self, report_id: str) -> Optional[ReportAnalytics]:
        """Get analytics for a report"""
        try:
            return self._report_analytics.get(report_id)
        except Exception as e:
            logger.error(f"Report analytics retrieval failed: {str(e)}")
            raise
    
    async def export_report(
        self, 
        report_id: str, 
        export_format: ExportFormat,
        user_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Export a report in specified format"""
        try:
            # Get report
            report_data = await self.get_report(report_id, user_id)
            if not report_data:
                raise ValueError("Report not found")
            
            # Export using export service
            export_data = await self.export_service.export_report(
                report_data["content"], 
                export_format.value, 
                options
            )
            
            # Update export count
            metadata = self._reports.get(report_id)
            if metadata:
                metadata.export_count += 1
            
            logger.info(f"Exported report: {report_id} in format: {export_format.value}")
            return export_data
            
        except Exception as e:
            logger.error(f"Report export failed: {str(e)}")
            raise
    
    async def duplicate_report(
        self, 
        report_id: str, 
        new_title: str, 
        user_id: str
    ) -> ReportMetadata:
        """Duplicate a report"""
        try:
            # Get original report
            original_report = await self.get_report(report_id, user_id)
            if not original_report:
                raise ValueError("Original report not found")
            
            # Create new report
            new_report = await self.create_report(
                title=new_title,
                description=f"Copy of {original_report['metadata']['title']}",
                report_type=ReportType(original_report['metadata']['type']),
                author_id=user_id,
                content=original_report['content'],
                tags=original_report['metadata']['tags'],
                access_level=ReportAccessLevel.PRIVATE
            )
            
            logger.info(f"Duplicated report: {report_id} to {new_report.id}")
            return new_report
            
        except Exception as e:
            logger.error(f"Report duplication failed: {str(e)}")
            raise
    
    # Private helper methods
    async def _check_report_access(self, metadata: ReportMetadata, user_id: Optional[str]) -> bool:
        """Check if user has access to report"""
        if metadata.access_level == ReportAccessLevel.PUBLIC:
            return True
        if metadata.access_level == ReportAccessLevel.SHARED and user_id:
            return True
        if metadata.access_level == ReportAccessLevel.PRIVATE and user_id == metadata.author_id:
            return True
        return False
    
    async def _check_edit_permissions(self, metadata: ReportMetadata, user_id: str) -> bool:
        """Check if user can edit report"""
        return user_id == metadata.author_id
    
    async def _check_delete_permissions(self, metadata: ReportMetadata, user_id: str) -> bool:
        """Check if user can delete report"""
        return user_id == metadata.author_id
    
    async def _check_share_permissions(self, metadata: ReportMetadata, user_id: str) -> bool:
        """Check if user can share report"""
        return user_id == metadata.author_id
    
    async def _get_latest_version(self, report_id: str) -> Optional[ReportVersion]:
        """Get the latest version of a report"""
        versions = self._report_versions.get(report_id, [])
        current_versions = [v for v in versions if v.is_current]
        return current_versions[0] if current_versions else None
    
    async def _create_report_version(
        self, 
        report_id: str, 
        content: Dict[str, Any], 
        created_by: str,
        change_summary: str
    ) -> ReportVersion:
        """Create a new report version (internal method)"""
        return await self.create_report_version(report_id, content, created_by, change_summary)
    
    async def _update_view_analytics(self, report_id: str, user_id: Optional[str]):
        """Update view analytics for a report"""
        try:
            metadata = self._reports.get(report_id)
            if metadata:
                metadata.view_count += 1
            
            # Update detailed analytics
            if report_id not in self._report_analytics:
                self._report_analytics[report_id] = ReportAnalytics(
                    report_id=report_id,
                    total_views=0,
                    unique_viewers=0,
                    total_exports=0,
                    export_formats={},
                    view_duration_avg=0.0
                )
            
            analytics = self._report_analytics[report_id]
            analytics.total_views += 1
            analytics.last_viewed = datetime.now()
            
        except Exception as e:
            logger.error(f"Analytics update failed: {str(e)}")
    
    async def cleanup_expired_shares(self):
        """Clean up expired report shares"""
        try:
            now = datetime.now()
            for report_id, shares in self._report_shares.items():
                self._report_shares[report_id] = [
                    share for share in shares 
                    if not share.expires_at or share.expires_at > now
                ]
            
            logger.info("Cleaned up expired report shares")
            
        except Exception as e:
            logger.error(f"Share cleanup failed: {str(e)}")
    
    async def get_user_report_stats(self, user_id: str) -> Dict[str, Any]:
        """Get report statistics for a user"""
        try:
            user_reports = [r for r in self._reports.values() if r.author_id == user_id]
            
            stats = {
                "total_reports": len(user_reports),
                "published_reports": len([r for r in user_reports if r.status == ReportStatus.COMPLETED]),
                "draft_reports": len([r for r in user_reports if r.status == ReportStatus.DRAFT]),
                "total_views": sum(r.view_count for r in user_reports),
                "total_exports": sum(r.export_count for r in user_reports),
                "total_shares": sum(r.share_count for r in user_reports),
                "reports_by_type": {},
                "recent_reports": []
            }
            
            # Count by type
            for report in user_reports:
                report_type = report.type.value
                stats["reports_by_type"][report_type] = stats["reports_by_type"].get(report_type, 0) + 1
            
            # Recent reports (last 5)
            recent_reports = sorted(user_reports, key=lambda x: x.updated_at, reverse=True)[:5]
            stats["recent_reports"] = [asdict(r) for r in recent_reports]
            
            return stats
            
        except Exception as e:
            logger.error(f"User report stats failed: {str(e)}")
            raise
