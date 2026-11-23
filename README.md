# Expense Tracker

A command-line expense manager that stores everything in a readable JSON file.
Add expenses, filter them, see category totals and export to CSV — no database,
no dependencies.

## Usage

```bash
# Add an expense
python expense_tracker.py add 250 Food --note "lunch" --date 2026-11-23

# List everything, or filter
python expense_tracker.py list
python expense_tracker.py list --month 2026-11 --category Food

# Category breakdown
python expense_tracker.py summary --month 2026-11

# Delete by id (ids are shown by `list`)
python expense_tracker.py delete a1b2c3d4

# Export to CSV
python expense_tracker.py export report.csv --month 2026-11

# Use a different store file
python expense_tracker.py --file ~/my-expenses.json add 99 Transport --note "bus"
```

## Data format

The store is a JSON array of objects:

```json
[
  {
    "id": "a1b2c3d4",
    "date": "2026-11-23",
    "amount": 250.0,
    "category": "Food",
    "note": "lunch"
  }
]
```

That makes backups a simple file copy and lets you inspect the data with any
text editor.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
