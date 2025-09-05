"""
Portfolio optimization service.

Provides portfolio optimization algorithms including Markowitz mean-variance optimization,
Black-Litterman model, and risk parity optimization.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass

from scipy.optimize import minimize
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Portfolio optimization result."""
    weights: Dict[str, Decimal]
    expected_return: Decimal
    expected_risk: Decimal
    sharpe_ratio: Decimal
    efficient_frontier: List[Dict[str, float]]
    optimization_method: str
    constraints_used: Dict[str, Any]
    calculation_time: float


@dataclass
class OptimizationConstraints:
    """Portfolio optimization constraints."""
    max_weight: Decimal = Decimal('0.1')
    min_weight: Decimal = Decimal('0.01')
    sector_limits: Dict[str, Decimal] = None
    exclude_symbols: List[str] = None
    target_return: Optional[Decimal] = None
    max_risk: Optional[Decimal] = None
    rebalance_threshold: Decimal = Decimal('0.05')


class PortfolioOptimizer:
    """Portfolio optimization engine."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """Initialize optimizer with risk-free rate."""
        self.risk_free_rate = risk_free_rate
    
    def optimize_markowitz(
        self, 
        expected_returns: Dict[str, float],
        covariance_matrix: np.ndarray,
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """Optimize portfolio using Markowitz mean-variance optimization."""
        symbols = list(expected_returns.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return self._empty_optimization_result()
        
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
        
        # Add target return constraint if specified
        if constraints.target_return:
            constraints_list.append({
                'type': 'eq', 
                'fun': lambda x: np.dot(x, mu) - float(constraints.target_return)
            })
        
        # Add risk constraint if specified
        if constraints.max_risk:
            constraints_list.append({
                'type': 'ineq',
                'fun': lambda x: float(constraints.max_risk) - np.sqrt(np.dot(x.T, np.dot(covariance_matrix, x)))
            })
        
        # Bounds
        bounds = [
            (float(constraints.min_weight), float(constraints.max_weight)) 
            for _ in range(n_assets)
        ]
        
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
                
                # Calculate efficient frontier
                efficient_frontier = self._calculate_efficient_frontier(mu, covariance_matrix, 50)
                
                return OptimizationResult(
                    weights={symbols[i]: Decimal(str(optimal_weights[i])) for i in range(n_assets)},
                    expected_return=Decimal(str(portfolio_return)),
                    expected_risk=Decimal(str(portfolio_risk)),
                    sharpe_ratio=Decimal(str(sharpe_ratio)),
                    efficient_frontier=efficient_frontier,
                    optimization_method='markowitz',
                    constraints_used=constraints.__dict__,
                    calculation_time=result.fun
                )
        except Exception as e:
            logger.error(f"Markowitz optimization failed: {e}")
        
        return self._empty_optimization_result()
    
    def optimize_black_litterman(
        self, 
        market_caps: Dict[str, float],
        covariance_matrix: np.ndarray,
        views: Dict[str, float],
        view_confidences: Dict[str, float],
        risk_aversion: float = 3.0
    ) -> OptimizationResult:
        """Optimize portfolio using Black-Litterman model."""
        symbols = list(market_caps.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return self._empty_optimization_result()
        
        try:
            # Calculate market capitalization weights
            total_market_cap = sum(market_caps.values())
            market_weights = np.array([market_caps[symbol] / total_market_cap for symbol in symbols])
            
            # Calculate implied equilibrium returns
            implied_returns = risk_aversion * np.dot(covariance_matrix, market_weights)
            
            # Create view matrix and view returns
            view_matrix = np.zeros((len(views), n_assets))
            view_returns = np.zeros(len(views))
            view_confidences_array = np.zeros(len(views))
            
            for i, (symbol, view_return) in enumerate(views.items()):
                if symbol in symbols:
                    symbol_index = symbols.index(symbol)
                    view_matrix[i, symbol_index] = 1.0
                    view_returns[i] = view_return
                    view_confidences_array[i] = view_confidences.get(symbol, 0.5)
            
            # Calculate uncertainty matrix
            tau = 0.05  # Scaling factor
            uncertainty_matrix = np.diag(view_confidences_array)
            
            # Black-Litterman formula
            # P^T * Omega^-1 * P + (tau * Sigma)^-1
            bl_covariance = np.linalg.inv(
                np.dot(np.dot(view_matrix.T, np.linalg.inv(uncertainty_matrix)), view_matrix) + 
                np.linalg.inv(tau * covariance_matrix)
            )
            
            # Black-Litterman expected returns
            bl_returns = np.dot(bl_covariance, 
                np.dot(np.dot(view_matrix.T, np.linalg.inv(uncertainty_matrix)), view_returns) +
                np.dot(np.linalg.inv(tau * covariance_matrix), implied_returns)
            )
            
            # Optimize using Markowitz with BL returns
            constraints = OptimizationConstraints()
            return self.optimize_markowitz(
                {symbols[i]: bl_returns[i] for i in range(n_assets)},
                bl_covariance,
                constraints
            )
            
        except Exception as e:
            logger.error(f"Black-Litterman optimization failed: {e}")
            return self._empty_optimization_result()
    
    def optimize_risk_parity(
        self, 
        covariance_matrix: np.ndarray,
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """Optimize portfolio using risk parity approach."""
        n_assets = covariance_matrix.shape[0]
        
        if n_assets == 0:
            return self._empty_optimization_result()
        
        try:
            # Risk parity objective: minimize sum of squared differences in risk contributions
            def risk_parity_objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
                marginal_contributions = np.dot(covariance_matrix, weights)
                risk_contributions = weights * marginal_contributions / portfolio_variance
                
                # Calculate sum of squared differences from equal risk contribution
                target_risk_contribution = 1.0 / n_assets
                return np.sum((risk_contributions - target_risk_contribution) ** 2)
            
            # Constraints
            constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
            
            # Bounds
            bounds = [
                (float(constraints.min_weight), float(constraints.max_weight)) 
                for _ in range(n_assets)
            ]
            
            # Initial guess
            x0 = np.array([1/n_assets] * n_assets)
            
            result = minimize(
                risk_parity_objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate portfolio metrics
                portfolio_variance = np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights))
                portfolio_risk = np.sqrt(portfolio_variance)
                
                # For risk parity, we don't have expected returns, so we'll use a placeholder
                portfolio_return = self.risk_free_rate  # Conservative estimate
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
                
                return OptimizationResult(
                    weights={f"Asset_{i}": Decimal(str(optimal_weights[i])) for i in range(n_assets)},
                    expected_return=Decimal(str(portfolio_return)),
                    expected_risk=Decimal(str(portfolio_risk)),
                    sharpe_ratio=Decimal(str(sharpe_ratio)),
                    efficient_frontier=[],
                    optimization_method='risk_parity',
                    constraints_used=constraints.__dict__,
                    calculation_time=result.fun
                )
                
        except Exception as e:
            logger.error(f"Risk parity optimization failed: {e}")
        
        return self._empty_optimization_result()
    
    def optimize_equal_weight(
        self, 
        symbols: List[str],
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """Optimize portfolio using equal weight approach."""
        n_assets = len(symbols)
        
        if n_assets == 0:
            return self._empty_optimization_result()
        
        # Equal weights
        weight = 1.0 / n_assets
        weights = {symbol: Decimal(str(weight)) for symbol in symbols}
        
        # Placeholder metrics (would need actual data for real calculations)
        expected_return = Decimal(str(self.risk_free_rate + 0.05))  # 5% excess return
        expected_risk = Decimal('0.15')  # 15% volatility
        sharpe_ratio = (expected_return - Decimal(str(self.risk_free_rate))) / expected_risk
        
        return OptimizationResult(
            weights=weights,
            expected_return=expected_return,
            expected_risk=expected_risk,
            sharpe_ratio=sharpe_ratio,
            efficient_frontier=[],
            optimization_method='equal_weight',
            constraints_used=constraints.__dict__,
            calculation_time=0.0
        )
    
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
    
    def calculate_portfolio_metrics(
        self, 
        weights: Dict[str, Decimal],
        expected_returns: Dict[str, float],
        covariance_matrix: np.ndarray
    ) -> Dict[str, float]:
        """Calculate portfolio metrics for given weights."""
        symbols = list(weights.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return {}
        
        # Convert weights to numpy array
        weight_array = np.array([float(weights[symbol]) for symbol in symbols])
        mu = np.array([expected_returns[symbol] for symbol in symbols])
        
        # Calculate portfolio metrics
        portfolio_return = np.dot(weight_array, mu)
        portfolio_variance = np.dot(weight_array.T, np.dot(covariance_matrix, weight_array))
        portfolio_risk = np.sqrt(portfolio_variance)
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_risk
        
        return {
            'expected_return': float(portfolio_return),
            'expected_risk': float(portfolio_risk),
            'sharpe_ratio': float(sharpe_ratio),
            'variance': float(portfolio_variance)
        }
    
    def calculate_risk_contribution(
        self, 
        weights: Dict[str, Decimal],
        covariance_matrix: np.ndarray
    ) -> Dict[str, float]:
        """Calculate risk contribution of each asset."""
        symbols = list(weights.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return {}
        
        # Convert weights to numpy array
        weight_array = np.array([float(weights[symbol]) for symbol in symbols])
        
        # Calculate portfolio variance
        portfolio_variance = np.dot(weight_array.T, np.dot(covariance_matrix, weight_array))
        
        # Calculate marginal contributions
        marginal_contributions = np.dot(covariance_matrix, weight_array)
        
        # Calculate risk contributions
        risk_contributions = weight_array * marginal_contributions / portfolio_variance
        
        return {symbols[i]: float(risk_contributions[i]) for i in range(n_assets)}
    
    def calculate_correlation_matrix(self, returns_data: Dict[str, List[float]]) -> np.ndarray:
        """Calculate correlation matrix from returns data."""
        if not returns_data:
            return np.array([])
        
        # Convert to DataFrame
        df = pd.DataFrame(returns_data)
        
        # Calculate correlation matrix
        correlation_matrix = df.corr().values
        
        return correlation_matrix
    
    def calculate_covariance_matrix(self, returns_data: Dict[str, List[float]]) -> np.ndarray:
        """Calculate covariance matrix from returns data."""
        if not returns_data:
            return np.array([])
        
        # Convert to DataFrame
        df = pd.DataFrame(returns_data)
        
        # Calculate covariance matrix
        covariance_matrix = df.cov().values
        
        return covariance_matrix
    
    def calculate_expected_returns(
        self, 
        returns_data: Dict[str, List[float]], 
        method: str = "historical"
    ) -> Dict[str, float]:
        """Calculate expected returns using specified method."""
        if not returns_data:
            return {}
        
        expected_returns = {}
        
        for symbol, returns in returns_data.items():
            if method == "historical":
                # Use historical average
                expected_returns[symbol] = np.mean(returns) * 252  # Annualized
            elif method == "capm":
                # CAPM model (would need market data)
                # For now, use historical average
                expected_returns[symbol] = np.mean(returns) * 252
            else:
                # Default to historical
                expected_returns[symbol] = np.mean(returns) * 252
        
        return expected_returns
    
    def _calculate_efficient_frontier(
        self, 
        mu: np.ndarray, 
        sigma: np.ndarray, 
        num_portfolios: int
    ) -> List[Dict[str, float]]:
        """Calculate efficient frontier points."""
        n_assets = len(mu)
        efficient_portfolios = []
        
        # Generate target returns
        min_return = np.min(mu)
        max_return = np.max(mu)
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        for target_return in target_returns:
            try:
                # Minimize variance for given return
                def objective(weights):
                    return np.dot(weights.T, np.dot(sigma, weights))
                
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x: np.dot(x, mu) - target_return}
                ]
                
                bounds = [(0, 1) for _ in range(n_assets)]
                x0 = np.array([1/n_assets] * n_assets)
                
                result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
                
                if result.success:
                    portfolio_risk = np.sqrt(result.fun)
                    efficient_portfolios.append({
                        'return': float(target_return),
                        'risk': float(portfolio_risk)
                    })
            except:
                continue
        
        return efficient_portfolios
    
    def _empty_optimization_result(self) -> OptimizationResult:
        """Return empty optimization result."""
        return OptimizationResult(
            weights={},
            expected_return=Decimal('0'),
            expected_risk=Decimal('0'),
            sharpe_ratio=Decimal('0'),
            efficient_frontier=[],
            optimization_method='none',
            constraints_used={},
            calculation_time=0.0
        )
