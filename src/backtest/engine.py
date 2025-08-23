import pandas as pd
import yfinance as yf

def backtest_top_n(tickers, start="2020-01-01", end=None):
    """
    Backtest equal-weighted portfolio of top N tickers vs SPY benchmark.
    """
    prices = yf.download(tickers, start=start, end=end)["Adj Close"]
    returns = prices.pct_change().dropna()

    port_rets = returns[tickers].mean(axis=1)
    eq_curve = (1 + port_rets).cumprod()
    bench_curve = (1 + returns["SPY"]).cumprod() if "SPY" in returns else None

    return pd.DataFrame({"Portfolio": eq_curve, "Benchmark": bench_curve})
