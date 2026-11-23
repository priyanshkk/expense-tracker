import csv
import tempfile
import unittest
from pathlib import Path

from expense_tracker import Expense, export_csv, filter_expenses, load, save, summarize


class ExpenseTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Path(self.temp.name) / "expenses.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_create_sets_fields_and_validates(self):
        item = Expense.create(250.5, "Food", "lunch", "2026-01-15")
        self.assertEqual(item.date, "2026-01-15")
        self.assertEqual(item.amount, 250.5)
        self.assertEqual(item.note, "lunch")
        self.assertEqual(len(item.id), 8)
        with self.assertRaises(ValueError):
            Expense.create(0, "Food")
        with self.assertRaises(ValueError):
            Expense.create(10, "Food", day="15-01-2026")

    def test_save_and_load_roundtrip(self):
        items = [
            Expense.create(100, "Food", day="2026-01-01"),
            Expense.create(50, "Transport", day="2026-01-02"),
        ]
        save(self.store, items)
        loaded = load(self.store)
        self.assertEqual([item.id for item in loaded], [item.id for item in items])
        self.assertEqual(loaded[0].category, "Food")

    def test_load_missing_file_returns_empty_list(self):
        self.assertEqual(load(self.store), [])

    def test_filter_by_category_and_month(self):
        items = [
            Expense.create(100, "Food", day="2026-01-01"),
            Expense.create(200, "Food", day="2026-02-01"),
            Expense.create(50, "Transport", day="2026-01-05"),
        ]
        self.assertEqual(len(filter_expenses(items, month="2026-01")), 2)
        self.assertEqual(len(filter_expenses(items, category="food")), 2)
        self.assertEqual(len(filter_expenses(items, category="Food", month="2026-02")), 1)

    def test_summarize_totals_and_top_category(self):
        items = [
            Expense.create(100, "Food", day="2026-01-01"),
            Expense.create(40, "Food", day="2026-01-02"),
            Expense.create(60, "Transport", day="2026-01-03"),
        ]
        result = summarize(items)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["total"], 200.0)
        self.assertEqual(result["by_category"]["Food"], 140.0)
        self.assertEqual(result["top_category"], "Food")

    def test_export_csv(self):
        items = [Expense.create(12.5, "Snacks", "tea", "2026-01-01")]
        output = Path(self.temp.name) / "report.csv"
        export_csv(items, output)
        with output.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "Snacks")
        self.assertEqual(rows[0]["amount"], "12.5")


if __name__ == "__main__":
    unittest.main()
