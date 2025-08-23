import pandas as pd

def compute_quality_scores(df: pd.DataFrame) -> pd.Series:
    """
    Compute quality factor score based on ROE, NetMargin, and DebtEquity.
    Automatically handles missing columns by creating placeholders.
    Higher ROE/NetMargin is better; lower DebtEquity is better.
    """
    # Ensure required columns exist
    for col in ["ROE", "NetMargin", "DebtEquity"]:
        if col not in df.columns:
            df[col] = 0  # fallback placeholder

    # z-scores (higher = better)
    df["ROE_z"] = (df["ROE"] - df["ROE"].mean()) / (df["ROE"].std() + 1e-9)
    df["NetMargin_z"] = (df["NetMargin"] - df["NetMargin"].mean()) / (df["NetMargin"].std() + 1e-9)
    df["DebtEquity_z"] = -(df["DebtEquity"] - df["DebtEquity"].mean()) / (df["DebtEquity"].std() + 1e-9)

    quality_score = df[["ROE_z", "NetMargin_z", "DebtEquity_z"]].mean(axis=1)
    return quality_score
