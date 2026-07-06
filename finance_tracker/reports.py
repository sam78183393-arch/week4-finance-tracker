"""
reports.py
Generates human-readable reports: monthly summaries, category breakdowns,
trend analysis, and simple text-based bar charts.
"""

from datetime import datetime


def _bar(amount, max_amount, width=30):
    if max_amount <= 0:
        return ""
    filled = int((amount / max_amount) * width)
    return "#" * filled + "-" * (width - filled)


def monthly_summary_report(expense_manager, year_month):
    expenses = expense_manager.get_by_month(year_month)
    lines = []
    lines.append("=" * 50)
    lines.append(f" MONTHLY REPORT: {year_month}")
    lines.append("=" * 50)

    if not expenses:
        lines.append("No expenses recorded for this month.")
        return "\n".join(lines)

    total = expense_manager.total(expenses)
    avg_daily = expense_manager.average_daily_spend(year_month)
    lines.append(f"Total spent:       Rs.{total:.2f}")
    lines.append(f"Number of entries: {len(expenses)}")
    lines.append(f"Avg per active day: Rs.{avg_daily:.2f}")

    budget_status = expense_manager.check_budget(year_month)
    if budget_status:
        lines.append("")
        lines.append(f"Budget:     Rs.{budget_status['budget']:.2f}")
        lines.append(f"Remaining:  Rs.{budget_status['remaining']:.2f}")
        if budget_status["over_budget"]:
            lines.append("⚠ OVER BUDGET")

    lines.append("")
    lines.append("Category breakdown:")
    breakdown = expense_manager.category_breakdown(expenses)
    max_val = max(breakdown.values()) if breakdown else 0
    for category, amount in breakdown.items():
        bar = _bar(amount, max_val)
        lines.append(f"  {category:<14} Rs.{amount:>8.2f}  {bar}")

    return "\n".join(lines)


def category_breakdown_report(expense_manager):
    breakdown = expense_manager.category_breakdown()
    lines = ["=" * 50, " CATEGORY BREAKDOWN (ALL TIME)", "=" * 50]

    if not breakdown:
        lines.append("No expenses recorded yet.")
        return "\n".join(lines)

    total = sum(breakdown.values())
    max_val = max(breakdown.values())
    for category, amount in breakdown.items():
        pct = (amount / total) * 100 if total else 0
        bar = _bar(amount, max_val)
        lines.append(f"  {category:<14} Rs.{amount:>8.2f} ({pct:4.1f}%)  {bar}")

    lines.append("-" * 50)
    lines.append(f"  {'TOTAL':<14} Rs.{total:>8.2f}")
    return "\n".join(lines)


def trend_report(expense_manager, last_n_months=6):
    monthly_totals = expense_manager.monthly_totals()
    months = list(monthly_totals.keys())[-last_n_months:]
    lines = ["=" * 50, f" SPENDING TREND (last {len(months)} months)", "=" * 50]

    if not months:
        lines.append("No expense history yet.")
        return "\n".join(lines)

    max_val = max(monthly_totals[m] for m in months)
    for month in months:
        amount = monthly_totals[month]
        bar = _bar(amount, max_val)
        lines.append(f"  {month}  Rs.{amount:>8.2f}  {bar}")

    if len(months) >= 2:
        change = monthly_totals[months[-1]] - monthly_totals[months[-2]]
        direction = "up" if change > 0 else "down" if change < 0 else "flat"
        lines.append("")
        lines.append(f"Change vs. previous month: {direction} Rs.{abs(change):.2f}")

    return "\n".join(lines)


def statistics_report(expense_manager):
    stats = expense_manager.statistics()
    lines = ["=" * 50, " OVERALL STATISTICS", "=" * 50]

    if stats["count"] == 0:
        lines.append("No expenses recorded yet.")
        return "\n".join(lines)

    lines.append(f"Total expenses:  {stats['count']}")
    lines.append(f"Total spent:     Rs.{stats['total']:.2f}")
    lines.append(f"Average expense: Rs.{stats['average']:.2f}")
    lines.append(f"Largest expense: {stats['max']}")
    lines.append(f"Smallest expense: {stats['min']}")
    return "\n".join(lines)


def predict_next_month(expense_manager):
    """Simple prediction: average of the last 3 months' totals."""
    monthly_totals = expense_manager.monthly_totals()
    recent = list(monthly_totals.values())[-3:]
    if not recent:
        return 0.0
    return round(sum(recent) / len(recent), 2)
