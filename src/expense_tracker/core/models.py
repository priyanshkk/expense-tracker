"""The expense record and its validation rules."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime

from expense_tracker.config import DATE_FORMAT


@dataclass
class Expense:
    """A single expense entry.

    Attributes:
        id: Eight-character hexadecimal identifier.
        date: ISO date in ``YYYY-MM-DD`` form.
        amount: Positive amount rounded to two decimals.
        category: Non-empty category name.
        note: Optional free-text note.
    """

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
    ) -> Expense:
        """Validate inputs and build a new expense with a generated id.

        Args:
            amount: Positive amount.
            category: Category name; surrounding whitespace is stripped.
            note: Optional note; surrounding whitespace is stripped.
            day: ``YYYY-MM-DD`` date, or ``None`` for today.

        Returns:
            A validated :class:`Expense`.

        Raises:
            ValueError: If the amount is not positive, the category is empty,
                or the date is not in ``YYYY-MM-DD`` form.
        """
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
