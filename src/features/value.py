import pandas as pd

def compute_value_scores(df: pd.DataFrame) -> pd.Series:
    """
    Compute value factor score based on PE, PB, EV/EBITDA if present.
    Automatically creates missing columns with zeros to avoid KeyErrors.
    """
    for col in ["PE", "PB", "EV_EBITDA"]:
        if col not in df.columns:
            df[col] = 0  # fallback placeholder

    # z-scores (higher = better value)
    df["PE_z"] = -(df["PE"] - df["PE"].mean()) / (df["PE"].std() + 1e-9)
    df["PB_z"] = -(df["PB"] - df["PB"].mean()) / (df["PB"].std() + 1e-9)
    if "EV_EBITDA" in df.columns:
        df["EV_EBITDA_z"] = -(df["EV_EBITDA"] - df["EV_EBITDA"].mean()) / (df["EV_EBITDA"].std() + 1e-9)
    else:
        df["EV_EBITDA_z"] = 0

    value_score = df[["PE_z", "PB_z", "EV_EBITDA_z"]].mean(axis=1)
    return value_score
