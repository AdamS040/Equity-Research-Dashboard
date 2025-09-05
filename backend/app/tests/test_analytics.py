"""
Tests for Analytics Engine

Comprehensive test suite for the advanced analytics and financial modeling engine.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.services.analytics_engine import (
    AnalyticsEngine, DCFAnalysisEngine, RiskAnalysisEngine, OptionsAnalysisEngine,
    DCFInputs, DCFResults, RiskMetrics, OptionsGreeks, MathematicalValidator
)
from app.services.comparable_analysis import (
    ComparableValuationEngine, PeerIdentificationEngine, ValuationMultiplesEngine
)
from app.services.backtesting_engine import (
    BacktestingEngine, StrategyEngine, BacktestStrategy
)
from app.services.economic_indicators import (
    EconomicIndicatorsEngine, EconomicDataProvider
)


class TestMathematicalValidator:
    """Test mathematical validation functions"""
    
    def test_validate_dcf_inputs_valid(self):
        """Test DCF input validation with valid inputs"""
        validator = MathematicalValidator()
        
        inputs = DCFInputs(
            symbol="AAPL",
            current_price=150.0,
            revenue=1000000000,
            revenue_growth_rate=0.1,
            ebitda_margin=0.3,
            tax_rate=0.25,
            capex=50000000,
            working_capital=100000000,
            terminal_growth_rate=0.03,
            wacc=0.1,
            beta=1.2,
            risk_free_rate=0.02,
            market_risk_premium=0.08,
            debt_to_equity=0.5,
            cost_of_debt=0.05,
            projection_years=5
        )
        
        errors = validator.validate_dcf_inputs(inputs)
        assert len(errors) == 0
    
    def test_validate_dcf_inputs_invalid(self):
        """Test DCF input validation with invalid inputs"""
        validator = MathematicalValidator()
        
        inputs = DCFInputs(
            symbol="AAPL",
            current_price=-150.0,  # Invalid: negative price
            revenue=0,  # Invalid: zero revenue
            revenue_growth_rate=1.5,  # Invalid: > 1
            ebitda_margin=1.5,  # Invalid: > 1
            tax_rate=1.5,  # Invalid: > 1
            capex=50000000,
            working_capital=100000000,
            terminal_growth_rate=0.15,  # Invalid: > 0.1
            wacc=0.1,
            beta=1.2,
            risk_free_rate=0.02,
            market_risk_premium=0.08,
            debt_to_equity=0.5,
            cost_of_debt=0.05,
            projection_years=25  # Invalid: > 20
        )
        
        errors = validator.validate_dcf_inputs(inputs)
        assert len(errors) > 0
        assert any("Revenue must be positive" in error for error in errors)
        assert any("Revenue growth rate must be between 0 and 1" in error for error in errors)
    
    def test_validate_risk_inputs_valid(self):
        """Test risk input validation with valid data"""
        validator = MathematicalValidator()
        
        returns = [0.01, -0.02, 0.03, -0.01, 0.02] * 10  # 50 data points
        
        errors = validator.validate_risk_inputs(returns)
        assert len(errors) == 0
    
    def test_validate_risk_inputs_invalid(self):
        """Test risk input validation with invalid data"""
        validator = MathematicalValidator()
        
        # Too few data points
        returns = [0.01, -0.02, 0.03]
        errors = validator.validate_risk_inputs(returns)
        assert len(errors) > 0
        assert any("At least 30 data points required" in error for error in errors)
        
        # Invalid values
        returns = [0.01, float('nan'), 0.03] * 10
        errors = validator.validate_risk_inputs(returns)
        assert len(errors) > 0
        assert any("Returns contain invalid values" in error for error in errors)


class TestDCFAnalysisEngine:
    """Test DCF Analysis Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.dcf_engine = DCFAnalysisEngine()
        
        self.valid_inputs = DCFInputs(
            symbol="AAPL",
            current_price=150.0,
            revenue=1000000000,
            revenue_growth_rate=0.1,
            ebitda_margin=0.3,
            tax_rate=0.25,
            capex=50000000,
            working_capital=100000000,
            terminal_growth_rate=0.03,
            wacc=0.1,
            beta=1.2,
            risk_free_rate=0.02,
            market_risk_premium=0.08,
            debt_to_equity=0.5,
            cost_of_debt=0.05,
            projection_years=5
        )
    
    def test_calculate_wacc(self):
        """Test WACC calculation"""
        wacc = self.dcf_engine.calculate_wacc(self.valid_inputs)
        
        assert isinstance(wacc, float)
        assert 0 < wacc < 1
        assert wacc > self.valid_inputs.risk_free_rate
    
    def test_calculate_free_cash_flow(self):
        """Test free cash flow calculation"""
        projection = self.dcf_engine.calculate_free_cash_flow(self.valid_inputs, 1)
        
        assert projection.year == 1
        assert projection.revenue > self.valid_inputs.revenue
        assert projection.ebitda > 0
        assert projection.free_cash_flow > 0
        assert projection.present_value > 0
    
    def test_calculate_terminal_value(self):
        """Test terminal value calculation"""
        final_fcf = 100000000
        terminal_value = self.dcf_engine.calculate_terminal_value(self.valid_inputs, final_fcf)
        
        assert terminal_value > 0
        assert terminal_value > final_fcf
    
    def test_perform_dcf_analysis(self):
        """Test complete DCF analysis"""
        results = self.dcf_engine.perform_dcf_analysis(self.valid_inputs)
        
        assert isinstance(results, DCFResults)
        assert results.fair_value > 0
        assert len(results.projections) == self.valid_inputs.projection_years
        assert results.terminal_value > 0
        assert 'wacc' in results.wacc_breakdown
    
    def test_perform_sensitivity_analysis(self):
        """Test sensitivity analysis"""
        base_fair_value = 1000000000
        sensitivity = self.dcf_engine.perform_sensitivity_analysis(self.valid_inputs, base_fair_value)
        
        assert isinstance(sensitivity, dict)
        assert 'wacc' in sensitivity
        assert 'terminal_growth' in sensitivity
        assert 'revenue_growth' in sensitivity
    
    def test_perform_monte_carlo_dcf(self):
        """Test Monte Carlo DCF simulation"""
        monte_carlo_results = self.dcf_engine.perform_monte_carlo_dcf(self.valid_inputs, simulations=100)
        
        assert isinstance(monte_carlo_results, dict)
        assert 'mean' in monte_carlo_results
        assert 'median' in monte_carlo_results
        assert 'std' in monte_carlo_results
        assert monte_carlo_results['simulations'] > 0


class TestRiskAnalysisEngine:
    """Test Risk Analysis Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.risk_engine = RiskAnalysisEngine()
        
        # Generate realistic returns data
        np.random.seed(42)
        self.returns = np.random.normal(0.001, 0.02, 252).tolist()  # Daily returns for 1 year
        self.benchmark_returns = np.random.normal(0.0008, 0.015, 252).tolist()
    
    def test_calculate_risk_metrics(self):
        """Test risk metrics calculation"""
        metrics = self.risk_engine.calculate_risk_metrics(self.returns, self.benchmark_returns)
        
        assert isinstance(metrics, RiskMetrics)
        assert metrics.volatility > 0
        assert metrics.beta > 0
        assert metrics.sharpe_ratio is not None
        assert metrics.max_drawdown <= 0
        assert metrics.var_95 < 0
        assert metrics.var_99 < metrics.var_95
    
    def test_perform_stress_test(self):
        """Test stress testing"""
        scenarios = {
            'market_crash': -0.2,
            'recession': -0.1,
            'volatility_spike': 0.5
        }
        
        stress_results = self.risk_engine.perform_stress_test(self.returns, scenarios)
        
        assert isinstance(stress_results, dict)
        assert 'market_crash' in stress_results
        assert 'recession' in stress_results
        assert 'volatility_spike' in stress_results
        
        for scenario, result in stress_results.items():
            assert 'shock' in result
            assert 'expected_loss' in result
            assert 'var_95' in result
    
    def test_calculate_correlation_matrix(self):
        """Test correlation matrix calculation"""
        returns_data = {
            'AAPL': self.returns,
            'MSFT': self.benchmark_returns,
            'GOOGL': [r * 1.1 for r in self.returns]  # Slightly different returns
        }
        
        correlation_matrix = self.risk_engine.calculate_correlation_matrix(returns_data)
        
        assert isinstance(correlation_matrix, dict)
        assert 'matrix' in correlation_matrix
        assert 'average_correlation' in correlation_matrix
        assert 'max_correlation' in correlation_matrix
        assert 'min_correlation' in correlation_matrix


class TestOptionsAnalysisEngine:
    """Test Options Analysis Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.options_engine = OptionsAnalysisEngine()
        
        self.test_params = {
            'S': 100.0,  # Stock price
            'K': 105.0,  # Strike price
            'T': 0.25,   # Time to expiration (3 months)
            'r': 0.05,   # Risk-free rate
            'sigma': 0.2  # Volatility
        }
    
    def test_black_scholes_price_call(self):
        """Test Black-Scholes pricing for call option"""
        price = self.options_engine.black_scholes_price(
            self.test_params['S'],
            self.test_params['K'],
            self.test_params['T'],
            self.test_params['r'],
            self.test_params['sigma'],
            'call'
        )
        
        assert price > 0
        assert price < self.test_params['S']  # Call price should be less than stock price
    
    def test_black_scholes_price_put(self):
        """Test Black-Scholes pricing for put option"""
        price = self.options_engine.black_scholes_price(
            self.test_params['S'],
            self.test_params['K'],
            self.test_params['T'],
            self.test_params['r'],
            self.test_params['sigma'],
            'put'
        )
        
        assert price > 0
        assert price < self.test_params['K']  # Put price should be less than strike price
    
    def test_calculate_greeks_call(self):
        """Test Greeks calculation for call option"""
        greeks = self.options_engine.calculate_greeks(
            self.test_params['S'],
            self.test_params['K'],
            self.test_params['T'],
            self.test_params['r'],
            self.test_params['sigma'],
            'call'
        )
        
        assert isinstance(greeks, OptionsGreeks)
        assert 0 <= greeks.delta <= 1  # Call delta should be between 0 and 1
        assert greeks.gamma > 0
        assert greeks.theta < 0  # Theta should be negative (time decay)
        assert greeks.vega > 0
        assert greeks.rho > 0  # Call rho should be positive
    
    def test_calculate_greeks_put(self):
        """Test Greeks calculation for put option"""
        greeks = self.options_engine.calculate_greeks(
            self.test_params['S'],
            self.test_params['K'],
            self.test_params['T'],
            self.test_params['r'],
            self.test_params['sigma'],
            'put'
        )
        
        assert isinstance(greeks, OptionsGreeks)
        assert -1 <= greeks.delta <= 0  # Put delta should be between -1 and 0
        assert greeks.gamma > 0
        assert greeks.theta < 0  # Theta should be negative (time decay)
        assert greeks.vega > 0
        assert greeks.rho < 0  # Put rho should be negative
    
    def test_implied_volatility(self):
        """Test implied volatility calculation"""
        # First calculate theoretical price
        theoretical_price = self.options_engine.black_scholes_price(
            self.test_params['S'],
            self.test_params['K'],
            self.test_params['T'],
            self.test_params['r'],
            self.test_params['sigma'],
            'call'
        )
        
        # Then calculate implied volatility
        implied_vol = self.options_engine.implied_volatility(
            theoretical_price,
            self.test_params['S'],
            self.test_params['K'],
            self.test_params['T'],
            self.test_params['r'],
            'call'
        )
        
        # Should be close to the original volatility
        assert abs(implied_vol - self.test_params['sigma']) < 0.01


class TestComparableAnalysisEngine:
    """Test Comparable Analysis Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.comparable_engine = ComparableValuationEngine()
        
        self.target_company = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'industry': 'Technology',
            'sector': 'Technology',
            'market_cap': 3000000000000,
            'country': 'US'
        }
        
        self.peer_universe = [
            {
                'symbol': 'MSFT',
                'name': 'Microsoft Corporation',
                'industry': 'Technology',
                'sector': 'Technology',
                'market_cap': 2800000000000,
                'revenue': 200000000000,
                'ebitda': 80000000000,
                'net_income': 60000000000,
                'shares_outstanding': 7500000000,
                'price': 150.0,
                'total_debt': 50000000000,
                'cash': 100000000000,
                'book_value': 100000000000,
                'total_assets': 400000000000,
                'total_equity': 150000000000,
                'current_assets': 200000000000,
                'current_liabilities': 100000000000,
                'revenue_growth_rate': 0.15,
                'country': 'US'
            },
            {
                'symbol': 'GOOGL',
                'name': 'Alphabet Inc.',
                'industry': 'Technology',
                'sector': 'Technology',
                'market_cap': 1800000000000,
                'revenue': 250000000000,
                'ebitda': 70000000000,
                'net_income': 50000000000,
                'shares_outstanding': 6000000000,
                'price': 120.0,
                'total_debt': 30000000000,
                'cash': 150000000000,
                'book_value': 200000000000,
                'total_assets': 350000000000,
                'total_equity': 180000000000,
                'current_assets': 180000000000,
                'current_liabilities': 80000000000,
                'revenue_growth_rate': 0.20,
                'country': 'US'
            }
        ]
        
        self.target_financials = {
            'revenue': 400000000000,
            'ebitda': 120000000000,
            'net_income': 100000000000,
            'book_value': 50000000000
        }
    
    def test_identify_peers(self):
        """Test peer identification"""
        criteria = {
            'require_industry_match': True,
            'min_market_cap_ratio': 0.1,
            'max_market_cap_ratio': 10.0,
            'max_peers': 20
        }
        
        peers = self.comparable_engine.peer_engine.identify_peers(
            self.target_company,
            self.peer_universe,
            criteria
        )
        
        assert len(peers) > 0
        assert all(peer.industry == 'Technology' for peer in peers)
        assert all(peer.market_cap > 0 for peer in peers)
    
    def test_calculate_valuation_metrics(self):
        """Test valuation metrics calculation"""
        # First identify peers
        criteria = {'require_industry_match': True, 'max_peers': 20}
        peers = self.comparable_engine.peer_engine.identify_peers(
            self.target_company, self.peer_universe, criteria
        )
        
        # Then calculate metrics
        metrics = self.comparable_engine.multiples_engine.calculate_valuation_metrics(peers)
        
        assert isinstance(metrics, dict)
        assert 'pe' in metrics
        assert 'pb' in metrics
        assert 'ps' in metrics
        assert 'ev_revenue' in metrics
        assert 'ev_ebitda' in metrics
        
        for metric_name, metric in metrics.items():
            assert metric.min <= metric.median <= metric.max
            assert metric.count > 0
    
    def test_perform_comparable_analysis(self):
        """Test complete comparable analysis"""
        results = self.comparable_engine.perform_comparable_analysis(
            self.target_company,
            self.peer_universe,
            self.target_financials
        )
        
        assert isinstance(results, dict)
        assert 'peers' in results
        assert 'valuation_metrics' in results
        assert 'comparable_valuation' in results
        assert 'peer_rankings' in results
        assert 'industry_analysis' in results
        assert 'analysis_metadata' in results


class TestBacktestingEngine:
    """Test Backtesting Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.backtesting_engine = BacktestingEngine()
        
        # Create sample historical data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Generate realistic price data
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * np.cumprod(1 + returns)
        
        self.historical_data = {
            'AAPL': pd.DataFrame({
                'close': prices,
                'open': prices * 0.99,
                'high': prices * 1.02,
                'low': prices * 0.98,
                'volume': np.random.randint(1000000, 10000000, len(dates))
            }, index=dates)
        }
        
        self.strategy = BacktestStrategy(
            name='moving_average_crossover',
            description='Simple moving average crossover strategy',
            parameters={'short_window': 20, 'long_window': 50},
            entry_rules=['SMA short > SMA long'],
            exit_rules=['SMA short < SMA long'],
            position_sizing='equal_weight'
        )
    
    def test_moving_average_crossover_strategy(self):
        """Test moving average crossover strategy"""
        strategy_engine = StrategyEngine()
        
        result = strategy_engine.moving_average_crossover(
            self.historical_data['AAPL'],
            short_window=20,
            long_window=50
        )
        
        assert 'sma_short' in result.columns
        assert 'sma_long' in result.columns
        assert 'signal' in result.columns
        assert 'position' in result.columns
        
        # Check that signals are valid
        assert all(signal in [-1, 0, 1] for signal in result['signal'].dropna())
    
    def test_rsi_strategy(self):
        """Test RSI strategy"""
        strategy_engine = StrategyEngine()
        
        result = strategy_engine.rsi_strategy(
            self.historical_data['AAPL'],
            rsi_period=14,
            oversold=30,
            overbought=70
        )
        
        assert 'rsi' in result.columns
        assert 'signal' in result.columns
        assert 'position' in result.columns
        
        # Check RSI values are between 0 and 100
        rsi_values = result['rsi'].dropna()
        assert all(0 <= rsi <= 100 for rsi in rsi_values)
    
    def test_momentum_strategy(self):
        """Test momentum strategy"""
        strategy_engine = StrategyEngine()
        
        result = strategy_engine.momentum_strategy(
            self.historical_data['AAPL'],
            lookback_period=20,
            threshold=0.02
        )
        
        assert 'momentum' in result.columns
        assert 'signal' in result.columns
        assert 'position' in result.columns
    
    def test_mean_reversion_strategy(self):
        """Test mean reversion strategy"""
        strategy_engine = StrategyEngine()
        
        result = strategy_engine.mean_reversion_strategy(
            self.historical_data['AAPL'],
            lookback_period=20,
            std_threshold=2.0
        )
        
        assert 'rolling_mean' in result.columns
        assert 'rolling_std' in result.columns
        assert 'z_score' in result.columns
        assert 'signal' in result.columns
        assert 'position' in result.columns


class TestEconomicIndicatorsEngine:
    """Test Economic Indicators Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.economic_engine = EconomicIndicatorsEngine()
    
    @pytest.mark.asyncio
    async def test_get_key_indicators(self):
        """Test getting key economic indicators"""
        # Mock the data provider
        with patch.object(self.economic_engine.data_provider, 'fetch_fred_data') as mock_fetch:
            # Mock FRED data response
            mock_data = pd.DataFrame({
                'value': [100, 101, 102]
            }, index=pd.date_range('2023-01-01', periods=3, freq='M'))
            mock_fetch.return_value = mock_data
            
            indicators = await self.economic_engine.get_key_indicators('US')
            
            assert isinstance(indicators, dict)
            # Note: In a real test, you'd need to mock all the indicator methods
    
    @pytest.mark.asyncio
    async def test_get_market_sentiment(self):
        """Test getting market sentiment"""
        sentiment = await self.economic_engine.get_market_sentiment()
        
        assert sentiment.vix >= 0
        assert sentiment.fear_greed_index >= 0
        assert sentiment.put_call_ratio >= 0
    
    def test_assess_indicator_impact(self):
        """Test indicator impact assessment"""
        from app.services.economic_indicators import EconomicIndicator
        
        # Test GDP indicator
        gdp_indicator = EconomicIndicator(
            name='GDP',
            symbol='GDP',
            value=100,
            previous_value=99,
            change=1,
            change_percent=1.01,
            unit='Billions',
            frequency='Quarterly',
            last_updated='2023-01-01',
            source='FRED',
            description='GDP',
            importance='High',
            country='US',
            category='GDP'
        )
        
        impact = self.economic_engine._assess_indicator_impact(gdp_indicator)
        assert impact == 'Positive'
        
        # Test inflation indicator
        inflation_indicator = EconomicIndicator(
            name='CPI',
            symbol='CPI',
            value=100,
            previous_value=99,
            change=1,
            change_percent=1.01,
            unit='Index',
            frequency='Monthly',
            last_updated='2023-01-01',
            source='FRED',
            description='CPI',
            importance='High',
            country='US',
            category='Inflation'
        )
        
        impact = self.economic_engine._assess_indicator_impact(inflation_indicator)
        assert impact in ['Positive', 'Negative', 'Neutral']


class TestAnalyticsEngine:
    """Test Main Analytics Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analytics_engine = AnalyticsEngine()
    
    @pytest.mark.asyncio
    async def test_analyze_dcf_async(self):
        """Test async DCF analysis"""
        inputs = DCFInputs(
            symbol="AAPL",
            current_price=150.0,
            revenue=1000000000,
            revenue_growth_rate=0.1,
            ebitda_margin=0.3,
            tax_rate=0.25,
            capex=50000000,
            working_capital=100000000,
            terminal_growth_rate=0.03,
            wacc=0.1,
            beta=1.2,
            risk_free_rate=0.02,
            market_risk_premium=0.08,
            debt_to_equity=0.5,
            cost_of_debt=0.05,
            projection_years=5
        )
        
        results = await self.analytics_engine.analyze_dcf(inputs)
        
        assert isinstance(results, DCFResults)
        assert results.fair_value > 0
    
    @pytest.mark.asyncio
    async def test_analyze_risk_async(self):
        """Test async risk analysis"""
        returns = np.random.normal(0.001, 0.02, 100).tolist()
        benchmark_returns = np.random.normal(0.0008, 0.015, 100).tolist()
        
        results = await self.analytics_engine.analyze_risk(returns, benchmark_returns)
        
        assert isinstance(results, RiskMetrics)
        assert results.volatility > 0
    
    @pytest.mark.asyncio
    async def test_analyze_options_async(self):
        """Test async options analysis"""
        results = await self.analytics_engine.analyze_options(
            S=100.0,
            K=105.0,
            T=0.25,
            r=0.05,
            sigma=0.2,
            option_type='call'
        )
        
        assert 'price' in results
        assert 'greeks' in results
        assert results['price'] > 0
        assert 'delta' in results['greeks']


if __name__ == '__main__':
    pytest.main([__file__])
