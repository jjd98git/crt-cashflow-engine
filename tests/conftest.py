"""Shared fixtures: the real inputs, loaded once per session."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from crt.io.appendix_g import AppendixG, load_appendix_g
from crt.io.deal_terms import DealTerms, load_deal_terms
from crt.io.rep_lines import RepLine, load_rep_lines
from crt.pool.projection import PoolProjection, project_pool

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def deal() -> DealTerms:
    return load_deal_terms(PROJECT_ROOT / "data/deal_terms/stacr_2026_dna1.yaml")


@pytest.fixture(scope="session")
def rep_lines(deal: DealTerms) -> tuple[RepLine, ...]:
    return load_rep_lines(
        PROJECT_ROOT / "data/ppm_tables/appendix_c_rep_lines.csv",
        cut_off_date_balance=deal.cut_off_date_balance,
    )


@pytest.fixture(scope="session")
def appendix_g() -> AppendixG:
    return load_appendix_g(
        PROJECT_ROOT / "data/ppm_tables/appendix_g_class_a1_reduction_schedule.csv"
    )


@pytest.fixture(scope="session")
def pool_10_0(deal: DealTerms, rep_lines: tuple[RepLine, ...]) -> PoolProjection:
    """The spec's worked-example pool: 10 % CPR, 0 % CER."""
    return project_pool(
        rep_lines,
        cpr=Decimal("0.10"),
        cer=Decimal(0),
        cut_off_date_balance=deal.cut_off_date_balance,
    )


@pytest.fixture(scope="session")
def rep_lines_pool_0_0(deal: DealTerms, rep_lines: tuple[RepLine, ...]) -> PoolProjection:
    """0 % CPR, 0 % CER: the pool on which A-1 retires on Payment Date 39."""
    return project_pool(
        rep_lines,
        cpr=Decimal(0),
        cer=Decimal(0),
        cut_off_date_balance=deal.cut_off_date_balance,
    )
