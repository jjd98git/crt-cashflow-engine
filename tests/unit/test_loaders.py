"""Loaders fail loud and never coerce."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from crt.io.appendix_g import AppendixGError, load_appendix_g
from crt.io.csv_reader import CsvLayoutError
from crt.io.deal_terms import DealTerms, DealTermsError, load_deal_terms
from crt.io.rep_lines import RepLineError, load_rep_lines
from crt.money import MoneyError, parse_money, round2, round7

pytestmark = pytest.mark.fast

D = Decimal


def test_parse_money_strips_separators_and_rejects_bad_forms() -> None:
    assert parse_money("5,703,897,138.22", field="x", record="r") == D("5703897138.22")
    assert parse_money("275900000.00", field="x", record="r") == D("275900000.00")
    for bad in ("1,00.00", "12.5", "abc", "", "1e5", "12,345.678"):
        with pytest.raises(MoneyError, match="field 'x' of record 'r'"):
            parse_money(bad, field="x", record="r")


def test_rounding_is_half_up() -> None:
    assert round2(D("0.005")) == D("0.01")
    assert round2(D("0.0049999")) == D("0.00")
    assert round2(D("2.675")) == D("2.68")
    assert round7(D("0.96474995624")) == D("0.9647500")
    assert round7(D("0.00000005")) == D("0.0000001")


def test_rep_lines_load_and_reject_tampering(tmp_path: Path, project_root: Path, deal: DealTerms) -> None:
    source = project_root / "data/ppm_tables/appendix_c_rep_lines.csv"
    lines = load_rep_lines(source, cut_off_date_balance=deal.cut_off_date_balance)
    assert len(lines) == 31
    assert lines[16].interest_rate == D("0.06933")

    text = source.read_text(encoding="utf-8")
    tampered = tmp_path / "rep.csv"
    tampered.write_text(text.replace('"5,703,897,138.22"', '"5,703,897,138.23"'), encoding="utf-8")
    with pytest.raises(RepLineError, match="Cut-off Date Balance"):
        load_rep_lines(tampered, cut_off_date_balance=deal.cut_off_date_balance)

    short = tmp_path / "short.csv"
    short.write_text("\n".join(text.splitlines()[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(RepLineError, match="30 rows"):
        load_rep_lines(short, cut_off_date_balance=deal.cut_off_date_balance)

    wrong_header = tmp_path / "hdr.csv"
    wrong_header.write_text(text.replace("interest_rate_pct", "rate"), encoding="utf-8")
    with pytest.raises(CsvLayoutError):
        load_rep_lines(wrong_header, cut_off_date_balance=deal.cut_off_date_balance)


def test_appendix_g_rejects_inconsistent_aggregate(tmp_path: Path, project_root: Path) -> None:
    source = project_root / "data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv"
    text = source.read_text(encoding="utf-8")
    bad = tmp_path / "g.csv"
    bad.write_text(text.replace("10892238.08", "10892238.09", 1), encoding="utf-8")
    with pytest.raises(AppendixGError, match="aggregate"):
        load_appendix_g(bad)


def test_deal_terms_rejects_tampered_tranche_sum(tmp_path: Path, project_root: Path) -> None:
    source = project_root / "data/deal_terms/stacr_2026_dna1.yaml"
    text = source.read_text(encoding="utf-8")
    bad = tmp_path / "deal.yaml"
    bad.write_text(text.replace('value: "56953878"', 'value: "56953879"'), encoding="utf-8")
    with pytest.raises(DealTermsError, match="Cut-off Date"):
        load_deal_terms(bad)


def test_deal_terms_percentages_are_decimal_not_float(deal: DealTerms) -> None:
    assert isinstance(deal.minimum_credit_enhancement_threshold, Decimal)
    assert isinstance(deal.notes["A-1"].margin, Decimal)
    assert str(deal.sofr_rate_flat) == "0.0365786"
