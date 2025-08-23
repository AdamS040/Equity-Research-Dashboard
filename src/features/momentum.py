import pandas as pd

def compute_momentum_scores(prices: pd.DataFrame, lookback: int = 126, min_lookback: int = 63) -> pd.Series:
    """
    Momentum = total return over lookback (z-scored).
    Falls back to available window if history < lookback.
    """
    if prices is None or prices.empty:
        raise ValueError("No price data provided to compute_momentum_scores.")

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    n = len(prices)
    if n < (min_lookback + 1):
        raise ValueError("Not enough history for momentum (<~3 months).")

    lb = min(lookback, n - 1)

    # vectorized total return over lb days
    last = prices.iloc[-1]
    prev = prices.iloc[-1 - lb]
    total_ret = (last / prev) - 1

    z = (total_ret - total_ret.mean()) / total_ret.std(ddof=0)
    return z
