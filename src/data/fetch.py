from .schemas import PriceDataSchema

def get_price_data(ticker: str, start: str = "2015-01-01") -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(ticker, start=start, auto_adjust=True)
    df.index.name = "date"
    PriceDataSchema.validate(df)
    return df
