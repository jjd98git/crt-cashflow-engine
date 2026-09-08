"""Altair charts for the GUI (display only).

The stacked tranche chart takes the ``float`` frame from ``crt.gui.formatting`` (already
the one lossy Decimal -> float conversion of the GUI) and only reshapes it: nothing is
added, scaled or summed here; Vega-Lite stacks the bands on screen.  The stack order and
the colours come from ``crt.presentation`` so that the GUI, the Excel export and the
browser page agree.
"""

from __future__ import annotations

import altair as alt
import pandas as pd

from crt.presentation import STACK_ORDER_BOTTOM_UP, tranche_colour_css

STACK_RANK_FIELD = "stack_rank"
PAYMENT_DATE_TITLE = "Payment Date #"
BALANCE_TITLE = "Class Notional Amount (USD)"
X_AXIS_TICK_EVERY = 12  # one label per year of Payment Dates, as in the workbook charts


def stack_columns(frame: pd.DataFrame) -> list[str]:
    """The frame's tranche columns, checked to be in ``STACK_ORDER_BOTTOM_UP``."""
    columns = [str(column) for column in frame.columns]
    expected = [tranche for tranche in STACK_ORDER_BOTTOM_UP if tranche in columns]
    if columns != expected:
        raise ValueError(
            f"chart frame columns {columns} are not in stack order {expected}"
        )
    return columns


def stacked_tranche_chart(frame: pd.DataFrame, *, title: str, height: int = 380) -> alt.Chart:
    """A stacked area of ``frame`` (index: Payment Date number; one column per tranche,
    bottom of the stack first).  The first column sits on the baseline, the last on top;
    the legend mirrors the stack, top band first, so a Note's H tranche reads directly
    next to its Note in both."""
    tranches = stack_columns(frame)
    top_down = list(reversed(tranches))
    rank = {tranche: index for index, tranche in enumerate(tranches)}
    index_name = str(frame.index.name or "payment_date_number")
    long = frame.rename_axis(index_name).reset_index().melt(
        id_vars=index_name, var_name="Tranche", value_name="Balance"
    )
    long[STACK_RANK_FIELD] = long["Tranche"].map(rank)
    chart: alt.Chart = (
        alt.Chart(long, title=title, height=height)
        .mark_area(line={"strokeWidth": 0.5}, opacity=1)
        .encode(
            x=alt.X(
                f"{index_name}:Q",
                title=PAYMENT_DATE_TITLE,
                axis=alt.Axis(tickMinStep=X_AXIS_TICK_EVERY),
                scale=alt.Scale(nice=False),
            ),
            y=alt.Y("Balance:Q", stack="zero", title=BALANCE_TITLE, axis=alt.Axis(format="~s")),
            color=alt.Color(
                "Tranche:N",
                sort=top_down,
                scale=alt.Scale(domain=top_down, range=[tranche_colour_css(t) for t in top_down]),
                legend=alt.Legend(title="Tranche (top of stack first)"),
            ),
            order=alt.Order(f"{STACK_RANK_FIELD}:Q", sort="ascending"),
            tooltip=[
                alt.Tooltip(f"{index_name}:Q", title=PAYMENT_DATE_TITLE),
                alt.Tooltip("Tranche:N"),
                alt.Tooltip("Balance:Q", format=",.2f", title=BALANCE_TITLE),
            ],
        )
    )
    return chart
