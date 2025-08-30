"""
Test suite for data modules
Tests data fetching, financial data processing, and market data functionality
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import requests

# Import modules to test
from data.data_fetcher import DataFetcher
from data.financial_data import FinancialDataProcessor, FinancialDataAggregator
from data.market_data import MarketDataFetcher


class TestDataFetcher(unittest.TestCase):
    """Test DataFetcher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = DataFetcher()
        
        # Mock API keys
        self.mock_api_keys = {
            'alpha_vantage': 'test_key_1',
            'fmp': 'test_key_2',
            'news': 'test_key_3',
            'quandl': 'test_key_4'
        }
    
    @patch('yfinance.download')
    def test_get_stock_data(self, mock_download):
        """Test getting stock data"""
        # Mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        mock_data = pd.DataFrame({
            'Open': np.random.normal(100, 10, len(dates)),
            'High': np.random.normal(105, 10, len(dates)),
            'Low': np.random.normal(95, 10, len(dates)),
            'Close': np.random.normal(100, 10, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        mock_download.return_value = mock_data
        
        result = self.fetcher.get_stock_data('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        self.assertIn('Close', result.columns)
        self.assertIn('Volume', result.columns)
    
    @patch('yfinance.Ticker')
    def test_get_financial_statements(self, mock_ticker):
        """Test getting financial statements"""
        # Mock financial data
        mock_stock = Mock()
        mock_stock.financials = pd.DataFrame({
            'Total Revenue': [1000000000, 900000000],
            'Net Income': [100000000, 90000000]
        }, index=['2023-12-31', '2022-12-31'])
        mock_stock.balance_sheet = pd.DataFrame({
            'Total Assets': [2000000000, 1800000000],
            'Total Equity': [1200000000, 1080000000]
        }, index=['2023-12-31', '2022-12-31'])
        mock_stock.cashflow = pd.DataFrame({
            'Operating Cash Flow': [120000000, 108000000],
            'Free Cash Flow': [100000000, 90000000]
        }, index=['2023-12-31', '2022-12-31'])
        mock_ticker.return_value = mock_stock
        
        result = self.fetcher.get_financial_statements('AAPL')
        
        self.assertIn('income_statement', result)
        self.assertIn('balance_sheet', result)
        self.assertIn('cash_flow', result)
        self.assertIsInstance(result['income_statement'], pd.DataFrame)
    
    @patch('yfinance.Ticker')
    def test_get_market_data(self, mock_ticker):
        """Test getting market data for multiple symbols"""
        # Mock market data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        mock_data = pd.DataFrame({
            'AAPL': np.random.normal(100, 10, len(dates)),
            'MSFT': np.random.normal(200, 20, len(dates)),
            'GOOGL': np.random.normal(150, 15, len(dates))
        }, index=dates)
        
        with patch('yfinance.download') as mock_download:
            mock_download.return_value = mock_data
            
            result = self.fetcher.get_market_data(['AAPL', 'MSFT', 'GOOGL'])
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertIn('AAPL', result.columns)
            self.assertIn('MSFT', result.columns)
            self.assertIn('GOOGL', result.columns)
    
    def test_retry_decorator_success_on_first_attempt(self):
        """Test that retry decorator works correctly on first attempt"""
        from data.data_fetcher import retry_on_failure
        
        @retry_on_failure(max_retries=3, backoff_factor=1.0)
        def mock_function():
            return "success"
        
        result = mock_function()
        self.assertEqual(result, "success")
    
    def test_retry_decorator_success_after_retries(self):
        """Test that retry decorator succeeds after some failures"""
        from data.data_fetcher import retry_on_failure
        call_count = 0
        
        @retry_on_failure(max_retries=3, backoff_factor=0.1)
        def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = mock_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_retry_decorator_max_retries_exceeded(self):
        """Test that retry decorator respects maximum retry limit"""
        from data.data_fetcher import retry_on_failure
        call_count = 0
        
        @retry_on_failure(max_retries=2, backoff_factor=0.1)
        def mock_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent failure")
        
        with self.assertRaises(ValueError):
            mock_function()
        
        self.assertEqual(call_count, 3)  # Initial attempt + 2 retries
    
    def test_retry_decorator_rate_limit_handling(self):
        """Test that retry decorator handles rate limit errors with longer delays"""
        from data.data_fetcher import retry_on_failure
        import time
        call_count = 0
        
        @retry_on_failure(max_retries=2, backoff_factor=0.1)
        def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Simulate rate limit error
                error = requests.exceptions.HTTPError()
                error.response = Mock()
                error.response.status_code = 429
                raise error
            return "success"
        
        start_time = time.time()
        result = mock_function()
        end_time = time.time()
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)
        # Should have taken longer due to rate limit delay
        self.assertGreater(end_time - start_time, 0.1)
    
    def test_cache_functionality(self):
        """Test that caching works correctly"""
        # Mock the _fetch_with_yfinance method
        with patch.object(self.fetcher, '_fetch_with_yfinance') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            # First call should fetch from API
            result1 = self.fetcher.get_stock_data('AAPL', period='1d')
            self.assertEqual(len(result1), 3)
            mock_fetch.assert_called_once()
            
            # Reset mock call count
            mock_fetch.reset_mock()
            
            # Second call should use cache
            result2 = self.fetcher.get_stock_data('AAPL', period='1d')
            self.assertEqual(len(result2), 3)
            mock_fetch.assert_not_called()  # Should not be called due to cache
    
    def test_cache_expiration(self):
        """Test that cache expires correctly"""
        import time
        # Set short cache duration
        self.fetcher.set_cache_duration(1)  # 1 second
        
        with patch.object(self.fetcher, '_fetch_with_yfinance') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            # First call
            result1 = self.fetcher.get_stock_data('AAPL', period='1d')
            self.assertEqual(len(result1), 3)
            
            # Wait for cache to expire
            time.sleep(1.1)
            
            # Second call should fetch again due to expiration
            result2 = self.fetcher.get_stock_data('AAPL', period='1d')
            self.assertEqual(len(result2), 3)
            self.assertEqual(mock_fetch.call_count, 2)
    
    def test_cache_key_uniqueness(self):
        """Test that different parameters create different cache keys"""
        with patch.object(self.fetcher, '_fetch_with_yfinance') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            # Call with different parameters
            self.fetcher.get_stock_data('AAPL', period='1d')
            self.fetcher.get_stock_data('AAPL', period='1w')
            self.fetcher.get_stock_data('GOOGL', period='1d')
            
            # Should have 3 different cache entries
            self.assertEqual(len(self.fetcher.cache), 3)
    
    def test_clear_cache(self):
        """Test that cache clearing works correctly"""
        with patch.object(self.fetcher, '_fetch_with_yfinance') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            # Add some data to cache
            self.fetcher.get_stock_data('AAPL', period='1d')
            self.fetcher.get_stock_data('GOOGL', period='1d')
            
            # Verify cache has data
            self.assertGreater(len(self.fetcher.cache), 0)
            
            # Clear cache
            self.fetcher.clear_cache()
            
            # Verify cache is empty
            self.assertEqual(len(self.fetcher.cache), 0)
            self.assertEqual(len(self.fetcher.cache_timestamps), 0)
    
    def test_get_cache_stats(self):
        """Test that cache statistics are returned correctly"""
        with patch.object(self.fetcher, '_fetch_with_yfinance') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            # Add some data to cache
            self.fetcher.get_stock_data('AAPL', period='1d')
            
            stats = self.fetcher.get_cache_stats()
            
            self.assertIn('cache_size', stats)
            self.assertIn('cache_keys', stats)
            self.assertIn('total_cache_size_bytes', stats)
            self.assertIn('cache_duration_seconds', stats)
            self.assertIn('requests_cache_enabled', stats)
            
            self.assertEqual(stats['cache_size'], 1)
            self.assertTrue(stats['requests_cache_enabled'])
    
    def test_session_creation(self):
        """Test that session is created with proper configuration"""
        session = self.fetcher._create_session()
        
        # Check that session has retry adapter
        self.assertIsNotNone(session.adapters.get('http://'))
        self.assertIsNotNone(session.adapters.get('https://'))
        
        # Check headers
        self.assertIn('User-Agent', session.headers)
        self.assertIn('Accept', session.headers)
    
    def test_fetch_with_yfinance_retry_logic(self):
        """Test that _fetch_with_yfinance uses retry logic"""
        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            
            # First two calls fail, third succeeds
            mock_ticker.history.side_effect = [
                ValueError("API Error"),
                ValueError("API Error"),
                pd.DataFrame({'Close': [100, 101, 102]})
            ]
            
            result = self.fetcher._fetch_with_yfinance('AAPL', period='1d')
            
            self.assertEqual(len(result), 3)
            self.assertEqual(mock_ticker.history.call_count, 3)
    
    def test_fetch_with_yfinance_empty_data_raises_error(self):
        """Test that empty data raises ValueError"""
        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            mock_ticker.history.return_value = pd.DataFrame()  # Empty data
            
            with self.assertRaises(ValueError):
                self.fetcher._fetch_with_yfinance('INVALID', period='1d')
    
    def test_lru_cache_functionality(self):
        """Test that LRU cache works for ticker info"""
        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            mock_ticker.info = {'name': 'Apple Inc.', 'sector': 'Technology'}
            
            # First call
            result1 = self.fetcher._get_cached_ticker_info('AAPL')
            self.assertEqual(result1['name'], 'Apple Inc.')
            
            # Second call should use cache
            result2 = self.fetcher._get_cached_ticker_info('AAPL')
            self.assertEqual(result2['name'], 'Apple Inc.')
            
            # Ticker should only be created once due to LRU cache
            mock_ticker_class.assert_called_once_with('AAPL')
    
    def test_rate_limiting_delays(self):
        """Test that rate limiting delays are applied"""
        import time
        with patch.object(self.fetcher, '_fetch_with_yfinance') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            start_time = time.time()
            self.fetcher.get_stock_data('AAPL', period='1d')
            end_time = time.time()
            
            # Should have some delay due to rate limiting
            self.assertGreater(end_time - start_time, 0.05)
    
    def test_financial_statements_caching(self):
        """Test that financial statements are cached correctly"""
        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            
            # Mock financial data
            mock_ticker.income_stmt = pd.DataFrame({'Revenue': [1000, 1100]})
            mock_ticker.balance_sheet = pd.DataFrame({'Assets': [2000, 2200]})
            mock_ticker.cashflow = pd.DataFrame({'Cash': [500, 550]})
            mock_ticker.info = {'name': 'Apple Inc.'}
            
            # First call
            result1 = self.fetcher.get_financial_statements('AAPL')
            self.assertIn('income_statement', result1)
            
            # Reset mock to verify cache usage
            mock_ticker_class.reset_mock()
            
            # Second call should use cache
            result2 = self.fetcher.get_financial_statements('AAPL')
            self.assertIn('income_statement', result2)
            
            # Ticker should not be created again due to cache
            mock_ticker_class.assert_not_called()
    
    def test_market_data_caching(self):
        """Test that market data is cached correctly"""
        with patch('yfinance.download') as mock_download:
            mock_download.return_value = pd.DataFrame({'Close': [100, 101, 102]})
            
            symbols = ['AAPL', 'GOOGL']
            
            # First call
            result1 = self.fetcher.get_market_data(symbols, period='1d')
            self.assertEqual(len(result1), 3)
            
            # Reset mock
            mock_download.reset_mock()
            
            # Second call should use cache
            result2 = self.fetcher.get_market_data(symbols, period='1d')
            self.assertEqual(len(result2), 3)
            
            # Download should not be called again due to cache
            mock_download.assert_not_called()
    
    def test_earnings_calendar_caching(self):
        """Test that earnings calendar is cached correctly"""
        with patch('yfinance.Ticker') as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            
            # Mock earnings calendar data
            calendar_data = pd.DataFrame({
                'Earnings Date': ['2024-01-15'],
                'Earnings Average': [2.50],
                'Revenue Average': [1000000]
            })
            mock_ticker.calendar = calendar_data
            
            symbols = ['AAPL']
            
            # First call
            result1 = self.fetcher.get_earnings_calendar(symbols)
            self.assertGreater(len(result1), 0)
            
            # Reset mock
            mock_ticker_class.reset_mock()
            
            # Second call should use cache
            result2 = self.fetcher.get_earnings_calendar(symbols)
            self.assertGreater(len(result2), 0)
            
            # Ticker should not be created again due to cache
            mock_ticker_class.assert_not_called()
    
    @patch('yfinance.Ticker')
    def test_get_earnings_calendar(self, mock_ticker):
        """Test getting earnings calendar"""
        # Mock earnings data
        mock_stock = Mock()
        mock_stock.calendar = pd.DataFrame({
            'Earnings Date': ['2024-01-25', '2024-04-25'],
            'Earnings Average': [2.10, 2.25],
            'Earnings Low': [2.00, 2.15],
            'Earnings High': [2.20, 2.35]
        })
        mock_ticker.return_value = mock_stock
        
        result = self.fetcher.get_earnings_calendar('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('Earnings Date', result.columns)
    
    @patch('yfinance.Ticker')
    def test_get_news(self, mock_ticker):
        """Test getting news data"""
        # Mock news data
        mock_stock = Mock()
        mock_stock.news = [
            {
                'title': 'Test News 1',
                'link': 'http://test1.com',
                'publisher': 'Test Publisher',
                'published': '2024-01-01'
            },
            {
                'title': 'Test News 2',
                'link': 'http://test2.com',
                'publisher': 'Test Publisher',
                'published': '2024-01-02'
            }
        ]
        mock_ticker.return_value = mock_stock
        
        result = self.fetcher.get_news('AAPL')
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('title', result[0])
        self.assertIn('link', result[0])
    
    @patch('yfinance.Ticker')
    def test_get_analyst_recommendations(self, mock_ticker):
        """Test getting analyst recommendations"""
        # Mock recommendations data
        mock_stock = Mock()
        mock_stock.recommendations = pd.DataFrame({
            'To Grade': ['Buy', 'Hold', 'Sell'],
            'From Grade': ['Hold', 'Buy', 'Hold'],
            'Action': ['up', 'main', 'down'],
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        mock_ticker.return_value = mock_stock
        
        result = self.fetcher.get_analyst_recommendations('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('To Grade', result.columns)
        self.assertIn('Action', result.columns)
    
    @patch('yfinance.Ticker')
    def test_get_major_holders(self, mock_ticker):
        """Test getting major holders"""
        # Mock holders data
        mock_stock = Mock()
        mock_stock.major_holders = pd.DataFrame({
            'Holder': ['Vanguard', 'BlackRock', 'State Street'],
            'Shares': [100000000, 80000000, 60000000],
            'Percentage': [10.0, 8.0, 6.0]
        })
        mock_ticker.return_value = mock_stock
        
        result = self.fetcher.get_major_holders('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('Holder', result.columns)
        self.assertIn('Shares', result.columns)
    
    @patch('yfinance.Ticker')
    def test_get_options_data(self, mock_ticker):
        """Test getting options data"""
        # Mock options data
        mock_stock = Mock()
        mock_stock.options = ['2024-01-19', '2024-02-16', '2024-03-15']
        
        # Mock option chain
        mock_option_chain = Mock()
        mock_option_chain.calls = pd.DataFrame({
            'strike': [100, 110, 120],
            'lastPrice': [5.0, 2.0, 0.5],
            'bid': [4.9, 1.9, 0.4],
            'ask': [5.1, 2.1, 0.6],
            'volume': [1000, 500, 200],
            'openInterest': [5000, 2500, 1000]
        })
        mock_option_chain.puts = pd.DataFrame({
            'strike': [100, 110, 120],
            'lastPrice': [2.0, 5.0, 10.0],
            'bid': [1.9, 4.9, 9.9],
            'ask': [2.1, 5.1, 10.1],
            'volume': [800, 1200, 1500],
            'openInterest': [4000, 6000, 7500]
        })
        
        mock_stock.option_chain.return_value = mock_option_chain
        mock_ticker.return_value = mock_stock
        
        result = self.fetcher.get_options_data('AAPL', '2024-01-19')
        
        self.assertIn('calls', result)
        self.assertIn('puts', result)
        self.assertIsInstance(result['calls'], pd.DataFrame)
        self.assertIsInstance(result['puts'], pd.DataFrame)
    
    def test_cache_functionality(self):
        """Test caching functionality"""
        # Test cache validation
        result = self.fetcher._is_cache_valid('test_key')
        self.assertIsInstance(result, bool)
        
        # Test cache duration setting
        self.fetcher.set_cache_duration(300)
        self.assertEqual(self.fetcher.cache_duration, 300)
        
        # Test cache clearing
        self.fetcher.clear_cache()
        # Verify cache is empty after clearing
        self.assertEqual(len(self.fetcher.cache), 0)
        self.assertEqual(len(self.fetcher.cache_timestamps), 0)


class TestFinancialDataProcessor(unittest.TestCase):
    """Test FinancialDataProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = FinancialDataProcessor()
        
        # Mock financial statement data
        self.mock_income_stmt = pd.DataFrame({
            'Total Revenue': [1000000, 900000, 800000],
            'Net Income': [100000, 90000, 80000],
            'Gross Profit': [400000, 360000, 320000],
            'EBIT': [150000, 135000, 120000],
            'EBITDA': [180000, 162000, 144000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        
        self.mock_balance_sheet = pd.DataFrame({
            'Total Assets': [2000000, 1800000, 1600000],
            'Total Equity': [1200000, 1080000, 960000],
            'Total Current Assets': [800000, 720000, 640000],
            'Total Current Liabilities': [400000, 360000, 320000],
            'Cash and Cash Equivalents': [200000, 180000, 160000],
            'Total Debt': [300000, 270000, 240000],
            'Inventory': [100000, 90000, 80000],
            'Accounts Receivable': [150000, 135000, 120000],
            'Accounts Payable': [80000, 72000, 64000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        
        self.mock_cash_flow = pd.DataFrame({
            'Operating Cash Flow': [120000, 108000, 96000],
            'Free Cash Flow': [100000, 90000, 80000],
            'Capital Expenditure': [-20000, -18000, -16000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
    
    def test_clean_financial_statement(self):
        """Test financial statement cleaning"""
        # Test with dirty data
        dirty_data = pd.DataFrame({
            'Total Revenue': ['1,000,000', '900,000', '800,000'],
            'Net Income': ['100,000', '90,000', '80,000'],
            'Gross Profit': ['400,000', '360,000', '320,000']
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        
        cleaned_data = self.processor.clean_financial_statement(dirty_data, 'income')
        
        self.assertIsInstance(cleaned_data, pd.DataFrame)
        self.assertEqual(len(cleaned_data), len(dirty_data))
        
        # Check that numeric conversion worked
        self.assertTrue(cleaned_data['TOTAL REVENUE'].dtype in ['float64', 'int64'])
    
    def test_calculate_financial_ratios(self):
        """Test financial ratio calculations"""
        ratios = self.processor.calculate_financial_ratios(
            self.mock_income_stmt, 
            self.mock_balance_sheet, 
            self.mock_cash_flow
        )
        
        self.assertIn('profitability', ratios)
        self.assertIn('liquidity', ratios)
        self.assertIn('solvency', ratios)
        self.assertIn('efficiency', ratios)
        self.assertIn('cash_flow', ratios)
        self.assertIn('growth', ratios)
    
    def test_calculate_technical_indicators(self):
        """Test technical indicator calculations"""
        # Create mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        prices = pd.DataFrame({
            'Close': np.random.normal(100, 10, len(dates)),
            'High': np.random.normal(105, 10, len(dates)),
            'Low': np.random.normal(95, 10, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        indicators = self.processor.calculate_technical_indicators(prices)
        
        self.assertIn('sma_20', indicators)
        self.assertIn('sma_50', indicators)
        self.assertIn('ema_12', indicators)
        self.assertIn('macd', indicators)
        self.assertIn('rsi', indicators)
        self.assertIn('bb_upper', indicators)
        self.assertIn('bb_lower', indicators)
    
    def test_detect_anomalies(self):
        """Test anomaly detection"""
        # Create test data with outliers
        data = pd.Series([1, 2, 3, 4, 5, 100, 6, 7, 8, 9, 10])
        
        # Test z-score method
        anomalies_zscore = self.processor.detect_anomalies(data, method='zscore', threshold=2.0)
        self.assertIsInstance(anomalies_zscore, pd.Series)
        self.assertTrue(anomalies_zscore.sum() > 0)  # Should detect the outlier
        
        # Test IQR method
        anomalies_iqr = self.processor.detect_anomalies(data, method='iqr')
        self.assertIsInstance(anomalies_iqr, pd.Series)
    
    def test_calculate_rolling_metrics(self):
        """Test rolling metrics calculation"""
        # Create mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        prices = pd.DataFrame({
            'Close': np.random.normal(100, 10, len(dates)),
            'Market_Returns': np.random.normal(0.001, 0.015, len(dates))
        }, index=dates)
        
        metrics = self.processor.calculate_rolling_metrics(prices, window=60)
        
        self.assertIn('rolling_volatility', metrics)
        self.assertIn('rolling_sharpe', metrics)
        self.assertIn('rolling_drawdown', metrics)
        self.assertIsInstance(metrics['rolling_volatility'], pd.Series)
    
    def test_normalize_currency(self):
        """Test currency normalization"""
        # Create test data in EUR
        eur_data = pd.DataFrame({
            'Revenue': [1000000, 900000],
            'Assets': [2000000, 1800000]
        })
        
        # Convert to USD
        usd_data = self.processor.normalize_currency(eur_data, 'EUR', 'USD')
        
        self.assertIsInstance(usd_data, pd.DataFrame)
        self.assertEqual(len(usd_data), len(eur_data))
        
        # Check that conversion was applied (EUR to USD should increase values)
        self.assertTrue(usd_data['Revenue'].iloc[0] > eur_data['Revenue'].iloc[0])


class TestFinancialDataAggregator(unittest.TestCase):
    """Test FinancialDataAggregator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.aggregator = FinancialDataAggregator()
    
    @patch('yfinance.Ticker')
    def test_aggregate_company_data(self, mock_ticker):
        """Test company data aggregation"""
        # Mock comprehensive stock data
        mock_stock = Mock()
        mock_stock.info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'marketCap': 2000000000000,
            'beta': 1.2,
            'trailingPE': 25.5,
            'forwardPE': 24.0,
            'priceToBook': 15.2,
            'debtToEquity': 0.8,
            'returnOnEquity': 0.15,
            'returnOnAssets': 0.10
        }
        
        # Mock financial statements
        mock_stock.financials = pd.DataFrame({
            'Total Revenue': [1000000000, 900000000],
            'Net Income': [100000000, 90000000],
            'Free Cash Flow': [80000000, 72000000]
        }, index=['2023-12-31', '2022-12-31'])
        
        mock_stock.balance_sheet = pd.DataFrame({
            'Total Assets': [2000000000, 1800000000],
            'Total Equity': [1200000000, 1080000000],
            'Total Current Assets': [800000000, 720000000],
            'Total Current Liabilities': [400000000, 360000000]
        }, index=['2023-12-31', '2022-12-31'])
        
        mock_stock.cashflow = pd.DataFrame({
            'Operating Cash Flow': [120000000, 108000000],
            'Free Cash Flow': [100000000, 90000000]
        }, index=['2023-12-31', '2022-12-31'])
        
        # Mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        mock_stock.history.return_value = pd.DataFrame({
            'Open': np.random.normal(100, 10, len(dates)),
            'High': np.random.normal(105, 10, len(dates)),
            'Low': np.random.normal(95, 10, len(dates)),
            'Close': np.random.normal(100, 10, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        mock_ticker.return_value = mock_stock
        
        result = self.aggregator.aggregate_company_data('AAPL')
        
        self.assertIn('symbol', result)
        self.assertIn('company_info', result)
        self.assertIn('financial_statements', result)
        self.assertIn('financial_ratios', result)
        self.assertIn('stock_data', result)
        self.assertIn('technical_indicators', result)
        self.assertIn('last_updated', result)
        
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertIsInstance(result['company_info'], dict)
        self.assertIsInstance(result['financial_statements'], dict)
        self.assertIsInstance(result['stock_data'], pd.DataFrame)
    
    def test_compare_companies(self):
        """Test company comparison"""
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        
        with patch.object(self.aggregator, 'aggregate_company_data') as mock_aggregate:
            # Mock aggregated data for each company
            mock_data = {
                'symbol': 'AAPL',
                'company_info': {'longName': 'Apple Inc.'},
                'financial_ratios': {
                    'profitability': {'roe': 0.15, 'roa': 0.10},
                    'valuation': {'pe_ratio': 25.0, 'pb_ratio': 15.0},
                    'solvency': {'debt_to_equity': 0.8},
                    'liquidity': {'current_ratio': 2.0}
                }
            }
            mock_aggregate.return_value = mock_data
            
            result = self.aggregator.compare_companies(symbols)
            
            self.assertIsInstance(result, dict)
            self.assertIn('AAPL', result)
            self.assertIn('MSFT', result)
            self.assertIn('GOOGL', result)
            self.assertIn('relative_metrics', result)
    
    def test_calculate_relative_metrics(self):
        """Test relative metrics calculation"""
        companies_data = {
            'AAPL': {
                'financial_ratios': {
                    'valuation': {'pe_ratio': 25.0, 'pb_ratio': 15.0},
                    'profitability': {'roe': 0.15, 'roa': 0.10},
                    'solvency': {'debt_to_equity': 0.8},
                    'liquidity': {'current_ratio': 2.0}
                }
            },
            'MSFT': {
                'financial_ratios': {
                    'valuation': {'pe_ratio': 30.0, 'pb_ratio': 12.0},
                    'profitability': {'roe': 0.20, 'roa': 0.12},
                    'solvency': {'debt_to_equity': 0.6},
                    'liquidity': {'current_ratio': 2.5}
                }
            }
        }
        
        result = self.aggregator._calculate_relative_metrics(companies_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('pe_ratio_avg', result)
        self.assertIn('roe_avg', result)
        self.assertIn('pe_ratio_rankings', result)
        self.assertIn('roe_rankings', result)


class TestMarketDataFetcher(unittest.TestCase):
    """Test MarketDataFetcher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = MarketDataFetcher()
    
    @patch('yfinance.download')
    def test_get_stock_data(self, mock_download):
        """Test getting stock data with caching"""
        # Mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        mock_data = pd.DataFrame({
            'Open': np.random.normal(100, 10, len(dates)),
            'High': np.random.normal(105, 10, len(dates)),
            'Low': np.random.normal(95, 10, len(dates)),
            'Close': np.random.normal(100, 10, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        mock_download.return_value = mock_data
        
        result = self.fetcher.get_stock_data('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        self.assertIn('Close', result.columns)
    
    def test_cache_validation(self):
        """Test cache validation"""
        # Test with non-existent cache
        result = self.fetcher._is_cache_valid('nonexistent_key')
        self.assertFalse(result)
        
        # Test cache duration setting
        self.fetcher.cache_duration = 300
        self.assertEqual(self.fetcher.cache_duration, 300)


class TestIntegration(unittest.TestCase):
    """Integration tests for data modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_fetcher = DataFetcher()
        self.financial_processor = FinancialDataProcessor()
        self.financial_aggregator = FinancialDataAggregator()
        self.market_fetcher = MarketDataFetcher()
    
    @patch('yfinance.Ticker')
    @patch('yfinance.download')
    def test_full_data_pipeline(self, mock_download, mock_ticker):
        """Test full data processing pipeline"""
        # Mock comprehensive data
        mock_stock = Mock()
        mock_stock.info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'marketCap': 2000000000000,
            'beta': 1.2
        }
        mock_stock.financials = pd.DataFrame({
            'Total Revenue': [1000000000, 900000000],
            'Net Income': [100000000, 90000000],
            'Free Cash Flow': [80000000, 72000000]
        }, index=['2023-12-31', '2022-12-31'])
        mock_stock.balance_sheet = pd.DataFrame({
            'Total Assets': [2000000000, 1800000000],
            'Total Equity': [1200000000, 1080000000]
        }, index=['2023-12-31', '2022-12-31'])
        mock_stock.cashflow = pd.DataFrame({
            'Operating Cash Flow': [120000000, 108000000]
        }, index=['2023-12-31', '2022-12-31'])
        mock_ticker.return_value = mock_stock
        
        # Mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        prices = pd.DataFrame({
            'Close': np.random.normal(100, 10, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        mock_download.return_value = prices
        
        # Run full pipeline
        symbol = 'AAPL'
        
        # 1. Fetch raw data
        stock_data = self.data_fetcher.get_stock_data(symbol)
        financial_statements = self.data_fetcher.get_financial_statements(symbol)
        
        # 2. Process financial data
        cleaned_income = self.financial_processor.clean_financial_statement(
            financial_statements['income_statement'], 'income'
        )
        ratios = self.financial_processor.calculate_financial_ratios(
            cleaned_income,
            financial_statements['balance_sheet'],
            financial_statements['cash_flow']
        )
        
        # 3. Calculate technical indicators
        technical_indicators = self.financial_processor.calculate_technical_indicators(stock_data)
        
        # 4. Aggregate all data
        aggregated_data = self.financial_aggregator.aggregate_company_data(symbol)
        
        # Assertions
        self.assertIsInstance(stock_data, pd.DataFrame)
        self.assertIsInstance(financial_statements, dict)
        self.assertIsInstance(cleaned_income, pd.DataFrame)
        self.assertIsInstance(ratios, dict)
        self.assertIsInstance(technical_indicators, dict)
        self.assertIsInstance(aggregated_data, dict)
        
        # Check data integrity
        self.assertGreater(len(stock_data), 0)
        self.assertIn('income_statement', financial_statements)
        self.assertIn('profitability', ratios)
        self.assertIn('sma_20', technical_indicators)
        self.assertIn('symbol', aggregated_data)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
