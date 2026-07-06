"""
test_file_handler.py
Unit tests for JSON persistence, backups, and CSV import/export.
Uses temporary directories so tests never touch real project data.
"""

import sys
import os
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker.expense_manager import ExpenseManager
from finance_tracker import file_handler as fh


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmp_dir, "expenses.json")
        self.backup_dir = os.path.join(self.tmp_dir, "backup")
        self.manager = ExpenseManager()
        self.manager.add_expense("2026-06-01", 20, "Food", "Groceries")
        self.manager.add_expense("2026-06-05", 15, "Transport", "Bus pass")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_save_and_load_roundtrip(self):
        fh.save_expenses(self.manager, filepath=self.filepath)
        new_manager = ExpenseManager()
        loaded = fh.load_expenses(new_manager, filepath=self.filepath)
        self.assertTrue(loaded)
        self.assertEqual(len(new_manager.expenses), 2)

    def test_load_nonexistent_file_returns_false(self):
        new_manager = ExpenseManager()
        loaded = fh.load_expenses(new_manager, filepath=os.path.join(self.tmp_dir, "nope.json"))
        self.assertFalse(loaded)

    def test_load_corrupted_file_raises(self):
        with open(self.filepath, "w") as f:
            f.write("{not valid json::")
        new_manager = ExpenseManager()
        with self.assertRaises(fh.FileHandlerError):
            fh.load_expenses(new_manager, filepath=self.filepath)

    def test_backup_and_restore(self):
        fh.save_expenses(self.manager, filepath=self.filepath)
        backup_path = fh.create_backup(filepath=self.filepath, backup_dir=self.backup_dir)
        self.assertTrue(os.path.exists(backup_path))

        # Corrupt/clear the live file, then restore.
        self.manager.add_expense("2026-06-10", 99, "Bills", "Extra charge")
        fh.save_expenses(self.manager, filepath=self.filepath)

        restored_manager = ExpenseManager()
        backup_name = os.path.basename(backup_path)
        fh.restore_backup(backup_name, restored_manager, backup_dir=self.backup_dir, filepath=self.filepath)
        self.assertEqual(len(restored_manager.expenses), 2)  # pre-corruption count

    def test_backup_missing_source_raises(self):
        with self.assertRaises(fh.FileHandlerError):
            fh.create_backup(filepath=os.path.join(self.tmp_dir, "missing.json"), backup_dir=self.backup_dir)

    def test_csv_export_and_import(self):
        export_dir = os.path.join(self.tmp_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        # Monkey-patch export dir via direct path build since export_to_csv uses EXPORT_DIR constant
        original_export_dir = fh.EXPORT_DIR
        fh.EXPORT_DIR = export_dir
        try:
            path = fh.export_to_csv(self.manager, filename="test_export.csv")
            self.assertTrue(os.path.exists(path))

            new_manager = ExpenseManager()
            imported, errors = fh.import_from_csv(path, new_manager)
            self.assertEqual(imported, 2)
            self.assertEqual(errors, [])
        finally:
            fh.EXPORT_DIR = original_export_dir

    def test_csv_import_missing_file_raises(self):
        with self.assertRaises(fh.FileHandlerError):
            fh.import_from_csv(os.path.join(self.tmp_dir, "missing.csv"), ExpenseManager())


if __name__ == "__main__":
    unittest.main()
