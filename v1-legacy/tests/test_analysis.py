"""
Test suite for analysis modules
Tests financial metrics, risk analysis, portfolio optimization, and valuation models
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
from analysis.financial_metrics import FinancialAnalyzer
from analysis.risk_analysis import RiskAnalyzer
from analysis.portfolio_optimizer import PortfolioOptimizer
from analysis.valuation_models import DCFModel, DividendDiscountModel


class TestFinancialAnalyzer(unittest.TestCase):
    """Test FinancialAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = FinancialAnalyzer()
        
        # Mock financial data
        self.mock_income_stmt = pd.DataFrame({
            'Total Revenue': [1000000, 900000, 800000],
            'Net Income': [100000, 90000, 80000],
            'Gross Profit': [400000, 360000, 320000],
            'EBIT': [150000, 135000, 120000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        
        self.mock_balance_sheet = pd.DataFrame({
            'Total Assets': [2000000, 1800000, 1600000],
            'Total Equity': [1200000, 1080000, 960000],
            'Total Current Assets': [800000, 720000, 640000],
            'Total Current Liabilities': [400000, 360000, 320000],
            'Cash and Cash Equivalents': [200000, 180000, 160000],
            'Total Debt': [300000, 270000, 240000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
        
        self.mock_cash_flow = pd.DataFrame({
            'Operating Cash Flow': [120000, 108000, 96000],
            'Free Cash Flow': [100000, 90000, 80000],
            'Capital Expenditure': [-20000, -18000, -16000]
        }, index=['2023-12-31', '2022-12-31', '2021-12-31'])
    
    @patch('yfinance.Ticker')
    def test_get_financial_statements(self, mock_ticker):
        """Test getting financial statements"""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.financials = self.mock_income_stmt
        mock_stock.balance_sheet = self.mock_balance_sheet
        mock_stock.cashflow = self.mock_cash_flow
        mock_ticker.return_value = mock_stock
        
        result = self.analyzer.get_financial_statements('AAPL')
        
        self.assertIn('income_statement', result)
        self.assertIn('balance_sheet', result)
        self.assertIn('cash_flow', result)
        self.assertIsInstance(result['income_statement'], pd.DataFrame)
    
    def test_calculate_profitability_ratios(self):
        """Test profitability ratio calculations"""
        ratios = self.analyzer.calculate_profitability_ratios('AAPL')
        
        # Mock the financial statements call
        with patch.object(self.analyzer, 'get_financial_statements') as mock_get:
            mock_get.return_value = {
                'income_statement': self.mock_income_stmt,
                'balance_sheet': self.mock_balance_sheet,
                'cash_flow': self.mock_cash_flow
            }
            
            ratios = self.analyzer.calculate_profitability_ratios('AAPL')
            
            self.assertIn('roe', ratios)
            self.assertIn('roa', ratios)
            self.assertIn('net_margin', ratios)
            self.assertIn('gross_margin', ratios)
    
    def test_calculate_liquidity_ratios(self):
        """Test liquidity ratio calculations"""
        with patch.object(self.analyzer, 'get_financial_statements') as mock_get:
            mock_get.return_value = {
                'balance_sheet': self.mock_balance_sheet
            }
            
            ratios = self.analyzer.calculate_liquidity_ratios('AAPL')
            
            self.assertIn('current_ratio', ratios)
            self.assertIn('quick_ratio', ratios)
            self.assertIn('cash_ratio', ratios)
    
    def test_calculate_solvency_ratios(self):
        """Test solvency ratio calculations"""
        with patch.object(self.analyzer, 'get_financial_statements') as mock_get:
            mock_get.return_value = {
                'balance_sheet': self.mock_balance_sheet
            }
            
            ratios = self.analyzer.calculate_solvency_ratios('AAPL')
            
            self.assertIn('debt_to_equity', ratios)
            self.assertIn('debt_to_assets', ratios)
            self.assertIn('equity_ratio', ratios)
    
    def test_calculate_efficiency_ratios(self):
        """Test efficiency ratio calculations"""
        with patch.object(self.analyzer, 'get_financial_statements') as mock_get:
            mock_get.return_value = {
                'income_statement': self.mock_income_stmt,
                'balance_sheet': self.mock_balance_sheet
            }
            
            ratios = self.analyzer.calculate_efficiency_ratios('AAPL')
            
            self.assertIn('asset_turnover', ratios)
            self.assertIn('inventory_turnover', ratios)
    
    def test_calculate_valuation_ratios(self):
        """Test valuation ratio calculations"""
        with patch.object(self.analyzer, 'get_financial_statements') as mock_get:
            mock_get.return_value = {
                'income_statement': self.mock_income_stmt,
                'balance_sheet': self.mock_balance_sheet
            }
            
            ratios = self.analyzer.calculate_valuation_ratios('AAPL')
            
            self.assertIn('pe_ratio', ratios)
            self.assertIn('pb_ratio', ratios)
            self.assertIn('ps_ratio', ratios)
    
    def test_get_comprehensive_analysis(self):
        """Test comprehensive analysis"""
        with patch.object(self.analyzer, 'get_financial_statements') as mock_get:
            mock_get.return_value = {
                'income_statement': self.mock_income_stmt,
                'balance_sheet': self.mock_balance_sheet,
                'cash_flow': self.mock_cash_flow
            }
            
            analysis = self.analyzer.get_comprehensive_analysis('AAPL')
            
            self.assertIn('profitability_ratios', analysis)
            self.assertIn('liquidity_ratios', analysis)
            self.assertIn('solvency_ratios', analysis)
            self.assertIn('efficiency_ratios', analysis)
            self.assertIn('valuation_ratios', analysis)
            self.assertIn('growth_metrics', analysis)
            self.assertIn('financial_health_score', analysis)
    
    def test_calculate_financial_health_score(self):
        """Test financial health score calculation"""
        analysis = {
            'profitability_ratios': {'roe': 0.15, 'roa': 0.10},
            'liquidity_ratios': {'current_ratio': 2.0},
            'solvency_ratios': {'debt_to_equity': 0.5},
            'efficiency_ratios': {'asset_turnover': 1.2}
        }
        
        score = self.analyzer.calculate_financial_health_score(analysis)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class TestRiskAnalyzer(unittest.TestCase):
    """Test RiskAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = RiskAnalyzer()
        
        # Create mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * (1 + returns).cumprod()
        
        self.mock_price_data = pd.DataFrame({
            'Close': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
    
    @patch('yfinance.download')
    def test_calculate_volatility(self, mock_download):
        """Test volatility calculation"""
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.calculate_volatility('AAPL')
        
        self.assertIn('historical_volatility', result)
        self.assertIn('rolling_volatility', result)
        self.assertIsInstance(result['historical_volatility'], float)
        self.assertIsInstance(result['rolling_volatility'], pd.Series)
    
    @patch('yfinance.download')
    def test_calculate_var(self, mock_download):
        """Test Value at Risk calculation"""
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.calculate_var('AAPL')
        
        self.assertIn('historical_var', result)
        self.assertIn('parametric_var', result)
        self.assertIn('monte_carlo_var', result)
        self.assertIsInstance(result['historical_var'], float)
    
    @patch('yfinance.download')
    def test_calculate_beta(self, mock_download):
        """Test beta calculation"""
        # Mock both stock and market data
        mock_download.side_effect = [self.mock_price_data, self.mock_price_data]
        
        result = self.analyzer.calculate_beta('AAPL')
        
        self.assertIn('beta', result)
        self.assertIsInstance(result['beta'], float)
    
    @patch('yfinance.download')
    def test_calculate_max_drawdown(self, mock_download):
        """Test maximum drawdown calculation"""
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.calculate_max_drawdown('AAPL')
        
        self.assertIn('max_drawdown', result)
        self.assertIn('drawdown_period', result)
        self.assertIsInstance(result['max_drawdown'], float)
        self.assertLessEqual(result['max_drawdown'], 0)
    
    @patch('yfinance.download')
    def test_calculate_risk_ratios(self, mock_download):
        """Test risk ratio calculations"""
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.calculate_risk_ratios('AAPL')
        
        self.assertIn('sharpe_ratio', result)
        self.assertIn('sortino_ratio', result)
        self.assertIn('calmar_ratio', result)
        self.assertIsInstance(result['sharpe_ratio'], float)
    
    @patch('yfinance.download')
    def test_stress_testing(self, mock_download):
        """Test stress testing"""
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.stress_testing('AAPL')
        
        self.assertIn('market_crash_scenario', result)
        self.assertIn('interest_rate_shock', result)
        self.assertIn('volatility_spike', result)
        self.assertIn('correlation_breakdown', result)
    
    @patch('yfinance.download')
    def test_calculate_correlation(self, mock_download):
        """Test correlation calculation"""
        # Mock multiple stocks
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.calculate_correlation(['AAPL', 'MSFT', 'GOOGL'])
        
        self.assertIn('correlation_matrix', result)
        self.assertIsInstance(result['correlation_matrix'], pd.DataFrame)
    
    @patch('yfinance.download')
    def test_get_comprehensive_risk_analysis(self, mock_download):
        """Test comprehensive risk analysis"""
        mock_download.return_value = self.mock_price_data
        
        result = self.analyzer.get_comprehensive_risk_analysis('AAPL')
        
        self.assertIn('volatility_analysis', result)
        self.assertIn('var_analysis', result)
        self.assertIn('beta_analysis', result)
        self.assertIn('drawdown_analysis', result)
        self.assertIn('risk_ratios', result)
        self.assertIn('stress_test_results', result)
        self.assertIn('risk_score', result)
    
    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        analysis = {
            'volatility_analysis': {'historical_volatility': 0.25},
            'var_analysis': {'historical_var': -0.05},
            'beta_analysis': {'beta': 1.2},
            'drawdown_analysis': {'max_drawdown': -0.15},
            'risk_ratios': {'sharpe_ratio': 1.5}
        }
        
        score = self.analyzer.calculate_risk_score(analysis)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class TestPortfolioOptimizer(unittest.TestCase):
    """Test PortfolioOptimizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = PortfolioOptimizer()
        
        # Create mock portfolio data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Create correlated returns for multiple stocks
        n_stocks = 5
        returns_data = {}
        for i in range(n_stocks):
            returns = np.random.normal(0.001, 0.02, len(dates))
            returns_data[f'Stock_{i+1}'] = returns
        
        self.mock_returns = pd.DataFrame(returns_data, index=dates)
        self.mock_prices = (1 + self.mock_returns).cumprod()
    
    @patch('yfinance.download')
    def test_get_stock_data(self, mock_download):
        """Test getting stock data"""
        mock_download.return_value = self.mock_prices
        
        result = self.optimizer.get_stock_data(['AAPL', 'MSFT', 'GOOGL'])
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
    
    def test_calculate_returns(self):
        """Test return calculation"""
        returns = self.optimizer.calculate_returns(self.mock_prices)
        
        self.assertIsInstance(returns, pd.DataFrame)
        self.assertEqual(returns.shape[0], self.mock_prices.shape[0] - 1)
    
    def test_calculate_portfolio_metrics(self):
        """Test portfolio metrics calculation"""
        weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        returns = self.mock_returns
        
        metrics = self.optimizer.calculate_portfolio_metrics(weights, returns)
        
        self.assertIn('return', metrics)
        self.assertIn('volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('var_5', metrics)
    
    def test_optimize_portfolio(self):
        """Test portfolio optimization"""
        returns = self.mock_returns
        
        # Test different optimization methods
        methods = ['max_sharpe', 'min_volatility', 'equal_weight']
        
        for method in methods:
            result = self.optimizer.optimize_portfolio(returns, method=method)
            
            self.assertIn('weights', result)
            self.assertIn('metrics', result)
            self.assertIsInstance(result['weights'], np.ndarray)
            self.assertAlmostEqual(np.sum(result['weights']), 1.0, places=5)
    
    def test_efficient_frontier(self):
        """Test efficient frontier calculation"""
        returns = self.mock_returns
        
        result = self.optimizer.efficient_frontier(returns)
        
        self.assertIn('returns', result)
        self.assertIn('volatilities', result)
        self.assertIn('sharpe_ratios', result)
        self.assertIsInstance(result['returns'], list)
        self.assertIsInstance(result['volatilities'], list)
    
    def test_rebalance_portfolio(self):
        """Test portfolio rebalancing"""
        current_weights = np.array([0.3, 0.3, 0.2, 0.1, 0.1])
        target_weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        current_values = np.array([30000, 30000, 20000, 10000, 10000])
        
        result = self.optimizer.rebalance_portfolio(current_weights, target_weights, current_values)
        
        self.assertIn('trades', result)
        self.assertIn('new_weights', result)
        self.assertIn('cost', result)
        self.assertIsInstance(result['trades'], dict)


class TestValuationModels(unittest.TestCase):
    """Test valuation models"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dcf_model = DCFModel()
        self.ddm_model = DividendDiscountModel()
    
    @patch('yfinance.Ticker')
    def test_dcf_model_calculate_wacc(self, mock_ticker):
        """Test WACC calculation"""
        # Mock stock info
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
    def test_dcf_model_project_cash_flows(self, mock_ticker):
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
    
    @patch('yfinance.Ticker')
    def test_dcf_model_calculate_dcf_value(self, mock_ticker):
        """Test DCF value calculation"""
        # Mock stock data
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
        self.assertIsInstance(result['enterprise_value'], float)
        self.assertIsInstance(result['equity_value'], float)
        self.assertIsInstance(result['value_per_share'], float)
    
    def test_dcf_model_sensitivity_analysis(self):
        """Test DCF sensitivity analysis"""
        result = self.dcf_model.sensitivity_analysis('AAPL')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)
    
    @patch('yfinance.Ticker')
    def test_ddm_model_gordon_growth_model(self, mock_ticker):
        """Test Gordon Growth Model"""
        # Mock stock data
        mock_stock = Mock()
        mock_stock.info = {
            'trailingAnnualDividendRate': 2.0,
            'marketCap': 1000000000,
            'sharesOutstanding': 100000000
        }
        mock_stock.dividends = pd.Series([2.0, 1.8, 1.6], 
                                       index=['2023-12-31', '2022-12-31', '2021-12-31'])
        mock_ticker.return_value = mock_stock
        
        result = self.ddm_model.gordon_growth_model('AAPL')
        
        self.assertIn('value_per_share', result)
        self.assertIn('required_return', result)
        self.assertIn('growth_rate', result)
        self.assertIsInstance(result['value_per_share'], float)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.financial_analyzer = FinancialAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.dcf_model = DCFModel()
    
    @patch('yfinance.Ticker')
    @patch('yfinance.download')
    def test_full_analysis_pipeline(self, mock_download, mock_ticker):
        """Test full analysis pipeline"""
        # Mock all necessary data
        mock_stock = Mock()
        mock_stock.info = {
            'beta': 1.2,
            'marketCap': 1000000000,
            'totalDebt': 200000000,
            'cash': 50000000,
            'sharesOutstanding': 100000000
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
        mock_ticker.return_value = mock_stock
        
        # Mock price data
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        prices = pd.DataFrame({'Close': np.random.normal(100, 10, len(dates))}, index=dates)
        mock_download.return_value = prices
        
        # Run full analysis
        symbol = 'AAPL'
        
        # Financial analysis
        financial_analysis = self.financial_analyzer.get_comprehensive_analysis(symbol)
        
        # Risk analysis
        risk_analysis = self.risk_analyzer.get_comprehensive_risk_analysis(symbol)
        
        # Portfolio optimization (with multiple stocks)
        portfolio_returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 252),
            'MSFT': np.random.normal(0.001, 0.02, 252),
            'GOOGL': np.random.normal(0.001, 0.02, 252)
        })
        portfolio_result = self.portfolio_optimizer.optimize_portfolio(portfolio_returns)
        
        # DCF valuation
        dcf_result = self.dcf_model.calculate_dcf_value(symbol)
        
        # Assertions
        self.assertIsInstance(financial_analysis, dict)
        self.assertIsInstance(risk_analysis, dict)
        self.assertIsInstance(portfolio_result, dict)
        self.assertIsInstance(dcf_result, dict)
        
        # Check that all analyses have expected keys
        self.assertIn('financial_health_score', financial_analysis)
        self.assertIn('risk_score', risk_analysis)
        self.assertIn('weights', portfolio_result)
        self.assertIn('value_per_share', dcf_result)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
