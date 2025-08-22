import pytest
from src.data.fetch import get_price_data

def test_price_fetch_shape():
    df = get_price_data("AAPL", start="2020-01-01")
    assert not df.empty
    assert "Close" in df.columns

def test_price_fetch_dates_sorted():
    df = get_price_data("AAPL", start="2020-01-01")
    assert df.index.is_monotonic_increasing
