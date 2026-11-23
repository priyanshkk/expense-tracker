"""Argument parsing and command dispatch for expense-tracker."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from expense_tracker.config import get_default_category, get_store_path
from expense_tracker.core.ledger import export_csv, filter_expenses, load, save, summarize
from expense_tracker.core.models import Expense


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser with environment-aware defaults.

    Returns:
        A parser with the ``add``, ``list``, ``summary``, ``delete`` and
        ``export`` subcommands.
    """
    parser = argparse.ArgumentParser(description="Track expenses from the terminal.")
    parser.add_argument(
        "--file",
        default=get_store_path(),
        help="path to the JSON store (default: ./.expense-tracker.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category", nargs="?", help="default: EXPENSE_DEFAULT_CATEGORY (Misc)")
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
    """Run the CLI.

    Args:
        argv: Optional argument list; ``sys.argv[1:]`` is used when omitted.

    Returns:
        ``0`` on success and ``1`` for store, validation or id errors.
    """
    args = build_parser().parse_args(argv)
    store = Path(args.file)

    try:
        expenses = load(store)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read store: {exc}", file=sys.stderr)
        return 1

    if args.command == "add":
        category = args.category or get_default_category()
        try:
            item = Expense.create(args.amount, category, args.note, args.date)
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
