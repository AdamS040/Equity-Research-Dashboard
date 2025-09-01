"""
Main application module for Equity Research Dashboard
"""
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import json
import time
import io
import base64
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Import custom modules
from data.market_data import MarketDataFetcher
from analysis.financial_metrics import FinancialAnalyzer
from analysis.valuation_models import DCFModel
from analysis.portfolio_optimizer import PortfolioOptimizer
from analysis.risk_analysis import RiskAnalyzer
from visualizations.charts import ChartGenerator
from models.comparable_analysis import ComparableAnalysis
from app.auth import AuthManager, init_auth_routes, create_login_layout, create_register_layout, create_profile_layout

def create_app(config_name='development'):
    """Create and configure the Dash application"""
    
    # Import configuration
    from config import config
    config_class = config.get(config_name, config['default'])
    
    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        suppress_callback_exceptions=True  # Add this to suppress callback exceptions
    )
    
    # Set Flask secret key for session management
    app.server.config['SECRET_KEY'] = config_class.SECRET_KEY
    app.server.config['DEBUG'] = config_class.DEBUG
    
    # Initialize authentication manager
    auth_manager = AuthManager(app.server)
    init_auth_routes(app.server, auth_manager)
    
    # Store auth_manager in app config for access in callbacks
    app.server.config['auth_manager'] = auth_manager
    
    # Initialize data services
    market_data = MarketDataFetcher()
    analyzer = FinancialAnalyzer()
    dcf_model = DCFModel()
    portfolio_optimizer = PortfolioOptimizer()
    risk_analyzer = RiskAnalyzer()
    chart_generator = ChartGenerator()
    comp_analysis = ComparableAnalysis()
    
    # App layout
    app.layout = dbc.Container([
        # Header with authentication
        dbc.NavbarSimple(
            brand="🏦 Equity Research Dashboard",
            brand_href="#",
            color="primary",
            dark=True,
            className="mb-4",
            children=[
                dbc.NavItem(dbc.NavLink("Dashboard", href="#dashboard")),
                dbc.NavItem(dbc.NavLink("Analysis", href="#analysis")),
                dbc.NavItem(dbc.NavLink("Portfolio", href="#portfolio")),
                dbc.NavItem(dbc.NavLink("Reports", href="#reports")),
                dbc.NavItem(dbc.NavLink("Profile", href="/auth/profile", external_link=True)),
                dbc.NavItem(dbc.NavLink("Login", href="/auth/login", external_link=True)),
                dbc.NavItem(dbc.NavLink("Logout", href="/auth/logout", external_link=True)),
            ]
        ),
        
        # Main content
        dcc.Tabs(id="main-tabs", value="dashboard", children=[
            # Dashboard Tab
            dcc.Tab(label="📊 Market Dashboard", value="dashboard", children=[
                html.Div(id="dashboard-content")
            ]),
            
            # Stock Analysis Tab  
            dcc.Tab(label="🔍 Stock Analysis", value="analysis", children=[
                html.Div(id="analysis-content")
            ]),
            
            # Portfolio Tab
            dcc.Tab(label="💼 Portfolio", value="portfolio", children=[
                html.Div(id="portfolio-content")
            ]),
            
            # Research Reports Tab
            dcc.Tab(label="📋 Research Reports", value="reports", children=[
                html.Div(id="reports-content")
            ])
        ]),
        
        # Store components for data
        dcc.Store(id="market-data-store"),
        dcc.Store(id="portfolio-data-store"),
        dcc.Store(id="analysis-data-store"),
        
        # Authentication status
        html.Div(id="auth-status"),
        
        # Interval component for real-time updates
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # 30 seconds
            n_intervals=0
        ),
        
    ], fluid=True)
    
    # Dashboard content layout
    def create_dashboard_layout():
        return [
            dbc.Row([
                # Market Overview Cards
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("S&P 500", className="card-title"),
                            html.H2(id="sp500-price", className="text-success"),
                            html.P(id="sp500-change", className="card-text"),
                        ])
                    ], color="light", className="mb-3")
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("NASDAQ", className="card-title"),
                            html.H2(id="nasdaq-price", className="text-info"),
                            html.P(id="nasdaq-change", className="card-text"),
                        ])
                    ], color="light", className="mb-3")
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("VIX", className="card-title"),
                            html.H2(id="vix-price", className="text-warning"),
                            html.P(id="vix-change", className="card-text"),
                        ])
                    ], color="light", className="mb-3")
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("10Y Treasury", className="card-title"),
                            html.H2(id="treasury-price", className="text-primary"),
                            html.P(id="treasury-change", className="card-text"),
                        ])
                    ], color="light", className="mb-3")
                ], width=3),
            ]),
            
            dbc.Row([
                # Market Charts
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Market Performance"),
                        dbc.CardBody([
                            dcc.Graph(id="market-performance-chart")
                        ])
                    ])
                ], width=8),
                
                # Top Movers
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H5("Top Movers", className="mb-0"),
                                dbc.Button([
                                    html.I(className="fas fa-sync-alt")
                                ], 
                                id="refresh-top-movers",
                                color="link", 
                                size="sm",
                                className="float-end")
                            ], className="d-flex justify-content-between align-items-center")
                        ]),
                        dbc.CardBody([
                            html.Div(id="top-movers-table")
                        ])
                    ])
                ], width=4),
            ]),
            
            dbc.Row([
                # Sector Performance
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Sector Performance"),
                        dbc.CardBody([
                            dcc.Graph(id="sector-performance-chart")
                        ])
                    ])
                ], width=12),
            ], className="mt-4"),
        ]
    
    # Stock Analysis content layout
    def create_analysis_layout():
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Stock Selection & Analysis"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Enter Stock Symbol:"),
                                    dbc.Input(
                                        id="stock-input",
                                        type="text",
                                        placeholder="e.g., AAPL",
                                        value="AAPL"
                                    ),
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Analysis Period:"),
                                    dcc.Dropdown(
                                        id="period-dropdown",
                                        options=[
                                            {'label': '1 Month', 'value': '1mo'},
                                            {'label': '3 Months', 'value': '3mo'},
                                            {'label': '6 Months', 'value': '6mo'},
                                            {'label': '1 Year', 'value': '1y'},
                                            {'label': '2 Years', 'value': '2y'},
                                            {'label': '5 Years', 'value': '5y'},
                                        ],
                                        value='1y'
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Br(),
                                    dbc.Button(
                                        "Analyze",
                                        id="analyze-button",
                                        color="primary",
                                        className="mt-2"
                                    )
                                ], width=2),
                            ])
                        ])
                    ])
                ], width=12),
            ]),
            
            # Analysis Results
            html.Div(id="stock-analysis-results", className="mt-4")
        ]
    
    # Portfolio content layout  
    def create_portfolio_layout():
        return [
            # Portfolio Configuration Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Portfolio Configuration"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Select Stocks (comma separated):"),
                                    dbc.Input(
                                        id="portfolio-stocks-input",
                                        type="text",
                                        placeholder="AAPL,GOOGL,MSFT,AMZN",
                                        value="AAPL,JPM,JNJ,PG,XOM"
                                    ),
                                    html.Small([
                                        html.I(className="bi bi-info-circle me-1"),
                                        "Tip: Include stocks from different sectors to avoid correlation issues and ensure proper portfolio optimization. The default portfolio is already diversified across sectors."
                                    ], className="text-muted mt-1 d-block"),
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Optimization Method:"),
                                    dcc.Dropdown(
                                        id="optimization-method",
                                        options=[
                                            {'label': 'Maximum Sharpe Ratio', 'value': 'max_sharpe'},
                                            {'label': 'Minimum Volatility', 'value': 'min_volatility'},
                                            {'label': 'Equal Weight', 'value': 'equal_weight'},
                                            {'label': 'Risk Parity', 'value': 'risk_parity'},
                                            {'label': 'Target Return', 'value': 'target_return'},
                                        ],
                                        value='max_sharpe'
                                    )
                                ], width=6),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Analysis Period:"),
                                    dcc.Dropdown(
                                        id="portfolio-period",
                                        options=[
                                            {'label': '6 Months', 'value': '6mo'},
                                            {'label': '1 Year', 'value': '1y'},
                                            {'label': '2 Years', 'value': '2y'},
                                            {'label': '5 Years', 'value': '5y'},
                                        ],
                                        value='1y'
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Target Return (%):", id="target-return-label"),
                                    dbc.Input(
                                        id="target-return-input",
                                        type="number",
                                        placeholder="12.5",
                                        step=0.1,
                                        style={"display": "none"}
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Risk-Free Rate (%):"),
                                    dbc.Input(
                                        id="risk-free-rate-input",
                                        type="number",
                                        placeholder="2.0",
                                        value=2.0,
                                        step=0.1
                                    )
                                ], width=3),
                                dbc.Col([
                                    dbc.Label("Rebalancing Frequency:"),
                                    dcc.Dropdown(
                                        id="rebalancing-frequency",
                                        options=[
                                            {'label': 'Monthly', 'value': 'monthly'},
                                            {'label': 'Quarterly', 'value': 'quarterly'},
                                            {'label': 'Annually', 'value': 'annually'},
                                        ],
                                        value='quarterly'
                                    )
                                ], width=3),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "Optimize Portfolio",
                                        id="optimize-button",
                                        color="success",
                                        size="lg",
                                        className="w-100"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Button(
                                        "Suggest Diverse Portfolio",
                                        id="suggest-diverse-button",
                                        color="info",
                                        size="lg",
                                        className="w-100"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Button(
                                        "Test Portfolio",
                                        id="test-portfolio-button",
                                        color="warning",
                                        size="lg",
                                        className="w-100"
                                    )
                                ], width=4),
                            ])
                        ])
                    ], className="portfolio-config-section")
                ], width=12),
            ]),
            
            # Portfolio Constraints Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Portfolio Constraints"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Maximum Weight per Stock (%):"),
                                    dbc.Input(
                                        id="max-weight-input",
                                        type="number",
                                        placeholder="40",
                                        value=40,
                                        step=1
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Minimum Weight per Stock (%):"),
                                    dbc.Input(
                                        id="min-weight-input",
                                        type="number",
                                        placeholder="1",
                                        value=1,
                                        step=1
                                    )
                                ], width=6),
                            ])
                        ])
                    ], className="portfolio-constraints-section")
                ], width=12),
            ], className="mt-3"),
            
            # Loading State
            html.Div(id="portfolio-loading", style={"display": "none"}, children=[
                dbc.Spinner(
                    html.Div([
                        html.H4("Optimizing Portfolio...", className="text-center mb-3"),
                        html.P("Please wait while we calculate the optimal portfolio allocation.", className="text-center text-muted")
                    ]),
                    color="primary",
                    size="lg"
                )
            ]),
            
            # Portfolio Results Section
            html.Div(id="portfolio-results", className="mt-4"),
            
            # Portfolio Comparison Section
            html.Div(id="portfolio-comparison", className="mt-4"),
            
            # Portfolio Export Section
            html.Div(id="portfolio-export", className="mt-4")
        ]
    
    # Reports content layout
    def create_reports_layout():
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Research Report Generator"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Stock Symbol:"),
                                    dbc.Input(
                                        id="report-stock-input",
                                        type="text",
                                        placeholder="AAPL",
                                        value="AAPL"
                                    ),
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Report Type:"),
                                    dcc.Dropdown(
                                        id="report-type",
                                        options=[
                                            {'label': 'Full Analysis', 'value': 'full'},
                                            {'label': 'Valuation Summary', 'value': 'valuation'},
                                            {'label': 'Risk Assessment', 'value': 'risk'},
                                            {'label': 'Peer Comparison', 'value': 'peer'},
                                        ],
                                        value='full'
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Br(),
                                    dbc.Button(
                                        "Generate Report",
                                        id="generate-report-button",
                                        color="info",
                                        className="mt-2"
                                    )
                                ], width=2),
                            ])
                        ])
                    ])
                ], width=12),
            ]),
            
            # Report Results
            html.Div(id="report-results", className="mt-4")
        ]
    
    # PDF Generation Function
    def generate_portfolio_pdf(result, symbols, method):
        """Generate a professional PDF report for portfolio analysis"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        normal_style = styles['Normal']
        
        # Title
        story.append(Paragraph("PORTFOLIO OPTIMIZATION REPORT", title_style))
        story.append(Spacer(1, 20))
        
        # Header information
        header_data = [
            ['Generated:', datetime.now().strftime('%B %d, %Y at %H:%M')],
            ['Optimization Method:', method.replace('_', ' ').title()],
            ['Portfolio Symbols:', ', '.join(symbols)],
            ['Number of Assets:', str(len(symbols))]
        ]
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Portfolio Allocation
        story.append(Paragraph("PORTFOLIO ALLOCATION", heading_style))
        if 'optimal_weights' in result:
            allocation_data = [['Symbol', 'Weight (%)']]
            total_weight = 0
            for symbol, weight in result['optimal_weights'].items():
                allocation_data.append([symbol, f"{weight:.2f}%"])
                total_weight += weight
            allocation_data.append(['Total', f"{total_weight:.2f}%"])
            
            allocation_table = Table(allocation_data, colWidths=[2*inch, 1.5*inch])
            allocation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(allocation_table)
        story.append(Spacer(1, 20))
        
        # Portfolio Metrics
        story.append(Paragraph("PORTFOLIO METRICS", heading_style))
        if 'portfolio_metrics' in result:
            metrics = result['portfolio_metrics']
            metrics_data = [
                ['Metric', 'Value'],
                ['Annual Return', f"{metrics.get('annual_return', 0):.2%}"],
                ['Annual Volatility', f"{metrics.get('annual_volatility', 0):.2%}"],
                ['Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.2f}"],
                ['Maximum Drawdown', f"{metrics.get('max_drawdown', 0):.2%}"],
                ['Value at Risk (5%)', f"{metrics.get('var_5_percent', 0):.2%}"],
                ['Value at Risk (1%)', f"{metrics.get('var_1_percent', 0):.2%}"],
                ['Sortino Ratio', f"{metrics.get('sortino_ratio', 0):.2f}"],
                ['Information Ratio', f"{metrics.get('information_ratio', 0):.2f}"],
                ['Calmar Ratio', f"{metrics.get('calmar_ratio', 0):.2f}"]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Individual Stock Metrics
        story.append(Paragraph("INDIVIDUAL STOCK METRICS", heading_style))
        if 'stock_metrics' in result:
            stock_data = [['Symbol', 'Expected Return', 'Volatility', 'Sharpe Ratio', 'Current Price']]
            for symbol in symbols:
                if symbol in result['stock_metrics']:
                    metrics = result['stock_metrics'][symbol]
                    stock_data.append([
                        symbol,
                        f"{metrics.get('expected_return', 0):.2%}",
                        f"{metrics.get('volatility', 0):.2%}",
                        f"{metrics.get('sharpe_ratio', 0):.2f}",
                        f"${metrics.get('current_price', 0):.2f}"
                    ])
            
            stock_table = Table(stock_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            stock_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(stock_table)
        story.append(Spacer(1, 20))
        
        # Current Market Data
        story.append(Paragraph("CURRENT MARKET DATA", heading_style))
        if 'stock_metrics' in result:
            market_data = [['Symbol', 'Current Price', 'Weight', 'Market Value']]
            total_value = 0
            for symbol in symbols:
                if symbol in result['stock_metrics']:
                    metrics = result['stock_metrics'][symbol]
                    current_price = metrics.get('current_price', 0)
                    weight = metrics.get('weight', 0)
                    # Assume $100,000 portfolio for market value calculation
                    portfolio_value = 100000
                    market_value = portfolio_value * weight
                    total_value += market_value
                    market_data.append([
                        symbol,
                        f"${current_price:.2f}",
                        f"{weight:.2%}",
                        f"${market_value:.2f}"
                    ])
            market_data.append(['Total', '', '100%', f"${total_value:.2f}"])
            
            market_table = Table(market_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
            market_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(market_table)
        story.append(Spacer(1, 20))
        
        # Risk Analysis
        story.append(Paragraph("RISK ANALYSIS", heading_style))
        if 'portfolio_metrics' in result:
            metrics = result['portfolio_metrics']
            volatility = metrics.get('annual_volatility', 0)
            if volatility > 0.25:
                risk_level = "HIGH"
            elif volatility > 0.15:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            risk_data = [
                ['Risk Level', risk_level],
                ['Volatility Classification', 'High' if volatility > 0.25 else 'Medium' if volatility > 0.15 else 'Low'],
                ['Diversification', 'Good' if len(symbols) >= 10 else 'Moderate' if len(symbols) >= 5 else 'Limited']
            ]
            
            risk_table = Table(risk_data, colWidths=[2.5*inch, 2*inch])
            risk_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(risk_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("RECOMMENDATIONS", heading_style))
        recommendations = []
        if 'portfolio_metrics' in result:
            metrics = result['portfolio_metrics']
            sharpe = metrics.get('sharpe_ratio', 0)
            max_dd = metrics.get('max_drawdown', 0)
            volatility = metrics.get('annual_volatility', 0)
            sortino = metrics.get('sortino_ratio', 0)
            
            # Risk-adjusted return analysis
            if sharpe > 1.0:
                recommendations.append("✓ Strong risk-adjusted returns (Sharpe Ratio > 1.0)")
            elif sharpe > 0.5:
                recommendations.append("✓ Moderate risk-adjusted returns (Sharpe Ratio > 0.5)")
            else:
                recommendations.append("⚠ Consider risk management strategies to improve Sharpe ratio")
            
            # Drawdown analysis
            if max_dd < -0.15:
                recommendations.append("⚠ High maximum drawdown - consider defensive positions")
            elif max_dd < -0.10:
                recommendations.append("⚠ Moderate drawdown risk - monitor closely")
            else:
                recommendations.append("✓ Acceptable drawdown levels")
            
            # Diversification analysis
            if len(symbols) < 5:
                recommendations.append("⚠ Limited diversification - consider adding more positions")
            elif len(symbols) < 10:
                recommendations.append("✓ Moderate diversification achieved")
            else:
                recommendations.append("✓ Good diversification with adequate position count")
            
            # Volatility analysis
            if volatility > 0.25:
                recommendations.append("⚠ High volatility portfolio - suitable for aggressive investors")
            elif volatility > 0.15:
                recommendations.append("✓ Moderate volatility - balanced risk profile")
            else:
                recommendations.append("✓ Low volatility - conservative portfolio")
            
            # Sortino ratio analysis
            if sortino > 1.0:
                recommendations.append("✓ Excellent downside risk management")
            elif sortino > 0.5:
                recommendations.append("✓ Good downside risk management")
            else:
                recommendations.append("⚠ Consider strategies to reduce downside volatility")
        
        for rec in recommendations:
            story.append(Paragraph(rec, normal_style))
        
        story.append(Spacer(1, 30))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph("Report generated by Equity Research Dashboard", footer_style))
        story.append(Paragraph("For investment advice, consult with a qualified financial advisor.", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    # Callbacks
    @app.callback(
        [Output("dashboard-content", "children"),
         Output("analysis-content", "children"), 
         Output("portfolio-content", "children"),
         Output("reports-content", "children")],
        [Input("main-tabs", "value")]
    )
    def render_tab_content(active_tab):
        if active_tab == "dashboard":
            return create_dashboard_layout(), [], [], []
        elif active_tab == "analysis":
            return [], create_analysis_layout(), [], []
        elif active_tab == "portfolio":
            return [], [], create_portfolio_layout(), []
        elif active_tab == "reports":
            return [], [], [], create_reports_layout()
        return [], [], [], []
    
    # Market data callback - triggers on both tab change and interval updates
    @app.callback(
        [Output("sp500-price", "children"),
         Output("sp500-change", "children"),
         Output("nasdaq-price", "children"), 
         Output("nasdaq-change", "children"),
         Output("vix-price", "children"),
         Output("vix-change", "children"),
         Output("treasury-price", "children"),
         Output("treasury-change", "children"),
         Output("market-performance-chart", "figure")],
        [Input("interval-component", "n_intervals"),
         Input("main-tabs", "value")]
    )
    def update_market_data(n_intervals, active_tab):
        # Only update market data when dashboard tab is active
        if active_tab != "dashboard":
            # Return current values to prevent unnecessary updates
            raise dash.exceptions.PreventUpdate
        
        try:
            # Configure yfinance with proper headers to avoid blocking
            import yfinance as yf
            import time
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Configure session with retry strategy
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Set proper headers to mimic a real browser
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Use more reliable symbols and alternative symbols as fallbacks
            symbol_configs = [
                {
                    'primary': '^GSPC',
                    'fallback': 'SPY',
                    'name': 'S&P 500',
                    'format': 'currency'
                },
                {
                    'primary': '^IXIC', 
                    'fallback': 'QQQ',
                    'name': 'NASDAQ',
                    'format': 'currency'
                },
                {
                    'primary': '^VIX',
                    'fallback': 'VXX',
                    'name': 'VIX',
                    'format': 'decimal'
                },
                {
                    'primary': '^TNX',
                    'fallback': '^TYX',
                    'name': '10Y Treasury',
                    'format': 'percentage'
                }
            ]
            
            results = []
            got_real_data = False
            
            for i, config in enumerate(symbol_configs):
                try:
                    # Add delay between requests to avoid rate limiting
                    if i > 0:
                        time.sleep(1)  # Increased delay
                    
                    # Try primary symbol first
                    symbol = config['primary']
                    ticker = yf.Ticker(symbol)
                    ticker._session = session
                    
                    # Use a shorter period to reduce data load
                    hist = ticker.history(period='2d', interval='1d')
                    
                    if hist.empty or len(hist) < 2:
                        # Try fallback symbol
                        symbol = config['fallback']
                        ticker = yf.Ticker(symbol)
                        ticker._session = session
                        hist = ticker.history(period='2d', interval='1d')
                    
                    if not hist.empty and len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change = current - previous
                        change_pct = (change / previous) * 100
                        
                        # Format price string based on config
                        if config['format'] == 'currency':
                            price_str = f"${current:.2f}"
                        elif config['format'] == 'percentage':
                            price_str = f"{current:.2f}%"
                        else:
                            price_str = f"{current:.2f}"
                        
                        change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                        results.extend([price_str, change_str])
                        got_real_data = True
                        print(f"Successfully fetched data for {config['name']}: {price_str}")
                    else:
                        results.extend(["N/A", "N/A"])
                        print(f"No data available for {config['name']}")
                        
                except Exception as e:
                    print(f"Error fetching {config['name']}: {e}")
                    results.extend(["N/A", "N/A"])
            
            # If no real data was fetched, provide sample data for demonstration
            if not got_real_data:
                print("No real data available, providing sample data for demonstration")
                sample_data = [
                    "$4,567.89", "+12.34 (+0.27%)",  # S&P 500
                    "$14,234.56", "+45.67 (+0.32%)",  # NASDAQ  
                    "15.67", "-0.23 (-1.45%)",        # VIX
                    "4.25%", "+0.05 (+1.19%)"         # 10Y Treasury
                ]
                results = sample_data
            
            # Create market performance chart with available data
            fig = go.Figure()
            
            # Try to get chart data for market indices
            chart_data_available = False
            chart_symbols = [('^GSPC', 'S&P 500'), ('^IXIC', 'NASDAQ')]
            
            for symbol, name in chart_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    ticker._session = session
                    hist = ticker.history(period='5d', interval='1d')
                    
                    if hist.empty:
                        # Try fallback
                        if symbol == '^GSPC':
                            ticker = yf.Ticker('SPY')
                        elif symbol == '^IXIC':
                            ticker = yf.Ticker('QQQ')
                        ticker._session = session
                        hist = ticker.history(period='5d', interval='1d')
                    
                    if not hist.empty:
                        fig.add_trace(go.Scatter(
                            x=hist.index,
                            y=hist['Close'],
                            mode='lines',
                            name=name,
                            line=dict(width=2)
                        ))
                        chart_data_available = True
                        print(f"Successfully created chart for {name}")
                except Exception as e:
                    print(f"Error creating chart for {name}: {e}")
            
            # If no chart data available, create sample chart
            if not chart_data_available:
                import numpy as np
                from datetime import datetime, timedelta
                
                # Create sample dates for the last 5 days
                dates = [datetime.now() - timedelta(days=i) for i in range(4, -1, -1)]
                
                # Sample data for S&P 500 and NASDAQ
                sp500_data = [4560, 4570, 4580, 4565, 4567.89]
                nasdaq_data = [14200, 14250, 14300, 14280, 14234.56]
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=sp500_data,
                    mode='lines',
                    name='S&P 500',
                    line=dict(width=2, color='blue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=nasdaq_data,
                    mode='lines',
                    name='NASDAQ',
                    line=dict(width=2, color='red')
                ))
            
            fig.update_layout(
                title="Market Performance (5 Days)",
                xaxis_title="Date",
                yaxis_title="Index Value",
                template="plotly_white",
                height=400
            )
            
            results.append(fig)
            return results
            
        except Exception as e:
            print(f"Error in update_market_data: {e}")
            # Return default values on error
            return ["N/A"] * 8 + [go.Figure()]
    
    # Stock analysis callback
    @app.callback(
        Output("stock-analysis-results", "children"),
        [Input("analyze-button", "n_clicks")],
        [State("stock-input", "value"),
         State("period-dropdown", "value")]
    )
    def update_stock_analysis(n_clicks, symbol, period):
        # Prevent callback from firing if no button click
        if not n_clicks or not symbol:
            return []
        
        try:
            # Configure yfinance with proper headers to avoid blocking
            import yfinance as yf
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Configure session with retry strategy
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Set proper headers to mimic a real browser
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Fetch stock data with robust error handling
            stock = yf.Ticker(symbol.upper())
            stock._session = session
            
            hist = stock.history(period=period)
            info = stock.info
            
            if hist.empty:
                return [
                    dbc.Alert(f"No data available for {symbol.upper()}. Please check the symbol and try again.", color="warning")
                ]
            
            # Calculate basic metrics
            current_price = hist['Close'].iloc[-1]
            price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[-2] 
            price_change_pct = (price_change / hist['Close'].iloc[-2]) * 100
            
            # Create price chart
            price_fig = go.Figure()
            price_fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name='Price',
                line=dict(color='#1f77b4', width=2)
            ))
            price_fig.update_layout(
                title=f"{symbol.upper()} Price Chart",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                template="plotly_white",
                height=400
            )
            
            # Volume chart
            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(
                x=hist.index,
                y=hist['Volume'],
                name='Volume',
                marker_color='rgba(55, 83, 109, 0.7)'
            ))
            volume_fig.update_layout(
                title=f"{symbol.upper()} Volume",
                xaxis_title="Date", 
                yaxis_title="Volume",
                template="plotly_white",
                height=300
            )
            
            # Key metrics
            metrics_data = {
                'Metric': ['Current Price', 'Daily Change', 'Daily Change %', 
                          'Market Cap', 'P/E Ratio', '52W High', '52W Low'],
                'Value': [
                    f"${current_price:.2f}",
                    f"${price_change:+.2f}",
                    f"{price_change_pct:+.2f}%",
                    f"${info.get('marketCap', 0)/1e9:.2f}B",
                    f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else 'N/A',
                    f"${info.get('fiftyTwoWeekHigh', 0):.2f}",
                    f"${info.get('fiftyTwoWeekLow', 0):.2f}"
                ]
            }
            
            metrics_table = dash_table.DataTable(
                data=pd.DataFrame(metrics_data).to_dict('records'),
                columns=[{"name": i, "id": i} for i in metrics_data.keys()],
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
            )
            
            return [
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(f"{symbol.upper()} Analysis"),
                            dbc.CardBody([
                                dcc.Graph(figure=price_fig)
                            ])
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Key Metrics"),
                            dbc.CardBody([
                                metrics_table
                            ])
                        ])
                    ], width=4),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Volume Analysis"),
                            dbc.CardBody([
                                dcc.Graph(figure=volume_fig)
                            ])
                        ])
                    ], width=12),
                ], className="mt-4")
            ]
            
        except Exception as e:
            print(f"Error in stock analysis callback: {str(e)}")
            return [
                dbc.Alert(f"Error analyzing {symbol}: {str(e)}", color="danger")
            ]
    
    # Portfolio optimization callback
    @app.callback(
        [Output("portfolio-results", "children"),
         Output("portfolio-comparison", "children"),
         Output("portfolio-export", "children"),
         Output("portfolio-loading", "style")],
        [Input("optimize-button", "n_clicks"),
         Input("suggest-diverse-button", "n_clicks"),
         Input("test-portfolio-button", "n_clicks")],
        [State("portfolio-stocks-input", "value"),
         State("optimization-method", "value"),
         State("portfolio-period", "value"),
         State("target-return-input", "value"),
         State("max-weight-input", "value"),
         State("min-weight-input", "value"),
         State("risk-free-rate-input", "value"),
         State("rebalancing-frequency", "value")]
    )
    def update_portfolio_optimization(n_clicks, suggest_clicks, test_clicks, stocks_input, method, period, target_return, 
                                    max_weight, min_weight, risk_free_rate, rebalancing_frequency):
        # Initialize portfolio optimizer
        portfolio_optimizer = PortfolioOptimizer(risk_free_rate=risk_free_rate or 0.02)
        
        # Determine which button was clicked
        ctx = dash.callback_context
        if not ctx.triggered:
            return [], [], [], {"display": "none"}
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Handle suggest diverse portfolio button
        if button_id == "suggest-diverse-button":
            try:
                # Create a guaranteed diverse portfolio suggestion
                diverse_stocks = portfolio_optimizer.create_guaranteed_diverse_portfolio(n_stocks=10)
                diverse_stocks_str = ",".join(diverse_stocks)
                
                # Update the input field with diverse stocks
                suggestions_display = [
                    dbc.Alert([
                        html.I(className="bi bi-lightbulb me-2"),
                        html.Strong("Diverse Portfolio Suggestion"),
                        html.Br(),
                        html.Span("Here's a diversified portfolio to avoid correlation issues:"),
                        html.Br(),
                        html.Br(),
                        html.Code(diverse_stocks_str, className="fs-5"),
                        html.Br(),
                        html.Br(),
                        html.Small("This portfolio includes stocks from different sectors (Technology, Financials, Healthcare, Consumer, Energy) to minimize correlation and avoid singular covariance matrices.")
                    ], color="info", dismissable=True, className="portfolio-alert"),
                    html.Div([
                        html.H5("Suggested Portfolio Composition:"),
                        html.Ul([
                            html.Li("Technology: AAPL, MSFT"),
                            html.Li("Financials: JPM, V"),
                            html.Li("Healthcare: JNJ, UNH"),
                            html.Li("Consumer: PG, HD"),
                            html.Li("Energy: XOM"),
                            html.Li("Additional: ADBE, CRM")
                        ]),
                        html.Br(),
                        html.P([
                            "Click 'Optimize Portfolio' to analyze this diverse selection, or modify the stock list above."
                        ], className="text-muted")
                    ])
                ]
                
                return suggestions_display, [], [], {"display": "none"}
                
            except Exception as e:
                error_alert = dbc.Alert(f"Error creating diverse portfolio suggestion: {str(e)}", color="danger")
                return [error_alert], [], [], {"display": "none"}
        
        # Handle test portfolio button
        if button_id == "test-portfolio-button":
            if not stocks_input:
                error_alert = dbc.Alert("Please enter stock symbols to test", color="warning")
                return [error_alert], [], [], {"display": "none"}
            
            try:
                # Parse stock symbols
                symbols = [s.strip().upper() for s in stocks_input.split(',')]
                
                # Test portfolio properties
                portfolio_test = portfolio_optimizer.test_portfolio_optimization_properties(symbols, period or '1y')
                
                if 'error' in portfolio_test:
                    error_alert = dbc.Alert(f"Error testing portfolio: {portfolio_test['error']}", color="danger")
                    return [error_alert], [], [], {"display": "none"}
                
                # Create test results display
                test_results = [
                    dbc.Alert([
                        html.I(className="bi bi-clipboard-data me-2"),
                        html.Strong("Portfolio Analysis Results"),
                        html.Br(),
                        html.Span(f"Analyzed {portfolio_test['n_stocks']} stocks over {portfolio_test['n_days']} days")
                    ], color="info", dismissable=True, className="portfolio-alert"),
                    
                    html.Div([
                        html.H5("Portfolio Statistics:"),
                        html.Ul([
                            html.Li(f"Number of stocks: {portfolio_test['n_stocks']}"),
                            html.Li(f"Data points: {portfolio_test['n_days']}"),
                            html.Li(f"Average correlation: {portfolio_test['avg_correlation']:.3f}"),
                            html.Li(f"Maximum correlation: {portfolio_test['max_correlation']:.3f}"),
                            html.Li(f"Minimum correlation: {portfolio_test['min_correlation']:.3f}"),
                            html.Li(f"Singular matrix: {'Yes' if portfolio_test['is_singular_matrix'] else 'No'}")
                        ]),
                        
                        html.Br(),
                        html.H5("High Correlation Pairs (>0.7):"),
                        html.Ul([
                            html.Li(f"{pair['stock1']} - {pair['stock2']}: {pair['correlation']:.3f}")
                            for pair in portfolio_test['high_correlation_pairs']
                        ]) if portfolio_test['high_correlation_pairs'] else html.P("None found - good diversification!"),
                        
                        html.Br(),
                        html.H5("Recommendations:"),
                        html.Ul([
                            html.Li(recommendation) for recommendation in portfolio_test['recommendations']
                        ]) if portfolio_test['recommendations'] else html.P("Portfolio looks good for optimization!")
                    ])
                ]
                
                return test_results, [], [], {"display": "none"}
                
            except Exception as e:
                error_alert = dbc.Alert(f"Error testing portfolio properties: {str(e)}", color="danger")
                return [error_alert], [], [], {"display": "none"}
        
        # Handle optimize portfolio button
        if button_id == "optimize-button":
            # Prevent callback from firing if no stocks input
            if not stocks_input:
                return [], [], [], {"display": "none"}
            
            # Show loading state immediately
            loading_style = {"display": "block"}
            
            try:
                # Clear any previous results first
                print(f"Portfolio optimization triggered - n_clicks: {n_clicks}")
                print(f"Input parameters: symbols={stocks_input}, method={method}, period={period}")
                
                # Parse stock symbols
                symbols = [s.strip().upper() for s in stocks_input.split(',')]
                
                # Validate symbols
                if not symbols or len(symbols) < 2:
                    error_alert = dbc.Alert("Please enter at least 2 stock symbols separated by commas.", color="warning")
                    return [error_alert], [], [], {"display": "none"}
                
                # Set default values and convert to proper types
                period = period or '1y'
                risk_free_rate = float(risk_free_rate) / 100 if risk_free_rate else 0.02
                max_weight = float(max_weight) / 100 if max_weight else 0.4
                min_weight = float(min_weight) / 100 if min_weight else 0.01
                target_return = float(target_return) / 100 if target_return else None
                
                print(f"Processed parameters: risk_free_rate={risk_free_rate}, max_weight={max_weight}, min_weight={min_weight}")
                
                # Create constraints dictionary
                constraints = {
                    'min_weight': min_weight,
                    'max_weight': max_weight
                }
                
                # Initialize portfolio optimizer with user-defined risk-free rate
                portfolio_optimizer = PortfolioOptimizer(risk_free_rate=risk_free_rate)
                
                # Optimize portfolio
                print(f"Starting portfolio optimization for {len(symbols)} symbols: {symbols}")
                result = portfolio_optimizer.optimize_portfolio(
                    symbols=symbols,
                    method=method,
                    period=period,
                    target_return=target_return,
                    constraints=constraints
                )
                
                if 'error' in result:
                    error_alert = dbc.Alert(f"Error optimizing portfolio: {result['error']}", color="danger")
                    return [error_alert], [], [], {"display": "none"}
                
                # Validate result structure
                required_keys = ['optimal_weights', 'portfolio_metrics', 'stock_metrics']
                for key in required_keys:
                    if key not in result:
                        error_alert = dbc.Alert(f"Invalid portfolio optimization result: missing {key}", color="danger")
                        return [error_alert], [], [], {"display": "none"}
                
                print(f"Portfolio optimization completed successfully")
                print(f"Portfolio metrics: {result['portfolio_metrics']}")
                
                # Check for validation warnings and create notifications
                notifications = []
                if 'validation_info' in result:
                    validation_info = result['validation_info']
                    
                    # Check for single asset portfolio
                    if validation_info.get('is_single_asset', False):
                        notifications.append(
                            dbc.Alert([
                                html.I(className="bi bi-info-circle me-2"),
                                "Single asset portfolio detected. Optimization returned equal weight of 100%."
                            ], color="info", dismissable=True, className="portfolio-alert")
                        )
                    
                    # Check for singular covariance matrix
                    if validation_info.get('is_singular_matrix', False):
                        # Get suggestions for diverse alternatives
                        try:
                            suggestions = portfolio_optimizer.suggest_diverse_alternatives(symbols)
                            suggestion_text = []
                            
                            if suggestions['high_correlation_replacement']:
                                suggestion_text.append(html.Br())
                                suggestion_text.append(html.Strong("Suggested replacements for high correlation:"))
                                suggestion_text.append(html.Br())
                                suggestion_text.append(", ".join(suggestions['high_correlation_replacement'][:3]))
                            
                            if suggestions['sector_diversification']:
                                suggestion_text.append(html.Br())
                                suggestion_text.append(html.Strong("Suggested sector diversification:"))
                                suggestion_text.append(html.Br())
                                suggestion_text.append(", ".join(suggestions['sector_diversification'][:3]))
                            
                            notifications.append(
                                dbc.Alert([
                                    html.I(className="bi bi-exclamation-triangle me-2"),
                                    html.Span([
                                        "Singular covariance matrix detected. Portfolio optimization defaulted to equal weights due to perfect correlation between assets. ",
                                        html.Br(),
                                        html.Br(),
                                        html.Strong("To avoid this issue:"),
                                        html.Br(),
                                        "• Add more diverse assets with different risk profiles",
                                        html.Br(),
                                        "• Use a longer time period for historical data",
                                        html.Br(),
                                        "• Consider removing highly correlated assets from your selection",
                                        html.Br(),
                                        "• Try different optimization methods or adjust constraints"
                                    ] + suggestion_text)
                                ], color="warning", dismissable=True, className="portfolio-alert")
                            )
                        except Exception as e:
                            # Fallback to original message if suggestions fail
                            notifications.append(
                                dbc.Alert([
                                    html.I(className="bi bi-exclamation-triangle me-2"),
                                    html.Span([
                                        "Singular covariance matrix detected. Portfolio optimization defaulted to equal weights due to perfect correlation between assets. ",
                                        html.Br(),
                                        html.Br(),
                                        html.Strong("To avoid this issue:"),
                                        html.Br(),
                                        "• Add more diverse assets with different risk profiles",
                                        html.Br(),
                                        "• Use a longer time period for historical data",
                                        html.Br(),
                                        "• Consider removing highly correlated assets from your selection",
                                        html.Br(),
                                        "• Try different optimization methods or adjust constraints"
                                    ])
                                ], color="warning", dismissable=True, className="portfolio-alert")
                            )
                
                # Check for NaN handling
                if validation_info.get('has_nans', False):
                    nan_handling = validation_info.get('nan_handling', 'unknown')
                    if nan_handling == 'forward_fill':
                        notifications.append(
                            dbc.Alert([
                                html.I(className="bi bi-info-circle me-2"),
                                f"Missing data detected. Used forward-fill method to handle {validation_info.get('nan_count', 0)} NaN values."
                            ], color="info", dismissable=True, className="portfolio-alert")
                        )
                    elif nan_handling == 'dropna':
                        notifications.append(
                            dbc.Alert([
                                html.I(className="bi bi-exclamation-triangle me-2"),
                                f"Missing data detected. Dropped {validation_info.get('original_shape', [0, 0])[0] - validation_info.get('cleaned_shape', [0, 0])[0]} rows with NaN values."
                            ], color="warning", dismissable=True, className="portfolio-alert")
                        )
                
                # Check for other validation warnings
                if validation_info.get('warnings'):
                    for warning in validation_info['warnings']:
                        if 'fallback' in warning.lower() or 'equal weights' in warning.lower():
                            notifications.append(
                                dbc.Alert([
                                    html.I(className="bi bi-exclamation-triangle me-2"),
                                    f"Optimization fallback: {warning}"
                                ], color="warning", dismissable=True, className="portfolio-alert")
                            )
                        else:
                            notifications.append(
                                dbc.Alert([
                                    html.I(className="bi bi-info-circle me-2"),
                                    warning
                                ], color="info", dismissable=True, className="portfolio-alert")
                            )
                
                # Additional checks for optimization fallbacks based on actual results
                if 'optimal_weights' in result:
                    optimal_weights = result['optimal_weights']
                    weights_list = list(optimal_weights.values())
                    
                    # Check if all weights are equal (indicating fallback to equal weights)
                    if len(weights_list) > 1 and all(abs(w - weights_list[0]) < 1e-6 for w in weights_list):
                        # This suggests equal weights were used as a fallback
                        notifications.append(
                            dbc.Alert([
                                html.I(className="bi bi-exclamation-triangle me-2"),
                                html.Span([
                                    "Portfolio optimization defaulted to equal weights (",
                                    html.Strong(f"{100/len(weights_list):.1f}% each"),
                                    "). This may indicate optimization constraints or data issues."
                                ])
                            ], color="warning", dismissable=True, className="portfolio-alert")
                        )
                    
                    # Check if any weight is exactly 1.0 (single asset case)
                    if len(weights_list) == 1 and abs(weights_list[0] - 1.0) < 1e-6:
                        notifications.append(
                            dbc.Alert([
                                html.I(className="bi bi-info-circle me-2"),
                                "Single asset portfolio detected. Weight set to 100%."
                            ], color="info", dismissable=True, className="portfolio-alert")
                        )
                    
                    # Check for extreme weight concentrations
                    max_weight_val = max(weights_list)
                    if max_weight_val > 0.8:  # More than 80% in one asset
                        notifications.append(
                            dbc.Alert([
                                html.I(className="bi bi-exclamation-triangle me-2"),
                                html.Span([
                                    "High concentration detected: ",
                                    html.Strong(f"{max_weight_val:.1%}"),
                                    " allocated to a single asset. Consider diversification."
                                ])
                            ], color="warning", dismissable=True, className="portfolio-alert")
                        )
                
                # Create results displays with timestamp for unique keys
                import time
                timestamp = int(time.time())
                results_display = create_portfolio_results_display(result, symbols, method, timestamp)
                comparison_display = create_portfolio_comparison_display(result, symbols, method)
                export_display = create_portfolio_export_display(result, symbols, method)
                
                # Combine notifications with results
                if notifications:
                    results_display = notifications + results_display
                
                return results_display, comparison_display, export_display, {"display": "none"}
                
            except Exception as e:
                print(f"Error in portfolio optimization callback: {str(e)}")
                import traceback
                traceback.print_exc()
                error_alert = dbc.Alert(f"Error optimizing portfolio: {str(e)}", color="danger")
                return [error_alert], [], [], {"display": "none"}
    
    # Callback to show/hide target return input
    @app.callback(
        [Output("target-return-input", "style"),
         Output("target-return-label", "style")],
        [Input("optimization-method", "value")]
    )
    def toggle_target_return_input(method):
        if method == 'target_return':
            return {"display": "block"}, {"display": "block"}
        else:
            return {"display": "none"}, {"display": "none"}
    
    # Callback to clear results when inputs change
    @app.callback(
        [Output("portfolio-results", "children", allow_duplicate=True),
         Output("portfolio-comparison", "children", allow_duplicate=True),
         Output("portfolio-export", "children", allow_duplicate=True)],
        [Input("portfolio-stocks-input", "value"),
         Input("optimization-method", "value"),
         Input("portfolio-period", "value"),
         Input("target-return-input", "value"),
         Input("max-weight-input", "value"),
         Input("min-weight-input", "value"),
         Input("risk-free-rate-input", "value"),
         Input("rebalancing-frequency", "value")],
        [State("optimize-button", "n_clicks")],
        prevent_initial_call=True
    )
    def clear_portfolio_results_on_input_change(stocks_input, method, period, target_return,
                                              max_weight, min_weight, risk_free_rate, rebalancing_frequency, n_clicks):
        """Clear portfolio results when any input parameter changes"""
        # Only clear if the optimize button hasn't been clicked yet
        if not n_clicks:
            return [], [], []
        
        # Return current values to prevent clearing when button is clicked
        raise dash.exceptions.PreventUpdate
    
    # Helper functions for portfolio optimization display
    def create_portfolio_results_display(result, symbols, method, timestamp=None):
        """Create the main portfolio results display"""
        optimal_weights = result['optimal_weights']
        portfolio_metrics = result['portfolio_metrics']
        stock_metrics = result['stock_metrics']
        
        # Use timestamp or current time for unique keys
        if timestamp is None:
            import time
            timestamp = int(time.time())
        
        # Convert weights to array for calculations
        weights = np.array([optimal_weights[symbol] for symbol in symbols])
        
        # Create metrics cards
        metrics_cards = [
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{portfolio_metrics['annual_return']:.2%}", className="text-primary mb-0"),
                    html.P("Expected Annual Return", className="text-muted mb-0")
                ])
            ], className="portfolio-metrics-card text-center"),
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{portfolio_metrics['annual_volatility']:.2%}", className="text-warning mb-0"),
                    html.P("Annual Volatility", className="text-muted mb-0")
                ])
            ], className="portfolio-metrics-card text-center"),
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{portfolio_metrics['sharpe_ratio']:.2f}", className="text-success mb-0"),
                    html.P("Sharpe Ratio", className="text-muted mb-0")
                ])
            ], className="portfolio-metrics-card text-center"),
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{portfolio_metrics['max_drawdown']:.2%}", className="text-danger mb-0"),
                    html.P("Max Drawdown", className="text-muted mb-0")
                ])
            ], className="portfolio-metrics-card text-center")
        ]
        
        # Create allocation pie chart
        allocation_fig = go.Figure(data=[go.Pie(
            labels=symbols,
            values=weights,
            hole=0.3,
            textinfo='percent+label',
            textposition='inside'
        )])
        allocation_fig.update_layout(
            title=f"Asset Allocation - {method.replace('_', ' ').title()}",
            template="plotly_white",
            height=400,
            showlegend=True
        )
        
        # Create performance comparison chart
        performance_fig = go.Figure()
        
        # Add individual stock performance
        for symbol in symbols:
            if symbol in stock_metrics and 'dates' in stock_metrics[symbol] and 'cumulative_returns' in stock_metrics[symbol]:
                try:
                    performance_fig.add_trace(go.Scatter(
                        x=stock_metrics[symbol]['dates'],
                        y=stock_metrics[symbol]['cumulative_returns'],
                        mode='lines',
                        name=symbol,
                        line=dict(width=1)
                    ))
                except Exception as e:
                    print(f"Error adding stock performance for {symbol}: {e}")
        
        # Add portfolio performance
        if 'portfolio_dates' in portfolio_metrics and 'portfolio_returns' in portfolio_metrics:
            try:
                performance_fig.add_trace(go.Scatter(
                    x=portfolio_metrics['portfolio_dates'],
                    y=portfolio_metrics['portfolio_returns'],
                    mode='lines',
                    name='Portfolio',
                    line=dict(color='black', width=3)
                ))
            except Exception as e:
                print(f"Error adding portfolio performance: {e}")
        
        performance_fig.update_layout(
            title=f"Performance Comparison - {method.replace('_', ' ').title()}",
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            template="plotly_white",
            height=400
        )
        
        # Create holdings table
        holdings_data = []
        for symbol in symbols:
            weight = optimal_weights.get(symbol, 0)
            if symbol in stock_metrics:
                try:
                    holdings_data.append({
                        'Symbol': symbol,
                        'Weight': f"{weight:.2%}",
                        'Expected Return': f"{stock_metrics[symbol].get('expected_return', 0):.2%}",
                        'Volatility': f"{stock_metrics[symbol].get('volatility', 0):.2%}",
                        'Sharpe Ratio': f"{stock_metrics[symbol].get('sharpe_ratio', 0):.2f}"
                    })
                except Exception as e:
                    print(f"Error creating holdings data for {symbol}: {e}")
                    # Add fallback data
                    holdings_data.append({
                        'Symbol': symbol,
                        'Weight': f"{weight:.2%}",
                        'Expected Return': "N/A",
                        'Volatility': "N/A",
                        'Sharpe Ratio': "N/A"
                    })
        
        holdings_table = dash_table.DataTable(
            data=holdings_data,
            columns=[
                {"name": "Symbol", "id": "Symbol"},
                {"name": "Weight", "id": "Weight"},
                {"name": "Expected Return", "id": "Expected Return"},
                {"name": "Volatility", "id": "Volatility"},
                {"name": "Sharpe Ratio", "id": "Sharpe Ratio"}
            ],
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
        
        return [
            # Optimization method badge
            dbc.Row([
                dbc.Col([
                    html.Span(
                        f"Optimization Method: {method.replace('_', ' ').title()}",
                        className=f"optimization-method-badge optimization-method-{method}"
                    )
                ], className="text-center mb-3")
            ]),
            
            # Metrics cards
            dbc.Row([
                dbc.Col(card, width=3) for card in metrics_cards
            ], className="mb-4"),
            
            # Charts and table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Asset Allocation"),
                                                 dbc.CardBody([
                             dcc.Graph(figure=allocation_fig)
                         ])
                    ], className="portfolio-chart-card")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Performance Comparison"),
                                                 dbc.CardBody([
                             dcc.Graph(figure=performance_fig)
                         ])
                    ], className="portfolio-chart-card")
                ], width=6)
            ], className="mb-4"),
            
            # Holdings table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Portfolio Holdings"),
                        dbc.CardBody([
                            holdings_table
                        ])
                    ], className="portfolio-table-card")
                ])
            ])
        ]
    
    def create_portfolio_comparison_display(result, symbols, method):
        """Create the portfolio comparison display"""
        if 'efficient_frontier' not in result or not result['efficient_frontier']:
            return []
        
        efficient_frontier = result['efficient_frontier']
        optimal_weights = result['optimal_weights']
        portfolio_metrics = result['portfolio_metrics']
        
        # Create efficient frontier chart
        frontier_fig = go.Figure()
        
        # Add efficient frontier points
        frontier_fig.add_trace(go.Scatter(
            x=[point['volatility'] for point in efficient_frontier],
            y=[point['return'] for point in efficient_frontier],
            mode='markers',
            name='Efficient Frontier',
            marker=dict(color='lightblue', size=8)
        ))
        
        # Add optimal portfolio point
        frontier_fig.add_trace(go.Scatter(
            x=[portfolio_metrics['annual_volatility']],
            y=[portfolio_metrics['annual_return']],
            mode='markers',
            name='Optimal Portfolio',
            marker=dict(color='red', size=12, symbol='star')
        ))
        
        frontier_fig.update_layout(
            title="Efficient Frontier Analysis",
            xaxis_title="Portfolio Volatility",
            yaxis_title="Expected Return",
            template="plotly_white",
            height=400
        )
        
        # Create benchmark comparison table
        benchmark_data = [
            {
                'Metric': 'Expected Return',
                'Portfolio': f"{portfolio_metrics['annual_return']:.2%}",
                'S&P 500': '10.5%',
                'Russell 2000': '12.2%',
                'MSCI World': '8.7%'
            },
            {
                'Metric': 'Volatility',
                'Portfolio': f"{portfolio_metrics['annual_volatility']:.2%}",
                'S&P 500': '15.2%',
                'Russell 2000': '18.5%',
                'MSCI World': '14.8%'
            },
            {
                'Metric': 'Sharpe Ratio',
                'Portfolio': f"{portfolio_metrics['sharpe_ratio']:.2f}",
                'S&P 500': '0.69',
                'Russell 2000': '0.66',
                'MSCI World': '0.59'
            },
            {
                'Metric': 'Max Drawdown',
                'Portfolio': f"{portfolio_metrics['max_drawdown']:.2%}",
                'S&P 500': '-12.5%',
                'Russell 2000': '-15.8%',
                'MSCI World': '-11.2%'
            }
        ]
        
        benchmark_table = dash_table.DataTable(
            data=benchmark_data,
            columns=[
                {"name": "Metric", "id": "Metric"},
                {"name": "Portfolio", "id": "Portfolio"},
                {"name": "S&P 500", "id": "S&P 500"},
                {"name": "Russell 2000", "id": "Russell 2000"},
                {"name": "MSCI World", "id": "MSCI World"}
            ],
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
        
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Efficient Frontier Analysis"),
                        dbc.CardBody([
                            dcc.Graph(figure=frontier_fig)
                        ])
                    ], className="efficient-frontier-chart")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Performance Benchmarks"),
                        dbc.CardBody([
                            benchmark_table
                        ])
                    ], className="performance-benchmark-table")
                ], width=6)
            ])
        ]
    
    def create_portfolio_export_display(result, symbols, method):
        """Create the portfolio export display"""
        return [
            dbc.Card([
                dbc.CardHeader("Export & Save Options"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-download me-2"),
                                "Export as JSON"
                            ], id="export-json-btn", color="primary", className="w-100 mb-2")
                        ], width=3),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-file-csv me-2"),
                                "Export as CSV"
                            ], id="export-csv-btn", color="success", className="w-100 mb-2")
                        ], width=3),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-user me-2"),
                                "Save to Profile"
                            ], id="save-portfolio-btn", color="info", className="w-100 mb-2")
                        ], width=3),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-file-pdf me-2"),
                                "Generate Report"
                            ], id="generate-report-btn", color="warning", className="w-100 mb-2")
                        ], width=3)
                    ]),
                    # Hidden div to store portfolio data for export
                    dcc.Store(id="portfolio-export-data", data={
                        'result': result,
                        'symbols': symbols,
                        'method': method
                    }),
                    # Download components
                    dcc.Download(id="download-json"),
                    dcc.Download(id="download-csv"),
                    dcc.Download(id="download-pdf")
                ])
            ], className="portfolio-export-section")
        ]
    
    # Research report callback
    @app.callback(
        Output("report-results", "children"),
        [Input("generate-report-button", "n_clicks")],
        [State("report-stock-input", "value"),
         State("report-type", "value")]
    )
    def generate_research_report(n_clicks, symbol, report_type):
        if not n_clicks or not symbol:
            return []
        
        try:
            # Fetch comprehensive stock data
            stock = yf.Ticker(symbol.upper())
            info = stock.info
            hist = stock.history(period='2y')
            
            # Generate report content based on type
            if report_type == 'full':
                report_content = generate_full_report(symbol, stock, info, hist)
            elif report_type == 'valuation':
                report_content = generate_valuation_report(symbol, stock, info, hist)
            elif report_type == 'risk':
                report_content = generate_risk_report(symbol, stock, info, hist)
            else:  # peer comparison
                report_content = generate_peer_report(symbol, stock, info, hist)
            
            return report_content
            
        except Exception as e:
            return [
                dbc.Alert(f"Error generating report for {symbol}: {str(e)}", color="danger")
            ]
    
    def generate_full_report(symbol, stock, info, hist):
        """Generate a comprehensive research report"""
        
        # Executive Summary
        current_price = hist['Close'].iloc[-1]
        market_cap = info.get('marketCap', 0) / 1e9
        pe_ratio = info.get('trailingPE', 'N/A')
        
        # Price targets (simple calculation)
        price_52w_high = info.get('fiftyTwoWeekHigh', current_price)
        price_52w_low = info.get('fiftyTwoWeekLow', current_price)
        target_price = current_price * 1.15  # 15% upside assumption
        
        return [
            dbc.Card([
                dbc.CardHeader([
                    html.H3(f"📋 Research Report: {symbol.upper()}")
                ]),
                dbc.CardBody([
                    # Executive Summary
                    html.H4("Executive Summary", className="text-primary"),
                    html.Hr(),
                    html.P([
                        f"{info.get('longName', symbol.upper())} is trading at ${current_price:.2f} "
                        f"with a market capitalization of ${market_cap:.2f}B. "
                        f"The stock has a P/E ratio of {pe_ratio if pe_ratio != 'N/A' else 'N/A'}."
                    ]),
                    
                    # Key Metrics
                    html.H4("Key Financial Metrics", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.P(f"🏷️ Current Price: ${current_price:.2f}"),
                            html.P(f"🎯 Price Target: ${target_price:.2f}"),
                            html.P(f"📈 52W High: ${price_52w_high:.2f}"),
                        ], width=4),
                        dbc.Col([
                            html.P(f"📉 52W Low: ${price_52w_low:.2f}"),
                            html.P(f"💰 Market Cap: ${market_cap:.2f}B"),
                            html.P(f"📊 P/E Ratio: {pe_ratio if pe_ratio != 'N/A' else 'N/A'}"),
                        ], width=4),
                        dbc.Col([
                            html.P(f"🏢 Sector: {info.get('sector', 'N/A')}"),
                            html.P(f"🏭 Industry: {info.get('industry', 'N/A')}"),
                            html.P(f"👥 Employees: {info.get('fullTimeEmployees', 'N/A'):,}" if info.get('fullTimeEmployees') else "👥 Employees: N/A"),
                        ], width=4),
                    ]),
                    
                    # Investment Thesis
                    html.H4("Investment Thesis", className="text-primary mt-4"),
                    html.Hr(),
                    html.P([
                        "Based on our analysis, we maintain a positive outlook on ",
                        html.Strong(symbol.upper()),
                        f". The company's current valuation appears reasonable given its market position "
                        f"and growth prospects. Key factors supporting our thesis include:"
                    ]),
                    html.Ul([
                        html.Li("Strong market position in its sector"),
                        html.Li("Consistent financial performance"),
                        html.Li("Attractive valuation metrics"),
                        html.Li("Potential for continued growth"),
                    ]),
                    
                    # Risk Factors
                    html.H4("Risk Factors", className="text-primary mt-4"),
                    html.Hr(),
                    html.Ul([
                        html.Li("Market volatility and economic conditions"),
                        html.Li("Sector-specific regulatory risks"),
                        html.Li("Competitive pressures"),
                        html.Li("Interest rate sensitivity"),
                    ]),
                    
                    # Recommendation
                    html.H4("Recommendation", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Alert([
                        html.H5("📊 BUY", className="alert-heading"),
                        html.P(f"Price Target: ${target_price:.2f} | "
                              f"Upside: {((target_price/current_price)-1)*100:.1f}%"),
                    ], color="success"),
                    
                    html.Small(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                             f"Data as of market close", className="text-muted"),
                ])
            ])
        ]
    
    def generate_valuation_report(symbol, stock, info, hist):
        """Generate valuation-focused report"""
        current_price = hist['Close'].iloc[-1]
        market_cap = info.get('marketCap', 0) / 1e9
        pe_ratio = info.get('trailingPE', 'N/A')
        pb_ratio = info.get('priceToBook', 'N/A')
        ps_ratio = info.get('priceToSalesTrailing12Months', 'N/A')
        
        # Calculate basic valuation metrics
        price_52w_high = info.get('fiftyTwoWeekHigh', current_price)
        price_52w_low = info.get('fiftyTwoWeekLow', current_price)
        
        # Simple DCF assumptions
        growth_rate = 0.05  # 5% assumed growth
        discount_rate = 0.10  # 10% discount rate
        target_price = current_price * (1 + growth_rate) / (discount_rate - growth_rate)
        
        return [
            dbc.Card([
                dbc.CardHeader([
                    html.H3(f"💰 Valuation Summary: {symbol.upper()}")
                ]),
                dbc.CardBody([
                    # Executive Summary
                    html.H4("Valuation Overview", className="text-primary"),
                    html.Hr(),
                    html.P([
                        f"{info.get('longName', symbol.upper())} is currently trading at ${current_price:.2f} "
                        f"with a market capitalization of ${market_cap:.2f}B. "
                        f"Our valuation analysis suggests the stock is "
                    ] + ([html.Strong("UNDERVALUED")] if target_price > current_price else [html.Strong("FAIRLY VALUED")]) + [
                        f" with a target price of ${target_price:.2f}."
                    ]),
                    
                    # Key Valuation Metrics
                    html.H4("Key Valuation Metrics", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Price Ratios", className="text-secondary"),
                            html.P(f"P/E Ratio: {pe_ratio if pe_ratio != 'N/A' else 'N/A'}"),
                            html.P(f"P/B Ratio: {pb_ratio if pb_ratio != 'N/A' else 'N/A'}"),
                            html.P(f"P/S Ratio: {ps_ratio if ps_ratio != 'N/A' else 'N/A'}"),
                        ], width=4),
                        dbc.Col([
                            html.H5("Price Targets", className="text-secondary"),
                            html.P(f"Current Price: ${current_price:.2f}"),
                            html.P(f"Target Price: ${target_price:.2f}"),
                            html.P(f"Upside Potential: {((target_price/current_price - 1) * 100):.1f}%"),
                        ], width=4),
                        dbc.Col([
                            html.H5("52-Week Range", className="text-secondary"),
                            html.P(f"52W High: ${price_52w_high:.2f}"),
                            html.P(f"52W Low: ${price_52w_low:.2f}"),
                            html.P(f"Range: {((price_52w_high/price_52w_low - 1) * 100):.1f}%"),
                        ], width=4),
                    ]),
                    
                    # Valuation Models
                    html.H4("Valuation Models", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Discounted Cash Flow (DCF)", className="text-secondary"),
                            html.P("Assumptions:"),
                            html.Ul([
                                html.Li(f"Growth Rate: {growth_rate*100:.1f}%"),
                                html.Li(f"Discount Rate: {discount_rate*100:.1f}%"),
                                html.Li("Terminal Value: Perpetuity Growth Model"),
                            ]),
                            html.P(f"Target Price: ${target_price:.2f}"),
                        ], width=6),
                        dbc.Col([
                            html.H5("Comparable Company Analysis", className="text-secondary"),
                            html.P("Based on industry peers:"),
                            html.Ul([
                                html.Li("P/E Multiple: Industry Average"),
                                html.Li("P/B Multiple: Sector Median"),
                                html.Li("EV/EBITDA: Peer Comparison"),
                            ]),
                            html.P("Target Range: $" + f"{current_price*0.9:.2f}" + " - $" + f"{current_price*1.2:.2f}"),
                        ], width=6),
                    ]),
                    
                    # Investment Recommendation
                    html.H4("Investment Recommendation", className="text-primary mt-4"),
                    html.Hr(),
                    html.P([
                        "Based on our valuation analysis, we recommend a ",
                        html.Strong("BUY" if target_price > current_price * 1.1 else "HOLD" if target_price > current_price * 0.9 else "SELL"),
                        f" rating for {symbol.upper()}. "
                        f"Key factors supporting this recommendation include:"
                    ]),
                    html.Ul([
                        html.Li("Attractive valuation relative to peers"),
                        html.Li("Strong market position and competitive advantages"),
                        html.Li("Consistent financial performance"),
                        html.Li("Growth opportunities in core markets"),
                    ]),
                    
                    # Risk Factors
                    html.H4("Risk Factors", className="text-primary mt-4"),
                    html.Hr(),
                    html.Ul([
                        html.Li("Market volatility and economic uncertainty"),
                        html.Li("Regulatory changes affecting the industry"),
                        html.Li("Competition from new market entrants"),
                        html.Li("Changes in consumer preferences"),
                    ]),
                ])
            ])
        ]
    
    def generate_risk_report(symbol, stock, info, hist):
        """Generate risk assessment report"""
        current_price = hist['Close'].iloc[-1]
        market_cap = info.get('marketCap', 0) / 1e9
        
        # Calculate risk metrics
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
        beta = info.get('beta', 1.0)
        
        # Calculate Value at Risk (VaR)
        var_95 = returns.quantile(0.05) * current_price
        var_99 = returns.quantile(0.01) * current_price
        
        # Calculate maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Risk rating based on volatility
        if volatility < 0.15:
            risk_level = "LOW"
            risk_color = "success"
        elif volatility < 0.25:
            risk_level = "MODERATE"
            risk_color = "warning"
        else:
            risk_level = "HIGH"
            risk_color = "danger"
        
        return [
            dbc.Card([
                dbc.CardHeader([
                    html.H3(f"⚠️ Risk Assessment: {symbol.upper()}")
                ]),
                dbc.CardBody([
                    # Risk Overview
                    html.H4("Risk Profile Overview", className="text-primary"),
                    html.Hr(),
                    html.P([
                        f"{info.get('longName', symbol.upper())} has a ",
                        html.Strong(risk_level, className=f"text-{risk_color}"),
                        f" risk profile with an annualized volatility of {volatility*100:.1f}%. "
                        f"The stock's beta of {beta:.2f} indicates it moves "
                    ] + ([html.Strong("more")] if beta > 1 else [html.Strong("less")]) + [
                        " than the market average."
                    ]),
                    
                    # Key Risk Metrics
                    html.H4("Key Risk Metrics", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Volatility Metrics", className="text-secondary"),
                            html.P(f"Annualized Volatility: {volatility*100:.1f}%"),
                            html.P(f"Beta: {beta:.2f}"),
                            html.P(f"Risk Level: {risk_level}"),
                        ], width=4),
                        dbc.Col([
                            html.H5("Value at Risk (VaR)", className="text-secondary"),
                            html.P(f"95% VaR: ${abs(var_95):.2f}"),
                            html.P(f"99% VaR: ${abs(var_99):.2f}"),
                            html.P(f"Max Daily Loss: ${abs(returns.min() * current_price):.2f}"),
                        ], width=4),
                        dbc.Col([
                            html.H5("Drawdown Analysis", className="text-secondary"),
                            html.P(f"Maximum Drawdown: {max_drawdown*100:.1f}%"),
                            html.P(f"Current Drawdown: {drawdown.iloc[-1]*100:.1f}%"),
                            html.P(f"Recovery Period: ~{abs(max_drawdown/volatility/252*365):.0f} days"),
                        ], width=4),
                    ]),
                    
                    # Risk Categories
                    html.H4("Risk Categories", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Market Risk", className="text-secondary"),
                            html.Ul([
                                html.Li(f"Beta: {beta:.2f} (Market sensitivity)"),
                                html.Li(f"Volatility: {volatility*100:.1f}% (Price fluctuations)"),
                                html.Li("Sector correlation risk"),
                                html.Li("Economic cycle sensitivity"),
                            ]),
                        ], width=6),
                        dbc.Col([
                            html.H5("Company-Specific Risk", className="text-secondary"),
                            html.Ul([
                                html.Li("Business model risk"),
                                html.Li("Management execution risk"),
                                html.Li("Competitive positioning risk"),
                                html.Li("Regulatory compliance risk"),
                            ]),
                        ], width=6),
                    ]),
                    
                    # Stress Testing
                    html.H4("Stress Testing Scenarios", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Market Stress Scenarios", className="text-secondary"),
                            html.P("Impact on stock price under different market conditions:"),
                            html.Ul([
                                html.Li(f"Market crash (-20%): ${current_price * (1 - 0.2 * beta):.2f}"),
                                html.Li(f"Recession (-10%): ${current_price * (1 - 0.1 * beta):.2f}"),
                                html.Li(f"Market rally (+15%): ${current_price * (1 + 0.15 * beta):.2f}"),
                            ]),
                        ], width=6),
                        dbc.Col([
                            html.H5("Company-Specific Scenarios", className="text-secondary"),
                            html.P("Potential impact of company-specific events:"),
                            html.Ul([
                                html.Li("Earnings miss: -15% to -25%"),
                                html.Li("Management change: -5% to +10%"),
                                html.Li("Regulatory issues: -20% to -40%"),
                                html.Li("Merger/Acquisition: -10% to +30%"),
                            ]),
                        ], width=6),
                    ]),
                    
                    # Risk Management Recommendations
                    html.H4("Risk Management Recommendations", className="text-primary mt-4"),
                    html.Hr(),
                    html.P([
                        "Based on our risk assessment, we recommend the following risk management strategies:"
                    ]),
                    html.Ul([
                        html.Li("Position sizing: Limit exposure to 2-5% of portfolio"),
                        html.Li("Stop-loss orders: Set at 15-20% below current price"),
                        html.Li("Diversification: Ensure adequate sector diversification"),
                        html.Li("Regular monitoring: Review position monthly"),
                        html.Li("Hedging: Consider options for downside protection"),
                    ]),
                    
                    # Risk Rating Summary
                    html.H4("Risk Rating Summary", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Alert([
                        html.H5(f"Overall Risk Rating: {risk_level}", className=f"text-{risk_color}"),
                        html.P([
                            f"Volatility: {volatility*100:.1f}% | Beta: {beta:.2f} | "
                            f"Max Drawdown: {max_drawdown*100:.1f}%"
                        ]),
                    ], color=risk_color),
                ])
            ])
        ]
    
    def generate_peer_report(symbol, stock, info, hist):
        """Generate peer comparison report"""
        current_price = hist['Close'].iloc[-1]
        market_cap = info.get('marketCap', 0) / 1e9
        sector = info.get('sector', 'Technology')
        industry = info.get('industry', 'Software')
        
        # Define peer companies based on sector/industry
        peer_companies = {
            'Technology': ['MSFT', 'GOOGL', 'META', 'NVDA', 'TSLA'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
            'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA'],
            'Industrials': ['BA', 'CAT', 'GE', 'MMM', 'HON'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
            'Consumer Defensive': ['PG', 'KO', 'WMT', 'COST', 'PEP'],
            'Real Estate': ['PLD', 'AMT', 'CCI', 'EQIX', 'DLR'],
            'Basic Materials': ['LIN', 'APD', 'FCX', 'NEM', 'DOW']
        }
        
        # Get peers for the sector
        peers = peer_companies.get(sector, ['MSFT', 'GOOGL', 'AAPL', 'AMZN', 'META'])
        
        # Simulate peer data (in a real implementation, this would fetch actual data)
        peer_data = []
        for peer in peers[:5]:  # Top 5 peers
            try:
                peer_stock = yf.Ticker(peer)
                peer_info = peer_stock.info
                peer_hist = peer_stock.history(period='1y')
                
                if not peer_hist.empty:
                    peer_price = peer_hist['Close'].iloc[-1]
                    peer_market_cap = peer_info.get('marketCap', 0) / 1e9
                    peer_pe = peer_info.get('trailingPE', 'N/A')
                    peer_pb = peer_info.get('priceToBook', 'N/A')
                    
                    peer_data.append({
                        'symbol': peer,
                        'name': peer_info.get('longName', peer),
                        'price': peer_price,
                        'market_cap': peer_market_cap,
                        'pe_ratio': peer_pe,
                        'pb_ratio': peer_pb,
                        'sector': peer_info.get('sector', sector),
                        'industry': peer_info.get('industry', industry)
                    })
            except:
                continue
        
        # Add the target company to the comparison
        target_pe = info.get('trailingPE', 'N/A')
        target_pb = info.get('priceToBook', 'N/A')
        
        target_data = {
            'symbol': symbol.upper(),
            'name': info.get('longName', symbol.upper()),
            'price': current_price,
            'market_cap': market_cap,
            'pe_ratio': target_pe,
            'pb_ratio': target_pb,
            'sector': sector,
            'industry': industry
        }
        
        # Calculate relative valuation
        avg_pe = 0
        pe_count = 0
        for peer in peer_data:
            if peer['pe_ratio'] != 'N/A' and peer['pe_ratio'] > 0:
                avg_pe += peer['pe_ratio']
                pe_count += 1
        
        avg_pe = avg_pe / pe_count if pe_count > 0 else 20
        pe_premium = ((target_pe - avg_pe) / avg_pe * 100) if target_pe != 'N/A' and target_pe > 0 else 0
        
        return [
            dbc.Card([
                dbc.CardHeader([
                    html.H3(f"📊 Peer Comparison: {symbol.upper()}")
                ]),
                dbc.CardBody([
                    # Executive Summary
                    html.H4("Peer Comparison Overview", className="text-primary"),
                    html.Hr(),
                    html.P([
                        f"{info.get('longName', symbol.upper())} is compared against {len(peer_data)} peer companies "
                        f"in the {sector} sector. The company trades at a P/E ratio of {target_pe if target_pe != 'N/A' else 'N/A'}."
                    ]),
                    html.P([
                        f"This is {abs(pe_premium):.1f}% ",
                        html.Strong("ABOVE" if pe_premium > 0 else "BELOW"),
                        " the peer average."
                    ]) if target_pe != 'N/A' and target_pe > 0 else html.P("Limited peer comparison data available."),
                    
                    # Peer Comparison Table
                    html.H4("Peer Company Comparison", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Company"),
                                html.Th("Symbol"),
                                html.Th("Price"),
                                html.Th("Market Cap (B)"),
                                html.Th("P/E Ratio"),
                                html.Th("P/B Ratio"),
                            ])
                        ]),
                        html.Tbody([
                            # Target company (highlighted)
                            html.Tr([
                                html.Td(html.Strong(target_data['name'])),
                                html.Td(html.Strong(target_data['symbol'])),
                                html.Td(html.Strong(f"${target_data['price']:.2f}")),
                                html.Td(html.Strong(f"${target_data['market_cap']:.1f}")),
                                html.Td(html.Strong(str(target_data['pe_ratio']))),
                                html.Td(html.Strong(str(target_data['pb_ratio']))),
                            ], className="table-primary"),
                            # Peer companies
                        ] + [
                            html.Tr([
                                html.Td(peer['name']),
                                html.Td(peer['symbol']),
                                html.Td(f"${peer['price']:.2f}"),
                                html.Td(f"${peer['market_cap']:.1f}"),
                                html.Td(str(peer['pe_ratio'])),
                                html.Td(str(peer['pb_ratio'])),
                            ]) for peer in peer_data
                        ])
                    ], bordered=True, hover=True, responsive=True, striped=True),
                    
                    # Relative Valuation Analysis
                    html.H4("Relative Valuation Analysis", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("P/E Ratio Analysis", className="text-secondary"),
                            html.P([
                                f"Average Peer P/E: {avg_pe:.1f}",
                                html.Br(),
                                f"Target P/E: {target_pe if target_pe != 'N/A' else 'N/A'}",
                                html.Br(),
                                f"P/E Premium: {pe_premium:.1f}%" if target_pe != 'N/A' and target_pe > 0 else "P/E Premium: N/A",
                            ]),
                            html.P([
                                "Interpretation: ",
                                html.Strong("UNDERVALUED" if pe_premium < -10 else "FAIRLY VALUED" if abs(pe_premium) <= 10 else "OVERVALUED")
                            ]) if target_pe != 'N/A' and target_pe > 0 else html.P("Insufficient data for comparison"),
                        ], width=6),
                        dbc.Col([
                            html.H5("Market Position", className="text-secondary"),
                            html.P([
                                f"Sector: {sector}",
                                html.Br(),
                                f"Industry: {industry}",
                                html.Br(),
                                f"Market Cap Rank: {sorted([p['market_cap'] for p in peer_data + [target_data]], reverse=True).index(target_data['market_cap']) + 1} of {len(peer_data) + 1}",
                            ]),
                            html.P([
                                "Market Position: ",
                                html.Strong("LEADER" if target_data['market_cap'] > sum(p['market_cap'] for p in peer_data) / len(peer_data) else "FOLLOWER")
                            ]),
                        ], width=6),
                    ]),
                    
                    # Competitive Analysis
                    html.H4("Competitive Analysis", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Strengths", className="text-success"),
                            html.Ul([
                                html.Li("Strong market position in core business"),
                                html.Li("Consistent financial performance"),
                                html.Li("Innovation and R&D investment"),
                                html.Li("Diversified revenue streams"),
                            ]),
                        ], width=6),
                        dbc.Col([
                            html.H5("Challenges", className="text-warning"),
                            html.Ul([
                                html.Li("Intense competition from peers"),
                                html.Li("Regulatory environment changes"),
                                html.Li("Technology disruption risks"),
                                html.Li("Market saturation in some segments"),
                            ]),
                        ], width=6),
                    ]),
                    
                    # Investment Recommendation
                    html.H4("Peer-Based Investment Recommendation", className="text-primary mt-4"),
                    html.Hr(),
                    html.P([
                        "Based on our peer comparison analysis, we recommend a ",
                        html.Strong("BUY" if pe_premium < -10 else "HOLD" if abs(pe_premium) <= 10 else "SELL"),
                        f" rating for {symbol.upper()}. "
                        f"Key factors supporting this recommendation include:"
                    ]),
                    html.Ul([
                        html.Li("Relative valuation compared to peers"),
                        html.Li("Market position and competitive advantages"),
                        html.Li("Growth prospects relative to industry"),
                        html.Li("Financial strength and stability"),
                    ]),
                    
                    # Peer Performance Summary
                    html.H4("Peer Performance Summary", className="text-primary mt-4"),
                    html.Hr(),
                    dbc.Alert([
                        html.H5("Key Takeaways", className="text-info"),
                        html.P([
                            f"• {symbol.upper()} ranks #",
                            f"{sorted([p['market_cap'] for p in peer_data + [target_data]], reverse=True).index(target_data['market_cap']) + 1}",
                            f" by market capitalization among peers",
                            html.Br(),
                            f"• P/E ratio is {abs(pe_premium):.1f}% ",
                            "above" if pe_premium > 0 else "below",
                            " peer average" if target_pe != 'N/A' and target_pe > 0 else "• P/E comparison not available",
                            html.Br(),
                            f"• Operating in {sector} sector with {len(peer_data)} comparable peers",
                        ]),
                    ], color="info"),
                ])
            ])
        ]
    
    # Authentication callbacks
    @app.callback(
        Output('auth-status', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_auth_status(n):
        """Update authentication status display"""
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                return [
                    dbc.Alert([
                        html.I(className="fas fa-user-check me-2"),
                        f"Welcome, {current_user.username}!"
                    ], color="success", className="mb-3")
                ]
            else:
                return [
                    dbc.Alert([
                        html.I(className="fas fa-user-times me-2"),
                        "Please log in to access full features"
                    ], color="warning", className="mb-3")
                ]
        except Exception as e:
            print(f"Error in auth status callback: {str(e)}")
            return [
                dbc.Alert([
                    html.I(className="fas fa-user-times me-2"),
                    "Please log in to access full features"
                ], color="warning", className="mb-3")
            ]
    
    # Top movers callback
    @app.callback(
        Output('top-movers-table', 'children'),
        [Input('interval-component', 'n_intervals'),
         Input('main-tabs', 'value'),
         Input('refresh-top-movers', 'n_clicks')]
    )
    def update_top_movers(n_intervals, active_tab, refresh_clicks):
        """Update top movers table with real market data"""
        # Only update when dashboard tab is active
        if active_tab != "dashboard":
            raise dash.exceptions.PreventUpdate
        
        def format_volume(volume):
            """Helper function to format volume numbers"""
            if volume >= 1e9:
                return f"{volume/1e9:.1f}B"
            elif volume >= 1e6:
                return f"{volume/1e6:.1f}M"
            elif volume >= 1e3:
                return f"{volume/1e3:.1f}K"
            else:
                return f"{volume:.0f}"
        
        try:
            # Show loading state if this is a manual refresh
            if refresh_clicks and refresh_clicks > 0:
                return [
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-spinner fa-spin me-2"),
                            "Refreshing top movers data..."
                        ], className="text-center text-muted")
                    ], className="p-4")
                ]
            
            # Configure yfinance with proper headers to avoid blocking
            import yfinance as yf
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            import time
            
            # Configure session with retry strategy
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Set proper headers to mimic a real browser
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Popular stocks for top movers analysis (S&P 500 focus)
            popular_stocks = [
                'AAPL', 'MSFT', 'JPM', 'V', 'JNJ', 'PG', 'XOM',
                'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'MA', 'HD', 'BAC',
                'DIS', 'ADBE', 'NFLX', 'CRM', 'PYPL', 'INTC', 'AMD', 'ORCL',
                'NKE', 'KO', 'PEP', 'ABT', 'TMO', 'AVGO', 'COST', 'MRK',
                'PFE', 'TXN', 'ACN', 'DHR', 'LLY', 'VZ', 'CMCSA', 'BMY',
                'QCOM', 'HON', 'RTX', 'LOW', 'UPS', 'SPGI', 'T', 'DE',
                'CAT', 'MMC', 'AXP', 'GS', 'MS', 'BLK', 'SCHW', 'USB',
                'PNC', 'COF', 'TFC', 'KEY', 'RF', 'HBAN', 'FITB', 'ZION',
                'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'O', 'SPG'
            ]
            
            # Get current data for popular stocks
            changes = []
            successful_fetches = 0
            
            for i, symbol in enumerate(popular_stocks):
                try:
                    # Add delay between requests to avoid rate limiting
                    if i > 0:
                        time.sleep(0.1)
                    
                    ticker = yf.Ticker(symbol)
                    ticker._session = session
                    
                    # Get 2 days of data to calculate change
                    hist = ticker.history(period='2d', interval='1d')
                    
                    if not hist.empty and len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change = current - previous
                        change_percent = (change / previous) * 100
                        
                        changes.append({
                            'Symbol': symbol,
                            'Price': current,
                            'Change': change,
                            'Change%': change_percent,
                            'Volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                        })
                        successful_fetches += 1
                        
                        # Limit to first 30 successful fetches for performance
                        if successful_fetches >= 30:
                            break
                            
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    continue
            
            if not changes:
                # Return sample data if no real data available
                sample_changes = [
                    {'Symbol': 'NVDA', 'Price': 485.67, 'Change': 12.34, 'Change%': 2.61, 'Volume': 45678900},
                    {'Symbol': 'TSLA', 'Price': 234.56, 'Change': 8.91, 'Change%': 3.95, 'Volume': 67890100},
                    {'Symbol': 'META', 'Price': 345.78, 'Change': 6.78, 'Change%': 2.00, 'Volume': 34567800},
                    {'Symbol': 'AAPL', 'Price': 178.90, 'Change': 4.56, 'Change%': 2.62, 'Volume': 56789000},
                    {'Symbol': 'MSFT', 'Price': 378.45, 'Change': 3.21, 'Change%': 0.86, 'Volume': 23456700},
                    {'Symbol': 'AMZN', 'Price': 145.67, 'Change': -2.34, 'Change%': -1.58, 'Volume': 45678900},
                    {'Symbol': 'GOOGL', 'Price': 134.56, 'Change': -3.45, 'Change%': -2.50, 'Volume': 34567800},
                    {'Symbol': 'JPM', 'Price': 167.89, 'Change': -4.67, 'Change%': -2.71, 'Volume': 12345600},
                    {'Symbol': 'BAC', 'Price': 34.56, 'Change': -1.23, 'Change%': -3.44, 'Volume': 78901200},
                    {'Symbol': 'WMT', 'Price': 67.89, 'Change': -2.45, 'Change%': -3.48, 'Volume': 23456700}
                ]
                changes = sample_changes
            
            # Sort by percentage change
            changes.sort(key=lambda x: x['Change%'], reverse=True)
            
            # Create top gainers and losers tables
            top_gainers = changes[:5]  # Top 5 gainers
            top_losers = changes[-5:]  # Bottom 5 losers (reverse to show biggest losers first)
            top_losers.reverse()
            
            # Create gainers table
            gainers_rows = []
            for stock in top_gainers:
                volume_str = format_volume(stock['Volume'])
                gainers_rows.append(html.Tr([
                    html.Td(stock['Symbol'], className="stock-symbol"),
                    html.Td(f"${stock['Price']:.2f}", className="stock-price"),
                    html.Td(f"+{stock['Change']:.2f}", className="stock-change positive"),
                    html.Td(f"+{stock['Change%']:.2f}%", className="stock-change positive"),
                    html.Td(volume_str, className="text-muted small")
                ]))
            
            # Create losers table
            losers_rows = []
            for stock in top_losers:
                volume_str = format_volume(stock['Volume'])
                losers_rows.append(html.Tr([
                    html.Td(stock['Symbol'], className="stock-symbol"),
                    html.Td(f"${stock['Price']:.2f}", className="stock-price"),
                    html.Td(f"{stock['Change']:.2f}", className="stock-change negative"),
                    html.Td(f"{stock['Change%']:.2f}%", className="stock-change negative"),
                    html.Td(volume_str, className="text-muted small")
                ]))
            
            return [
                # Market Summary
                html.Div([
                    html.Div([
                        html.Span(f"📊 {len(changes)} stocks tracked", className="badge bg-primary me-2"),
                        html.Span(f"📈 {len(top_gainers)} gainers", className="badge bg-success me-2"),
                        html.Span(f"📉 {len(top_losers)} losers", className="badge bg-danger")
                    ], className="mb-3 text-center")
                ]),
                
                # Top Gainers Section
                html.Div([
                    html.H6([
                        html.I(className="fas fa-arrow-up me-2"),
                        "Top Gainers"
                    ], className="top-movers-title text-success"),
                    html.Div([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Symbol", className="text-muted small"),
                                    html.Th("Price", className="text-muted small"),
                                    html.Th("Change", className="text-muted small"),
                                    html.Th("%", className="text-muted small"),
                                    html.Th("Vol", className="text-muted small")
                                ])
                            ]),
                            html.Tbody(gainers_rows)
                        ], className="table table-sm table-borderless top-movers-table mb-3")
                    ], className="top-movers-border gainers")
                ], className="top-movers-section"),
                
                # Top Losers Section
                html.Div([
                    html.H6([
                        html.I(className="fas fa-arrow-down me-2"),
                        "Top Losers"
                    ], className="top-movers-title text-danger"),
                    html.Div([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Symbol", className="text-muted small"),
                                    html.Th("Price", className="text-muted small"),
                                    html.Th("Change", className="text-muted small"),
                                    html.Th("%", className="text-muted small"),
                                    html.Th("Vol", className="text-muted small")
                                ])
                            ]),
                            html.Tbody(losers_rows)
                        ], className="table table-sm table-borderless top-movers-table")
                    ], className="top-movers-border losers")
                ], className="top-movers-section"),
                
                # Last Updated
                html.Div([
                    html.Small([
                        html.I(className="fas fa-clock me-1"),
                        f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
                    ], className="last-updated")
                ])
            ]
            
        except Exception as e:
            print(f"Error in top movers callback: {str(e)}")
            return [
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Unable to load top movers data. Please try again later.",
                    html.Br(),
                    html.Small(f"Error: {str(e)}", className="text-muted")
                ], color="warning")
            ]
    
    @app.callback(
        Output('sector-performance-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_sector_performance(n):
        """Update sector performance chart with real data"""
        try:
            # Get real sector performance data
            sector_data = market_data.get_sector_performance(period='1mo')
            
            if sector_data.empty:
                # Fallback to empty chart if no data available
                fig = go.Figure()
                fig.add_annotation(
                    text="No sector data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                fig.update_layout(
                    title="Sector Performance (1 Month)",
                    xaxis_title="Sector",
                    yaxis_title="Performance (%)",
                    template="plotly_white",
                    height=300
                )
                return fig
            
            # Create chart with real data
            fig = go.Figure()
            
            # Use daily change percentage for the chart
            sectors = sector_data['Sector'].tolist()
            performance = sector_data['Daily_Change_Pct'].tolist()
            
            # Color bars based on performance (green for positive, red for negative)
            colors = ['green' if p >= 0 else 'red' for p in performance]
            
            fig.add_trace(go.Bar(
                x=sectors,
                y=performance,
                marker_color=colors,
                text=[f'{p:.2f}%' for p in performance],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>' +
                            'Daily Change: %{y:.2f}%<br>' +
                            '<extra></extra>'
            ))
            
            fig.update_layout(
                title="Sector Performance (1 Day)",
                xaxis_title="Sector",
                yaxis_title="Performance (%)",
                template="plotly_white",
                height=300,
                showlegend=False,
                xaxis={'tickangle': 45},
                margin=dict(l=50, r=50, t=80, b=80)
            )
            
            return fig
            
        except Exception as e:
            logging.error(f"Error in sector performance callback: {str(e)}")
            # Return empty chart on error
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error loading data: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(
                title="Sector Performance (1 Day)",
                xaxis_title="Sector",
                yaxis_title="Performance (%)",
                template="plotly_white",
                height=300
            )
            return fig
    
    # Portfolio Export Callbacks
    @app.callback(
        [Output("export-json-btn", "children"),
         Output("download-json", "data")],
        Input("export-json-btn", "n_clicks"),
        State("portfolio-export-data", "data"),
        prevent_initial_call=True
    )
    def export_portfolio_json(n_clicks, portfolio_data):
        """Export portfolio data as JSON"""
        if not n_clicks or not portfolio_data:
            raise dash.exceptions.PreventUpdate
        
        try:
            # Create export data structure
            export_data = {
                'portfolio_info': {
                    'symbols': portfolio_data['symbols'],
                    'optimization_method': portfolio_data['method'],
                    'export_date': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'optimization_results': portfolio_data['result']
            }
            
            # Convert to JSON string
            json_data = json.dumps(export_data, indent=2, default=str)
            
            # Create filename
            filename = f"portfolio_{portfolio_data['method']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            return [
                [html.I(className="fas fa-check me-2"), "Downloaded JSON"],
                dict(content=json_data, filename=filename)
            ]
            
        except Exception as e:
            return [
                [html.I(className="fas fa-exclamation-triangle me-2"), f"Error: {str(e)}"],
                None
            ]
    
    @app.callback(
        [Output("export-csv-btn", "children"),
         Output("download-csv", "data")],
        Input("export-csv-btn", "n_clicks"),
        State("portfolio-export-data", "data"),
        prevent_initial_call=True
    )
    def export_portfolio_csv(n_clicks, portfolio_data):
        """Export portfolio data as CSV"""
        if not n_clicks or not portfolio_data:
            raise dash.exceptions.PreventUpdate
        
        try:
            result = portfolio_data['result']
            symbols = portfolio_data['symbols']
            method = portfolio_data['method']
            
            # Create CSV data with proper headers
            csv_data = []
            
            # Portfolio Summary Header
            csv_data.append(['Portfolio Analysis Report'])
            csv_data.append([f'Optimization Method: {method.replace("_", " ").title()}'])
            csv_data.append([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            csv_data.append([])
            
            # Portfolio Allocation Section
            csv_data.append(['PORTFOLIO ALLOCATION'])
            csv_data.append(['Symbol', 'Weight (%)', 'Current Price ($)', 'Expected Return (%)', 'Volatility (%)', 'Sharpe Ratio'])
            
            if 'optimal_weights' in result and 'stock_metrics' in result:
                for symbol in symbols:
                    weight = result['optimal_weights'].get(symbol, 0) * 100
                    stock_metrics = result['stock_metrics'].get(symbol, {})
                    current_price = stock_metrics.get('current_price', 0)
                    expected_return = stock_metrics.get('expected_return', 0) * 100
                    volatility = stock_metrics.get('volatility', 0) * 100
                    sharpe_ratio = stock_metrics.get('sharpe_ratio', 0)
                    
                    csv_data.append([
                        symbol,
                        f"{weight:.2f}",
                        f"{current_price:.2f}",
                        f"{expected_return:.2f}",
                        f"{volatility:.2f}",
                        f"{sharpe_ratio:.3f}"
                    ])
            else:
                # Fallback if data is missing
                csv_data.append(['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
            csv_data.append([])
            
            # Portfolio Metrics Section
            csv_data.append(['PORTFOLIO METRICS'])
            if 'portfolio_metrics' in result:
                metrics = result['portfolio_metrics']
                csv_data.append(['Metric', 'Value'])
                csv_data.append(['Annual Return (%)', f"{metrics.get('annual_return', 0) * 100:.2f}"])
                csv_data.append(['Annual Volatility (%)', f"{metrics.get('annual_volatility', 0) * 100:.2f}"])
                csv_data.append(['Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.3f}"])
                csv_data.append(['Maximum Drawdown (%)', f"{metrics.get('max_drawdown', 0) * 100:.2f}"])
                csv_data.append(['Value at Risk (5%) (%)', f"{metrics.get('var_5_percent', 0) * 100:.2f}"])
                csv_data.append(['Value at Risk (1%) (%)', f"{metrics.get('var_1_percent', 0) * 100:.2f}"])
                csv_data.append(['Sortino Ratio', f"{metrics.get('sortino_ratio', 0):.3f}"])
            else:
                # Fallback if portfolio metrics are missing
                csv_data.append(['Metric', 'Value'])
                csv_data.append(['Annual Return (%)', 'N/A'])
                csv_data.append(['Annual Volatility (%)', 'N/A'])
                csv_data.append(['Sharpe Ratio', 'N/A'])
                csv_data.append(['Maximum Drawdown (%)', 'N/A'])
                csv_data.append(['Value at Risk (5%) (%)', 'N/A'])
                csv_data.append(['Value at Risk (1%) (%)', 'N/A'])
                csv_data.append(['Sortino Ratio', 'N/A'])
            csv_data.append([])
            
            # Individual Stock Performance Section
            csv_data.append(['INDIVIDUAL STOCK PERFORMANCE'])
            csv_data.append(['Symbol', 'Current Price ($)', 'Expected Return (%)', 'Volatility (%)', 'Sharpe Ratio', 'Weight (%)'])
            
            if 'stock_metrics' in result:
                for symbol in symbols:
                    if symbol in result['stock_metrics']:
                        metrics = result['stock_metrics'][symbol]
                        current_price = metrics.get('current_price', 0)
                        expected_return = metrics.get('expected_return', 0) * 100
                        volatility = metrics.get('volatility', 0) * 100
                        sharpe_ratio = metrics.get('sharpe_ratio', 0)
                        weight = result['optimal_weights'].get(symbol, 0) * 100
                        
                        csv_data.append([
                            symbol,
                            f"{current_price:.2f}",
                            f"{expected_return:.2f}",
                            f"{volatility:.2f}",
                            f"{sharpe_ratio:.3f}",
                            f"{weight:.2f}"
                        ])
            else:
                # Fallback if data is missing
                csv_data.append(['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
            csv_data.append([])
            
            # Risk Analysis Section
            csv_data.append(['RISK ANALYSIS'])
            if 'portfolio_metrics' in result:
                metrics = result['portfolio_metrics']
                csv_data.append(['Risk Metric', 'Value', 'Description'])
                csv_data.append(['Downside Deviation (%)', f"{metrics.get('downside_deviation', 0) * 100:.2f}", 'Downside risk measure'])
            else:
                csv_data.append(['Risk Metric', 'Value', 'Description'])
                csv_data.append(['Downside Deviation (%)', 'N/A', 'Downside risk measure'])
            
            # Convert to CSV string with proper escaping
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            for row in csv_data:
                writer.writerow(row)
            
            csv_string = output.getvalue()
            output.close()
            
            # Create filename with method and timestamp
            filename = f"Portfolio_Analysis_{method.replace('_', '_').title()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return [
                [html.I(className="fas fa-check me-2"), "CSV Downloaded"],
                dict(content=csv_string, filename=filename)
            ]
            
        except Exception as e:
            print(f"Error in CSV export: {str(e)}")
            import traceback
            traceback.print_exc()
            return [
                [html.I(className="fas fa-exclamation-triangle me-2"), f"Error: {str(e)}"],
                None
            ]
    
    @app.callback(
        Output("save-portfolio-btn", "children"),
        Input("save-portfolio-btn", "n_clicks"),
        State("portfolio-export-data", "data"),
        prevent_initial_call=True
    )
    def save_portfolio_to_profile(n_clicks, portfolio_data):
        """Save portfolio to user's profile"""
        if not n_clicks or not portfolio_data:
            raise dash.exceptions.PreventUpdate
        
        try:
            # Check if user is authenticated
            from flask_login import current_user
            if not current_user.is_authenticated:
                return [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Please login to save portfolio"
                ]
            
            # Create portfolio name
            portfolio_name = f"Portfolio_{portfolio_data['method'].replace('_', ' ').title()}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            # Prepare portfolio data for database storage
            portfolio_entry = {
                'symbols': portfolio_data['symbols'],
                'method': portfolio_data['method'],
                'created_date': datetime.now().isoformat(),
                'data': portfolio_data['result']
            }
            
            # Save to user's profile using the auth manager
            auth_manager = app.server.config.get('auth_manager')
            if auth_manager and auth_manager.save_user_portfolio(current_user.id, portfolio_name, portfolio_entry):
                return [
                    html.I(className="fas fa-check me-2"),
                    "Saved to Profile"
                ]
            else:
                return [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Failed to save portfolio"
                ]
            
        except Exception as e:
            return [
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error: {str(e)}"
            ]
    
    @app.callback(
    [Output("generate-report-btn", "children"),
     Output("download-pdf", "data")],
    Input("generate-report-btn", "n_clicks"),
    State("portfolio-export-data", "data"),
    prevent_initial_call=True
)
    def generate_portfolio_report(n_clicks, portfolio_data):
        """Generate a comprehensive portfolio report as PDF"""
        if not n_clicks or not portfolio_data:
            raise dash.exceptions.PreventUpdate
        
        try:
            result = portfolio_data['result']
            symbols = portfolio_data['symbols']
            method = portfolio_data['method']
            
            # Generate PDF using the PDF generation function
            pdf_content = generate_portfolio_pdf(result, symbols, method)
            
            # Encode PDF content to Base64 for JSON serialization
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Create filename with .pdf extension
            filename = f"Portfolio_Report_{method}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
            
            return [
                [html.I(className="fas fa-check me-2"), "PDF Generated"],
                dict(content=pdf_base64, filename=filename, type='application/pdf', base64=True)
            ]
            
        except Exception as e:
            return [
                [html.I(className="fas fa-exclamation-triangle me-2"), f"Error: {str(e)}"],
                None
            ]
    
    return app


# For development
if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)