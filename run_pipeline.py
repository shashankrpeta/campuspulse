import subprocess
import sys
from pathlib import Path

# step 0 - generate raw data if it doesn't exist yet
if not Path("data/raw/assignments.csv").exists():
    print("generating raw data...")
    subprocess.run([sys.executable, "generate_data.py"], check=True)
else:
    print("raw data already exists, skipping generation")

# step 1 - ETL
print("\n--- ETL ---")
from etl.ingest import load_calendar, load_assignments, load_shifts
from etl.transform import build_weekly_table
from etl.load import save_table

calendar    = load_calendar()
assignments = load_assignments()
shifts      = load_shifts()

print(f"loaded {len(calendar)} calendar events")
print(f"loaded {len(assignments)} assignments")
print(f"loaded {len(shifts)} shifts")

weekly = build_weekly_table(calendar, assignments, shifts)
print(f"built weekly table: {len(weekly)} weeks")

save_table(calendar,    "calendar_events")
save_table(assignments, "assignments")
save_table(shifts,      "shifts")
save_table(weekly,      "weekly_workload")

# step 2 - train model
print("\n--- ML Training ---")
from ml.features import get_features_and_labels
from ml.train import train

X, y, meta, df_full = get_features_and_labels(weekly)
model, metrics = train(X, y)

# step 3 - generate predictions and save
print("\n--- Predictions ---")
from ml.predict import predict_all_weeks
predictions = predict_all_weeks(weekly)
save_table(predictions, "predictions")

print("\ndone! run the dashboard with:")
print("  streamlit run dashboard/app.py")
