"""Allocation primitives (spec ``02-waterfall.md`` section 4; register A8).

``allocate_pair`` splits an amount pro rata between a Note tranche and its H tranche using
the exact Decimal ratio of their Class Notional Amounts *immediately prior to the Payment
Date*; the Note leg is rounded to the cent and the H leg is the remainder (R4 / A8).
``allocate_one`` reduces a single tranche.  Both stop at zero ("until its Class Notional
Amount is reduced to zero").
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.money import ZERO, round2
from crt.waterfall.tranches import PAIRED_H_TRANCHE, TrancheState


class AllocationError(ValueError):
    """An allocation could not be carried out as the spec requires."""


@dataclass(frozen=True)
class PairAllocation:
    note_amount: Decimal
    h_amount: Decimal

    @property
    def used(self) -> Decimal:
        return self.note_amount + self.h_amount


def split_pair(
    amount: Decimal,
    *,
    note_prior: Decimal,
    h_prior: Decimal,
    note_current: Decimal,
    h_current: Decimal,
) -> PairAllocation:
    """Split ``amount`` between a Note tranche and its H tranche (A8).

    The ratio uses the balances immediately prior to the Payment Date; the caps use the
    current balances (an earlier priority on the same Payment Date may already have
    reduced them).  With one member at zero the whole amount goes to the other.
    """
    current_total = note_current + h_current
    if amount <= ZERO or current_total <= ZERO:
        return PairAllocation(ZERO, ZERO)
    used = min(amount, current_total)
    prior_total = note_prior + h_prior
    if prior_total <= ZERO:
        # Q18: the PPM's "pro rata based on their Class Notional Amounts immediately
        # prior to such Payment Date" has no ratio when both were zero.  Unreachable in
        # v1 (balances never rise from zero); raise rather than guess.
        raise AllocationError(
            "pair split requested with both prior Class Notional Amounts at zero (Q18)"
        )
    to_note = round2(used * note_prior / prior_total)
    to_note = min(to_note, note_current)
    to_h = used - to_note
    if to_h > h_current:
        to_h = h_current
        to_note = used - to_h
    if to_note < ZERO or to_h < ZERO or to_note > note_current or to_h > h_current:
        raise AllocationError("pair split produced an out-of-range leg")
    return PairAllocation(note_amount=to_note, h_amount=to_h)


def allocate_pair(
    state: TrancheState, prior: dict[str, Decimal], note: str, amount: Decimal
) -> PairAllocation:
    """Reduce Note tranche ``note`` and its H tranche pro rata by up to ``amount``."""
    h_tranche = PAIRED_H_TRANCHE[note]
    allocation = split_pair(
        amount,
        note_prior=prior[note],
        h_prior=prior[h_tranche],
        note_current=state.balances[note],
        h_current=state.balances[h_tranche],
    )
    if allocation.note_amount > ZERO:
        state.reduce(note, allocation.note_amount)
    if allocation.h_amount > ZERO:
        state.reduce(h_tranche, allocation.h_amount)
    return allocation


def allocate_one(state: TrancheState, tranche: str, amount: Decimal) -> Decimal:
    """Reduce a single tranche by up to ``amount``; return the amount used."""
    if amount <= ZERO:
        return ZERO
    used = min(amount, state.balances[tranche])
    if used > ZERO:
        state.reduce(tranche, used)
    return used


def increase_pair_capped(
    state: TrancheState, prior: dict[str, Decimal], note: str, amount: Decimal
) -> PairAllocation:
    """Tranche Write-up Amount to a Note/H pair: ``allocate_pair`` with the sign reversed
    and each member capped at its cumulative unreimbursed write-downs (spec 02 section 5).
    """
    h_tranche = PAIRED_H_TRANCHE[note]
    note_cap = state.unreimbursed_write_downs(note)
    h_cap = state.unreimbursed_write_downs(h_tranche)
    allocation = split_pair(
        amount,
        note_prior=prior[note],
        h_prior=prior[h_tranche],
        note_current=note_cap,
        h_current=h_cap,
    )
    if allocation.note_amount > ZERO:
        state.increase(note, allocation.note_amount)
    if allocation.h_amount > ZERO:
        state.increase(h_tranche, allocation.h_amount)
    return allocation


def increase_one_capped(state: TrancheState, tranche: str, amount: Decimal) -> Decimal:
    """Tranche Write-up Amount to a single tranche, capped at its unreimbursed write-downs."""
    if amount <= ZERO:
        return ZERO
    used = min(amount, state.unreimbursed_write_downs(tranche))
    if used > ZERO:
        state.increase(tranche, used)
    return used
