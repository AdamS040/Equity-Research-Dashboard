import pandas as pd
import numpy as np

def backtest_top_n(prices: pd.DataFrame, scores: pd.DataFrame, top_n: int = 20):
    """
    Backtest top-N long-only portfolio.
    Args:
        prices: OHLCV dataframe (date x tickers) - Close prices
        scores: Value factor scores (date x tickers)
        top_n: Number of stocks to hold

    Returns:
        DataFrame with daily portfolio returns and cumulative equity
    """
    # Daily returns
    returns = prices.pct_change().shift(-1)  # next-day return

    portfolio_ret = []

    # Rebalance monthly
    rebalance_dates = scores.resample("M").last().index

    for date in rebalance_dates:
        if date not in scores.index:
            continue
        top_stocks = scores.loc[date].nlargest(top_n).index
        daily_ret = returns[top_stocks].mean(axis=1)
        portfolio_ret.append(daily_ret)

    portfolio_ret = pd.concat(portfolio_ret).sort_index()
    portfolio_cum = (1 + portfolio_ret).cumprod()
    return pd.DataFrame({"daily_return": portfolio_ret, "equity_curve": portfolio_cum})
