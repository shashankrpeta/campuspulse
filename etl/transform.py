import pandas as pd


def add_week_start(df, date_col):
    # figure out what Monday of that week is
    df = df.copy()
    df["week_start"] = df[date_col] - pd.to_timedelta(df[date_col].dt.dayofweek, unit="D")
    return df


def build_weekly_table(calendar, assignments, shifts):
    # add week_start to each source
    cal  = add_week_start(calendar,    "date")
    asgn = add_week_start(assignments, "due_date")
    shft = add_week_start(shifts,      "date")

    # how many hours of class per week
    class_hrs = (
        cal[cal["event_type"] == "class"]
        .groupby("week_start")["duration_minutes"]
        .sum()
        .div(60)
        .rename("class_hours")
    )

    # total events per week (classes + clubs + office hours)
    event_cnt = (
        cal.groupby("week_start")["event_id"]
        .count()
        .rename("event_count")
    )

    # assignment stats per week
    asgn_weekly = asgn.groupby("week_start").agg(
        assignments_due  = ("assignment_id",  "count"),
        assignment_hours = ("estimated_hours", "sum"),
        # 1 if there's a midterm or final that week, 0 otherwise
        has_exam         = ("type", lambda x: int(any(t in ["Midterm", "Final Exam"] for t in x)))
    )

    # shift stats per week
    shift_weekly = shft.groupby("week_start").agg(
        shift_count = ("shift_id",     "count"),
        shift_hours = ("hours_worked", "sum")
    )

    # build a row for every monday in the semester
    all_mondays = pd.date_range(
        start=cal["week_start"].min(),
        end=cal["week_start"].max(),
        freq="W-MON"
    )
    weekly = pd.DataFrame(index=all_mondays)
    weekly.index.name = "week_start"

    # join everything together, fill missing weeks with 0
    weekly = weekly.join(class_hrs).join(event_cnt).join(asgn_weekly).join(shift_weekly)
    weekly = weekly.fillna(0)

    # total hours this week = assignment work + shift work
    weekly["total_workload_hours"] = weekly["assignment_hours"] + weekly["shift_hours"]

    # label: 1 if this is a high workload week (top 40% by total hours)
    threshold = weekly["total_workload_hours"].quantile(0.60)
    weekly["high_workload"] = (weekly["total_workload_hours"] >= threshold).astype(int)

    weekly = weekly.reset_index()
    weekly["week_number"] = range(1, len(weekly) + 1)

    return weekly
