"""
file_handler.py
Handles all file I/O: loading/saving expenses as JSON, CSV import/export,
backups, and recovery. All functions raise FileHandlerError with a clear
message on failure rather than letting raw exceptions propagate.
"""

import json
import csv
import os
import shutil
from datetime import datetime

DATA_DIR = "data"
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")


class FileHandlerError(Exception):
    """Raised for any file-related failure, with a user-friendly message."""
    pass


def ensure_directories():
    for d in (DATA_DIR, BACKUP_DIR, EXPORT_DIR):
        os.makedirs(d, exist_ok=True)


# ---------- JSON persistence ----------
def save_expenses(expense_manager, filepath=EXPENSES_FILE):
    ensure_directories()
    payload = {
        "expenses": [e.to_dict() for e in expense_manager.expenses],
        "budgets": expense_manager.budgets,
        "saved_at": datetime.now().isoformat(),
    }
    try:
        # Write to a temp file first, then replace, to avoid corrupting
        # the real file if the process is interrupted mid-write.
        tmp_path = filepath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        shutil.move(tmp_path, filepath)
    except PermissionError:
        raise FileHandlerError(f"Permission denied writing to '{filepath}'.")
    except OSError as e:
        raise FileHandlerError(f"Could not save data to '{filepath}': {e}")


def load_expenses(expense_manager, filepath=EXPENSES_FILE):
    if not os.path.exists(filepath):
        # Nothing to load yet — not an error, just a fresh start.
        return False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except PermissionError:
        raise FileHandlerError(f"Permission denied reading '{filepath}'.")
    except json.JSONDecodeError:
        raise FileHandlerError(
            f"Data file '{filepath}' is corrupted and could not be read. "
            "Try restoring from a backup (menu option 9)."
        )
    except OSError as e:
        raise FileHandlerError(f"Could not read '{filepath}': {e}")

    try:
        expense_manager.load_expenses(payload.get("expenses", []))
        expense_manager.budgets = payload.get("budgets", {})
    except Exception as e:
        raise FileHandlerError(f"Data file '{filepath}' has invalid content: {e}")

    return True


# ---------- Backups ----------
def create_backup(filepath=EXPENSES_FILE, backup_dir=BACKUP_DIR):
    os.makedirs(backup_dir, exist_ok=True)
    if not os.path.exists(filepath):
        raise FileHandlerError("No data file exists yet to back up.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"expenses_backup_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        shutil.copy2(filepath, backup_path)
    except OSError as e:
        raise FileHandlerError(f"Backup failed: {e}")

    return backup_path


def list_backups(backup_dir=BACKUP_DIR):
    os.makedirs(backup_dir, exist_ok=True)
    files = [f for f in os.listdir(backup_dir) if f.endswith(".json")]
    return sorted(files, reverse=True)


def restore_backup(backup_filename, expense_manager, backup_dir=BACKUP_DIR, filepath=EXPENSES_FILE):
    backup_path = os.path.join(backup_dir, backup_filename)
    if not os.path.exists(backup_path):
        raise FileHandlerError(f"Backup '{backup_filename}' not found.")

    try:
        shutil.copy2(backup_path, filepath)
    except OSError as e:
        raise FileHandlerError(f"Restore failed: {e}")

    load_expenses(expense_manager, filepath)


# ---------- CSV export/import ----------
def export_to_csv(expense_manager, filename=None):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    if filename is None:
        filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    export_path = os.path.join(EXPORT_DIR, filename)

    try:
        with open(export_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "amount", "category", "description"])
            for e in expense_manager.expenses:
                d = e.to_dict()
                writer.writerow([d["id"], d["date"], d["amount"], d["category"], d["description"]])
    except PermissionError:
        raise FileHandlerError(f"Permission denied writing to '{export_path}'.")
    except OSError as e:
        raise FileHandlerError(f"CSV export failed: {e}")

    return export_path


def import_from_csv(filepath, expense_manager):
    if not os.path.exists(filepath):
        raise FileHandlerError(f"CSV file '{filepath}' does not exist.")

    imported = 0
    errors = []
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):  # row 1 is the header
                try:
                    expense_manager.add_expense(
                        date=row["date"],
                        amount=row["amount"],
                        category=row["category"],
                        description=row.get("description", ""),
                    )
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {i}: {e}")
    except PermissionError:
        raise FileHandlerError(f"Permission denied reading '{filepath}'.")
    except OSError as e:
        raise FileHandlerError(f"CSV import failed: {e}")

    return imported, errors
