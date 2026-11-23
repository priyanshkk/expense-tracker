"""CLI tests for ``python -m expense_tracker`` behaviour."""

from __future__ import annotations

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

# Plain `unittest discover -s tests` uses tests/ as its top-level directory and
# does not import tests/__init__.py, so ensure src/ is importable here too.
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from expense_tracker import build_parser, load, main  # noqa: E402


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    """Run the CLI and capture its output.

    Args:
        argv: Arguments to pass to ``main``.

    Returns:
        A tuple of exit code, stdout and stderr.
    """
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    """Tests for add, list, summary, delete and export commands."""

    def setUp(self) -> None:
        """Create a temporary directory and store path."""
        self.temp = tempfile.TemporaryDirectory()
        self.store = Path(self.temp.name) / "expenses.json"

    def tearDown(self) -> None:
        """Remove the temporary directory."""
        self.temp.cleanup()

    def add_expense(self) -> str:
        """Add one fixed expense and return its generated id."""
        code, out, err = run_cli(
            [
                "--file",
                str(self.store),
                "add",
                "12.50",
                "Food",
                "--note",
                "lunch",
                "--date",
                "2026-01-15",
            ]
        )
        self.assertEqual((code, err), (0, ""))
        self.assertRegex(out, r"^Added [0-9a-f]{8}: Food - 12\.50 on 2026-01-15\n$")
        return out.split()[1].rstrip(":")

    def test_add_then_list_and_summary(self) -> None:
        """An added expense appears in listing and summary output."""
        self.add_expense()
        code, out, _ = run_cli(["--file", str(self.store), "list"])
        self.assertEqual(code, 0)
        self.assertIn("Food", out)
        self.assertIn("12.50", out)
        self.assertIn("lunch", out)
        code, out, _ = run_cli(["--file", str(self.store), "summary"])
        self.assertEqual(code, 0)
        self.assertIn("Expenses : 1", out)
        self.assertIn("Total    : 12.50", out)
        self.assertIn("Top category: Food", out)

    def test_list_empty_store(self) -> None:
        """An empty store reports that no expenses were found."""
        code, out, _ = run_cli(["--file", str(self.store), "list"])
        self.assertEqual((code, out), (0, "No expenses found.\n"))

    def test_delete_existing_and_missing_id(self) -> None:
        """Delete removes a known id and errors on an unknown one."""
        expense_id = self.add_expense()
        code, out, err = run_cli(["--file", str(self.store), "delete", expense_id])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, f"Deleted {expense_id}\n")
        code, out, _ = run_cli(["--file", str(self.store), "list"])
        self.assertEqual((code, out), (0, "No expenses found.\n"))
        code, _, err = run_cli(["--file", str(self.store), "delete", "deadbeef"])
        self.assertEqual(code, 1)
        self.assertIn("No expense with id 'deadbeef'", err)

    def test_export_to_csv(self) -> None:
        """Export writes the selected expenses with a header."""
        self.add_expense()
        output = Path(self.temp.name) / "report.csv"
        code, out, _ = run_cli(["--file", str(self.store), "export", str(output)])
        self.assertEqual(code, 0)
        self.assertIn("Exported 1 expense(s)", out)
        with output.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["category"], "Food")
        self.assertEqual(rows[0]["amount"], "12.5")

    def test_invalid_amount_is_reported(self) -> None:
        """A zero amount exits with status 1 and a useful message."""
        code, out, err = run_cli(["--file", str(self.store), "add", "0", "Food"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Amount must be greater than zero.", err)

    def test_corrupt_store_is_reported(self) -> None:
        """A non-list JSON document exits with status 1."""
        self.store.write_text('{"not": "a list"}', encoding="utf-8")
        code, out, err = run_cli(["--file", str(self.store), "list"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("could not read store", err)

    def test_environment_defaults_are_used_by_cli(self) -> None:
        """Both environment variables affect commands with omitted options."""
        env = {
            "EXPENSE_STORE": str(self.store),
            "EXPENSE_DEFAULT_CATEGORY": "Travel",
        }
        with mock.patch.dict("os.environ", env):
            code, out, _ = run_cli(["add", "42", "--date", "2026-01-15"])
            args = build_parser().parse_args(["add", "42"])
        self.assertEqual(code, 0)
        self.assertIn("Travel", out)
        self.assertEqual(args.file, str(self.store))
        self.assertEqual(load(self.store)[0].category, "Travel")


if __name__ == "__main__":
    unittest.main()
