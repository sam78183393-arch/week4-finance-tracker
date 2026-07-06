"""
utils.py
Small reusable helpers for the CLI layer: input prompting with validation
and retry loops, so main.py stays focused on menu flow.
"""

from datetime import datetime

VALID_CATEGORIES = [
    "Food", "Transport", "Entertainment", "Bills",
    "Shopping", "Health", "Education", "Other"
]


def prompt_nonempty(label):
    while True:
        value = input(label).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def prompt_date(label="Date (YYYY-MM-DD, blank = today): "):
    while True:
        value = input(label).strip()
        if not value:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
            if parsed > datetime.now():
                print("Date cannot be in the future.")
                continue
            return value
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD.")


def prompt_amount(label="Amount: Rs."):
    while True:
        value = input(label).strip()
        try:
            amount = float(value)
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number.")


def prompt_category(label=None):
    label = label or f"Category ({'/'.join(VALID_CATEGORIES)}): "
    while True:
        value = input(label).strip().title()
        if value in VALID_CATEGORIES:
            return value
        print(f"Invalid category. Choose from: {', '.join(VALID_CATEGORIES)}")


def prompt_month(label="Month (YYYY-MM): "):
    while True:
        value = input(label).strip()
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            print("Invalid format. Please use YYYY-MM.")


def confirm(label="Are you sure? (y/n): "):
    return input(label).strip().lower() in ("y", "yes")
