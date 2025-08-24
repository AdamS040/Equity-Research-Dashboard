"""
Risk Analysis Module
Comprehensive risk assessment and analysis tools
"""
import pandas as pd
import numpy as np
import yfinance as yf
from scipy import stats
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class RiskAnalyzer:
    """
    Comprehensive risk analysis and assessment
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize risk analyzer
        
        Args:
            risk_free_rate (float): Risk-free rate for calculations
        """
        self.risk_free_rate = risk_free_rate
    
    def get_stock_data(self, symbol: str, period: str = '2y') -> pd.DataFrame:
        """
        Get stock price data for risk analysis
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for historical data
            
        Returns:
            pd.DataFrame: Stock price data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_volatility(self, symbol: str, period: str = '1y', 
                           window: int = 252) -> Dict:
        """
        Calculate historical and rolling volatility
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for data
            window (int): Rolling window size
            
        Returns:
            Dict: Volatility metrics
        """
        try:
            data = self.get_stock_data(symbol, period)
            if data.empty:
                return {}
            
            returns = data['Close'].pct_change().dropna()
            
            # Historical volatility (annualized)
            hist_vol = returns.std() * np.sqrt(252)
            
            # Rolling volatility
            rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
            
            # Volatility of volatility
            vol_of_vol = rolling_vol.std()
            
            return {
                'historical_volatility': hist_vol,
                'current_volatility': rolling_vol.iloc[-1] if not rolling_vol.empty else hist_vol,
                'volatility_of_volatility': vol_of_vol,
                'min_volatility': rolling_vol.min(),
                'max_volatility': rolling_vol.max(),
                'volatility_percentile': stats.percentileofscore(rolling_vol.dropna(), rolling_vol.iloc[-1]) if not rolling_vol.empty else 50
            }
            
        except Exception as e:
            print(f"Error calculating volatility for {symbol}: {e}")
            return {}
    
    def calculate_var(self, symbol: str, confidence_level: float = 0.05, 
                     period: str = '1y', method: str = 'historical') -> Dict:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            symbol (str): Stock symbol
            confidence_level (float): VaR confidence level (e.g., 0.05 for 95% VaR)
            period (str): Time period for data
            method (str): VaR calculation method ('historical', 'parametric', 'monte_carlo')
            
        Returns:
            Dict: VaR metrics
        """
        try:
            data = self.get_stock_data(symbol, period)
            if data.empty:
                return {}
            
            returns = data['Close'].pct_change().dropna()
            current_price = data['Close'].iloc[-1]
            
            if method == 'historical':
                var_daily = np.percentile(returns, confidence_level * 100)
                var_annual = var_daily * np.sqrt(252)
                
            elif method == 'parametric':
                # Assuming normal distribution
                mean_return = returns.mean()
                std_return = returns.std()
                var_daily = stats.norm.ppf(confidence_level, mean_return, std_return)
                var_annual = var_daily * np.sqrt(252)
                
            else:  # monte_carlo
                # Simple Monte Carlo simulation
                n_simulations = 10000
                simulated_returns = np.random.normal(returns.mean(), returns.std(), n_simulations)
                var_daily = np.percentile(simulated_returns, confidence_level * 100)
                var_annual = var_daily * np.sqrt(252)
            
            # Calculate VaR in dollar terms
            var_dollar_daily = abs(var_daily) * current_price
            var_dollar_annual = abs(var_annual) * current_price
            
            return {
                'var_daily': var_daily,
                'var_annual': var_annual,
                'var_dollar_daily': var_dollar_daily,
                'var_dollar_annual': var_dollar_annual,
                'confidence_level': confidence_level,
                'method': method
            }
            
        except Exception as e:
            print(f"Error calculating VaR for {symbol}: {e}")
            return {}
    
    def calculate_beta(self, symbol: str, market_symbol: str = '^GSPC', 
                      period: str = '1y') -> Dict:
        """
        Calculate beta relative to market
        
        Args:
            symbol (str): Stock symbol
            market_symbol (str): Market index symbol
            period (str): Time period for data
            
        Returns:
            Dict: Beta metrics
        """
        try:
            # Get stock and market data
            stock_data = self.get_stock_data(symbol, period)
            market_data = self.get_stock_data(market_symbol, period)
            
            if stock_data.empty or market_data.empty:
                return {}
            
            # Calculate returns
            stock_returns = stock_data['Close'].pct_change().dropna()
            market_returns = market_data['Close'].pct_change().dropna()
            
            # Align data
            aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
            if len(aligned_data) < 30:  # Need sufficient data
                return {}
            
            stock_ret = aligned_data.iloc[:, 0]
            market_ret = aligned_data.iloc[:, 1]
            
            # Calculate beta
            covariance = np.cov(stock_ret, market_ret)[0, 1]
            market_variance = np.var(market_ret)
            beta = covariance / market_variance if market_variance > 0 else 1.0
            
            # Calculate R-squared
            correlation = np.corrcoef(stock_ret, market_ret)[0, 1]
            r_squared = correlation ** 2
            
            # Calculate alpha (excess return)
            stock_mean = stock_ret.mean() * 252
            market_mean = market_ret.mean() * 252
            alpha = stock_mean - (self.risk_free_rate + beta * (market_mean - self.risk_free_rate))
            
            return {
                'beta': beta,
                'alpha': alpha,
                'r_squared': r_squared,
                'correlation': correlation,
                'market_symbol': market_symbol
            }
            
        except Exception as e:
            print(f"Error calculating beta for {symbol}: {e}")
            return {}
    
    def calculate_drawdown(self, symbol: str, period: str = '2y') -> Dict:
        """
        Calculate maximum drawdown and related metrics
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for data
            
        Returns:
            Dict: Drawdown metrics
        """
        try:
            data = self.get_stock_data(symbol, period)
            if data.empty:
                return {}
            
            prices = data['Close']
            cumulative_returns = (prices / prices.iloc[0]) - 1
            
            # Calculate rolling maximum
            rolling_max = cumulative_returns.expanding().max()
            drawdown = cumulative_returns - rolling_max
            
            # Maximum drawdown
            max_drawdown = drawdown.min()
            max_drawdown_pct = max_drawdown * 100
            
            # Find drawdown duration
            drawdown_periods = (drawdown < 0).sum()
            total_periods = len(drawdown)
            drawdown_duration = drawdown_periods / total_periods if total_periods > 0 else 0
            
            # Current drawdown
            current_drawdown = drawdown.iloc[-1]
            current_drawdown_pct = current_drawdown * 100
            
            return {
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown_pct,
                'current_drawdown': current_drawdown,
                'current_drawdown_pct': current_drawdown_pct,
                'drawdown_duration': drawdown_duration,
                'drawdown_periods': drawdown_periods,
                'total_periods': total_periods
            }
            
        except Exception as e:
            print(f"Error calculating drawdown for {symbol}: {e}")
            return {}
    
    def calculate_sharpe_ratio(self, symbol: str, period: str = '1y') -> Dict:
        """
        Calculate Sharpe ratio and related risk-adjusted returns
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for data
            
        Returns:
            Dict: Risk-adjusted return metrics
        """
        try:
            data = self.get_stock_data(symbol, period)
            if data.empty:
                return {}
            
            returns = data['Close'].pct_change().dropna()
            
            # Annualized metrics
            annual_return = returns.mean() * 252
            annual_volatility = returns.std() * np.sqrt(252)
            
            # Sharpe ratio
            sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
            
            # Sortino ratio (using downside deviation)
            negative_returns = returns[returns < 0]
            downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
            sortino_ratio = (annual_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            # Calmar ratio (return / max drawdown)
            drawdown_metrics = self.calculate_drawdown(symbol, period)
            max_drawdown_abs = abs(drawdown_metrics.get('max_drawdown', 0))
            calmar_ratio = annual_return / max_drawdown_abs if max_drawdown_abs > 0 else 0
            
            return {
                'annual_return': annual_return,
                'annual_volatility': annual_volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio,
                'risk_free_rate': self.risk_free_rate
            }
            
        except Exception as e:
            print(f"Error calculating Sharpe ratio for {symbol}: {e}")
            return {}
    
    def stress_test(self, symbol: str, scenarios: Optional[Dict] = None) -> Dict:
        """
        Perform stress testing under various scenarios
        
        Args:
            symbol (str): Stock symbol
            scenarios (Dict): Custom stress scenarios
            
        Returns:
            Dict: Stress test results
        """
        try:
            data = self.get_stock_data(symbol, '1y')
            if data.empty:
                return {}
            
            current_price = data['Close'].iloc[-1]
            
            # Default scenarios if none provided
            if scenarios is None:
                scenarios = {
                    'market_crash': -0.20,  # 20% market decline
                    'recession': -0.15,     # 15% decline
                    'volatility_spike': -0.10,  # 10% decline
                    'interest_rate_hike': -0.05,  # 5% decline
                    'bull_market': 0.15,    # 15% increase
                    'strong_growth': 0.25   # 25% increase
                }
            
            # Get beta for market sensitivity
            beta_metrics = self.calculate_beta(symbol)
            beta = beta_metrics.get('beta', 1.0)
            
            results = {}
            for scenario_name, market_change in scenarios.items():
                # Estimate stock price change based on beta
                stock_change = beta * market_change
                new_price = current_price * (1 + stock_change)
                price_change = new_price - current_price
                price_change_pct = (price_change / current_price) * 100
                
                results[scenario_name] = {
                    'market_change': market_change * 100,
                    'estimated_stock_change': stock_change * 100,
                    'current_price': current_price,
                    'estimated_price': new_price,
                    'price_change': price_change,
                    'price_change_pct': price_change_pct
                }
            
            return {
                'scenarios': results,
                'beta': beta,
                'current_price': current_price
            }
            
        except Exception as e:
            print(f"Error in stress testing for {symbol}: {e}")
            return {}
    
    def calculate_correlation_matrix(self, symbols: List[str], period: str = '1y') -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple stocks
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period for data
            
        Returns:
            pd.DataFrame: Correlation matrix
        """
        try:
            returns_data = {}
            
            for symbol in symbols:
                data = self.get_stock_data(symbol, period)
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return pd.DataFrame()
            
            # Create DataFrame and calculate correlation
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix
            
        except Exception as e:
            print(f"Error calculating correlation matrix: {e}")
            return pd.DataFrame()
    
    def calculate_portfolio_risk(self, symbols: List[str], weights: List[float], 
                               period: str = '1y') -> Dict:
        """
        Calculate portfolio-level risk metrics
        
        Args:
            symbols (List[str]): List of stock symbols
            weights (List[float]): Portfolio weights
            period (str): Time period for data
            
        Returns:
            Dict: Portfolio risk metrics
        """
        try:
            if len(symbols) != len(weights):
                return {}
            
            # Get returns for all stocks
            returns_data = {}
            for symbol in symbols:
                data = self.get_stock_data(symbol, period)
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return {}
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            # Calculate portfolio metrics
            weights_array = np.array(weights)
            portfolio_returns = returns_df.dot(weights_array)
            
            # Portfolio volatility
            portfolio_vol = portfolio_returns.std() * np.sqrt(252)
            
            # Portfolio VaR
            portfolio_var = np.percentile(portfolio_returns, 5) * np.sqrt(252)
            
            # Portfolio Sharpe ratio
            portfolio_return = portfolio_returns.mean() * 252
            portfolio_sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
            
            # Diversification ratio
            individual_vols = returns_df.std() * np.sqrt(252)
            weighted_individual_vol = np.sum(weights_array * individual_vols)
            diversification_ratio = weighted_individual_vol / portfolio_vol if portfolio_vol > 0 else 1
            
            return {
                'portfolio_volatility': portfolio_vol,
                'portfolio_return': portfolio_return,
                'portfolio_sharpe': portfolio_sharpe,
                'portfolio_var': portfolio_var,
                'diversification_ratio': diversification_ratio,
                'number_of_stocks': len(symbols)
            }
            
        except Exception as e:
            print(f"Error calculating portfolio risk: {e}")
            return {}
    
    def get_comprehensive_risk_analysis(self, symbol: str, period: str = '1y') -> Dict:
        """
        Get comprehensive risk analysis for a stock
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for data
            
        Returns:
            Dict: Comprehensive risk analysis
        """
        try:
            analysis = {
                'volatility': self.calculate_volatility(symbol, period),
                'var': self.calculate_var(symbol, period=period),
                'beta': self.calculate_beta(symbol, period=period),
                'drawdown': self.calculate_drawdown(symbol, period),
                'risk_adjusted_returns': self.calculate_sharpe_ratio(symbol, period),
                'stress_test': self.stress_test(symbol)
            }
            
            # Calculate overall risk score
            risk_score = self.calculate_risk_score(analysis)
            analysis['risk_score'] = risk_score
            
            return analysis
            
        except Exception as e:
            print(f"Error in comprehensive risk analysis for {symbol}: {e}")
            return {}
    
    def calculate_risk_score(self, analysis: Dict) -> float:
        """
        Calculate overall risk score (0-100, higher = more risky)
        
        Args:
            analysis (Dict): Risk analysis results
            
        Returns:
            float: Risk score
        """
        try:
            score = 0
            max_score = 0
            
            # Volatility (25 points)
            if 'volatility' in analysis:
                vol = analysis['volatility']
                current_vol = vol.get('current_volatility', 0)
                
                if current_vol > 0.4: score += 25
                elif current_vol > 0.3: score += 20
                elif current_vol > 0.2: score += 15
                elif current_vol > 0.15: score += 10
                elif current_vol > 0.1: score += 5
                max_score += 25
            
            # Beta (20 points)
            if 'beta' in analysis:
                beta = analysis['beta']
                beta_val = abs(beta.get('beta', 1))
                
                if beta_val > 1.5: score += 20
                elif beta_val > 1.2: score += 15
                elif beta_val > 0.8: score += 10
                elif beta_val > 0.5: score += 5
                max_score += 20
            
            # VaR (20 points)
            if 'var' in analysis:
                var = analysis['var']
                var_annual = abs(var.get('var_annual', 0))
                
                if var_annual > 0.4: score += 20
                elif var_annual > 0.3: score += 15
                elif var_annual > 0.2: score += 10
                elif var_annual > 0.1: score += 5
                max_score += 20
            
            # Drawdown (20 points)
            if 'drawdown' in analysis:
                drawdown = analysis['drawdown']
                max_dd = abs(drawdown.get('max_drawdown_pct', 0))
                
                if max_dd > 50: score += 20
                elif max_dd > 30: score += 15
                elif max_dd > 20: score += 10
                elif max_dd > 10: score += 5
                max_score += 20
            
            # Sharpe ratio (15 points)
            if 'risk_adjusted_returns' in analysis:
                sharpe = analysis['risk_adjusted_returns']
                sharpe_ratio = sharpe.get('sharpe_ratio', 0)
                
                if sharpe_ratio < 0: score += 15
                elif sharpe_ratio < 0.5: score += 10
                elif sharpe_ratio < 1: score += 5
                max_score += 15
            
            return round((score / max_score) * 100, 1) if max_score > 0 else 0
            
        except Exception as e:
            print(f"Error calculating risk score: {e}")
            return 0
