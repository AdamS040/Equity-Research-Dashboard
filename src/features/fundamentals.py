# src/features/fundamentals.py
import hashlib
import pandas as pd
import yfinance as yf

# -----------------------------
# Helpers
# -----------------------------
def stable_u01(s) -> float:
    """Deterministic pseudo-random in [0,1) per ticker"""
    s = str(s)  # ensure string
    h = hashlib.sha1(s.encode()).hexdigest()
    return (int(h[:10], 16) % 1_000_000) / 1_000_000.0

def make_placeholder_financials(universe: list) -> pd.DataFrame:
    """Return a DataFrame of dummy fundamentals for tickers"""
    u = pd.Series({t: stable_u01(t) for t in universe})
    df = pd.DataFrame(index=universe)
    df["PE"]        = 12 + 25 * u
    df["PB"]        = 0.8 + 6 * u
    df["EV_EBITDA"] = 6 + 18 * u
    df["ROE"]       = 5 + 25 * u
    df["NetMargin"] = 3 + 22 * u
    df["DebtEquity"] = 0.2 + 1.5 * u
    return df

# -----------------------------
# Fetch fundamentals
# -----------------------------
def fetch_fundamentals(tickers: list) -> pd.DataFrame:
    """
    Fetch basic fundamentals via yfinance.
    Returns placeholder DataFrame if Yahoo fails.
    """
    df_list = []
    for t in tickers:
        try:
            t_upper = str(t).upper()
            info = yf.Ticker(t_upper).info
            row = {
                "PE": info.get("trailingPE", None),
                "PB": info.get("priceToBook", None),
                "EV_EBITDA": info.get("enterpriseToEbitda", None),
                "ROE": info.get("returnOnEquity", None),
                "NetMargin": info.get("netMargins", None),
                "DebtEquity": info.get("debtToEquity", None),
            }
            df_list.append(pd.Series(row, name=t_upper))
        except Exception:
            # If fetch fails, use placeholders
            df_list.append(pd.Series(index=["PE","PB","EV_EBITDA","ROE","NetMargin","DebtEquity"], name=t))

    if df_list:
        df = pd.DataFrame(df_list)
        # Fill missing with placeholders
        missing_tickers = df.index[df.isna().any(axis=1)]
        if len(missing_tickers) > 0:
            df.update(make_placeholder_financials(missing_tickers))
        return df
    else:
        return make_placeholder_financials(tickers)

__all__ = ["fetch_fundamentals", "stable_u01", "make_placeholder_financials"]
