# src/features/fundamentals.py
import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
from .prices import stable_u01

REQUIRED_COLUMNS = ["PE", "PB", "EV_EBITDA", "ROE", "NetMargin", "DebtEquity"]

def fetch_fundamentals(tickers: list[str]) -> pd.DataFrame:
    """
    Fetch fundamentals from Yahoo Finance for a list of tickers.
    Always returns a DataFrame with REQUIRED_COLUMNS. Missing data is filled with placeholders.

    Args:
        tickers: List of ticker symbols

    Returns:
        pd.DataFrame indexed by tickers with columns PE, PB, EV_EBITDA, ROE, NetMargin, DebtEquity
    """
    df = pd.DataFrame(index=tickers, columns=REQUIRED_COLUMNS, dtype=float)

    for t in tickers:
        try:
            st.info(f"Fetching fundamentals for {t}")
            yf_ticker = yf.Ticker(t)
            info = yf_ticker.info

            df.at[t, "PE"] = info.get("trailingPE", np.nan)
            df.at[t, "PB"] = info.get("priceToBook", np.nan)
            df.at[t, "EV_EBITDA"] = info.get("enterpriseToEbitda", np.nan)
            df.at[t, "ROE"] = info.get("returnOnEquity", np.nan)
            df.at[t, "NetMargin"] = info.get("profitMargins", np.nan)
            df.at[t, "DebtEquity"] = info.get("debtToEquity", np.nan)

        except Exception as e:
            st.warning(f"Could not fetch fundamentals for {t}: {e}")

    # Fill missing values with deterministic placeholders
    for col in REQUIRED_COLUMNS:
        missing = df[col].isna()
        if missing.any():
            st.warning(f"Filling missing {col} with placeholders for {missing.sum()} tickers.")
            df.loc[missing, col] = [make_placeholder_value(t, col) for t in df.index[missing]]

    return df

def make_placeholder_value(ticker: str, column: str) -> float:
    """
    Deterministic placeholder for a given ticker and column.
    """
    base = {
        "PE": 15,
        "PB": 2,
        "EV_EBITDA": 10,
        "ROE": 0.15,
        "NetMargin": 0.10,
        "DebtEquity": 0.5
    }
    u = stable_u01(ticker)
    # Slight variation based on ticker
    return base.get(column, 1.0) * (0.8 + 0.4 * u)
