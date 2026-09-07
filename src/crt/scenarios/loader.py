"""Scenario files (BRIEF section 9 "Scenario inputs"): YAML in, ``Scenario`` out.

File format (every key required unless marked optional; unknown keys are rejected)::

    name: pricing-speed                 # short label used in file names and the manifest
    description: free text              # optional
    cpr_pct: 10                         # vector, see below
    cer_pct: 0                          # vector
    sofr_pct: 3.65786                   # vector; the flat SOFR Rate of P12 is 3.65786
    early_redemption: true              # T18 basis switch
    delinquency_test_satisfied: true    # Modeling Assumption (e), T10 / P73
    rm_pct: 0                           # optional; v1 accepts 0 only (spec 00 section 5)
    distressed_principal_balance_usd_by_payment_date: ["0.00", ...]
                                        # required iff delinquency_test_satisfied is false

A *vector* key takes one of three shapes.  All three are validated on load; only ``flat``
is honoured by the v1 engine.  A ramp or step schedule is rejected by ``to_scenario`` with
a message naming the field -- it is never flattened silently::

    cpr_pct: 10                                        # flat, shorthand
    cpr_pct: {kind: flat, value_pct: 10}               # flat, long form
    cpr_pct: {kind: ramp, start_pct: 6, end_pct: 18, over_months: 12}
        # linear from start_pct in collection month 1 to end_pct in month over_months,
        # then flat at end_pct
    cpr_pct: {kind: steps, steps: [{from_month: 1, value_pct: 5},
                                   {from_month: 13, value_pct: 10}]}
        # piecewise constant; the first step must start at month 1 and months must be
        # strictly increasing

Percentages are written as percentages (``10`` means 10 %) and converted to fractions
exactly (a power-of-ten shift).  YAML floats are read as ``Decimal`` from their text.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml

from crt.io.yaml_decimal import DecimalSafeLoader, YamlDecimalError
from crt.money import ZERO, percent_to_fraction
from crt.scenarios.scenario import Scenario, ScenarioError

REQUIRED_KEYS: tuple[str, ...] = (
    "name",
    "cpr_pct",
    "cer_pct",
    "sofr_pct",
    "early_redemption",
    "delinquency_test_satisfied",
)
OPTIONAL_KEYS: tuple[str, ...] = (
    "description",
    "rm_pct",
    "distressed_principal_balance_usd_by_payment_date",
)
VECTOR_KEYS: tuple[str, ...] = ("cpr_pct", "cer_pct", "sofr_pct")
VECTOR_KINDS: tuple[str, ...] = ("flat", "ramp", "steps")
# Spec 00 section 1 / Scenario class: annual rates are fractions in [0, 1).
PERCENT_UPPER_BOUND_EXCLUSIVE = Decimal(100)


class ScenarioFileError(ScenarioError):
    """A scenario file is missing, malformed, or holds a value outside its range."""


class ScenarioVectorUnsupportedError(ScenarioFileError):
    """The file is valid but asks for a vector shape the v1 engine cannot honour."""


@dataclass(frozen=True)
class FlatVector:
    value_pct: Decimal

    @property
    def kind(self) -> str:
        return "flat"


@dataclass(frozen=True)
class RampVector:
    start_pct: Decimal
    end_pct: Decimal
    over_months: int

    @property
    def kind(self) -> str:
        return "ramp"


@dataclass(frozen=True)
class Step:
    from_month: int
    value_pct: Decimal


@dataclass(frozen=True)
class StepVector:
    steps: tuple[Step, ...]

    @property
    def kind(self) -> str:
        return "steps"


Vector = FlatVector | RampVector | StepVector


@dataclass(frozen=True)
class ScenarioFile:
    """The validated contents of one scenario YAML file, before engine capability checks."""

    path: Path
    name: str
    description: str | None
    cpr_pct: Vector
    cer_pct: Vector
    sofr_pct: Vector
    early_redemption: bool
    delinquency_test_satisfied: bool
    rm_pct: Decimal
    distressed_principal_balance_by_payment_date: tuple[Decimal, ...] | None

    def vector(self, key: str) -> Vector:
        if key not in VECTOR_KEYS:
            raise ScenarioFileError(f"{key!r} is not a vector field; expected one of {VECTOR_KEYS}")
        vector: Vector = getattr(self, key)
        return vector

    def to_scenario(self) -> Scenario:
        """Build the engine ``Scenario``; reject any vector the engine cannot honour."""
        values: dict[str, Decimal] = {}
        for key in VECTOR_KEYS:
            vector = self.vector(key)
            if not isinstance(vector, FlatVector):
                raise ScenarioVectorUnsupportedError(
                    f"{self.path}: field {key!r} is a {vector.kind!r} vector; the v1 engine "
                    "takes a flat value only (vector support is not implemented yet, so the "
                    "schedule is rejected rather than flattened)"
                )
            values[key] = vector.value_pct
        return Scenario(
            cpr=percent_to_fraction(values["cpr_pct"]),
            cer=percent_to_fraction(values["cer_pct"]),
            rm=percent_to_fraction(self.rm_pct),
            early_redemption=self.early_redemption,
            delinquency_test_satisfied=self.delinquency_test_satisfied,
            sofr_rate=percent_to_fraction(values["sofr_pct"]),
            distressed_principal_balance_by_payment_date=(
                self.distressed_principal_balance_by_payment_date
            ),
        )


def _percent(value: Any, *, field: str, path: Path) -> Decimal:
    """A percentage scalar: YAML int or Decimal (never bool, float or string)."""
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ScenarioFileError(
            f"{path}: field {field!r} must be a number written as a percentage "
            f"(e.g. 10 for 10 %), got {value!r}"
        )
    return Decimal(value)


def _positive_int(value: Any, *, field: str, path: Path) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ScenarioFileError(
            f"{path}: field {field!r} must be a positive integer, got {value!r}"
        )
    return value


def _bool(value: Any, *, field: str, path: Path) -> bool:
    if not isinstance(value, bool):
        raise ScenarioFileError(f"{path}: field {field!r} must be true or false, got {value!r}")
    return value


def _require_keys(mapping: dict[str, Any], expected: set[str], *, field: str, path: Path) -> None:
    present = set(mapping)
    missing = sorted(expected - present)
    unknown = sorted(present - expected)
    if missing:
        raise ScenarioFileError(f"{path}: field {field!r} is missing key(s) {missing}")
    if unknown:
        raise ScenarioFileError(f"{path}: field {field!r} has unknown key(s) {unknown}")


def _steps(raw_steps: Any, *, field: str, path: Path) -> StepVector:
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ScenarioFileError(f"{path}: field {field!r}.steps must be a non-empty list")
    steps: list[Step] = []
    for index, raw in enumerate(raw_steps, 1):
        label = f"{field}.steps[{index}]"
        if not isinstance(raw, dict):
            raise ScenarioFileError(f"{path}: {label} must be a mapping")
        _require_keys(raw, {"from_month", "value_pct"}, field=label, path=path)
        steps.append(
            Step(
                from_month=_positive_int(raw["from_month"], field=f"{label}.from_month", path=path),
                value_pct=_percent(raw["value_pct"], field=f"{label}.value_pct", path=path),
            )
        )
    if steps[0].from_month != 1:
        raise ScenarioFileError(f"{path}: field {field!r}.steps must start at from_month 1")
    for earlier, later in pairwise(steps):
        if later.from_month <= earlier.from_month:
            raise ScenarioFileError(
                f"{path}: field {field!r}.steps months must be strictly increasing "
                f"({earlier.from_month} then {later.from_month})"
            )
    return StepVector(steps=tuple(steps))


def _vector(value: Any, *, field: str, path: Path) -> Vector:
    if not isinstance(value, dict):
        return FlatVector(value_pct=_percent(value, field=field, path=path))
    kind = value.get("kind")
    if kind not in VECTOR_KINDS:
        raise ScenarioFileError(
            f"{path}: field {field!r} vector 'kind' must be one of {VECTOR_KINDS}, got {kind!r}"
        )
    if kind == "flat":
        _require_keys(value, {"kind", "value_pct"}, field=field, path=path)
        return FlatVector(
            value_pct=_percent(value["value_pct"], field=f"{field}.value_pct", path=path)
        )
    if kind == "ramp":
        _require_keys(
            value, {"kind", "start_pct", "end_pct", "over_months"}, field=field, path=path
        )
        return RampVector(
            start_pct=_percent(value["start_pct"], field=f"{field}.start_pct", path=path),
            end_pct=_percent(value["end_pct"], field=f"{field}.end_pct", path=path),
            over_months=_positive_int(
                value["over_months"], field=f"{field}.over_months", path=path
            ),
        )
    _require_keys(value, {"kind", "steps"}, field=field, path=path)
    return _steps(value["steps"], field=field, path=path)


def _distressed_balances(value: Any, *, path: Path) -> tuple[Decimal, ...]:
    field = "distressed_principal_balance_usd_by_payment_date"
    if not isinstance(value, list) or not value:
        raise ScenarioFileError(
            f"{path}: field {field!r} must be a non-empty list of dollar strings"
        )
    amounts: list[Decimal] = []
    for index, item in enumerate(value, 1):
        if not isinstance(item, str):
            raise ScenarioFileError(
                f"{path}: field {field!r} entry {index} must be a quoted dollar string, "
                f"got {item!r}"
            )
        try:
            amount = Decimal(item)
        except InvalidOperation:
            raise ScenarioFileError(
                f"{path}: field {field!r} entry {index} = {item!r} is not a Decimal"
            ) from None
        if amount < ZERO:
            raise ScenarioFileError(f"{path}: field {field!r} entry {index} is negative")
        amounts.append(amount)
    return tuple(amounts)


def _points(vector: Vector) -> tuple[Decimal, ...]:
    if isinstance(vector, FlatVector):
        return (vector.value_pct,)
    if isinstance(vector, RampVector):
        return (vector.start_pct, vector.end_pct)
    return tuple(step.value_pct for step in vector.steps)


def _check_ranges(scenario_file: ScenarioFile) -> None:
    """The range checks the ``Scenario`` class applies to flat values, applied to every
    point of every vector so that a ramp or step file is validated even before the engine
    can run it."""
    path = scenario_file.path
    for key in ("cpr_pct", "cer_pct"):
        for point in _points(scenario_file.vector(key)):
            if point < ZERO or point >= PERCENT_UPPER_BOUND_EXCLUSIVE:
                raise ScenarioFileError(
                    f"{path}: field {key!r} value {point} % must satisfy 0 <= value < 100"
                )
    if scenario_file.rm_pct != ZERO:
        raise ScenarioFileError(
            f"{path}: field 'rm_pct' = {scenario_file.rm_pct} is not supported in v1; only 0 "
            "(spec 00 section 5)"
        )


def load_scenario_file(path: Path) -> ScenarioFile:
    """Read and validate a scenario YAML file.  Raises ``ScenarioFileError`` naming the
    file and the field for anything missing, unknown, mistyped or out of range."""
    if not path.is_file():
        raise ScenarioFileError(f"{path}: scenario file not found")
    try:
        with path.open(encoding="utf-8") as handle:
            raw = yaml.load(handle, Loader=DecimalSafeLoader)
    except (yaml.YAMLError, YamlDecimalError) as error:
        raise ScenarioFileError(f"{path}: not valid YAML ({error})") from None
    if not isinstance(raw, dict):
        raise ScenarioFileError(f"{path}: top level must be a mapping of scenario fields")

    present = set(raw)
    missing = sorted(set(REQUIRED_KEYS) - present)
    unknown = sorted(present - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS))
    if missing:
        raise ScenarioFileError(f"{path}: missing required field(s) {missing}")
    if unknown:
        raise ScenarioFileError(
            f"{path}: unknown field(s) {unknown}; allowed: "
            f"{sorted(REQUIRED_KEYS + OPTIONAL_KEYS)}"
        )

    name = raw["name"]
    if not isinstance(name, str) or not name.strip():
        raise ScenarioFileError(f"{path}: field 'name' must be a non-empty string")
    description = raw.get("description")
    if description is not None and not isinstance(description, str):
        raise ScenarioFileError(f"{path}: field 'description' must be a string")

    delinquency_test_satisfied = _bool(
        raw["delinquency_test_satisfied"], field="delinquency_test_satisfied", path=path
    )
    distressed = raw.get("distressed_principal_balance_usd_by_payment_date")
    if not delinquency_test_satisfied and distressed is None:
        raise ScenarioFileError(
            f"{path}: 'delinquency_test_satisfied' is false, so "
            "'distressed_principal_balance_usd_by_payment_date' is required (spec 02 "
            "section 3.3); it is never defaulted to zero"
        )
    # T26 / T16: v1 runs the RM = 0 rows only.  The key may be omitted because zero is the
    # only value the engine accepts, not because zero is a default.
    rm_pct = _percent(raw["rm_pct"], field="rm_pct", path=path) if "rm_pct" in raw else ZERO

    scenario_file = ScenarioFile(
        path=path,
        name=name.strip(),
        description=description,
        cpr_pct=_vector(raw["cpr_pct"], field="cpr_pct", path=path),
        cer_pct=_vector(raw["cer_pct"], field="cer_pct", path=path),
        sofr_pct=_vector(raw["sofr_pct"], field="sofr_pct", path=path),
        early_redemption=_bool(raw["early_redemption"], field="early_redemption", path=path),
        delinquency_test_satisfied=delinquency_test_satisfied,
        rm_pct=rm_pct,
        distressed_principal_balance_by_payment_date=(
            None if distressed is None else _distressed_balances(distressed, path=path)
        ),
    )
    _check_ranges(scenario_file)
    return scenario_file


def load_scenario(path: Path) -> Scenario:
    """Load a scenario file and return the engine ``Scenario`` (flat vectors only)."""
    return load_scenario_file(path).to_scenario()


def scenario_from_values(
    *,
    cpr_pct: Decimal,
    cer_pct: Decimal,
    sofr_pct: Decimal,
    early_redemption: bool,
    delinquency_test_satisfied: bool,
) -> Scenario:
    """Build a flat ``Scenario`` from percentage inputs (the GUI editor path).  Validation
    is the ``Scenario`` class's own; errors propagate unchanged."""
    return Scenario(
        cpr=percent_to_fraction(cpr_pct),
        cer=percent_to_fraction(cer_pct),
        rm=ZERO,  # T26 / T16: RM = 0 rows only in v1
        early_redemption=early_redemption,
        delinquency_test_satisfied=delinquency_test_satisfied,
        sofr_rate=percent_to_fraction(sofr_pct),
    )


def scenario_as_dict(scenario: Scenario) -> dict[str, Any]:
    """JSON-ready view of a ``Scenario`` for the run manifest.  Rates are written as
    exact percentage strings; nothing is converted to float."""
    distressed = scenario.distressed_principal_balance_by_payment_date
    return {
        "cpr_pct": str(scenario.cpr.scaleb(2)),
        "cer_pct": str(scenario.cer.scaleb(2)),
        "rm_pct": str(scenario.rm.scaleb(2)),
        "sofr_pct": str(scenario.sofr_rate.scaleb(2)),
        "early_redemption": scenario.early_redemption,
        "delinquency_test_satisfied": scenario.delinquency_test_satisfied,
        "distressed_principal_balance_usd_by_payment_date": (
            None if distressed is None else [str(amount) for amount in distressed]
        ),
        "label": scenario.label(),
    }
