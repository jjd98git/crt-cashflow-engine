"""Scenario definition for the v1 run (spec ``00-overview.md`` section 1).

Every field is required; nothing defaults.  The Distressed Principal Balance vector is
only consulted when the Delinquency Test flag is false (spec 02 section 3.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from crt.money import ONE, ZERO


class ScenarioError(ValueError):
    """A scenario field is missing, malformed or outside its allowed range."""


@dataclass(frozen=True)
class Scenario:
    """One point of the scenario grid.

    ``cpr``, ``cer`` and ``rm`` are annual rates as fractions (10 % CPR -> ``0.10``).
    ``sofr_rate`` is the flat SOFR Rate as a fraction (P12).  ``early_redemption`` is the
    T18 switch; ``delinquency_test_satisfied`` is Modeling Assumption (e) (T10 / P73).
    """

    cpr: Decimal
    cer: Decimal
    rm: Decimal
    early_redemption: bool
    delinquency_test_satisfied: bool
    sofr_rate: Decimal
    distressed_principal_balance_by_payment_date: tuple[Decimal, ...] | None = None

    def __post_init__(self) -> None:
        for name in ("cpr", "cer", "rm", "sofr_rate"):
            value = getattr(self, name)
            if not isinstance(value, Decimal):
                raise ScenarioError(f"scenario field {name!r} must be a Decimal, got {value!r}")
        if self.cpr < ZERO or self.cpr >= ONE:
            raise ScenarioError(f"CPR {self.cpr} must satisfy 0 <= CPR < 1")
        if self.cer < ZERO or self.cer >= ONE:
            raise ScenarioError(f"CER {self.cer} must satisfy 0 <= CER < 1")
        if self.rm != ZERO:
            # Spec 00 section 5: RM > 0 requires the Modification Loss machinery, out of v1.
            raise ScenarioError(f"RM {self.rm} is not supported in v1; only RM = 0")
        if not isinstance(self.early_redemption, bool):
            raise ScenarioError("early_redemption must be a bool")
        if not isinstance(self.delinquency_test_satisfied, bool):
            raise ScenarioError("delinquency_test_satisfied must be a bool")
        if self.distressed_principal_balance_by_payment_date is not None:
            for index, amount in enumerate(self.distressed_principal_balance_by_payment_date, 1):
                if not isinstance(amount, Decimal) or amount < ZERO:
                    raise ScenarioError(
                        f"Distressed Principal Balance for Payment Date {index} must be a "
                        f"non-negative Decimal, got {amount!r}"
                    )

    def label(self) -> str:
        basis = "early redemption on" if self.early_redemption else "to scheduled maturity"
        return f"CPR {self.cpr:.2%}, CER {self.cer:.2%}, RM {self.rm:.2%}, {basis}"
