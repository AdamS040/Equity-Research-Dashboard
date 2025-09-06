"""
Chart Generation Service

This module provides comprehensive chart and visualization generation
for reports with support for multiple chart types and data sources.
"""

import asyncio
import io
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
import uuid

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder
import plotly.io as pio

from ..models.portfolio import Portfolio, PortfolioHolding
from ..models.market_data import Stock, StockQuote, HistoricalData
from ..utils.cache_service import CacheService

logger = logging.getLogger(__name__)


class ChartType:
    """Chart type constants"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    CANDLESTICK = "candlestick"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    WATERFALL = "waterfall"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    GAUGE = "gauge"
    INDICATOR = "indicator"


class ChartTheme:
    """Chart theme constants"""
    LIGHT = "light"
    DARK = "dark"
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"
    COLORFUL = "colorful"


class ChartGenerationService:
    """Service for generating charts and visualizations"""
    
    def __init__(self):
        self.cache_service = CacheService()
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Configure plotly
        pio.templates.default = "plotly_white"
    
    async def generate_chart(
        self, 
        chart_config: Dict[str, Any], 
        data: Dict[str, Any],
        format: str = "plotly"
    ) -> Dict[str, Any]:
        """Generate a chart based on configuration and data"""
        try:
            logger.info(f"Generating chart: {chart_config.get('type', 'unknown')}")
            
            chart_type = chart_config.get("type", ChartType.LINE)
            theme = chart_config.get("theme", ChartTheme.PROFESSIONAL)
            
            if format == "plotly":
                return await self._generate_plotly_chart(chart_config, data, theme)
            elif format == "matplotlib":
                return await self._generate_matplotlib_chart(chart_config, data, theme)
            else:
                raise ValueError(f"Unsupported chart format: {format}")
                
        except Exception as e:
            logger.error(f"Chart generation failed: {str(e)}")
            raise
    
    async def _generate_plotly_chart(
        self, 
        chart_config: Dict[str, Any], 
        data: Dict[str, Any],
        theme: str
    ) -> Dict[str, Any]:
        """Generate chart using Plotly"""
        try:
            chart_type = chart_config.get("type", ChartType.LINE)
            title = chart_config.get("title", "Chart")
            
            # Apply theme
            self._apply_plotly_theme(theme)
            
            if chart_type == ChartType.LINE:
                fig = await self._create_line_chart(chart_config, data)
            elif chart_type == ChartType.BAR:
                fig = await self._create_bar_chart(chart_config, data)
            elif chart_type == ChartType.PIE:
                fig = await self._create_pie_chart(chart_config, data)
            elif chart_type == ChartType.SCATTER:
                fig = await self._create_scatter_chart(chart_config, data)
            elif chart_type == ChartType.AREA:
                fig = await self._create_area_chart(chart_config, data)
            elif chart_type == ChartType.CANDLESTICK:
                fig = await self._create_candlestick_chart(chart_config, data)
            elif chart_type == ChartType.HEATMAP:
                fig = await self._create_heatmap_chart(chart_config, data)
            elif chart_type == ChartType.HISTOGRAM:
                fig = await self._create_histogram_chart(chart_config, data)
            elif chart_type == ChartType.BOX:
                fig = await self._create_box_chart(chart_config, data)
            elif chart_type == ChartType.VIOLIN:
                fig = await self._create_violin_chart(chart_config, data)
            elif chart_type == ChartType.WATERFALL:
                fig = await self._create_waterfall_chart(chart_config, data)
            elif chart_type == ChartType.TREEMAP:
                fig = await self._create_treemap_chart(chart_config, data)
            elif chart_type == ChartType.SANKEY:
                fig = await self._create_sankey_chart(chart_config, data)
            elif chart_type == ChartType.GAUGE:
                fig = await self._create_gauge_chart(chart_config, data)
            elif chart_type == ChartType.INDICATOR:
                fig = await self._create_indicator_chart(chart_config, data)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Update layout
            fig.update_layout(
                title=title,
                title_x=0.5,
                font=dict(size=12),
                margin=dict(l=50, r=50, t=50, b=50),
                showlegend=True
            )
            
            # Convert to JSON
            chart_json = json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
            
            return {
                "type": "plotly",
                "data": chart_json,
                "config": {
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"]
                }
            }
            
        except Exception as e:
            logger.error(f"Plotly chart generation failed: {str(e)}")
            raise
    
    async def _generate_matplotlib_chart(
        self, 
        chart_config: Dict[str, Any], 
        data: Dict[str, Any],
        theme: str
    ) -> Dict[str, Any]:
        """Generate chart using Matplotlib"""
        try:
            chart_type = chart_config.get("type", ChartType.LINE)
            title = chart_config.get("title", "Chart")
            
            # Apply theme
            self._apply_matplotlib_theme(theme)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if chart_type == ChartType.LINE:
                await self._create_matplotlib_line_chart(ax, chart_config, data)
            elif chart_type == ChartType.BAR:
                await self._create_matplotlib_bar_chart(ax, chart_config, data)
            elif chart_type == ChartType.PIE:
                await self._create_matplotlib_pie_chart(ax, chart_config, data)
            elif chart_type == ChartType.SCATTER:
                await self._create_matplotlib_scatter_chart(ax, chart_config, data)
            elif chart_type == ChartType.AREA:
                await self._create_matplotlib_area_chart(ax, chart_config, data)
            elif chart_type == ChartType.HISTOGRAM:
                await self._create_matplotlib_histogram_chart(ax, chart_config, data)
            else:
                raise ValueError(f"Unsupported matplotlib chart type: {chart_type}")
            
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Convert to base64
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return {
                "type": "matplotlib",
                "data": image_base64,
                "format": "png"
            }
            
        except Exception as e:
            logger.error(f"Matplotlib chart generation failed: {str(e)}")
            raise
    
    # Plotly chart creation methods
    async def _create_line_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create line chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: range(10),
                    y_column: np.random.randn(10).cumsum()
                })
            
            fig = go.Figure()
            
            # Add line trace
            fig.add_trace(go.Scatter(
                x=chart_data[x_column],
                y=chart_data[y_column],
                mode='lines+markers',
                name=config.get("name", "Line"),
                line=dict(
                    color=config.get("color", "#007acc"),
                    width=config.get("line_width", 2)
                ),
                marker=dict(
                    size=config.get("marker_size", 6),
                    color=config.get("marker_color", "#007acc")
                )
            ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Line chart creation failed: {str(e)}")
            raise
    
    async def _create_bar_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create bar chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: ['A', 'B', 'C', 'D', 'E'],
                    y_column: [20, 14, 23, 25, 22]
                })
            
            fig = go.Figure()
            
            # Add bar trace
            fig.add_trace(go.Bar(
                x=chart_data[x_column],
                y=chart_data[y_column],
                name=config.get("name", "Bar"),
                marker=dict(
                    color=config.get("color", "#007acc"),
                    line=dict(color='#000000', width=1)
                )
            ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Bar chart creation failed: {str(e)}")
            raise
    
    async def _create_pie_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create pie chart using Plotly"""
        try:
            data_source = config.get("data_source")
            labels_column = config.get("labels_column", "labels")
            values_column = config.get("values_column", "values")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    labels_column: ['A', 'B', 'C', 'D'],
                    values_column: [30, 25, 20, 25]
                })
            
            fig = go.Figure()
            
            # Add pie trace
            fig.add_trace(go.Pie(
                labels=chart_data[labels_column],
                values=chart_data[values_column],
                name=config.get("name", "Pie"),
                marker=dict(
                    colors=config.get("colors", px.colors.qualitative.Set3)
                )
            ))
            
            return fig
            
        except Exception as e:
            logger.error(f"Pie chart creation failed: {str(e)}")
            raise
    
    async def _create_scatter_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create scatter chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            size_column = config.get("size_column")
            color_column = config.get("color_column")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: np.random.randn(50),
                    y_column: np.random.randn(50),
                    size_column: np.random.randint(5, 20, 50) if size_column else None,
                    color_column: np.random.randint(0, 5, 50) if color_column else None
                })
            
            fig = go.Figure()
            
            # Add scatter trace
            scatter_kwargs = {
                "x": chart_data[x_column],
                "y": chart_data[y_column],
                "mode": "markers",
                "name": config.get("name", "Scatter"),
                "marker": dict(
                    color=config.get("color", "#007acc"),
                    size=config.get("marker_size", 8)
                )
            }
            
            if size_column and size_column in chart_data.columns:
                scatter_kwargs["marker"]["size"] = chart_data[size_column]
            
            if color_column and color_column in chart_data.columns:
                scatter_kwargs["marker"]["color"] = chart_data[color_column]
                scatter_kwargs["marker"]["colorscale"] = "Viridis"
                scatter_kwargs["marker"]["showscale"] = True
            
            fig.add_trace(go.Scatter(**scatter_kwargs))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Scatter chart creation failed: {str(e)}")
            raise
    
    async def _create_area_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create area chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: range(10),
                    y_column: np.random.randn(10).cumsum()
                })
            
            fig = go.Figure()
            
            # Add area trace
            fig.add_trace(go.Scatter(
                x=chart_data[x_column],
                y=chart_data[y_column],
                mode='lines',
                fill='tonexty' if config.get("stacked") else 'tozeroy',
                name=config.get("name", "Area"),
                line=dict(
                    color=config.get("color", "#007acc"),
                    width=2
                ),
                fillcolor=config.get("fill_color", "rgba(0, 122, 204, 0.3)")
            ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Area chart creation failed: {str(e)}")
            raise
    
    async def _create_candlestick_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create candlestick chart using Plotly"""
        try:
            data_source = config.get("data_source")
            date_column = config.get("date_column", "date")
            open_column = config.get("open_column", "open")
            high_column = config.get("high_column", "high")
            low_column = config.get("low_column", "low")
            close_column = config.get("close_column", "close")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample OHLC data
                dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
                base_price = 100
                prices = []
                for i in range(30):
                    change = np.random.randn() * 2
                    open_price = base_price + change
                    high_price = open_price + abs(np.random.randn() * 3)
                    low_price = open_price - abs(np.random.randn() * 3)
                    close_price = open_price + np.random.randn() * 2
                    prices.append([open_price, high_price, low_price, close_price])
                    base_price = close_price
                
                chart_data = pd.DataFrame(prices, columns=[open_column, high_column, low_column, close_column])
                chart_data[date_column] = dates
            
            fig = go.Figure()
            
            # Add candlestick trace
            fig.add_trace(go.Candlestick(
                x=chart_data[date_column],
                open=chart_data[open_column],
                high=chart_data[high_column],
                low=chart_data[low_column],
                close=chart_data[close_column],
                name=config.get("name", "Candlestick")
            ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", "Date"))
            fig.update_yaxes(title_text=config.get("y_title", "Price"))
            
            return fig
            
        except Exception as e:
            logger.error(f"Candlestick chart creation failed: {str(e)}")
            raise
    
    async def _create_heatmap_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create heatmap chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            z_column = config.get("z_column", "z")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample heatmap data
                x_values = ['A', 'B', 'C', 'D', 'E']
                y_values = ['X', 'Y', 'Z']
                z_values = np.random.randn(len(y_values), len(x_values))
                
                fig = go.Figure(data=go.Heatmap(
                    z=z_values,
                    x=x_values,
                    y=y_values,
                    colorscale='Viridis'
                ))
            else:
                # Pivot data for heatmap
                pivot_data = chart_data.pivot_table(
                    values=z_column, 
                    index=y_column, 
                    columns=x_column, 
                    aggfunc='mean'
                )
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    colorscale=config.get("colorscale", "Viridis")
                ))
            
            return fig
            
        except Exception as e:
            logger.error(f"Heatmap chart creation failed: {str(e)}")
            raise
    
    async def _create_histogram_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create histogram chart using Plotly"""
        try:
            data_source = config.get("data_source")
            column = config.get("column", "values")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    column: np.random.randn(1000)
                })
            
            fig = go.Figure()
            
            # Add histogram trace
            fig.add_trace(go.Histogram(
                x=chart_data[column],
                name=config.get("name", "Histogram"),
                nbinsx=config.get("bins", 30),
                marker=dict(
                    color=config.get("color", "#007acc"),
                    line=dict(color='#000000', width=1)
                )
            ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", column))
            fig.update_yaxes(title_text=config.get("y_title", "Frequency"))
            
            return fig
            
        except Exception as e:
            logger.error(f"Histogram chart creation failed: {str(e)}")
            raise
    
    async def _create_box_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create box chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column")
            y_column = config.get("y_column", "values")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'] if x_column else None,
                    y_column: np.random.randn(9)
                })
            
            fig = go.Figure()
            
            if x_column and x_column in chart_data.columns:
                # Grouped box plot
                for group in chart_data[x_column].unique():
                    group_data = chart_data[chart_data[x_column] == group][y_column]
                    fig.add_trace(go.Box(
                        y=group_data,
                        name=group,
                        boxpoints='outliers'
                    ))
            else:
                # Single box plot
                fig.add_trace(go.Box(
                    y=chart_data[y_column],
                    name=config.get("name", "Box Plot"),
                    boxpoints='outliers'
                ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column or ""))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Box chart creation failed: {str(e)}")
            raise
    
    async def _create_violin_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create violin chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column")
            y_column = config.get("y_column", "values")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'] if x_column else None,
                    y_column: np.random.randn(9)
                })
            
            fig = go.Figure()
            
            if x_column and x_column in chart_data.columns:
                # Grouped violin plot
                for group in chart_data[x_column].unique():
                    group_data = chart_data[chart_data[x_column] == group][y_column]
                    fig.add_trace(go.Violin(
                        y=group_data,
                        name=group,
                        box_visible=True,
                        meanline_visible=True
                    ))
            else:
                # Single violin plot
                fig.add_trace(go.Violin(
                    y=chart_data[y_column],
                    name=config.get("name", "Violin Plot"),
                    box_visible=True,
                    meanline_visible=True
                ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column or ""))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Violin chart creation failed: {str(e)}")
            raise
    
    async def _create_waterfall_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create waterfall chart using Plotly"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "category")
            y_column = config.get("y_column", "value")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample waterfall data
                chart_data = pd.DataFrame({
                    x_column: ['Start', 'Revenue', 'Costs', 'Taxes', 'End'],
                    y_column: [100, 50, -30, -10, 110]
                })
            
            fig = go.Figure()
            
            # Add waterfall trace
            fig.add_trace(go.Waterfall(
                x=chart_data[x_column],
                y=chart_data[y_column],
                name=config.get("name", "Waterfall"),
                measure=config.get("measure", ["absolute", "relative", "relative", "relative", "total"])
            ))
            
            # Update axes
            fig.update_xaxes(title_text=config.get("x_title", x_column))
            fig.update_yaxes(title_text=config.get("y_title", y_column))
            
            return fig
            
        except Exception as e:
            logger.error(f"Waterfall chart creation failed: {str(e)}")
            raise
    
    async def _create_treemap_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create treemap chart using Plotly"""
        try:
            data_source = config.get("data_source")
            labels_column = config.get("labels_column", "labels")
            values_column = config.get("values_column", "values")
            parents_column = config.get("parents_column", "parents")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample treemap data
                chart_data = pd.DataFrame({
                    labels_column: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                    values_column: [20, 15, 10, 8, 6, 4, 3, 2],
                    parents_column: ['', '', 'A', 'A', 'B', 'B', 'C', 'C']
                })
            
            fig = go.Figure()
            
            # Add treemap trace
            fig.add_trace(go.Treemap(
                labels=chart_data[labels_column],
                values=chart_data[values_column],
                parents=chart_data[parents_column],
                name=config.get("name", "Treemap")
            ))
            
            return fig
            
        except Exception as e:
            logger.error(f"Treemap chart creation failed: {str(e)}")
            raise
    
    async def _create_sankey_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create Sankey chart using Plotly"""
        try:
            data_source = config.get("data_source")
            source_column = config.get("source_column", "source")
            target_column = config.get("target_column", "target")
            value_column = config.get("value_column", "value")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample Sankey data
                chart_data = pd.DataFrame({
                    source_column: [0, 1, 0, 2, 3, 3],
                    target_column: [2, 3, 3, 4, 4, 5],
                    value_column: [8, 4, 2, 8, 4, 2]
                })
            
            fig = go.Figure()
            
            # Add Sankey trace
            fig.add_trace(go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=config.get("node_labels", ["A", "B", "C", "D", "E", "F"])
                ),
                link=dict(
                    source=chart_data[source_column],
                    target=chart_data[target_column],
                    value=chart_data[value_column]
                )
            ))
            
            return fig
            
        except Exception as e:
            logger.error(f"Sankey chart creation failed: {str(e)}")
            raise
    
    async def _create_gauge_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create gauge chart using Plotly"""
        try:
            data_source = config.get("data_source")
            value_column = config.get("value_column", "value")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                value = 75
            else:
                value = chart_data[value_column].iloc[0] if not chart_data.empty else 75
            
            fig = go.Figure()
            
            # Add gauge trace
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': config.get("title", "Gauge")},
                delta={'reference': config.get("reference", 50)},
                gauge={
                    'axis': {'range': [config.get("min", 0), config.get("max", 100)]},
                    'bar': {'color': config.get("color", "#007acc")},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': config.get("threshold", 90)
                    }
                }
            ))
            
            return fig
            
        except Exception as e:
            logger.error(f"Gauge chart creation failed: {str(e)}")
            raise
    
    async def _create_indicator_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> go.Figure:
        """Create indicator chart using Plotly"""
        try:
            data_source = config.get("data_source")
            value_column = config.get("value_column", "value")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                value = 75
            else:
                value = chart_data[value_column].iloc[0] if not chart_data.empty else 75
            
            fig = go.Figure()
            
            # Add indicator trace
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=value,
                title={'text': config.get("title", "Indicator")},
                delta={'reference': config.get("reference", 50)},
                number={'font': {'size': 40}}
            ))
            
            return fig
            
        except Exception as e:
            logger.error(f"Indicator chart creation failed: {str(e)}")
            raise
    
    # Matplotlib chart creation methods
    async def _create_matplotlib_line_chart(self, ax, config: Dict[str, Any], data: Dict[str, Any]):
        """Create line chart using Matplotlib"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: range(10),
                    y_column: np.random.randn(10).cumsum()
                })
            
            ax.plot(chart_data[x_column], chart_data[y_column], 
                   marker='o', linewidth=2, markersize=6)
            ax.set_xlabel(config.get("x_title", x_column))
            ax.set_ylabel(config.get("y_title", y_column))
            
        except Exception as e:
            logger.error(f"Matplotlib line chart creation failed: {str(e)}")
            raise
    
    async def _create_matplotlib_bar_chart(self, ax, config: Dict[str, Any], data: Dict[str, Any]):
        """Create bar chart using Matplotlib"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: ['A', 'B', 'C', 'D', 'E'],
                    y_column: [20, 14, 23, 25, 22]
                })
            
            ax.bar(chart_data[x_column], chart_data[y_column])
            ax.set_xlabel(config.get("x_title", x_column))
            ax.set_ylabel(config.get("y_title", y_column))
            
        except Exception as e:
            logger.error(f"Matplotlib bar chart creation failed: {str(e)}")
            raise
    
    async def _create_matplotlib_pie_chart(self, ax, config: Dict[str, Any], data: Dict[str, Any]):
        """Create pie chart using Matplotlib"""
        try:
            data_source = config.get("data_source")
            labels_column = config.get("labels_column", "labels")
            values_column = config.get("values_column", "values")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    labels_column: ['A', 'B', 'C', 'D'],
                    values_column: [30, 25, 20, 25]
                })
            
            ax.pie(chart_data[values_column], labels=chart_data[labels_column], 
                  autopct='%1.1f%%', startangle=90)
            
        except Exception as e:
            logger.error(f"Matplotlib pie chart creation failed: {str(e)}")
            raise
    
    async def _create_matplotlib_scatter_chart(self, ax, config: Dict[str, Any], data: Dict[str, Any]):
        """Create scatter chart using Matplotlib"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: np.random.randn(50),
                    y_column: np.random.randn(50)
                })
            
            ax.scatter(chart_data[x_column], chart_data[y_column], s=50, alpha=0.6)
            ax.set_xlabel(config.get("x_title", x_column))
            ax.set_ylabel(config.get("y_title", y_column))
            
        except Exception as e:
            logger.error(f"Matplotlib scatter chart creation failed: {str(e)}")
            raise
    
    async def _create_matplotlib_area_chart(self, ax, config: Dict[str, Any], data: Dict[str, Any]):
        """Create area chart using Matplotlib"""
        try:
            data_source = config.get("data_source")
            x_column = config.get("x_column", "x")
            y_column = config.get("y_column", "y")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    x_column: range(10),
                    y_column: np.random.randn(10).cumsum()
                })
            
            ax.fill_between(chart_data[x_column], chart_data[y_column], alpha=0.3)
            ax.plot(chart_data[x_column], chart_data[y_column], linewidth=2)
            ax.set_xlabel(config.get("x_title", x_column))
            ax.set_ylabel(config.get("y_title", y_column))
            
        except Exception as e:
            logger.error(f"Matplotlib area chart creation failed: {str(e)}")
            raise
    
    async def _create_matplotlib_histogram_chart(self, ax, config: Dict[str, Any], data: Dict[str, Any]):
        """Create histogram chart using Matplotlib"""
        try:
            data_source = config.get("data_source")
            column = config.get("column", "values")
            
            # Extract data
            chart_data = self._extract_data(data, data_source)
            
            if not chart_data or chart_data.empty:
                # Create sample data
                chart_data = pd.DataFrame({
                    column: np.random.randn(1000)
                })
            
            ax.hist(chart_data[column], bins=config.get("bins", 30), alpha=0.7, edgecolor='black')
            ax.set_xlabel(config.get("x_title", column))
            ax.set_ylabel(config.get("y_title", "Frequency"))
            
        except Exception as e:
            logger.error(f"Matplotlib histogram chart creation failed: {str(e)}")
            raise
    
    # Utility methods
    def _extract_data(self, data: Dict[str, Any], data_source: str) -> pd.DataFrame:
        """Extract data from data source"""
        try:
            if not data_source:
                return pd.DataFrame()
            
            # Navigate through nested data structure
            keys = data_source.split('.')
            current_data = data
            
            for key in keys:
                if isinstance(current_data, dict) and key in current_data:
                    current_data = current_data[key]
                else:
                    return pd.DataFrame()
            
            # Convert to DataFrame if it's a list of dictionaries
            if isinstance(current_data, list):
                if current_data and isinstance(current_data[0], dict):
                    return pd.DataFrame(current_data)
                else:
                    return pd.DataFrame({"values": current_data})
            elif isinstance(current_data, dict):
                return pd.DataFrame([current_data])
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            return pd.DataFrame()
    
    def _apply_plotly_theme(self, theme: str):
        """Apply theme to Plotly"""
        try:
            if theme == ChartTheme.DARK:
                pio.templates.default = "plotly_dark"
            elif theme == ChartTheme.MINIMAL:
                pio.templates.default = "plotly_white"
            elif theme == ChartTheme.PROFESSIONAL:
                pio.templates.default = "plotly_white"
            else:
                pio.templates.default = "plotly_white"
                
        except Exception as e:
            logger.error(f"Theme application failed: {str(e)}")
    
    def _apply_matplotlib_theme(self, theme: str):
        """Apply theme to Matplotlib"""
        try:
            if theme == ChartTheme.DARK:
                plt.style.use('dark_background')
            elif theme == ChartTheme.MINIMAL:
                plt.style.use('default')
            elif theme == ChartTheme.PROFESSIONAL:
                plt.style.use('seaborn-v0_8-whitegrid')
            else:
                plt.style.use('seaborn-v0_8')
                
        except Exception as e:
            logger.error(f"Theme application failed: {str(e)}")
    
    async def generate_dashboard_charts(self, dashboard_config: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple charts for a dashboard"""
        try:
            charts = []
            
            for chart_config in dashboard_config.get("charts", []):
                chart = await self.generate_chart(chart_config, data)
                charts.append(chart)
            
            return charts
            
        except Exception as e:
            logger.error(f"Dashboard chart generation failed: {str(e)}")
            raise
    
    async def get_chart_capabilities(self) -> Dict[str, Any]:
        """Get information about chart generation capabilities"""
        return {
            "supported_formats": ["plotly", "matplotlib"],
            "supported_types": [
                ChartType.LINE, ChartType.BAR, ChartType.PIE, ChartType.SCATTER,
                ChartType.AREA, ChartType.CANDLESTICK, ChartType.HEATMAP,
                ChartType.HISTOGRAM, ChartType.BOX, ChartType.VIOLIN,
                ChartType.WATERFALL, ChartType.TREEMAP, ChartType.SANKEY,
                ChartType.GAUGE, ChartType.INDICATOR
            ],
            "supported_themes": [
                ChartTheme.LIGHT, ChartTheme.DARK, ChartTheme.MINIMAL,
                ChartTheme.PROFESSIONAL, ChartTheme.COLORFUL
            ],
            "features": [
                "interactive_charts", "static_charts", "custom_styling",
                "multiple_data_sources", "responsive_design", "export_capabilities"
            ]
        }
