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
                                        value="AAPL,GOOGL,MSFT,AMZN,TSLA"
                                    ),
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Optimization Method:"),
                                    dcc.Dropdown(
                                        id="optimization-method",
                                        options=[
                                            {'label': 'Maximum Sharpe Ratio', 'value': 'max_sharpe'},
                                            {'label': 'Minimum Volatility', 'value': 'min_vol'},
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
                                ], width=12),
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
            html.Div(id="portfolio-loading", style={"display": "none"}),
            
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
        [Input("optimize-button", "n_clicks")],
        [State("portfolio-stocks-input", "value"),
         State("optimization-method", "value"),
         State("portfolio-period", "value"),
         State("target-return-input", "value"),
         State("max-weight-input", "value"),
         State("min-weight-input", "value"),
         State("risk-free-rate-input", "value"),
         State("rebalancing-frequency", "value")]
    )
    def update_portfolio_optimization(n_clicks, stocks_input, method, period, target_return, 
                                    max_weight, min_weight, risk_free_rate, rebalancing_frequency):
        # Prevent callback from firing if no button click
        if not n_clicks or not stocks_input:
            return [], [], [], {"display": "none"}
        
        # Show loading state
        loading_style = {"display": "block"}
        
        try:
            # Parse stock symbols
            symbols = [s.strip().upper() for s in stocks_input.split(',')]
            
            # Validate symbols
            if not symbols or len(symbols) < 2:
                error_alert = dbc.Alert("Please enter at least 2 stock symbols separated by commas.", color="warning")
                return [error_alert], [], [], {"display": "none"}
            
            # Set default values
            period = period or '1y'
            risk_free_rate = risk_free_rate or 0.02
            max_weight = max_weight or 0.4
            min_weight = min_weight or 0.01
            
            # Create constraints dictionary
            constraints = {
                'min_weight': min_weight,
                'max_weight': max_weight
            }
            
            # Initialize portfolio optimizer with user-defined risk-free rate
            portfolio_optimizer = PortfolioOptimizer(risk_free_rate=risk_free_rate)
            
            # Optimize portfolio
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
            
            # Create results displays
            results_display = create_portfolio_results_display(result, symbols, method)
            comparison_display = create_portfolio_comparison_display(result, symbols, method)
            export_display = create_portfolio_export_display(result, symbols, method)
            
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
    
    # Helper functions for portfolio optimization display
    def create_portfolio_results_display(result, symbols, method):
        """Create the main portfolio results display"""
        optimal_weights = result['optimal_weights']
        portfolio_metrics = result['portfolio_metrics']
        stock_metrics = result['stock_metrics']
        
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
            title="Asset Allocation",
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
            title="Performance Comparison",
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
        if 'efficient_frontier' not in result:
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
                            ], color="primary", className="w-100 mb-2")
                        ], width=3),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-file-csv me-2"),
                                "Export as CSV"
                            ], color="success", className="w-100 mb-2")
                        ], width=3),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-save me-2"),
                                "Save to Portfolio Library"
                            ], color="info", className="w-100 mb-2")
                        ], width=3),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-file-pdf me-2"),
                                "Generate Report"
                            ], color="warning", className="w-100 mb-2")
                        ], width=3)
                    ])
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
        return [
            dbc.Alert("Valuation report functionality would be implemented here", color="info")
        ]
    
    def generate_risk_report(symbol, stock, info, hist):
        """Generate risk assessment report"""
        return [
            dbc.Alert("Risk assessment report functionality would be implemented here", color="info")
        ]
    
    def generate_peer_report(symbol, stock, info, hist):
        """Generate peer comparison report"""
        return [
            dbc.Alert("Peer comparison report functionality would be implemented here", color="info")
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
                'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA',
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
        """Update sector performance chart"""
        try:
            # Create a sample sector performance chart
            fig = go.Figure()
            sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 'Communication Services']
            performance = [2.5, 1.8, -0.5, 3.2, 1.1]  # Sample data
            
            fig.add_trace(go.Bar(
                x=sectors,
                y=performance,
                marker_color=['green' if p > 0 else 'red' for p in performance]
            ))
            
            fig.update_layout(
                title="Sector Performance (1 Day)",
                xaxis_title="Sector",
                yaxis_title="Performance (%)",
                template="plotly_white",
                height=300
            )
            
            return fig
        except Exception as e:
            print(f"Error in sector performance callback: {str(e)}")
            return go.Figure()
    
    return app


# For development
if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)