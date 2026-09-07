"""Deal facts for the sidebar (display only).  Everything the engine consumes comes from
``DealTerms``; the deal name and Table 3 initial subordination percentages are read from
the same YAML for display because the engine has no use for them."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER, DealTerms, DealTermsError
from crt.io.yaml_decimal import DecimalSafeLoader


@dataclass(frozen=True)
class TrancheDisplayRow:
    tranche: str
    initial_class_notional_amount: Decimal
    initial_subordination_pct: Decimal  # Table 3 column, as printed (percent)
    note_issued: bool


@dataclass(frozen=True)
class NoteDisplayRow:
    note: str
    original_class_principal_balance: Decimal
    margin_pct: Decimal
    initial_class_coupon_pct: Decimal
    expected_wal_years_table1: Decimal
    expected_principal_window_table1: str


@dataclass(frozen=True)
class DealDisplay:
    name: str
    closing_date: date
    cut_off_date: date
    cut_off_date_balance: Decimal
    first_payment_date: date
    scheduled_maturity_payment_date_number: int
    sofr_rate_flat_pct: Decimal
    tranches: tuple[TrancheDisplayRow, ...]
    notes: tuple[NoteDisplayRow, ...]


def _leaf_value(raw: dict[str, Any], path: str) -> Any:
    node: Any = raw
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            raise DealTermsError(f"deal terms: missing field {path!r}")
        node = node[key]
    if not isinstance(node, dict) or "value" not in node or node["value"] is None:
        raise DealTermsError(f"deal terms: {path!r} is not a leaf with a 'value'")
    return node["value"]


def load_deal_display(deal_terms_path: Path, deal: DealTerms) -> DealDisplay:
    with deal_terms_path.open(encoding="utf-8") as handle:
        raw = yaml.load(handle, Loader=DecimalSafeLoader)
    if not isinstance(raw, dict):
        raise DealTermsError(f"{deal_terms_path}: top level is not a mapping")
    name = str(_leaf_value(raw, "deal.name"))
    tranches: list[TrancheDisplayRow] = []
    for tranche in TRANCHE_ORDER:
        subordination = _leaf_value(raw, f"reference_tranches.{tranche}.initial_subordination_pct")
        if isinstance(subordination, bool) or not isinstance(subordination, (int, Decimal)):
            raise DealTermsError(
                f"deal terms: reference_tranches.{tranche}.initial_subordination_pct is not numeric"
            )
        tranches.append(
            TrancheDisplayRow(
                tranche=tranche,
                initial_class_notional_amount=deal.initial_class_notional_amounts[tranche],
                initial_subordination_pct=Decimal(subordination),
                note_issued=tranche in NOTE_CLASSES,
            )
        )
    notes = tuple(
        NoteDisplayRow(
            note=note,
            original_class_principal_balance=terms.original_class_principal_balance,
            margin_pct=terms.margin.scaleb(2),
            initial_class_coupon_pct=terms.initial_class_coupon.scaleb(2),
            expected_wal_years_table1=terms.expected_wal_years_table1,
            expected_principal_window_table1=(
                f"{terms.expected_principal_window_table1[0]}-"
                f"{terms.expected_principal_window_table1[1]}"
            ),
        )
        for note, terms in ((n, deal.notes[n]) for n in NOTE_CLASSES)
    )
    return DealDisplay(
        name=name,
        closing_date=deal.closing_date,
        cut_off_date=deal.cut_off_date,
        cut_off_date_balance=deal.cut_off_date_balance,
        first_payment_date=deal.first_payment_date,
        scheduled_maturity_payment_date_number=deal.scheduled_maturity_payment_date_number,
        sofr_rate_flat_pct=deal.sofr_rate_flat.scaleb(2),
        tranches=tuple(tranches),
        notes=notes,
    )
