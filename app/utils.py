"""
Utility Functions for Equity Research Dashboard
Common helper functions, data validation, formatting, and caching utilities
"""

import os
import re
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from functools import wraps, lru_cache
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('equity_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def is_valid_stock_symbol(symbol: str) -> bool:
        """Validate stock symbol format"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Basic stock symbol validation (1-5 characters, alphanumeric)
        pattern = r'^[A-Z]{1,5}$'
        return bool(re.match(pattern, symbol.upper()))
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """Validate date string format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_period(period: str) -> bool:
        """Validate time period string"""
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        return period in valid_periods
    
    @staticmethod
    def is_valid_interval(interval: str) -> bool:
        """Validate time interval string"""
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        return interval in valid_intervals
    
    @staticmethod
    def validate_portfolio_data(portfolio_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate portfolio data structure"""
        required_fields = ['stocks', 'weights', 'total_value']
        
        for field in required_fields:
            if field not in portfolio_data:
                return False, f"Missing required field: {field}"
        
        if not isinstance(portfolio_data['stocks'], list):
            return False, "Stocks must be a list"
        
        if not isinstance(portfolio_data['weights'], list):
            return False, "Weights must be a list"
        
        if len(portfolio_data['stocks']) != len(portfolio_data['weights']):
            return False, "Number of stocks must match number of weights"
        
        # Validate weights sum to 1
        weights_sum = sum(portfolio_data['weights'])
        if abs(weights_sum - 1.0) > 0.01:
            return False, f"Weights must sum to 1.0, got {weights_sum}"
        
        return True, "Valid portfolio data"


class DataFormatter:
    """Data formatting utilities"""
    
    @staticmethod
    def format_currency(value: Union[float, int, str], currency: str = 'USD') -> str:
        """Format number as currency"""
        if value is None or pd.isna(value):
            return f"{currency} 0.00"
        
        try:
            value = float(value)
            if currency == 'USD':
                return f"${value:,.2f}"
            else:
                return f"{currency} {value:,.2f}"
        except (ValueError, TypeError):
            return f"{currency} 0.00"
    
    @staticmethod
    def format_percentage(value: Union[float, int, str], decimals: int = 2) -> str:
        """Format number as percentage"""
        if value is None or pd.isna(value):
            return "0.00%"
        
        try:
            value = float(value) * 100
            return f"{value:.{decimals}f}%"
        except (ValueError, TypeError):
            return "0.00%"
    
    @staticmethod
    def format_large_number(value: Union[float, int, str]) -> str:
        """Format large numbers with K, M, B suffixes"""
        if value is None or pd.isna(value):
            return "0"
        
        try:
            value = float(value)
            if abs(value) >= 1e12:
                return f"{value/1e12:.2f}T"
            elif abs(value) >= 1e9:
                return f"{value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"{value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"{value/1e3:.2f}K"
            else:
                return f"{value:.2f}"
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def format_ratio(value: Union[float, int, str], decimals: int = 2) -> str:
        """Format ratio values"""
        if value is None or pd.isna(value):
            return "0.00"
        
        try:
            value = float(value)
            return f"{value:.{decimals}f}"
        except (ValueError, TypeError):
            return "0.00"
    
    @staticmethod
    def format_date(date: Union[str, datetime], format_str: str = '%Y-%m-%d') -> str:
        """Format date consistently"""
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return date
        
        if isinstance(date, datetime):
            return date.strftime(format_str)
        
        return str(date)
    
    @staticmethod
    def format_timestamp(timestamp: Union[str, datetime]) -> str:
        """Format timestamp for display"""
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                return timestamp
        
        if isinstance(timestamp, datetime):
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        return str(timestamp)


class CacheManager:
    """Simple cache management utility"""
    
    def __init__(self, cache_dir: str = 'cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache file path"""
        return os.path.join(self.cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.json")
    
    def get(self, key: str, max_age_minutes: int = 60) -> Optional[Any]:
        """Get cached data"""
        cache_file = self._get_cache_key(key)
        
        if not os.path.exists(cache_file):
            return None
        
        # Check if cache is expired
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_age > timedelta(minutes=max_age_minutes):
            os.remove(cache_file)
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def set(self, key: str, data: Any) -> bool:
        """Set cached data"""
        cache_file = self._get_cache_key(key)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, default=str)
            return True
        except (TypeError, IOError):
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached data"""
        cache_file = self._get_cache_key(key)
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                return True
            except OSError:
                return False
        return False
    
    def clear(self) -> bool:
        """Clear all cached data"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            return True
        except OSError:
            return False


class FinancialCalculator:
    """Financial calculation utilities"""
    
    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """Calculate percentage returns"""
        return prices.pct_change().dropna()
    
    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """Calculate log returns"""
        return np.log(prices / prices.shift(1)).dropna()
    
    @staticmethod
    def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
        """Calculate volatility"""
        if annualize:
            return returns.std() * np.sqrt(252)
        return returns.std()
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    @staticmethod
    def calculate_max_drawdown(prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, confidence_level * 100)
    
    @staticmethod
    def calculate_beta(returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate beta relative to market"""
        covariance = returns.cov(market_returns)
        market_variance = market_returns.var()
        
        if market_variance == 0:
            return 0
        
        return covariance / market_variance
    
    @staticmethod
    def calculate_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix"""
        return returns_df.corr()
    
    @staticmethod
    def calculate_portfolio_metrics(weights: np.array, returns: pd.DataFrame, 
                                  risk_free_rate: float = 0.02) -> Dict[str, float]:
        """Calculate portfolio metrics"""
        portfolio_returns = (returns * weights).sum(axis=1)
        
        metrics = {
            'return': portfolio_returns.mean() * 252,
            'volatility': portfolio_returns.std() * np.sqrt(252),
            'sharpe_ratio': FinancialCalculator.calculate_sharpe_ratio(portfolio_returns, risk_free_rate),
            'max_drawdown': FinancialCalculator.calculate_max_drawdown((1 + portfolio_returns).cumprod()),
            'var_5': FinancialCalculator.calculate_var(portfolio_returns, 0.05)
        }
        
        return metrics


class ErrorHandler:
    """Error handling utilities"""
    
    @staticmethod
    def handle_api_error(error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle API errors gracefully"""
        error_msg = str(error)
        logger.error(f"API Error in {context}: {error_msg}")
        
        if "rate limit" in error_msg.lower():
            return {
                'success': False,
                'error': 'API rate limit exceeded. Please try again later.',
                'retry_after': 60
            }
        elif "not found" in error_msg.lower():
            return {
                'success': False,
                'error': 'Data not found. Please check the symbol or parameters.',
                'retry_after': 0
            }
        elif "timeout" in error_msg.lower():
            return {
                'success': False,
                'error': 'Request timeout. Please try again.',
                'retry_after': 30
            }
        else:
            return {
                'success': False,
                'error': 'An error occurred while fetching data.',
                'retry_after': 0
            }
    
    @staticmethod
    def handle_data_error(error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle data processing errors"""
        error_msg = str(error)
        logger.error(f"Data Error in {context}: {error_msg}")
        
        return {
            'success': False,
            'error': 'Error processing data. Please check your input.',
            'details': error_msg
        }


class ConfigManager:
    """Configuration management utilities"""
    
    @staticmethod
    def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_file: str = 'config.json') -> bool:
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError:
            return False
    
    @staticmethod
    def get_api_keys() -> Dict[str, str]:
        """Get API keys from environment variables"""
        return {
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
            'fmp': os.getenv('FMP_API_KEY', ''),
            'news': os.getenv('NEWS_API_KEY', ''),
            'quandl': os.getenv('QUANDL_API_KEY', '')
        }


# Decorators
def cache_result(cache_manager: CacheManager, key_prefix: str = "", ttl_minutes: int = 60):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(key, ttl_minutes)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(key, result)
            return result
        return wrapper
    return decorator


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on error"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            raise last_exception
        return wrapper
    return decorator


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        
        return result
    return wrapper


# Global instances
validator = DataValidator()
formatter = DataFormatter()
cache_manager = CacheManager()
calculator = FinancialCalculator()
error_handler = ErrorHandler()
config_manager = ConfigManager()


def configure_yfinance_session():
    """
    Configure yfinance with proper headers and retry logic to avoid blocking
    
    Returns:
        requests.Session: Configured session for yfinance
    """
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
    
    return session


def get_yfinance_ticker(symbol: str, session=None):
    """
    Get yfinance ticker with proper session configuration
    
    Args:
        symbol (str): Stock symbol
        session (requests.Session, optional): Pre-configured session
        
    Returns:
        yfinance.Ticker: Configured ticker object
    """
    import yfinance as yf
    
    if session is None:
        session = configure_yfinance_session()
    
    ticker = yf.Ticker(symbol)
    ticker._session = session
    return ticker


def fetch_stock_data_robust(symbol: str, period: str = '1y', interval: str = '1d', session=None):
    """
    Fetch stock data with robust error handling
    
    Args:
        symbol (str): Stock symbol
        period (str): Time period
        interval (str): Data interval
        session (requests.Session, optional): Pre-configured session
        
    Returns:
        pd.DataFrame: Stock data or empty DataFrame if error
    """
    import yfinance as yf
    import pandas as pd
    
    try:
        ticker = get_yfinance_ticker(symbol, session)
        data = ticker.history(period=period, interval=interval, progress=False)
        
        if not data.empty:
            logger.info(f"Successfully fetched data for {symbol}")
            return data
        else:
            logger.warning(f"No data found for {symbol}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()


def fetch_market_data_with_fallbacks(symbols: list, period: str = '2d', interval: str = '1d'):
    """
    Fetch market data with multiple fallback strategies
    
    Args:
        symbols (list): List of symbols to fetch
        period (str): Time period
        interval (str): Data interval
        
    Returns:
        dict: Dictionary with symbol as key and data as value
    """
    import yfinance as yf
    import pandas as pd
    import time
    
    results = {}
    session = configure_yfinance_session()
    
    # Alternative symbols for common indices
    symbol_alternatives = {
        '^GSPC': ['SPY', 'SPX'],
        '^IXIC': ['QQQ', 'NDX'],
        '^VIX': ['VXX', 'VIXY'],
        '^TNX': ['^TYX', 'TNX'],
        '^DJI': ['DIA', 'DJI']
    }
    
    for symbol in symbols:
        try:
            # Try primary symbol first
            ticker = get_yfinance_ticker(symbol, session)
            data = ticker.history(period=period, interval=interval, progress=False)
            
            # If primary fails, try alternatives
            if data.empty and symbol in symbol_alternatives:
                for alt_symbol in symbol_alternatives[symbol]:
                    try:
                        logger.info(f"Trying alternative symbol {alt_symbol} for {symbol}")
                        ticker = get_yfinance_ticker(alt_symbol, session)
                        data = ticker.history(period=period, interval=interval, progress=False)
                        if not data.empty:
                            logger.info(f"Successfully fetched data using alternative {alt_symbol}")
                            break
                    except Exception as e:
                        logger.warning(f"Alternative symbol {alt_symbol} also failed: {e}")
                        continue
            
            if not data.empty:
                results[symbol] = data
                logger.info(f"Successfully fetched data for {symbol}")
            else:
                logger.warning(f"No data available for {symbol}")
                results[symbol] = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            results[symbol] = pd.DataFrame()
        
        # Add delay between requests
        time.sleep(0.5)
    
    return results


def get_market_overview_robust():
    """
    Get market overview with robust error handling and fallbacks
    
    Returns:
        dict: Market overview data
    """
    import yfinance as yf
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Define market symbols with alternatives
    market_symbols = [
        ('^GSPC', 'S&P 500', 'currency'),
        ('^IXIC', 'NASDAQ', 'currency'),
        ('^VIX', 'VIX', 'decimal'),
        ('^TNX', '10Y Treasury', 'percentage')
    ]
    
    session = configure_yfinance_session()
    market_data = {}
    
    for symbol, name, format_type in market_symbols:
        try:
            # Try primary symbol
            ticker = get_yfinance_ticker(symbol, session)
            hist = ticker.history(period='2d', interval='1d', progress=False)
            
            # If primary fails, try alternatives
            if hist.empty:
                alternatives = {
                    '^GSPC': 'SPY',
                    '^IXIC': 'QQQ',
                    '^VIX': 'VXX',
                    '^TNX': '^TYX'
                }
                
                if symbol in alternatives:
                    alt_symbol = alternatives[symbol]
                    logger.info(f"Trying alternative {alt_symbol} for {symbol}")
                    ticker = get_yfinance_ticker(alt_symbol, session)
                    hist = ticker.history(period='2d', interval='1d', progress=False)
            
            if not hist.empty and len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change = current - previous
                change_pct = (change / previous) * 100
                
                # Format based on type
                if format_type == 'currency':
                    price_str = f"${current:.2f}"
                elif format_type == 'percentage':
                    price_str = f"{current:.2f}%"
                else:
                    price_str = f"{current:.2f}"
                
                change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                
                market_data[name] = {
                    'price': price_str,
                    'change': change_str,
                    'current_value': current,
                    'change_value': change,
                    'change_pct': change_pct
                }
                
                logger.info(f"Successfully fetched {name}: {price_str}")
            else:
                logger.warning(f"No data available for {name}")
                market_data[name] = {
                    'price': 'N/A',
                    'change': 'N/A',
                    'current_value': 0,
                    'change_value': 0,
                    'change_pct': 0
                }
                
        except Exception as e:
            logger.error(f"Error fetching {name}: {e}")
            market_data[name] = {
                'price': 'N/A',
                'change': 'N/A',
                'current_value': 0,
                'change_value': 0,
                'change_pct': 0
            }
    
    return market_data
