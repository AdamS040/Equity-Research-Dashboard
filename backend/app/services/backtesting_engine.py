"""
Backtesting Engine for Trading Strategies

This module provides comprehensive backtesting capabilities including:
- Historical strategy performance testing
- Portfolio optimization backtesting
- Risk-adjusted return analysis
- Drawdown analysis and recovery periods
- Benchmark comparison
- Transaction cost impact analysis
- Strategy validation and optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
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
class BacktestStrategy:
    """Backtesting Strategy Definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    entry_rules: List[str]
    exit_rules: List[str]
    position_sizing: str
    max_positions: int = 10
    rebalance_frequency: str = 'daily'  # daily, weekly, monthly


@dataclass
class BacktestTrade:
    """Individual Trade Record"""
    entry_date: str
    exit_date: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    duration: int  # days
    reason: str  # entry/exit reason


@dataclass
class BacktestResults:
    """Backtesting Results"""
    strategy: BacktestStrategy
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    trades: List[BacktestTrade]
    monthly_returns: List[Dict[str, Any]]
    benchmark_comparison: Dict[str, Any]
    performance_metrics: Dict[str, Any]


@dataclass
class PortfolioWeights:
    """Portfolio Weight Configuration"""
    symbol: str
    weight: float
    rebalance_date: str


class StrategyEngine:
    """Strategy Implementation Engine"""
    
    def __init__(self):
        pass
    
    def moving_average_crossover(self, data: pd.DataFrame, short_window: int = 20, 
                               long_window: int = 50) -> pd.DataFrame:
        """Moving Average Crossover Strategy"""
        try:
            df = data.copy()
            
            # Calculate moving averages
            df['sma_short'] = df['close'].rolling(window=short_window).mean()
            df['sma_long'] = df['close'].rolling(window=long_window).mean()
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1  # Buy
            df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1  # Sell
            
            # Calculate position changes
            df['position'] = df['signal'].diff()
            
            return df
            
        except Exception as e:
            logger.error(f"Moving average crossover strategy failed: {e}")
            raise ValueError(f"Moving average crossover strategy failed: {e}")
    
    def rsi_strategy(self, data: pd.DataFrame, rsi_period: int = 14, 
                    oversold: float = 30, overbought: float = 70) -> pd.DataFrame:
        """RSI Mean Reversion Strategy"""
        try:
            df = data.copy()
            
            # Calculate RSI
            df['rsi'] = self._calculate_rsi(df['close'], rsi_period)
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['rsi'] < oversold, 'signal'] = 1  # Buy when oversold
            df.loc[df['rsi'] > overbought, 'signal'] = -1  # Sell when overbought
            
            # Calculate position changes
            df['position'] = df['signal'].diff()
            
            return df
            
        except Exception as e:
            logger.error(f"RSI strategy failed: {e}")
            raise ValueError(f"RSI strategy failed: {e}")
    
    def momentum_strategy(self, data: pd.DataFrame, lookback_period: int = 20, 
                         threshold: float = 0.02) -> pd.DataFrame:
        """Momentum Strategy"""
        try:
            df = data.copy()
            
            # Calculate momentum
            df['momentum'] = df['close'].pct_change(lookback_period)
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['momentum'] > threshold, 'signal'] = 1  # Buy on positive momentum
            df.loc[df['momentum'] < -threshold, 'signal'] = -1  # Sell on negative momentum
            
            # Calculate position changes
            df['position'] = df['signal'].diff()
            
            return df
            
        except Exception as e:
            logger.error(f"Momentum strategy failed: {e}")
            raise ValueError(f"Momentum strategy failed: {e}")
    
    def mean_reversion_strategy(self, data: pd.DataFrame, lookback_period: int = 20, 
                               std_threshold: float = 2.0) -> pd.DataFrame:
        """Mean Reversion Strategy"""
        try:
            df = data.copy()
            
            # Calculate rolling mean and standard deviation
            df['rolling_mean'] = df['close'].rolling(window=lookback_period).mean()
            df['rolling_std'] = df['close'].rolling(window=lookback_period).std()
            
            # Calculate z-score
            df['z_score'] = (df['close'] - df['rolling_mean']) / df['rolling_std']
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['z_score'] < -std_threshold, 'signal'] = 1  # Buy when oversold
            df.loc[df['z_score'] > std_threshold, 'signal'] = -1  # Sell when overbought
            
            # Calculate position changes
            df['position'] = df['signal'].diff()
            
            return df
            
        except Exception as e:
            logger.error(f"Mean reversion strategy failed: {e}")
            raise ValueError(f"Mean reversion strategy failed: {e}")
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"RSI calculation failed: {e}")
            raise ValueError(f"RSI calculation failed: {e}")


class BacktestingEngine:
    """Main Backtesting Engine"""
    
    def __init__(self):
        self.strategy_engine = StrategyEngine()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def run_backtest(self, strategy: BacktestStrategy, historical_data: Dict[str, pd.DataFrame],
                    initial_capital: float = 100000, transaction_cost: float = 0.001,
                    benchmark_data: Optional[pd.DataFrame] = None) -> BacktestResults:
        """Run comprehensive backtesting analysis"""
        try:
            # Validate inputs
            if not historical_data:
                raise ValueError("No historical data provided")
            
            if initial_capital <= 0:
                raise ValueError("Initial capital must be positive")
            
            # Get date range
            start_date, end_date = self._get_date_range(historical_data)
            
            # Initialize portfolio
            portfolio_value = initial_capital
            positions = {}
            trades = []
            portfolio_values = []
            dates = []
            
            # Get all trading dates
            all_dates = set()
            for symbol, data in historical_data.items():
                all_dates.update(data.index)
            
            trading_dates = sorted(list(all_dates))
            
            # Run backtest day by day
            for date in trading_dates:
                current_portfolio_value = self._calculate_portfolio_value(
                    positions, historical_data, date, initial_capital
                )
                
                # Apply strategy for each symbol
                for symbol, data in historical_data.items():
                    if date in data.index:
                        signal = self._get_strategy_signal(strategy, data, date)
                        
                        if signal != 0:
                            trade = self._execute_trade(
                                symbol, signal, data.loc[date], positions, 
                                portfolio_value, transaction_cost, date
                            )
                            if trade:
                                trades.append(trade)
                
                # Update portfolio value
                portfolio_value = self._calculate_portfolio_value(
                    positions, historical_data, date, initial_capital
                )
                
                portfolio_values.append(portfolio_value)
                dates.append(date)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                portfolio_values, initial_capital, trading_dates
            )
            
            # Calculate benchmark comparison
            benchmark_comparison = self._calculate_benchmark_comparison(
                portfolio_values, benchmark_data, trading_dates, initial_capital
            )
            
            # Calculate monthly returns
            monthly_returns = self._calculate_monthly_returns(portfolio_values, dates)
            
            # Final results
            final_value = portfolio_values[-1] if portfolio_values else initial_capital
            total_return = (final_value - initial_capital) / initial_capital
            
            return BacktestResults(
                strategy=strategy,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_value=final_value,
                total_return=total_return,
                annualized_return=performance_metrics.get('annualized_return', 0),
                volatility=performance_metrics.get('volatility', 0),
                sharpe_ratio=performance_metrics.get('sharpe_ratio', 0),
                max_drawdown=performance_metrics.get('max_drawdown', 0),
                max_drawdown_duration=performance_metrics.get('max_drawdown_duration', 0),
                win_rate=performance_metrics.get('win_rate', 0),
                profit_factor=performance_metrics.get('profit_factor', 0),
                trades=trades,
                monthly_returns=monthly_returns,
                benchmark_comparison=benchmark_comparison,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Backtesting failed: {e}")
            raise ValueError(f"Backtesting failed: {e}")
    
    def _get_date_range(self, historical_data: Dict[str, pd.DataFrame]) -> Tuple[str, str]:
        """Get the date range from historical data"""
        try:
            all_dates = set()
            for data in historical_data.values():
                all_dates.update(data.index)
            
            if not all_dates:
                raise ValueError("No dates found in historical data")
            
            start_date = min(all_dates).strftime('%Y-%m-%d')
            end_date = max(all_dates).strftime('%Y-%m-%d')
            
            return start_date, end_date
            
        except Exception as e:
            logger.error(f"Date range calculation failed: {e}")
            raise ValueError(f"Date range calculation failed: {e}")
    
    def _get_strategy_signal(self, strategy: BacktestStrategy, data: pd.DataFrame, date: str) -> int:
        """Get trading signal for a specific date"""
        try:
            # Get data up to current date
            current_data = data.loc[:date]
            
            if len(current_data) < 50:  # Need minimum data for calculations
                return 0
            
            # Apply strategy based on strategy name
            if strategy.name == 'moving_average_crossover':
                short_window = strategy.parameters.get('short_window', 20)
                long_window = strategy.parameters.get('long_window', 50)
                result = self.strategy_engine.moving_average_crossover(current_data, short_window, long_window)
            elif strategy.name == 'rsi_strategy':
                rsi_period = strategy.parameters.get('rsi_period', 14)
                oversold = strategy.parameters.get('oversold', 30)
                overbought = strategy.parameters.get('overbought', 70)
                result = self.strategy_engine.rsi_strategy(current_data, rsi_period, oversold, overbought)
            elif strategy.name == 'momentum_strategy':
                lookback = strategy.parameters.get('lookback_period', 20)
                threshold = strategy.parameters.get('threshold', 0.02)
                result = self.strategy_engine.momentum_strategy(current_data, lookback, threshold)
            elif strategy.name == 'mean_reversion_strategy':
                lookback = strategy.parameters.get('lookback_period', 20)
                std_threshold = strategy.parameters.get('std_threshold', 2.0)
                result = self.strategy_engine.mean_reversion_strategy(current_data, lookback, std_threshold)
            else:
                return 0
            
            # Get the latest signal
            if date in result.index and 'position' in result.columns:
                return int(result.loc[date, 'position'])
            
            return 0
            
        except Exception as e:
            logger.error(f"Signal generation failed for {strategy.name}: {e}")
            return 0
    
    def _execute_trade(self, symbol: str, signal: int, price_data: pd.Series, 
                      positions: Dict[str, float], portfolio_value: float,
                      transaction_cost: float, date: str) -> Optional[BacktestTrade]:
        """Execute a trade based on signal"""
        try:
            current_price = price_data['close']
            current_position = positions.get(symbol, 0)
            
            # Calculate position size (simplified - equal weight)
            max_position_value = portfolio_value * 0.1  # 10% max per position
            target_shares = max_position_value / current_price
            
            if signal > 0 and current_position == 0:  # Buy signal
                # Buy shares
                shares_to_buy = target_shares
                cost = shares_to_buy * current_price * (1 + transaction_cost)
                
                if cost <= portfolio_value * 0.95:  # Leave 5% cash buffer
                    positions[symbol] = shares_to_buy
                    
                    return BacktestTrade(
                        entry_date=date,
                        exit_date='',
                        symbol=symbol,
                        entry_price=current_price,
                        exit_price=0,
                        quantity=shares_to_buy,
                        pnl=0,
                        pnl_percent=0,
                        duration=0,
                        reason='buy_signal'
                    )
            
            elif signal < 0 and current_position > 0:  # Sell signal
                # Sell all shares
                shares_to_sell = current_position
                proceeds = shares_to_sell * current_price * (1 - transaction_cost)
                
                positions[symbol] = 0
                
                return BacktestTrade(
                    entry_date='',  # Would need to track entry date
                    exit_date=date,
                    symbol=symbol,
                    entry_price=0,  # Would need to track entry price
                    exit_price=current_price,
                    quantity=shares_to_sell,
                    pnl=0,  # Would need to calculate actual P&L
                    pnl_percent=0,
                    duration=0,
                    reason='sell_signal'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return None
    
    def _calculate_portfolio_value(self, positions: Dict[str, float], 
                                 historical_data: Dict[str, pd.DataFrame],
                                 date: str, initial_capital: float) -> float:
        """Calculate current portfolio value"""
        try:
            total_value = 0
            
            for symbol, shares in positions.items():
                if shares > 0 and symbol in historical_data:
                    data = historical_data[symbol]
                    if date in data.index:
                        current_price = data.loc[date, 'close']
                        total_value += shares * current_price
            
            return total_value
            
        except Exception as e:
            logger.error(f"Portfolio value calculation failed: {e}")
            return initial_capital
    
    def _calculate_performance_metrics(self, portfolio_values: List[float], 
                                     initial_capital: float, dates: List[str]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            if not portfolio_values:
                return {}
            
            # Convert to returns
            returns = []
            for i in range(1, len(portfolio_values)):
                ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                returns.append(ret)
            
            if not returns:
                return {}
            
            returns_array = np.array(returns)
            
            # Basic metrics
            total_return = (portfolio_values[-1] - initial_capital) / initial_capital
            
            # Annualized return
            days = len(dates)
            years = days / 365.25
            annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
            
            # Volatility (annualized)
            volatility = np.std(returns_array) * np.sqrt(252)
            
            # Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02
            excess_returns = returns_array - risk_free_rate / 252
            sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdowns)
            
            # Maximum drawdown duration
            max_drawdown_duration = self._calculate_max_drawdown_duration(drawdowns)
            
            # Win rate and profit factor (simplified)
            positive_returns = returns_array[returns_array > 0]
            negative_returns = returns_array[returns_array < 0]
            
            win_rate = len(positive_returns) / len(returns_array) if len(returns_array) > 0 else 0
            
            gross_profit = np.sum(positive_returns) if len(positive_returns) > 0 else 0
            gross_loss = abs(np.sum(negative_returns)) if len(negative_returns) > 0 else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            return {
                'total_return': round(total_return, 4),
                'annualized_return': round(annualized_return, 4),
                'volatility': round(volatility, 4),
                'sharpe_ratio': round(sharpe_ratio, 4),
                'max_drawdown': round(max_drawdown, 4),
                'max_drawdown_duration': max_drawdown_duration,
                'win_rate': round(win_rate, 4),
                'profit_factor': round(profit_factor, 4),
                'total_trades': len(returns_array),
                'positive_trades': len(positive_returns),
                'negative_trades': len(negative_returns)
            }
            
        except Exception as e:
            logger.error(f"Performance metrics calculation failed: {e}")
            return {}
    
    def _calculate_max_drawdown_duration(self, drawdowns: np.ndarray) -> int:
        """Calculate maximum drawdown duration in days"""
        try:
            max_duration = 0
            current_duration = 0
            
            for drawdown in drawdowns:
                if drawdown < 0:
                    current_duration += 1
                    max_duration = max(max_duration, current_duration)
                else:
                    current_duration = 0
            
            return max_duration
            
        except Exception as e:
            logger.error(f"Max drawdown duration calculation failed: {e}")
            return 0
    
    def _calculate_benchmark_comparison(self, portfolio_values: List[float],
                                      benchmark_data: Optional[pd.DataFrame],
                                      dates: List[str], initial_capital: float) -> Dict[str, Any]:
        """Calculate benchmark comparison metrics"""
        try:
            if not benchmark_data or not portfolio_values:
                return {}
            
            # Calculate portfolio returns
            portfolio_returns = []
            for i in range(1, len(portfolio_values)):
                ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
                portfolio_returns.append(ret)
            
            # Calculate benchmark returns
            benchmark_returns = []
            benchmark_values = []
            benchmark_initial = initial_capital
            
            for date in dates[1:]:  # Skip first date
                if date in benchmark_data.index:
                    current_price = benchmark_data.loc[date, 'close']
                    if len(benchmark_values) == 0:
                        benchmark_values.append(benchmark_initial)
                    else:
                        prev_price = benchmark_data.loc[dates[dates.index(date)-1], 'close']
                        ret = (current_price - prev_price) / prev_price
                        benchmark_returns.append(ret)
                        benchmark_values.append(benchmark_values[-1] * (1 + ret))
            
            if not benchmark_returns or not portfolio_returns:
                return {}
            
            # Calculate comparison metrics
            portfolio_returns_array = np.array(portfolio_returns)
            benchmark_returns_array = np.array(benchmark_returns)
            
            # Alpha and Beta
            if len(portfolio_returns_array) == len(benchmark_returns_array):
                covariance = np.cov(portfolio_returns_array, benchmark_returns_array)[0, 1]
                benchmark_variance = np.var(benchmark_returns_array)
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 1
                
                portfolio_annual_return = np.mean(portfolio_returns_array) * 252
                benchmark_annual_return = np.mean(benchmark_returns_array) * 252
                risk_free_rate = 0.02
                
                alpha = portfolio_annual_return - (risk_free_rate + beta * (benchmark_annual_return - risk_free_rate))
                
                # Information ratio
                excess_returns = portfolio_returns_array - benchmark_returns_array
                tracking_error = np.std(excess_returns) * np.sqrt(252)
                information_ratio = np.mean(excess_returns) * 252 / tracking_error if tracking_error > 0 else 0
                
                return {
                    'alpha': round(alpha, 4),
                    'beta': round(beta, 4),
                    'information_ratio': round(information_ratio, 4),
                    'tracking_error': round(tracking_error, 4),
                    'portfolio_return': round(portfolio_annual_return, 4),
                    'benchmark_return': round(benchmark_annual_return, 4),
                    'excess_return': round(portfolio_annual_return - benchmark_annual_return, 4)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Benchmark comparison calculation failed: {e}")
            return {}
    
    def _calculate_monthly_returns(self, portfolio_values: List[float], dates: List[str]) -> List[Dict[str, Any]]:
        """Calculate monthly returns"""
        try:
            if not portfolio_values or not dates:
                return []
            
            # Create DataFrame with dates and values
            df = pd.DataFrame({
                'date': dates,
                'value': portfolio_values
            })
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Resample to monthly
            monthly_data = df.resample('M').last()
            
            # Calculate monthly returns
            monthly_returns = []
            for i in range(1, len(monthly_data)):
                prev_value = monthly_data.iloc[i-1]['value']
                current_value = monthly_data.iloc[i]['value']
                monthly_return = (current_value - prev_value) / prev_value
                
                monthly_returns.append({
                    'month': monthly_data.index[i].strftime('%Y-%m'),
                    'return': round(monthly_return, 4),
                    'value': current_value
                })
            
            return monthly_returns
            
        except Exception as e:
            logger.error(f"Monthly returns calculation failed: {e}")
            return []
    
    async def run_backtest_async(self, strategy: BacktestStrategy, 
                               historical_data: Dict[str, pd.DataFrame],
                               initial_capital: float = 100000,
                               transaction_cost: float = 0.001,
                               benchmark_data: Optional[pd.DataFrame] = None) -> BacktestResults:
        """Run backtesting analysis asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.run_backtest, 
            strategy, 
            historical_data, 
            initial_capital, 
            transaction_cost, 
            benchmark_data
        )
    
    def __del__(self):
        """Cleanup executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
