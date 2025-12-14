#!/usr/bin/env python3
"""
Spending analysis script.

Usage:
    python3 spending.py summary [--period PERIOD] [--category CATEGORY]
    python3 spending.py budget-check [--category CATEGORY]
    python3 spending.py log --amount AMOUNT --category CATEGORY --vendor VENDOR [--note NOTE]

Examples:
    python3 spending.py summary --period "this month"
    python3 spending.py budget-check --category dining
    python3 spending.py log --amount 42.50 --category food --vendor "Sweetgreen" --note "lunch"
"""

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
BUDGETS_FILE = DATA_DIR / "budgets.json"


def load_transactions():
    """Load all transactions from CSV."""
    transactions = []
    with open(TRANSACTIONS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["amount"] = float(row["amount"])
            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d")
            transactions.append(row)
    return transactions


def load_budgets():
    """Load budget configuration."""
    with open(BUDGETS_FILE, "r") as f:
        return json.load(f)


def filter_by_period(transactions, period):
    """Filter transactions by time period."""
    today = datetime.now()

    if period == "this month":
        start = today.replace(day=1)
        return [t for t in transactions if t["date"] >= start]
    elif period == "last week":
        start = today - timedelta(days=7)
        return [t for t in transactions if t["date"] >= start]
    elif period == "this week":
        start = today - timedelta(days=today.weekday())
        return [t for t in transactions if t["date"] >= start]
    else:
        return transactions


def summarize(transactions, category=None):
    """Summarize spending by category."""
    if category:
        transactions = [t for t in transactions if t["category"] == category]

    by_category = {}
    for t in transactions:
        cat = t["category"]
        by_category[cat] = by_category.get(cat, 0) + t["amount"]

    return by_category


def budget_check(transactions, budgets, category=None):
    """Check spending against budgets."""
    today = datetime.now()
    days_in_month = 30  # Simplified
    days_elapsed = today.day

    monthly_budgets = budgets["monthly_budgets"]
    summary = summarize(transactions, category)

    results = []
    categories = [category] if category else monthly_budgets.keys()

    for cat in categories:
        if cat not in monthly_budgets:
            continue

        spent = summary.get(cat, 0)
        limit = monthly_budgets[cat]["limit"]
        prorated_limit = (limit / days_in_month) * days_elapsed

        status = "✓ On track" if spent <= prorated_limit else "⚠ Over pace"
        projected = (spent / days_elapsed) * days_in_month if days_elapsed > 0 else 0

        results.append({
            "category": cat,
            "spent": spent,
            "budget": limit,
            "prorated": prorated_limit,
            "projected": projected,
            "status": status
        })

    return results


def log_transaction(amount, category, vendor, note=""):
    """Add a new transaction."""
    today = datetime.now().strftime("%Y-%m-%d")

    with open(TRANSACTIONS_FILE, "a") as f:
        writer = csv.writer(f)
        writer.writerow([today, amount, category, vendor, note])

    return {"date": today, "amount": amount, "category": category, "vendor": vendor}


def main():
    parser = argparse.ArgumentParser(description="Spending analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Summary command
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--period", default="this month")
    summary_parser.add_argument("--category")

    # Budget check command
    budget_parser = subparsers.add_parser("budget-check")
    budget_parser.add_argument("--category")

    # Log command
    log_parser = subparsers.add_parser("log")
    log_parser.add_argument("--amount", type=float, required=True)
    log_parser.add_argument("--category", required=True)
    log_parser.add_argument("--vendor", required=True)
    log_parser.add_argument("--note", default="")

    args = parser.parse_args()

    if args.command == "summary":
        transactions = load_transactions()
        filtered = filter_by_period(transactions, args.period)
        summary = summarize(filtered, args.category)

        print(f"\nSpending Summary ({args.period}):\n")
        total = 0
        for cat, amount in sorted(summary.items()):
            print(f"  {cat:15} ${amount:,.2f}")
            total += amount
        print(f"\n  {'Total':15} ${total:,.2f}")

    elif args.command == "budget-check":
        transactions = load_transactions()
        this_month = filter_by_period(transactions, "this month")
        budgets = load_budgets()
        results = budget_check(this_month, budgets, args.category)

        print(f"\nBudget Status:\n")
        print(f"  {'Category':15} {'Spent':>10} {'Budget':>10} {'Status'}")
        print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*12}")
        for r in results:
            print(f"  {r['category']:15} ${r['spent']:>8,.2f} ${r['budget']:>8,.2f} {r['status']}")

    elif args.command == "log":
        result = log_transaction(args.amount, args.category, args.vendor, args.note)
        print(f"\n✓ Logged: ${result['amount']:.2f} for {result['category']} at {result['vendor']}")


if __name__ == "__main__":
    main()
