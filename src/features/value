import pandas as pd

def price_to_book(price: pd.Series, book_value_per_share: pd.Series) -> pd.Series:
    """Compute lagged Price/Book ratio (Value factor)."""
    return price / book_value_per_share

def value_score(price: pd.Series, book_value_per_share: pd.Series) -> pd.Series:
    """
    Convert P/B into a ranking score (lower P/B = higher score).
    Output: cross-sectionally standardized z-score.
    """
    pb = price_to_book(price, book_value_per_share)
    score = -1 * (pb - pb.mean()) / pb.std()
    return score
