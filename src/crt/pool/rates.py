"""Annual-to-monthly rate conversions (spec ``01-pool.md`` section 2; register A1, A2, A14).

Both rates are computed once per scenario in ``Decimal`` at context precision and are
never rounded (R5).
"""

from __future__ import annotations

from decimal import Decimal

from crt.money import ONE, TWELVE, ZERO

# A1 / A2: the exponent 1/12 of the Bond Market Association conversion.
_ONE_TWELFTH = ONE / TWELVE


class RateError(ValueError):
    """An annual rate is outside [0, 1)."""


def _require_annual_rate(rate: Decimal, *, name: str) -> None:
    if rate < ZERO or rate >= ONE:
        raise RateError(f"{name} = {rate} must satisfy 0 <= {name} < 1")


def smm_from_cpr(cpr: Decimal) -> Decimal:
    """SMM = 1 - (1 - CPR)^(1/12)  (A1).  CPR = 0 gives exactly 0."""
    _require_annual_rate(cpr, name="CPR")
    if cpr == ZERO:
        return ZERO
    return ONE - (ONE - cpr) ** _ONE_TWELFTH


def mdr_from_cer(cer: Decimal) -> Decimal:
    """Monthly credit-event rate = 1 - (1 - CER)^(1/12)  (A2).  CER = 0 gives exactly 0."""
    _require_annual_rate(cer, name="CER")
    if cer == ZERO:
        return ZERO
    return ONE - (ONE - cer) ** _ONE_TWELFTH
