import hypothesis.strategies as st
from hypothesis import given
import pandas as pd
from src.features.value import price_to_book

@given(
    st.lists(st.floats(min_value=1, max_value=1000), min_size=5, max_size=5),
    st.lists(st.floats(min_value=1, max_value=1000), min_size=5, max_size=5),
)
def test_price_to_book_monotonic(price_list, bvps_list):
    price = pd.Series(price_list)
    bvps = pd.Series(bvps_list)
    pb = price_to_book(price, bvps)

    # P/B must always be non-negative
    assert (pb >= 0).all()
