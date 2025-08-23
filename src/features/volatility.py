# src/features/volatility.py
import pandas as pd

def compute_vol_scores(prices: pd.DataFrame, lookback: int = 252) -> pd.Series:
    """
    Compute low-volatility scores as inverse of annualized std deviation over lookback period.
    Higher score = lower volatility.
    Handles missing or short price series gracefully.
    """
    scores = pd.Series(index=prices.columns, dtype=float)

    for ticker in prices.columns:
        series = prices[ticker].dropna()
        if len(series) < 2:
            scores[ticker] = 0  # insufficient data
        else:
            daily_ret = series.pct_change().fillna(0)
            if len(daily_ret) < lookback:
                vol = daily_ret.std()
            else:
                vol = daily_ret[-lookback:].std()
            scores[ticker] = -vol  # negative because low vol = high score

    # z-score across universe
    scores = (scores - scores.mean()) / (scores.std() + 1e-9)
    return scores
