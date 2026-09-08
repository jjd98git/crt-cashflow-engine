"""Formatting for the GUI (display only; no arithmetic beyond string formatting).

Two kinds of output: exact strings for tables (``format(Decimal, ",.2f")`` on cents that
the engine already rounded) and ``float`` frames for the Streamlit charts, which are the
one lossy conversion and are never fed back into anything."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pandas as pd

from crt.api import RunResult, SummaryDifference
from crt.io.deal_terms import NOTE_CLASSES
from crt.money import round_half_up
from crt.presentation import STACK_ORDER_BOTTOM_UP

WAL_DISPLAY_PLACES = 2  # R6: WAL reported to 2 decimals; the stored value is unrounded
PERCENT_DISPLAY_PLACES = 5  # R3: percentages are carried to 1/100,000 of a point


def money(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return format(value, ",.2f")


def percent_of_fraction(value: Decimal | None) -> str:
    """A fraction such as ``0.0352500`` shown as ``3.52500 %``."""
    if value is None:
        return "n/a"
    return f"{format(value.scaleb(2), f',.{PERCENT_DISPLAY_PLACES}f')} %"


def wal(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return format(round_half_up(value, WAL_DISPLAY_PLACES), ".2f")


def summary_table(result: RunResult) -> pd.DataFrame:
    """One row per Note, every cell a formatted string."""
    rows: list[dict[str, str]] = []
    for summary in result.note_summaries:
        rows.append(
            {
                "Note": summary.note,
                "Original balance": money(summary.original_balance),
                "WAL (years)": wal(summary.wal_years),
                "First principal PD": _window_cell(
                    summary.first_principal_payment_date_number,
                    summary.first_principal_payment_date,
                ),
                "Last principal PD": _window_cell(
                    summary.last_principal_payment_date_number,
                    summary.last_principal_payment_date,
                ),
                "Total principal": money(summary.total_principal),
                "Total interest": money(summary.total_interest),
                "Total write-downs": money(summary.total_write_downs),
                "Final balance": money(summary.final_balance),
            }
        )
    return pd.DataFrame(rows).set_index("Note")


def _window_cell(number: int | None, when: Any) -> str:
    if number is None or when is None:
        return "never"
    return f"{number} ({when.isoformat()})"


def pool_totals_table(result: RunResult) -> pd.DataFrame:
    totals = result.pool_totals
    rows = [
        ("Cut-off Date Balance", money(totals.cut_off_date_balance)),
        ("Collection months", f"{totals.first_month}-{totals.last_month} (to {totals.last_month_end})"),
        ("Scheduled principal", money(totals.total_scheduled_principal)),
        ("Prepayments", money(totals.total_prepayment)),
        ("Credit Event Amount", money(totals.total_credit_event_amount)),
        ("Interest", money(totals.total_interest)),
        ("Ending pool balance", money(totals.ending_balance)),
        (
            "Maturity Date",
            (
                f"PD {totals.maturity_payment_date_number} ({totals.maturity_payment_date}): "
                f"{totals.maturity_reason}"
            ),
        ),
    ]
    return pd.DataFrame(rows, columns=["Pool", "Value"]).set_index("Pool")


def _float_frame(result: RunResult, table: str) -> pd.DataFrame:
    """The polars display frame as pandas with Decimal -> float (charts only)."""
    frame = result.to_frames(money_as="float")[table]
    return pd.DataFrame(frame.to_dicts())


def tranche_balance_chart_frame(
    result: RunResult, *, label: str | None = None, include_a_h: bool = False
) -> pd.DataFrame:
    """Class Notional Amount after each Payment Date, one column per Reference Tranche in
    stack order (bottom of the stack first, each Note directly followed by its H tranche).
    A-H is omitted unless asked for: it dwarfs the others."""
    structure = _float_frame(result, "structure").set_index("payment_date_number")
    columns = {
        f"balance_after_{t}": (f"{t} ({label})" if label else t)
        for t in STACK_ORDER_BOTTOM_UP
        if include_a_h or t != "A-H"
    }
    return structure[list(columns)].rename(columns=columns)


def note_balance_chart_frame(result: RunResult, *, label: str | None = None) -> pd.DataFrame:
    """Class Principal Balance after each Payment Date, one column per Note."""
    structure = _float_frame(result, "structure").set_index("payment_date_number")
    columns = {f"balance_after_{n}": (f"{n} ({label})" if label else n) for n in NOTE_CLASSES}
    return structure[list(columns)].rename(columns=columns)


def note_flows_chart_frame(result: RunResult, note: str) -> pd.DataFrame:
    """Principal paid, interest and write-down per Payment Date for one Note."""
    flows = _float_frame(result, "note_cashflows")
    flows = flows[flows["note"] == note].set_index("payment_date_number")
    return flows[["principal_paid", "interest", "write_down"]].rename(
        columns={"principal_paid": "Principal", "interest": "Interest", "write_down": "Write-down"}
    )


def pool_balance_chart_frame(result: RunResult, *, label: str | None = None) -> pd.DataFrame:
    months = _float_frame(result, "pool_months").set_index("month")
    name = f"Pool UPB ({label})" if label else "Pool UPB"
    return months[["balance_end"]].rename(columns={"balance_end": name})


def display_table(result: RunResult, table: str) -> pd.DataFrame:
    """A full table with exact string money (for ``st.dataframe``)."""
    frame = result.to_frames(money_as="str")[table]
    return pd.DataFrame(frame.to_dicts())


def difference_table(differences: tuple[SummaryDifference, ...]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for difference in differences:
        rows.append(
            {
                "Note": difference.note,
                "Metric": difference.metric,
                "A": _metric_cell(difference.metric, difference.a),
                "B": _metric_cell(difference.metric, difference.b),
                "B - A": _metric_cell(difference.metric, difference.b_minus_a),
            }
        )
    return pd.DataFrame(rows)


def _metric_cell(metric: str, value: Decimal | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    if metric == "wal_years":
        return wal(value)
    return money(value)
