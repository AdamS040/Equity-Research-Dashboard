"""
Unit tests for chart error handling and data validation
Tests charts with missing data, invalid inputs, and edge cases
"""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import the charts module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualizations.charts import ChartGenerator, validate_chart_data, validate_dataframe, safe_calculate_returns, create_empty_chart_with_message


class TestChartErrorHandling(unittest.TestCase):
    """Test chart error handling and data validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.chart_generator = ChartGenerator()

        # Create sample valid data
        self.valid_data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [105, 106, 107, 108, 109],
            'Low': [95, 96, 97, 98, 99],
            'Close': [102, 103, 104, 105, 106],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range('2023-01-01', periods=5))

        # Create sample returns data
        self.valid_returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])

    def test_validate_chart_data_with_valid_data(self):
        """Test validate_chart_data with valid data"""
        required_keys = ['Open', 'High', 'Low', 'Close']
        missing_keys = validate_chart_data(self.valid_data, required_keys)
        self.assertEqual(missing_keys, [])

    def test_validate_chart_data_with_missing_keys(self):
        """Test validate_chart_data with missing keys"""
        required_keys = ['Open', 'High', 'Low', 'Close', 'MissingKey']
        missing_keys = validate_chart_data(self.valid_data, required_keys)
        self.assertEqual(missing_keys, ['MissingKey'])

    def test_validate_chart_data_with_none_values(self):
        """Test validate_chart_data with None values"""
        data_with_none = self.valid_data.copy()
        data_with_none['Open'] = None
        required_keys = ['Open', 'High', 'Low', 'Close']
        missing_keys = validate_chart_data(data_with_none, required_keys)
        self.assertEqual(missing_keys, ['Open'])

    def test_validate_dataframe_with_valid_data(self):
        """Test validate_dataframe with valid data"""
        self.assertTrue(validate_dataframe(self.valid_data, 1))
        self.assertTrue(validate_dataframe(self.valid_data, 5))
        self.assertFalse(validate_dataframe(self.valid_data, 10))

    def test_validate_dataframe_with_empty_data(self):
        """Test validate_dataframe with empty data"""
        empty_df = pd.DataFrame()
        self.assertFalse(validate_dataframe(empty_df))
        self.assertFalse(validate_dataframe(None))

    def test_safe_calculate_returns_with_valid_data(self):
        """Test safe_calculate_returns with valid data"""
        returns = safe_calculate_returns(self.valid_data)
        self.assertIsNotNone(returns)
        self.assertEqual(len(returns), 4)  # 5 data points - 1 for pct_change

    def test_safe_calculate_returns_with_missing_close(self):
        """Test safe_calculate_returns with missing Close column"""
        data_no_close = self.valid_data.drop('Close', axis=1)
        returns = safe_calculate_returns(data_no_close)
        self.assertIsNone(returns)

    def test_safe_calculate_returns_with_insufficient_data(self):
        """Test safe_calculate_returns with insufficient data"""
        insufficient_data = pd.DataFrame({'Close': [100]})  # Only 1 data point
        returns = safe_calculate_returns(insufficient_data)
        self.assertIsNone(returns)

    def test_create_empty_chart_with_message(self):
        """Test create_empty_chart_with_message"""
        fig = create_empty_chart_with_message("Test message", "Test title")
        self.assertIsNotNone(fig)
        # Check that the annotation contains the message
        annotations = fig.layout.annotations
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0].text, "Test message")

    @patch('visualizations.charts.yf.Ticker')
    def test_create_price_chart_with_invalid_symbol(self, mock_ticker):
        """Test create_price_chart with invalid symbol"""
        fig = self.chart_generator.create_price_chart("", "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_price_chart_with_empty_data(self, mock_ticker):
        """Test create_price_chart with empty data"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_price_chart("AAPL", "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_price_chart_with_missing_columns(self, mock_ticker):
        """Test create_price_chart with missing columns"""
        incomplete_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'Close': [102, 103, 104]
            # Missing High, Low
        })

        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = incomplete_data
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_price_chart("AAPL", "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_price_chart_with_insufficient_data(self, mock_ticker):
        """Test create_price_chart with insufficient data"""
        insufficient_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [105, 106],
            'Low': [95, 96],
            'Close': [102, 103],
            'Volume': [1000, 1100]
        })  # Only 2 data points, need at least 20

        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = insufficient_data
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_price_chart("AAPL", "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_technical_indicators_chart_with_insufficient_data(self, mock_ticker):
        """Test create_technical_indicators_chart with insufficient data"""
        insufficient_data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]
        })  # Only 5 data points, need at least 30

        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = insufficient_data
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_technical_indicators_chart("AAPL", "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_returns_distribution_chart_with_insufficient_data(self, mock_ticker):
        """Test create_returns_distribution_chart with insufficient data"""
        insufficient_data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]
        })  # Only 5 data points, need at least 30

        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = insufficient_data
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_returns_distribution_chart("AAPL", "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_correlation_heatmap_with_insufficient_symbols(self, mock_ticker):
        """Test create_correlation_heatmap with insufficient symbols"""
        fig = self.chart_generator.create_correlation_heatmap(["AAPL"], "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_correlation_heatmap_with_empty_data(self, mock_ticker):
        """Test create_correlation_heatmap with empty data"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_correlation_heatmap(["AAPL", "MSFT"], "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_portfolio_performance_chart_with_mismatched_weights(self, mock_ticker):
        """Test create_portfolio_performance_chart with mismatched weights"""
        fig = self.chart_generator.create_portfolio_performance_chart(
            ["AAPL", "MSFT"], [0.5], "1y"
        )
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_risk_return_scatter_with_insufficient_symbols(self, mock_ticker):
        """Test create_risk_return_scatter with insufficient symbols"""
        fig = self.chart_generator.create_risk_return_scatter(["AAPL"], "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_sector_performance_chart_with_empty_data(self, mock_ticker):
        """Test create_sector_performance_chart with empty data"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance

        sector_etfs = {"Technology": "XLK", "Healthcare": "XLV"}
        fig = self.chart_generator.create_sector_performance_chart(sector_etfs, "1y")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_earnings_chart_with_empty_data(self, mock_ticker):
        """Test create_earnings_chart with empty data"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.income_stmt = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_earnings_chart("AAPL")
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    @patch('visualizations.charts.yf.Ticker')
    def test_create_valuation_comparison_chart_with_empty_data(self, mock_ticker):
        """Test create_valuation_comparison_chart with empty data"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = {}
        mock_ticker.return_value = mock_ticker_instance

        fig = self.chart_generator.create_valuation_comparison_chart("AAPL", ["MSFT", "GOOGL"])
        self.assertIsNotNone(fig)
        # Should return empty chart with message

    def test_chart_functions_with_none_inputs(self):
        """Test chart functions with None inputs"""
        # Test with None symbol
        fig1 = self.chart_generator.create_price_chart(None, "1y")
        self.assertIsNotNone(fig1)

        # Test with None symbols list
        fig2 = self.chart_generator.create_correlation_heatmap(None, "1y")
        self.assertIsNotNone(fig2)

        # Test with None weights
        fig3 = self.chart_generator.create_portfolio_performance_chart(["AAPL"], None, "1y")
        self.assertIsNotNone(fig3)

    def test_chart_functions_with_empty_lists(self):
        """Test chart functions with empty lists"""
        # Test with empty symbols list
        fig1 = self.chart_generator.create_correlation_heatmap([], "1y")
        self.assertIsNotNone(fig1)

        # Test with empty weights list
        fig2 = self.chart_generator.create_portfolio_performance_chart([], [], "1y")
        self.assertIsNotNone(fig2)

        # Test with empty sector_etfs
        fig3 = self.chart_generator.create_sector_performance_chart({}, "1y")
        self.assertIsNotNone(fig3)

    @patch('visualizations.charts.yf.Ticker')
    def test_chart_functions_with_exception_handling(self, mock_ticker):
        """Test chart functions handle exceptions gracefully"""
        # Mock ticker to raise exception
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = Exception("API Error")
        mock_ticker.return_value = mock_ticker_instance

        # All chart functions should handle exceptions and return valid figures
        fig1 = self.chart_generator.create_price_chart("AAPL", "1y")
        self.assertIsNotNone(fig1)

        fig2 = self.chart_generator.create_technical_indicators_chart("AAPL", "1y")
        self.assertIsNotNone(fig2)

        fig3 = self.chart_generator.create_returns_distribution_chart("AAPL", "1y")
        self.assertIsNotNone(fig3)

    def test_graceful_degradation_with_partial_data(self):
        """Test that charts degrade gracefully with partial data"""
        # Test price chart with some missing columns
        partial_data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'Close': [102, 103, 104, 105, 106]
            # Missing High, Low, Volume
        })

        with patch('visualizations.charts.yf.Ticker') as mock_ticker:
            mock_ticker_instance = Mock()
            mock_ticker_instance.history.return_value = partial_data
            mock_ticker.return_value = mock_ticker_instance

            fig = self.chart_generator.create_price_chart("AAPL", "1y")
            self.assertIsNotNone(fig)
            # Should return empty chart with message about missing data


if __name__ == '__main__':
    unittest.main()
