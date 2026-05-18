# CampusPulse

A personal workload analytics tool I built to track how busy my semester is and predict high-workload weeks before they hit.

It pulls together three data sources - my class schedule, assignment deadlines, and part-time work shifts - runs them through an ETL pipeline, stores them in a database, and trains a machine learning model to flag which weeks are going to be rough.

---

## What it does

- **ETL pipeline** - reads calendar, assignment, and shift data from CSVs, cleans and aggregates into a weekly summary, stores everything in SQLite
- **Feature engineering** - builds rolling 7-day and 30-day window features (how busy was last week? last month?) plus trend features
- **ML model** - Gradient Boosting classifier trained to predict high-workload weeks, evaluated with F1 score and AUC-ROC
- **Streamlit dashboard** - visualizes workload trends, risk scores, assignment heatmap, and feature importances

---

## Project structure

```
campuspulse/
├── data/
│   ├── raw/                  # raw CSVs (calendar, assignments, shifts)
│   ├── processed/            # saved model + metrics
│   └── campuspulse.db        # SQLite database
├── etl/
│   ├── ingest.py             # read CSVs into DataFrames
│   ├── transform.py          # aggregate into weekly table
│   └── load.py               # save/load from database
├── ml/
│   ├── features.py           # rolling window feature engineering
│   ├── train.py              # model training + evaluation
│   └── predict.py            # generate risk predictions
├── dashboard/
│   └── app.py                # Streamlit dashboard
├── generate_data.py          # generates synthetic semester data
├── run_pipeline.py           # runs everything end to end
└── requirements.txt
```

---

## Setup and run

```bash
# clone the repo
git clone https://github.com/<your-username>/campuspulse.git
cd campuspulse

# create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# install dependencies
pip install -r requirements.txt

# run the pipeline (generates data, trains model, saves predictions)
python run_pipeline.py

# launch the dashboard
streamlit run dashboard/app.py
```

Dashboard runs at `http://localhost:8501`

---

## Database

Uses SQLite by default - no setup needed, the `.db` file gets created automatically.

To use PostgreSQL instead:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/campuspulse"
python run_pipeline.py
```

---

## Tech stack

- Python, Pandas, NumPy
- scikit-learn (GradientBoostingClassifier)
- SQLAlchemy + SQLite / PostgreSQL
- Streamlit + Plotly
---

## Author

Shashank Reddy Peta  
M.S. Computer Science, University of South Florida  
shashankreddypeta@usf.edu
TAMPA, FLORIDA

## Status
Active development
