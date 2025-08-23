import streamlit as st
import pandas as pd
import yfinance as yf
from src.features.momentum import compute_mom_scores
from src.features.volatility import compute_vol_scores
from src.features.fundamentals import fetch_fundamentals


# -------------------------
# Universe setup
# -------------------------
st.set_page_config(page_title="Multi-Factor Screener", layout="wide")

st.title("📊 Multi-Factor Screener")

universe = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "GS", "NFLX"]


# -------------------------
# Price data
# -------------------------
@st.cache_data
def load_prices(tickers):
    return yf.download(tickers, period="5y")["Adj Close"]

prices = load_prices(universe)


# -------------------------
# Factor data
# -------------------------
st.subheader("Fetching Factor Data...")

try:
    financials = fetch_fundamentals(universe)
except Exception as e:
    st.warning(f"⚠️ Fundamentals fetch failed ({e}). Using zeros.")
    financials = pd.DataFrame(0, index=universe, columns=["Value_Score", "Quality_Score", "Leverage_Score"])

# Quant features
momentum = compute_mom_scores(prices)
volatility = compute_vol_scores(prices)

df = financials.copy()
df["Momentum"] = momentum
df["Volatility"] = volatility

st.write("Preview of Factor Data:", df.head())


# -------------------------
# Sliders for weights
# -------------------------
st.sidebar.header("⚖️ Factor Weights")

w_value = st.sidebar.slider("Value", 0.0, 1.0, 0.2)
w_quality = st.sidebar.slider("Quality", 0.0, 1.0, 0.2)
w_leverage = st.sidebar.slider("Leverage", 0.0, 1.0, 0.2)
w_mom = st.sidebar.slider("Momentum", 0.0, 1.0, 0.2)
w_vol = st.sidebar.slider("Low Volatility", 0.0, 1.0, 0.2)

weights = {
    "Value_Score": w_value,
    "Quality_Score": w_quality,
    "Leverage_Score": w_leverage,
    "Momentum": w_mom,
    "Volatility": w_vol,
}


# -------------------------
# Compute composite score
# -------------------------
scores = pd.Series(0, index=universe, dtype=float)

for f, w in weights.items():
    if f in df.columns:
        scores += w * df[f].fillna(0)

ranked = pd.DataFrame({
    "Score": scores,
    "Value": df["Value_Score"],
    "Quality": df["Quality_Score"],
    "Leverage": df["Leverage_Score"],
    "Momentum": df["Momentum"],
    "Volatility": df["Volatility"],
}).sort_values("Score", ascending=False)


# -------------------------
# Display
# -------------------------
st.subheader("🏆 Ranked Stocks")
st.dataframe(ranked.style.background_gradient(cmap="Blues"))

st.bar_chart(ranked["Score"])
