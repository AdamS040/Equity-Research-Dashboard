"""
Dashboards module for Equity Research Dashboard
Provides functionality for creating comprehensive dashboard layouts,
multi-chart displays, and interactive dashboard components.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.offline import plot
import warnings
warnings.filterwarnings('ignore')


class DashboardGenerator:
    """Generate comprehensive dashboard layouts"""
    
    def __init__(self):
        pass
    
    def create_market_overview_dashboard(self, market_data: Dict) -> go.Figure:
        """
        Create a comprehensive market overview dashboard
        
        Args:
            market_data: Market indices and sector data
            
        Returns:
            Plotly figure with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Major Indices Performance', 'Sector Performance',
                'Market Breadth', 'Volatility Index',
                'Top Gainers', 'Top Losers'
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "indicator"}, {"type": "scatter"}],
                [{"type": "table"}, {"type": "table"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # Major Indices Performance
        if 'indices' in market_data:
            indices = market_data['indices']
            names = list(indices.keys())
            values = [indices[name]['value'] for name in names]
            changes = [indices[name]['changePercent'] for name in names]
            
            colors = ['green' if change >= 0 else 'red' for change in changes]
            
            fig.add_trace(
                go.Bar(
                    x=names,
                    y=changes,
                    marker_color=colors,
                    name='Index Changes',
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Sector Performance
        if 'sectors' in market_data:
            sectors = market_data['sectors']
            sector_names = [s['name'] for s in sectors]
            sector_changes = [s['change'] for s in sectors]
            
            colors = ['green' if change >= 0 else 'red' for change in sector_changes]
            
            fig.add_trace(
                go.Bar(
                    x=sector_names,
                    y=sector_changes,
                    marker_color=colors,
                    name='Sector Changes',
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Market Breadth Indicator
        if 'market_breadth' in market_data:
            breadth = market_data['market_breadth']
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=breadth.get('advancing', 0),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Advancing Stocks"},
                    delta={'reference': breadth.get('declining', 0)},
                    gauge={
                        'axis': {'range': [None, breadth.get('total', 100)]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, breadth.get('total', 100) * 0.5], 'color': "lightgray"},
                            {'range': [breadth.get('total', 100) * 0.5, breadth.get('total', 100)], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': breadth.get('total', 100) * 0.7
                        }
                    }
                ),
                row=2, col=1
            )
        
        # Volatility Index
        if 'vix' in market_data:
            vix_data = market_data['vix']
            fig.add_trace(
                go.Scatter(
                    x=vix_data.get('dates', []),
                    y=vix_data.get('values', []),
                    mode='lines',
                    name='VIX',
                    line=dict(color='purple'),
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Top Gainers Table
        if 'top_gainers' in market_data:
            gainers = market_data['top_gainers']
            if gainers:
                fig.add_trace(
                    go.Table(
                        header=dict(
                            values=['Symbol', 'Name', 'Price', 'Change %'],
                            fill_color='paleturquoise',
                            align='left'
                        ),
                        cells=dict(
                            values=[
                                [g['symbol'] for g in gainers],
                                [g['name'] for g in gainers],
                                [f"${g['price']:.2f}" for g in gainers],
                                [f"{g['changePercent']:.2f}%" for g in gainers]
                            ],
                            fill_color='lavender',
                            align='left'
                        )
                    ),
                    row=3, col=1
                )
        
        # Top Losers Table
        if 'top_losers' in market_data:
            losers = market_data['top_losers']
            if losers:
                fig.add_trace(
                    go.Table(
                        header=dict(
                            values=['Symbol', 'Name', 'Price', 'Change %'],
                            fill_color='paleturquoise',
                            align='left'
                        ),
                        cells=dict(
                            values=[
                                [l['symbol'] for l in losers],
                                [l['name'] for l in losers],
                                [f"${l['price']:.2f}" for l in losers],
                                [f"{l['changePercent']:.2f}%" for l in losers]
                            ],
                            fill_color='lavender',
                            align='left'
                        )
                    ),
                    row=3, col=2
                )
        
        fig.update_layout(
            title_text="Market Overview Dashboard",
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_stock_analysis_dashboard(self, stock_data: Dict) -> go.Figure:
        """
        Create a comprehensive stock analysis dashboard
        
        Args:
            stock_data: Stock price, technical, and fundamental data
            
        Returns:
            Plotly figure with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Price Chart', 'Volume',
                'Technical Indicators', 'Financial Metrics',
                'Risk Metrics', 'Valuation Metrics'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # Price Chart
        if 'price_data' in stock_data:
            price_data = stock_data['price_data']
            fig.add_trace(
                go.Scatter(
                    x=price_data.get('dates', []),
                    y=price_data.get('prices', []),
                    mode='lines',
                    name='Price',
                    line=dict(color='blue'),
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Volume Chart
        if 'volume_data' in stock_data:
            volume_data = stock_data['volume_data']
            fig.add_trace(
                go.Bar(
                    x=volume_data.get('dates', []),
                    y=volume_data.get('volumes', []),
                    name='Volume',
                    marker_color='lightblue',
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Technical Indicators
        if 'technical' in stock_data:
            tech_data = stock_data['technical']
            if 'rsi' in tech_data:
                fig.add_trace(
                    go.Scatter(
                        x=tech_data['rsi'].get('dates', []),
                        y=tech_data['rsi'].get('values', []),
                        mode='lines',
                        name='RSI',
                        line=dict(color='orange'),
                        showlegend=False
                    ),
                    row=2, col=1
                )
        
        # Financial Metrics Gauge
        if 'financial_metrics' in stock_data:
            fin_metrics = stock_data['financial_metrics']
            if 'roe' in fin_metrics:
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=fin_metrics['roe'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "ROE (%)"},
                        gauge={
                            'axis': {'range': [None, 50]},
                            'bar': {'color': "darkgreen"},
                            'steps': [
                                {'range': [0, 10], 'color': "lightgray"},
                                {'range': [10, 20], 'color': "gray"},
                                {'range': [20, 50], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 30
                            }
                        }
                    ),
                    row=2, col=2
                )
        
        # Risk Metrics
        if 'risk_metrics' in stock_data:
            risk_metrics = stock_data['risk_metrics']
            if 'beta' in risk_metrics:
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=risk_metrics['beta'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Beta"},
                        gauge={
                            'axis': {'range': [0, 3]},
                            'bar': {'color': "darkred"},
                            'steps': [
                                {'range': [0, 1], 'color': "lightgreen"},
                                {'range': [1, 2], 'color': "yellow"},
                                {'range': [2, 3], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 1.5
                            }
                        }
                    ),
                    row=3, col=1
                )
        
        # Valuation Metrics
        if 'valuation_metrics' in stock_data:
            val_metrics = stock_data['valuation_metrics']
            if 'pe_ratio' in val_metrics:
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=val_metrics['pe_ratio'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "P/E Ratio"},
                        gauge={
                            'axis': {'range': [0, 50]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 15], 'color': "lightgreen"},
                                {'range': [15, 25], 'color': "yellow"},
                                {'range': [25, 50], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 30
                            }
                        }
                    ),
                    row=3, col=2
                )
        
        fig.update_layout(
            title_text="Stock Analysis Dashboard",
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_portfolio_dashboard(self, portfolio_data: Dict) -> go.Figure:
        """
        Create a comprehensive portfolio dashboard
        
        Args:
            portfolio_data: Portfolio holdings and performance data
            
        Returns:
            Plotly figure with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Portfolio Performance', 'Asset Allocation',
                'Risk Metrics', 'Sector Exposure',
                'Top Holdings', 'Performance vs Benchmark'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # Portfolio Performance
        if 'performance' in portfolio_data:
            perf_data = portfolio_data['performance']
            fig.add_trace(
                go.Scatter(
                    x=perf_data.get('dates', []),
                    y=perf_data.get('values', []),
                    mode='lines',
                    name='Portfolio',
                    line=dict(color='blue'),
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Asset Allocation Pie Chart
        if 'allocation' in portfolio_data:
            alloc_data = portfolio_data['allocation']
            symbols = list(alloc_data.keys())
            weights = list(alloc_data.values())
            
            fig.add_trace(
                go.Pie(
                    labels=symbols,
                    values=weights,
                    name="Allocation",
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Risk Metrics
        if 'risk_metrics' in portfolio_data:
            risk_metrics = portfolio_data['risk_metrics']
            if 'sharpe_ratio' in risk_metrics:
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=risk_metrics['sharpe_ratio'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Sharpe Ratio"},
                        gauge={
                            'axis': {'range': [0, 3]},
                            'bar': {'color': "darkgreen"},
                            'steps': [
                                {'range': [0, 1], 'color': "lightgray"},
                                {'range': [1, 2], 'color': "lightgreen"},
                                {'range': [2, 3], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 1.5
                            }
                        }
                    ),
                    row=2, col=1
                )
        
        # Sector Exposure
        if 'sector_exposure' in portfolio_data:
            sector_data = portfolio_data['sector_exposure']
            sectors = list(sector_data.keys())
            exposures = list(sector_data.values())
            
            fig.add_trace(
                go.Bar(
                    x=sectors,
                    y=exposures,
                    name='Sector Exposure',
                    marker_color='lightblue',
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Top Holdings
        if 'holdings' in portfolio_data:
            holdings = portfolio_data['holdings']
            if holdings:
                symbols = [h['symbol'] for h in holdings[:10]]
                values = [h['marketValue'] for h in holdings[:10]]
                
                fig.add_trace(
                    go.Bar(
                        x=symbols,
                        y=values,
                        name='Top Holdings',
                        marker_color='green',
                        showlegend=False
                    ),
                    row=3, col=1
                )
        
        # Performance vs Benchmark
        if 'benchmark_comparison' in portfolio_data:
            bench_data = portfolio_data['benchmark_comparison']
            dates = bench_data.get('dates', [])
            portfolio_perf = bench_data.get('portfolio', [])
            benchmark_perf = bench_data.get('benchmark', [])
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=portfolio_perf,
                    mode='lines',
                    name='Portfolio',
                    line=dict(color='blue'),
                    showlegend=False
                ),
                row=3, col=2
            )
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=benchmark_perf,
                    mode='lines',
                    name='Benchmark',
                    line=dict(color='red'),
                    showlegend=False
                ),
                row=3, col=2
            )
        
        fig.update_layout(
            title_text="Portfolio Dashboard",
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_risk_dashboard(self, risk_data: Dict) -> go.Figure:
        """
        Create a comprehensive risk analysis dashboard
        
        Args:
            risk_data: Risk metrics and analysis data
            
        Returns:
            Plotly figure with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Price Volatility', 'Value at Risk',
                'Beta Analysis', 'Correlation Matrix',
                'Stress Test Results', 'Risk Metrics Summary'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "histogram"}],
                [{"type": "scatter"}, {"type": "heatmap"}],
                [{"type": "bar"}, {"type": "indicator"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        # Price Volatility
        if 'volatility' in risk_data:
            vol_data = risk_data['volatility']
            fig.add_trace(
                go.Scatter(
                    x=vol_data.get('dates', []),
                    y=vol_data.get('values', []),
                    mode='lines',
                    name='Volatility',
                    line=dict(color='red'),
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Value at Risk Distribution
        if 'var_distribution' in risk_data:
            var_data = risk_data['var_distribution']
            fig.add_trace(
                go.Histogram(
                    x=var_data.get('returns', []),
                    nbinsx=50,
                    name='Returns Distribution',
                    marker_color='lightblue',
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Beta Analysis
        if 'beta_analysis' in risk_data:
            beta_data = risk_data['beta_analysis']
            fig.add_trace(
                go.Scatter(
                    x=beta_data.get('market_returns', []),
                    y=beta_data.get('stock_returns', []),
                    mode='markers',
                    name='Beta Scatter',
                    marker=dict(color='blue', size=8),
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Correlation Matrix
        if 'correlation_matrix' in risk_data:
            corr_matrix = risk_data['correlation_matrix']
            if isinstance(corr_matrix, pd.DataFrame):
                fig.add_trace(
                    go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.index,
                        colorscale='RdBu',
                        showlegend=False
                    ),
                    row=2, col=2
                )
        
        # Stress Test Results
        if 'stress_test' in risk_data:
            stress_data = risk_data['stress_test']
            scenarios = list(stress_data.keys())
            impacts = list(stress_data.values())
            
            fig.add_trace(
                go.Bar(
                    x=scenarios,
                    y=impacts,
                    name='Stress Test Impact',
                    marker_color='orange',
                    showlegend=False
                ),
                row=3, col=1
            )
        
        # Risk Score Indicator
        if 'risk_score' in risk_data:
            risk_score = risk_data['risk_score']
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=risk_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Risk Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkred"},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgreen"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ),
                row=3, col=2
            )
        
        fig.update_layout(
            title_text="Risk Analysis Dashboard",
            height=800,
            showlegend=False
        )
        
        return fig


class DashboardLayout:
    """Define dashboard layouts and configurations"""
    
    @staticmethod
    def get_market_dashboard_config() -> Dict:
        """Get market dashboard configuration"""
        return {
            'layout': 'grid',
            'rows': 3,
            'cols': 2,
            'height': 800,
            'width': 1200,
            'title': 'Market Overview Dashboard',
            'theme': 'plotly_white'
        }
    
    @staticmethod
    def get_stock_dashboard_config() -> Dict:
        """Get stock analysis dashboard configuration"""
        return {
            'layout': 'grid',
            'rows': 3,
            'cols': 2,
            'height': 800,
            'width': 1200,
            'title': 'Stock Analysis Dashboard',
            'theme': 'plotly_white'
        }
    
    @staticmethod
    def get_portfolio_dashboard_config() -> Dict:
        """Get portfolio dashboard configuration"""
        return {
            'layout': 'grid',
            'rows': 3,
            'cols': 2,
            'height': 800,
            'width': 1200,
            'title': 'Portfolio Dashboard',
            'theme': 'plotly_white'
        }
    
    @staticmethod
    def get_risk_dashboard_config() -> Dict:
        """Get risk analysis dashboard configuration"""
        return {
            'layout': 'grid',
            'rows': 3,
            'cols': 2,
            'height': 800,
            'width': 1200,
            'title': 'Risk Analysis Dashboard',
            'theme': 'plotly_white'
        }
