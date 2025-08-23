import pandas as pd
import yfinance as yf

def backtest_top_n(tickers, start="2020-01-01", end=None):
    """
    Backtest equal-weighted portfolio of provided tickers.
    SPY benchmark added only if explicitly included.
    """
    data = yf.download(list(tickers), start=start, end=end, auto_adjust=True, progress=False)
    if data.empty:
        raise ValueError("No data returned for backtest tickers.")

    prices = data["Adj Close"] if "Adj Close" in data else data
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    returns = prices.pct_change().dropna(how="all")
    port_rets = returns.mean(axis=1)
    eq_curve = (1 + port_rets).cumprod()

    df = pd.DataFrame({"Portfolio": eq_curve})
    if "SPY" in prices.columns:
        bench_curve = (1 + returns["SPY"]).cumprod()
        df["Benchmark"] = bench_curve
    return df
