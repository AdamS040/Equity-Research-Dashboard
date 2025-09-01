"""
Market Data Fetcher Module
Handles real-time and historical market data retrieval
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """
    Comprehensive market data fetching class
    Supports multiple data sources and caching
    """
    
    def __init__(self, cache_duration: int = 300):
        """
        Initialize the market data fetcher
        
        Args:
            cache_duration (int): Cache duration in seconds
        """
        self.cache_duration = cache_duration
        self.cache = {}
        self.last_update = {}
        
        # Market indices mapping
        self.indices = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC', 
            'DOW JONES': '^DJI',
            'VIX': '^VIX',
            'Russell 2000': '^RUT',
            '10Y Treasury': '^TNX'
        }
        
        # Sector ETFs for sector analysis
        self.sector_etfs = {
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
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.last_update:
            return False
        return time.time() - self.last_update[key] < self.cache_duration
    
    def get_stock_data(self, symbol: str, period: str = '1y', 
                      interval: str = '1d') -> pd.DataFrame:
        """
        Get stock price data with robust error handling
        
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
                return self.cache[cache_key]
            
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
            
            # Create ticker with custom session
            ticker = yf.Ticker(symbol)
            ticker._session = session
            
            # Try to get data with progress disabled
            data = ticker.history(period=period, interval=interval)
            
            if not data.empty:
                # Cache the data
                self.cache[cache_key] = data
                self.last_update[cache_key] = time.time()
                logger.info(f"Successfully fetched data for {symbol}")
                return data
            else:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get comprehensive stock information
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Stock information
        """
        cache_key = f"{symbol}_info"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            self.cache[cache_key] = info
            self.last_update[cache_key] = time.time()
            logger.info(f"Fetched info for {symbol}")
            return info
            
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            return {}
    
    def get_multiple_stocks(self, symbols: List[str], period: str = '1y') -> pd.DataFrame:
        """
        Get data for multiple stocks
        
        Args:
            symbols (List[str]): List of stock symbols
            period (str): Time period
            
        Returns:
            pd.DataFrame: Multi-stock data
        """
        cache_key = f"multi_{'_'.join(symbols)}_{period}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            data = yf.download(symbols, period=period)
            
            if not data.empty:
                self.cache[cache_key] = data
                self.last_update[cache_key] = time.time()
                logger.info(f"Fetched data for {len(symbols)} symbols")
                return data
            else:
                logger.warning(f"No data found for symbols: {symbols}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching multiple stocks: {str(e)}")
            return pd.DataFrame()
    
    def get_market_indices(self, period: str = '5d') -> pd.DataFrame:
        """
        Get major market indices data
        
        Args:
            period (str): Time period
            
        Returns:
            pd.DataFrame: Market indices data
        """
        symbols = list(self.indices.values())
        return self.get_multiple_stocks(symbols, period)
    
    def get_sector_performance(self, period: str = '1mo') -> pd.DataFrame:
        """
        Get sector performance data
        
        Args:
            period (str): Time period
            
        Returns:
            pd.DataFrame: Sector performance data
        """
        symbols = list(self.sector_etfs.values())
        return self.get_multiple_stocks(symbols, period)
    
    def get_real_time_quote(self, symbol: str) -> Dict:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Real-time quote data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                volume = data['Volume'].iloc[-1]
                
                # Get previous close for change calculation
                hist = ticker.history(period='2d')
                if len(hist) >= 2:
                    previous_close = hist['Close'].iloc[-2]
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                else:
                    change = 0
                    change_percent = 0
                
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': volume,
                    'timestamp': data.index[-1]
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching real-time quote for {symbol}: {str(e)}")
            return {}
    
    def get_top_gainers_losers(self, market: str = 'US', limit: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get top gainers and losers with enhanced data
        
        Args:
            market (str): Market region
            limit (int): Number of stocks to return for each category
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (gainers, losers)
        """
        # Extended list of popular stocks for comprehensive analysis
        popular_stocks = [
            'AAPL', 'MSFT', 'JPM', 'V', 'JNJ', 'PG', 'XOM',
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'MA', 'HD', 'BAC',
            'DIS', 'ADBE', 'NFLX', 'CRM', 'PYPL', 'INTC', 'AMD', 'ORCL',
            'NKE', 'KO', 'PEP', 'ABT', 'TMO', 'AVGO', 'COST', 'MRK',
            'PFE', 'TXN', 'ACN', 'DHR', 'LLY', 'VZ', 'CMCSA', 'BMY',
            'QCOM', 'HON', 'RTX', 'LOW', 'UPS', 'SPGI', 'T', 'DE',
            'CAT', 'MMC', 'AXP', 'GS', 'MS', 'BLK', 'SCHW', 'USB',
            'PNC', 'COF', 'TFC', 'KEY', 'RF', 'HBAN', 'FITB', 'ZION'
        ]
        
        try:
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
                        volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                        
                        changes.append({
                            'Symbol': symbol,
                            'Price': current,
                            'Change': change,
                            'Change%': change_percent,
                            'Volume': volume,
                            'Market_Cap': self._get_market_cap(symbol, current)
                        })
                        successful_fetches += 1
                        
                        # Limit to first 50 successful fetches for performance
                        if successful_fetches >= 50:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error fetching {symbol}: {e}")
                    continue
            
            if not changes:
                logger.warning("No data available for top movers")
                return pd.DataFrame(), pd.DataFrame()
            
            # Create DataFrame and sort by percentage change
            df = pd.DataFrame(changes)
            df = df.sort_values('Change%', ascending=False)
            
            # Top gainers and losers
            gainers = df.head(limit)
            losers = df.tail(limit)
            
            logger.info(f"Successfully fetched top movers: {len(gainers)} gainers, {len(losers)} losers")
            return gainers, losers
            
        except Exception as e:
            logger.error(f"Error fetching top movers: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()
    
    def _get_market_cap(self, symbol: str, current_price: float) -> float:
        """Helper method to estimate market cap"""
        try:
            # This is a simplified market cap calculation
            # In a real implementation, you'd get this from the stock info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('marketCap', 0) / 1e9  # Convert to billions
        except:
            return 0.0
    
    def get_earnings_calendar(self, symbol: str) -> pd.DataFrame:
        """
        Get earnings calendar for a stock
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Earnings calendar data
        """
        try:
            ticker = yf.Ticker(symbol)
            earnings = ticker.calendar
            
            if earnings is not None and not earnings.empty:
                return earnings
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching earnings calendar for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_options_chain(self, symbol: str) -> Dict:
        """
        Get options chain for a stock
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Options chain data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            exp_dates = ticker.options
            
            if not exp_dates:
                return {}
            
            # Get options for nearest expiration
            options = ticker.option_chain(exp_dates[0])
            
            return {
                'calls': options.calls,
                'puts': options.puts,
                'expiration': exp_dates[0]
            }
            
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {str(e)}")
            return {}
    
    def get_insider_trading(self, symbol: str) -> pd.DataFrame:
        """
        Get insider trading data
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Insider trading data
        """
        try:
            ticker = yf.Ticker(symbol)
            insider_purchases = ticker.insider_purchases
            insider_trades = ticker.insider_roster_holders
            
            return insider_trades if insider_trades is not None else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching insider trading for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.last_update.clear()
        logger.info("Cache cleared")
    
    def get_market_status(self) -> Dict:
        """
        Get current market status
        
        Returns:
            Dict: Market status information
        """
        try:
            # Simple market hours check (US markets)
            now = datetime.now()
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            # Check if it's a weekday
            is_weekday = now.weekday() < 5
            
            # Check if market is currently open
            is_open = is_weekday and market_open <= now <= market_close
            
            return {
                'is_open': is_open,
                'next_open': market_open + timedelta(days=1) if not is_open else market_open,
                'next_close': market_close if is_open else market_close,
                'timezone': 'US/Eastern'
            }
            
        except Exception as e:
            logger.error(f"Error checking market status: {str(e)}")
            return {'is_open': False}


# Convenience functions
def get_stock_price(symbol: str) -> float:
    """Get current stock price"""
    fetcher = MarketDataFetcher()
    quote = fetcher.get_real_time_quote(symbol)
    return quote.get('price', 0.0)

def get_market_overview() -> Dict:
    """Get market overview"""
    fetcher = MarketDataFetcher()
    indices_data = fetcher.get_market_indices()
    
    overview = {}
    for name, symbol in fetcher.indices.items():
        if symbol in indices_data['Close'].columns:
            current = indices_data['Close'][symbol].iloc[-1]
            previous = indices_data['Close'][symbol].iloc[-2] if len(indices_data) > 1 else current
            change = current - previous
            change_pct = (change / previous) * 100 if previous != 0 else 0
            
            overview[name] = {
                'price': current,
                'change': change,
                'change_percent': change_pct
            }
    
    return overview