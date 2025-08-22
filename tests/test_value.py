import pandas as pd
from src.features.value import price_to_book

def test_price_to_book_inverse_relation():
    price = pd.Series([100, 100, 100])
    bvps = pd.Series([10, 20, 50])  # higher BVPS = lower P/B
    pb = price_to_book(price, bvps)
    assert pb[0] > pb[1] > pb[2]

def test_price_to_book_no_div_zero():
    price = pd.Series([100])
    bvps = pd.Series([0.01])  # tiny denominator
    pb = price_to_book(price, bvps)
    assert pb.iloc[0] > 0
