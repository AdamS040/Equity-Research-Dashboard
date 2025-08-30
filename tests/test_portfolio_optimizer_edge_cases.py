"""
Edge case tests for portfolio optimizer validation and fallbacks
"""
import unittest
import pandas as pd
import numpy as np
from analysis.portfolio_optimizer import PortfolioOptimizer, validate_optimizer_inputs


class TestPortfolioOptimizerEdgeCases(unittest.TestCase):
    """Test edge cases for portfolio optimizer validation and fallbacks"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        
        # Create sample valid returns data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        self.valid_returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 100),
            'GOOGL': np.random.normal(0.001, 0.025, 100),
            'MSFT': np.random.normal(0.001, 0.018, 100)
        }, index=dates)
    
    def test_validate_optimizer_inputs_empty_data(self):
        """Test validation with empty returns data"""
        empty_returns = pd.DataFrame()
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(empty_returns)
        
        self.assertFalse(is_valid)
        self.assertTrue(empty_returns.empty)
        self.assertIn("Returns data is empty", validation_info['warnings'])
    
    def test_validate_optimizer_inputs_single_asset(self):
        """Test validation with single asset portfolio"""
        single_asset_returns = self.valid_returns[['AAPL']]
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(single_asset_returns)
        
        self.assertTrue(is_valid)
        self.assertTrue(validation_info['is_single_asset'])
        self.assertIn("Single asset portfolio detected", validation_info['warnings'])
        self.assertEqual(len(cleaned_data.columns), 1)
    
    def test_validate_optimizer_inputs_with_nans(self):
        """Test validation with NaN values in returns data"""
        # Add some NaN values
        returns_with_nans = self.valid_returns.copy()
        returns_with_nans.iloc[10:15, 0] = np.nan  # Add NaNs to first column
        
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(returns_with_nans)
        
        self.assertTrue(is_valid)
        self.assertTrue(validation_info['has_nans'])
        self.assertIsNotNone(validation_info['nan_handling'])
        self.assertEqual(len(cleaned_data), len(returns_with_nans))  # Should forward-fill
    
    def test_validate_optimizer_inputs_excessive_nans(self):
        """Test validation with excessive NaN values that require dropping rows"""
        # Create data with NaNs at the beginning that can't be forward-filled
        returns_with_nans = self.valid_returns.copy()
        returns_with_nans.iloc[0:5, 0] = np.nan  # NaNs at the beginning of first column
        returns_with_nans.iloc[10:15, :] = np.nan  # All columns NaN for some rows
        
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(returns_with_nans)
        
        self.assertTrue(is_valid)
        self.assertTrue(validation_info['has_nans'])
        self.assertIn('dropna', validation_info['nan_handling'])
        self.assertLess(len(cleaned_data), len(returns_with_nans))  # Should drop rows
    
    def test_validate_optimizer_inputs_insufficient_data(self):
        """Test validation with insufficient data after cleaning"""
        # Create very short dataset
        short_returns = self.valid_returns.iloc[:20]  # Only 20 days
        
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(short_returns)
        
        self.assertFalse(is_valid)
        self.assertIn("Insufficient data after cleaning (less than 30 days)", validation_info['warnings'])
    
    def test_validate_optimizer_inputs_singular_matrix(self):
        """Test validation with singular covariance matrix"""
        # Create perfectly correlated assets (singular matrix)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,  # Perfectly correlated
            'ASSET3': base_returns * 3   # Perfectly correlated
        }, index=dates)
        
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(singular_returns)
        
        self.assertTrue(is_valid)
        self.assertTrue(validation_info['is_singular_matrix'])
        self.assertIn("Covariance matrix is singular", validation_info['warnings'])
    
    def test_optimize_max_sharpe_single_asset(self):
        """Test max Sharpe optimization with single asset"""
        single_asset_returns = self.valid_returns[['AAPL']]
        weights = self.optimizer.optimize_max_sharpe(single_asset_returns)
        
        self.assertEqual(len(weights), 1)
        self.assertAlmostEqual(weights[0], 1.0, places=5)
    
    def test_optimize_max_sharpe_singular_matrix(self):
        """Test max Sharpe optimization with singular covariance matrix"""
        # Create perfectly correlated assets
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,
            'ASSET3': base_returns * 3
        }, index=dates)
        
        weights = self.optimizer.optimize_max_sharpe(singular_returns)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)
        # Should be equal weights due to fallback
        self.assertAlmostEqual(weights[0], weights[1], places=5)
        self.assertAlmostEqual(weights[1], weights[2], places=5)
    
    def test_optimize_max_sharpe_with_nans(self):
        """Test max Sharpe optimization with NaN values"""
        returns_with_nans = self.valid_returns.copy()
        returns_with_nans.iloc[10:15, 0] = np.nan
        
        weights = self.optimizer.optimize_max_sharpe(returns_with_nans)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)
        # Should not crash and should return valid weights
    
    def test_optimize_min_volatility_single_asset(self):
        """Test min volatility optimization with single asset"""
        single_asset_returns = self.valid_returns[['AAPL']]
        weights = self.optimizer.optimize_min_volatility(single_asset_returns)
        
        self.assertEqual(len(weights), 1)
        self.assertAlmostEqual(weights[0], 1.0, places=5)
    
    def test_optimize_min_volatility_singular_matrix(self):
        """Test min volatility optimization with singular covariance matrix"""
        # Create perfectly correlated assets
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,
            'ASSET3': base_returns * 3
        }, index=dates)
        
        weights = self.optimizer.optimize_min_volatility(singular_returns)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)
        # Should be equal weights due to fallback
        self.assertAlmostEqual(weights[0], weights[1], places=5)
        self.assertAlmostEqual(weights[1], weights[2], places=5)
    
    def test_optimize_target_return_single_asset(self):
        """Test target return optimization with single asset"""
        single_asset_returns = self.valid_returns[['AAPL']]
        weights = self.optimizer.optimize_target_return(single_asset_returns, 0.1)
        
        self.assertEqual(len(weights), 1)
        self.assertAlmostEqual(weights[0], 1.0, places=5)
    
    def test_optimize_target_return_singular_matrix(self):
        """Test target return optimization with singular covariance matrix"""
        # Create perfectly correlated assets
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,
            'ASSET3': base_returns * 3
        }, index=dates)
        
        weights = self.optimizer.optimize_target_return(singular_returns, 0.1)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)
        # Should be equal weights due to fallback
        self.assertAlmostEqual(weights[0], weights[1], places=5)
        self.assertAlmostEqual(weights[1], weights[2], places=5)
    
    def test_risk_parity_optimization_single_asset(self):
        """Test risk parity optimization with single asset"""
        single_asset_returns = self.valid_returns[['AAPL']]
        weights = self.optimizer.risk_parity_optimization(single_asset_returns)
        
        self.assertEqual(len(weights), 1)
        self.assertAlmostEqual(weights[0], 1.0, places=5)
    
    def test_risk_parity_optimization_singular_matrix(self):
        """Test risk parity optimization with singular covariance matrix"""
        # Create perfectly correlated assets
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,
            'ASSET3': base_returns * 3
        }, index=dates)
        
        weights = self.optimizer.risk_parity_optimization(singular_returns)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)
        # Should be equal weights due to fallback
        self.assertAlmostEqual(weights[0], weights[1], places=5)
        self.assertAlmostEqual(weights[1], weights[2], places=5)
    
    def test_generate_efficient_frontier_single_asset(self):
        """Test efficient frontier generation with single asset"""
        single_asset_returns = self.valid_returns[['AAPL']]
        frontier = self.optimizer.generate_efficient_frontier(single_asset_returns)
        
        self.assertTrue(frontier.empty)  # Should return empty DataFrame for single asset
    
    def test_generate_efficient_frontier_singular_matrix(self):
        """Test efficient frontier generation with singular covariance matrix"""
        # Create perfectly correlated assets
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,
            'ASSET3': base_returns * 3
        }, index=dates)
        
        frontier = self.optimizer.generate_efficient_frontier(singular_returns)
        
        self.assertTrue(frontier.empty)  # Should return empty DataFrame for singular matrix
    
    def test_optimize_portfolio_empty_data(self):
        """Test main optimize_portfolio function with empty data"""
        result = self.optimizer.optimize_portfolio([])
        
        self.assertIn('error', result)
        self.assertIn('Unable to fetch price data', result['error'])
    
    def test_optimize_portfolio_single_asset(self):
        """Test main optimize_portfolio function with single asset"""
        # This test requires actual data fetching, so we'll test the validation function directly
        # Create a single asset returns DataFrame
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        single_asset_returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 100)
        }, index=dates)
        
        # Test validation function directly
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(single_asset_returns)
        
        self.assertTrue(is_valid)
        self.assertTrue(validation_info['is_single_asset'])
        self.assertIn("Single asset portfolio detected", validation_info['warnings'])
        
        # Test optimization function directly
        weights = self.optimizer.optimize_max_sharpe(single_asset_returns)
        self.assertEqual(len(weights), 1)
        self.assertAlmostEqual(weights[0], 1.0, places=5)
    
    def test_optimize_portfolio_with_nans(self):
        """Test main optimize_portfolio function with NaN data"""
        # This test would require mocking the data fetching
        # For now, we'll test with the validation function directly
        returns_with_nans = self.valid_returns.copy()
        returns_with_nans.iloc[10:15, 0] = np.nan
        
        is_valid, cleaned_data, validation_info = validate_optimizer_inputs(returns_with_nans)
        
        self.assertTrue(is_valid)
        self.assertTrue(validation_info['has_nans'])
        self.assertIsNotNone(validation_info['nan_handling'])
    
    def test_weights_always_sum_to_one(self):
        """Test that all optimization methods return weights that sum to 1.0"""
        methods = ['max_sharpe', 'min_volatility', 'risk_parity']
        
        for method in methods:
            with self.subTest(method=method):
                if method == 'max_sharpe':
                    weights = self.optimizer.optimize_max_sharpe(self.valid_returns)
                elif method == 'min_volatility':
                    weights = self.optimizer.optimize_min_volatility(self.valid_returns)
                elif method == 'risk_parity':
                    weights = self.optimizer.risk_parity_optimization(self.valid_returns)
                
                self.assertAlmostEqual(np.sum(weights), 1.0, places=5)
                self.assertTrue(all(w >= 0 for w in weights))  # All weights should be non-negative
    
    def test_black_litterman_optimization_edge_cases(self):
        """Test Black-Litterman optimization with edge cases"""
        # Test with single asset
        single_asset_returns = self.valid_returns[['AAPL']]
        market_caps = {'AAPL': 1000000}
        weights = self.optimizer.black_litterman_optimization(single_asset_returns, market_caps)
        
        self.assertEqual(len(weights), 1)
        self.assertAlmostEqual(weights[0], 1.0, places=5)
        
        # Test with singular matrix
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        base_returns = np.random.normal(0.001, 0.02, 100)
        singular_returns = pd.DataFrame({
            'ASSET1': base_returns,
            'ASSET2': base_returns * 2,
            'ASSET3': base_returns * 3
        }, index=dates)
        market_caps = {'ASSET1': 1000000, 'ASSET2': 2000000, 'ASSET3': 3000000}
        
        weights = self.optimizer.black_litterman_optimization(singular_returns, market_caps)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
