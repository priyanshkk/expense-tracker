"""JSON persistence, filtering, reporting and CSV export."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import TypedDict

from expense_tracker.core.models import Expense

#: Column order used for CSV exports and the JSON store.
CSV_FIELDS = ("id", "date", "amount", "category", "note")


class Summary(TypedDict):
    """Aggregate statistics returned by :func:`summarize`.

    Attributes:
        count: Number of selected expenses.
        total: Sum of their amounts, rounded to two decimals.
        by_category: Alphabetically sorted category totals.
        top_category: Category with the largest total, or ``None`` if empty.
    """

    count: int
    total: float
    by_category: dict[str, float]
    top_category: str | None


def load(path: str | Path) -> list[Expense]:
    """Load expenses from *path*, returning an empty list if it does not exist.

    Args:
        path: JSON store location.

    Returns:
        The parsed expense list.

    Raises:
        ValueError: If the top-level JSON value is not a list.
    """
    file = Path(path)
    if not file.exists():
        return []
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Corrupt store: expected a JSON list.")
    return [Expense(**item) for item in data]


def save(path: str | Path, expenses: list[Expense]) -> None:
    """Write expenses to *path* as indented JSON.

    Parent directories are created if needed.

    Args:
        path: Destination JSON file.
        expenses: Records to write.
    """
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps([asdict(item) for item in expenses], indent=2), encoding="utf-8")


def filter_expenses(
    expenses: list[Expense],
    category: str | None = None,
    month: str | None = None,
) -> list[Expense]:
    """Filter by exact category (case-insensitive) and/or a ``YYYY-MM`` prefix.

    Args:
        expenses: Records to filter.
        category: Category to match, or ``None`` for all.
        month: Date prefix to match, or ``None`` for all.

    Returns:
        The matching records in their original order.
    """
    return [
        item
        for item in expenses
        if (not category or item.category.lower() == category.lower())
        and (not month or item.date.startswith(month))
    ]


def summarize(expenses: list[Expense]) -> Summary:
    """Compute count, total, category totals and the largest category.

    Args:
        expenses: Records to aggregate.

    Returns:
        A :class:`Summary` with sorted category totals.
    """
    by_category: dict[str, float] = {}
    for item in expenses:
        by_category[item.category] = round(by_category.get(item.category, 0.0) + item.amount, 2)
    top = max(by_category, key=lambda name: by_category[name]) if by_category else None
    return Summary(
        count=len(expenses),
        total=round(sum(item.amount for item in expenses), 2),
        by_category=dict(sorted(by_category.items())),
        top_category=top,
    )


def export_csv(expenses: list[Expense], output: str | Path) -> None:
    """Write expenses to a CSV file with a header row.

    Args:
        expenses: Records to export.
        output: Destination CSV path.
    """
    with Path(output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_FIELDS))
        writer.writeheader()
        for item in expenses:
            writer.writerow(asdict(item))
