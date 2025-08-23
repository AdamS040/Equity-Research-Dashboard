import yfinance as yf
import pandas as pd

def fetch_fundamentals(universe: list[str]) -> pd.DataFrame:
    """
    Pulls key ratios from Yahoo Finance for each ticker in universe.
    Returns a DataFrame with Value, Quality, Momentum, Volatility placeholders.
    """

    records = []

    for ticker in universe:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info  # metadata dict

            # Defensive parsing: some tickers may miss data
            pe = info.get("trailingPE", None)
            roe = info.get("returnOnEquity", None)
            debt_to_eq = info.get("debtToEquity", None)

            records.append({
                "Ticker": ticker,
                "Value": pe if pe else None,
                "Quality": roe if roe else None,
                "Leverage": debt_to_eq if debt_to_eq else None,
            })

        except Exception as e:
            print(f"⚠️ Could not fetch {ticker}: {e}")
            records.append({
                "Ticker": ticker,
                "Value": None,
                "Quality": None,
                "Leverage": None,
            })

    df = pd.DataFrame(records).set_index("Ticker")

    # Basic cleaning: lower P/E is better, higher ROE better, lower Debt/Equity better
    df = df.apply(pd.to_numeric, errors="coerce")

    # Normalize 0–1 for each factor (quant style)
    def normalize(series, reverse=False):
        s = series.copy()
        if reverse:  # lower = better
            s = -s
        return (s - s.min()) / (s.max() - s.min())

    df["Value_Score"] = normalize(df["Value"], reverse=True)
    df["Quality_Score"] = normalize(df["Quality"], reverse=False)
    df["Leverage_Score"] = normalize(df["Leverage"], reverse=True)

    return df[["Value_Score", "Quality_Score", "Leverage_Score"]]
