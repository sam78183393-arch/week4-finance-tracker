"""
main.py
The FinanceTracker CLI application: ties together expense_manager,
file_handler, reports, and utils into a menu-driven experience.
"""

from finance_tracker.expense_manager import ExpenseManager
from finance_tracker.expense import ExpenseValidationError
from finance_tracker import file_handler as fh
from finance_tracker import reports
from finance_tracker import utils


class FinanceTracker:
    def __init__(self):
        self.manager = ExpenseManager()
        self._load_on_startup()

    # ---------- Startup ----------
    def _load_on_startup(self):
        try:
            loaded = fh.load_expenses(self.manager)
            if loaded:
                print(f"Loaded {len(self.manager.expenses)} expense(s) from disk.")
            else:
                print("No existing data found. Starting fresh.")
        except fh.FileHandlerError as e:
            print(f"⚠ Could not load saved data: {e}")
            print("Starting with an empty tracker. Your old file is untouched.")

    def _save(self):
        try:
            fh.save_expenses(self.manager)
        except fh.FileHandlerError as e:
            print(f"⚠ Could not save data: {e}")

    # ---------- Main loop ----------
    def run(self):
        print("=" * 60)
        print("          PERSONAL FINANCE TRACKER")
        print("=" * 60)

        while True:
            print("\n" + "=" * 40)
            print("              MAIN MENU")
            print("=" * 40)
            print("1. Add New Expense")
            print("2. View All Expenses")
            print("3. Search Expenses")
            print("4. Generate Monthly Report")
            print("5. View Category Breakdown")
            print("6. Set/Update Budget")
            print("7. Export Data to CSV")
            print("8. View Statistics")
            print("9. Backup/Restore Data")
            print("10. Spending Trend / Prediction")
            print("11. Import from CSV")
            print("12. Recurring Expense")
            print("0. Exit")
            print("=" * 40)

            choice = input("\nEnter your choice: ").strip()

            actions = {
                '1': self.add_expense,
                '2': self.view_expenses,
                '3': self.search_expenses,
                '4': self.generate_monthly_report,
                '5': self.view_category_breakdown,
                '6': self.set_budget,
                '7': self.export_data,
                '8': self.view_statistics,
                '9': self.backup_restore,
                '10': self.trend_and_prediction,
                '11': self.import_csv,
                '12': self.recurring_expense,
            }

            if choice == '0':
                self._save()
                print("\n" + "=" * 60)
                print("Thank you for using Personal Finance Tracker!")
                print("=" * 60)
                break
            elif choice in actions:
                try:
                    actions[choice]()
                except ExpenseValidationError as e:
                    print(f"⚠ Validation error: {e}")
                except fh.FileHandlerError as e:
                    print(f"⚠ File error: {e}")
                except Exception as e:
                    print(f"⚠ Unexpected error: {e}")
            else:
                print("Invalid choice! Please try again.")

    # ---------- Menu actions ----------
    def add_expense(self):
        print("\n--- ADD NEW EXPENSE ---")
        date = utils.prompt_date()
        amount = utils.prompt_amount()
        category = utils.prompt_category()
        description = input("Description (optional): ").strip()

        expense = self.manager.add_expense(date, amount, category, description)
        self._save()
        print(f"Expense added successfully! {expense}")

    def view_expenses(self):
        print("\n--- ALL EXPENSES ---")
        if not self.manager.expenses:
            print("No expenses recorded yet.")
            return
        for e in sorted(self.manager.expenses, key=lambda x: x.date):
            print(e)
        print(f"\nTotal: Rs.{self.manager.total():.2f} across {len(self.manager.expenses)} entries.")

    def search_expenses(self):
        print("\n--- SEARCH EXPENSES ---")
        print("Leave any field blank to skip it.")
        keyword = input("Keyword (description/category): ").strip() or None
        category = input("Exact category: ").strip() or None
        start = input("Start date (YYYY-MM-DD): ").strip() or None
        end = input("End date (YYYY-MM-DD): ").strip() or None

        results = self.manager.search(keyword=keyword, category=category,
                                       start_date=start, end_date=end)
        if not results:
            print("No matching expenses found.")
            return
        for e in results:
            print(e)
        print(f"\n{len(results)} match(es), totaling Rs.{self.manager.total(results):.2f}")

    def generate_monthly_report(self):
        print("\n--- MONTHLY REPORT ---")
        month = utils.prompt_month()
        print(reports.monthly_summary_report(self.manager, month))

    def view_category_breakdown(self):
        print("\n--- CATEGORY BREAKDOWN ---")
        print(reports.category_breakdown_report(self.manager))

    def set_budget(self):
        print("\n--- SET/UPDATE BUDGET ---")
        print("Enter a month (YYYY-MM) or a category name to set a budget for.")
        key = input("Budget key: ").strip()
        amount = utils.prompt_amount("Budget amount: Rs.")
        self.manager.set_budget(key, amount)
        self._save()
        print(f"Budget set: {key} -> Rs.{amount:.2f}")

    def export_data(self):
        print("\n--- EXPORT DATA ---")
        path = fh.export_to_csv(self.manager)
        print(f"Data exported to: {path}")

    def import_csv(self):
        print("\n--- IMPORT FROM CSV ---")
        path = utils.prompt_nonempty("CSV file path: ")
        imported, errors = fh.import_from_csv(path, self.manager)
        self._save()
        print(f"Imported {imported} expense(s).")
        if errors:
            print(f"{len(errors)} row(s) had errors:")
            for err in errors[:10]:
                print(f"  - {err}")

    def view_statistics(self):
        print("\n--- STATISTICS ---")
        print(reports.statistics_report(self.manager))

    def backup_restore(self):
        print("\n--- BACKUP/RESTORE ---")
        print("1. Create backup")
        print("2. Restore from backup")
        print("3. List backups")
        sub = input("Choice: ").strip()

        if sub == '1':
            path = fh.create_backup()
            print(f"Backup created: {path}")
        elif sub == '2':
            backups = fh.list_backups()
            if not backups:
                print("No backups available.")
                return
            for i, b in enumerate(backups, 1):
                print(f"{i}. {b}")
            idx = input("Enter backup number to restore: ").strip()
            try:
                selected = backups[int(idx) - 1]
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
            if utils.confirm(f"This will overwrite current data with '{selected}'. Continue? (y/n): "):
                fh.restore_backup(selected, self.manager)
                print("Data restored successfully.")
        elif sub == '3':
            backups = fh.list_backups()
            if not backups:
                print("No backups available.")
            for b in backups:
                print(f"  {b}")
        else:
            print("Invalid choice.")

    def trend_and_prediction(self):
        print("\n--- SPENDING TREND / PREDICTION ---")
        print(reports.trend_report(self.manager))
        prediction = reports.predict_next_month(self.manager)
        print(f"\nPredicted spend next month (avg of last 3): Rs.{prediction:.2f}")

    def recurring_expense(self):
        print("\n--- SET UP RECURRING EXPENSE ---")
        date = utils.prompt_date("Start date (YYYY-MM-DD, blank = today): ")
        amount = utils.prompt_amount()
        category = utils.prompt_category()
        description = input("Description (optional): ").strip()
        months = input("How many months ahead (default 3): ").strip()
        months = int(months) if months.isdigit() else 3

        template = {"date": date, "amount": amount, "category": category, "description": description}
        added = self.manager.apply_recurring(template, months_ahead=months)
        self._save()
        print(f"Added {len(added)} recurring instance(s):")
        for e in added:
            print(f"  {e}")


def main():
    tracker = FinanceTracker()
    tracker.run()


if __name__ == "__main__":
    main()

