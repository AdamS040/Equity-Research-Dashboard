import hashlib
import pandas as pd
import yfinance as yf

# -----------------------------
# Helpers
# -----------------------------
def stable_u01(s: str) -> float:
    """Deterministic pseudo-random in [0,1) per ticker"""
    if not isinstance(s, str):
        s = str(s)
    h = hashlib.sha1(s.encode()).hexdigest()
    return (int(h[:10], 16) % 1_000_000) / 1_000_000.0

def make_placeholder_financials(universe: list[str]) -> pd.DataFrame:
    """Return a DataFrame of dummy fundamentals for tickers"""
    u = pd.Series({str(t): stable_u01(t) for t in universe})
    df = pd.DataFrame(index=[str(t) for t in universe])
    # Value proxies
    df["PE"]        = 12 + 25 * u
    df["PB"]        = 0.8 + 6 * u
    df["EV_EBITDA"] = 6 + 18 * u
    # Quality proxies
    df["ROE"]        = 5 + 25 * u
    df["NetMargin"]  = 3 + 22 * u
    df["DebtEquity"] = 0.2 + 1.5 * u
    return df

# -----------------------------
# Fetch fundamentals from Yahoo
# -----------------------------
def fetch_fundamentals(tickers: list[str]) -> pd.DataFrame:
    """
    Fetch basic fundamentals via yfinance.
    Returns placeholder DataFrame if Yahoo fails or any field missing.
    """
    df_list = []
    for t in tickers:
        try:
            t_upper = str(t).upper()
            stock = yf.Ticker(t_upper)
            info = stock.info

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
            # On failure, append empty series
            df_list.append(pd.Series(
                index=["PE","PB","EV_EBITDA","ROE","NetMargin","DebtEquity"], 
                name=str(t)
            ))

    if df_list:
        df = pd.DataFrame(df_list)
        # Fill missing values with placeholders for tickers that failed
        missing = df.index[df.isna().any(axis=1)]
        if len(missing) > 0:
            placeholder = make_placeholder_financials(missing)
            df.update(placeholder)
        return df
    else:
        # If nothing fetched, return full placeholders
        return make_placeholder_financials(tickers)

# Explicitly expose these for import
__all__ = ["fetch_fundamentals", "stable_u01", "make_placeholder_financials"]
