"""
Chart Generation Module
Comprehensive financial chart creation and visualization
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_chart_data(stock_data, required_keys):
    """Check if required data keys exist and have valid values"""
    missing_keys = []
    for key in required_keys:
        if key not in stock_data or stock_data[key] is None or (hasattr(stock_data[key], 'isna') and stock_data[key].isna().all()):
            missing_keys.append(key)
    return missing_keys

def create_empty_chart_with_message(message: str, title: str = "Chart Unavailable") -> go.Figure:
    """Create a placeholder chart with a message when data is missing"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        xanchor='center', yanchor='middle',
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        title=title,
        template='plotly_white',
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

def validate_dataframe(data: pd.DataFrame, min_rows: int = 1) -> bool:
    """Validate if DataFrame has sufficient data for charting"""
    if data is None or data.empty or len(data) < min_rows:
        return False
    return True

def safe_calculate_returns(data: pd.DataFrame) -> Optional[pd.Series]:
    """Safely calculate returns with error handling"""
    try:
        if not validate_dataframe(data, 2):
            return None
        if 'Close' not in data.columns:
            return None
        returns = data['Close'].pct_change().dropna()
        if len(returns) == 0:
            return None
        return returns
    except Exception as e:
        logger.warning(f"Error calculating returns: {e}")
        return None

class ChartGenerator:
    """
    Comprehensive chart generation for financial data
    """
    
    def __init__(self):
        """Initialize chart generator"""
        pass
    
    def create_price_chart(self, symbol: str, period: str = '1y', 
                          show_volume: bool = True) -> go.Figure:
        """
        Create comprehensive price chart with technical indicators
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period
            show_volume (bool): Whether to show volume
            
        Returns:
            go.Figure: Price chart
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return go.Figure()
            
            # Create candlestick chart
            fig = go.Figure()
            
            # Candlestick trace
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color='#26A69A',
                decreasing_line_color='#EF5350'
            ))
            
            # Add moving averages
            ma20 = data['Close'].rolling(window=20).mean()
            ma50 = data['Close'].rolling(window=50).mean()
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=ma20,
                mode='lines',
                name='MA20',
                line=dict(color='orange', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=ma50,
                mode='lines',
                name='MA50',
                line=dict(color='blue', width=1)
            ))
            
            # Volume subplot
            if show_volume:
                fig.add_trace(go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    yaxis='y2',
                    marker_color='rgba(100, 100, 100, 0.3)'
                ))
            
            # Update layout
            fig.update_layout(
                title=f'{symbol} Price Chart',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                template='plotly_white',
                height=600,
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ) if show_volume else None,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating price chart for {symbol}: {e}")
            return go.Figure()
    
    def create_technical_indicators_chart(self, symbol: str, period: str = '1y') -> go.Figure:
        """
        Create technical indicators chart
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period
            
        Returns:
            go.Figure: Technical indicators chart
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return go.Figure()
            
            # Calculate technical indicators
            close = data['Close']
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            
            # Bollinger Bands
            ma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            upper_band = ma20 + (std20 * 2)
            lower_band = ma20 - (std20 * 2)
            
            # Create subplots
            fig = go.Figure()
            
            # Price and Bollinger Bands
            fig.add_trace(go.Scatter(
                x=data.index,
                y=close,
                mode='lines',
                name='Price',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=upper_band,
                mode='lines',
                name='Upper BB',
                line=dict(color='rgba(255,0,0,0.3)', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=lower_band,
                mode='lines',
                name='Lower BB',
                line=dict(color='rgba(255,0,0,0.3)', width=1),
                fill='tonexty'
            ))
            
            # RSI
            fig.add_trace(go.Scatter(
                x=data.index,
                y=rsi,
                mode='lines',
                name='RSI',
                yaxis='y2',
                line=dict(color='purple', width=1)
            ))
            
            # Add RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", yaxis='y2')
            fig.add_hline(y=30, line_dash="dash", line_color="green", yaxis='y2')
            
            # MACD
            fig.add_trace(go.Scatter(
                x=data.index,
                y=macd,
                mode='lines',
                name='MACD',
                yaxis='y3',
                line=dict(color='blue', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=signal,
                mode='lines',
                name='Signal',
                yaxis='y3',
                line=dict(color='red', width=1)
            ))
            
            fig.add_trace(go.Bar(
                x=data.index,
                y=histogram,
                name='Histogram',
                yaxis='y3',
                marker_color='gray'
            ))
            
            # Update layout
            fig.update_layout(
                title=f'{symbol} Technical Indicators',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                template='plotly_white',
                height=800,
                yaxis2=dict(
                    title='RSI',
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                yaxis3=dict(
                    title='MACD',
                    overlaying='y',
                    side='right',
                    anchor='free',
                    position=0.95
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating technical indicators chart for {symbol}: {e}")
            return go.Figure()
    
    def create_returns_distribution_chart(self, symbol: str, period: str = '1y') -> go.Figure:
        """
        Create returns distribution chart
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period
            
        Returns:
            go.Figure: Returns distribution chart
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return go.Figure()
            
            returns = data['Close'].pct_change().dropna()
            
            # Create histogram
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=returns,
                nbinsx=50,
                name='Returns',
                marker_color='rgba(100, 100, 100, 0.7)'
            ))
            
            # Add normal distribution overlay
            mu = returns.mean()
            sigma = returns.std()
            x_norm = np.linspace(returns.min(), returns.max(), 100)
            y_norm = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_norm - mu) / sigma) ** 2)
            y_norm = y_norm * len(returns) * (returns.max() - returns.min()) / 50  # Scale to histogram
            
            fig.add_trace(go.Scatter(
                x=x_norm,
                y=y_norm,
                mode='lines',
                name='Normal Distribution',
                line=dict(color='red', width=2)
            ))
            
            # Add vertical line for mean
            fig.add_vline(x=mu, line_dash="dash", line_color="blue", annotation_text=f"Mean: {mu:.4f}")
            
            fig.update_layout(
                title=f'{symbol} Returns Distribution',
                xaxis_title='Returns',
                yaxis_title='Frequency',
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating returns distribution chart for {symbol}: {e}")
            return go.Figure()
    
    def create_correlation_heatmap(self, symbols: List[str], period: str = '1y') -> go.Figure:
        """
        Create correlation heatmap for multiple stocks
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period
            
        Returns:
            go.Figure: Correlation heatmap
        """
        try:
            returns_data = {}
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return go.Figure()
            
            # Create correlation matrix
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=correlation_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='Stock Correlation Matrix',
                template='plotly_white',
                height=600,
                width=600
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating correlation heatmap: {e}")
            return go.Figure()
    
    def create_portfolio_performance_chart(self, symbols: List[str], weights: List[float], 
                                         period: str = '1y') -> go.Figure:
        """
        Create portfolio performance comparison chart
        
        Args:
            symbols (List[str]): List of stock symbols
            weights (List[float]): Portfolio weights
            period (str): Time period
            
        Returns:
            go.Figure: Portfolio performance chart
        """
        try:
            if len(symbols) != len(weights):
                return go.Figure()
            
            # Get data for all stocks
            returns_data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return go.Figure()
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            # Calculate portfolio returns
            weights_array = np.array(weights)
            portfolio_returns = returns_df.dot(weights_array)
            
            # Calculate cumulative returns
            portfolio_cumulative = (1 + portfolio_returns).cumprod()
            
            # Calculate individual stock cumulative returns
            individual_cumulative = {}
            for symbol in symbols:
                if symbol in returns_df.columns:
                    individual_cumulative[symbol] = (1 + returns_df[symbol]).cumprod()
            
            # Create chart
            fig = go.Figure()
            
            # Portfolio performance
            fig.add_trace(go.Scatter(
                x=portfolio_cumulative.index,
                y=portfolio_cumulative,
                mode='lines',
                name='Portfolio',
                line=dict(color='black', width=3)
            ))
            
            # Individual stock performance
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            for i, symbol in enumerate(symbols):
                if symbol in individual_cumulative:
                    color = colors[i % len(colors)]
                    fig.add_trace(go.Scatter(
                        x=individual_cumulative[symbol].index,
                        y=individual_cumulative[symbol],
                        mode='lines',
                        name=symbol,
                        line=dict(color=color, width=1)
                    ))
            
            fig.update_layout(
                title='Portfolio Performance Comparison',
                xaxis_title='Date',
                yaxis_title='Cumulative Return',
                template='plotly_white',
                height=600,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating portfolio performance chart: {e}")
            return go.Figure()
    
    def create_risk_return_scatter(self, symbols: List[str], period: str = '1y') -> go.Figure:
        """
        Create risk-return scatter plot
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period
            
        Returns:
            go.Figure: Risk-return scatter plot
        """
        try:
            risk_return_data = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    
                    # Calculate metrics
                    annual_return = returns.mean() * 252
                    annual_volatility = returns.std() * np.sqrt(252)
                    sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
                    
                    risk_return_data.append({
                        'Symbol': symbol,
                        'Return': annual_return,
                        'Risk': annual_volatility,
                        'Sharpe': sharpe_ratio
                    })
            
            if not risk_return_data:
                return go.Figure()
            
            df = pd.DataFrame(risk_return_data)
            
            # Create scatter plot
            fig = px.scatter(
                df,
                x='Risk',
                y='Return',
                size='Sharpe',
                color='Sharpe',
                hover_name='Symbol',
                text='Symbol',
                title='Risk-Return Analysis',
                color_continuous_scale='RdYlGn',
                size_max=20
            )
            
            # Add efficient frontier line (simplified)
            min_risk = df['Risk'].min()
            max_risk = df['Risk'].max()
            risk_range = np.linspace(min_risk, max_risk, 100)
            
            # Simple efficient frontier approximation
            efficient_frontier = risk_range * 0.5  # Simplified relationship
            
            fig.add_trace(go.Scatter(
                x=risk_range,
                y=efficient_frontier,
                mode='lines',
                name='Efficient Frontier',
                line=dict(color='black', width=2, dash='dash')
            ))
            
            fig.update_layout(
                template='plotly_white',
                height=600,
                xaxis_title='Annual Volatility (Risk)',
                yaxis_title='Annual Return',
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating risk-return scatter plot: {e}")
            return go.Figure()
    
    def create_sector_performance_chart(self, sector_etfs: Dict[str, str], 
                                      period: str = '1y') -> go.Figure:
        """
        Create sector performance comparison chart
        
        Args:
            sector_etfs (Dict[str, str]): Dictionary of sector names and ETF symbols
            period (str): Time period
            
        Returns:
            go.Figure: Sector performance chart
        """
        try:
            sector_data = {}
            
            for sector_name, etf_symbol in sector_etfs.items():
                ticker = yf.Ticker(etf_symbol)
                data = ticker.history(period=period)
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    cumulative = (1 + returns).cumprod()
                    sector_data[sector_name] = cumulative
            
            if not sector_data:
                return go.Figure()
            
            # Create chart
            fig = go.Figure()
            
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta', 'yellow']
            
            for i, (sector_name, cumulative_returns) in enumerate(sector_data.items()):
                color = colors[i % len(colors)]
                fig.add_trace(go.Scatter(
                    x=cumulative_returns.index,
                    y=cumulative_returns,
                    mode='lines',
                    name=sector_name,
                    line=dict(color=color, width=2)
                ))
            
            fig.update_layout(
                title='Sector Performance Comparison',
                xaxis_title='Date',
                yaxis_title='Cumulative Return',
                template='plotly_white',
                height=600,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating sector performance chart: {e}")
            return go.Figure()
    
    def create_earnings_chart(self, symbol: str) -> go.Figure:
        """
        Create earnings and revenue chart
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            go.Figure: Earnings chart
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get financial data
            income_stmt = ticker.income_stmt
            if income_stmt.empty:
                return go.Figure()
            
            # Extract data
            revenue = income_stmt.loc['Total Revenue'] if 'Total Revenue' in income_stmt.index else pd.Series()
            net_income = income_stmt.loc['Net Income'] if 'Net Income' in income_stmt.index else pd.Series()
            
            if revenue.empty or net_income.empty:
                return go.Figure()
            
            # Create chart
            fig = go.Figure()
            
            # Revenue
            fig.add_trace(go.Bar(
                x=revenue.index,
                y=revenue / 1e9,  # Convert to billions
                name='Revenue (Billions)',
                marker_color='blue'
            ))
            
            # Net Income
            fig.add_trace(go.Bar(
                x=net_income.index,
                y=net_income / 1e9,  # Convert to billions
                name='Net Income (Billions)',
                marker_color='green'
            ))
            
            fig.update_layout(
                title=f'{symbol} Financial Performance',
                xaxis_title='Year',
                yaxis_title='Amount (Billions $)',
                template='plotly_white',
                height=500,
                barmode='group'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating earnings chart for {symbol}: {e}")
            return go.Figure()
    
    def create_valuation_comparison_chart(self, symbol: str, peer_symbols: List[str]) -> go.Figure:
        """
        Create valuation comparison chart
        
        Args:
            symbol (str): Target stock symbol
            peer_symbols (List[str]): List of peer symbols
            
        Returns:
            go.Figure: Valuation comparison chart
        """
        try:
            all_symbols = [symbol] + peer_symbols
            valuation_data = []
            
            for sym in all_symbols:
                ticker = yf.Ticker(sym)
                info = ticker.info
                
                if info:
                    valuation_data.append({
                        'Symbol': sym,
                        'P/E Ratio': info.get('trailingPE', 0),
                        'P/B Ratio': info.get('priceToBook', 0),
                        'P/S Ratio': info.get('priceToSalesTrailing12Months', 0),
                        'EV/EBITDA': info.get('enterpriseToEbitda', 0)
                    })
            
            if not valuation_data:
                return go.Figure()
            
            df = pd.DataFrame(valuation_data)
            
            # Create subplots for different metrics
            fig = go.Figure()
            
            metrics = ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'EV/EBITDA']
            colors = ['blue', 'red', 'green', 'orange']
            
            for i, metric in enumerate(metrics):
                fig.add_trace(go.Bar(
                    x=df['Symbol'],
                    y=df[metric],
                    name=metric,
                    marker_color=colors[i],
                    yaxis=f'y{i+1}' if i > 0 else 'y'
                ))
            
            # Update layout for subplots
            fig.update_layout(
                title=f'{symbol} Valuation Comparison',
                template='plotly_white',
                height=600,
                barmode='group',
                yaxis=dict(title='P/E Ratio'),
                yaxis2=dict(title='P/B Ratio', overlaying='y', side='right'),
                yaxis3=dict(title='P/S Ratio', overlaying='y', side='right', anchor='free', position=0.95),
                yaxis4=dict(title='EV/EBITDA', overlaying='y', side='right', anchor='free', position=0.9)
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating valuation comparison chart: {e}")
       
            return go.Figure()
