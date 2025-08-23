import sys
from pathlib import Path

# Make 'src' importable when running via "streamlit run"
src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import hashlib
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

st.set_page_config(page_title="Multi-Factor Screener", layout="wide")
st.title("📊 Multi-Factor Equity Screener")

# -----------------------------
# Helpers
# -----------------------------
def clean_tickers(raw: str) -> list[str]:
    return sorted({t.strip().upper() for t in raw.split(",") if t.strip()})

def stable_u01(s: str) -> float:
    # deterministic pseudo-random in [0,1) per ticker (no internet/fundamentals needed for demo)
    h = hashlib.sha1(s.encode()).hexdigest()
    return (int(h[:10], 16) % 1_000_000) / 1_000_000.0

def make_placeholder_financials(universe: list[str]) -> pd.DataFrame:
    u = pd.Series({t: stable_u01(t) for t in universe})
    df = pd.DataFrame(index=universe)
    # Value proxies (deterministic variation)
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
w_value   = st.sidebar.slider("Value",          0.0, 1.0, 0.25, 0.05)
w_quality = st.sidebar.slider("Quality",        0.0, 1.0, 0.25, 0.05)
w_mom     = st.sidebar.slider("Momentum",       0.0, 1.0, 0.25, 0.05)
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

    st.info("Fetching price data…")
    data = yf.download(tickers, start=start_date, auto_adjust=True, progress=False)
    if data.empty:
        st.error("No price data returned. Check tickers and date range.")
        st.stop()

    prices = data["Adj Close"] if "Adj Close" in data else data
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    # Drop tickers with too many NaNs or too short history
    prices = prices.dropna(how="all", axis=1)
    min_rows = 130  # ~6 months
    valid_cols = [c for c in prices.columns if prices[c].notna().sum() >= min_rows]
    dropped = sorted(set(prices.columns) - set(valid_cols))
    prices = prices[valid_cols]

    if not len(prices.columns):
        st.error("All tickers were dropped due to insufficient data. Try a longer date range.")
        st.stop()
    if dropped:
        st.warning(f"Dropped {len(dropped)} ticker(s) with insufficient data: {', '.join(dropped)}")

    universe = list(prices.columns)

    # Placeholder fundamentals aligned to actual universe
    financials = make_placeholder_financials(universe)

    # -----------------------------
    # Factor scores
    # -----------------------------
    try:
        df = pd.DataFrame(index=universe)
        df["Value"]      = compute_value_scores(financials)
        df["Quality"]    = compute_quality_scores(financials)
        df["Momentum"]   = compute_momentum_scores(prices)
        df["Volatility"] = compute_vol_scores(prices)
        df = df.dropna(how="any")
    except ValueError as e:
        st.error(f"Factor computation error: {e}")
        st.stop()

    # Weighted score & ranking
    df["Final Score"] = (
        w_value * df["Value"] +
        w_quality * df["Quality"] +
        w_mom * df["Momentum"] +
        w_vol * df["Volatility"]
    )
    df = df.sort_values("Final Score", ascending=False)

    st.subheader("Top Picks")
    top_picks = df.head(top_n)
    st.dataframe(top_picks, use_container_width=True)

    # Bar chart of top picks
    fig = px.bar(
        top_picks.reset_index(),
        x="index", y="Final Score",
        hover_data=["Value", "Quality", "Momentum", "Volatility"],
        title="Top N Factor Picks"
    )
    fig.update_layout(xaxis_title="Ticker", yaxis_title="Weighted Score")
    st.plotly_chart(fig, use_container_width=True)

    # Backtest (equal-weight top N)
    st.subheader("Backtest")
    try:
        eq_curve = backtest_top_n(list(top_picks.index), start=str(prices.index.min().date()))
        st.plotly_chart(plot_equity_curve(eq_curve), use_container_width=True)
    except Exception as e:
        st.warning(f"Backtest skipped: {e}")
