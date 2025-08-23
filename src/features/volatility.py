import pandas as pd

def compute_vol_scores(prices: pd.DataFrame, window: int = 252, min_periods: int = 126) -> pd.Series:
    """
    Low Volatility factor = inverse 1Y vol (z-scored).
    Robust to short histories and empty inputs.
    """
    if prices is None or prices.empty:
        raise ValueError("No price data provided to compute_vol_scores.")

    # Ensure 2D
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    daily_returns = prices.pct_change()

    # Rolling vol with tolerance for shorter histories
    vol = daily_returns.rolling(window=window, min_periods=min_periods).std()

    # Try to take the last valid row; if none, fall back to simple std
    vol_last = vol.dropna(how="all").tail(1)
    if vol_last.empty:
        # require at least ~3 months of data to say anything
        if daily_returns.shape[0] < 63:
            raise ValueError("Not enough history (<63 trading days) for volatility.")
        vol_last = daily_returns.std().to_frame().T

    vol_last = vol_last.iloc[0]
    vol_inv = 1.0 / vol_last.replace(0, pd.NA)
    vol_inv = vol_inv.fillna(vol_inv.median())

    z = (vol_inv - vol_inv.mean()) / vol_inv.std(ddof=0)
    return z
