"""
Report Generation Engine

This module provides the core functionality for generating dynamic reports
with template-based content creation, data binding, and export capabilities.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from jinja2 import Environment, BaseLoader, Template, TemplateError
import pandas as pd
import numpy as np

from ..models.portfolio import Portfolio, PortfolioHolding
from ..models.market_data import Stock, StockQuote, HistoricalData
from ..models.user import User
from ..services.market_data_service import MarketDataService
from ..services.portfolio_calculations import PortfolioCalculations
from ..services.analytics_engine import AnalyticsEngine
from ..utils.cache_service import CacheService

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Report type enumeration"""
    PORTFOLIO_PERFORMANCE = "portfolio_performance"
    RISK_ANALYSIS = "risk_analysis"
    DCF_ANALYSIS = "dcf_analysis"
    COMPARABLE_ANALYSIS = "comparable_analysis"
    MARKET_RESEARCH = "market_research"
    CUSTOM_ANALYSIS = "custom_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"
    SCHEDULED_UPDATE = "scheduled_update"


class ReportStatus(Enum):
    """Report status enumeration"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ExportFormat(Enum):
    """Export format enumeration"""
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"
    IMAGE = "image"
    CSV = "csv"
    JSON = "json"


@dataclass
class ReportTemplate:
    """Report template structure"""
    id: str
    name: str
    description: str
    type: ReportType
    version: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    author_id: Optional[str] = None


@dataclass
class ReportSection:
    """Report section structure"""
    id: str
    title: str
    type: str  # 'text', 'chart', 'table', 'metric', 'analysis'
    content: Dict[str, Any]
    order: int
    visible: bool = True
    conditional: Optional[Dict[str, Any]] = None


@dataclass
class ReportData:
    """Report data structure"""
    portfolio_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    analytics_data: Optional[Dict[str, Any]] = None
    custom_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ReportGenerationRequest:
    """Report generation request structure"""
    template_id: str
    portfolio_id: Optional[str] = None
    symbol: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    scheduled: bool = False
    export_formats: List[ExportFormat] = None


@dataclass
class ReportGenerationResult:
    """Report generation result structure"""
    report_id: str
    status: ReportStatus
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    generated_at: datetime
    processing_time: float
    error_message: Optional[str] = None
    exports: Optional[Dict[str, str]] = None


class ReportTemplateLoader(BaseLoader):
    """Custom Jinja2 template loader for report templates"""
    
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates
    
    def get_source(self, environment, template):
        if template in self.templates:
            source = self.templates[template]
            return source, None, lambda: True
        raise TemplateError(f"Template '{template}' not found")


class ReportEngine:
    """Core report generation engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.portfolio_calculations = PortfolioCalculations(db)
        self.analytics_engine = AnalyticsEngine(db)
        self.cache_service = CacheService()
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=ReportTemplateLoader({}),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['currency'] = self._format_currency
        self.jinja_env.filters['percentage'] = self._format_percentage
        self.jinja_env.filters['number'] = self._format_number
        self.jinja_env.filters['date'] = self._format_date
        
        # Initialize built-in templates
        self._initialize_builtin_templates()
    
    def _initialize_builtin_templates(self):
        """Initialize built-in report templates"""
        self.builtin_templates = {
            "portfolio_performance": self._get_portfolio_performance_template(),
            "risk_analysis": self._get_risk_analysis_template(),
            "dcf_analysis": self._get_dcf_analysis_template(),
            "comparable_analysis": self._get_comparable_analysis_template(),
            "market_research": self._get_market_research_template(),
            "executive_summary": self._get_executive_summary_template()
        }
    
    async def generate_report(self, request: ReportGenerationRequest) -> ReportGenerationResult:
        """Generate a report based on the request"""
        start_time = datetime.now()
        report_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting report generation: {report_id}")
            
            # Load template
            template = await self._load_template(request.template_id)
            if not template:
                raise ValueError(f"Template not found: {request.template_id}")
            
            # Collect data
            report_data = await self._collect_report_data(request)
            
            # Process template
            processed_content = await self._process_template(template, report_data, request.parameters)
            
            # Generate charts and visualizations
            processed_content = await self._generate_charts(processed_content, report_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ReportGenerationResult(
                report_id=report_id,
                status=ReportStatus.COMPLETED,
                content=processed_content,
                metadata={
                    "template_id": request.template_id,
                    "template_name": template.name,
                    "template_version": template.version,
                    "generated_by": request.user_id,
                    "portfolio_id": request.portfolio_id,
                    "symbol": request.symbol,
                    "parameters": request.parameters,
                    "scheduled": request.scheduled
                },
                generated_at=datetime.now(),
                processing_time=processing_time
            )
            
            logger.info(f"Report generation completed: {report_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Report generation failed: {report_id} - {str(e)}")
            
            return ReportGenerationResult(
                report_id=report_id,
                status=ReportStatus.FAILED,
                content={},
                metadata={},
                generated_at=datetime.now(),
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _load_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Load a report template"""
        # Check built-in templates first
        if template_id in self.builtin_templates:
            return self.builtin_templates[template_id]
        
        # TODO: Load from database
        # For now, return None if not found in built-in templates
        return None
    
    async def _collect_report_data(self, request: ReportGenerationRequest) -> ReportData:
        """Collect all necessary data for report generation"""
        report_data = ReportData()
        
        try:
            # Collect portfolio data if portfolio_id is provided
            if request.portfolio_id:
                portfolio_data = await self._collect_portfolio_data(request.portfolio_id)
                report_data.portfolio_data = portfolio_data
            
            # Collect market data if symbol is provided
            if request.symbol:
                market_data = await self._collect_market_data(request.symbol)
                report_data.market_data = market_data
            
            # Collect analytics data
            analytics_data = await self._collect_analytics_data(request)
            report_data.analytics_data = analytics_data
            
            # Add metadata
            report_data.metadata = {
                "generated_at": datetime.now().isoformat(),
                "timezone": "UTC",
                "data_sources": ["market_data", "portfolio_data", "analytics"]
            }
            
        except Exception as e:
            logger.error(f"Error collecting report data: {str(e)}")
            raise
        
        return report_data
    
    async def _collect_portfolio_data(self, portfolio_id: str) -> Dict[str, Any]:
        """Collect portfolio-specific data"""
        try:
            # Get portfolio from database
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                raise ValueError(f"Portfolio not found: {portfolio_id}")
            
            # Get portfolio metrics
            metrics = await self.portfolio_calculations.calculate_portfolio_metrics(portfolio_id)
            
            # Get performance data
            performance_data = await self.portfolio_calculations.get_performance_history(
                portfolio_id, 
                start_date=datetime.now() - timedelta(days=365),
                end_date=datetime.now()
            )
            
            # Get risk metrics
            risk_metrics = await self.portfolio_calculations.calculate_risk_metrics(portfolio_id)
            
            # Get allocation data
            allocation_data = await self.portfolio_calculations.calculate_asset_allocation(portfolio_id)
            
            return {
                "portfolio": asdict(portfolio),
                "metrics": metrics,
                "performance": performance_data,
                "risk": risk_metrics,
                "allocation": allocation_data,
                "holdings": [asdict(holding) for holding in portfolio.holdings]
            }
            
        except Exception as e:
            logger.error(f"Error collecting portfolio data: {str(e)}")
            raise
    
    async def _collect_market_data(self, symbol: str) -> Dict[str, Any]:
        """Collect market data for a symbol"""
        try:
            # Get stock information
            stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                raise ValueError(f"Stock not found: {symbol}")
            
            # Get current quote
            quote = await self.market_data_service.get_latest_quote(symbol)
            
            # Get historical data
            historical_data = await self.market_data_service.get_historical_data(
                symbol, 
                period="1y",
                interval="1d"
            )
            
            # Get financial metrics
            financial_metrics = await self.market_data_service.get_financial_metrics(symbol)
            
            return {
                "stock": asdict(stock),
                "quote": asdict(quote) if quote else None,
                "historical": [asdict(data) for data in historical_data],
                "financial_metrics": financial_metrics
            }
            
        except Exception as e:
            logger.error(f"Error collecting market data: {str(e)}")
            raise
    
    async def _collect_analytics_data(self, request: ReportGenerationRequest) -> Dict[str, Any]:
        """Collect analytics data"""
        try:
            analytics_data = {}
            
            # Get DCF analysis if symbol is provided
            if request.symbol:
                dcf_analysis = await self.analytics_engine.get_dcf_analysis(request.symbol)
                if dcf_analysis:
                    analytics_data["dcf"] = dcf_analysis
            
            # Get comparable analysis if symbol is provided
            if request.symbol:
                comparable_analysis = await self.analytics_engine.get_comparable_analysis(request.symbol)
                if comparable_analysis:
                    analytics_data["comparable"] = comparable_analysis
            
            # Get risk analysis
            if request.portfolio_id:
                risk_analysis = await self.analytics_engine.get_portfolio_risk_analysis(request.portfolio_id)
                if risk_analysis:
                    analytics_data["risk"] = risk_analysis
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error collecting analytics data: {str(e)}")
            raise
    
    async def _process_template(self, template: ReportTemplate, data: ReportData, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Process template with data"""
        try:
            # Create template context
            context = {
                "data": asdict(data),
                "parameters": parameters or {},
                "template": asdict(template),
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Process each section
            processed_sections = []
            for section in template.content.get("sections", []):
                processed_section = await self._process_section(section, context)
                if processed_section:
                    processed_sections.append(processed_section)
            
            return {
                "title": template.name,
                "type": template.type.value,
                "sections": processed_sections,
                "metadata": template.metadata,
                "generated_at": context["generated_at"]
            }
            
        except Exception as e:
            logger.error(f"Error processing template: {str(e)}")
            raise
    
    async def _process_section(self, section: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single section"""
        try:
            # Check conditional visibility
            if section.get("conditional"):
                if not self._evaluate_condition(section["conditional"], context):
                    return None
            
            # Process section content based on type
            section_type = section.get("type", "text")
            
            if section_type == "text":
                return await self._process_text_section(section, context)
            elif section_type == "chart":
                return await self._process_chart_section(section, context)
            elif section_type == "table":
                return await self._process_table_section(section, context)
            elif section_type == "metric":
                return await self._process_metric_section(section, context)
            elif section_type == "analysis":
                return await self._process_analysis_section(section, context)
            else:
                logger.warning(f"Unknown section type: {section_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing section: {str(e)}")
            return None
    
    async def _process_text_section(self, section: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a text section"""
        template_str = section.get("content", "")
        template = self.jinja_env.from_string(template_str)
        rendered_content = template.render(**context)
        
        return {
            "id": section.get("id"),
            "title": section.get("title"),
            "type": "text",
            "content": rendered_content,
            "order": section.get("order", 0)
        }
    
    async def _process_chart_section(self, section: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chart section"""
        return {
            "id": section.get("id"),
            "title": section.get("title"),
            "type": "chart",
            "chart_type": section.get("chart_type", "line"),
            "data_source": section.get("data_source"),
            "config": section.get("config", {}),
            "order": section.get("order", 0)
        }
    
    async def _process_table_section(self, section: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a table section"""
        return {
            "id": section.get("id"),
            "title": section.get("title"),
            "type": "table",
            "data_source": section.get("data_source"),
            "columns": section.get("columns", []),
            "config": section.get("config", {}),
            "order": section.get("order", 0)
        }
    
    async def _process_metric_section(self, section: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a metric section"""
        return {
            "id": section.get("id"),
            "title": section.get("title"),
            "type": "metric",
            "metrics": section.get("metrics", []),
            "layout": section.get("layout", "grid"),
            "order": section.get("order", 0)
        }
    
    async def _process_analysis_section(self, section: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analysis section"""
        return {
            "id": section.get("id"),
            "title": section.get("title"),
            "type": "analysis",
            "analysis_type": section.get("analysis_type"),
            "parameters": section.get("parameters", {}),
            "order": section.get("order", 0)
        }
    
    async def _generate_charts(self, content: Dict[str, Any], data: ReportData) -> Dict[str, Any]:
        """Generate charts and visualizations"""
        # This will be implemented in the chart generation service
        # For now, return content as-is
        return content
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a conditional expression"""
        try:
            # Simple condition evaluation
            # This can be extended to support more complex conditions
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if not field or not operator:
                return True
            
            # Get field value from context
            field_value = self._get_nested_value(context, field)
            
            # Evaluate condition
            if operator == "equals":
                return field_value == value
            elif operator == "not_equals":
                return field_value != value
            elif operator == "greater_than":
                return field_value > value
            elif operator == "less_than":
                return field_value < value
            elif operator == "exists":
                return field_value is not None
            elif operator == "not_exists":
                return field_value is None
            else:
                logger.warning(f"Unknown operator: {operator}")
                return True
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return True
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get a nested value from a dictionary using dot notation"""
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    # Custom Jinja2 filters
    def _format_currency(self, value: Union[int, float], currency: str = "USD") -> str:
        """Format a number as currency"""
        if value is None:
            return "N/A"
        return f"${value:,.2f}"
    
    def _format_percentage(self, value: Union[int, float], decimals: int = 2) -> str:
        """Format a number as percentage"""
        if value is None:
            return "N/A"
        return f"{value:.{decimals}f}%"
    
    def _format_number(self, value: Union[int, float], decimals: int = 2) -> str:
        """Format a number with specified decimals"""
        if value is None:
            return "N/A"
        return f"{value:,.{decimals}f}"
    
    def _format_date(self, value: Union[str, datetime], format: str = "%Y-%m-%d") -> str:
        """Format a date"""
        if value is None:
            return "N/A"
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)
    
    # Built-in template definitions
    def _get_portfolio_performance_template(self) -> ReportTemplate:
        """Get portfolio performance template"""
        return ReportTemplate(
            id="portfolio_performance",
            name="Portfolio Performance Report",
            description="Comprehensive portfolio performance analysis",
            type=ReportType.PORTFOLIO_PERFORMANCE,
            version="1.0",
            content={
                "sections": [
                    {
                        "id": "summary",
                        "title": "Portfolio Summary",
                        "type": "metric",
                        "order": 1,
                        "metrics": [
                            {"name": "Total Value", "source": "data.portfolio_data.metrics.total_value"},
                            {"name": "Total Return", "source": "data.portfolio_data.metrics.total_return"},
                            {"name": "Total Return %", "source": "data.portfolio_data.metrics.total_return_percent"},
                            {"name": "Day Change", "source": "data.portfolio_data.metrics.day_change"}
                        ]
                    },
                    {
                        "id": "performance_chart",
                        "title": "Performance Over Time",
                        "type": "chart",
                        "order": 2,
                        "chart_type": "line",
                        "data_source": "data.portfolio_data.performance"
                    },
                    {
                        "id": "holdings_table",
                        "title": "Holdings",
                        "type": "table",
                        "order": 3,
                        "data_source": "data.portfolio_data.holdings",
                        "columns": [
                            {"key": "symbol", "title": "Symbol"},
                            {"key": "shares", "title": "Shares"},
                            {"key": "market_value", "title": "Market Value"},
                            {"key": "unrealized_gain_percent", "title": "Gain %"}
                        ]
                    }
                ]
            },
            metadata={
                "category": "portfolio",
                "tags": ["performance", "holdings", "analysis"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _get_risk_analysis_template(self) -> ReportTemplate:
        """Get risk analysis template"""
        return ReportTemplate(
            id="risk_analysis",
            name="Risk Analysis Report",
            description="Comprehensive risk analysis and metrics",
            type=ReportType.RISK_ANALYSIS,
            version="1.0",
            content={
                "sections": [
                    {
                        "id": "risk_metrics",
                        "title": "Risk Metrics",
                        "type": "metric",
                        "order": 1,
                        "metrics": [
                            {"name": "Beta", "source": "data.analytics_data.risk.beta"},
                            {"name": "Volatility", "source": "data.analytics_data.risk.volatility"},
                            {"name": "Sharpe Ratio", "source": "data.analytics_data.risk.sharpe_ratio"},
                            {"name": "Max Drawdown", "source": "data.analytics_data.risk.max_drawdown"}
                        ]
                    }
                ]
            },
            metadata={
                "category": "risk",
                "tags": ["risk", "volatility", "metrics"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _get_dcf_analysis_template(self) -> ReportTemplate:
        """Get DCF analysis template"""
        return ReportTemplate(
            id="dcf_analysis",
            name="DCF Analysis Report",
            description="Discounted Cash Flow analysis",
            type=ReportType.DCF_ANALYSIS,
            version="1.0",
            content={
                "sections": [
                    {
                        "id": "dcf_summary",
                        "title": "DCF Summary",
                        "type": "metric",
                        "order": 1,
                        "metrics": [
                            {"name": "Fair Value", "source": "data.analytics_data.dcf.fair_value"},
                            {"name": "Current Price", "source": "data.market_data.quote.price"},
                            {"name": "Upside", "source": "data.analytics_data.dcf.upside"},
                            {"name": "Upside %", "source": "data.analytics_data.dcf.upside_percent"}
                        ]
                    }
                ]
            },
            metadata={
                "category": "valuation",
                "tags": ["dcf", "valuation", "analysis"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _get_comparable_analysis_template(self) -> ReportTemplate:
        """Get comparable analysis template"""
        return ReportTemplate(
            id="comparable_analysis",
            name="Comparable Analysis Report",
            description="Peer comparison and valuation analysis",
            type=ReportType.COMPARABLE_ANALYSIS,
            version="1.0",
            content={
                "sections": [
                    {
                        "id": "peer_comparison",
                        "title": "Peer Comparison",
                        "type": "table",
                        "order": 1,
                        "data_source": "data.analytics_data.comparable.peers",
                        "columns": [
                            {"key": "symbol", "title": "Symbol"},
                            {"key": "pe", "title": "P/E"},
                            {"key": "pb", "title": "P/B"},
                            {"key": "ps", "title": "P/S"},
                            {"key": "ev_ebitda", "title": "EV/EBITDA"}
                        ]
                    }
                ]
            },
            metadata={
                "category": "valuation",
                "tags": ["comparable", "peers", "valuation"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _get_market_research_template(self) -> ReportTemplate:
        """Get market research template"""
        return ReportTemplate(
            id="market_research",
            name="Market Research Report",
            description="Market analysis and research",
            type=ReportType.MARKET_RESEARCH,
            version="1.0",
            content={
                "sections": [
                    {
                        "id": "market_overview",
                        "title": "Market Overview",
                        "type": "text",
                        "order": 1,
                        "content": "Market analysis and trends..."
                    }
                ]
            },
            metadata={
                "category": "market",
                "tags": ["market", "research", "analysis"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _get_executive_summary_template(self) -> ReportTemplate:
        """Get executive summary template"""
        return ReportTemplate(
            id="executive_summary",
            name="Executive Summary Report",
            description="High-level executive summary",
            type=ReportType.EXECUTIVE_SUMMARY,
            version="1.0",
            content={
                "sections": [
                    {
                        "id": "summary",
                        "title": "Executive Summary",
                        "type": "text",
                        "order": 1,
                        "content": "Executive summary of key findings and recommendations..."
                    }
                ]
            },
            metadata={
                "category": "summary",
                "tags": ["executive", "summary", "overview"]
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
