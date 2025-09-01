"""
Data Fetcher Module
Comprehensive data retrieval from multiple sources with enhanced caching and retry logic
"""
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional, Tuple, Callable, Any
import time
import logging
import random
from functools import lru_cache, wraps
from datetime import datetime, timedelta
import requests_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure requests-cache for enhanced caching
requests_cache.install_cache(
    'yfinance_cache',
    expire_after=1800,  # 30 minutes cache duration
    allowable_methods=('GET', 'POST'),
    include_get_headers=True
)

def retry_on_failure(max_retries: int = 3, backoff_factor: float = 1.0, 
                    exceptions: tuple = (Exception,)):
    """
    Decorator for retrying yfinance calls with exponential backoff
    
    Args:
        max_retries (int): Maximum number of retry attempts
        backoff_factor (float): Backoff multiplier for delays
        exceptions (tuple): Exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Add random jitter to prevent thundering herd
                    if attempt > 0:
                        jitter = random.uniform(0, 0.1 * backoff_factor)
                        delay = (backoff_factor ** attempt) + jitter
                        logger.info(f"Retry attempt {attempt} for {func.__name__}, waiting {delay:.2f}s")
                        time.sleep(delay)
                    
                    result = func(*args, **kwargs)
                    
                    # Log successful retry if it wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"Successfully completed {func.__name__} on attempt {attempt + 1}")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")
                        break
                    
                    # Check if it's a rate limit error (429)
                    if hasattr(e, 'response') and e.response and e.response.status_code == 429:
                        logger.warning("Rate limit detected, using longer delay")
                        time.sleep(backoff_factor ** (attempt + 2))  # Longer delay for rate limits
            
            # If we get here, all retries failed
            logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts")
            raise last_exception
            
        return wrapper
    return decorator

class DataFetcher:
    """
    Comprehensive data fetcher for financial data with enhanced caching and retry logic
    """
    
    def __init__(self, api_keys: Optional[Dict] = None):
        """
        Initialize data fetcher
        
        Args:
            api_keys (Dict): Dictionary of API keys
        """
        self.api_keys = api_keys or {}
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 1800  # 30 minutes default (increased from 5 minutes)
        
        # Configure session with enhanced retry strategy
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with enhanced retry strategy and caching
        
        Returns:
            requests.Session: Configured session
        """
        session = requests.Session()
        
        # Enhanced retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=2.0,  # Increased backoff factor
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            respect_retry_after_header=True
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Enhanced headers to mimic a real browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        return session
    
    @retry_on_failure(max_retries=3, backoff_factor=2.0)
    def _fetch_with_yfinance(self, symbol: str, period: str = '1y', 
                            interval: str = '1d') -> pd.DataFrame:
        """
        Internal method to fetch data from yfinance with retry logic
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period
            interval (str): Data interval
            
        Returns:
            pd.DataFrame: Stock data
        """
        # Create ticker with custom session
        ticker = yf.Ticker(symbol)
        ticker._session = self.session
        
        # Add rate limiting delay
        time.sleep(random.uniform(0.1, 0.5))  # Random delay between 100-500ms
        
        # Fetch data
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            raise ValueError(f"No data returned for symbol {symbol}")
        
        return data
    
    @lru_cache(maxsize=128)
    def _get_cached_ticker_info(self, symbol: str) -> Dict:
        """
        Get cached ticker info using LRU cache
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Ticker info
        """
        ticker = yf.Ticker(symbol)
        ticker._session = self.session
        return ticker.info
    
    def get_stock_data(self, symbol: str, period: str = '1y', 
                      interval: str = '1d') -> pd.DataFrame:
        """
        Get stock price data with robust error handling and enhanced caching
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period
            interval (str): Data interval
            
        Returns:
            pd.DataFrame: Stock data
        """
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for {symbol} ({period}, {interval})")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for {symbol} ({period}, {interval}), fetching from API")
            
            # Fetch data with retry logic
            data = self._fetch_with_yfinance(symbol, period, interval)
            
            if not data.empty:
                # Cache the data
                self.cache[cache_key] = data
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached data for {symbol}")
                return data
            else:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_financial_statements(self, symbol: str) -> Dict:
        """
        Get financial statements with retry logic
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Financial statements
        """
        try:
            cache_key = f"financial_{symbol}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for financial statements of {symbol}")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for financial statements of {symbol}, fetching from API")
            
            ticker = yf.Ticker(symbol)
            ticker._session = self.session
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.2, 0.8))
            
            statements = {
                'income_statement': ticker.income_stmt,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
                'info': ticker.info
            }
            
            # Cache the data
            self.cache[cache_key] = statements
            self.cache_timestamps[cache_key] = time.time()
            
            logger.info(f"Successfully fetched and cached financial statements for {symbol}")
            return statements
            
        except Exception as e:
            logger.error(f"Error fetching financial statements for {symbol}: {str(e)}")
            return {}
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_market_data(self, symbols: List[str], period: str = '1d') -> pd.DataFrame:
        """
        Get market data for multiple symbols with retry logic
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period
            
        Returns:
            pd.DataFrame: Market data
        """
        try:
            cache_key = f"market_{'_'.join(symbols)}_{period}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for market data of {len(symbols)} symbols")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for market data of {len(symbols)} symbols, fetching from API")
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.3, 1.0))
            
            # Use yf.download without custom session to avoid compatibility issues
            data = yf.download(symbols, period=period)
            
            if not data.empty:
                # Cache the data
                self.cache[cache_key] = data
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Fetched and cached market data for {len(symbols)} symbols")
                return data
            else:
                logger.warning(f"No market data found for symbols: {symbols}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_earnings_calendar(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get earnings calendar for symbols with retry logic
        
        Args:
            symbols (List[str]): List of stock symbols
            
        Returns:
            pd.DataFrame: Earnings calendar
        """
        try:
            cache_key = f"earnings_{'_'.join(symbols)}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for earnings calendar of {len(symbols)} symbols")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for earnings calendar of {len(symbols)} symbols, fetching from API")
            
            earnings_data = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    ticker._session = self.session
                    
                    # Add rate limiting delay between symbols
                    time.sleep(random.uniform(0.2, 0.6))
                    
                    calendar = ticker.calendar
                    
                    if calendar is not None and not calendar.empty:
                        for _, row in calendar.iterrows():
                            earnings_data.append({
                                'Symbol': symbol,
                                'Earnings Date': row.get('Earnings Date', 'N/A'),
                                'Earnings Average': row.get('Earnings Average', 'N/A'),
                                'Earnings Low': row.get('Earnings Low', 'N/A'),
                                'Earnings High': row.get('Earnings High', 'N/A'),
                                'Revenue Average': row.get('Revenue Average', 'N/A'),
                                'Revenue Low': row.get('Revenue Low', 'N/A'),
                                'Revenue High': row.get('Revenue High', 'N/A')
                            })
                except Exception as e:
                    logger.warning(f"Error fetching earnings data for {symbol}: {str(e)}")
                    continue
            
            if earnings_data:
                result = pd.DataFrame(earnings_data)
                # Cache the data
                self.cache[cache_key] = result
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached earnings calendar for {len(symbols)} symbols")
                return result
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {str(e)}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_news_data(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news data for a symbol with retry logic
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of news articles to fetch
            
        Returns:
            List[Dict]: News data
        """
        try:
            cache_key = f"news_{symbol}_{limit}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for news data of {symbol}")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for news data of {symbol}, fetching from API")
            
            ticker = yf.Ticker(symbol)
            ticker._session = self.session
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.2, 0.6))
            
            news = ticker.news
            
            if news:
                # Format news data
                formatted_news = []
                for article in news[:limit]:
                    formatted_news.append({
                        'title': article.get('title', ''),
                        'publisher': article.get('publisher', ''),
                        'link': article.get('link', ''),
                        'published': article.get('providerPublishTime', ''),
                        'summary': article.get('summary', '')
                    })
                
                # Cache the data
                self.cache[cache_key] = formatted_news
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached news data for {symbol}")
                return formatted_news
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_analyst_recommendations(self, symbol: str) -> pd.DataFrame:
        """
        Get analyst recommendations with retry logic
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Analyst recommendations
        """
        try:
            cache_key = f"recommendations_{symbol}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for analyst recommendations of {symbol}")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for analyst recommendations of {symbol}, fetching from API")
            
            ticker = yf.Ticker(symbol)
            ticker._session = self.session
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.2, 0.6))
            
            recommendations = ticker.recommendations
            
            if recommendations is not None and not recommendations.empty:
                # Cache the data
                self.cache[cache_key] = recommendations
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached analyst recommendations for {symbol}")
                return recommendations
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching analyst recommendations for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_major_holders(self, symbol: str) -> pd.DataFrame:
        """
        Get major holders data with retry logic
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Major holders data
        """
        try:
            cache_key = f"major_holders_{symbol}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for major holders of {symbol}")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for major holders of {symbol}, fetching from API")
            
            ticker = yf.Ticker(symbol)
            ticker._session = self.session
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.2, 0.6))
            
            major_holders = ticker.major_holders
            
            if major_holders is not None and not major_holders.empty:
                # Cache the data
                self.cache[cache_key] = major_holders
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached major holders for {symbol}")
                return major_holders
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching major holders for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_institutional_holders(self, symbol: str) -> pd.DataFrame:
        """
        Get institutional holders data with retry logic
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Institutional holders data
        """
        try:
            cache_key = f"institutional_holders_{symbol}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for institutional holders of {symbol}")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for institutional holders of {symbol}, fetching from API")
            
            ticker = yf.Ticker(symbol)
            ticker._session = self.session
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.2, 0.6))
            
            institutional_holders = ticker.institutional_holders
            
            if institutional_holders is not None and not institutional_holders.empty:
                # Cache the data
                self.cache[cache_key] = institutional_holders
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached institutional holders for {symbol}")
                return institutional_holders
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching institutional holders for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2, backoff_factor=1.5)
    def get_options_data(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """
        Get options data with retry logic
        
        Args:
            symbol (str): Stock symbol
            expiration_date (str): Option expiration date
            
        Returns:
            Dict: Options data
        """
        try:
            cache_key = f"options_{symbol}_{expiration_date or 'next'}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for options data of {symbol}")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for options data of {symbol}, fetching from API")
            
            ticker = yf.Ticker(symbol)
            ticker._session = self.session
            
            # Add rate limiting delay
            time.sleep(random.uniform(0.3, 0.8))
            
            if expiration_date:
                options = ticker.option_chain(expiration_date)
            else:
                # Get next expiration
                expirations = ticker.options
                if expirations:
                    options = ticker.option_chain(expirations[0])
                else:
                    return {}
            
            result = {
                'calls': options.calls,
                'puts': options.puts
            }
            
            # Cache the data
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
            logger.info(f"Successfully fetched and cached options data for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching options data for {symbol}: {str(e)}")
            return {}
    
    def get_sector_performance(self) -> pd.DataFrame:
        """
        Get sector performance data with enhanced caching
        
        Returns:
            pd.DataFrame: Sector performance data
        """
        try:
            cache_key = "sector_performance"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info("Cache hit for sector performance data")
                return self.cache[cache_key]
            
            logger.info("Cache miss for sector performance data, fetching from API")
            
            # Sector ETFs
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financials': 'XLF',
                'Consumer Discretionary': 'XLY',
                'Communication Services': 'XLC',
                'Industrials': 'XLI',
                'Consumer Staples': 'XLP',
                'Energy': 'XLE',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE',
                'Materials': 'XLB'
            }
            
            performance_data = []
            
            for sector, etf in sector_etfs.items():
                data = self.get_stock_data(etf, period='1mo')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    previous_price = data['Close'].iloc[-2]
                    change = current_price - previous_price
                    change_pct = (change / previous_price) * 100
                    
                    performance_data.append({
                        'Sector': sector,
                        'ETF': etf,
                        'Current Price': current_price,
                        'Change': change,
                        'Change %': change_pct
                    })
            
            if performance_data:
                result = pd.DataFrame(performance_data)
                # Cache the data
                self.cache[cache_key] = result
                self.cache_timestamps[cache_key] = time.time()
                logger.info("Successfully fetched and cached sector performance data")
                return result
            else:
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching sector performance: {str(e)}")
            return pd.DataFrame()
    
    def get_market_indices(self) -> pd.DataFrame:
        """
        Get major market indices data with enhanced caching
        
        Returns:
            pd.DataFrame: Market indices data
        """
        try:
            cache_key = "market_indices"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info("Cache hit for market indices data")
                return self.cache[cache_key]
            
            logger.info("Cache miss for market indices data, fetching from API")
            
            indices = {
                'S&P 500': '^GSPC',
                'NASDAQ': '^IXIC',
                'DOW JONES': '^DJI',
                'VIX': '^VIX',
                'Russell 2000': '^RUT',
                '10Y Treasury': '^TNX'
            }
            
            indices_data = []
            
            for name, symbol in indices.items():
                data = self.get_stock_data(symbol, period='5d')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    previous_price = data['Close'].iloc[-2]
                    change = current_price - previous_price
                    change_pct = (change / previous_price) * 100
                    
                    indices_data.append({
                        'Index': name,
                        'Symbol': symbol,
                        'Current Value': current_price,
                        'Change': change,
                        'Change %': change_pct
                    })
            
            if indices_data:
                result = pd.DataFrame(indices_data)
                # Cache the data
                self.cache[cache_key] = result
                self.cache_timestamps[cache_key] = time.time()
                logger.info("Successfully fetched and cached market indices data")
                return result
            else:
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching market indices: {str(e)}")
            return pd.DataFrame()
    
    def get_top_movers(self, market: str = 'us') -> pd.DataFrame:
        """
        Get top movers (gainers and losers) with enhanced caching
        
        Args:
            market (str): Market to analyze
            
        Returns:
            pd.DataFrame: Top movers data
        """
        try:
            cache_key = f"top_movers_{market}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for top movers data ({market})")
                return self.cache[cache_key]
            
            logger.info(f"Cache miss for top movers data ({market}), fetching from API")
            
            # Popular stocks for analysis
            popular_stocks = [
                'AAPL', 'MSFT', 'JPM', 'V', 'JNJ', 'PG', 'XOM', 'KO', 'HD', 'UNH',
                'PG', 'UNH', 'HD', 'MA', 'PYPL', 'ADBE', 'CRM', 'NFLX', 'CMCSA', 'PFE'
            ]
            
            movers_data = []
            
            for symbol in popular_stocks:
                data = self.get_stock_data(symbol, period='1d')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    previous_price = data['Open'].iloc[0]
                    change = current_price - previous_price
                    change_pct = (change / previous_price) * 100
                    volume = data['Volume'].iloc[0]
                    
                    movers_data.append({
                        'Symbol': symbol,
                        'Current Price': current_price,
                        'Change': change,
                        'Change %': change_pct,
                        'Volume': volume
                    })
            
            if movers_data:
                df = pd.DataFrame(movers_data)
                # Sort by absolute change percentage
                df['Abs Change %'] = df['Change %'].abs()
                df = df.sort_values('Abs Change %', ascending=False)
                df = df.drop('Abs Change %', axis=1)
                result = df.head(10)
                
                # Cache the data
                self.cache[cache_key] = result
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched and cached top movers data ({market})")
                return result
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching top movers: {str(e)}")
            return pd.DataFrame()
    
    def get_economic_indicators(self) -> Dict:
        """
        Get economic indicators with enhanced caching
        
        Returns:
            Dict: Economic indicators data
        """
        try:
            cache_key = "economic_indicators"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                logger.info("Cache hit for economic indicators data")
                return self.cache[cache_key]
            
            logger.info("Cache miss for economic indicators data, fetching from API")
            
            indicators = {
                '10Y Treasury Yield': '^TNX',
                '2Y Treasury Yield': '^UST2YR',
                '30Y Treasury Yield': '^TYX',
                'Dollar Index': 'DX-Y.NYB',
                'Gold': 'GC=F',
                'Oil': 'CL=F'
            }
            
            indicators_data = {}
            
            for name, symbol in indicators.items():
                data = self.get_stock_data(symbol, period='5d')
                if not data.empty:
                    current_value = data['Close'].iloc[-1]
                    previous_value = data['Close'].iloc[-2]
                    change = current_value - previous_value
                    change_pct = (change / previous_value) * 100
                    
                    indicators_data[name] = {
                        'Current Value': current_value,
                        'Change': change,
                        'Change %': change_pct
                    }
            
            # Cache the data
            self.cache[cache_key] = indicators_data
            self.cache_timestamps[cache_key] = time.time()
            logger.info("Successfully fetched and cached economic indicators data")
            return indicators_data
            
        except Exception as e:
            logger.error(f"Error fetching economic indicators: {str(e)}")
            return {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """
        Check if cached data is still valid
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: True if cache is valid
        """
        if key not in self.cache_timestamps:
            return False
        return time.time() - self.cache_timestamps[key] < self.cache_duration
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_timestamps.clear()
        # Clear requests-cache as well
        requests_cache.clear()
        logger.info("Cache cleared (both internal and requests-cache)")
    
    def set_cache_duration(self, duration: int):
        """
        Set cache duration in seconds
        
        Args:
            duration (int): Cache duration in seconds
        """
        self.cache_duration = duration
        logger.info(f"Cache duration set to {duration} seconds")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dict: Cache statistics
        """
        cache_size = len(self.cache)
        cache_keys = list(self.cache.keys())
        total_cache_size = sum(len(str(v)) for v in self.cache.values())
        
        return {
            'cache_size': cache_size,
            'cache_keys': cache_keys,
            'total_cache_size_bytes': total_cache_size,
            'cache_duration_seconds': self.cache_duration,
            'requests_cache_enabled': True
        }
