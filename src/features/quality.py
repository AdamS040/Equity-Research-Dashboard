import pandas as pd

def compute_quality_scores(financials: pd.DataFrame) -> pd.Series:
    """
    Compute Quality factor scores:
    - Return on Equity (ROE)
    - Net Margin
    - Debt/Equity (lower is better)
    Input:
        financials: DataFrame with ['ROE', 'NetMargin', 'DebtEquity']
    Output:
        Series of z-scored quality scores
    """
    df = financials.copy()
    df["ROE_z"] = (df["ROE"] - df["ROE"].mean()) / df["ROE"].std()
    df["NetMargin_z"] = (df["NetMargin"] - df["NetMargin"].mean()) / df["NetMargin"].std()
    df["DE_z"] = -(df["DebtEquity"] - df["DebtEquity"].mean()) / df["DebtEquity"].std()

    return df[["ROE_z", "NetMargin_z", "DE_z"]].mean(axis=1)
