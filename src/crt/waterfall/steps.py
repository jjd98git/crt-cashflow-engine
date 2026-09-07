"""Steps 1-4 of a Payment Date (spec ``02-waterfall.md`` sections 5-8).

Each step runs its PPM priority list in order, "in each case until its Class Notional
Amount is reduced to zero", passing the remaining amount down the list.  The functions
record the amount allocated to every tranche so the Notes' cashflows and the WAL can be
derived from them.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.io.deal_terms import TRANCHE_ORDER
from crt.money import ZERO
from crt.waterfall.allocation import (
    allocate_one,
    allocate_pair,
    increase_one_capped,
    increase_pair_capped,
)
from crt.waterfall.tranches import PAIRED_H_TRANCHE, TrancheState


class StepError(ValueError):
    """A priority list did not allocate the amount the spec requires it to."""


@dataclass(frozen=True)
class StepResult:
    """Amount allocated to each tranche in one step, and the unallocated remainder."""

    amounts: dict[str, Decimal]
    remaining: Decimal

    def allocated(self, tranche: str) -> Decimal:
        return self.amounts[tranche]

    def total_allocated(self) -> Decimal:
        return sum(self.amounts.values(), ZERO)


class _Ledger:
    """Records per-tranche allocations while a priority list runs."""

    def __init__(self, state: TrancheState, prior: dict[str, Decimal]) -> None:
        self.state = state
        self.prior = prior
        self.amounts: dict[str, Decimal] = {name: ZERO for name in TRANCHE_ORDER}

    def reduce_pair(self, note: str, amount: Decimal) -> Decimal:
        """Reduce a Note/H pair pro rata (A8); return the amount used."""
        allocation = allocate_pair(self.state, self.prior, note, amount)
        self.amounts[note] += allocation.note_amount
        self.amounts[PAIRED_H_TRANCHE[note]] += allocation.h_amount
        return allocation.used

    def reduce_one(self, tranche: str, amount: Decimal) -> Decimal:
        used = allocate_one(self.state, tranche, amount)
        self.amounts[tranche] += used
        return used

    def increase_pair(self, note: str, amount: Decimal) -> Decimal:
        allocation = increase_pair_capped(self.state, self.prior, note, amount)
        self.amounts[note] += allocation.note_amount
        self.amounts[PAIRED_H_TRANCHE[note]] += allocation.h_amount
        return allocation.used

    def increase_one(self, tranche: str, amount: Decimal) -> Decimal:
        used = increase_one_capped(self.state, tranche, amount)
        self.amounts[tranche] += used
        return used

    def result(self, remaining: Decimal) -> StepResult:
        return StepResult(amounts=dict(self.amounts), remaining=remaining)


def step1_tranche_write_down(
    state: TrancheState,
    prior: dict[str, Decimal],
    write_down: Decimal,
    *,
    clause_d_principal_loss: Decimal,
) -> StepResult:
    """Allocate the Tranche Write-down Amount (P88, C6; spec 02 section 5).

    Order: Overcollateralization Amount, B-3H, B-2H, B-1H, M-2B/M-2BH, M-2A/M-2AH,
    M-1/M-1H, A-1/A-1H, then A-H for the excess of the remainder over the clause (d)
    (Modification Loss) portion of the Principal Loss Amount.  A remainder beyond every
    tranche is permitted by the PPM and is returned, not raised.
    """
    ledger = _Ledger(state, prior)
    remaining = write_down
    if remaining < ZERO:
        raise StepError(f"negative Tranche Write-down Amount {write_down}")

    # First: reduce the Overcollateralization Amount to zero (write_up_excess_use).
    from_overcollateralization = min(remaining, state.overcollateralization_amount)
    state.overcollateralization_amount -= from_overcollateralization
    remaining -= from_overcollateralization

    remaining -= ledger.reduce_one("B-3H", remaining)  # first
    remaining -= ledger.reduce_one("B-2H", remaining)  # second
    remaining -= ledger.reduce_one("B-1H", remaining)  # third
    remaining -= ledger.reduce_pair("M-2B", remaining)  # fourth
    remaining -= ledger.reduce_pair("M-2A", remaining)  # fifth
    remaining -= ledger.reduce_pair("M-1", remaining)  # sixth
    remaining -= ledger.reduce_pair("A-1", remaining)  # seventh
    to_a_h = max(ZERO, remaining - clause_d_principal_loss)  # eighth (ninth in spec numbering)
    remaining -= ledger.reduce_one("A-H", to_a_h)

    for tranche, amount in ledger.amounts.items():
        state.cumulative_write_downs[tranche] += amount
    return ledger.result(remaining)


def step1_tranche_write_up(
    state: TrancheState, prior: dict[str, Decimal], write_up: Decimal
) -> StepResult:
    """Allocate the Tranche Write-up Amount (P89, C7; spec 02 section 5), each increase
    capped at the tranche's cumulative unreimbursed write-downs.  The remainder is the
    Write-up Excess and increases the Overcollateralization Amount."""
    ledger = _Ledger(state, prior)
    remaining = write_up
    if remaining < ZERO:
        raise StepError(f"negative Tranche Write-up Amount {write_up}")
    remaining -= ledger.increase_one("A-H", remaining)  # first
    remaining -= ledger.increase_pair("A-1", remaining)  # second
    remaining -= ledger.increase_pair("M-1", remaining)  # third
    remaining -= ledger.increase_pair("M-2A", remaining)  # fourth
    remaining -= ledger.increase_pair("M-2B", remaining)  # fifth
    remaining -= ledger.increase_one("B-1H", remaining)  # sixth
    remaining -= ledger.increase_one("B-2H", remaining)  # seventh
    remaining -= ledger.increase_one("B-3H", remaining)  # eighth
    for tranche, amount in ledger.amounts.items():
        state.cumulative_write_ups[tranche] += amount
    state.overcollateralization_amount += remaining  # Write-up Excess
    return ledger.result(remaining)


def step2_senior_reduction(
    state: TrancheState,
    prior: dict[str, Decimal],
    senior_reduction: Decimal,
    *,
    class_a1_reduction: Decimal,
    class_a1_test_satisfied: bool,
) -> StepResult:
    """Allocate the Senior Reduction Amount (P90, T45; spec 02 section 6)."""
    ledger = _Ledger(state, prior)
    remaining = senior_reduction
    if remaining < ZERO:
        raise StepError(f"negative Senior Reduction Amount {senior_reduction}")
    if class_a1_test_satisfied:  # first: if and only if the Class A-1 CNL Test passes
        remaining -= ledger.reduce_pair("A-1", min(remaining, class_a1_reduction))
    remaining -= ledger.reduce_one("A-H", remaining)  # second
    remaining -= ledger.reduce_pair("A-1", remaining)  # third
    remaining -= ledger.reduce_pair("M-1", remaining)  # fourth
    remaining -= ledger.reduce_pair("M-2A", remaining)  # fifth
    remaining -= ledger.reduce_pair("M-2B", remaining)  # sixth
    remaining -= ledger.reduce_one("B-1H", remaining)  # seventh
    remaining -= ledger.reduce_one("B-2H", remaining)  # eighth
    remaining -= ledger.reduce_one("B-3H", remaining)  # ninth
    if remaining != ZERO:
        raise StepError(f"Senior Reduction Amount left {remaining} unallocated")
    return ledger.result(remaining)


def step3_subordinate_reduction(
    state: TrancheState, prior: dict[str, Decimal], subordinate_reduction: Decimal
) -> StepResult:
    """Allocate the Subordinate Reduction Amount (P91; spec 02 section 7)."""
    ledger = _Ledger(state, prior)
    remaining = subordinate_reduction
    if remaining < ZERO:
        raise StepError(f"negative Subordinate Reduction Amount {subordinate_reduction}")
    remaining -= ledger.reduce_pair("M-1", remaining)  # first
    remaining -= ledger.reduce_pair("M-2A", remaining)  # second
    remaining -= ledger.reduce_pair("M-2B", remaining)  # third
    remaining -= ledger.reduce_one("B-1H", remaining)  # fourth
    remaining -= ledger.reduce_one("B-2H", remaining)  # fifth
    remaining -= ledger.reduce_one("B-3H", remaining)  # sixth
    remaining -= ledger.reduce_pair("A-1", remaining)  # seventh
    remaining -= ledger.reduce_one("A-H", remaining)  # eighth
    if remaining != ZERO:
        raise StepError(f"Subordinate Reduction Amount left {remaining} unallocated")
    return ledger.result(remaining)


def step4_supplemental_reduction(
    state: TrancheState,
    prior: dict[str, Decimal],
    supplemental_reduction: Decimal,
    *,
    class_a1_additional_reduction: Decimal,
) -> StepResult:
    """Allocate the Supplemental Reduction Amount (P92; spec 02 section 8) and add the
    equal Supplemental Senior Increase Amount to A-H."""
    ledger = _Ledger(state, prior)
    remaining = supplemental_reduction
    if remaining < ZERO:
        raise StepError(f"negative Supplemental Reduction Amount {supplemental_reduction}")
    remaining -= ledger.reduce_pair("A-1", min(remaining, class_a1_additional_reduction))  # first
    remaining -= ledger.reduce_pair("M-1", remaining)  # second
    remaining -= ledger.reduce_pair("M-2A", remaining)  # third
    remaining -= ledger.reduce_pair("M-2B", remaining)  # fourth
    remaining -= ledger.reduce_pair("A-1", remaining)  # fifth
    if remaining != ZERO:
        raise StepError(f"Supplemental Reduction Amount left {remaining} unallocated")
    # Supplemental Senior Increase Amount (YAML: principal.supplemental_senior_increase_amount).
    state.increase("A-H", supplemental_reduction)
    return ledger.result(remaining)
