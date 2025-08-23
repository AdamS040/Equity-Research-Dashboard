import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

from src.features.value import compute_value_scores
from src.features.quality import compute_quality_scores
from src.features.momentum import compute_momentum_scores
from src.features.volatility import compute_vol_scores
from src.backtest.engine import backtest_top_n
from src.viz.plots import plot_equity_curve

st.title("📊 Multi-Factor Equity Screener")

# Sidebar - Factor Weights
st.sidebar.header("Factor Weights")
w_value = st.sidebar.slider("Value", 0.0, 1.0, 0.25, 0.05)
w_quality = st.sidebar.slider("Quality", 0.0, 1.0, 0.25, 0.05)
w_momentum = st.sidebar.slider("Momentum", 0.0, 1.0, 0.25, 0.05)
w_vol = st.sidebar.slider("Low Volatility", 0.0, 1.0, 0.25, 0.05)

# Universe + settings
tickers = st.text_input("Enter tickers (comma-separated)", "AAPL, MSFT, AMZN, TSLA, META").split(",")
top_n = st.slider("Top N Stocks", 5, 20, 10, 1)

if st.button("Run Screener"):
    prices = yf.download(tickers, period="2y")["Adj Close"]
    financials = pd.DataFrame({
        "PE": [30, 28, 60, 90, 35],
        "PB": [8, 11, 15, 20, 9],
        "EV_EBITDA": [22, 18, 35, 60, 25],
        "ROE": [25, 30, 15, 10, 28],
        "NetMargin": [20, 22, 12, 5, 18],
        "DebtEquity": [0.5, 0.6, 0.9, 1.5, 0.7]
    }, index=[t.strip() for t in tickers])

    df = pd.DataFrame(index=financials.index)
    df["Value"] = compute_value_scores(financials)
    df["Quality"] = compute_quality_scores(financials)
    df["Momentum"] = compute_momentum_scores(prices)
    df["Volatility"] = compute_vol_scores(prices)

    df["Final Score"] = (
        w_value * df["Value"] +
        w_quality * df["Quality"] +
        w_momentum * df["Momentum"] +
        w_vol * df["Volatility"]
    )

    df = df.sort_values("Final Score", ascending=False)
    top_picks = df.head(top_n)

    st.subheader("Top Picks")
    st.dataframe(top_picks)

    fig = px.bar(top_picks, x=top_picks.index, y="Final Score", title="Top N Factor Picks")
    st.plotly_chart(fig)

    eq_curve = backtest_top_n(top_picks.index)
    st.plotly_chart(plot_equity_curve(eq_curve))
    