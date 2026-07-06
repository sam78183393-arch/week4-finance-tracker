"""
expense_manager.py
ExpenseManager handles an in-memory collection of Expense objects:
adding, removing, searching, filtering, and computing aggregates.
Persistence is delegated to file_handler.py.
"""

from datetime import datetime
from finance_tracker.expense import Expense, ExpenseValidationError


class ExpenseManager:
    def __init__(self):
        self.expenses = []
        self.budgets = {}  # {"YYYY-MM": amount} or {"category": amount}

    # ---------- CRUD ----------
    def add_expense(self, date, amount, category, description=""):
        expense = Expense(date=date, amount=amount, category=category, description=description)
        self.expenses.append(expense)
        return expense

    def remove_expense(self, expense_id):
        for i, exp in enumerate(self.expenses):
            if exp.id == expense_id:
                return self.expenses.pop(i)
        raise ValueError(f"No expense found with id {expense_id}")

    def update_expense(self, expense_id, **fields):
        old = self.remove_expense(expense_id)
        merged = old.to_dict()
        merged.update(fields)
        try:
            new_expense = Expense.from_dict(merged)
        except ExpenseValidationError:
            # Roll back on validation failure
            self.expenses.append(old)
            raise
        self.expenses.append(new_expense)
        return new_expense

    def load_expenses(self, expense_dicts):
        self.expenses = [Expense.from_dict(d) for d in expense_dicts]

    # ---------- Search & filter ----------
    def search(self, keyword=None, category=None, start_date=None, end_date=None,
               min_amount=None, max_amount=None):
        results = self.expenses

        if keyword:
            keyword = keyword.lower()
            results = [e for e in results if keyword in e.description.lower()
                       or keyword in e.category.lower()]
        if category:
            results = [e for e in results if e.category.lower() == category.lower()]
        if start_date:
            results = [e for e in results if e.date >= start_date]
        if end_date:
            results = [e for e in results if e.date <= end_date]
        if min_amount is not None:
            results = [e for e in results if e.amount >= min_amount]
        if max_amount is not None:
            results = [e for e in results if e.amount <= max_amount]

        return sorted(results, key=lambda e: e.date)

    def get_by_month(self, year_month):
        """year_month like '2026-07'"""
        return [e for e in self.expenses if e.get_month_key() == year_month]

    def get_by_category(self, category):
        return [e for e in self.expenses if e.category.lower() == category.lower()]

    # ---------- Aggregates ----------
    def total(self, expenses=None):
        pool = expenses if expenses is not None else self.expenses
        return round(sum(e.amount for e in pool), 2)

    def category_breakdown(self, expenses=None):
        pool = expenses if expenses is not None else self.expenses
        breakdown = {}
        for e in pool:
            breakdown[e.category] = round(breakdown.get(e.category, 0) + e.amount, 2)
        return dict(sorted(breakdown.items(), key=lambda kv: kv[1], reverse=True))

    def monthly_totals(self):
        totals = {}
        for e in self.expenses:
            key = e.get_month_key()
            totals[key] = round(totals.get(key, 0) + e.amount, 2)
        return dict(sorted(totals.items()))

    def average_daily_spend(self, year_month):
        month_expenses = self.get_by_month(year_month)
        if not month_expenses:
            return 0.0
        dates = {e.date for e in month_expenses}
        return round(self.total(month_expenses) / len(dates), 2)

    def statistics(self):
        if not self.expenses:
            return {"count": 0, "total": 0, "average": 0, "max": None, "min": None}
        amounts = [e.amount for e in self.expenses]
        max_exp = max(self.expenses, key=lambda e: e.amount)
        min_exp = min(self.expenses, key=lambda e: e.amount)
        return {
            "count": len(self.expenses),
            "total": round(sum(amounts), 2),
            "average": round(sum(amounts) / len(amounts), 2),
            "max": max_exp,
            "min": min_exp,
        }

    # ---------- Budgets ----------
    def set_budget(self, key, amount):
        if amount <= 0:
            raise ValueError("Budget must be greater than zero.")
        self.budgets[key] = round(float(amount), 2)

    def check_budget(self, key):
        """key is a 'YYYY-MM' month or a category name."""
        if key not in self.budgets:
            return None
        budget = self.budgets[key]
        if len(key) == 7 and key[4] == '-':  # looks like YYYY-MM
            spent = self.total(self.get_by_month(key))
        else:
            spent = self.total(self.get_by_category(key))
        return {
            "budget": budget,
            "spent": spent,
            "remaining": round(budget - spent, 2),
            "over_budget": spent > budget,
        }

    # ---------- Recurring expenses ----------
    def apply_recurring(self, template, months_ahead=1):
        """Adds a recurring expense template for N upcoming months (same day-of-month)."""
        added = []
        base_date = datetime.strptime(template["date"], "%Y-%m-%d")
        for i in range(months_ahead):
            month = base_date.month + i
            year = base_date.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            try:
                new_date = base_date.replace(year=year, month=month)
            except ValueError:
                continue  # skip invalid day-of-month overflow (e.g., Feb 30)
            exp = self.add_expense(
                date=new_date.strftime("%Y-%m-%d"),
                amount=template["amount"],
                category=template["category"],
                description=template.get("description", "") + " (recurring)",
            )
            added.append(exp)
        return added
