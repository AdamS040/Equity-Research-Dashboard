import streamlit as st
import pandas as pd
import yfinance as yf
from src.features.value import value_score
from src.backtest.engine import backtest_top_n
from src.backtest.metrics import sharpe_ratio, max_drawdown
from src.viz.plots import plot_equity_curve
import plotly.express as px

st.set_page_config(page_title="Equity Tear Sheet", layout="wide")
st.title("Equity Research Dashboard – Tear Sheet MVP")

# -----------------------------
# 1. Universe Selection
# -----------------------------
st.sidebar.header("Universe & Parameters")
tickers_input = st.sidebar.text_area(
    "Enter tickers (comma separated):", "AAPL, MSFT, GOOG, AMZN, META"
)
tickers = [t.strip().upper() for t in tickers_input.split(",")]

top_n = st.sidebar.slider("Top-N stocks to show/backtest", 1, min(20, len(tickers)), 5)

start_date = st.sidebar.date_input("Start date", pd.to_datetime("2018-01-01"))

# -----------------------------
# 2. Download Data
# -----------------------------
st.sidebar.info("Fetching price data...")
prices = yf.download(tickers, start=start_date)["Adj Close"]
st.sidebar.success("Data fetched!")

# -----------------------------
# 3. Factor Calculation
# -----------------------------
# For MVP, fake fundamentals (replace with real later)
book_values = prices / 3
scores = pd.DataFrame({t: value_score(prices[t], book_values[t]) for t in tickers})

st.subheader("Factor Scores (latest date)")
latest_scores = scores.iloc[-1].sort_values(ascending=False)
st.dataframe(latest_scores)

# -----------------------------
# 4. Filter Top-N & Backtest
# -----------------------------
results = backtest_top_n(prices, scores, top_n=top_n)
st.subheader(f"Top-{top_n} Portfolio Backtest")
st.write(f"Sharpe: {sharpe_ratio(results['daily_return']):.2f}")
st.write(f"Max Drawdown: {max_drawdown(results['equity_curve']):.2%}")

# Plot equity curve with Plotly
fig = px.line(results, y="equity_curve", title="Portfolio Equity Curve")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 5. Individual Stock Tear Sheet
# -----------------------------
st.subheader("Individual Stock Analysis")
selected_stock = st.selectbox("Select a stock", tickers)

st.write(f"Latest Factor Score (P/B): {scores[selected_stock].iloc[-1]:.2f}")

fig_stock = px.line(prices[selected_stock], title=f"{selected_stock} Price Chart")
st.plotly_chart(fig_stock, use_container_width=True)
