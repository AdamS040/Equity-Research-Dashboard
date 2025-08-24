"""
Financial Metrics Analysis Module
Comprehensive financial ratio and metric calculations
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class FinancialAnalyzer:
    """
    Comprehensive financial analysis class
    Calculates various financial metrics and ratios
    """
    
    def __init__(self):
        """Initialize the financial analyzer"""
        pass
    
    def calculate_returns(self, prices: pd.Series) -> Dict:
        """
        Calculate various return metrics
        
        Args:
            prices (pd.Series): Stock prices
            
        Returns:
            Dict: Return metrics
        """
        if len(prices) < 2:
            return {}
        
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Daily statistics
        daily_return = returns.mean()
        daily_volatility = returns.std()
        
        # Annualized metrics (assuming 252 trading days)
        annual_return = daily_return * 252
        annual_volatility = daily_volatility * np.sqrt(252)
        
        # Total return
        total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility != 0 else 0
        
        # Calmar ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'daily_return': daily_return,
            'daily_volatility': daily_volatility,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio
        }
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        
        Args:
            data (pd.DataFrame): OHLCV data
            
        Returns:
            pd.DataFrame: Data with technical indicators
        """
        df = data.copy()
        
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Exponential moving averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Stochastic Oscillator
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # On Balance Volume (OBV)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        return df
    
    def calculate_valuation_ratios(self, symbol: str) -> Dict:
        """
        Calculate valuation ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Valuation ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get financial data
            income_stmt = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            # Basic info
            market_cap = info.get('marketCap', 0)
            enterprise_value = info.get('enterpriseValue', market_cap)
            shares_outstanding = info.get('sharesOutstanding', 0)
            current_price = info.get('currentPrice', 0)
            
            # Valuation ratios
            pe_ratio = info.get('trailingPE', 0)
            forward_pe = info.get('forwardPE', 0)
            peg_ratio = info.get('pegRatio', 0)
            pb_ratio = info.get('priceToBook', 0)
            ps_ratio = info.get('priceToSalesTrailing12Months', 0)
            
            # Enterprise ratios
            ev_revenue = info.get('enterpriseToRevenue', 0)
            ev_ebitda = info.get('enterpriseToEbitda', 0)
            
            # Additional metrics
            book_value = info.get('bookValue', 0)
            revenue_per_share = info.get('revenuePerShare', 0)
            
            return {
                'market_cap': market_cap,
                'enterprise_value': enterprise_value,
                'pe_ratio': pe_ratio,
                'forward_pe': forward_pe,
                'peg_ratio': peg_ratio,
                'pb_ratio': pb_ratio,
                'ps_ratio': ps_ratio,
                'ev_revenue': ev_revenue,
                'ev_ebitda': ev_ebitda,
                'book_value': book_value,
                'revenue_per_share': revenue_per_share,
                'current_price': current_price,
                'shares_outstanding': shares_outstanding
            }
            
        except Exception as e:
            print(f"Error calculating valuation ratios for {symbol}: {e}")
            return {}
    
    def calculate_profitability_ratios(self, symbol: str) -> Dict:
        """
        Calculate profitability ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Profitability ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Profitability metrics
            gross_margin = info.get('grossMargins', 0)
            operating_margin = info.get('operatingMargins', 0)
            profit_margin = info.get('profitMargins', 0)
            
            # Return ratios
            roe = info.get('returnOnEquity', 0)
            roa = info.get('returnOnAssets', 0)
            roic = info.get('returnOnCapital', 0)
            
            # Growth rates
            revenue_growth = info.get('revenueGrowth', 0)
            earnings_growth = info.get('earningsGrowth', 0)
            
            return {
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'profit_margin': profit_margin,
                'roe': roe,
                'roa': roa,
                'roic': roic,
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth
            }
            
        except Exception as e:
            print(f"Error calculating profitability ratios for {symbol}: {e}")
            return {}
    
    def calculate_liquidity_ratios(self, symbol: str) -> Dict:
        """
        Calculate liquidity ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Liquidity ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            balance_sheet = ticker.balance_sheet
            
            # Basic liquidity metrics
            current_ratio = info.get('currentRatio', 0)
            quick_ratio = info.get('quickRatio', 0)
            
            # Cash metrics
            total_cash = info.get('totalCash', 0)
            total_debt = info.get('totalDebt', 0)
            net_cash = total_cash - total_debt
            
            # Working capital metrics
            if not balance_sheet.empty and len(balance_sheet.columns) > 0:
                try:
                    current_assets = balance_sheet.loc['Current Assets'].iloc[0]
                    current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0]
                    working_capital = current_assets - current_liabilities
                except:
                    working_capital = 0
            else:
                working_capital = 0
            
            return {
                'current_ratio': current_ratio,
                'quick_ratio': quick_ratio,
                'total_cash': total_cash,
                'total_debt': total_debt,
                'net_cash': net_cash,
                'working_capital': working_capital
            }
            
        except Exception as e:
            print(f"Error calculating liquidity ratios for {symbol}: {e}")
            return {}
    
    def calculate_leverage_ratios(self, symbol: str) -> Dict:
        """
        Calculate leverage ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Leverage ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Debt ratios
            debt_to_equity = info.get('debtToEquity', 0)
            total_debt = info.get('totalDebt', 0)
            total_cash = info.get('totalCash', 0)
            
            # Coverage ratios
            interest_coverage = info.get('interestCoverage', 0)
            
            # Additional metrics
            enterprise_value = info.get('enterpriseValue', 0)
            market_cap = info.get('marketCap', 0)
            
            return {
                'debt_to_equity': debt_to_equity,
                'total_debt': total_debt,
                'total_cash': total_cash,
                'interest_coverage': interest_coverage,
                'enterprise_value': enterprise_value,
                'market_cap': market_cap
            }
            
        except Exception as e:
            print(f"Error calculating leverage ratios for {symbol}: {e}")
            return {}
    
    def calculate_efficiency_ratios(self, symbol: str) -> Dict:
        """
        Calculate efficiency ratios
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Efficiency ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Turnover ratios (simplified - would need more detailed financial data)
            asset_turnover = info.get('assetTurnover', 0)
            inventory_turnover = info.get('inventoryTurnover', 0)
            receivables_turnover = info.get('receivablesTurnover', 0)
            
            # Days metrics
            days_sales_outstanding = 365 / receivables_turnover if receivables_turnover > 0 else 0
            days_inventory_outstanding = 365 / inventory_turnover if inventory_turnover > 0 else 0
            
            return {
                'asset_turnover': asset_turnover,
                'inventory_turnover': inventory_turnover,
                'receivables_turnover': receivables_turnover,
                'days_sales_outstanding': days_sales_outstanding,
                'days_inventory_outstanding': days_inventory_outstanding
            }
            
        except Exception as e:
            print(f"Error calculating efficiency ratios for {symbol}: {e}")
            return {}
    
    def calculate_beta(self, stock_prices: pd.Series, market_prices: pd.Series) -> float:
        """
        Calculate beta coefficient
        
        Args:
            stock_prices (pd.Series): Stock prices
            market_prices (pd.Series): Market/benchmark prices
            
        Returns:
            float: Beta coefficient
        """
        try:
            # Calculate returns
            stock_returns = stock_prices.pct_change().dropna()
            market_returns = market_prices.pct_change().dropna()
            
            # Align data
            aligned_data = pd.concat([stock_returns, market_returns], axis=1, join='inner')
            aligned_data.columns = ['stock', 'market']
            aligned_data = aligned_data.dropna()
            
            if len(aligned_data) < 10:  # Need sufficient data points
                return 1.0
            
            # Calculate beta
            covariance = np.cov(aligned_data['stock'], aligned_data['market'])[0][1]
            market_variance = np.var(aligned_data['market'])
            
            beta = covariance / market_variance if market_variance != 0 else 1.0
            
            return beta
            
        except Exception as e:
            print(f"Error calculating beta: {e}")
            return 1.0
    
    def calculate_alpha(self, stock_prices: pd.Series, market_prices: pd.Series, 
                       risk_free_rate: float = 0.02) -> float:
        """
        Calculate alpha (Jensen's alpha)
        
        Args:
            stock_prices (pd.Series): Stock prices
            market_prices (pd.Series): Market/benchmark prices
            risk_free_rate (float): Risk-free rate
            
        Returns:
            float: Alpha coefficient
        """
        try:
            # Calculate returns
            stock_returns = stock_prices.pct_change().dropna()
            market_returns = market_prices.pct_change().dropna()
            
            # Align data
            aligned_data = pd.concat([stock_returns, market_returns], axis=1, join='inner')
            aligned_data.columns = ['stock', 'market']
            aligned_data = aligned_data.dropna()
            
            if len(aligned_data) < 10:
                return 0.0
            
            # Calculate beta first
            beta = self.calculate_beta(stock_prices, market_prices)
            
            # Calculate average returns (annualized)
            avg_stock_return = aligned_data['stock'].mean() * 252
            avg_market_return = aligned_data['market'].mean() * 252
            
            # Calculate alpha using CAPM
            expected_return = risk_free_rate + beta * (avg_market_return - risk_free_rate)
            alpha = avg_stock_return - expected_return
            
            return alpha
            
        except Exception as e:
            print(f"Error calculating alpha: {e}")
            return 0.0
    
    def comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Perform comprehensive financial analysis
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Comprehensive analysis results
        """
        # Get stock data
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period='2y')
        
        # Calculate various metrics
        returns_analysis = self.calculate_returns(hist_data['Close'])
        technical_indicators = self.calculate_technical_indicators(hist_data)
        valuation_ratios = self.calculate_valuation_ratios(symbol)
        profitability_ratios = self.calculate_profitability_ratios(symbol)
        liquidity_ratios = self.calculate_liquidity_ratios(symbol)
        leverage_ratios = self.calculate_leverage_ratios(symbol)
        efficiency_ratios = self.calculate_efficiency_ratios(symbol)
        
        # Calculate beta vs S&P 500
        sp500_data = yf.download('^GSPC', period='2y')['Close']
        beta = self.calculate_beta(hist_data['Close'], sp500_data)
        alpha = self.calculate_alpha(hist_data['Close'], sp500_data)
        
        return {
            'symbol': symbol,
            'returns_analysis': returns_analysis,
            'valuation_ratios': valuation_ratios,
            'profitability_ratios': profitability_ratios,
            'liquidity_ratios': liquidity_ratios,
            'leverage_ratios': leverage_ratios,
            'efficiency_ratios': efficiency_ratios,
            'beta': beta,
            'alpha': alpha,
            'technical_data': technical_indicators.tail(1).to_dict('records')[0] if not technical_indicators.empty else {}
        }