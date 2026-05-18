import pandas as pd

# these are the base columns we'll compute rolling stats for
BASE_COLS = [
    "class_hours",
    "event_count",
    "assignments_due",
    "assignment_hours",
    "has_exam",
    "shift_count",
    "shift_hours",
]


def add_rolling_features(df):
    df = df.copy().sort_values("week_start").reset_index(drop=True)

    for col in BASE_COLS:
        # 1-week lookback (what was last week like?)
        df[f"{col}_last1w_avg"] = df[col].shift(1).rolling(1, min_periods=1).mean()
        df[f"{col}_last1w_sum"] = df[col].shift(1).rolling(1, min_periods=1).sum()

        # 4-week lookback (~30 days, how busy has the past month been?)
        df[f"{col}_last4w_avg"] = df[col].shift(1).rolling(4, min_periods=1).mean()
        df[f"{col}_last4w_sum"] = df[col].shift(1).rolling(4, min_periods=1).sum()

        # trend: is this week more or less busy than last week?
        df[f"{col}_trend"] = df[col] - df[col].shift(1).fillna(0)

    return df


def get_features_and_labels(df):
    df = add_rolling_features(df)
    df = df.dropna()

    # all the rolling and trend columns we just created
    engineered = [c for c in df.columns if "_last" in c or "_trend" in c]
    all_features = BASE_COLS + engineered

    X    = df[all_features]
    y    = df["high_workload"]
    meta = df[["week_start", "week_number", "total_workload_hours"]]

    return X, y, meta, df
