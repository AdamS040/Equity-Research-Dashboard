"""
Report API Endpoints

This module provides REST API endpoints for report generation, management,
export, sharing, and analytics.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from ....database import get_db
from ....auth.dependencies import get_current_user
from ....models.user import User
from ....services.report_engine import (
    ReportEngine, 
    ReportGenerationRequest, 
    ReportType, 
    ReportStatus,
    ExportFormat
)
from ....services.report_management_service import (
    ReportManagementService,
    ReportAccessLevel,
    ReportShareType
)
from ....services.export_service import ExportService
from ....services.chart_generation_service import ChartGenerationService
from ....utils.cache_service import CacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


# Pydantic models for request/response
class ReportCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    type: ReportType
    portfolio_id: Optional[str] = None
    symbol: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    access_level: ReportAccessLevel = ReportAccessLevel.PRIVATE

    @validator('parameters')
    def validate_parameters(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('Parameters must be a dictionary')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Tag length cannot exceed 50 characters')
        return v


class ReportUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    access_level: Optional[ReportAccessLevel] = None
    content: Optional[Dict[str, Any]] = None
    change_summary: Optional[str] = Field(None, max_length=500)

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Tag length cannot exceed 50 characters')
        return v


class ReportGenerateRequest(BaseModel):
    template_id: str = Field(..., min_length=1)
    portfolio_id: Optional[str] = None
    symbol: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    export_formats: Optional[List[ExportFormat]] = None

    @validator('export_formats')
    def validate_export_formats(cls, v):
        if v is not None and len(v) > 5:
            raise ValueError('Maximum 5 export formats allowed')
        return v


class ReportShareRequest(BaseModel):
    share_type: ReportShareType
    expires_at: Optional[datetime] = None
    password_protected: bool = False
    password: Optional[str] = Field(None, min_length=4, max_length=50)
    allowed_recipients: Optional[List[str]] = None

    @validator('allowed_recipients')
    def validate_recipients(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError('Maximum 100 recipients allowed')
        return v


class ReportCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    section_id: Optional[str] = None
    parent_comment_id: Optional[str] = None


class ReportListResponse(BaseModel):
    reports: List[Dict[str, Any]]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class ReportResponse(BaseModel):
    id: str
    title: str
    description: str
    type: str
    status: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    access_level: str
    tags: List[str]
    version: str
    file_size: int
    generation_time: float
    export_count: int
    view_count: int
    share_count: int


class ReportGenerationResponse(BaseModel):
    report_id: str
    status: str
    content: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]
    generated_at: datetime
    processing_time: float
    error_message: Optional[str] = None
    exports: Optional[Dict[str, str]] = None


class ReportShareResponse(BaseModel):
    id: str
    report_id: str
    share_token: str
    share_type: str
    expires_at: Optional[datetime] = None
    password_protected: bool
    allowed_recipients: List[str]
    created_at: datetime
    created_by: str
    access_count: int
    last_accessed: Optional[datetime] = None


class ReportCommentResponse(BaseModel):
    id: str
    report_id: str
    user_id: str
    content: str
    section_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_resolved: bool
    parent_comment_id: Optional[str] = None


class ReportAnalyticsResponse(BaseModel):
    report_id: str
    total_views: int
    unique_viewers: int
    total_exports: int
    export_formats: Dict[str, int]
    view_duration_avg: float
    last_viewed: Optional[datetime] = None
    popular_sections: Optional[List[str]] = None
    user_engagement: Optional[Dict[str, Any]] = None


# Dependency injection
def get_report_engine(db: Session = Depends(get_db)) -> ReportEngine:
    return ReportEngine(db)


def get_report_management_service(db: Session = Depends(get_db)) -> ReportManagementService:
    return ReportManagementService(db)


def get_export_service() -> ExportService:
    return ExportService()


def get_chart_generation_service() -> ChartGenerationService:
    return ChartGenerationService()


# Report CRUD endpoints
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Create a new report"""
    try:
        report = await report_service.create_report(
            title=request.title,
            description=request.description,
            report_type=request.type,
            author_id=current_user.id,
            tags=request.tags,
            access_level=request.access_level
        )
        
        return ReportResponse(**report.__dict__)
        
    except Exception as e:
        logger.error(f"Report creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service),
    report_type: Optional[ReportType] = Query(None),
    status: Optional[ReportStatus] = Query(None),
    access_level: Optional[ReportAccessLevel] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List reports with filtering and pagination"""
    try:
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        result = await report_service.list_reports(
            user_id=current_user.id,
            report_type=report_type,
            status=status,
            access_level=access_level,
            tags=tag_list,
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit
        )
        
        return ReportListResponse(**result)
        
    except Exception as e:
        logger.error(f"Report listing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reports"
        )


@router.get("/{report_id}", response_model=Dict[str, Any])
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Get a specific report"""
    try:
        report = await report_service.get_report(report_id, current_user.id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report"
        )


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    request: ReportUpdateRequest,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Update a report"""
    try:
        updates = request.dict(exclude_unset=True)
        report = await report_service.update_report(
            report_id=report_id,
            updates=updates,
            user_id=current_user.id,
            change_summary=request.change_summary or "Updated report"
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        return ReportResponse(**report.__dict__)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update report"
        )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Delete a report"""
    try:
        success = await report_service.delete_report(report_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )


# Report generation endpoints
@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    report_engine: ReportEngine = Depends(get_report_engine)
):
    """Generate a report from a template"""
    try:
        generation_request = ReportGenerationRequest(
            template_id=request.template_id,
            portfolio_id=request.portfolio_id,
            symbol=request.symbol,
            parameters=request.parameters,
            user_id=current_user.id,
            export_formats=request.export_formats
        )
        
        result = await report_engine.generate_report(generation_request)
        
        return ReportGenerationResponse(
            report_id=result.report_id,
            status=result.status.value,
            content=result.content,
            metadata=result.metadata,
            generated_at=result.generated_at,
            processing_time=result.processing_time,
            error_message=result.error_message,
            exports=result.exports
        )
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )


@router.post("/{report_id}/generate", response_model=ReportGenerationResponse)
async def regenerate_report(
    report_id: str,
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    report_engine: ReportEngine = Depends(get_report_engine),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Regenerate an existing report"""
    try:
        # Check if report exists and user has access
        existing_report = await report_service.get_report(report_id, current_user.id)
        if not existing_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        generation_request = ReportGenerationRequest(
            template_id=request.template_id,
            portfolio_id=request.portfolio_id,
            symbol=request.symbol,
            parameters=request.parameters,
            user_id=current_user.id,
            export_formats=request.export_formats
        )
        
        result = await report_engine.generate_report(generation_request)
        
        # Update the existing report with new content
        if result.status == ReportStatus.COMPLETED:
            await report_service.update_report(
                report_id=report_id,
                updates={"content": result.content},
                user_id=current_user.id,
                change_summary="Regenerated report"
            )
        
        return ReportGenerationResponse(
            report_id=result.report_id,
            status=result.status.value,
            content=result.content,
            metadata=result.metadata,
            generated_at=result.generated_at,
            processing_time=result.processing_time,
            error_message=result.error_message,
            exports=result.exports
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report regeneration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate report"
        )


# Export endpoints
@router.get("/{report_id}/export/{format}")
async def export_report(
    report_id: str,
    format: ExportFormat,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service),
    export_service: ExportService = Depends(get_export_service),
    options: Optional[str] = Query(None)
):
    """Export a report in specified format"""
    try:
        # Parse export options
        export_options = None
        if options:
            try:
                export_options = json.loads(options)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid export options format"
                )
        
        # Export the report
        export_data = await report_service.export_report(
            report_id=report_id,
            export_format=format,
            user_id=current_user.id,
            options=export_options
        )
        
        # Get file extension and MIME type
        file_extension = export_service._get_file_extension(format.value)
        mime_type = export_service._get_mime_type(format.value)
        
        # Create filename
        filename = f"report_{report_id}{file_extension}"
        
        # Return streaming response
        return StreamingResponse(
            io.BytesIO(export_data),
            media_type=mime_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report export failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export report"
        )


# Report versioning endpoints
@router.get("/{report_id}/versions")
async def get_report_versions(
    report_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Get all versions of a report"""
    try:
        versions = await report_service.get_report_versions(report_id)
        return {"versions": [version.__dict__ for version in versions]}
        
    except Exception as e:
        logger.error(f"Report versions retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report versions"
        )


@router.post("/{report_id}/versions/{version_id}/restore")
async def restore_report_version(
    report_id: str,
    version_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Restore a specific version of a report"""
    try:
        success = await report_service.restore_report_version(
            report_id=report_id,
            version_id=version_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        return {"message": "Version restored successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report version restoration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore report version"
        )


# Report sharing endpoints
@router.post("/{report_id}/share", response_model=ReportShareResponse)
async def share_report(
    report_id: str,
    request: ReportShareRequest,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Share a report"""
    try:
        share = await report_service.share_report(
            report_id=report_id,
            share_type=request.share_type,
            created_by=current_user.id,
            expires_at=request.expires_at,
            password_protected=request.password_protected,
            password=request.password,
            allowed_recipients=request.allowed_recipients
        )
        
        return ReportShareResponse(**share.__dict__)
        
    except Exception as e:
        logger.error(f"Report sharing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to share report"
        )


@router.get("/shared/{share_token}")
async def get_shared_report(
    share_token: str,
    password: Optional[str] = Query(None),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Get a shared report by token"""
    try:
        report = await report_service.get_shared_report(share_token, password)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared report not found or access denied"
            )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shared report retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shared report"
        )


# Report comments endpoints
@router.post("/{report_id}/comments", response_model=ReportCommentResponse)
async def add_report_comment(
    report_id: str,
    request: ReportCommentRequest,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Add a comment to a report"""
    try:
        comment = await report_service.add_report_comment(
            report_id=report_id,
            user_id=current_user.id,
            content=request.content,
            section_id=request.section_id,
            parent_comment_id=request.parent_comment_id
        )
        
        return ReportCommentResponse(**comment.__dict__)
        
    except Exception as e:
        logger.error(f"Report comment addition failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )


@router.get("/{report_id}/comments")
async def get_report_comments(
    report_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Get all comments for a report"""
    try:
        comments = await report_service.get_report_comments(report_id)
        return {"comments": [comment.__dict__ for comment in comments]}
        
    except Exception as e:
        logger.error(f"Report comments retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve comments"
        )


# Report analytics endpoints
@router.get("/{report_id}/analytics", response_model=ReportAnalyticsResponse)
async def get_report_analytics(
    report_id: str,
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Get analytics for a report"""
    try:
        analytics = await report_service.get_report_analytics(report_id)
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analytics not found"
            )
        
        return ReportAnalyticsResponse(**analytics.__dict__)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report analytics retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


# Report duplication endpoint
@router.post("/{report_id}/duplicate", response_model=ReportResponse)
async def duplicate_report(
    report_id: str,
    new_title: str = Query(..., min_length=1, max_length=200),
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Duplicate a report"""
    try:
        new_report = await report_service.duplicate_report(
            report_id=report_id,
            new_title=new_title,
            user_id=current_user.id
        )
        
        return ReportResponse(**new_report.__dict__)
        
    except Exception as e:
        logger.error(f"Report duplication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate report"
        )


# User report statistics endpoint
@router.get("/stats/user")
async def get_user_report_stats(
    current_user: User = Depends(get_current_user),
    report_service: ReportManagementService = Depends(get_report_management_service)
):
    """Get report statistics for the current user"""
    try:
        stats = await report_service.get_user_report_stats(current_user.id)
        return stats
        
    except Exception as e:
        logger.error(f"User report stats failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


# Chart generation endpoint
@router.post("/charts/generate")
async def generate_chart(
    chart_config: Dict[str, Any],
    data: Dict[str, Any],
    format: str = Query("plotly"),
    chart_service: ChartGenerationService = Depends(get_chart_generation_service)
):
    """Generate a chart"""
    try:
        chart = await chart_service.generate_chart(chart_config, data, format)
        return chart
        
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate chart"
        )


# Export format information endpoint
@router.get("/export/formats")
async def get_export_formats(
    export_service: ExportService = Depends(get_export_service)
):
    """Get information about available export formats"""
    try:
        formats = []
        for format_type in ExportFormat:
            info = await export_service.get_export_info(format_type.value)
            formats.append(info)
        
        return {"formats": formats}
        
    except Exception as e:
        logger.error(f"Export formats retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve export formats"
        )


# Chart capabilities endpoint
@router.get("/charts/capabilities")
async def get_chart_capabilities(
    chart_service: ChartGenerationService = Depends(get_chart_generation_service)
):
    """Get information about chart generation capabilities"""
    try:
        capabilities = await chart_service.get_chart_capabilities()
        return capabilities
        
    except Exception as e:
        logger.error(f"Chart capabilities retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chart capabilities"
        )
