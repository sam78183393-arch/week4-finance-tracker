"""
expense.py
Defines the Expense class: a single financial transaction record,
along with validation logic for each of its fields.
"""

from datetime import datetime
import itertools

VALID_CATEGORIES = [
    "Food", "Transport", "Entertainment", "Bills",
    "Shopping", "Health", "Education", "Other"
]

DATE_FORMAT = "%Y-%m-%d"

# Monotonic counter ensures unique IDs even when expenses are created
# within the same millisecond (e.g. bulk import, recurring expenses).
_id_counter = itertools.count(1)


class ExpenseValidationError(Exception):
    """Raised when expense data fails validation."""
    pass


class Expense:
    """Represents a single expense entry."""

    def __init__(self, date, amount, category, description="", expense_id=None):
        self.id = expense_id if expense_id is not None else self._generate_id()
        self.date = self._validate_date(date)
        self.amount = self._validate_amount(amount)
        self.category = self._validate_category(category)
        self.description = self._validate_description(description)

    # ---------- ID generation ----------
    @staticmethod
    def _generate_id():
        # Combine a millisecond timestamp with a monotonic counter so IDs
        # stay unique even for expenses created in rapid succession.
        return int(datetime.now().timestamp() * 1000) * 1000 + (next(_id_counter) % 1000)

    # ---------- Validators ----------
    @staticmethod
    def _validate_date(date_value):
        if isinstance(date_value, datetime):
            return date_value.strftime(DATE_FORMAT)
        if isinstance(date_value, str):
            try:
                parsed = datetime.strptime(date_value, DATE_FORMAT)
            except ValueError:
                raise ExpenseValidationError(
                    f"Invalid date '{date_value}'. Expected format YYYY-MM-DD."
                )
            if parsed > datetime.now():
                raise ExpenseValidationError("Expense date cannot be in the future.")
            return date_value
        raise ExpenseValidationError("Date must be a string in YYYY-MM-DD format.")

    @staticmethod
    def _validate_amount(amount_value):
        try:
            amount = float(amount_value)
        except (TypeError, ValueError):
            raise ExpenseValidationError(f"Amount '{amount_value}' is not a valid number.")
        if amount <= 0:
            raise ExpenseValidationError("Amount must be greater than zero.")
        return round(amount, 2)

    @staticmethod
    def _validate_category(category_value):
        if not isinstance(category_value, str) or not category_value.strip():
            raise ExpenseValidationError("Category cannot be empty.")
        category = category_value.strip().title()
        if category not in VALID_CATEGORIES:
            raise ExpenseValidationError(
                f"Category '{category}' is not valid. Choose from: {', '.join(VALID_CATEGORIES)}"
            )
        return category

    @staticmethod
    def _validate_description(description_value):
        if description_value is None:
            return ""
        if not isinstance(description_value, str):
            raise ExpenseValidationError("Description must be text.")
        if len(description_value) > 200:
            raise ExpenseValidationError("Description must be under 200 characters.")
        return description_value.strip()

    # ---------- Serialization ----------
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data["date"],
            amount=data["amount"],
            category=data["category"],
            description=data.get("description", ""),
            expense_id=data.get("id"),
        )

    def get_month_key(self):
        """Returns 'YYYY-MM' for grouping by month."""
        return self.date[:7]

    def __repr__(self):
        return f"<Expense {self.date} {self.category} Rs.{self.amount:.2f}>"

    def __str__(self):
        desc = f" - {self.description}" if self.description else ""
        return f"[{self.id}] {self.date} | {self.category:<13} | Rs.{self.amount:>8.2f}{desc}"
