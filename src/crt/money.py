"""Decimal helpers shared by every engine module.

Rounding policy: spec ``00-overview.md`` section 3.2.  Every rounding point in the engine
calls one of the helpers below with ``ROUND_HALF_UP`` (register P51 as applied by A7, A8,
A12).  Nothing else in the engine rounds.  Money is never a ``float`` (CLAUDE.md rule 3).
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, getcontext

ZERO = Decimal(0)
ONE = Decimal(1)
HUNDRED = Decimal(100)
TWELVE = Decimal(12)

# R1 / R2: dollar amounts to the cent, one-half cent rounded up (P51, A7, A12).
CENT = Decimal("0.01")
# R3: percentages to 1/100,000 of a percentage point = 7 decimal places as a fraction
# (P51, A12), e.g. Decimal("0.9647500").
PERCENT_QUANTUM = Decimal("0.0000001")

# A14: Decimal context precision must be at least 28 significant digits (Python's default).
MINIMUM_DECIMAL_PRECISION = 28


class MoneyError(ValueError):
    """A money or rate field could not be parsed exactly."""


def require_decimal_context() -> None:
    """Raise unless the active Decimal context satisfies A14 (precision >= 28)."""
    precision = getcontext().prec
    if precision < MINIMUM_DECIMAL_PRECISION:  # A14
        raise RuntimeError(
            f"Decimal context precision is {precision}; A14 requires at least "
            f"{MINIMUM_DECIMAL_PRECISION}"
        )


def round2(amount: Decimal) -> Decimal:
    """Round a dollar amount half-up to the cent (R1 / R2)."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def round7(fraction: Decimal) -> Decimal:
    """Round a percentage expressed as a fraction half-up to 7 decimal places (R3)."""
    return fraction.quantize(PERCENT_QUANTUM, rounding=ROUND_HALF_UP)


def round_half_up(value: Decimal, places: int) -> Decimal:
    """Round half-up to ``places`` decimal places.  Used for report display and the A13
    round-match criterion only; never inside the cashflow arithmetic."""
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


# Printed dollar amount: optional thousands separators, exactly two decimals.
_MONEY_WITH_SEPARATORS = re.compile(r"^-?\d{1,3}(?:,\d{3})*\.\d{2}$")
_MONEY_PLAIN = re.compile(r"^-?\d+\.\d{2}$")


def parse_money(text: str, *, field: str, record: str) -> Decimal:
    """Parse a printed dollar amount such as ``"5,703,897,138.22"`` to ``Decimal``.

    Thousands separators are stripped explicitly.  Anything that is not a plain number
    with exactly two decimals raises ``MoneyError`` naming the field and the record; the
    loader never coerces.
    """
    stripped = text.strip()
    if not (_MONEY_WITH_SEPARATORS.match(stripped) or _MONEY_PLAIN.match(stripped)):
        raise MoneyError(
            f"field {field!r} of record {record!r}: {text!r} is not a dollar amount with "
            "two decimals"
        )
    return Decimal(stripped.replace(",", ""))


_PERCENT = re.compile(r"^-?\d+(?:\.\d+)?%?$")


def parse_percent(text: str, *, field: str, record: str) -> Decimal:
    """Parse a printed percentage such as ``"0.25%"`` or ``"6.933"`` to the *percentage*
    number (``Decimal("0.25")``), not the fraction.  Use ``percent_to_fraction`` next."""
    stripped = text.strip()
    if not _PERCENT.match(stripped):
        raise MoneyError(f"field {field!r} of record {record!r}: {text!r} is not a percentage")
    return Decimal(stripped.rstrip("%"))


def percent_to_fraction(percent: Decimal) -> Decimal:
    """``Decimal("6.933")`` -> ``Decimal("0.06933")`` exactly (a power-of-ten shift)."""
    return percent.scaleb(-2)


def parse_int(text: str, *, field: str, record: str) -> int:
    """Parse a printed integer; raise naming the field and record otherwise."""
    stripped = text.strip()
    if not re.match(r"^-?\d+$", stripped):
        raise MoneyError(f"field {field!r} of record {record!r}: {text!r} is not an integer")
    return int(stripped)
