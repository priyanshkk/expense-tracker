# Expense Tracker

[![Tests](https://github.com/priyanshkk/expense-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/priyanshkk/expense-tracker/actions/workflows/tests.yml)
[![Lint and Typing](https://github.com/priyanshkk/expense-tracker/actions/workflows/linter.yml/badge.svg)](https://github.com/priyanshkk/expense-tracker/actions/workflows/linter.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Tests: unittest](https://img.shields.io/badge/tests-unittest-brightgreen.svg)
![Typing: mypy](https://img.shields.io/badge/typing-mypy-blue.svg)

## The problem

Expense apps are often heavier than the job: a database, a server and an
account before you can write down what you spent. This tool keeps the workflow
to one terminal command and one plain JSON file you can inspect, copy or edit
yourself. It validates input, groups totals by category and exports CSV — with
no runtime dependencies.

## Overview

`expense_tracker` stores records in a JSON array with an 8-character id, date,
amount, category and note. It supports adding, listing (with month/category
filters), summarizing, deleting by id and exporting to CSV. It runs on Python
3.10-3.13, uses only the standard library, and works both as a CLI
(`python -m expense_tracker`) and as a library (`from expense_tracker import
Expense`).

Details: [documentation index](docs/index.md) · [architecture](docs/architecture.md)
· [full usage reference](docs/usage.md).

## Tech stack

| Area | Choice | Why |
| --- | --- | --- |
| Language | Python 3.10+ | Standard-library only at runtime |
| Storage | JSON file via `json` | Readable, portable, trivial to back up |
| Data model | `dataclasses` + `TypedDict` | One definition drives validation and exports |
| CLI | `argparse` | Subcommands and validation without a dependency |
| Packaging | Hatchling, PEP 621 | `src/` layout and console-script entry point |
| Testing | `unittest`, `pytest` | Same tests run under both runners |
| Linting | Ruff (`E,F,I,UP,B,SIM`, 100 columns) | Fast, deterministic checks |
| Typing | mypy (strict) | Checked over `src/expense_tracker` |
| CI | GitHub Actions | Tests on 3.10-3.13, lint + typing on 3.12 |

## Real demo output

Captured by running the CLI with a temporary `--file` store (ids are random):

```console
$ python -m expense_tracker --file ./demo.json add 250 Food --note "lunch" --date 2026-11-23
Added cd1e2a6f: Food - 250.00 on 2026-11-23

$ python -m expense_tracker --file ./demo.json add 45.50 Transport --note "bus" --date 2026-11-24
Added ff36f7b8: Transport - 45.50 on 2026-11-24

$ python -m expense_tracker --file ./demo.json list --month 2026-11 --category Food
cd1e2a6f  2026-11-23  Food               250.00  # lunch

$ python -m expense_tracker --file ./demo.json summary --month 2026-11
Expenses : 2
Total    : 295.50
  Food               250.00
  Transport           45.50
Top category: Food

$ python -m expense_tracker --file ./demo.json export report.csv --month 2026-11
Exported 2 expense(s) to report.csv
```

The store is a JSON array of objects, so backups are a file copy:

```json
[
  {
    "id": "cd1e2a6f",
    "date": "2026-11-23",
    "amount": 250.0,
    "category": "Food",
    "note": "lunch"
  }
]
```

## Install and setup

```bash
git clone https://github.com/priyanshkk/expense-tracker.git
cd expense-tracker

# Windows
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
.venv\Scripts\python -m expense_tracker --help

# POSIX (macOS / Linux)
sh scripts/setup.sh
.venv/bin/python -m expense_tracker --help
```

The setup scripts create `.venv` and install `requirements-dev.txt`, which is
an editable install (`-e ".[dev]"`) with pytest, Ruff, mypy and build. For a
runtime-only install use `python -m pip install -e .` (the `expense-tracker`
console script is then available). Running the tests from the repo root does
not require installation.

## Usage examples

```bash
# Add an expense (category defaults to Misc / EXPENSE_DEFAULT_CATEGORY)
python -m expense_tracker add 250 Food --note "lunch" --date 2026-11-23

# List everything, or filter by month and/or category
python -m expense_tracker list
python -m expense_tracker list --month 2026-11 --category Food

# Category breakdown
python -m expense_tracker summary --month 2026-11

# Delete by id (ids are shown by `list`)
python -m expense_tracker delete a1b2c3d4

# Export to CSV
python -m expense_tracker export report.csv --month 2026-11

# Use a different store file
python -m expense_tracker --file ./my-expenses.json add 99 Transport --note "bus"
```

Every command, flag and error case is documented in [docs/usage.md](docs/usage.md).

## Project structure

```text
expense-tracker/
├── .github/
│   ├── ISSUE_TEMPLATE/{bug_report.md,feature_request.md}
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/{tests.yml,linter.yml}
├── docs/{index.md,architecture.md,usage.md}
├── scripts/{setup.ps1,setup.sh}
├── src/expense_tracker/
│   ├── __init__.py          public API
│   ├── __main__.py          python -m entry point
│   ├── config.py            constants + environment defaults
│   └── core/
│       ├── models.py        Expense dataclass and validation
│       ├── ledger.py        JSON, filtering, summary, CSV export
│       └── cli.py           argument parsing and dispatch
├── tests/
│   ├── __init__.py          src/ path setup for package imports
│   ├── test_core.py         model, storage and config tests
│   └── test_main.py         CLI tests
├── .env.example
├── .pre-commit-config.yaml
├── requirements.txt         stdlib only (editable install)
├── requirements-dev.txt     -e ".[dev]"
├── pyproject.toml
├── LICENSE
└── README.md
```

## Environment configuration

Copy `.env.example` to `.env` if you use a dotenv loader, or export the
variables directly. `config.py` reads them on every command.

| Variable | Default | Effect |
| --- | --- | --- |
| `EXPENSE_STORE` | `.expense-tracker.json` | JSON file used when `--file` is omitted. An explicit `--file` wins. Blank values fall back to the default. |
| `EXPENSE_DEFAULT_CATEGORY` | `Misc` | Category used when `add` is called without a category. An explicit category wins. Blank values fall back to the default. |

## Testing and checks

```bash
python -m unittest discover -s tests -v   # 15 tests
python -m pytest                          # same tests via pytest
python -m ruff check .                    # E,F,I,UP,B,SIM, line length 100
python -m mypy src/expense_tracker        # strict typing
```

## Roadmap

- Optional month-to-month comparison in `summary`.
- An opt-in atomic/locked write path for concurrent use.
- Configurable currency formatting for reports.

These are ideas only; they are not implemented in this version.

## License

MIT - see [LICENSE](LICENSE). Copyright (c) 2026 Priyanshu Kumar.
