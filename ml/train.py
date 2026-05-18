import json
import pickle
from pathlib import Path

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_PATH   = Path("data/processed/model.pkl")
METRICS_PATH = Path("data/processed/metrics.json")


def train(X, y):
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    # scaler + gradient boosting wrapped in a pipeline
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42,
        ))
    ])

    # 5-fold cross validation to see how well it generalizes
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1_scores  = cross_val_score(model, X, y, cv=cv, scoring="f1")
    auc_scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")

    # train on all data
    model.fit(X, y)
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]

    print(f"\nCV F1  : {f1_scores.mean():.4f} (+/- {f1_scores.std():.4f})")
    print(f"CV AUC : {auc_scores.mean():.4f} (+/- {auc_scores.std():.4f})")
    print(f"\n{classification_report(y, preds, target_names=['Normal', 'High Workload'])}")

    # save feature importances
    clf = model.named_steps["clf"]
    importances = sorted(
        zip(X.columns, clf.feature_importances_),
        key=lambda x: x[1], reverse=True
    )

    metrics = {
        "cv_f1_mean":  round(float(f1_scores.mean()), 4),
        "cv_f1_std":   round(float(f1_scores.std()),  4),
        "cv_auc_mean": round(float(auc_scores.mean()), 4),
        "cv_auc_std":  round(float(auc_scores.std()),  4),
        "train_f1":    round(float(f1_score(y, preds)), 4),
        "train_auc":   round(float(roc_auc_score(y, probs)), 4),
        "top_features": [
            {"feature": k, "importance": round(float(v), 4)}
            for k, v in importances[:10]
        ]
    }

    # save model and metrics
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "features": list(X.columns)}, f)

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"model saved to {MODEL_PATH}")
    return model, metrics


def load_model():
    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)
    return saved["model"], saved["features"]
