"""
Portfolio financial calculations engine.

Provides sophisticated financial calculations for portfolio management,
risk analysis, and optimization.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data class."""
    total_return: Decimal
    annualized_return: Decimal
    volatility: Decimal
    sharpe_ratio: Optional[Decimal]
    sortino_ratio: Optional[Decimal]
    calmar_ratio: Optional[Decimal]
    max_drawdown: Decimal
    max_drawdown_duration: int
    win_rate: Decimal
    profit_factor: Decimal
    var_95: Optional[Decimal]
    var_99: Optional[Decimal]
    cvar_95: Optional[Decimal]
    cvar_99: Optional[Decimal]


@dataclass
class RiskMetrics:
    """Risk metrics data class."""
    beta: Decimal
    alpha: Decimal
    tracking_error: Decimal
    information_ratio: Decimal
    treynor_ratio: Decimal
    jensen_alpha: Decimal
    downside_deviation: Decimal
    upside_capture: Decimal
    downside_capture: Decimal
    correlation_with_benchmark: Decimal


class PortfolioCalculator:
    """Portfolio financial calculations engine."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """Initialize calculator with risk-free rate."""
        self.risk_free_rate = risk_free_rate
    
    def calculate_portfolio_value(self, holdings: List[Dict]) -> Decimal:
        """Calculate total portfolio value."""
        total_value = Decimal('0')
        for holding in holdings:
            shares = Decimal(str(holding.get('shares', 0)))
            current_price = Decimal(str(holding.get('current_price', 0)))
            total_value += shares * current_price
        return total_value
    
    def calculate_portfolio_returns(self, portfolio_values: List[Decimal]) -> List[Decimal]:
        """Calculate portfolio returns from values."""
        if len(portfolio_values) < 2:
            return []
        
        returns = []
        for i in range(1, len(portfolio_values)):
            prev_value = float(portfolio_values[i-1])
            curr_value = float(portfolio_values[i])
            if prev_value > 0:
                ret = (curr_value - prev_value) / prev_value
                returns.append(Decimal(str(ret)))
        return returns
    
    def calculate_performance_metrics(
        self, 
        returns: List[Decimal], 
        portfolio_values: List[Decimal],
        benchmark_returns: Optional[List[Decimal]] = None
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        if not returns:
            return self._empty_performance_metrics()
        
        returns_array = np.array([float(r) for r in returns])
        
        # Basic metrics
        total_return = self._calculate_total_return(portfolio_values)
        annualized_return = self._calculate_annualized_return(returns_array)
        volatility = self._calculate_volatility(returns_array)
        
        # Risk-adjusted metrics
        sharpe_ratio = self._calculate_sharpe_ratio(returns_array)
        sortino_ratio = self._calculate_sortino_ratio(returns_array)
        
        # Drawdown metrics
        max_drawdown, max_drawdown_duration = self._calculate_max_drawdown(portfolio_values)
        calmar_ratio = self._calculate_calmar_ratio(annualized_return, max_drawdown)
        
        # Win rate and profit factor
        win_rate = self._calculate_win_rate(returns_array)
        profit_factor = self._calculate_profit_factor(returns_array)
        
        # VaR and CVaR
        var_95, var_99 = self._calculate_var(returns_array)
        cvar_95, cvar_99 = self._calculate_cvar(returns_array)
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            win_rate=win_rate,
            profit_factor=profit_factor,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99
        )
    
    def calculate_risk_metrics(
        self, 
        portfolio_returns: List[Decimal], 
        benchmark_returns: List[Decimal]
    ) -> RiskMetrics:
        """Calculate risk metrics relative to benchmark."""
        if not portfolio_returns or not benchmark_returns:
            return self._empty_risk_metrics()
        
        portfolio_array = np.array([float(r) for r in portfolio_returns])
        benchmark_array = np.array([float(r) for r in benchmark_returns])
        
        # Ensure same length
        min_length = min(len(portfolio_array), len(benchmark_array))
        portfolio_array = portfolio_array[:min_length]
        benchmark_array = benchmark_array[:min_length]
        
        # Beta and Alpha
        beta = self._calculate_beta(portfolio_array, benchmark_array)
        alpha = self._calculate_alpha(portfolio_array, benchmark_array, beta)
        
        # Tracking error and information ratio
        tracking_error = self._calculate_tracking_error(portfolio_array, benchmark_array)
        information_ratio = self._calculate_information_ratio(portfolio_array, benchmark_array, tracking_error)
        
        # Treynor ratio
        treynor_ratio = self._calculate_treynor_ratio(portfolio_array, beta)
        
        # Jensen's alpha
        jensen_alpha = self._calculate_jensen_alpha(portfolio_array, benchmark_array)
        
        # Downside deviation
        downside_deviation = self._calculate_downside_deviation(portfolio_array)
        
        # Capture ratios
        upside_capture, downside_capture = self._calculate_capture_ratios(portfolio_array, benchmark_array)
        
        # Correlation
        correlation = self._calculate_correlation(portfolio_array, benchmark_array)
        
        return RiskMetrics(
            beta=beta,
            alpha=alpha,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            treynor_ratio=treynor_ratio,
            jensen_alpha=jensen_alpha,
            downside_deviation=downside_deviation,
            upside_capture=upside_capture,
            downside_capture=downside_capture,
            correlation_with_benchmark=correlation
        )
    
    def calculate_allocation_metrics(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio allocation metrics."""
        total_value = self.calculate_portfolio_value(holdings)
        if total_value == 0:
            return {}
        
        # Sector allocation
        sector_allocation = {}
        industry_allocation = {}
        market_cap_allocation = {}
        
        # Top holdings
        top_holdings = []
        
        for holding in holdings:
            shares = Decimal(str(holding.get('shares', 0)))
            current_price = Decimal(str(holding.get('current_price', 0)))
            market_value = shares * current_price
            weight = market_value / total_value
            
            # Sector allocation
            sector = holding.get('sector', 'Unknown')
            sector_allocation[sector] = sector_allocation.get(sector, Decimal('0')) + weight
            
            # Industry allocation
            industry = holding.get('industry', 'Unknown')
            industry_allocation[industry] = industry_allocation.get(industry, Decimal('0')) + weight
            
            # Market cap allocation
            market_cap = holding.get('market_cap', 'Unknown')
            market_cap_allocation[market_cap] = market_cap_allocation.get(market_cap, Decimal('0')) + weight
            
            # Top holdings
            top_holdings.append({
                'symbol': holding.get('symbol'),
                'name': holding.get('name'),
                'weight': weight,
                'market_value': market_value
            })
        
        # Sort top holdings by weight
        top_holdings.sort(key=lambda x: x['weight'], reverse=True)
        
        # Calculate concentration risk (Herfindahl-Hirschman Index)
        concentration_risk = sum(w**2 for w in sector_allocation.values())
        
        # Calculate diversification ratio
        diversification_ratio = 1 / concentration_risk if concentration_risk > 0 else Decimal('0')
        
        return {
            'sector_allocation': sector_allocation,
            'industry_allocation': industry_allocation,
            'market_cap_allocation': market_cap_allocation,
            'top_holdings': top_holdings[:10],  # Top 10 holdings
            'concentration_risk': concentration_risk,
            'diversification_ratio': diversification_ratio
        }
    
    def optimize_portfolio(
        self, 
        expected_returns: Dict[str, float],
        covariance_matrix: np.ndarray,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize portfolio using Markowitz mean-variance optimization."""
        symbols = list(expected_returns.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return {}
        
        # Convert to numpy arrays
        mu = np.array([expected_returns[symbol] for symbol in symbols])
        
        # Objective function (negative Sharpe ratio for minimization)
        def objective(weights):
            portfolio_return = np.dot(weights, mu)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            if portfolio_risk == 0:
                return -float('inf')
            return -(portfolio_return - self.risk_free_rate) / portfolio_risk
        
        # Constraints
        constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1
        
        # Bounds
        max_weight = constraints.get('max_weight', 0.1)
        min_weight = constraints.get('min_weight', 0.01)
        bounds = [(min_weight, max_weight) for _ in range(n_assets)]
        
        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)
        
        try:
            result = minimize(
                objective, 
                x0, 
                method='SLSQP', 
                bounds=bounds, 
                constraints=constraints_list,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = result.x
                portfolio_return = np.dot(optimal_weights, mu)
                portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
                
                return {
                    'weights': {symbols[i]: Decimal(str(optimal_weights[i])) for i in range(n_assets)},
                    'expected_return': Decimal(str(portfolio_return)),
                    'expected_risk': Decimal(str(portfolio_risk)),
                    'sharpe_ratio': Decimal(str(sharpe_ratio)),
                    'optimization_method': 'markowitz',
                    'calculation_time': result.fun
                }
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
        
        return {}
    
    def calculate_efficient_frontier(
        self, 
        expected_returns: Dict[str, float],
        covariance_matrix: np.ndarray,
        num_portfolios: int = 100
    ) -> List[Dict[str, float]]:
        """Calculate efficient frontier."""
        symbols = list(expected_returns.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return []
        
        mu = np.array([expected_returns[symbol] for symbol in symbols])
        
        # Generate random portfolios
        portfolios = []
        for _ in range(num_portfolios):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            portfolio_return = np.dot(weights, mu)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            
            portfolios.append({
                'return': float(portfolio_return),
                'risk': float(portfolio_risk),
                'weights': {symbols[i]: float(weights[i]) for i in range(n_assets)}
            })
        
        # Sort by risk
        portfolios.sort(key=lambda x: x['risk'])
        
        return portfolios
    
    def calculate_rebalancing_recommendations(
        self, 
        current_weights: Dict[str, Decimal],
        target_weights: Dict[str, Decimal],
        portfolio_value: Decimal,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate rebalancing recommendations."""
        recommendations = []
        
        # Get all symbols
        all_symbols = set(current_weights.keys()) | set(target_weights.keys())
        
        for symbol in all_symbols:
            current_weight = current_weights.get(symbol, Decimal('0'))
            target_weight = target_weights.get(symbol, Decimal('0'))
            weight_difference = target_weight - current_weight
            
            # Only recommend trades above threshold
            threshold = constraints.get('rebalance_threshold', Decimal('0.05'))
            if abs(weight_difference) > threshold:
                # Calculate shares to trade
                current_price = Decimal('100')  # This should come from market data
                current_shares = (current_weight * portfolio_value) / current_price
                target_shares = (target_weight * portfolio_value) / current_price
                shares_to_trade = target_shares - current_shares
                
                trade_type = "buy" if shares_to_trade > 0 else "sell"
                estimated_cost = abs(shares_to_trade) * current_price
                
                # Calculate priority based on weight difference
                priority = min(5, max(1, int(abs(weight_difference) * 20)))
                
                recommendations.append({
                    'symbol': symbol,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'weight_difference': weight_difference,
                    'current_shares': current_shares,
                    'target_shares': target_shares,
                    'shares_to_trade': shares_to_trade,
                    'trade_type': trade_type,
                    'estimated_cost': estimated_cost,
                    'priority': priority
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations
    
    # Private helper methods
    def _calculate_total_return(self, portfolio_values: List[Decimal]) -> Decimal:
        """Calculate total return."""
        if len(portfolio_values) < 2:
            return Decimal('0')
        
        initial_value = float(portfolio_values[0])
        final_value = float(portfolio_values[-1])
        
        if initial_value == 0:
            return Decimal('0')
        
        return Decimal(str((final_value - initial_value) / initial_value))
    
    def _calculate_annualized_return(self, returns: np.ndarray) -> Decimal:
        """Calculate annualized return."""
        if len(returns) == 0:
            return Decimal('0')
        
        # Assuming daily returns
        total_return = np.prod(1 + returns) - 1
        annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
        
        return Decimal(str(annualized_return))
    
    def _calculate_volatility(self, returns: np.ndarray) -> Decimal:
        """Calculate annualized volatility."""
        if len(returns) == 0:
            return Decimal('0')
        
        # Assuming daily returns
        volatility = np.std(returns) * np.sqrt(252)
        return Decimal(str(volatility))
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray) -> Optional[Decimal]:
        """Calculate Sharpe ratio."""
        if len(returns) == 0:
            return None
        
        excess_returns = returns - self.risk_free_rate / 252
        if np.std(excess_returns) == 0:
            return None
        
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return Decimal(str(sharpe_ratio))
    
    def _calculate_sortino_ratio(self, returns: np.ndarray) -> Optional[Decimal]:
        """Calculate Sortino ratio."""
        if len(returns) == 0:
            return None
        
        excess_returns = returns - self.risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return None
        
        sortino_ratio = np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(252)
        return Decimal(str(sortino_ratio))
    
    def _calculate_max_drawdown(self, portfolio_values: List[Decimal]) -> Tuple[Decimal, int]:
        """Calculate maximum drawdown and duration."""
        if len(portfolio_values) < 2:
            return Decimal('0'), 0
        
        values = np.array([float(v) for v in portfolio_values])
        peak = np.maximum.accumulate(values)
        drawdown = (values - peak) / peak
        
        max_drawdown = Decimal(str(np.min(drawdown)))
        
        # Calculate duration
        drawdown_duration = 0
        current_duration = 0
        for dd in drawdown:
            if dd < 0:
                current_duration += 1
                drawdown_duration = max(drawdown_duration, current_duration)
            else:
                current_duration = 0
        
        return max_drawdown, drawdown_duration
    
    def _calculate_calmar_ratio(self, annualized_return: Decimal, max_drawdown: Decimal) -> Optional[Decimal]:
        """Calculate Calmar ratio."""
        if max_drawdown == 0:
            return None
        
        return annualized_return / abs(max_drawdown)
    
    def _calculate_win_rate(self, returns: np.ndarray) -> Decimal:
        """Calculate win rate."""
        if len(returns) == 0:
            return Decimal('0')
        
        positive_returns = np.sum(returns > 0)
        return Decimal(str(positive_returns / len(returns)))
    
    def _calculate_profit_factor(self, returns: np.ndarray) -> Decimal:
        """Calculate profit factor."""
        if len(returns) == 0:
            return Decimal('0')
        
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return Decimal('inf') if len(positive_returns) > 0 else Decimal('0')
        
        gross_profit = np.sum(positive_returns)
        gross_loss = abs(np.sum(negative_returns))
        
        if gross_loss == 0:
            return Decimal('inf') if gross_profit > 0 else Decimal('0')
        
        return Decimal(str(gross_profit / gross_loss))
    
    def _calculate_var(self, returns: np.ndarray) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Calculate Value at Risk."""
        if len(returns) == 0:
            return None, None
        
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        return Decimal(str(var_95)), Decimal(str(var_99))
    
    def _calculate_cvar(self, returns: np.ndarray) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Calculate Conditional Value at Risk."""
        if len(returns) == 0:
            return None, None
        
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        cvar_95 = np.mean(returns[returns <= var_95])
        cvar_99 = np.mean(returns[returns <= var_99])
        
        return Decimal(str(cvar_95)), Decimal(str(cvar_99))
    
    def _calculate_beta(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> Decimal:
        """Calculate beta."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return Decimal('0')
        
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        
        if benchmark_variance == 0:
            return Decimal('0')
        
        beta = covariance / benchmark_variance
        return Decimal(str(beta))
    
    def _calculate_alpha(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray, beta: Decimal) -> Decimal:
        """Calculate alpha."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return Decimal('0')
        
        portfolio_mean = np.mean(portfolio_returns)
        benchmark_mean = np.mean(benchmark_returns)
        
        alpha = portfolio_mean - (self.risk_free_rate / 252 + float(beta) * (benchmark_mean - self.risk_free_rate / 252))
        return Decimal(str(alpha * 252))  # Annualized
    
    def _calculate_tracking_error(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> Decimal:
        """Calculate tracking error."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return Decimal('0')
        
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = np.std(excess_returns) * np.sqrt(252)
        return Decimal(str(tracking_error))
    
    def _calculate_information_ratio(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray, tracking_error: Decimal) -> Decimal:
        """Calculate information ratio."""
        if float(tracking_error) == 0:
            return Decimal('0')
        
        excess_returns = portfolio_returns - benchmark_returns
        mean_excess_return = np.mean(excess_returns) * 252  # Annualized
        
        return Decimal(str(mean_excess_return / float(tracking_error)))
    
    def _calculate_treynor_ratio(self, portfolio_returns: np.ndarray, beta: Decimal) -> Decimal:
        """Calculate Treynor ratio."""
        if float(beta) == 0:
            return Decimal('0')
        
        excess_return = np.mean(portfolio_returns) * 252 - self.risk_free_rate
        return Decimal(str(excess_return / float(beta)))
    
    def _calculate_jensen_alpha(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> Decimal:
        """Calculate Jensen's alpha."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return Decimal('0')
        
        # Simple alpha calculation
        portfolio_mean = np.mean(portfolio_returns)
        benchmark_mean = np.mean(benchmark_returns)
        
        alpha = portfolio_mean - benchmark_mean
        return Decimal(str(alpha * 252))  # Annualized
    
    def _calculate_downside_deviation(self, returns: np.ndarray) -> Decimal:
        """Calculate downside deviation."""
        if len(returns) == 0:
            return Decimal('0')
        
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return Decimal('0')
        
        downside_deviation = np.std(downside_returns) * np.sqrt(252)
        return Decimal(str(downside_deviation))
    
    def _calculate_capture_ratios(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> Tuple[Decimal, Decimal]:
        """Calculate upside and downside capture ratios."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return Decimal('0'), Decimal('0')
        
        # Upside capture
        portfolio_up = portfolio_returns[benchmark_returns > 0]
        benchmark_up = benchmark_returns[benchmark_returns > 0]
        
        if len(portfolio_up) > 0 and len(benchmark_up) > 0:
            upside_capture = np.mean(portfolio_up) / np.mean(benchmark_up)
        else:
            upside_capture = 0
        
        # Downside capture
        portfolio_down = portfolio_returns[benchmark_returns < 0]
        benchmark_down = benchmark_returns[benchmark_returns < 0]
        
        if len(portfolio_down) > 0 and len(benchmark_down) > 0:
            downside_capture = np.mean(portfolio_down) / np.mean(benchmark_down)
        else:
            downside_capture = 0
        
        return Decimal(str(upside_capture)), Decimal(str(downside_capture))
    
    def _calculate_correlation(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> Decimal:
        """Calculate correlation with benchmark."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return Decimal('0')
        
        correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]
        return Decimal(str(correlation))
    
    def _empty_performance_metrics(self) -> PerformanceMetrics:
        """Return empty performance metrics."""
        return PerformanceMetrics(
            total_return=Decimal('0'),
            annualized_return=Decimal('0'),
            volatility=Decimal('0'),
            sharpe_ratio=None,
            sortino_ratio=None,
            calmar_ratio=None,
            max_drawdown=Decimal('0'),
            max_drawdown_duration=0,
            win_rate=Decimal('0'),
            profit_factor=Decimal('0'),
            var_95=None,
            var_99=None,
            cvar_95=None,
            cvar_99=None
        )
    
    def _empty_risk_metrics(self) -> RiskMetrics:
        """Return empty risk metrics."""
        return RiskMetrics(
            beta=Decimal('0'),
            alpha=Decimal('0'),
            tracking_error=Decimal('0'),
            information_ratio=Decimal('0'),
            treynor_ratio=Decimal('0'),
            jensen_alpha=Decimal('0'),
            downside_deviation=Decimal('0'),
            upside_capture=Decimal('0'),
            downside_capture=Decimal('0'),
            correlation_with_benchmark=Decimal('0')
        )
