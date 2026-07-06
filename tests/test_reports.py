"""
test_reports.py
Unit tests for report generation: monthly summaries, breakdowns,
trends, statistics, and predictions.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker.expense_manager import ExpenseManager
from finance_tracker import reports


class TestReports(unittest.TestCase):
    def setUp(self):
        self.manager = ExpenseManager()
        self.manager.add_expense("2026-05-01", 50, "Food", "Groceries")
        self.manager.add_expense("2026-05-15", 30, "Transport", "Fuel")
        self.manager.add_expense("2026-06-02", 40, "Food", "Groceries")
        self.manager.add_expense("2026-06-10", 20, "Entertainment", "Movie")

    def test_monthly_summary_report_contains_total(self):
        report = reports.monthly_summary_report(self.manager, "2026-06")
        self.assertIn("2026-06", report)
        self.assertIn("60.00", report)  # 40 + 20

    def test_monthly_summary_report_empty_month(self):
        report = reports.monthly_summary_report(self.manager, "2026-01")
        self.assertIn("No expenses recorded", report)

    def test_category_breakdown_report(self):
        report = reports.category_breakdown_report(self.manager)
        self.assertIn("Food", report)
        self.assertIn("Transport", report)
        self.assertIn("Entertainment", report)

    def test_trend_report_has_months(self):
        report = reports.trend_report(self.manager)
        self.assertIn("2026-05", report)
        self.assertIn("2026-06", report)

    def test_statistics_report(self):
        report = reports.statistics_report(self.manager)
        self.assertIn("Total expenses:  4", report)

    def test_statistics_report_empty(self):
        empty_manager = ExpenseManager()
        report = reports.statistics_report(empty_manager)
        self.assertIn("No expenses recorded", report)

    def test_predict_next_month(self):
        prediction = reports.predict_next_month(self.manager)
        # Average of (80, 60) = 70.0
        self.assertEqual(prediction, 70.0)

    def test_predict_next_month_no_data(self):
        empty_manager = ExpenseManager()
        self.assertEqual(reports.predict_next_month(empty_manager), 0.0)

    def test_budget_status_in_monthly_report(self):
        self.manager.set_budget("2026-06", 50)
        report = reports.monthly_summary_report(self.manager, "2026-06")
        self.assertIn("OVER BUDGET", report)


if __name__ == "__main__":
    unittest.main()
