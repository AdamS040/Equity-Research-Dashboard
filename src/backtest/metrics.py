import pandas as pd
import numpy as np

def sharpe_ratio(returns: pd.Series, freq: int = 252) -> float:
    """Annualized Sharpe ratio assuming risk-free = 0."""
    return np.sqrt(freq) * returns.mean() / returns.std()

def max_drawdown(equity_curve: pd.Series) -> float:
    """Max drawdown."""
    roll_max = equity_curve.cummax()
    drawdown = (equity_curve - roll_max) / roll_max
    return drawdown.min()
