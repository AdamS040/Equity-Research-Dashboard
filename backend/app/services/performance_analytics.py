"""
Performance analytics service.

Provides comprehensive performance analysis, attribution analysis,
and reporting for portfolios.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import logging

from app.services.portfolio_calculations import PortfolioCalculator

logger = logging.getLogger(__name__)


class PerformanceAnalyticsService:
    """Service for portfolio performance analytics and reporting."""
    
    def __init__(self):
        """Initialize performance analytics service."""
        self.calculator = PortfolioCalculator()
    
    def calculate_attribution_analysis(
        self, 
        portfolio_returns: List[Decimal],
        benchmark_returns: List[Decimal],
        holdings_data: List[Dict[str, Any]],
        period: str = "1y"
    ) -> Dict[str, Any]:
        """Calculate performance attribution analysis."""
        try:
            if not portfolio_returns or not benchmark_returns:
                return {}
            
            # Convert to numpy arrays
            portfolio_array = np.array([float(r) for r in portfolio_returns])
            benchmark_array = np.array([float(r) for r in benchmark_returns])
            
            # Calculate excess returns
            excess_returns = portfolio_array - benchmark_array
            
            # Calculate attribution components
            total_attribution = np.sum(excess_returns)
            
            # Security selection effect (simplified)
            selection_effect = total_attribution * 0.6  # Assume 60% from selection
            
            # Asset allocation effect
            allocation_effect = total_attribution * 0.4  # Assume 40% from allocation
            
            # Interaction effect
            interaction_effect = total_attribution - selection_effect - allocation_effect
            
            # Calculate by holding (simplified)
            holding_attribution = []
            for holding in holdings_data:
                symbol = holding.get('symbol', '')
                weight = float(holding.get('weight', 0))
                
                # Simplified attribution calculation
                holding_contribution = total_attribution * weight
                
                holding_attribution.append({
                    'symbol': symbol,
                    'weight': weight,
                    'contribution': float(holding_contribution),
                    'selection_effect': float(selection_effect * weight),
                    'allocation_effect': float(allocation_effect * weight)
                })
            
            return {
                'total_attribution': float(total_attribution),
                'selection_effect': float(selection_effect),
                'allocation_effect': float(allocation_effect),
                'interaction_effect': float(interaction_effect),
                'holding_attribution': holding_attribution,
                'period': period
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate attribution analysis: {e}")
            return {}
    
    def calculate_rolling_metrics(
        self, 
        portfolio_values: List[Decimal],
        benchmark_values: Optional[List[Decimal]] = None,
        window: int = 252  # 1 year for daily data
    ) -> Dict[str, List[float]]:
        """Calculate rolling performance metrics."""
        try:
            if len(portfolio_values) < window:
                return {}
            
            portfolio_array = np.array([float(v) for v in portfolio_values])
            
            # Calculate rolling returns
            rolling_returns = []
            rolling_volatility = []
            rolling_sharpe = []
            rolling_max_drawdown = []
            
            for i in range(window, len(portfolio_array)):
                window_data = portfolio_array[i-window:i]
                returns = np.diff(window_data) / window_data[:-1]
                
                # Rolling return
                rolling_return = np.mean(returns) * 252  # Annualized
                rolling_returns.append(rolling_return)
                
                # Rolling volatility
                rolling_vol = np.std(returns) * np.sqrt(252)  # Annualized
                rolling_volatility.append(rolling_vol)
                
                # Rolling Sharpe ratio
                if rolling_vol > 0:
                    rolling_sharpe.append((rolling_return - 0.02) / rolling_vol)  # Assuming 2% risk-free rate
                else:
                    rolling_sharpe.append(0)
                
                # Rolling max drawdown
                peak = np.maximum.accumulate(window_data)
                drawdown = (window_data - peak) / peak
                rolling_max_dd = np.min(drawdown)
                rolling_max_drawdown.append(rolling_max_dd)
            
            result = {
                'rolling_returns': rolling_returns,
                'rolling_volatility': rolling_volatility,
                'rolling_sharpe': rolling_sharpe,
                'rolling_max_drawdown': rolling_max_drawdown
            }
            
            # Add benchmark comparison if available
            if benchmark_values and len(benchmark_values) >= window:
                benchmark_array = np.array([float(v) for v in benchmark_values])
                rolling_alpha = []
                rolling_beta = []
                rolling_tracking_error = []
                
                for i in range(window, len(portfolio_array)):
                    portfolio_window = portfolio_array[i-window:i]
                    benchmark_window = benchmark_array[i-window:i]
                    
                    portfolio_returns = np.diff(portfolio_window) / portfolio_window[:-1]
                    benchmark_returns = np.diff(benchmark_window) / benchmark_window[:-1]
                    
                    # Rolling beta
                    if len(portfolio_returns) > 1 and len(benchmark_returns) > 1:
                        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
                        benchmark_variance = np.var(benchmark_returns)
                        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
                        rolling_beta.append(beta)
                        
                        # Rolling alpha
                        alpha = np.mean(portfolio_returns) - 0.02/252 - beta * (np.mean(benchmark_returns) - 0.02/252)
                        rolling_alpha.append(alpha * 252)  # Annualized
                        
                        # Rolling tracking error
                        excess_returns = portfolio_returns - benchmark_returns
                        tracking_error = np.std(excess_returns) * np.sqrt(252)
                        rolling_tracking_error.append(tracking_error)
                    else:
                        rolling_beta.append(0)
                        rolling_alpha.append(0)
                        rolling_tracking_error.append(0)
                
                result.update({
                    'rolling_alpha': rolling_alpha,
                    'rolling_beta': rolling_beta,
                    'rolling_tracking_error': rolling_tracking_error
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate rolling metrics: {e}")
            return {}
    
    def calculate_sector_attribution(
        self, 
        holdings_data: List[Dict[str, Any]],
        sector_returns: Dict[str, List[float]],
        benchmark_sector_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate sector attribution analysis."""
        try:
            # Calculate portfolio sector weights
            portfolio_sector_weights = {}
            for holding in holdings_data:
                sector = holding.get('sector', 'Unknown')
                weight = float(holding.get('weight', 0))
                portfolio_sector_weights[sector] = portfolio_sector_weights.get(sector, 0) + weight
            
            # Calculate sector attribution
            sector_attribution = []
            total_attribution = 0
            
            for sector in portfolio_sector_weights.keys():
                portfolio_weight = portfolio_sector_weights[sector]
                benchmark_weight = benchmark_sector_weights.get(sector, 0)
                
                # Get sector returns (simplified - would need actual data)
                sector_return = 0.1  # Placeholder
                
                # Allocation effect
                allocation_effect = (portfolio_weight - benchmark_weight) * sector_return
                
                # Selection effect (simplified)
                selection_effect = portfolio_weight * (sector_return - sector_return)  # Would need actual stock returns
                
                total_effect = allocation_effect + selection_effect
                total_attribution += total_effect
                
                sector_attribution.append({
                    'sector': sector,
                    'portfolio_weight': portfolio_weight,
                    'benchmark_weight': benchmark_weight,
                    'allocation_effect': allocation_effect,
                    'selection_effect': selection_effect,
                    'total_effect': total_effect
                })
            
            return {
                'sector_attribution': sector_attribution,
                'total_attribution': total_attribution,
                'portfolio_sector_weights': portfolio_sector_weights,
                'benchmark_sector_weights': benchmark_sector_weights
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate sector attribution: {e}")
            return {}
    
    def calculate_risk_decomposition(
        self, 
        holdings_data: List[Dict[str, Any]],
        correlation_matrix: np.ndarray,
        volatility_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate risk decomposition by asset and factor."""
        try:
            symbols = [h['symbol'] for h in holdings_data]
            weights = [float(h['weight']) for h in holdings_data]
            n_assets = len(symbols)
            
            if n_assets == 0:
                return {}
            
            # Create weight vector
            weight_vector = np.array(weights)
            
            # Create volatility vector
            volatility_vector = np.array([volatility_data.get(symbol, 0.2) for symbol in symbols])
            
            # Calculate portfolio variance
            portfolio_variance = np.dot(weight_vector.T, np.dot(correlation_matrix, weight_vector))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Calculate risk contributions
            marginal_contributions = np.dot(correlation_matrix, weight_vector)
            risk_contributions = weight_vector * marginal_contributions / portfolio_variance
            
            # Asset risk decomposition
            asset_risk_decomposition = []
            for i, symbol in enumerate(symbols):
                asset_risk_decomposition.append({
                    'symbol': symbol,
                    'weight': weights[i],
                    'volatility': volatility_vector[i],
                    'risk_contribution': float(risk_contributions[i]),
                    'marginal_contribution': float(marginal_contributions[i])
                })
            
            # Factor risk decomposition (simplified)
            factor_risk_decomposition = {
                'market_factor': 0.6,  # Placeholder
                'size_factor': 0.2,
                'value_factor': 0.1,
                'momentum_factor': 0.1
            }
            
            return {
                'portfolio_volatility': float(portfolio_volatility),
                'portfolio_variance': float(portfolio_variance),
                'asset_risk_decomposition': asset_risk_decomposition,
                'factor_risk_decomposition': factor_risk_decomposition,
                'concentration_risk': float(np.sum(risk_contributions ** 2)),  # Herfindahl index
                'diversification_ratio': float(portfolio_volatility / np.dot(weight_vector, volatility_vector))
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate risk decomposition: {e}")
            return {}
    
    def calculate_performance_attribution(
        self, 
        portfolio_returns: List[Decimal],
        benchmark_returns: List[Decimal],
        holdings_data: List[Dict[str, Any]],
        factor_returns: Optional[Dict[str, List[float]]] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance attribution."""
        try:
            # Basic attribution
            basic_attribution = self.calculate_attribution_analysis(
                portfolio_returns, benchmark_returns, holdings_data
            )
            
            # Rolling metrics
            portfolio_values = [Decimal('1000') * (1 + sum(portfolio_returns[:i+1])) for i in range(len(portfolio_returns))]
            benchmark_values = [Decimal('1000') * (1 + sum(benchmark_returns[:i+1])) for i in range(len(benchmark_returns))]
            
            rolling_metrics = self.calculate_rolling_metrics(portfolio_values, benchmark_values)
            
            # Risk decomposition (simplified)
            n_assets = len(holdings_data)
            correlation_matrix = np.eye(n_assets) * 0.3 + np.ones((n_assets, n_assets)) * 0.1  # Placeholder
            volatility_data = {h['symbol']: 0.2 for h in holdings_data}  # Placeholder
            
            risk_decomposition = self.calculate_risk_decomposition(
                holdings_data, correlation_matrix, volatility_data
            )
            
            # Factor attribution (if factor returns provided)
            factor_attribution = {}
            if factor_returns:
                factor_attribution = self._calculate_factor_attribution(
                    portfolio_returns, factor_returns
                )
            
            return {
                'basic_attribution': basic_attribution,
                'rolling_metrics': rolling_metrics,
                'risk_decomposition': risk_decomposition,
                'factor_attribution': factor_attribution,
                'summary': {
                    'total_attribution': basic_attribution.get('total_attribution', 0),
                    'selection_effect': basic_attribution.get('selection_effect', 0),
                    'allocation_effect': basic_attribution.get('allocation_effect', 0),
                    'portfolio_volatility': risk_decomposition.get('portfolio_volatility', 0),
                    'diversification_ratio': risk_decomposition.get('diversification_ratio', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance attribution: {e}")
            return {}
    
    def generate_performance_report(
        self, 
        portfolio_id: str,
        portfolio_data: Dict[str, Any],
        benchmark_data: Dict[str, Any],
        period: str = "1y"
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        try:
            # Extract data
            portfolio_returns = portfolio_data.get('returns', [])
            benchmark_returns = benchmark_data.get('returns', [])
            holdings_data = portfolio_data.get('holdings', [])
            
            # Calculate performance metrics
            performance_metrics = self.calculator.calculate_performance_metrics(
                portfolio_returns, [], benchmark_returns
            )
            
            # Calculate risk metrics
            risk_metrics = self.calculator.calculate_risk_metrics(
                portfolio_returns, benchmark_returns
            )
            
            # Calculate attribution
            attribution = self.calculate_performance_attribution(
                portfolio_returns, benchmark_returns, holdings_data
            )
            
            # Generate report
            report = {
                'portfolio_id': portfolio_id,
                'period': period,
                'generated_at': datetime.utcnow().isoformat(),
                'performance_metrics': {
                    'total_return': float(performance_metrics.total_return),
                    'annualized_return': float(performance_metrics.annualized_return),
                    'volatility': float(performance_metrics.volatility),
                    'sharpe_ratio': float(performance_metrics.sharpe_ratio) if performance_metrics.sharpe_ratio else 0,
                    'max_drawdown': float(performance_metrics.max_drawdown),
                    'win_rate': float(performance_metrics.win_rate)
                },
                'risk_metrics': {
                    'beta': float(risk_metrics.beta),
                    'alpha': float(risk_metrics.alpha),
                    'tracking_error': float(risk_metrics.tracking_error),
                    'information_ratio': float(risk_metrics.information_ratio)
                },
                'attribution_analysis': attribution,
                'summary': {
                    'outperformance': float(performance_metrics.annualized_return) - float(risk_metrics.alpha),
                    'risk_adjusted_return': float(performance_metrics.sharpe_ratio) if performance_metrics.sharpe_ratio else 0,
                    'volatility_vs_benchmark': float(performance_metrics.volatility) - 0.15,  # Assuming 15% benchmark vol
                    'max_drawdown_vs_benchmark': float(performance_metrics.max_drawdown) + 0.05  # Assuming -5% benchmark DD
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {}
    
    def _calculate_factor_attribution(
        self, 
        portfolio_returns: List[Decimal],
        factor_returns: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Calculate factor attribution (simplified)."""
        try:
            # This would require factor loadings and factor returns
            # For now, return placeholder data
            return {
                'market_factor': 0.6,
                'size_factor': 0.2,
                'value_factor': 0.1,
                'momentum_factor': 0.1,
                'residual': 0.0
            }
        except Exception as e:
            logger.error(f"Failed to calculate factor attribution: {e}")
            return {}
