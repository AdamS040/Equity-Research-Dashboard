import pandas as pd

def compute_value_scores(financials: pd.DataFrame) -> pd.Series:
    """
    Compute Value factor scores based on common ratios:
    - Price to Earnings (P/E)
    - Price to Book (P/B)
    - EV/EBITDA
    Lower ratios = better value.
    Input:
        financials: DataFrame with columns ['PE', 'PB', 'EV_EBITDA']
    Output:
        Series of z-scored value scores
    """
    df = financials.copy()
    df["PE_z"] = -(df["PE"] - df["PE"].mean()) / df["PE"].std()
    df["PB_z"] = -(df["PB"] - df["PB"].mean()) / df["PB"].std()
    df["EVEBITDA_z"] = -(df["EV_EBITDA"] - df["EV_EBITDA"].mean()) / df["EV_EBITDA"].std()

    return df[["PE_z", "PB_z", "EVEBITDA_z"]].mean(axis=1)
