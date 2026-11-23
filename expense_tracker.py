"""A JSON-backed command-line expense tracker.

Standard library only. Data is stored as a list of expense objects in a JSON
file, which keeps the format easy to inspect, back up and version.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

DATE_FORMAT = "%Y-%m-%d"


@dataclass
class Expense:
    id: str
    date: str
    amount: float
    category: str
    note: str = ""

    @classmethod
    def create(
        cls,
        amount: float,
        category: str,
        note: str = "",
        day: str | None = None,
    ) -> "Expense":
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        category = category.strip()
        if not category:
            raise ValueError("Category cannot be empty.")
        day = day or date.today().isoformat()
        try:
            datetime.strptime(day, DATE_FORMAT)
        except ValueError as exc:
            raise ValueError(f"Date must be YYYY-MM-DD, got {day!r}") from exc
        return cls(
            id=uuid.uuid4().hex[:8],
            date=day,
            amount=round(float(amount), 2),
            category=category,
            note=note.strip(),
        )


def load(path: str | Path) -> list[Expense]:
    """Load expenses from *path*, returning an empty list if it does not exist."""
    file = Path(path)
    if not file.exists():
        return []
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Corrupt store: expected a JSON list.")
    return [Expense(**item) for item in data]


def save(path: str | Path, expenses: list[Expense]) -> None:
    """Atomically-ish write expenses to *path*."""
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps([asdict(item) for item in expenses], indent=2), encoding="utf-8")


def filter_expenses(
    expenses: list[Expense],
    category: str | None = None,
    month: str | None = None,
) -> list[Expense]:
    """Filter by exact category and/or a YYYY-MM month prefix."""
    return [
        item
        for item in expenses
        if (not category or item.category.lower() == category.lower())
        and (not month or item.date.startswith(month))
    ]


def summarize(expenses: list[Expense]) -> dict:
    """Return count, total, per-category totals and the largest category."""
    by_category: dict[str, float] = {}
    for item in expenses:
        by_category[item.category] = round(by_category.get(item.category, 0.0) + item.amount, 2)
    top = max(by_category, key=by_category.get) if by_category else None
    return {
        "count": len(expenses),
        "total": round(sum(item.amount for item in expenses), 2),
        "by_category": dict(sorted(by_category.items())),
        "top_category": top,
    }


def export_csv(expenses: list[Expense], output: str | Path) -> None:
    """Write expenses to a CSV file."""
    with Path(output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "date", "amount", "category", "note"])
        writer.writeheader()
        for item in expenses:
            writer.writerow(asdict(item))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track expenses from the terminal.")
    parser.add_argument(
        "--file",
        default=".expense-tracker.json",
        help="path to the JSON store (default: ./.expense-tracker.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("--note", default="")
    add.add_argument("--date", help="YYYY-MM-DD (default: today)")

    listing = sub.add_parser("list", help="list expenses")
    listing.add_argument("--category")
    listing.add_argument("--month", help="YYYY-MM")

    summary = sub.add_parser("summary", help="show totals")
    summary.add_argument("--category")
    summary.add_argument("--month", help="YYYY-MM")

    delete = sub.add_parser("delete", help="delete an expense by id")
    delete.add_argument("id")

    export = sub.add_parser("export", help="export to CSV")
    export.add_argument("output")
    export.add_argument("--month", help="YYYY-MM")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = Path(args.file)

    try:
        expenses = load(store)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read store: {exc}", file=sys.stderr)
        return 1

    if args.command == "add":
        try:
            item = Expense.create(args.amount, args.category, args.note, args.date)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        expenses.append(item)
        save(store, expenses)
        print(f"Added {item.id}: {item.category} - {item.amount:.2f} on {item.date}")
        return 0

    if args.command == "delete":
        remaining = [item for item in expenses if item.id != args.id]
        if len(remaining) == len(expenses):
            print(f"No expense with id {args.id!r}", file=sys.stderr)
            return 1
        save(store, remaining)
        print(f"Deleted {args.id}")
        return 0

    if args.command == "export":
        selected = filter_expenses(expenses, month=args.month)
        export_csv(selected, args.output)
        print(f"Exported {len(selected)} expense(s) to {args.output}")
        return 0

    selected = filter_expenses(
        expenses,
        category=getattr(args, "category", None),
        month=getattr(args, "month", None),
    )

    if args.command == "list":
        if not selected:
            print("No expenses found.")
            return 0
        for item in selected:
            note = f"  # {item.note}" if item.note else ""
            print(f"{item.id}  {item.date}  {item.category:<15} {item.amount:>9.2f}{note}")
        return 0

    result = summarize(selected)
    print(f"Expenses : {result['count']}")
    print(f"Total    : {result['total']:.2f}")
    for category, total in result["by_category"].items():
        print(f"  {category:<15} {total:>9.2f}")
    if result["top_category"]:
        print(f"Top category: {result['top_category']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
