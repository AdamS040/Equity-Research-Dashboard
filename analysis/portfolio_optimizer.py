"""
Portfolio Optimization Module
Modern Portfolio Theory implementation with advanced optimization techniques
"""
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.optimize import minimize
from typing import Dict, List, Optional, Tuple
import warnings
import logging
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_optimizer_inputs(returns_data: pd.DataFrame) -> Tuple[bool, pd.DataFrame, Dict]:
    """
    Validate returns data for optimizer
    
    Args:
        returns_data (pd.DataFrame): Stock returns data
        
    Returns:
        Tuple[bool, pd.DataFrame, Dict]: (is_valid, cleaned_data, validation_info)
    """
    validation_info = {
        'has_nans': False,
        'nan_handling': None,
        'is_single_asset': False,
        'is_singular_matrix': False,
        'original_shape': None,
        'cleaned_shape': None,
        'warnings': []
    }
    
    # Store original shape
    validation_info['original_shape'] = returns_data.shape
    
    # Check if data is empty
    if returns_data.empty:
        validation_info['warnings'].append("Returns data is empty")
        return False, returns_data, validation_info
    
    # Check for single asset case
    if len(returns_data.columns) == 1:
        validation_info['is_single_asset'] = True
        validation_info['warnings'].append("Single asset portfolio detected")
        return True, returns_data, validation_info
    
    # Check for NaNs
    nan_count = returns_data.isna().sum().sum()
    if nan_count > 0:
        validation_info['has_nans'] = True
        
        # Try forward-fill first
        cleaned_data = returns_data.ffill()
        remaining_nans = cleaned_data.isna().sum().sum()
        
        if remaining_nans > 0:
            # If forward-fill doesn't work, drop rows with NaNs
            cleaned_data = returns_data.dropna()
            validation_info['nan_handling'] = 'dropna'
            validation_info['warnings'].append(f"Dropped {len(returns_data) - len(cleaned_data)} rows with NaNs")
        else:
            validation_info['nan_handling'] = 'forward_fill'
            validation_info['warnings'].append(f"Forward-filled {nan_count} NaN values")
    else:
        cleaned_data = returns_data.copy()
    
    # Check if we have enough data after cleaning
    if len(cleaned_data) < 30:  # Minimum 30 days of data
        validation_info['warnings'].append("Insufficient data after cleaning (less than 30 days)")
        return False, cleaned_data, validation_info
    
    # Check for singular covariance matrix
    try:
        cov_matrix = cleaned_data.cov()
        # Check if matrix is singular by computing determinant
        det = np.linalg.det(cov_matrix.values)
        if abs(det) < 1e-10:  # Very small determinant indicates singularity
            validation_info['is_singular_matrix'] = True
            validation_info['warnings'].append("Covariance matrix is singular")
    except Exception as e:
        validation_info['is_singular_matrix'] = True
        validation_info['warnings'].append(f"Error computing covariance matrix: {e}")
    
    validation_info['cleaned_shape'] = cleaned_data.shape
    
    return True, cleaned_data, validation_info

class PortfolioOptimizer:
    """
    Advanced portfolio optimization using Modern Portfolio Theory
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate (float): Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
    
    def get_stock_data(self, symbols: List[str], period: str = '2y') -> pd.DataFrame:
        """
        Get stock price data for portfolio optimization
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period for historical data
            
        Returns:
            pd.DataFrame: Stock price data
        """
        try:
            # Download data
            data = yf.download(symbols, period=period)['Close']
            
            # Handle single stock case
            if len(symbols) == 1:
                data = data.to_frame()
                data.columns = symbols
            
            # Remove any columns with all NaN values
            data = data.dropna(axis=1, how='all')
            
            return data
        except Exception as e:
            print(f"Error downloading data: {e}")
            return pd.DataFrame()
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily returns from price data
        
        Args:
            prices (pd.DataFrame): Stock prices
            
        Returns:
            pd.DataFrame: Daily returns
        """
        return prices.pct_change().dropna()
    
    def calculate_portfolio_metrics(self, weights: np.array, returns: pd.DataFrame) -> Dict:
        """
        Calculate portfolio performance metrics
        
        Args:
            weights (np.array): Portfolio weights
            returns (pd.DataFrame): Stock returns
            
        Returns:
            Dict: Portfolio metrics
        """
        # Portfolio returns
        portfolio_returns = returns.dot(weights)
        
        # Annual metrics (252 trading days)
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Sharpe ratio
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # VaR (Value at Risk) - 5% VaR
        var_5 = np.percentile(portfolio_returns, 5)
        var_1 = np.percentile(portfolio_returns, 1)
        
        # Sortino ratio (using downside deviation)
        negative_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
        sortino_ratio = (annual_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # Information ratio (assuming benchmark is risk-free rate)
        information_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Calmar ratio (annual return / maximum drawdown)
        max_drawdown_abs = abs(max_drawdown)
        calmar_ratio = annual_return / max_drawdown_abs if max_drawdown_abs > 0 else 0
        
        return {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'var_5_percent': var_5,
            'var_1_percent': var_1,
            'information_ratio': information_ratio,
            'calmar_ratio': calmar_ratio,
            'portfolio_dates': returns.index.tolist(),
            'portfolio_returns': cumulative_returns.tolist()
        }
    
    def optimize_max_sharpe(self, returns: pd.DataFrame, constraints: Optional[Dict] = None) -> np.array:
        """
        Optimize portfolio for maximum Sharpe ratio
        
        Args:
            returns (pd.DataFrame): Stock returns
            constraints (Dict, optional): Weight constraints
            
        Returns:
            np.array: Optimal weights
        """
        # Validate inputs
        is_valid, cleaned_returns, validation_info = validate_optimizer_inputs(returns)
        
        if not is_valid:
            logger.warning(f"Input validation failed: {validation_info['warnings']}")
            # Return equal weights as fallback
            n_assets = len(returns.columns) if not returns.empty else 1
            return np.array([1.0 / n_assets] * n_assets)
        
        # Handle single asset case
        if validation_info['is_single_asset']:
            logger.info("Single asset portfolio - returning weight of 1.0")
            return np.array([1.0])
        
        # Handle singular covariance matrix
        if validation_info['is_singular_matrix']:
            logger.warning("Singular covariance matrix detected - using equal weights fallback")
            n_assets = len(cleaned_returns.columns)
            return np.array([1.0 / n_assets] * n_assets)
        
        # Log any warnings
        if validation_info['warnings']:
            logger.info(f"Validation warnings: {validation_info['warnings']}")
        
        n_assets = len(cleaned_returns.columns)
        
        # Calculate expected returns and covariance matrix
        expected_returns = cleaned_returns.mean() * 252
        cov_matrix = cleaned_returns.cov() * 252
        
        # Objective function (negative Sharpe ratio to minimize)
        def neg_sharpe_ratio(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            if portfolio_volatility == 0:
                return 1e6  # Large penalty for zero volatility
            
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            return -sharpe_ratio  # Negative because we minimize
        
        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1
        
        # Bounds (default: no short selling, max 40% per asset)
        if constraints:
            min_weight = constraints.get('min_weight', 0.0)
            max_weight = constraints.get('max_weight', 0.4)
        else:
            min_weight, max_weight = 0.0, 0.4
            
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Try multiple initial guesses for better optimization
        best_result = None
        best_sharpe = -np.inf
        
        initial_guesses = [
            np.array([1.0 / n_assets] * n_assets),  # Equal weights
            np.random.dirichlet(np.ones(n_assets)),  # Random weights
            np.array([0.5] + [0.5/(n_assets-1)] * (n_assets-1)),  # Concentrated
        ]
        
        for x0 in initial_guesses:
            try:
                result = minimize(neg_sharpe_ratio, x0, method='SLSQP', 
                                bounds=bounds, constraints=constraints_list,
                                options={'maxiter': 1000})
                
                if result.success:
                    # Calculate Sharpe ratio for this result
                    weights = result.x
                    portfolio_return = np.dot(weights, expected_returns)
                    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                    
                    if portfolio_volatility > 0:
                        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                        
                        if sharpe_ratio > best_sharpe:
                            best_sharpe = sharpe_ratio
                            best_result = weights
                            
            except Exception as e:
                print(f"Optimization attempt failed: {e}")
                continue
        
        if best_result is not None:
            # Ensure weights sum to 1.0
            best_result = best_result / np.sum(best_result)
            return best_result
        else:
            # Fallback to equal weights
            logger.warning("Optimization failed - using equal weights fallback")
            return np.array([1.0 / n_assets] * n_assets)
    
    def optimize_min_volatility(self, returns: pd.DataFrame, constraints: Optional[Dict] = None) -> np.array:
        """
        Optimize portfolio for minimum volatility
        
        Args:
            returns (pd.DataFrame): Stock returns
            constraints (Dict, optional): Weight constraints
            
        Returns:
            np.array: Optimal weights
        """
        # Validate inputs
        is_valid, cleaned_returns, validation_info = validate_optimizer_inputs(returns)
        
        if not is_valid:
            logger.warning(f"Input validation failed: {validation_info['warnings']}")
            # Return equal weights as fallback
            n_assets = len(returns.columns) if not returns.empty else 1
            return np.array([1.0 / n_assets] * n_assets)
        
        # Handle single asset case
        if validation_info['is_single_asset']:
            logger.info("Single asset portfolio - returning weight of 1.0")
            return np.array([1.0])
        
        # Handle singular covariance matrix
        if validation_info['is_singular_matrix']:
            logger.warning("Singular covariance matrix detected - using equal weights fallback")
            n_assets = len(cleaned_returns.columns)
            return np.array([1.0 / n_assets] * n_assets)
        
        # Log any warnings
        if validation_info['warnings']:
            logger.info(f"Validation warnings: {validation_info['warnings']}")
        
        n_assets = len(cleaned_returns.columns)
        
        # Objective function (portfolio volatility)
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cleaned_returns.cov() * 252, weights)))
        
        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Bounds
        if constraints:
            min_weight = constraints.get('min_weight', 0.0)
            max_weight = constraints.get('max_weight', 0.4)
        else:
            min_weight, max_weight = 0.0, 0.4
            
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        try:
            result = minimize(portfolio_volatility, x0, method='SLSQP',
                            bounds=bounds, constraints=constraints_list)
            
            if result.success:
                weights = result.x
                # Ensure weights sum to 1.0
                weights = weights / np.sum(weights)
                return weights
            else:
                logger.warning("Min volatility optimization failed - using equal weights fallback")
                return x0
        except Exception as e:
            logger.warning(f"Min volatility optimization error: {e} - using equal weights fallback")
            return x0
    
    def optimize_target_return(self, returns: pd.DataFrame, target_return: float, 
                             constraints: Optional[Dict] = None) -> np.array:
        """
        Optimize portfolio for target return with minimum risk
        
        Args:
            returns (pd.DataFrame): Stock returns
            target_return (float): Target annual return
            constraints (Dict, optional): Weight constraints
            
        Returns:
            np.array: Optimal weights
        """
        # Validate inputs
        is_valid, cleaned_returns, validation_info = validate_optimizer_inputs(returns)
        
        if not is_valid:
            logger.warning(f"Input validation failed: {validation_info['warnings']}")
            # Return equal weights as fallback
            n_assets = len(returns.columns) if not returns.empty else 1
            return np.array([1.0 / n_assets] * n_assets)
        
        # Handle single asset case
        if validation_info['is_single_asset']:
            logger.info("Single asset portfolio - returning weight of 1.0")
            return np.array([1.0])
        
        # Handle singular covariance matrix
        if validation_info['is_singular_matrix']:
            logger.warning("Singular covariance matrix detected - using equal weights fallback")
            n_assets = len(cleaned_returns.columns)
            return np.array([1.0 / n_assets] * n_assets)
        
        # Log any warnings
        if validation_info['warnings']:
            logger.info(f"Validation warnings: {validation_info['warnings']}")
        
        n_assets = len(cleaned_returns.columns)
        expected_returns = cleaned_returns.mean() * 252
        cov_matrix = cleaned_returns.cov() * 252
        
        # Objective function (portfolio volatility)
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Constraints
        constraints_list = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
            {'type': 'eq', 'fun': lambda x: np.dot(x, expected_returns) - target_return}  # Target return
        ]
        
        # Bounds
        if constraints:
            min_weight = constraints.get('min_weight', 0.0)
            max_weight = constraints.get('max_weight', 0.4)
        else:
            min_weight, max_weight = 0.0, 0.4
            
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        try:
            result = minimize(portfolio_volatility, x0, method='SLSQP',
                            bounds=bounds, constraints=constraints_list,
                            options={'maxiter': 1000})
            
            if result.success:
                weights = result.x
                # Ensure weights sum to 1.0
                weights = weights / np.sum(weights)
                return weights
            else:
                logger.warning("Target return optimization failed - using equal weights fallback")
                return x0
        except Exception as e:
            logger.warning(f"Target return optimization error: {e} - using equal weights fallback")
            return x0
    
    def generate_efficient_frontier(self, returns: pd.DataFrame, n_portfolios: int = 100,
                                  constraints: Optional[Dict] = None) -> pd.DataFrame:
        """
        Generate efficient frontier
        
        Args:
            returns (pd.DataFrame): Stock returns
            n_portfolios (int): Number of portfolios on frontier
            constraints (Dict, optional): Weight constraints
            
        Returns:
            pd.DataFrame: Efficient frontier data
        """
        # Validate inputs
        is_valid, cleaned_returns, validation_info = validate_optimizer_inputs(returns)
        
        if not is_valid:
            logger.warning(f"Input validation failed for efficient frontier: {validation_info['warnings']}")
            return pd.DataFrame()
        
        # Handle single asset case
        if validation_info['is_single_asset']:
            logger.info("Single asset portfolio - cannot generate efficient frontier")
            return pd.DataFrame()
        
        # Handle singular covariance matrix
        if validation_info['is_singular_matrix']:
            logger.warning("Singular covariance matrix - cannot generate efficient frontier")
            return pd.DataFrame()
        
        # Calculate return range
        min_vol_weights = self.optimize_min_volatility(cleaned_returns, constraints)
        min_vol_return = np.sum(cleaned_returns.mean() * min_vol_weights) * 252
        
        max_return = cleaned_returns.mean().max() * 252 * 0.9  # 90% of max individual return
        
        # Generate target returns
        target_returns = np.linspace(min_vol_return, max_return, n_portfolios)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            try:
                weights = self.optimize_target_return(cleaned_returns, target_return, constraints)
                metrics = self.calculate_portfolio_metrics(weights, cleaned_returns)
                
                portfolio = {
                    'target_return': target_return,
                    'return': metrics['annual_return'],
                    'volatility': metrics['annual_volatility'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'weights': weights
                }
                
                efficient_portfolios.append(portfolio)
            except Exception as e:
                logger.warning(f"Error generating portfolio for target return {target_return}: {e}")
                continue
        
        return pd.DataFrame(efficient_portfolios)
    
    def risk_parity_optimization(self, returns: pd.DataFrame) -> np.array:
        """
        Risk parity portfolio optimization
        
        Args:
            returns (pd.DataFrame): Stock returns
            
        Returns:
            np.array: Risk parity weights
        """
        # Validate inputs
        is_valid, cleaned_returns, validation_info = validate_optimizer_inputs(returns)
        
        if not is_valid:
            logger.warning(f"Input validation failed: {validation_info['warnings']}")
            # Return equal weights as fallback
            n_assets = len(returns.columns) if not returns.empty else 1
            return np.array([1.0 / n_assets] * n_assets)
        
        # Handle single asset case
        if validation_info['is_single_asset']:
            logger.info("Single asset portfolio - returning weight of 1.0")
            return np.array([1.0])
        
        # Handle singular covariance matrix
        if validation_info['is_singular_matrix']:
            logger.warning("Singular covariance matrix detected - using equal weights fallback")
            n_assets = len(cleaned_returns.columns)
            return np.array([1.0 / n_assets] * n_assets)
        
        # Log any warnings
        if validation_info['warnings']:
            logger.info(f"Validation warnings: {validation_info['warnings']}")
        
        n_assets = len(cleaned_returns.columns)
        cov_matrix = cleaned_returns.cov() * 252
        
        # Objective function for risk parity
        def risk_budget_objective(weights):
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_volatility
            contrib = weights * marginal_contrib
            
            # Risk parity: all assets contribute equally to risk
            target_contrib = portfolio_volatility / n_assets
            return np.sum((contrib - target_contrib) ** 2)
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0.01, 0.4) for _ in range(n_assets))  # Min 1%, max 40%
        
        # Initial guess
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        try:
            result = minimize(risk_budget_objective, x0, method='SLSQP',
                            bounds=bounds, constraints=constraints)
            
            if result.success:
                weights = result.x
                # Ensure weights sum to 1.0
                weights = weights / np.sum(weights)
                return weights
            else:
                logger.warning("Risk parity optimization failed - using equal weights fallback")
                return x0
        except Exception as e:
            logger.warning(f"Risk parity optimization error: {e} - using equal weights fallback")
            return x0
    
    def black_litterman_optimization(self, returns: pd.DataFrame, market_caps: Dict,
                                   views: Optional[Dict] = None) -> np.array:
        """
        Black-Litterman portfolio optimization (simplified implementation)
        
        Args:
            returns (pd.DataFrame): Stock returns
            market_caps (Dict): Market capitalizations for each stock
            views (Dict, optional): Investor views on expected returns
            
        Returns:
            np.array: Black-Litterman optimal weights
        """
        # Market capitalization weights as prior
        symbols = returns.columns.tolist()
        total_market_cap = sum(market_caps.get(symbol, 1e9) for symbol in symbols)
        market_weights = np.array([market_caps.get(symbol, 1e9) / total_market_cap for symbol in symbols])
        
        # If no views provided, return market cap weighted portfolio
        if not views:
            return market_weights
        
        # Simplified Black-Litterman (without full implementation)
        # In practice, this would involve more complex matrix operations
        cov_matrix = returns.cov() * 252
        
        # Risk aversion parameter (simplified)
        risk_aversion = 3.0
        
        # Implied equilibrium returns
        implied_returns = risk_aversion * np.dot(cov_matrix, market_weights)
        
        # Combine with views (simplified approach)
        adjusted_returns = implied_returns.copy()
        for symbol, expected_return in views.items():
            if symbol in symbols:
                idx = symbols.index(symbol)
                # Simple view incorporation (weight by confidence)
                confidence = 0.5  # 50% confidence in view
                adjusted_returns[idx] = (1 - confidence) * implied_returns[idx] + confidence * expected_return
        
        # Optimize with adjusted returns
        def neg_utility(weights):
            port_return = np.dot(adjusted_returns, weights)
            port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            return -(port_return - 0.5 * risk_aversion * port_variance)
        
        # Constraints and bounds
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0.0, 0.4) for _ in range(len(symbols)))
        
        try:
            result = minimize(neg_utility, market_weights, method='SLSQP',
                            bounds=bounds, constraints=constraints)
            
            if result.success:
                return result.x
            else:
                return market_weights
        except:
            return market_weights
    
    def optimize_portfolio(self, symbols: List[str], method: str = 'max_sharpe',
                         period: str = '2y', constraints: Optional[Dict] = None,
                         target_return: Optional[float] = None,
                         **kwargs) -> Dict:
        """
        Main portfolio optimization function
        
        Args:
            symbols (List[str]): List of stock symbols
            method (str): Optimization method ('max_sharpe', 'min_volatility', 'target_return', 'equal_weight', 'risk_parity')
            period (str): Historical data period
            constraints (Dict, optional): Portfolio constraints
            target_return (float, optional): Target return for target_return method
            **kwargs: Additional parameters
            
        Returns:
            Dict: Optimization results
        """
        # Get data
        prices = self.get_stock_data(symbols, period)
        
        if prices.empty:
            return {'error': 'Unable to fetch price data'}
        
        returns = self.calculate_returns(prices)
        
        if returns.empty:
            return {'error': 'Unable to calculate returns'}
        
        # Validate returns data
        is_valid, cleaned_returns, validation_info = validate_optimizer_inputs(returns)
        
        if not is_valid:
            logger.warning(f"Returns data validation failed: {validation_info['warnings']}")
            return {'error': f'Invalid returns data: {validation_info["warnings"]}'}
        
        # Optimize based on method
        if method == 'max_sharpe':
            optimal_weights = self.optimize_max_sharpe(cleaned_returns, constraints)
        elif method == 'min_volatility':
            optimal_weights = self.optimize_min_volatility(cleaned_returns, constraints)
        elif method == 'target_return':
            if target_return is None:
                target_return = cleaned_returns.mean().mean() * 252 * 1.1  # 10% above average
            optimal_weights = self.optimize_target_return(cleaned_returns, target_return, constraints)
        elif method == 'risk_parity':
            optimal_weights = self.risk_parity_optimization(cleaned_returns)
        elif method == 'equal_weight':
            optimal_weights = np.array([1.0 / len(symbols)] * len(symbols))
        else:
            optimal_weights = np.array([1.0 / len(symbols)] * len(symbols))
        
        # Ensure weights sum to 1.0
        optimal_weights = optimal_weights / np.sum(optimal_weights)
        
        # Calculate portfolio metrics
        portfolio_metrics = self.calculate_portfolio_metrics(optimal_weights, cleaned_returns)
        
        # Current prices and market data
        current_prices = prices.iloc[-1].to_dict()
        
        # Calculate individual stock metrics
        stock_metrics = {}
        for symbol in symbols:
            if symbol in cleaned_returns.columns:
                try:
                    stock_returns = cleaned_returns[symbol]
                    annual_return = stock_returns.mean() * 252
                    annual_volatility = stock_returns.std() * np.sqrt(252)
                    sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
                    
                    # Calculate cumulative returns for performance chart
                    cumulative_returns = (1 + stock_returns).cumprod()
                    
                    # Get the weight for this symbol
                    symbol_index = list(cleaned_returns.columns).index(symbol)
                    weight = optimal_weights[symbol_index] if symbol_index < len(optimal_weights) else 0
                    
                    stock_metrics[symbol] = {
                        'expected_return': annual_return,
                        'volatility': annual_volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'current_price': current_prices.get(symbol, 0),
                        'weight': weight,
                        'dates': cleaned_returns.index.tolist(),
                        'cumulative_returns': cumulative_returns.tolist()
                    }
                except Exception as e:
                    logger.error(f"Error calculating metrics for {symbol}: {e}")
                    # Add fallback data
                    stock_metrics[symbol] = {
                        'expected_return': 0.0,
                        'volatility': 0.0,
                        'sharpe_ratio': 0.0,
                        'current_price': current_prices.get(symbol, 0),
                        'weight': 0.0,
                        'dates': cleaned_returns.index.tolist(),
                        'cumulative_returns': [1.0] * len(cleaned_returns.index)
                    }
        
        # Calculate efficient frontier for comparison
        efficient_frontier_df = self.generate_efficient_frontier(cleaned_returns, n_portfolios=50, constraints=constraints)
        efficient_frontier = efficient_frontier_df.to_dict('records') if not efficient_frontier_df.empty else []
        
        return {
            'symbols': symbols,
            'optimal_weights': dict(zip(cleaned_returns.columns, optimal_weights)),
            'portfolio_metrics': portfolio_metrics,
            'stock_metrics': stock_metrics,
            'optimization_method': method,
            'period': period,
            'price_data': prices.to_dict('records'),
            'returns_data': cleaned_returns.to_dict('records'),
            'efficient_frontier': efficient_frontier,
            'target_return': target_return if method == 'target_return' else None,
            'validation_info': validation_info
        }