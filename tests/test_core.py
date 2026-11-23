"""Tests for the expense model, persistence, analysis and configuration."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Plain `unittest discover -s tests` uses tests/ as its top-level directory and
# does not import tests/__init__.py, so ensure src/ is importable here too.
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from expense_tracker import (  # noqa: E402
    DEFAULT_CATEGORY,
    DEFAULT_STORE,
    Expense,
    export_csv,
    filter_expenses,
    load,
    save,
    summarize,
)
from expense_tracker.config import get_default_category, get_store_path  # noqa: E402


class ExpenseTrackerTests(unittest.TestCase):
    """Behavioural tests preserved from the original single-file module."""

    def setUp(self) -> None:
        """Create a temporary store location for each test."""
        self.temp = tempfile.TemporaryDirectory()
        self.store = Path(self.temp.name) / "expenses.json"

    def tearDown(self) -> None:
        """Remove the temporary directory."""
        self.temp.cleanup()

    def test_create_sets_fields_and_validates(self) -> None:
        """Creation sets fields and rejects invalid input."""
        item = Expense.create(250.5, "Food", "lunch", "2026-01-15")
        self.assertEqual(item.date, "2026-01-15")
        self.assertEqual(item.amount, 250.5)
        self.assertEqual(item.note, "lunch")
        self.assertEqual(len(item.id), 8)
        with self.assertRaises(ValueError):
            Expense.create(0, "Food")
        with self.assertRaises(ValueError):
            Expense.create(10, "Food", day="15-01-2026")

    def test_save_and_load_roundtrip(self) -> None:
        """Expenses survive a save/load round trip in order."""
        items = [
            Expense.create(100, "Food", day="2026-01-01"),
            Expense.create(50, "Transport", day="2026-01-02"),
        ]
        save(self.store, items)
        loaded = load(self.store)
        self.assertEqual([item.id for item in loaded], [item.id for item in items])
        self.assertEqual(loaded[0].category, "Food")

    def test_load_missing_file_returns_empty_list(self) -> None:
        """A missing store is treated as an empty ledger."""
        self.assertEqual(load(self.store), [])

    def test_filter_by_category_and_month(self) -> None:
        """Category and month filters combine."""
        items = [
            Expense.create(100, "Food", day="2026-01-01"),
            Expense.create(200, "Food", day="2026-02-01"),
            Expense.create(50, "Transport", day="2026-01-05"),
        ]
        self.assertEqual(len(filter_expenses(items, month="2026-01")), 2)
        self.assertEqual(len(filter_expenses(items, category="food")), 2)
        self.assertEqual(len(filter_expenses(items, category="Food", month="2026-02")), 1)

    def test_summarize_totals_and_top_category(self) -> None:
        """Summary reports count, total and per-category totals."""
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

    def test_export_csv(self) -> None:
        """CSV export contains a header and the expected row."""
        items = [Expense.create(12.5, "Snacks", "tea", "2026-01-01")]
        output = Path(self.temp.name) / "report.csv"
        export_csv(items, output)
        with output.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "Snacks")
        self.assertEqual(rows[0]["amount"], "12.5")


class ConfigTests(unittest.TestCase):
    """Tests for genuine environment-variable support."""

    def test_store_environment_variable(self) -> None:
        """``EXPENSE_STORE`` overrides the default store path."""
        with mock.patch.dict("os.environ", {"EXPENSE_STORE": "ledger.json"}):
            self.assertEqual(get_store_path(), "ledger.json")
        self.assertEqual(get_store_path(), DEFAULT_STORE)

    def test_default_category_environment_variable(self) -> None:
        """``EXPENSE_DEFAULT_CATEGORY`` overrides the default category."""
        with mock.patch.dict("os.environ", {"EXPENSE_DEFAULT_CATEGORY": "Travel"}):
            self.assertEqual(get_default_category(), "Travel")
        self.assertEqual(get_default_category(), DEFAULT_CATEGORY)


if __name__ == "__main__":
    unittest.main()
