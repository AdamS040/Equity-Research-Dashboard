"""
Test suite for models modules
Tests comparable analysis, Monte Carlo simulations, and valuation models
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
from models.comparable_analysis import ComparableAnalysis
from models.monte_carlo import MonteCarloSimulator, MonteCarloAnalyzer
from models.dcf_model import DCFModel


class TestComparableAnalysis(unittest.TestCase):
    """Test ComparableAnalysis class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ComparableAnalysis()
        
        # Mock peer companies data
        self.mock_peer_data = {
            'AAPL': {
                'info': {
                    'longName': 'Apple Inc.',
                    'sector': 'Technology',
                    'industry': 'Consumer Electronics',
                    'marketCap': 2000000000000,
                    'trailingPE': 25.5,
                    'forwardPE': 24.0,
                    'priceToBook': 15.2,
                    'priceToSalesTrailing12Months': 5.8,
                    'enterpriseToRevenue': 6.2,
                    'enterpriseToEbitda': 18.5,
                    'debtToEquity': 0.8,
                    'returnOnEquity': 0.15,
                    'returnOnAssets': 0.10,
                    'profitMargins': 0.25,
                    'operatingMargins': 0.30
                }
            },
            'MSFT': {
                'info': {
                    'longName': 'Microsoft Corporation',
                    'sector': 'Technology',
                    'industry': 'Software',
                    'marketCap': 1800000000000,
                    'trailingPE': 30.0,
                    'forwardPE': 28.5,
                    'priceToBook': 12.0,
                    'priceToSalesTrailing12Months': 8.5,
                    'enterpriseToRevenue': 9.0,
                    'enterpriseToEbitda': 22.0,
                    'debtToEquity': 0.6,
                    'returnOnEquity': 0.20,
                    'returnOnAssets': 0.12,
                    'profitMargins': 0.30,
                    'operatingMargins': 0.35
                }
            },
            'GOOGL': {
                'info': {
                    'longName': 'Alphabet Inc.',
                    'sector': 'Technology',
                    'industry': 'Internet Content & Information',
                    'marketCap': 1600000000000,
                    'trailingPE': 28.0,
                    'forwardPE': 26.5,
                    'priceToBook': 6.8,
                    'priceToSalesTrailing12Months': 6.2,
                    'enterpriseToRevenue': 6.8,
                    'enterpriseToEbitda': 16.5,
                    'debtToEquity': 0.4,
                    'returnOnEquity': 0.18,
                    'returnOnAssets': 0.11,
                    'profitMargins': 0.22,
                    'operatingMargins': 0.28
                }
            }
        }
    
    @patch('yfinance.Ticker')
    def test_get_peer_companies(self, mock_ticker):
        """Test getting peer companies"""
        # Mock target company info
        mock_stock = Mock()
        mock_stock.info = {
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }
        mock_ticker.return_value = mock_stock
        
        peers = self.analyzer.get_peer_companies('AAPL')
        
        self.assertIsInstance(peers, list)
        self.assertGreater(len(peers), 0)
        # All peers should be valid stock symbols
        for peer in peers:
            self.assertTrue(len(peer) <= 5)
            self.assertTrue(peer.isalpha())
    
    @patch('yfinance.Ticker')
    def test_calculate_valuation_metrics(self, mock_ticker):
        """Test valuation metrics calculation"""
        # Mock stock data
        mock_stock = Mock()
        mock_stock.info = {
            'trailingPE': 25.5,
            'forwardPE': 24.0,
            'priceToBook': 15.2,
            'priceToSalesTrailing12Months': 5.8,
            'enterpriseToRevenue': 6.2,
            'enterpriseToEbitda': 18.5,
            'debtToEquity': 0.8,
            'returnOnEquity': 0.15,
            'returnOnAssets': 0.10,
            'profitMargins': 0.25,
            'operatingMargins': 0.30,
            'marketCap': 2000000000000,
            'totalRevenue': 1000000000000,
            'ebitda': 500000000000
        }
        mock_ticker.return_value = mock_stock
        
        metrics = self.analyzer.calculate_valuation_metrics('AAPL')
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('pe_ratio', metrics)
        self.assertIn('pb_ratio', metrics)
        self.assertIn('ps_ratio', metrics)
        self.assertIn('ev_revenue', metrics)
        self.assertIn('ev_ebitda', metrics)
        self.assertIn('roe', metrics)
        self.assertIn('roa', metrics)
        self.assertIn('debt_to_equity', metrics)
        self.assertIn('profit_margin', metrics)
        self.assertIn('operating_margin', metrics)
    
    @patch('yfinance.Ticker')
    def test_get_peer_comparison(self, mock_ticker):
        """Test peer comparison"""
        # Mock multiple stocks
        def mock_ticker_side_effect(symbol):
            mock_stock = Mock()
            if symbol in self.mock_peer_data:
                mock_stock.info = self.mock_peer_data[symbol]['info']
            else:
                mock_stock.info = {}
            return mock_stock
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        comparison = self.analyzer.get_peer_comparison('AAPL', ['MSFT', 'GOOGL'])
        
        self.assertIsInstance(comparison, pd.DataFrame)
        self.assertIn('AAPL', comparison.columns)
        self.assertIn('MSFT', comparison.columns)
        self.assertIn('GOOGL', comparison.columns)
        self.assertIn('Average', comparison.columns)
        self.assertIn('Median', comparison.columns)
    
    @patch('yfinance.Ticker')
    def test_calculate_relative_valuation(self, mock_ticker):
        """Test relative valuation calculation"""
        # Mock target and peer data
        def mock_ticker_side_effect(symbol):
            mock_stock = Mock()
            if symbol in self.mock_peer_data:
                mock_stock.info = self.mock_peer_data[symbol]['info']
            else:
                mock_stock.info = {}
            return mock_stock
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        relative_valuation = self.analyzer.calculate_relative_valuation('AAPL', ['MSFT', 'GOOGL'])
        
        self.assertIsInstance(relative_valuation, dict)
        self.assertIn('pe_ratio_comparison', relative_valuation)
        self.assertIn('pb_ratio_comparison', relative_valuation)
        self.assertIn('ps_ratio_comparison', relative_valuation)
        self.assertIn('ev_ebitda_comparison', relative_valuation)
        self.assertIn('valuation_score', relative_valuation)
    
    @patch('yfinance.Ticker')
    def test_calculate_implied_value(self, mock_ticker):
        """Test implied value calculation"""
        # Mock target and peer data
        def mock_ticker_side_effect(symbol):
            mock_stock = Mock()
            if symbol in self.mock_peer_data:
                mock_stock.info = self.mock_peer_data[symbol]['info']
            else:
                mock_stock.info = {}
            return mock_stock
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        implied_values = self.analyzer.calculate_implied_value('AAPL', ['MSFT', 'GOOGL'])
        
        self.assertIsInstance(implied_values, dict)
        self.assertIn('pe_implied_value', implied_values)
        self.assertIn('pb_implied_value', implied_values)
        self.assertIn('ps_implied_value', implied_values)
        self.assertIn('ev_ebitda_implied_value', implied_values)
        self.assertIn('average_implied_value', implied_values)
    
    @patch('yfinance.Ticker')
    def test_get_sector_analysis(self, mock_ticker):
        """Test sector analysis"""
        # Mock sector data
        def mock_ticker_side_effect(symbol):
            mock_stock = Mock()
            if symbol in self.mock_peer_data:
                mock_stock.info = self.mock_peer_data[symbol]['info']
            else:
                mock_stock.info = {}
            return mock_stock
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        sector_analysis = self.analyzer.get_sector_analysis('Technology')
        
        self.assertIsInstance(sector_analysis, dict)
        self.assertIn('sector_metrics', sector_analysis)
        self.assertIn('sector_rankings', sector_analysis)
        self.assertIn('sector_trends', sector_analysis)
    
    @patch('yfinance.Ticker')
    def test_generate_comparable_report(self, mock_ticker):
        """Test comparable analysis report generation"""
        # Mock comprehensive data
        def mock_ticker_side_effect(symbol):
            mock_stock = Mock()
            if symbol in self.mock_peer_data:
                mock_stock.info = self.mock_peer_data[symbol]['info']
            else:
                mock_stock.info = {}
            return mock_stock
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        report = self.analyzer.generate_comparable_report('AAPL', ['MSFT', 'GOOGL'])
        
        self.assertIsInstance(report, dict)
        self.assertIn('target_company', report)
        self.assertIn('peer_companies', report)
        self.assertIn('valuation_comparison', report)
        self.assertIn('relative_valuation', report)
        self.assertIn('implied_values', report)
        self.assertIn('sector_analysis', report)
        self.assertIn('recommendations', report)


class TestMonteCarloSimulator(unittest.TestCase):
    """Test MonteCarloSimulator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.simulator = MonteCarloSimulator()
    
    def test_simulate_stock_price(self):
        """Test stock price simulation"""
        current_price = 100.0
        expected_return = 0.10  # 10% annual return
        volatility = 0.20  # 20% annual volatility
        time_horizon = 252  # 1 year in trading days
        num_simulations = 1000
        
        result = self.simulator.simulate_stock_price(
            current_price, expected_return, volatility, time_horizon, num_simulations
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('simulated_prices', result)
        self.assertIn('final_prices', result)
        self.assertIn('price_paths', result)
        self.assertIn('statistics', result)
        
        # Check data types and shapes
        self.assertIsInstance(result['simulated_prices'], np.ndarray)
        self.assertEqual(result['simulated_prices'].shape, (num_simulations, time_horizon + 1))
        self.assertIsInstance(result['final_prices'], np.ndarray)
        self.assertEqual(len(result['final_prices']), num_simulations)
        
        # Check statistics
        stats = result['statistics']
        self.assertIn('mean_final_price', stats)
        self.assertIn('median_final_price', stats)
        self.assertIn('std_final_price', stats)
        self.assertIn('min_final_price', stats)
        self.assertIn('max_final_price', stats)
        self.assertIn('percentiles', stats)
    
    def test_simulate_portfolio_returns(self):
        """Test portfolio returns simulation"""
        weights = [0.4, 0.3, 0.3]  # 3-asset portfolio
        returns_data = pd.DataFrame({
            'Asset1': np.random.normal(0.001, 0.02, 252),
            'Asset2': np.random.normal(0.001, 0.025, 252),
            'Asset3': np.random.normal(0.001, 0.03, 252)
        })
        time_horizon = 252
        num_simulations = 1000
        
        result = self.simulator.simulate_portfolio_returns(
            weights, returns_data, time_horizon, num_simulations
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('portfolio_returns', result)
        self.assertIn('cumulative_returns', result)
        self.assertIn('final_values', result)
        self.assertIn('statistics', result)
        
        # Check data types and shapes
        self.assertIsInstance(result['portfolio_returns'], np.ndarray)
        self.assertEqual(result['portfolio_returns'].shape, (num_simulations, time_horizon))
        self.assertIsInstance(result['final_values'], np.ndarray)
        self.assertEqual(len(result['final_values']), num_simulations)
    
    def test_simulate_option_pricing(self):
        """Test option pricing simulation"""
        current_price = 100.0
        strike_price = 100.0
        time_to_expiry = 1.0  # 1 year
        risk_free_rate = 0.02  # 2%
        volatility = 0.20  # 20%
        num_simulations = 10000
        
        # Test call option
        call_result = self.simulator.simulate_option_pricing(
            current_price, strike_price, time_to_expiry, risk_free_rate, 
            volatility, 'call', num_simulations
        )
        
        self.assertIsInstance(call_result, dict)
        self.assertIn('option_price', call_result)
        self.assertIn('payoffs', call_result)
        self.assertIn('statistics', call_result)
        self.assertGreater(call_result['option_price'], 0)
        
        # Test put option
        put_result = self.simulator.simulate_option_pricing(
            current_price, strike_price, time_to_expiry, risk_free_rate, 
            volatility, 'put', num_simulations
        )
        
        self.assertIsInstance(put_result, dict)
        self.assertIn('option_price', put_result)
        self.assertIn('payoffs', put_result)
        self.assertIn('statistics', put_result)
        self.assertGreater(put_result['option_price'], 0)
    
    def test_simulate_risk_analysis(self):
        """Test risk analysis simulation"""
        returns = np.random.normal(0.001, 0.02, 1000)
        confidence_level = 0.05
        num_simulations = 10000
        
        result = self.simulator.simulate_risk_analysis(
            returns, confidence_level, num_simulations
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('var', result)
        self.assertIn('cvar', result)
        self.assertIn('max_drawdown', result)
        self.assertIn('simulated_returns', result)
        self.assertIn('statistics', result)
        
        # Check that VaR is negative (loss)
        self.assertLess(result['var'], 0)
        # Check that CVaR is less than VaR (more extreme)
        self.assertLess(result['cvar'], result['var'])
    
    def test_simulate_stress_test(self):
        """Test stress testing simulation"""
        portfolio_value = 1000000
        asset_weights = [0.4, 0.3, 0.3]
        base_returns = [0.08, 0.10, 0.12]  # Annual returns
        base_volatilities = [0.15, 0.20, 0.25]  # Annual volatilities
        
        result = self.simulator.simulate_stress_test(
            portfolio_value, asset_weights, base_returns, base_volatilities
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('market_crash', result)
        self.assertIn('interest_rate_shock', result)
        self.assertIn('volatility_spike', result)
        self.assertIn('correlation_breakdown', result)
        
        # Check that stress scenarios show losses
        for scenario in result.values():
            self.assertIn('portfolio_value', scenario)
            self.assertIn('return', scenario)
            self.assertIn('var', scenario)
            self.assertLess(scenario['return'], 0)  # Stress scenarios should show losses


class TestMonteCarloAnalyzer(unittest.TestCase):
    """Test MonteCarloAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = MonteCarloAnalyzer()
    
    def test_analyze_simulation_results(self):
        """Test simulation results analysis"""
        # Create mock simulation results
        simulated_prices = np.random.normal(110, 10, 1000)  # Final prices
        price_paths = np.random.normal(100, 5, (1000, 252))  # Price paths
        
        result = self.analyzer.analyze_simulation_results(simulated_prices, price_paths)
        
        self.assertIsInstance(result, dict)
        self.assertIn('summary_statistics', result)
        self.assertIn('risk_metrics', result)
        self.assertIn('probability_analysis', result)
        self.assertIn('percentile_analysis', result)
        
        # Check summary statistics
        summary = result['summary_statistics']
        self.assertIn('mean', summary)
        self.assertIn('median', summary)
        self.assertIn('std', summary)
        self.assertIn('min', summary)
        self.assertIn('max', summary)
        
        # Check risk metrics
        risk = result['risk_metrics']
        self.assertIn('var_95', risk)
        self.assertIn('var_99', risk)
        self.assertIn('cvar_95', risk)
        self.assertIn('cvar_99', risk)
    
    def test_calculate_probability_metrics(self):
        """Test probability metrics calculation"""
        final_values = np.random.normal(110, 10, 10000)
        target_value = 100
        
        result = self.analyzer.calculate_probability_metrics(final_values, target_value)
        
        self.assertIsInstance(result, dict)
        self.assertIn('probability_above_target', result)
        self.assertIn('probability_below_target', result)
        self.assertIn('expected_shortfall', result)
        self.assertIn('expected_excess', result)
        
        # Check probability bounds
        self.assertGreaterEqual(result['probability_above_target'], 0)
        self.assertLessEqual(result['probability_above_target'], 1)
        self.assertGreaterEqual(result['probability_below_target'], 0)
        self.assertLessEqual(result['probability_below_target'], 1)
    
    def test_generate_scenario_analysis(self):
        """Test scenario analysis generation"""
        simulated_prices = np.random.normal(110, 10, 10000)
        
        result = self.analyzer.generate_scenario_analysis(simulated_prices)
        
        self.assertIsInstance(result, dict)
        self.assertIn('bull_scenario', result)
        self.assertIn('bear_scenario', result)
        self.assertIn('base_scenario', result)
        self.assertIn('scenario_probabilities', result)
        
        # Check scenario values
        self.assertGreater(result['bull_scenario']['value'], result['base_scenario']['value'])
        self.assertLess(result['bear_scenario']['value'], result['base_scenario']['value'])
    
    def test_calculate_confidence_intervals(self):
        """Test confidence interval calculation"""
        simulated_values = np.random.normal(110, 10, 10000)
        confidence_levels = [0.90, 0.95, 0.99]
        
        result = self.analyzer.calculate_confidence_intervals(simulated_values, confidence_levels)
        
        self.assertIsInstance(result, dict)
        for level in confidence_levels:
            level_str = f'{int(level*100)}%'
            self.assertIn(level_str, result)
            self.assertIn('lower', result[level_str])
            self.assertIn('upper', result[level_str])
            self.assertLess(result[level_str]['lower'], result[level_str]['upper'])


class TestDCFModel(unittest.TestCase):
    """Test DCFModel class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dcf_model = DCFModel()
    
    @patch('yfinance.Ticker')
    def test_calculate_wacc(self, mock_ticker):
        """Test WACC calculation"""
        # Mock stock data
        mock_stock = Mock()
        mock_stock.info = {
            'beta': 1.2,
            'marketCap': 1000000000,
            'totalDebt': 200000000,
            'cash': 50000000
        }
        mock_ticker.return_value = mock_stock
        
        wacc = self.dcf_model.calculate_wacc('AAPL')
        
        self.assertIsInstance(wacc, float)
        self.assertGreater(wacc, 0)
        self.assertLess(wacc, 1)
    
    @patch('yfinance.Ticker')
    def test_project_cash_flows(self, mock_ticker):
        """Test cash flow projection"""
        # Mock financial data
        mock_stock = Mock()
        mock_stock.financials = pd.DataFrame({
            'Free Cash Flow': [100000000, 90000000, 80000000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        mock_ticker.return_value = mock_stock
        
        cash_flows = self.dcf_model.project_cash_flows('AAPL')
        
        self.assertIsInstance(cash_flows, pd.DataFrame)
        self.assertGreater(len(cash_flows), 0)
        self.assertIn('Year', cash_flows.columns)
        self.assertIn('FCF', cash_flows.columns)
    
    @patch('yfinance.Ticker')
    def test_calculate_dcf_value(self, mock_ticker):
        """Test DCF value calculation"""
        # Mock comprehensive stock data
        mock_stock = Mock()
        mock_stock.info = {
            'beta': 1.2,
            'marketCap': 1000000000,
            'totalDebt': 200000000,
            'cash': 50000000,
            'sharesOutstanding': 100000000
        }
        mock_stock.financials = pd.DataFrame({
            'Free Cash Flow': [100000000, 90000000, 80000000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        mock_ticker.return_value = mock_stock
        
        result = self.dcf_model.calculate_dcf_value('AAPL')
        
        self.assertIn('enterprise_value', result)
        self.assertIn('equity_value', result)
        self.assertIn('value_per_share', result)
        self.assertIn('assumptions', result)
        self.assertIsInstance(result['enterprise_value'], float)
        self.assertIsInstance(result['equity_value'], float)
        self.assertIsInstance(result['value_per_share'], float)
    
    def test_sensitivity_analysis(self):
        """Test DCF sensitivity analysis"""
        result = self.dcf_model.sensitivity_analysis('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
        self.assertIn('Discount Rate', result.columns)
        self.assertIn('Growth Rate', result.columns)
        self.assertIn('Value per Share', result.columns)


class TestIntegration(unittest.TestCase):
    """Integration tests for models"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.comparable_analyzer = ComparableAnalysis()
        self.monte_carlo_simulator = MonteCarloSimulator()
        self.monte_carlo_analyzer = MonteCarloAnalyzer()
        self.dcf_model = DCFModel()
    
    @patch('yfinance.Ticker')
    def test_full_valuation_pipeline(self, mock_ticker):
        """Test full valuation pipeline"""
        # Mock comprehensive data
        def mock_ticker_side_effect(symbol):
            mock_stock = Mock()
            mock_stock.info = {
                'longName': 'Apple Inc.',
                'sector': 'Technology',
                'beta': 1.2,
                'marketCap': 2000000000000,
                'totalDebt': 200000000000,
                'cash': 50000000000,
                'sharesOutstanding': 10000000000,
                'trailingPE': 25.5,
                'priceToBook': 15.2,
                'returnOnEquity': 0.15
            }
            mock_stock.financials = pd.DataFrame({
                'Free Cash Flow': [80000000000, 72000000000, 64000000000]
            }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
            return mock_stock
        
        mock_ticker.side_effect = mock_ticker_side_effect
        
        symbol = 'AAPL'
        peer_symbols = ['MSFT', 'GOOGL']
        
        # 1. Comparable Analysis
        comparable_report = self.comparable_analyzer.generate_comparable_report(symbol, peer_symbols)
        
        # 2. DCF Valuation
        dcf_result = self.dcf_model.calculate_dcf_value(symbol)
        
        # 3. Monte Carlo Simulation
        current_price = 150.0
        expected_return = 0.10
        volatility = 0.20
        simulation_result = self.monte_carlo_simulator.simulate_stock_price(
            current_price, expected_return, volatility, 252, 1000
        )
        
        # 4. Monte Carlo Analysis
        analysis_result = self.monte_carlo_analyzer.analyze_simulation_results(
            simulation_result['final_prices'], simulation_result['price_paths']
        )
        
        # Assertions
        self.assertIsInstance(comparable_report, dict)
        self.assertIsInstance(dcf_result, dict)
        self.assertIsInstance(simulation_result, dict)
        self.assertIsInstance(analysis_result, dict)
        
        # Check key components
        self.assertIn('valuation_comparison', comparable_report)
        self.assertIn('value_per_share', dcf_result)
        self.assertIn('statistics', simulation_result)
        self.assertIn('summary_statistics', analysis_result)
    
    def test_risk_analysis_integration(self):
        """Test risk analysis integration"""
        # Create portfolio simulation
        weights = [0.4, 0.3, 0.3]
        returns_data = pd.DataFrame({
            'Asset1': np.random.normal(0.001, 0.02, 252),
            'Asset2': np.random.normal(0.001, 0.025, 252),
            'Asset3': np.random.normal(0.001, 0.03, 252)
        })
        
        # Portfolio simulation
        portfolio_result = self.monte_carlo_simulator.simulate_portfolio_returns(
            weights, returns_data, 252, 1000
        )
        
        # Risk analysis
        risk_result = self.monte_carlo_simulator.simulate_risk_analysis(
            portfolio_result['portfolio_returns'].flatten(), 0.05, 1000
        )
        
        # Analysis
        analysis_result = self.monte_carlo_analyzer.analyze_simulation_results(
            portfolio_result['final_values'], portfolio_result['portfolio_returns']
        )
        
        # Assertions
        self.assertIsInstance(portfolio_result, dict)
        self.assertIsInstance(risk_result, dict)
        self.assertIsInstance(analysis_result, dict)
        
        # Check risk metrics
        self.assertIn('var', risk_result)
        self.assertIn('cvar', risk_result)
        self.assertIn('max_drawdown', risk_result)
        self.assertLess(risk_result['var'], 0)  # VaR should be negative


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
