"""
Unit tests for financial_metrics.py safe accessor functionality
"""
import unittest
import unittest.mock
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.financial_metrics import safe_financial_lookup, FinancialAnalyzer


class TestSafeFinancialLookup(unittest.TestCase):
    """Test cases for the safe_financial_lookup function"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample financial statement data
        self.sample_income_stmt = pd.DataFrame({
            '2023': [1000000, 500000, 300000, 200000],
            '2022': [900000, 450000, 270000, 180000]
        }, index=['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income'])
        
        self.sample_balance_sheet = pd.DataFrame({
            '2023': [2000000, 1000000, 500000, 1500000, 800000],
            '2022': [1800000, 900000, 450000, 1350000, 720000]
        }, index=['Total Assets', 'Total Current Assets', 'Cash', 'Total Stockholder Equity', 'Total Current Liabilities'])
        
        self.empty_df = pd.DataFrame()
        self.none_df = None
        
    def test_successful_direct_lookup(self):
        """Test normal successful lookups still work"""
        result = safe_financial_lookup(self.sample_income_stmt, 'Total Revenue')
        self.assertEqual(result, 1000000.0)
        
        result = safe_financial_lookup(self.sample_balance_sheet, 'Total Assets')
        self.assertEqual(result, 2000000.0)
    
    def test_missing_rows_return_nan(self):
        """Test missing rows return np.nan"""
        result = safe_financial_lookup(self.sample_income_stmt, 'NonExistentMetric')
        self.assertTrue(np.isnan(result))
        
        result = safe_financial_lookup(self.sample_balance_sheet, 'MissingItem')
        self.assertTrue(np.isnan(result))
    
    def test_case_sensitivity_handling(self):
        """Test case sensitivity handling"""
        # Test exact match
        result = safe_financial_lookup(self.sample_income_stmt, 'Total Revenue')
        self.assertEqual(result, 1000000.0)
        
        # Test case-insensitive match
        result = safe_financial_lookup(self.sample_income_stmt, 'total revenue')
        self.assertEqual(result, 1000000.0)
        
        result = safe_financial_lookup(self.sample_income_stmt, 'TOTAL REVENUE')
        self.assertEqual(result, 1000000.0)
    
    def test_partial_matches_for_label_variations(self):
        """Test partial matches for label variations"""
        # Create DataFrame with variations
        variations_df = pd.DataFrame({
            '2023': [1000000, 500000, 300000]
        }, index=['Revenue', 'Gross Income', 'Operating Profit'])
        
        # Test exact match
        result = safe_financial_lookup(variations_df, 'Revenue')
        self.assertEqual(result, 1000000.0)
        
        # Test variation match
        result = safe_financial_lookup(variations_df, 'Gross Profit')
        self.assertEqual(result, 500000.0)  # Should match 'Gross Income'
        
        result = safe_financial_lookup(variations_df, 'Operating Income')
        self.assertEqual(result, 300000.0)  # Should match 'Operating Profit'
    
    def test_column_index_parameter(self):
        """Test column_index parameter works correctly"""
        result = safe_financial_lookup(self.sample_income_stmt, 'Total Revenue', 0)
        self.assertEqual(result, 1000000.0)
        
        result = safe_financial_lookup(self.sample_income_stmt, 'Total Revenue', 1)
        self.assertEqual(result, 900000.0)
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrame"""
        result = safe_financial_lookup(self.empty_df, 'Total Revenue')
        self.assertTrue(np.isnan(result))
    
    def test_none_dataframe_handling(self):
        """Test handling of None DataFrame"""
        result = safe_financial_lookup(self.none_df, 'Total Revenue')
        self.assertTrue(np.isnan(result))
    
    def test_index_error_handling(self):
        """Test handling of IndexError when column doesn't exist"""
        result = safe_financial_lookup(self.sample_income_stmt, 'Total Revenue', 10)
        self.assertTrue(np.isnan(result))
    
    def test_value_error_handling(self):
        """Test handling of ValueError when data can't be converted to float"""
        # Create DataFrame with non-numeric data
        bad_df = pd.DataFrame({
            '2023': ['Not a number', 500000, 300000]
        }, index=['Total Revenue', 'Gross Profit', 'Net Income'])
        
        result = safe_financial_lookup(bad_df, 'Total Revenue')
        self.assertTrue(np.isnan(result))
    
    def test_common_label_variations(self):
        """Test common label variations mapping"""
        # Test Total Revenue variations
        revenue_variations = pd.DataFrame({
            '2023': [1000000, 1000000, 1000000]
        }, index=['Revenue', 'Sales', 'Net Sales'])
        
        result = safe_financial_lookup(revenue_variations, 'Total Revenue')
        self.assertEqual(result, 1000000.0)
        
        # Test Net Income variations
        income_variations = pd.DataFrame({
            '2023': [200000, 200000, 200000]
        }, index=['Net Earnings', 'Profit After Tax', 'Net Profit'])
        
        result = safe_financial_lookup(income_variations, 'Net Income')
        self.assertEqual(result, 200000.0)
        
        # Test Total Assets variations
        assets_variations = pd.DataFrame({
            '2023': [2000000, 2000000]
        }, index=['Assets', 'Total Asset'])
        
        result = safe_financial_lookup(assets_variations, 'Total Assets')
        self.assertEqual(result, 2000000.0)


class TestFinancialAnalyzerWithSafeLookup(unittest.TestCase):
    """Test cases for FinancialAnalyzer with safe lookup functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.analyzer = FinancialAnalyzer()
        
        # Create sample financial data
        self.sample_income_stmt = pd.DataFrame({
            '2023': [1000000, 500000, 300000, 200000],
            '2022': [900000, 450000, 270000, 180000]
        }, index=['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income'])
        
        self.sample_balance_sheet = pd.DataFrame({
            '2023': [2000000, 1000000, 500000, 1500000, 800000],
            '2022': [1800000, 900000, 450000, 1350000, 720000]
        }, index=['Total Assets', 'Total Current Assets', 'Cash', 'Total Stockholder Equity', 'Total Current Liabilities'])
    
    def test_profitability_ratios_with_missing_data(self):
        """Test profitability ratios calculation with missing data"""
        # Create DataFrame with missing items
        incomplete_income = pd.DataFrame({
            '2023': [1000000, 200000]  # Missing Gross Profit and Operating Income
        }, index=['Total Revenue', 'Net Income'])
        
        incomplete_balance = pd.DataFrame({
            '2023': [2000000, 1500000]  # Missing Total Current Liabilities
        }, index=['Total Assets', 'Total Stockholder Equity'])
        
        # Mock the yfinance ticker to return our test data
        with unittest.mock.patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.income_stmt = incomplete_income
            mock_ticker.return_value.balance_sheet = incomplete_balance
            mock_ticker.return_value.info = {}
            
            result = self.analyzer.calculate_profitability_ratios('TEST')
            
            # Should not raise KeyError and should handle missing data gracefully
            self.assertIsInstance(result, dict)
            # Some ratios should be np.nan due to missing data
            self.assertTrue(any(np.isnan(v) for v in result.values()))
    
    def test_liquidity_ratios_with_missing_data(self):
        """Test liquidity ratios calculation with missing data"""
        # Create DataFrame with missing items
        incomplete_balance = pd.DataFrame({
            '2023': [1000000, 800000]  # Missing Cash and Inventory
        }, index=['Total Current Assets', 'Total Current Liabilities'])
        
        with unittest.mock.patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.balance_sheet = incomplete_balance
            mock_ticker.return_value.info = {}
            
            result = self.analyzer.calculate_liquidity_ratios('TEST')
            
            self.assertIsInstance(result, dict)
            # Should handle missing Cash and Inventory gracefully
            self.assertTrue(any(np.isnan(v) for v in result.values()))
    
    def test_efficiency_ratios_with_missing_data(self):
        """Test efficiency ratios calculation with missing data"""
        # Create DataFrame with missing items
        incomplete_income = pd.DataFrame({
            '2023': [1000000]  # Only Total Revenue
        }, index=['Total Revenue'])
        
        incomplete_balance = pd.DataFrame({
            '2023': [2000000]  # Only Total Assets
        }, index=['Total Assets'])
        
        with unittest.mock.patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.income_stmt = incomplete_income
            mock_ticker.return_value.balance_sheet = incomplete_balance
            mock_ticker.return_value.info = {}
            
            result = self.analyzer.calculate_efficiency_ratios('TEST')
            
            self.assertIsInstance(result, dict)
            # Should handle missing inventory, receivables, payables gracefully
            self.assertTrue(any(np.isnan(v) for v in result.values()))
    
    def test_growth_metrics_with_missing_data(self):
        """Test growth metrics calculation with missing data"""
        # Create DataFrame with only one year of data
        single_year_income = pd.DataFrame({
            '2023': [1000000, 200000]
        }, index=['Total Revenue', 'Net Income'])
        
        with unittest.mock.patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.income_stmt = single_year_income
            mock_ticker.return_value.balance_sheet = pd.DataFrame()
            mock_ticker.return_value.info = {'revenueGrowth': 0.1}
            
            result = self.analyzer.calculate_growth_metrics('TEST')
            
            self.assertIsInstance(result, dict)
            # Should handle missing historical data gracefully
            self.assertTrue(any(np.isnan(v) for v in result.values()))


if __name__ == '__main__':
    unittest.main()
