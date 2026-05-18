import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

def load_calendar():
    return pd.read_csv(RAW / "calendar_events.csv", parse_dates=["date"])

def load_assignments():
    return pd.read_csv(RAW / "assignments.csv", parse_dates=["due_date"])

def load_shifts():
    return pd.read_csv(RAW / "shifts.csv", parse_dates=["date"])
