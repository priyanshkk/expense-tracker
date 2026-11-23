# Usage

All examples use `python -m expense_tracker`. After an editable install the
`expense-tracker` console script is also available. Record ids are generated,
so yours will differ from the samples.

## Global option: `--file`

Place `--file` before the subcommand. It selects the JSON store (default:
`./.expense-tracker.json`, or `EXPENSE_STORE`).

```console
$ python -m expense_tracker --file ./my-expenses.json list
No expenses found.
```

## `add`

```console
$ python -m expense_tracker --file ./demo.json add 250 Food --note "lunch" --date 2026-11-23
Added cd1e2a6f: Food - 250.00 on 2026-11-23

$ python -m expense_tracker --file ./demo.json add 45.50 Transport --note "bus" --date 2026-11-24
Added ff36f7b8: Transport - 45.50 on 2026-11-24
```

`--date` must be `YYYY-MM-DD`; without it today's date is used. The category is
optional: when omitted, `EXPENSE_DEFAULT_CATEGORY` (default `Misc`) is used.

```console
$ EXPENSE_DEFAULT_CATEGORY=Travel python -m expense_tracker --file ./demo.json add 42 --date 2026-11-26
Added 1688b928: Travel - 42.00 on 2026-11-26
```

Invalid input is reported on stderr with exit status 1:

```console
$ python -m expense_tracker --file ./demo.json add 0 Food
error: Amount must be greater than zero.
$ python -m expense_tracker --file ./demo.json add 10 Food --date 23-11-2026
error: Date must be YYYY-MM-DD, got '23-11-2026'
```

## `list`

```console
$ python -m expense_tracker --file ./demo.json list
cd1e2a6f  2026-11-23  Food               250.00  # lunch
ff36f7b8  2026-11-24  Transport           45.50  # bus
```

Filter by month (`YYYY-MM`), category (case-insensitive) or both:

```console
$ python -m expense_tracker --file ./demo.json list --month 2026-11 --category Food
cd1e2a6f  2026-11-23  Food               250.00  # lunch
```

An empty result prints `No expenses found.` and exits 0.

## `summary`

```console
$ python -m expense_tracker --file ./demo.json summary --month 2026-11
Expenses : 2
Total    : 295.50
  Food               250.00
  Transport           45.50
Top category: Food
```

`--category` is also accepted. With no expenses in scope the output is
`Expenses : 0`, `Total    : 0.00` and no category lines.

## `delete`

Use an id from `list`:

```console
$ python -m expense_tracker --file ./demo.json delete 2f232afc
Deleted 2f232afc
$ python -m expense_tracker --file ./demo.json delete 00000000
No expense with id '00000000'
```

An unknown id exits 1; a successful delete exits 0.

## `export`

```console
$ python -m expense_tracker --file ./demo.json export report.csv --month 2026-11
Exported 2 expense(s) to report.csv
```

The CSV header is `id,date,amount,category,note`. Amounts are written as stored
(for example `250.0`, not `250.00`).

## Environment configuration

```console
$ export EXPENSE_STORE=./demo.json
$ export EXPENSE_DEFAULT_CATEGORY=Travel
$ python -m expense_tracker add 42 --date 2026-11-26
Added 1688b928: Travel - 42.00 on 2026-11-26

$ python -m expense_tracker list
1688b928  2026-11-26  Travel              42.00
```

An explicit `--file` wins over `EXPENSE_STORE`; an explicit category wins over
`EXPENSE_DEFAULT_CATEGORY`. Blank environment values fall back to the defaults.

## Library use

```python
from expense_tracker import Expense, filter_expenses, load, save, summarize

items = [Expense.create(12.5, "Food", "lunch", "2026-11-23")]
save("expenses.json", items)
print(summarize(load("expenses.json")))
print(filter_expenses(items, month="2026-11"))
```
