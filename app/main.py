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

def create_app(config_name='development'):
    """Create and configure the Dash application"""
    
    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    
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
        # Header
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
                        dbc.CardHeader("Top Movers"),
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
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Portfolio Construction"),
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
                                        ],
                                        value='max_sharpe'
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Br(),
                                    dbc.Button(
                                        "Optimize",
                                        id="optimize-button",
                                        color="success",
                                        className="mt-2"
                                    )
                                ], width=2),
                            ])
                        ])
                    ])
                ], width=12),
            ]),
            
            # Portfolio Results
            html.Div(id="portfolio-results", className="mt-4")
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
    
    # Market data callback
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
        [Input("interval-component", "n_intervals")]
    )
    def update_market_data(n):
        try:
            # Fetch market data
            indices = ['^GSPC', '^IXIC', '^VIX', '^TNX']
            data = yf.download(indices, period='5d', interval='1d')
            
            results = []
            for symbol in indices:
                if symbol in data['Close'].columns:
                    current = data['Close'][symbol].iloc[-1]
                    previous = data['Close'][symbol].iloc[-2]
                    change = current - previous
                    change_pct = (change / previous) * 100
                    
                    price_str = f"${current:.2f}" if symbol != '^VIX' else f"{current:.2f}"
                    if symbol == '^TNX':
                        price_str = f"{current:.2f}%"
                    
                    change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                    results.extend([price_str, change_str])
                else:
                    results.extend(["N/A", "N/A"])
            
            # Create market performance chart
            fig = go.Figure()
            for symbol, name in zip(['^GSPC', '^IXIC'], ['S&P 500', 'NASDAQ']):
                if symbol in data['Close'].columns:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Close'][symbol],
                        mode='lines',
                        name=name,
                        line=dict(width=2)
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
        if not n_clicks or not symbol:
            return []
        
        try:
            # Fetch stock data
            stock = yf.Ticker(symbol.upper())
            hist = stock.history(period=period)
            info = stock.info
            
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
            return [
                dbc.Alert(f"Error analyzing {symbol}: {str(e)}", color="danger")
            ]
    
    # Portfolio optimization callback
    @app.callback(
        Output("portfolio-results", "children"),
        [Input("optimize-button", "n_clicks")],
        [State("portfolio-stocks-input", "value"),
         State("optimization-method", "value")]
    )
    def update_portfolio_optimization(n_clicks, stocks_input, method):
        if not n_clicks or not stocks_input:
            return []
        
        try:
            # Parse stock symbols
            symbols = [s.strip().upper() for s in stocks_input.split(',')]
            
            # Fetch data
            data = yf.download(symbols, period='1y')['Close']
            returns = data.pct_change().dropna()
            
            # Calculate portfolio metrics based on method
            if method == 'equal_weight':
                weights = np.array([1/len(symbols)] * len(symbols))
            else:
                # Simple optimization (you can enhance this)
                cov_matrix = returns.cov()
                if method == 'min_vol':
                    # Minimum volatility
                    inv_cov = np.linalg.pinv(cov_matrix)
                    ones = np.ones((len(symbols), 1))
                    weights = (inv_cov @ ones) / (ones.T @ inv_cov @ ones)
                    weights = weights.flatten()
                else:  # max_sharpe
                    # Simple equal weight for now (enhance with proper optimization)
                    weights = np.array([1/len(symbols)] * len(symbols))
            
            # Ensure weights sum to 1 and are positive
            weights = np.abs(weights)
            weights = weights / weights.sum()
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(returns.mean() * weights) * 252
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Create allocation chart
            allocation_fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=weights,
                hole=.3
            )])
            allocation_fig.update_traces(textposition='inside', textinfo='percent+label')
            allocation_fig.update_layout(
                title="Portfolio Allocation",
                template="plotly_white",
                height=400
            )
            
            # Portfolio performance
            portfolio_values = (returns @ weights).cumsum()
            performance_fig = go.Figure()
            performance_fig.add_trace(go.Scatter(
                x=portfolio_values.index,
                y=portfolio_values,
                mode='lines',
                name='Portfolio',
                line=dict(color='green', width=2)
            ))
            performance_fig.update_layout(
                title="Portfolio Cumulative Returns",
                xaxis_title="Date",
                yaxis_title="Cumulative Return",
                template="plotly_white",
                height=400
            )
            
            # Allocation table
            allocation_data = pd.DataFrame({
                'Symbol': symbols,
                'Weight': [f"{w:.1%}" for w in weights],
                'Current Price': [f"${data[symbol].iloc[-1]:.2f}" for symbol in symbols]
            })
            
            allocation_table = dash_table.DataTable(
                data=allocation_data.to_dict('records'),
                columns=[{"name": i, "id": i} for i in allocation_data.columns],
                style_cell={'textAlign': 'center'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
            )
            
            return [
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Portfolio Metrics"),
                            dbc.CardBody([
                                html.H5(f"Expected Annual Return: {portfolio_return:.2%}"),
                                html.H5(f"Annual Volatility: {portfolio_volatility:.2%}"),
                                html.H5(f"Sharpe Ratio: {sharpe_ratio:.2f}"),
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Asset Allocation"),
                            dbc.CardBody([
                                dcc.Graph(figure=allocation_fig)
                            ])
                        ])
                    ], width=8),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Portfolio Performance"),
                            dbc.CardBody([
                                dcc.Graph(figure=performance_fig)
                            ])
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Holdings"),
                            dbc.CardBody([
                                allocation_table
                            ])
                        ])
                    ], width=4),
                ], className="mt-4")
            ]
            
        except Exception as e:
            return [
                dbc.Alert(f"Error optimizing portfolio: {str(e)}", color="danger")
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
    
    return app


# For development
if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)