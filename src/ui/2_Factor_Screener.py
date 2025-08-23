# src/ui/2_Factor_Screener.py
import sys
from pathlib import Path

# Make 'src' importable when running via "streamlit run"
src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px

from features.value import compute_value_scores
from features.quality import compute_quality_scores
from features.momentum import compute_momentum_scores
from features.volatility import compute_vol_scores
from backtest.engine import backtest_top_n
from viz.plots import plot_equity_curve
from src.features.fundamentals import fetch_fundamentals, stable_u01, make_placeholder_financials

st.set_page_config(page_title="Multi-Factor Screener", layout="wide")
st.title("📊 Multi-Factor Equity Screener")

# -----------------------------
# Helpers
# -----------------------------
def clean_tickers(raw: str) -> list[str]:
    return sorted({t.strip().upper() for t in raw.split(",") if t.strip()})

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
raw = st.text_input(
    "Enter tickers (comma-separated)", 
    "AAPL, MSFT, AMZN, TSLA, META, NVDA, GOOGL"
)
tickers = clean_tickers(raw)
top_n = st.slider("Top N Stocks", 3, 25, 8, 1)
start_date = st.date_input("Start date", pd.to_datetime("2020-01-01"))

run = st.button("Run Screener")

if run:
    if not tickers:
        st.error("Please enter at least one valid ticker.")
        st.stop()

    # -----------------------------
    # Fetch price data robustly
    # -----------------------------
    st.info("Fetching price data…")
    try:
        data = yf.download(tickers, start=start_date, auto_adjust=True, progress=False)
        if data.empty:
            raise ValueError("No data returned")

        # Use Adjusted Close if available
        prices = data["Adj Close"] if "Adj Close" in data else data

        # Flatten MultiIndex columns
        if isinstance(prices.columns, pd.MultiIndex):
            prices.columns = [
                col[1] if isinstance(col, tuple) else col for col in prices.columns
            ]

    except Exception as e:
        st.warning(f"Yahoo price fetch failed ({e}). Using placeholder price data.")
        # Placeholder: 252 trading days, 1 year, 5% noise
        prices = pd.DataFrame(
            {t: 100 + pd.Series(range(252)) + pd.Series([stable_u01(t)*10 for _ in range(252)])
             for t in tickers}
        )

    # -----------------------------
    # Drop tickers with insufficient data
    # -----------------------------
    min_rows = 130
    valid_cols = []
    for c in prices.columns:
        non_na_count = prices[c].dropna().shape[0]
        if non_na_count >= min_rows:
            valid_cols.append(c)
    dropped = sorted(set(prices.columns) - set(valid_cols))
    prices = prices[valid_cols]

    if not len(prices.columns):
        st.error("All tickers dropped due to insufficient data.")
        st.stop()
    if dropped:
        st.warning(f"Dropped tickers with insufficient data: {', '.join(dropped)}")
    universe = list(prices.columns)

    # -----------------------------
    # Fetch fundamentals
    # -----------------------------
    st.info("Fetching fundamentals…")
    try:
        financials = fetch_fundamentals(universe)
        # Ensure required columns are present
        required_cols = ["PE", "PB", "EV_EBITDA", "ROE", "NetMargin", "DebtEquity"]
        if any(col not in financials.columns for col in required_cols):
            st.warning("Missing fundamentals columns. Using placeholder fundamentals.")
            financials = make_placeholder_financials(universe)
    except Exception as e:
        st.warning(f"Could not fetch fundamentals, using placeholders ({e})")
        financials = make_placeholder_financials(universe)

    # -----------------------------
    # Compute factor scores
    # -----------------------------
    try:
        df = pd.DataFrame(index=universe)
        df["Value_Score"]   = compute_value_scores(financials)
        df["Quality_Score"] = compute_quality_scores(financials)
        df["Momentum"]      = compute_momentum_scores(prices)
        df["Volatility"]    = compute_vol_scores(prices)
        df = df.dropna(how="any")
    except Exception as e:
        st.error(f"Factor computation error: {e}")
        st.stop()

    # -----------------------------
    # Apply factor weights
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

    fig = px.bar(
        top_picks.reset_index(),
        x="index",
        y="Final Score",
        hover_data=["Value_Score", "Quality_Score", "Momentum", "Volatility"],
        title="Top N Factor Picks"
    )
    fig.update_layout(xaxis_title="Ticker", yaxis_title="Weighted Score")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Backtest top N
    # -----------------------------
    st.subheader("Backtest")
    try:
        eq_curve = backtest_top_n(list(top_picks.index), start=str(prices.index.min().date()))
        st.plotly_chart(plot_equity_curve(eq_curve), use_container_width=True)
    except Exception as e:
        st.warning(f"Backtest skipped: {e}")
