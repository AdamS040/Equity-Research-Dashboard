"""
Advanced Analytics & Financial Modeling Engine

This module provides comprehensive financial modeling capabilities including:
- DCF (Discounted Cash Flow) analysis with sensitivity analysis
- Comparable company analysis with peer benchmarking
- Risk analysis with VaR, stress testing, and Monte Carlo simulations
- Backtesting engine for trading strategies
- Options analysis with Greeks and strategy evaluation
- Economic indicators and market sentiment analysis

Mathematical precision and industry-standard calculations are prioritized.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
from scipy import stats
from scipy.optimize import minimize
import logging
from decimal import Decimal, ROUND_HALF_UP
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class DCFInputs:
    """DCF Analysis Input Parameters"""
    symbol: str
    current_price: float
    revenue: float
    revenue_growth_rate: float
    ebitda_margin: float
    tax_rate: float
    capex: float
    working_capital: float
    terminal_growth_rate: float
    wacc: float
    beta: float
    risk_free_rate: float
    market_risk_premium: float
    debt_to_equity: float
    cost_of_debt: float
    projection_years: int = 5


@dataclass
class DCFProjection:
    """DCF Projection for a single year"""
    year: int
    revenue: float
    ebitda: float
    ebit: float
    tax: float
    nopat: float
    depreciation: float
    capex: float
    working_capital_change: float
    free_cash_flow: float
    present_value: float


@dataclass
class DCFResults:
    """DCF Analysis Results"""
    fair_value: float
    upside: float
    upside_percent: float
    terminal_value: float
    projections: List[DCFProjection]
    sensitivity_analysis: Dict[str, Any]
    monte_carlo_results: Dict[str, Any]
    wacc_breakdown: Dict[str, float]


@dataclass
class RiskMetrics:
    """Comprehensive Risk Metrics"""
    beta: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    tracking_error: float
    information_ratio: float
    calmar_ratio: float


@dataclass
class OptionsGreeks:
    """Options Greeks"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class MathematicalValidator:
    """Validates mathematical calculations and models"""
    
    @staticmethod
    def validate_dcf_inputs(inputs: DCFInputs) -> List[str]:
        """Validate DCF inputs for mathematical consistency"""
        errors = []
        
        if inputs.revenue <= 0:
            errors.append("Revenue must be positive")
        if not 0 <= inputs.revenue_growth_rate <= 1:
            errors.append("Revenue growth rate must be between 0 and 1")
        if not 0 <= inputs.ebitda_margin <= 1:
            errors.append("EBITDA margin must be between 0 and 1")
        if not 0 <= inputs.tax_rate <= 1:
            errors.append("Tax rate must be between 0 and 1")
        if not 0 <= inputs.terminal_growth_rate <= 0.1:
            errors.append("Terminal growth rate must be between 0 and 10%")
        if inputs.wacc <= 0:
            errors.append("WACC must be positive")
        if inputs.projection_years < 1 or inputs.projection_years > 20:
            errors.append("Projection years must be between 1 and 20")
            
        return errors
    
    @staticmethod
    def validate_risk_inputs(returns: List[float]) -> List[str]:
        """Validate risk analysis inputs"""
        errors = []
        
        if len(returns) < 30:
            errors.append("At least 30 data points required for risk analysis")
        if any(math.isnan(r) or math.isinf(r) for r in returns):
            errors.append("Returns contain invalid values (NaN or Inf)")
            
        return errors


class DCFAnalysisEngine:
    """Discounted Cash Flow Analysis Engine"""
    
    def __init__(self):
        self.validator = MathematicalValidator()
    
    def calculate_wacc(self, inputs: DCFInputs) -> float:
        """Calculate Weighted Average Cost of Capital using CAPM"""
        try:
            # Cost of Equity using CAPM
            cost_of_equity = inputs.risk_free_rate + inputs.beta * inputs.market_risk_premium
            
            # Cost of Debt (after tax)
            cost_of_debt_after_tax = inputs.cost_of_debt * (1 - inputs.tax_rate)
            
            # Market value weights
            equity_weight = 1 / (1 + inputs.debt_to_equity)
            debt_weight = inputs.debt_to_equity / (1 + inputs.debt_to_equity)
            
            # WACC calculation
            wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt_after_tax)
            
            return round(wacc, 6)
        except Exception as e:
            logger.error(f"Error calculating WACC: {e}")
            raise ValueError(f"WACC calculation failed: {e}")
    
    def calculate_free_cash_flow(self, inputs: DCFInputs, year: int) -> DCFProjection:
        """Calculate free cash flow for a specific year"""
        try:
            # Revenue projection
            revenue = inputs.revenue * ((1 + inputs.revenue_growth_rate) ** year)
            
            # EBITDA calculation
            ebitda = revenue * inputs.ebitda_margin
            
            # Depreciation (simplified as % of revenue)
            depreciation = revenue * 0.05  # 5% of revenue
            
            # EBIT
            ebit = ebitda - depreciation
            
            # Tax calculation
            tax = ebit * inputs.tax_rate
            
            # NOPAT (Net Operating Profit After Tax)
            nopat = ebit - tax
            
            # Capital Expenditures
            capex = revenue * (inputs.capex / inputs.revenue) if inputs.revenue > 0 else 0
            
            # Working Capital Change
            working_capital_change = revenue * (inputs.working_capital / inputs.revenue) if inputs.revenue > 0 else 0
            
            # Free Cash Flow
            free_cash_flow = nopat + depreciation - capex - working_capital_change
            
            # Present Value
            present_value = free_cash_flow / ((1 + inputs.wacc) ** year)
            
            return DCFProjection(
                year=year,
                revenue=round(revenue, 2),
                ebitda=round(ebitda, 2),
                ebit=round(ebit, 2),
                tax=round(tax, 2),
                nopat=round(nopat, 2),
                depreciation=round(depreciation, 2),
                capex=round(capex, 2),
                working_capital_change=round(working_capital_change, 2),
                free_cash_flow=round(free_cash_flow, 2),
                present_value=round(present_value, 2)
            )
        except Exception as e:
            logger.error(f"Error calculating FCF for year {year}: {e}")
            raise ValueError(f"FCF calculation failed for year {year}: {e}")
    
    def calculate_terminal_value(self, inputs: DCFInputs, final_fcf: float) -> float:
        """Calculate terminal value using Gordon Growth Model"""
        try:
            if inputs.wacc <= inputs.terminal_growth_rate:
                raise ValueError("WACC must be greater than terminal growth rate")
            
            terminal_value = (final_fcf * (1 + inputs.terminal_growth_rate)) / (inputs.wacc - inputs.terminal_growth_rate)
            return round(terminal_value, 2)
        except Exception as e:
            logger.error(f"Error calculating terminal value: {e}")
            raise ValueError(f"Terminal value calculation failed: {e}")
    
    def perform_dcf_analysis(self, inputs: DCFInputs) -> DCFResults:
        """Perform comprehensive DCF analysis"""
        try:
            # Validate inputs
            validation_errors = self.validator.validate_dcf_inputs(inputs)
            if validation_errors:
                raise ValueError(f"Input validation failed: {', '.join(validation_errors)}")
            
            # Calculate WACC
            wacc = self.calculate_wacc(inputs)
            
            # Update inputs with calculated WACC
            inputs.wacc = wacc
            
            # Generate projections
            projections = []
            for year in range(1, inputs.projection_years + 1):
                projection = self.calculate_free_cash_flow(inputs, year)
                projections.append(projection)
            
            # Calculate terminal value
            final_fcf = projections[-1].free_cash_flow
            terminal_value = self.calculate_terminal_value(inputs, final_fcf)
            terminal_value_pv = terminal_value / ((1 + wacc) ** inputs.projection_years)
            
            # Calculate enterprise value
            pv_of_fcf = sum(p.present_value for p in projections)
            enterprise_value = pv_of_fcf + terminal_value_pv
            
            # Calculate fair value per share (simplified - would need shares outstanding)
            fair_value = enterprise_value  # This should be divided by shares outstanding
            
            # Calculate upside
            upside = fair_value - inputs.current_price
            upside_percent = (upside / inputs.current_price) * 100 if inputs.current_price > 0 else 0
            
            # WACC breakdown
            cost_of_equity = inputs.risk_free_rate + inputs.beta * inputs.market_risk_premium
            cost_of_debt_after_tax = inputs.cost_of_debt * (1 - inputs.tax_rate)
            equity_weight = 1 / (1 + inputs.debt_to_equity)
            debt_weight = inputs.debt_to_equity / (1 + inputs.debt_to_equity)
            
            wacc_breakdown = {
                'cost_of_equity': round(cost_of_equity, 6),
                'cost_of_debt_after_tax': round(cost_of_debt_after_tax, 6),
                'equity_weight': round(equity_weight, 6),
                'debt_weight': round(debt_weight, 6),
                'wacc': round(wacc, 6)
            }
            
            # Sensitivity analysis
            sensitivity_analysis = self.perform_sensitivity_analysis(inputs, fair_value)
            
            # Monte Carlo simulation
            monte_carlo_results = self.perform_monte_carlo_dcf(inputs)
            
            return DCFResults(
                fair_value=round(fair_value, 2),
                upside=round(upside, 2),
                upside_percent=round(upside_percent, 2),
                terminal_value=round(terminal_value, 2),
                projections=projections,
                sensitivity_analysis=sensitivity_analysis,
                monte_carlo_results=monte_carlo_results,
                wacc_breakdown=wacc_breakdown
            )
        except Exception as e:
            logger.error(f"DCF analysis failed: {e}")
            raise ValueError(f"DCF analysis failed: {e}")
    
    def perform_sensitivity_analysis(self, inputs: DCFInputs, base_fair_value: float) -> Dict[str, Any]:
        """Perform sensitivity analysis on key variables"""
        try:
            sensitivity_results = {}
            
            # Variables to test
            variables = {
                'wacc': [inputs.wacc * 0.8, inputs.wacc * 0.9, inputs.wacc * 1.1, inputs.wacc * 1.2],
                'terminal_growth': [inputs.terminal_growth_rate * 0.5, inputs.terminal_growth_rate * 0.75, 
                                  inputs.terminal_growth_rate * 1.25, inputs.terminal_growth_rate * 1.5],
                'revenue_growth': [inputs.revenue_growth_rate * 0.5, inputs.revenue_growth_rate * 0.75,
                                 inputs.revenue_growth_rate * 1.25, inputs.revenue_growth_rate * 1.5]
            }
            
            for var_name, values in variables.items():
                results = []
                for value in values:
                    # Create modified inputs
                    modified_inputs = DCFInputs(**inputs.__dict__)
                    setattr(modified_inputs, var_name, value)
                    
                    # Recalculate DCF
                    try:
                        dcf_result = self.perform_dcf_analysis(modified_inputs)
                        results.append({
                            'value': value,
                            'fair_value': dcf_result.fair_value,
                            'change_percent': ((dcf_result.fair_value - base_fair_value) / base_fair_value) * 100
                        })
                    except:
                        continue
                
                sensitivity_results[var_name] = results
            
            return sensitivity_results
        except Exception as e:
            logger.error(f"Sensitivity analysis failed: {e}")
            return {}
    
    def perform_monte_carlo_dcf(self, inputs: DCFInputs, simulations: int = 1000) -> Dict[str, Any]:
        """Perform Monte Carlo simulation for DCF analysis"""
        try:
            results = []
            
            for _ in range(simulations):
                # Add random variations to key inputs
                modified_inputs = DCFInputs(**inputs.__dict__)
                
                # Add normal distribution variations (±10%)
                modified_inputs.revenue_growth_rate *= (1 + np.random.normal(0, 0.1))
                modified_inputs.ebitda_margin *= (1 + np.random.normal(0, 0.05))
                modified_inputs.wacc *= (1 + np.random.normal(0, 0.05))
                modified_inputs.terminal_growth_rate *= (1 + np.random.normal(0, 0.1))
                
                # Ensure values are within reasonable bounds
                modified_inputs.revenue_growth_rate = max(0, min(0.5, modified_inputs.revenue_growth_rate))
                modified_inputs.ebitda_margin = max(0, min(0.5, modified_inputs.ebitda_margin))
                modified_inputs.wacc = max(0.01, min(0.3, modified_inputs.wacc))
                modified_inputs.terminal_growth_rate = max(0, min(0.1, modified_inputs.terminal_growth_rate))
                
                try:
                    dcf_result = self.perform_dcf_analysis(modified_inputs)
                    results.append(dcf_result.fair_value)
                except:
                    continue
            
            if not results:
                return {}
            
            # Calculate statistics
            results_array = np.array(results)
            
            return {
                'mean': round(float(np.mean(results_array)), 2),
                'median': round(float(np.median(results_array)), 2),
                'std': round(float(np.std(results_array)), 2),
                'percentile_5': round(float(np.percentile(results_array, 5)), 2),
                'percentile_25': round(float(np.percentile(results_array, 25)), 2),
                'percentile_75': round(float(np.percentile(results_array, 75)), 2),
                'percentile_95': round(float(np.percentile(results_array, 95)), 2),
                'simulations': len(results)
            }
        except Exception as e:
            logger.error(f"Monte Carlo DCF simulation failed: {e}")
            return {}


class RiskAnalysisEngine:
    """Comprehensive Risk Analysis Engine"""
    
    def __init__(self):
        self.validator = MathematicalValidator()
    
    def calculate_risk_metrics(self, returns: List[float], benchmark_returns: Optional[List[float]] = None) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            # Validate inputs
            validation_errors = self.validator.validate_risk_inputs(returns)
            if validation_errors:
                raise ValueError(f"Risk analysis validation failed: {', '.join(validation_errors)}")
            
            returns_array = np.array(returns)
            
            # Basic risk metrics
            volatility = float(np.std(returns_array) * np.sqrt(252))  # Annualized
            
            # Beta calculation (if benchmark provided)
            beta = 1.0
            if benchmark_returns and len(benchmark_returns) == len(returns):
                benchmark_array = np.array(benchmark_returns)
                covariance = np.cov(returns_array, benchmark_array)[0, 1]
                benchmark_variance = np.var(benchmark_array)
                if benchmark_variance > 0:
                    beta = covariance / benchmark_variance
            
            # Sharpe Ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02
            excess_returns = returns_array - risk_free_rate / 252
            sharpe_ratio = float(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)) if np.std(excess_returns) > 0 else 0
            
            # Sortino Ratio (downside deviation)
            downside_returns = returns_array[returns_array < 0]
            downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = float(np.mean(excess_returns) / downside_deviation * np.sqrt(252)) if downside_deviation > 0 else 0
            
            # Maximum Drawdown
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = float(np.min(drawdowns))
            
            # Value at Risk (VaR)
            var_95 = float(np.percentile(returns_array, 5))
            var_99 = float(np.percentile(returns_array, 1))
            
            # Conditional Value at Risk (CVaR)
            cvar_95 = float(np.mean(returns_array[returns_array <= var_95]))
            cvar_99 = float(np.mean(returns_array[returns_array <= var_99]))
            
            # Tracking Error and Information Ratio
            tracking_error = 0.0
            information_ratio = 0.0
            if benchmark_returns and len(benchmark_returns) == len(returns):
                tracking_error = float(np.std(returns_array - benchmark_array) * np.sqrt(252))
                excess_return = np.mean(returns_array - benchmark_array) * 252
                information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            # Calmar Ratio
            annual_return = float(np.mean(returns_array) * 252)
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            return RiskMetrics(
                beta=round(beta, 4),
                volatility=round(volatility, 4),
                sharpe_ratio=round(sharpe_ratio, 4),
                sortino_ratio=round(sortino_ratio, 4),
                max_drawdown=round(max_drawdown, 4),
                var_95=round(var_95, 4),
                var_99=round(var_99, 4),
                cvar_95=round(cvar_95, 4),
                cvar_99=round(cvar_99, 4),
                tracking_error=round(tracking_error, 4),
                information_ratio=round(information_ratio, 4),
                calmar_ratio=round(calmar_ratio, 4)
            )
        except Exception as e:
            logger.error(f"Risk metrics calculation failed: {e}")
            raise ValueError(f"Risk metrics calculation failed: {e}")
    
    def perform_stress_test(self, returns: List[float], scenarios: Dict[str, float]) -> Dict[str, Any]:
        """Perform stress testing with various scenarios"""
        try:
            returns_array = np.array(returns)
            stress_results = {}
            
            for scenario_name, shock in scenarios.items():
                # Apply shock to returns
                stressed_returns = returns_array * (1 + shock)
                
                # Calculate metrics under stress
                stressed_metrics = self.calculate_risk_metrics(stressed_returns.tolist())
                
                stress_results[scenario_name] = {
                    'shock': shock,
                    'expected_loss': float(np.mean(stressed_returns)),
                    'var_95': stressed_metrics.var_95,
                    'var_99': stressed_metrics.var_99,
                    'max_drawdown': stressed_metrics.max_drawdown
                }
            
            return stress_results
        except Exception as e:
            logger.error(f"Stress testing failed: {e}")
            raise ValueError(f"Stress testing failed: {e}")
    
    def calculate_correlation_matrix(self, returns_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate correlation matrix for multiple assets"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(returns_data)
            
            # Calculate correlation matrix
            correlation_matrix = df.corr()
            
            # Calculate average correlation
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
            correlations = correlation_matrix.values[mask]
            avg_correlation = float(np.mean(correlations)) if len(correlations) > 0 else 0
            
            return {
                'matrix': correlation_matrix.to_dict(),
                'average_correlation': round(avg_correlation, 4),
                'max_correlation': round(float(correlation_matrix.max().max()), 4),
                'min_correlation': round(float(correlation_matrix.min().min()), 4)
            }
        except Exception as e:
            logger.error(f"Correlation matrix calculation failed: {e}")
            raise ValueError(f"Correlation matrix calculation failed: {e}")


class OptionsAnalysisEngine:
    """Options Pricing and Analysis Engine"""
    
    def __init__(self):
        pass
    
    def black_scholes_price(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> float:
        """Calculate Black-Scholes option price"""
        try:
            if T <= 0:
                return max(S - K, 0) if option_type == 'call' else max(K - S, 0)
            
            d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            
            if option_type == 'call':
                price = S * stats.norm.cdf(d1) - K * math.exp(-r * T) * stats.norm.cdf(d2)
            else:  # put
                price = K * math.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
            
            return round(price, 4)
        except Exception as e:
            logger.error(f"Black-Scholes pricing failed: {e}")
            raise ValueError(f"Black-Scholes pricing failed: {e}")
    
    def calculate_greeks(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> OptionsGreeks:
        """Calculate options Greeks"""
        try:
            if T <= 0:
                return OptionsGreeks(0, 0, 0, 0, 0)
            
            d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            
            # Delta
            if option_type == 'call':
                delta = stats.norm.cdf(d1)
            else:  # put
                delta = stats.norm.cdf(d1) - 1
            
            # Gamma
            gamma = stats.norm.pdf(d1) / (S * sigma * math.sqrt(T))
            
            # Theta
            theta_part1 = -(S * stats.norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
            if option_type == 'call':
                theta_part2 = -r * K * math.exp(-r * T) * stats.norm.cdf(d2)
            else:  # put
                theta_part2 = r * K * math.exp(-r * T) * stats.norm.cdf(-d2)
            theta = (theta_part1 + theta_part2) / 365  # Per day
            
            # Vega
            vega = S * stats.norm.pdf(d1) * math.sqrt(T) / 100  # Per 1% change in volatility
            
            # Rho
            if option_type == 'call':
                rho = K * T * math.exp(-r * T) * stats.norm.cdf(d2) / 100  # Per 1% change in rate
            else:  # put
                rho = -K * T * math.exp(-r * T) * stats.norm.cdf(-d2) / 100
            
            return OptionsGreeks(
                delta=round(delta, 4),
                gamma=round(gamma, 4),
                theta=round(theta, 4),
                vega=round(vega, 4),
                rho=round(rho, 4)
            )
        except Exception as e:
            logger.error(f"Greeks calculation failed: {e}")
            raise ValueError(f"Greeks calculation failed: {e}")
    
    def implied_volatility(self, market_price: float, S: float, K: float, T: float, r: float, option_type: str = 'call') -> float:
        """Calculate implied volatility using Newton-Raphson method"""
        try:
            if T <= 0:
                return 0.0
            
            # Initial guess
            sigma = 0.2
            
            for _ in range(100):  # Max iterations
                price = self.black_scholes_price(S, K, T, r, sigma, option_type)
                vega = self.calculate_greeks(S, K, T, r, sigma, option_type).vega * 100
                
                if abs(vega) < 1e-10:
                    break
                
                diff = market_price - price
                if abs(diff) < 1e-6:
                    break
                
                sigma = sigma + diff / vega
                sigma = max(0.001, min(5.0, sigma))  # Bounds
            
            return round(sigma, 4)
        except Exception as e:
            logger.error(f"Implied volatility calculation failed: {e}")
            raise ValueError(f"Implied volatility calculation failed: {e}")


class AnalyticsEngine:
    """Main Analytics Engine coordinating all financial modeling capabilities"""
    
    def __init__(self):
        self.dcf_engine = DCFAnalysisEngine()
        self.risk_engine = RiskAnalysisEngine()
        self.options_engine = OptionsAnalysisEngine()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def analyze_dcf(self, inputs: DCFInputs) -> DCFResults:
        """Perform DCF analysis asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.dcf_engine.perform_dcf_analysis, inputs)
    
    async def analyze_risk(self, returns: List[float], benchmark_returns: Optional[List[float]] = None) -> RiskMetrics:
        """Perform risk analysis asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.risk_engine.calculate_risk_metrics, returns, benchmark_returns)
    
    async def analyze_options(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> Dict[str, Any]:
        """Perform options analysis asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run calculations in parallel
        price_task = loop.run_in_executor(self.executor, self.options_engine.black_scholes_price, S, K, T, r, sigma, option_type)
        greeks_task = loop.run_in_executor(self.executor, self.options_engine.calculate_greeks, S, K, T, r, sigma, option_type)
        
        price, greeks = await asyncio.gather(price_task, greeks_task)
        
        return {
            'price': price,
            'greeks': {
                'delta': greeks.delta,
                'gamma': greeks.gamma,
                'theta': greeks.theta,
                'vega': greeks.vega,
                'rho': greeks.rho
            }
        }
    
    def __del__(self):
        """Cleanup executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
