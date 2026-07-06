"""
test_expense.py
Unit tests for the Expense class and its validation logic.
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker.expense import Expense, ExpenseValidationError


class TestExpense(unittest.TestCase):
    def test_valid_expense_creation(self):
        e = Expense(date="2026-06-15", amount=42.5, category="Food", description="Lunch")
        self.assertEqual(e.amount, 42.5)
        self.assertEqual(e.category, "Food")
        self.assertEqual(e.date, "2026-06-15")

    def test_amount_must_be_positive(self):
        with self.assertRaises(ExpenseValidationError):
            Expense(date="2026-06-15", amount=-5, category="Food")

    def test_amount_zero_invalid(self):
        with self.assertRaises(ExpenseValidationError):
            Expense(date="2026-06-15", amount=0, category="Food")

    def test_amount_non_numeric(self):
        with self.assertRaises(ExpenseValidationError):
            Expense(date="2026-06-15", amount="abc", category="Food")

    def test_invalid_category(self):
        with self.assertRaises(ExpenseValidationError):
            Expense(date="2026-06-15", amount=10, category="Spaceships")

    def test_category_case_insensitive(self):
        e = Expense(date="2026-06-15", amount=10, category="food")
        self.assertEqual(e.category, "Food")

    def test_invalid_date_format(self):
        with self.assertRaises(ExpenseValidationError):
            Expense(date="15-06-2026", amount=10, category="Food")

    def test_future_date_rejected(self):
        future = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        with self.assertRaises(ExpenseValidationError):
            Expense(date=future, amount=10, category="Food")

    def test_description_too_long(self):
        with self.assertRaises(ExpenseValidationError):
            Expense(date="2026-06-15", amount=10, category="Food", description="x" * 201)

    def test_to_dict_and_from_dict_roundtrip(self):
        e = Expense(date="2026-06-15", amount=10, category="Food", description="Snack")
        d = e.to_dict()
        e2 = Expense.from_dict(d)
        self.assertEqual(e.date, e2.date)
        self.assertEqual(e.amount, e2.amount)
        self.assertEqual(e.category, e2.category)
        self.assertEqual(e.id, e2.id)

    def test_get_month_key(self):
        e = Expense(date="2026-06-15", amount=10, category="Food")
        self.assertEqual(e.get_month_key(), "2026-06")


if __name__ == "__main__":
    unittest.main()
