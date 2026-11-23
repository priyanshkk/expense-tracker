"""Constants and environment-backed defaults for expense-tracker.

``EXPENSE_STORE`` selects the JSON file used when ``--file`` is omitted.
``EXPENSE_DEFAULT_CATEGORY`` is used when ``add`` is called without a category.
"""

from __future__ import annotations

import os

#: Format used for expense dates and accepted by ``--date``.
DATE_FORMAT = "%Y-%m-%d"
#: Default JSON store, relative to the current working directory.
DEFAULT_STORE = ".expense-tracker.json"
#: Default category when none is supplied.
DEFAULT_CATEGORY = "Misc"
STORE_ENV = "EXPENSE_STORE"
CATEGORY_ENV = "EXPENSE_DEFAULT_CATEGORY"


def get_store_path() -> str:
    """Return the configured JSON store path.

    Returns:
        The value of ``EXPENSE_STORE`` when non-empty, otherwise
        :data:`DEFAULT_STORE`.
    """
    return os.environ.get(STORE_ENV, DEFAULT_STORE).strip() or DEFAULT_STORE


def get_default_category() -> str:
    """Return the category used when ``add`` has no positional category.

    Returns:
        The value of ``EXPENSE_DEFAULT_CATEGORY`` when non-empty, otherwise
        :data:`DEFAULT_CATEGORY`.
    """
    return os.environ.get(CATEGORY_ENV, DEFAULT_CATEGORY).strip() or DEFAULT_CATEGORY
