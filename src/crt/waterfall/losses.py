"""Losses, recoveries, write-down and write-up amounts (spec ``02-waterfall.md`` section 3.1).

The Principal Loss Amount and Principal Recovery Amount carry the PPM's full five-clause
structure (YAML: credit_events.principal_loss_amount, principal_recovery_amount) so that
the same code serves actual-pool runs.  In v1, Modeling Assumption (d) stipulates clause
(a) of the Principal Loss Amount as 25 % of the Credit Event Amount (P14, P78, T8) and
Modeling Assumptions (n), (o) make every other clause zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.money import ZERO, round2


@dataclass(frozen=True)
class PrincipalLossClauses:
    """Principal Loss Amount clauses (a)-(e), each already a cent amount."""

    credit_event_net_losses: Decimal  # (a)
    cramdowns: Decimal  # (b)
    subsequent_losses: Decimal  # (c)
    modification_loss_principal_priorities: Decimal  # (d)
    net_gains_on_reversed_credit_events: Decimal  # (e)

    def total(self) -> Decimal:
        return (
            self.credit_event_net_losses
            + self.cramdowns
            + self.subsequent_losses
            + self.modification_loss_principal_priorities
            + self.net_gains_on_reversed_credit_events
        )


@dataclass(frozen=True)
class PrincipalRecoveryClauses:
    """Principal Recovery Amount clauses (a)-(e), each already a cent amount."""

    net_losses_on_reversed_credit_events: Decimal  # (a)
    subsequent_recoveries: Decimal  # (b)
    credit_event_net_gains: Decimal  # (c)
    breach_settlement_amounts: Decimal  # (d)
    projected_recovery_amount: Decimal  # (e), Termination Date only

    def total(self) -> Decimal:
        return (
            self.net_losses_on_reversed_credit_events
            + self.subsequent_recoveries
            + self.credit_event_net_gains
            + self.breach_settlement_amounts
            + self.projected_recovery_amount
        )


def principal_loss_clauses_v1(
    credit_event_amount: Decimal, *, preliminary_loss_share: Decimal
) -> PrincipalLossClauses:
    """Modeling Assumption (d): clause (a) = round2(25 % x Credit Event Amount) (P14);
    clauses (b)-(e) are zero (Modeling Assumptions (k), (n); RM = 0)."""
    return PrincipalLossClauses(
        credit_event_net_losses=round2(preliminary_loss_share * credit_event_amount),  # R2
        cramdowns=ZERO,
        subsequent_losses=ZERO,
        modification_loss_principal_priorities=ZERO,
        net_gains_on_reversed_credit_events=ZERO,
    )


def principal_recovery_clauses_v1() -> PrincipalRecoveryClauses:
    """Modeling Assumptions (n), (o): no reversals, subsequent recoveries, net gains,
    settlements or Projected Recovery Amount (P75)."""
    return PrincipalRecoveryClauses(
        net_losses_on_reversed_credit_events=ZERO,
        subsequent_recoveries=ZERO,
        credit_event_net_gains=ZERO,
        breach_settlement_amounts=ZERO,
        projected_recovery_amount=ZERO,
    )


def tranche_write_down_amount(principal_loss: Decimal, principal_recovery: Decimal) -> Decimal:
    """``max(0, Principal Loss Amount - Principal Recovery Amount)``
    (YAML: credit_events.tranche_write_down_amount)."""
    return max(ZERO, principal_loss - principal_recovery)


def tranche_write_up_amount(principal_loss: Decimal, principal_recovery: Decimal) -> Decimal:
    """``max(0, Principal Recovery Amount - Principal Loss Amount)``
    (YAML: credit_events.tranche_write_up_amount)."""
    return max(ZERO, principal_recovery - principal_loss)


def recovery_principal(
    credit_event_amount: Decimal, write_down: Decimal, write_up: Decimal
) -> Decimal:
    """``(excess of Credit Event Amount over Tranche Write-down Amount) + Tranche Write-up
    Amount`` (YAML: principal.recovery_principal, P97).  The 75 % of v1 is a remainder,
    never a second rounding."""
    return max(ZERO, credit_event_amount - write_down) + write_up


def a_h_increase_on_write_down(write_down: Decimal, credit_event_amount: Decimal) -> Decimal:
    """``max(0, Tranche Write-down Amount - Credit Event Amount)`` added to A-H
    (YAML: credit_events.a_h_increase_on_write_down).  Zero in v1 (25 % < 100 %)."""
    return max(ZERO, write_down - credit_event_amount)
