import pandas as pd
from ml.train import load_model
from ml.features import add_rolling_features, BASE_COLS


def predict_all_weeks(df):
    model, feature_names = load_model()

    df = add_rolling_features(df).dropna()
    X  = df[feature_names]

    df = df.copy()
    df["risk_score"] = model.predict_proba(X)[:, 1]
    df["predicted"]  = model.predict(X)

    # bucket into Low / Medium / High
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[0, 0.35, 0.65, 1.0],
        labels=["Low", "Medium", "High"]
    )

    cols = ["week_start", "week_number", "total_workload_hours",
            "assignments_due", "shift_hours", "has_exam",
            "risk_score", "predicted", "risk_level"]

    return df[cols]
