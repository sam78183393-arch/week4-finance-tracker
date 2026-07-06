# Personal Finance Tracker

## Project Description
A comprehensive personal finance tracking application that helps users manage
their expenses, categorize spending, and generate insightful reports. Built as
a modular, menu-driven CLI application using only the Python standard library.

## Features
- Add expenses with full validation (date, amount, category, description)
- Categorize expenses (Food, Transport, Entertainment, Bills, Shopping, Health, Education, Other)
- Save data to JSON with atomic writes, so a crash mid-save can't corrupt your file
- Load data on startup with graceful error recovery
- Search and filter expenses by keyword, category, date range, or amount range
- Generate monthly expense reports with a text-based bar chart breakdown
- View category-wise spending breakdown across all time
- Set and track budgets per month or per category, with over-budget warnings
- View spending trends across recent months and a simple next-month prediction
- Export data to CSV for spreadsheet analysis; import expenses back from CSV
- Create and restore backups of your data file
- Set up recurring expenses that auto-generate for N upcoming months
- Overall statistics: totals, averages, largest/smallest expense

## Project Structure
```
week4-finance-tracker/
│── finance_tracker/
│   ├── __init__.py
│   ├── main.py             # CLI menu and application flow
│   ├── expense.py          # Expense data model + validation
│   ├── expense_manager.py  # In-memory collection: search, filter, aggregates, budgets
│   ├── file_handler.py     # JSON/CSV persistence, backups, recovery
│   ├── reports.py          # Report generation and text-based visualizations
│   └── utils.py            # CLI input-prompting helpers
│── data/
│   ├── expenses.json       # Created automatically on first save
│   ├── backup/             # Timestamped backups
│   └── exports/            # CSV exports
│── tests/
│   ├── test_expense.py
│   ├── test_file_handler.py
│   └── test_reports.py
│── requirements.txt
│── README.md
│── .gitignore
└── run.py
```

## How to Run
```bash
cd week4-finance-tracker
python run.py
```

No external dependencies are required — everything uses the Python standard
library (`json`, `csv`, `os`, `shutil`, `datetime`, `unittest`).

## Running the Tests
```bash
cd week4-finance-tracker
python -m unittest discover -s tests -v
```
All 27 unit tests cover expense validation, file operations (including
corrupted-file and permission-error handling), backup/restore, CSV
import/export, and report generation.

## Technical Details

### Architecture
The app follows a layered design:
- **Data layer** (`expense.py`): a single `Expense` is responsible only for
  validating and serializing itself. IDs combine a millisecond timestamp with
  a monotonic counter so bulk operations (imports, recurring expenses) never
  collide.
- **Business logic layer** (`expense_manager.py`): `ExpenseManager` owns the
  in-memory list of expenses and all aggregate operations (totals, category
  breakdowns, monthly totals, budget checks). It has no knowledge of files or
  the console — it's pure logic, which makes it easy to unit test.
- **Persistence layer** (`file_handler.py`): all disk I/O lives here. Saves
  are atomic (write to a `.tmp` file, then rename) so an interrupted save
  can't corrupt existing data. Every failure mode (missing file, bad
  permissions, corrupted JSON) raises a single `FileHandlerError` with a
  human-readable message instead of letting a raw exception surface.
- **Reporting layer** (`reports.py`): pure functions that take an
  `ExpenseManager` and return formatted strings, including simple ASCII bar
  charts sized relative to the largest value in the data set.
- **Presentation layer** (`main.py` + `utils.py`): the menu loop and input
  prompting. Validation errors and file errors raised by lower layers are
  caught here and shown to the user without crashing the app.

### Data format
Expenses are stored as a JSON object with `expenses` (a list of records) and
`budgets` (a dict keyed by either a `"YYYY-MM"` month or a category name).
CSV export/import uses the columns `id, date, amount, category, description`.

### Error handling
Every file operation is wrapped and re-raised as `FileHandlerError`, and every
data-validation issue raises `ExpenseValidationError`. The main menu loop
catches both so the whole application survives a single bad operation instead
of crashing.

## Testing Evidence
Run `python -m unittest discover -s tests -v` to see 27 tests pass, covering:
- Expense validation (negative/zero/non-numeric amounts, invalid categories,
  bad date formats, future dates, oversized descriptions, round-tripping)
- File handling (save/load round-trip, missing files, corrupted JSON, backup
  creation/restore, CSV export/import, missing-file errors)
- Reports (monthly summaries, category breakdowns, trends, statistics,
  next-month prediction, budget-exceeded warnings)
