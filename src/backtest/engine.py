import pandas as pd
import numpy as np

def simple_long_only(prices: pd.DataFrame, scores: pd.DataFrame, top_n: int = 20):
    """
    Very basic backtest:
    - Rebalance monthly
    - Long top-N by score
    - Equal weight portfolio
    """
    rets = prices.pct_change().shift(-1)  # next day return
    portfolio_vals = []

    for date, row in scores.resample("M").last().iterrows():
        top = row.nlargest(top_n).index
        port_ret = rets.loc[date:, top].iloc[0].mean()
        portfolio_vals.append((date, port_ret))

    return pd.DataFrame(portfolio_vals, columns=["date", "return"]).set_index("date")
