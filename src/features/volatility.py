import pandas as pd

def compute_vol_scores(prices: pd.DataFrame) -> pd.Series:
    """
    Compute Low Volatility factor:
    - Inverse of 1-year volatility
    Input:
        prices: DataFrame of adjusted close prices
    Output:
        Series of z-scored volatility scores (higher = lower vol)
    """
    daily_returns = prices.pct_change().dropna()
    vol = daily_returns.rolling(252).std().iloc[-1]  # 1Y volatility
    vol_inv = 1 / vol
    vol_z = (vol_inv - vol_inv.mean()) / vol_inv.std()
    return vol_z
