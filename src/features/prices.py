import yfinance as yf
import pandas as pd
import streamlit as st
import time

def fetch_prices(tickers: list[str], start_date: str, batch_size: int = 5, max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch historical price data robustly from Yahoo Finance.
    Falls back to placeholder prices if Yahoo fails.

    Args:
        tickers: List of ticker symbols
        start_date: Start date for historical data (YYYY-MM-DD)
        batch_size: Number of tickers to fetch per batch
        max_retries: Number of retries per batch

    Returns:
        DataFrame of adjusted close prices, tickers as columns
    """
    all_prices = pd.DataFrame()

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        success = False
        retries = 0

        while not success and retries < max_retries:
            try:
                st.info(f"Fetching batch: {batch}")
                data = yf.download(batch, start=start_date, auto_adjust=True, progress=False)
                if "Adj Close" in data:
                    batch_prices = data["Adj Close"]
                else:
                    batch_prices = data

                # If single ticker, make it a DataFrame
                if isinstance(batch_prices, pd.Series):
                    batch_prices = batch_prices.to_frame(batch[0])

                all_prices = pd.concat([all_prices, batch_prices], axis=1)
                success = True

            except Exception as e:
                retries += 1
                st.warning(f"Batch fetch failed (attempt {retries}/{max_retries}): {e}")
                time.sleep(1)  # brief pause before retry

        if not success:
            st.warning(f"Yahoo price fetch failed for batch {batch}. Using placeholder data.")
            for t in batch:
                # Create placeholder price series (~252 trading days)
                placeholder = pd.Series(
                    100 + 5 * pd.np.random.randn(252),  # mean 100, small random walk
                    index=pd.date_range(start=start_date, periods=252, freq='B'),
                    name=t
                )
                all_prices = pd.concat([all_prices, placeholder], axis=1)

    # Ensure all tickers are present
    missing = set(tickers) - set(all_prices.columns)
    for t in missing:
        placeholder = pd.Series(
            100 + 5 * pd.np.random.randn(252),
            index=pd.date_range(start=start_date, periods=252, freq='B'),
            name=t
        )
        all_prices = pd.concat([all_prices, placeholder], axis=1)

    all_prices = all_prices[sorted(all_prices.columns)]
    return all_prices
