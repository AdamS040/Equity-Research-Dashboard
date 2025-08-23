import sys
from pathlib import Path
import hashlib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Ensure 'src' is importable
src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Imports from repo
from features.value import compute_value_scores
from features.quality import compute_quality_scores
from features.momentum import compute_momentum_scores
from features.volatility import compute_vol_scores
from backtest.engine import backtest_top_n
from viz.plots import plot_equity_curve

from src.features.fundamentals import fetch_fundamentals
from src.features.prices import fetch_prices

st.set_page_config(page_title="Multi-Factor Screener", layout="wide")
st.title("📊 Multi-Factor Equity Screener")

# -----------------------------
# Helpers
# -----------------------------
def clean_tickers(raw: str) -> list[str]:
    return sorted({t.strip().upper() for t in raw.split(",") if t.strip()})

def stable_u01(s: str) -> float:
    """Deterministic pseudo-random in [0,1) per ticker."""
    if isinstance(s, tuple):
        s = s[0]
    return int(hashlib.sha1(str(s).encode()).hexdigest()[:10], 16) % 1_000_000 / 1_000_000.0

def make_placeholder_financials(universe: list[str]) -> pd.DataFrame:
    """Always returns all necessary columns for factor computation."""
    u = pd.Series({t: stable_u01(t) for t in universe})
    df = pd.DataFrame(index=universe)
    # Value proxies
    df["PE"] = 12 + 25 * u
    df["PB"] = 0.8 + 6 * u
    df["EV_EBITDA"] = 6 + 18 * u
    # Quality proxies
    df["ROE"] = 5 + 25 * u
    df["NetMargin"] = 3 + 22 * u
    df["DebtEquity"] = 0.2 + 1.5 * u
    return df

# -----------------------------
# Sidebar - Factor Weights
# -----------------------------
st.sidebar.header("Factor Weights")
w_value   = st.sidebar.slider("Value", 0.0, 1.0, 0.25, 0.05)
w_quality = st.sidebar.slider("Quality", 0.0, 1.0, 0.25, 0.05)
w_mom     = st.sidebar.slider("Momentum", 0.0, 1.0, 0.25, 0.05)
w_vol     = st.sidebar.slider("Low Volatility", 0.0, 1.0, 0.25, 0.05)

# -----------------------------
# Universe & settings
# -----------------------------
raw = st.text_input("Enter tickers (comma-separated)", "AAPL, MSFT, AMZN, TSLA, META, NVDA, GOOGL")
tickers = clean_tickers(raw)
top_n = st.slider("Top N Stocks", 3, 25, 8, 1)
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))

run = st.button("Run Screener")

if run:
    if not tickers:
        st.error("Please enter at least one valid ticker.")
        st.stop()

    # -----------------------------
    # Fetch prices robustly
    # -----------------------------
    st.info("Fetching price data…")
    prices = fetch_prices(tickers, start=str(start_date))
    st.success(f"Fetched price data for {len(prices.columns)} tickers.")

    # -----------------------------
    # Fetch fundamentals robustly
    # -----------------------------
    st.info("Fetching fundamentals…")
    try:
        financials = fetch_fundamentals(tickers)
        missing_cols = {"PE", "PB", "EV_EBITDA", "ROE", "NetMargin", "DebtEquity"} - set(financials.columns)
        if missing_cols:
            st.warning(f"Missing columns {missing_cols}, using placeholders for these.")
            placeholders = make_placeholder_financials(tickers)
            for col in missing_cols:
                financials[col] = placeholders[col]
    except Exception as e:
        st.warning(f"Fundamentals unavailable, using placeholders. ({e})")
        financials = make_placeholder_financials(tickers)

    # -----------------------------
    # Compute factor scores
    # -----------------------------
    try:
        df = pd.DataFrame(index=tickers)
        df["Value_Score"]   = compute_value_scores(financials)
        df["Quality_Score"] = compute_quality_scores(financials)
        df["Momentum"]      = compute_momentum_scores(prices)
        df["Volatility"]    = compute_vol_scores(prices)
        df = df.dropna(how="any")
    except Exception as e:
        st.error(f"Factor computation error: {e}")
        st.stop()

    # -----------------------------
    # Weighted scoring
    # -----------------------------
    weights = {
        "Value_Score": w_value,
        "Quality_Score": w_quality,
        "Momentum": w_mom,
        "Volatility": w_vol,
    }
    scores = pd.Series(0, index=df.index, dtype=float)
    for factor, w in weights.items():
        if factor in df.columns:
            scores += w * df[factor].fillna(0)
    df["Final Score"] = scores
    df = df.sort_values("Final Score", ascending=False)

    # -----------------------------
    # Display top picks
    # -----------------------------
    st.subheader("Top Picks")
    top_picks = df.head(top_n)
    st.dataframe(top_picks, use_container_width=True)

    # Bar chart
    fig = px.bar(
        top_picks.reset_index(),
        x="index", y="Final Score",
        hover_data=["Value_Score", "Quality_Score", "Momentum", "Volatility"],
        title="Top N Factor Picks"
    )
    fig.update_layout(xaxis_title="Ticker", yaxis_title="Weighted Score")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Backtest top N
    # -----
