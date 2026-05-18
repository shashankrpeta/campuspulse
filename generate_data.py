import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

# semester dates
START = date(2025, 1, 13)
END   = date(2025, 5, 2)

# my 5 courses and which days they meet (0=Mon, 1=Tue, etc.)
COURSES = [
    "Data Structures & Algorithms",
    "Operating Systems",
    "Data Networks & Security",
    "Affective Computing",
    "Database Systems",
]

COURSE_DAYS = {
    "Data Structures & Algorithms": [0, 2],
    "Operating Systems":            [1, 3],
    "Data Networks & Security":     [0, 2],
    "Affective Computing":          [1, 3],
    "Database Systems":             [2, 4],
}


def make_calendar_events():
    events = []
    eid = 1
    d = START

    while d <= END:
        # add a class event for each course that meets today
        for course, days in COURSE_DAYS.items():
            if d.weekday() in days:
                events.append({
                    "event_id":         f"EVT{eid:04d}",
                    "event_type":       "class",
                    "title":            course,
                    "date":             d.isoformat(),
                    "start_time":       "10:00" if d.weekday() in [0, 2, 4] else "13:00",
                    "duration_minutes": 75,
                })
                eid += 1

        # club meeting every other monday
        if d.weekday() == 0 and (d - START).days % 14 == 0:
            events.append({
                "event_id":         f"EVT{eid:04d}",
                "event_type":       "club",
                "title":            "ACM Student Chapter",
                "date":             d.isoformat(),
                "start_time":       "17:00",
                "duration_minutes": 60,
            })
            eid += 1

        # sometimes go to office hours on tue/thu
        if d.weekday() in [1, 3] and random.random() < 0.35:
            events.append({
                "event_id":         f"EVT{eid:04d}",
                "event_type":       "office_hours",
                "title":            random.choice(COURSES),
                "date":             d.isoformat(),
                "start_time":       "15:00",
                "duration_minutes": 30,
            })
            eid += 1

        d += timedelta(days=1)

    return events


def make_assignments():
    assignments = []
    aid = 1

    # weeks when each type of assignment is due
    schedule = {
        "Homework":   [2, 3, 4, 5, 6, 8, 10, 11, 12],
        "Quiz":       [2, 4, 6, 8, 10, 12],
        "Project":    [5, 9, 13],
        "Midterm":    [7],
        "Final Exam": [15],
    }

    for course in COURSES:
        for atype, weeks in schedule.items():
            for wk in weeks:
                due = START + timedelta(weeks=wk - 1, days=4)  # due on Friday
                if due > END:
                    continue

                # rough estimate of how long each type takes
                if atype == "Homework":
                    hours = round(random.uniform(2.0, 5.0), 1)
                elif atype == "Quiz":
                    hours = round(random.uniform(1.0, 2.5), 1)
                elif atype == "Project":
                    hours = round(random.uniform(8.0, 20.0), 1)
                elif atype == "Midterm":
                    hours = round(random.uniform(5.0, 10.0), 1)
                else:
                    hours = round(random.uniform(8.0, 15.0), 1)

                assignments.append({
                    "assignment_id":   f"ASGN{aid:04d}",
                    "course":          course,
                    "type":            atype,
                    "title":           f"{course} - {atype} {wk}",
                    "due_date":        due.isoformat(),
                    "estimated_hours": hours,
                    "submitted":       1 if due < date.today() else 0,
                })
                aid += 1

    return assignments


def make_shifts():
    shifts = []
    sid = 1
    d = START

    while d <= END:
        # work tue/thu evenings and sometimes saturdays
        if d.weekday() in [1, 3] and random.random() < 0.70:
            shifts.append({
                "shift_id":    f"SHF{sid:04d}",
                "date":        d.isoformat(),
                "start_time":  "17:00",
                "end_time":    "21:00",
                "hours_worked": round(random.uniform(3.0, 5.0), 1),
                "location":    "Campus Library",
            })
            sid += 1

        if d.weekday() == 5 and random.random() < 0.60:
            shifts.append({
                "shift_id":    f"SHF{sid:04d}",
                "date":        d.isoformat(),
                "start_time":  "09:00",
                "end_time":    "17:00",
                "hours_worked": round(random.uniform(4.0, 8.0), 1),
                "location":    "Campus Library",
            })
            sid += 1

        d += timedelta(days=1)

    return shifts


def save_csv(path, rows, fields):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved {path} ({len(rows)} rows)")


if __name__ == "__main__":
    print("generating semester data...")

    save_csv("data/raw/calendar_events.csv", make_calendar_events(),
             ["event_id", "event_type", "title", "date", "start_time", "duration_minutes"])

    save_csv("data/raw/assignments.csv", make_assignments(),
             ["assignment_id", "course", "type", "title", "due_date", "estimated_hours", "submitted"])

    save_csv("data/raw/shifts.csv", make_shifts(),
             ["shift_id", "date", "start_time", "end_time", "hours_worked", "location"])
