"""The Reference Tranche stack and its state (spec ``02-waterfall.md`` section 1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER
from crt.money import ZERO

# Senior tranches for the Senior Percentage (YAML: principal.senior_percentage, P95).
SENIOR_TRANCHES: tuple[str, ...] = ("A-H", "A-1", "A-1H")
# Offered Reference Tranches for the Offered Reference Tranche Percentage (P103).
OFFERED_TRANCHES: tuple[str, ...] = ("A-1", "A-1H", "M-1", "M-1H", "M-2A", "M-2AH", "M-2B", "M-2BH")
# Note tranche -> paired H tranche (YAML: reference_tranches.structure_note).
PAIRED_H_TRANCHE: dict[str, str] = {note: note + "H" for note in NOTE_CLASSES}


class TrancheError(ValueError):
    """A tranche name is unknown or a balance went negative."""


def require_tranche(name: str) -> None:
    if name not in TRANCHE_ORDER:
        raise TrancheError(f"unknown Reference Tranche {name!r}")


@dataclass
class TrancheState:
    """Class Notional Amounts and the cumulative amounts the PPM's caps depend on.

    ``balances`` are the current Class Notional Amounts.  ``cumulative_write_downs`` and
    ``cumulative_write_ups`` per tranche feed the write-up cap (spec 02 section 5).
    ``overcollateralization_amount`` is the PPM's Overcollateralization Amount
    (YAML: credit_events.overcollateralization_amount), zero throughout v1.
    """

    balances: dict[str, Decimal]
    cumulative_write_downs: dict[str, Decimal] = field(default_factory=dict)
    cumulative_write_ups: dict[str, Decimal] = field(default_factory=dict)
    overcollateralization_amount: Decimal = ZERO

    @classmethod
    def initial(cls, initial_class_notional_amounts: dict[str, Decimal]) -> TrancheState:
        for name in TRANCHE_ORDER:
            if name not in initial_class_notional_amounts:
                raise TrancheError(f"initial Class Notional Amount missing for {name}")
        return cls(
            balances={name: initial_class_notional_amounts[name] for name in TRANCHE_ORDER},
            cumulative_write_downs={name: ZERO for name in TRANCHE_ORDER},
            cumulative_write_ups={name: ZERO for name in TRANCHE_ORDER},
            overcollateralization_amount=ZERO,
        )

    def snapshot(self) -> dict[str, Decimal]:
        """Balances 'immediately prior to the Payment Date' (a copy)."""
        return dict(self.balances)

    def total(self) -> Decimal:
        return sum(self.balances.values(), ZERO)

    def reduce(self, name: str, amount: Decimal) -> None:
        require_tranche(name)
        if amount < ZERO:
            raise TrancheError(f"negative reduction {amount} for {name}")
        if amount > self.balances[name]:
            raise TrancheError(
                f"reduction {amount} exceeds Class Notional Amount {self.balances[name]} of {name}"
            )
        self.balances[name] -= amount

    def increase(self, name: str, amount: Decimal) -> None:
        require_tranche(name)
        if amount < ZERO:
            raise TrancheError(f"negative increase {amount} for {name}")
        self.balances[name] += amount

    def unreimbursed_write_downs(self, name: str) -> Decimal:
        """Cap for a write-up to ``name``: cumulative write-downs not yet written up."""
        return self.cumulative_write_downs[name] - self.cumulative_write_ups[name]
