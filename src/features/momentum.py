import pandas as pd

def compute_momentum_scores(prices: pd.DataFrame) -> pd.Series:
    """
    Compute Momentum factor:
    - 6-month price return
    Input:
        prices: DataFrame of adjusted close prices (tickers as columns)
    Output:
        Series of z-scored momentum scores
    """
    returns_6m = prices.pct_change(126).iloc[-1]  # ~126 trading days = 6 months
    momentum_z = (returns_6m - returns_6m.mean()) / returns_6m.std()
    return momentum_z
