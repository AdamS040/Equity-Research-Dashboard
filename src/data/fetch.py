import yfinance as yf
import pandas as pd

def get_price_data(ticker: str, start: str = "2015-01-01") -> pd.DataFrame:
    """Download OHLCV price data from Yahoo Finance."""
    df = yf.download(ticker, start=start, auto_adjust=True)
    df.index.name = "date"
    return df
