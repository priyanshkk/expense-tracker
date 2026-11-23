# Architecture

## Module map

```text
src/expense_tracker/
├── __init__.py        public API re-exports and version
├── __main__.py        `python -m expense_tracker` entry point
├── config.py          constants and environment-backed defaults
└── core/
    ├── __init__.py    core package marker
    ├── models.py      Expense dataclass and validation
    ├── ledger.py      JSON load/save, filtering, summary, CSV export
    └── cli.py         argparse parser and command dispatch
```

There is no `utils` package: the modules share only small configuration
constants, so a generic helper module would be artificial.

## Data flow

Every command starts by building the parser (which reads the environment for
`--file` and the default category), resolving the store path, and calling
`ledger.load()`. A missing file yields an empty list; a corrupt store exits
with status 1 and an `error: could not read store:` message on stderr.

| Command | Flow |
| --- | --- |
| `add` | Resolve category from the positional argument or `EXPENSE_DEFAULT_CATEGORY`, call `Expense.create()` to validate and assign an 8-hex id, append, `save()`, print confirmation. |
| `list` | Apply `filter_expenses()` with optional `--category` and `--month`, then print one aligned line per record or `No expenses found.` |
| `summary` | Apply the same filter, then `summarize()` computes count, total, sorted per-category totals and the top category. |
| `delete` | Remove records whose id matches; an unchanged list means the id was unknown (status 1). |
| `export` | Filter by `--month` only, then write a header and one CSV row per record via `csv.DictWriter`. |

## Design decisions

- **JSON array of objects:** the store can be inspected, backed up and edited
  with any text editor; no database or migration layer is needed.
- **Dataclass plus `asdict()`:** the same field definition drives validation,
  JSON serialization and CSV column order (`CSV_FIELDS`).
- **Validation in `Expense.create()`:** a positive amount, a non-empty category
  and a strict `YYYY-MM-DD` date are enforced before anything is written.
- **Direct writes:** `save()` creates parent directories and writes the whole
  JSON document. It is intentionally simple; it is not an atomic replace and
  does not use file locking.
- **ids are 8-hex prefixes of `uuid4()`:** short enough to read in a terminal.
  They are not cryptographically meaningful and are not used as access tokens.
- **Environment defaults are read at call time:** `get_store_path()` and
  `get_default_category()` are functions, so a change to the environment
  affects the next command. Blank values fall back to the documented defaults.
- **Category is optional:** `add AMOUNT` uses the configured default category.
  Supplying a category behaves exactly as before, so the change is additive.
- **Typed summary:** a `TypedDict` gives the CLI checked access to aggregate
  fields without introducing a runtime dependency.

## Testing model

`tests/test_core.py` covers validation, persistence, filtering, aggregation and
config parsing. `tests/test_main.py` calls `main()` with argument lists against
a temporary store and captures stdout/stderr. Both modules insert `src/` into
`sys.path` because plain `unittest discover -s tests` uses `tests/` as its
top-level directory.
