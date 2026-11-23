"""A JSON-backed command-line expense tracker.

Core helpers are re-exported here for a convenient import path; the CLI entry
point is :mod:`expense_tracker.__main__`.
"""

from expense_tracker.config import DATE_FORMAT, DEFAULT_CATEGORY, DEFAULT_STORE
from expense_tracker.core.cli import build_parser, main
from expense_tracker.core.ledger import export_csv, filter_expenses, load, save, summarize
from expense_tracker.core.models import Expense

__version__ = "0.1.0"

__all__ = [
    "DATE_FORMAT",
    "DEFAULT_CATEGORY",
    "DEFAULT_STORE",
    "Expense",
    "build_parser",
    "export_csv",
    "filter_expenses",
    "load",
    "main",
    "save",
    "summarize",
]
