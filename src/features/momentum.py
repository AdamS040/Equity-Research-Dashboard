# src/features/momentum.py
import pandas as pd

def compute_momentum_scores(prices: pd.DataFrame, lookback: int = 252) -> pd.Series:
    """
    Compute momentum scores as annualized return over lookback period (default 1Y ~ 252 trading days).
    Automatically handles missing tickers and short histories.
    """
    scores = pd.Series(index=prices.columns, dtype=float)

    for ticker in prices.columns:
        series = prices[ticker].dropna()
        if len(series) < 2:
            scores[ticker] = 0  # insufficient data
        else:
            ret = series.pct_change().fillna(0)
            if len(ret) < lookback:
                lookback_ret = ret.sum()  # shorter history fallback
            else:
                lookback_ret = ret[-lookback:].sum()
            scores[ticker] = lookback_ret

    # z-score across universe
    scores = (scores - scores.mean()) / (scores.std() + 1e-9)
    return scores
