from src.data.fetch import get_price_data
from src.features.value import price_to_book

def test_integration_value_factor():
    df = get_price_data("MSFT", start="2020-01-01")
    prices = df["Close"].iloc[-5:]  # last 5 days
    bvps = prices / 10  # fake fundamentals for test
    pb = price_to_book(prices, bvps)
    assert len(pb) == 5
    assert (pb > 0).all()
