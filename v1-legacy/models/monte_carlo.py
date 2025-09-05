"""
Monte Carlo Simulation module for Equity Research Dashboard
Provides functionality for Monte Carlo simulations in financial modeling,
risk analysis, and portfolio optimization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from scipy import stats
from scipy.stats import norm, lognorm, t
import warnings
warnings.filterwarnings('ignore')


class MonteCarloSimulator:
    """Monte Carlo simulation for financial modeling"""
    
    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize Monte Carlo simulator
        
        Args:
            random_seed: Random seed for reproducibility
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        self.random_seed = random_seed
    
    def simulate_stock_price(self, 
                           current_price: float,
                           expected_return: float,
                           volatility: float,
                           time_horizon: int,
                           num_simulations: int = 10000,
                           distribution: str = 'lognormal') -> Dict:
        """
        Simulate stock price paths using Monte Carlo
        
        Args:
            current_price: Current stock price
            expected_return: Expected annual return
            volatility: Annual volatility
            time_horizon: Number of days to simulate
            num_simulations: Number of simulation paths
            distribution: Price distribution ('lognormal', 'normal')
            
        Returns:
            Dictionary with simulation results
        """
        # Convert annual parameters to daily
        daily_return = expected_return / 252
        daily_volatility = volatility / np.sqrt(252)
        
        # Generate random numbers
        if distribution == 'lognormal':
            # Log-normal distribution for prices
            drift = daily_return - 0.5 * daily_volatility**2
            random_shocks = np.random.normal(0, 1, (num_simulations, time_horizon))
            price_paths = np.zeros((num_simulations, time_horizon + 1))
            price_paths[:, 0] = current_price
            
            for t in range(time_horizon):
                price_paths[:, t + 1] = price_paths[:, t] * np.exp(
                    drift + daily_volatility * random_shocks[:, t]
                )
        else:
            # Normal distribution for returns
            random_shocks = np.random.normal(0, 1, (num_simulations, time_horizon))
            price_paths = np.zeros((num_simulations, time_horizon + 1))
            price_paths[:, 0] = current_price
            
            for t in range(time_horizon):
                returns = daily_return + daily_volatility * random_shocks[:, t]
                price_paths[:, t + 1] = price_paths[:, t] * (1 + returns)
        
        # Calculate statistics
        final_prices = price_paths[:, -1]
        mean_price = np.mean(final_prices)
        median_price = np.median(final_prices)
        std_price = np.std(final_prices)
        
        # Calculate percentiles
        percentiles = {
            '5th': np.percentile(final_prices, 5),
            '25th': np.percentile(final_prices, 25),
            '50th': np.percentile(final_prices, 50),
            '75th': np.percentile(final_prices, 75),
            '95th': np.percentile(final_prices, 95)
        }
        
        # Calculate probability of profit
        prob_profit = np.mean(final_prices > current_price)
        
        return {
            'price_paths': price_paths,
            'final_prices': final_prices,
            'statistics': {
                'mean': mean_price,
                'median': median_price,
                'std': std_price,
                'min': np.min(final_prices),
                'max': np.max(final_prices)
            },
            'percentiles': percentiles,
            'probability_profit': prob_profit,
            'parameters': {
                'current_price': current_price,
                'expected_return': expected_return,
                'volatility': volatility,
                'time_horizon': time_horizon,
                'num_simulations': num_simulations,
                'distribution': distribution
            }
        }
    
    def simulate_portfolio_returns(self,
                                 weights: List[float],
                                 returns_data: pd.DataFrame,
                                 time_horizon: int,
                                 num_simulations: int = 10000) -> Dict:
        """
        Simulate portfolio returns using Monte Carlo
        
        Args:
            weights: Portfolio weights
            returns_data: Historical returns data
            time_horizon: Number of days to simulate
            num_simulations: Number of simulation paths
            
        Returns:
            Dictionary with simulation results
        """
        # Calculate portfolio statistics
        portfolio_returns = returns_data.dot(weights)
        mean_return = portfolio_returns.mean()
        volatility = portfolio_returns.std()
        
        # Generate correlated returns
        correlation_matrix = returns_data.corr()
        cholesky_matrix = np.linalg.cholesky(correlation_matrix.values)
        
        # Generate random numbers
        random_numbers = np.random.normal(0, 1, (num_simulations, time_horizon, len(weights)))
        
        # Apply correlation structure
        correlated_random = np.zeros_like(random_numbers)
        for i in range(num_simulations):
            for j in range(time_horizon):
                correlated_random[i, j, :] = cholesky_matrix @ random_numbers[i, j, :]
        
        # Generate returns for each asset
        asset_returns = np.zeros((num_simulations, time_horizon, len(weights)))
        for i in range(len(weights)):
            asset_mean = returns_data.iloc[:, i].mean()
            asset_std = returns_data.iloc[:, i].std()
            asset_returns[:, :, i] = asset_mean + asset_std * correlated_random[:, :, i]
        
        # Calculate portfolio returns
        portfolio_sim_returns = np.sum(asset_returns * weights, axis=2)
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + portfolio_sim_returns, axis=1)
        
        # Calculate statistics
        final_values = cumulative_returns[:, -1]
        mean_final_value = np.mean(final_values)
        median_final_value = np.median(final_values)
        std_final_value = np.std(final_values)
        
        # Calculate percentiles
        percentiles = {
            '5th': np.percentile(final_values, 5),
            '25th': np.percentile(final_values, 25),
            '50th': np.percentile(final_values, 50),
            '75th': np.percentile(final_values, 75),
            '95th': np.percentile(final_values, 95)
        }
        
        # Calculate VaR and CVaR
        var_95 = np.percentile(final_values, 5)
        cvar_95 = np.mean(final_values[final_values <= var_95])
        
        return {
            'cumulative_returns': cumulative_returns,
            'final_values': final_values,
            'statistics': {
                'mean': mean_final_value,
                'median': median_final_value,
                'std': std_final_value,
                'min': np.min(final_values),
                'max': np.max(final_values)
            },
            'percentiles': percentiles,
            'risk_metrics': {
                'var_95': var_95,
                'cvar_95': cvar_95,
                'volatility': volatility,
                'expected_return': mean_return
            },
            'parameters': {
                'weights': weights,
                'time_horizon': time_horizon,
                'num_simulations': num_simulations
            }
        }
    
    def simulate_option_pricing(self,
                               current_price: float,
                               strike_price: float,
                               time_to_maturity: float,
                               risk_free_rate: float,
                               volatility: float,
                               option_type: str = 'call',
                               num_simulations: int = 10000) -> Dict:
        """
        Simulate option pricing using Monte Carlo
        
        Args:
            current_price: Current stock price
            strike_price: Option strike price
            time_to_maturity: Time to maturity in years
            risk_free_rate: Risk-free rate
            volatility: Stock volatility
            option_type: 'call' or 'put'
            num_simulations: Number of simulations
            
        Returns:
            Dictionary with option pricing results
        """
        # Generate stock price paths
        drift = risk_free_rate - 0.5 * volatility**2
        random_shocks = np.random.normal(0, 1, num_simulations)
        
        # Simulate final stock prices
        final_prices = current_price * np.exp(
            drift * time_to_maturity + volatility * np.sqrt(time_to_maturity) * random_shocks
        )
        
        # Calculate option payoffs
        if option_type.lower() == 'call':
            payoffs = np.maximum(final_prices - strike_price, 0)
        else:  # put option
            payoffs = np.maximum(strike_price - final_prices, 0)
        
        # Discount payoffs to present value
        option_price = np.mean(payoffs) * np.exp(-risk_free_rate * time_to_maturity)
        
        # Calculate statistics
        mean_payoff = np.mean(payoffs)
        std_payoff = np.std(payoffs)
        
        # Calculate percentiles
        percentiles = {
            '5th': np.percentile(payoffs, 5),
            '25th': np.percentile(payoffs, 25),
            '50th': np.percentile(payoffs, 50),
            '75th': np.percentile(payoffs, 75),
            '95th': np.percentile(payoffs, 95)
        }
        
        # Calculate probability of exercise
        prob_exercise = np.mean(payoffs > 0)
        
        return {
            'option_price': option_price,
            'final_prices': final_prices,
            'payoffs': payoffs,
            'statistics': {
                'mean_payoff': mean_payoff,
                'std_payoff': std_payoff,
                'min_payoff': np.min(payoffs),
                'max_payoff': np.max(payoffs)
            },
            'percentiles': percentiles,
            'probability_exercise': prob_exercise,
            'parameters': {
                'current_price': current_price,
                'strike_price': strike_price,
                'time_to_maturity': time_to_maturity,
                'risk_free_rate': risk_free_rate,
                'volatility': volatility,
                'option_type': option_type,
                'num_simulations': num_simulations
            }
        }
    
    def simulate_risk_analysis(self,
                              returns_data: pd.DataFrame,
                              confidence_level: float = 0.95,
                              time_horizon: int = 252,
                              num_simulations: int = 10000) -> Dict:
        """
        Simulate risk analysis using Monte Carlo
        
        Args:
            returns_data: Historical returns data
            confidence_level: Confidence level for VaR
            time_horizon: Time horizon in days
            num_simulations: Number of simulations
            
        Returns:
            Dictionary with risk analysis results
        """
        # Calculate parameters
        mean_returns = returns_data.mean()
        cov_matrix = returns_data.cov()
        
        # Generate correlated returns
        cholesky_matrix = np.linalg.cholesky(cov_matrix.values)
        random_numbers = np.random.normal(0, 1, (num_simulations, time_horizon, len(mean_returns)))
        
        # Apply correlation structure
        correlated_random = np.zeros_like(random_numbers)
        for i in range(num_simulations):
            for j in range(time_horizon):
                correlated_random[i, j, :] = cholesky_matrix @ random_numbers[i, j, :]
        
        # Generate returns
        simulated_returns = np.zeros_like(correlated_random)
        for i in range(len(mean_returns)):
            simulated_returns[:, :, i] = mean_returns[i] + np.sqrt(cov_matrix.iloc[i, i]) * correlated_random[:, :, i]
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + simulated_returns, axis=1)
        
        # Calculate portfolio returns (equal weight for simplicity)
        weights = np.ones(len(mean_returns)) / len(mean_returns)
        portfolio_returns = np.sum(simulated_returns * weights, axis=2)
        portfolio_cumulative = np.cumprod(1 + portfolio_returns, axis=1)
        
        # Calculate risk metrics
        final_values = portfolio_cumulative[:, -1]
        
        # Value at Risk
        var_percentile = (1 - confidence_level) * 100
        var = np.percentile(final_values, var_percentile)
        
        # Conditional Value at Risk (Expected Shortfall)
        cvar = np.mean(final_values[final_values <= var])
        
        # Maximum Drawdown
        max_drawdowns = []
        for path in portfolio_cumulative:
            peak = np.maximum.accumulate(path)
            drawdown = (path - peak) / peak
            max_drawdowns.append(np.min(drawdown))
        
        max_drawdown = np.mean(max_drawdowns)
        
        # Volatility
        volatility = np.std(portfolio_returns, axis=1)
        mean_volatility = np.mean(volatility)
        
        return {
            'portfolio_cumulative': portfolio_cumulative,
            'final_values': final_values,
            'risk_metrics': {
                'var': var,
                'cvar': cvar,
                'max_drawdown': max_drawdown,
                'volatility': mean_volatility,
                'mean_return': np.mean(final_values),
                'median_return': np.median(final_values)
            },
            'percentiles': {
                '5th': np.percentile(final_values, 5),
                '25th': np.percentile(final_values, 25),
                '50th': np.percentile(final_values, 50),
                '75th': np.percentile(final_values, 75),
                '95th': np.percentile(final_values, 95)
            },
            'parameters': {
                'confidence_level': confidence_level,
                'time_horizon': time_horizon,
                'num_simulations': num_simulations
            }
        }
    
    def simulate_stress_test(self,
                           portfolio_data: Dict,
                           stress_scenarios: Dict,
                           num_simulations: int = 10000) -> Dict:
        """
        Simulate stress testing scenarios
        
        Args:
            portfolio_data: Portfolio data and parameters
            stress_scenarios: Dictionary of stress scenarios
            num_simulations: Number of simulations
            
        Returns:
            Dictionary with stress test results
        """
        results = {}
        
        for scenario_name, scenario_params in stress_scenarios.items():
            # Apply stress scenario parameters
            modified_data = self._apply_stress_scenario(portfolio_data, scenario_params)
            
            # Run simulation with modified parameters
            if 'returns_data' in modified_data:
                scenario_results = self.simulate_portfolio_returns(
                    weights=modified_data.get('weights', [1.0]),
                    returns_data=modified_data['returns_data'],
                    time_horizon=modified_data.get('time_horizon', 252),
                    num_simulations=num_simulations
                )
            else:
                scenario_results = self.simulate_stock_price(
                    current_price=modified_data.get('current_price', 100),
                    expected_return=modified_data.get('expected_return', 0.1),
                    volatility=modified_data.get('volatility', 0.2),
                    time_horizon=modified_data.get('time_horizon', 252),
                    num_simulations=num_simulations
                )
            
            results[scenario_name] = {
                'parameters': scenario_params,
                'results': scenario_results
            }
        
        return results
    
    def _apply_stress_scenario(self, portfolio_data: Dict, scenario_params: Dict) -> Dict:
        """Apply stress scenario parameters to portfolio data"""
        modified_data = portfolio_data.copy()
        
        # Apply volatility shock
        if 'volatility_shock' in scenario_params:
            shock = scenario_params['volatility_shock']
            if 'volatility' in modified_data:
                modified_data['volatility'] *= (1 + shock)
            if 'returns_data' in modified_data:
                # Increase volatility by scaling returns
                modified_data['returns_data'] = modified_data['returns_data'] * (1 + shock)
        
        # Apply return shock
        if 'return_shock' in scenario_params:
            shock = scenario_params['return_shock']
            if 'expected_return' in modified_data:
                modified_data['expected_return'] += shock
            if 'returns_data' in modified_data:
                # Shift returns by adding shock
                modified_data['returns_data'] = modified_data['returns_data'] + shock / 252
        
        # Apply correlation shock
        if 'correlation_shock' in scenario_params:
            shock = scenario_params['correlation_shock']
            if 'returns_data' in modified_data:
                # Modify correlation structure
                corr_matrix = modified_data['returns_data'].corr()
                modified_corr = corr_matrix * (1 + shock)
                # Ensure correlation matrix is valid
                modified_corr = np.clip(modified_corr, -1, 1)
                np.fill_diagonal(modified_corr, 1)
                # Reconstruct returns with new correlation
                # This is a simplified approach
                modified_data['returns_data'] = modified_data['returns_data'] * (1 + shock * 0.1)
        
        return modified_data


class MonteCarloAnalyzer:
    """Analyze Monte Carlo simulation results"""
    
    @staticmethod
    def analyze_price_simulation(simulation_results: Dict) -> Dict:
        """Analyze stock price simulation results"""
        final_prices = simulation_results['final_prices']
        
        analysis = {
            'summary_statistics': {
                'mean': np.mean(final_prices),
                'median': np.median(final_prices),
                'std': np.std(final_prices),
                'skewness': stats.skew(final_prices),
                'kurtosis': stats.kurtosis(final_prices)
            },
            'risk_metrics': {
                'var_95': np.percentile(final_prices, 5),
                'var_99': np.percentile(final_prices, 1),
                'cvar_95': np.mean(final_prices[final_prices <= np.percentile(final_prices, 5)]),
                'cvar_99': np.mean(final_prices[final_prices <= np.percentile(final_prices, 1)])
            },
            'probability_analysis': {
                'prob_profit': np.mean(final_prices > simulation_results['parameters']['current_price']),
                'prob_loss': np.mean(final_prices < simulation_results['parameters']['current_price']),
                'prob_double': np.mean(final_prices > 2 * simulation_results['parameters']['current_price']),
                'prob_half': np.mean(final_prices < 0.5 * simulation_results['parameters']['current_price'])
            }
        }
        
        return analysis
    
    @staticmethod
    def analyze_portfolio_simulation(simulation_results: Dict) -> Dict:
        """Analyze portfolio simulation results"""
        final_values = simulation_results['final_values']
        
        analysis = {
            'summary_statistics': {
                'mean': np.mean(final_values),
                'median': np.median(final_values),
                'std': np.std(final_values),
                'skewness': stats.skew(final_values),
                'kurtosis': stats.kurtosis(final_values)
            },
            'risk_metrics': {
                'var_95': np.percentile(final_values, 5),
                'var_99': np.percentile(final_values, 1),
                'cvar_95': np.mean(final_values[final_values <= np.percentile(final_values, 5)]),
                'cvar_99': np.mean(final_values[final_values <= np.percentile(final_values, 1)]),
                'volatility': simulation_results['risk_metrics']['volatility'],
                'expected_return': simulation_results['risk_metrics']['expected_return']
            },
            'performance_metrics': {
                'total_return': np.mean(final_values) - 1,
                'annualized_return': (np.mean(final_values) ** (252 / simulation_results['parameters']['time_horizon'])) - 1,
                'sharpe_ratio': (np.mean(final_values) - 1) / np.std(final_values) if np.std(final_values) > 0 else 0
            }
        }
        
        return analysis
