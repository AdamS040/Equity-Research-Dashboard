"""
Data Fetcher Module
Comprehensive data retrieval from multiple sources
"""
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional, Tuple
import time
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Comprehensive data fetcher for financial data
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
        self.cache_duration = 300  # 5 minutes default
        
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
            data = ticker.history(period=period, interval=interval, progress=False)
            
            if not data.empty:
                # Cache the data
                self.cache[cache_key] = data
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Successfully fetched data for {symbol}")
                return data
            else:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_financial_statements(self, symbol: str) -> Dict:
        """
        Get financial statements
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Financial statements
        """
        try:
            ticker = yf.Ticker(symbol)
            
            statements = {
                'income_statement': ticker.income_stmt,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
                'info': ticker.info
            }
            
            return statements
            
        except Exception as e:
            logger.error(f"Error fetching financial statements for {symbol}: {str(e)}")
            return {}
    
    def get_market_data(self, symbols: List[str], period: str = '1d') -> pd.DataFrame:
        """
        Get market data for multiple symbols
        
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
                return self.cache[cache_key]
            
            data = yf.download(symbols, period=period, progress=False)
            
            if not data.empty:
                # Cache the data
                self.cache[cache_key] = data
                self.cache_timestamps[cache_key] = time.time()
                logger.info(f"Fetched market data for {len(symbols)} symbols")
                return data
            else:
                logger.warning(f"No market data found for symbols: {symbols}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return pd.DataFrame()
    
    def get_earnings_calendar(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get earnings calendar for symbols
        
        Args:
            symbols (List[str]): List of stock symbols
            
        Returns:
            pd.DataFrame: Earnings calendar
        """
        try:
            earnings_data = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
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
            
            if earnings_data:
                return pd.DataFrame(earnings_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {str(e)}")
            return pd.DataFrame()
    
    def get_news_data(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news data for a symbol
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of news articles to fetch
            
        Returns:
            List[Dict]: News data
        """
        try:
            ticker = yf.Ticker(symbol)
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
                return formatted_news
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    def get_analyst_recommendations(self, symbol: str) -> pd.DataFrame:
        """
        Get analyst recommendations
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Analyst recommendations
        """
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is not None and not recommendations.empty:
                return recommendations
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching analyst recommendations for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_major_holders(self, symbol: str) -> pd.DataFrame:
        """
        Get major holders data
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Major holders data
        """
        try:
            ticker = yf.Ticker(symbol)
            major_holders = ticker.major_holders
            
            if major_holders is not None and not major_holders.empty:
                return major_holders
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching major holders for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_institutional_holders(self, symbol: str) -> pd.DataFrame:
        """
        Get institutional holders data
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Institutional holders data
        """
        try:
            ticker = yf.Ticker(symbol)
            institutional_holders = ticker.institutional_holders
            
            if institutional_holders is not None and not institutional_holders.empty:
                return institutional_holders
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching institutional holders for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_options_data(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """
        Get options data
        
        Args:
            symbol (str): Stock symbol
            expiration_date (str): Option expiration date
            
        Returns:
            Dict: Options data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            if expiration_date:
                options = ticker.option_chain(expiration_date)
            else:
                # Get next expiration
                expirations = ticker.options
                if expirations:
                    options = ticker.option_chain(expirations[0])
                else:
                    return {}
            
            return {
                'calls': options.calls,
                'puts': options.puts
            }
            
        except Exception as e:
            logger.error(f"Error fetching options data for {symbol}: {str(e)}")
            return {}
    
    def get_sector_performance(self) -> pd.DataFrame:
        """
        Get sector performance data
        
        Returns:
            pd.DataFrame: Sector performance data
        """
        try:
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
            
            return pd.DataFrame(performance_data)
            
        except Exception as e:
            logger.error(f"Error fetching sector performance: {str(e)}")
            return pd.DataFrame()
    
    def get_market_indices(self) -> pd.DataFrame:
        """
        Get major market indices data
        
        Returns:
            pd.DataFrame: Market indices data
        """
        try:
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
            
            return pd.DataFrame(indices_data)
            
        except Exception as e:
            logger.error(f"Error fetching market indices: {str(e)}")
            return pd.DataFrame()
    
    def get_top_movers(self, market: str = 'us') -> pd.DataFrame:
        """
        Get top movers (gainers and losers)
        
        Args:
            market (str): Market to analyze
            
        Returns:
            pd.DataFrame: Top movers data
        """
        try:
            # Popular stocks for analysis
            popular_stocks = [
                'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ',
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
                return df.head(10)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching top movers: {str(e)}")
            return pd.DataFrame()
    
    def get_economic_indicators(self) -> Dict:
        """
        Get economic indicators
        
        Returns:
            Dict: Economic indicators data
        """
        try:
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
        logger.info("Cache cleared")
    
    def set_cache_duration(self, duration: int):
        """
        Set cache duration in seconds
        
        Args:
            duration (int): Cache duration in seconds
        """
        self.cache_duration = duration
        logger.info(f"Cache duration set to {duration} seconds")
