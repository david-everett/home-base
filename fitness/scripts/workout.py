#!/usr/bin/env python3
"""
Workout tracking script.

Usage:
    python3 workout.py log --exercise EXERCISE --weight WEIGHT --reps REPS --sets SETS [--note NOTE]
    python3 workout.py progress [--exercise EXERCISE]
    python3 workout.py weekly

Examples:
    python3 workout.py log --exercise squat --weight 200 --reps 5 --sets 3
    python3 workout.py progress --exercise squat
    python3 workout.py weekly
"""

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
WORKOUTS_FILE = DATA_DIR / "workouts.csv"
GOALS_FILE = DATA_DIR / "goals.json"


def load_workouts():
    """Load all workouts from CSV."""
    workouts = []
    with open(WORKOUTS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["weight"] = float(row["weight"]) if row["weight"] else 0
            row["reps"] = int(row["reps"]) if row["reps"] else 0
            row["sets"] = int(row["sets"]) if row["sets"] else 0
            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d")
            workouts.append(row)
    return workouts


def load_goals():
    """Load goals configuration."""
    with open(GOALS_FILE, "r") as f:
        return json.load(f)


def save_goals(goals):
    """Save updated goals."""
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)


def log_workout(exercise, weight, reps, sets, note=""):
    """Log a new workout entry."""
    today = datetime.now().strftime("%Y-%m-%d")

    with open(WORKOUTS_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([today, exercise, weight, reps, sets, note])

    # Check for PR
    goals = load_goals()
    pr_message = None

    if exercise in goals.get("strength_goals", {}):
        current_pr = goals["strength_goals"][exercise]["current"]
        if weight > current_pr:
            pr_message = f"🎉 New PR! Previous best: {current_pr} lbs"
            goals["strength_goals"][exercise]["current"] = weight
            save_goals(goals)

    return {
        "date": today,
        "exercise": exercise,
        "weight": weight,
        "reps": reps,
        "sets": sets,
        "pr_message": pr_message
    }


def get_progress(exercise=None):
    """Get progress for an exercise or all exercises."""
    workouts = load_workouts()
    goals = load_goals()

    if exercise:
        workouts = [w for w in workouts if w["exercise"] == exercise]

    # Find PRs by exercise
    prs = {}
    for w in workouts:
        ex = w["exercise"]
        if ex not in prs or w["weight"] > prs[ex]["weight"]:
            prs[ex] = w

    results = []
    for ex, pr in prs.items():
        goal_info = goals.get("strength_goals", {}).get(ex, {})
        target = goal_info.get("target", pr["weight"])

        # Get recent sessions
        recent = sorted(
            [w for w in workouts if w["exercise"] == ex],
            key=lambda x: x["date"],
            reverse=True
        )[:5]

        results.append({
            "exercise": ex,
            "current_pr": pr["weight"],
            "target": target,
            "progress_pct": (pr["weight"] / target * 100) if target else 100,
            "recent": recent
        })

    return results


def weekly_summary():
    """Get weekly workout summary."""
    workouts = load_workouts()
    goals = load_goals()

    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())

    this_week = [w for w in workouts if w["date"] >= week_start]

    # Count unique days with workouts
    workout_days = set(w["date"].date() for w in this_week)
    strength_days = set(
        w["date"].date() for w in this_week
        if w["exercise"] not in ["run", "bike", "swim"]
    )
    cardio_days = set(
        w["date"].date() for w in this_week
        if w["exercise"] in ["run", "bike", "swim"]
    )

    targets = goals.get("weekly_targets", {})

    return {
        "strength_sessions": len(strength_days),
        "strength_target": targets.get("strength_sessions", 3),
        "cardio_sessions": len(cardio_days),
        "cardio_target": targets.get("cardio_sessions", 2),
        "total_workouts": len(workout_days)
    }


def main():
    parser = argparse.ArgumentParser(description="Workout tracking")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Log command
    log_parser = subparsers.add_parser("log")
    log_parser.add_argument("--exercise", required=True)
    log_parser.add_argument("--weight", type=float, default=0)
    log_parser.add_argument("--reps", type=int, default=0)
    log_parser.add_argument("--sets", type=int, default=1)
    log_parser.add_argument("--note", default="")

    # Progress command
    progress_parser = subparsers.add_parser("progress")
    progress_parser.add_argument("--exercise")

    # Weekly command
    subparsers.add_parser("weekly")

    args = parser.parse_args()

    if args.command == "log":
        result = log_workout(args.exercise, args.weight, args.reps, args.sets, args.note)
        print(f"\n✓ Logged: {result['exercise'].replace('_', ' ').title()} "
              f"{result['weight']}lbs × {result['reps']} reps × {result['sets']} sets")
        if result["pr_message"]:
            print(f"  {result['pr_message']}")

    elif args.command == "progress":
        results = get_progress(args.exercise)

        for r in results:
            print(f"\n{r['exercise'].replace('_', ' ').title()} Progress:")
            print(f"  Current PR: {r['current_pr']} lbs")
            print(f"  Goal: {r['target']} lbs")

            # Progress bar
            pct = min(r['progress_pct'], 100)
            filled = int(pct / 10)
            bar = "█" * filled + "░" * (10 - filled)
            print(f"  Progress: {pct:.0f}% {bar}")

            print(f"\n  Recent sessions:")
            for w in r["recent"][:3]:
                date_str = w["date"].strftime("%b %d")
                print(f"    - {date_str}: {w['weight']} × {w['reps']} × {w['sets']}")

    elif args.command == "weekly":
        summary = weekly_summary()

        print(f"\nWeekly Summary:")
        print(f"  Strength: {summary['strength_sessions']}/{summary['strength_target']} sessions")
        print(f"  Cardio: {summary['cardio_sessions']}/{summary['cardio_target']} sessions")
        print(f"  Total workout days: {summary['total_workouts']}")


if __name__ == "__main__":
    main()
