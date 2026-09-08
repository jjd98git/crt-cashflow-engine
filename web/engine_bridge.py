"""Python side of the browser page (``web/``): the glue between the Web Worker and
``crt.api``.

Runs unchanged under CPython and under Pyodide.  It adds no cashflow arithmetic: every
value it returns is read off a ``RunResult`` (or the tie-out result objects) and turned
into a string -- ``format(Decimal, "f")`` for exact digits, ``format(Decimal, ",.2f")``
for the summary money cells (engine cents, so nothing is rounded), ``round_half_up`` for
the two-decimal WAL display exactly as the Streamlit GUI does.  The JavaScript never
receives a float from here, and nothing it sends back is fed into a calculation except
the scenario inputs themselves, which go through ``scenario_from_values`` and the
``Scenario`` class's own validation.

Module state: one ``Session`` (inputs + pool cache, like the GUI's cached resources) and
the last few ``RunResult`` objects keyed by run id, so that the download buttons can ask
for the CSV bundle or the workbook of a run that is already on screen.
"""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from crt.api import TABLE_NAMES, RunResult, run_scenario
from crt.gui.tieout_status import TIEOUT_REPORT_PATH, parse_tieout_status
from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER, DealTerms
from crt.money import round_half_up
from crt.scenarios.grid import PPM_CER_AXIS_PCT, PPM_CPR_AXIS_PCT
from crt.scenarios.loader import FlatVector, load_scenario_file, scenario_from_values
from crt.scenarios.scenario import Scenario
from crt.tieout.manifest import engine_version
from crt.tieout.run import PoolCache, TieoutInputs, compare_all, load_inputs, run_grid

BUILD_INFO_FILE = "build_info.json"  # written by scripts/build_web.py
SCENARIOS_DIR = "scenarios"
MAX_KEPT_RESULTS = 8
WAL_DISPLAY_PLACES = 2  # R6: WAL reported to 2 decimals; the stored value is unrounded
PERCENT_DISPLAY_PLACES = 5  # R3: percentages are carried to 1/100,000 of a point


class BridgeError(RuntimeError):
    """The bridge was asked for something it does not have (no session, unknown run)."""


@dataclass
class Session:
    root: Path
    inputs: TieoutInputs
    pool_cache: PoolCache
    results: dict[str, RunResult]


_SESSION: Session | None = None


def _session() -> Session:
    if _SESSION is None:
        raise BridgeError("init_session() has not been called")
    return _SESSION


# --------------------------------------------------------------------------------------
# Display formatting (strings only)
# --------------------------------------------------------------------------------------


def money(value: Decimal | None) -> str:
    return "n/a" if value is None else format(value, ",.2f")


def exact(value: Decimal) -> str:
    return format(value, "f")


def wal(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return format(round_half_up(value, WAL_DISPLAY_PLACES), ".2f")


def percent_of_fraction(value: Decimal) -> str:
    return f"{format(value.scaleb(2), f',.{PERCENT_DISPLAY_PLACES}f')} %"


def _cell(value: Any) -> str:
    """The CSV cell convention of ``crt.api.export_csv``: exact digits, ISO dates."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Decimal):
        return exact(value)
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _window_cell(number: int | None, when: date | None) -> str:
    if number is None or when is None:
        return "never"
    return f"{number} ({when.isoformat()})"


# --------------------------------------------------------------------------------------
# Session
# --------------------------------------------------------------------------------------


def init_session(root: str) -> str:
    """Load the inputs once and describe the deal, the presets and the tie-out status."""
    global _SESSION
    root_path = Path(root)
    inputs = load_inputs(root_path)
    _SESSION = Session(root=root_path, inputs=inputs, pool_cache=PoolCache(inputs), results={})
    return json.dumps(
        {
            "engine_version": engine_version(root_path),
            "build": _build_info(root_path),
            "deal": _deal_info(inputs.deal),
            "ppm_grid": {
                "cpr_pct": [exact(x) for x in PPM_CPR_AXIS_PCT],
                "cer_pct": [exact(x) for x in PPM_CER_AXIS_PCT],
            },
            "presets": _presets(root_path),
            "tieout_status": _tieout_status(root_path),
            "tranche_order": list(TRANCHE_ORDER),
            "note_classes": list(NOTE_CLASSES),
            "table_names": list(TABLE_NAMES),
        }
    )


def _build_info(root: Path) -> dict[str, Any] | None:
    path = root / BUILD_INFO_FILE
    if not path.is_file():
        return None
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else None


def _deal_info(deal: DealTerms) -> dict[str, Any]:
    return {
        "name": deal.name,
        "closing_date": deal.closing_date.isoformat(),
        "cut_off_date": deal.cut_off_date.isoformat(),
        "cut_off_date_balance": money(deal.cut_off_date_balance),
        "first_payment_date": deal.first_payment_date.isoformat(),
        "scheduled_maturity_payment_date_number": deal.scheduled_maturity_payment_date_number,
        "earliest_early_redemption_payment_date_number": (
            deal.earliest_early_redemption_payment_date_number
        ),
        "sofr_rate_flat_pct": exact(deal.sofr_rate_flat.scaleb(2)),
        "tranches": [
            {
                "tranche": tranche,
                "initial_class_notional_amount": money(
                    deal.initial_class_notional_amounts[tranche]
                ),
                "note_issued": tranche in NOTE_CLASSES,
            }
            for tranche in TRANCHE_ORDER
        ],
        "notes": [
            {
                "note": note,
                "original_class_principal_balance": money(
                    deal.notes[note].original_class_principal_balance
                ),
                "margin_pct": exact(deal.notes[note].margin.scaleb(2)),
                "initial_class_coupon_pct": exact(
                    deal.notes[note].initial_class_coupon.scaleb(2)
                ),
                "expected_wal_years_table1": exact(deal.notes[note].expected_wal_years_table1),
                "expected_principal_window_table1": "{}-{}".format(
                    *deal.notes[note].expected_principal_window_table1
                ),
            }
            for note in NOTE_CLASSES
        ],
    }


def _presets(root: Path) -> list[dict[str, Any]]:
    """The scenario files, flat values as strings; a vector file is listed with the
    loader's message and no values (the page disables it)."""
    directory = root / SCENARIOS_DIR
    presets: list[dict[str, Any]] = []
    paths = sorted(directory.glob("*.yaml")) if directory.is_dir() else []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            scenario_file = load_scenario_file(path)
            values: dict[str, str] = {}
            for key in ("cpr_pct", "cer_pct", "sofr_pct"):
                vector = scenario_file.vector(key)
                if not isinstance(vector, FlatVector):
                    raise TypeError(
                        f"{relative}: field {key!r} is a {vector.kind!r} vector; the page "
                        "shows flat values only"
                    )
                values[key] = exact(vector.value_pct)
            presets.append(
                {
                    "path": relative,
                    "name": scenario_file.name,
                    "description": scenario_file.description,
                    "early_redemption": scenario_file.early_redemption,
                    "delinquency_test_satisfied": scenario_file.delinquency_test_satisfied,
                    "error": None,
                    **values,
                }
            )
        except (ValueError, RuntimeError) as error:
            presets.append(
                {"path": relative, "name": path.stem, "error": f"{type(error).__name__}: {error}"}
            )
    return presets


def _tieout_status(root: Path) -> dict[str, Any] | None:
    path = root / TIEOUT_REPORT_PATH
    if not path.is_file():
        return None
    status = parse_tieout_status(path.read_text(encoding="utf-8"))
    if status is None:
        return None
    return {
        "timestamp_utc": status.timestamp_utc,
        "overall": status.overall,
        "secondary_check": status.secondary_check,
        "rows": [vars(row) for row in status.rows],
    }


# --------------------------------------------------------------------------------------
# Running one scenario
# --------------------------------------------------------------------------------------


def _percent(form: dict[str, Any], key: str) -> Decimal:
    raw = form.get(key)
    text = str(raw).strip() if raw is not None else ""
    try:
        return Decimal(text)
    except InvalidOperation:
        raise ValueError(
            f"{key}: {text!r} is not a number (write percentages such as 7.5)"
        ) from None


def _flag(form: dict[str, Any], key: str) -> bool:
    value = form.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be true or false, got {value!r}")
    return value


def _cites_file(form: dict[str, Any], scenario: Scenario, root: Path) -> Path | None:
    """The preset file, if the run's values still equal the file's (the GUI's rule), so
    the manifest may cite it; otherwise None."""
    source = form.get("source")
    if not isinstance(source, str) or not source:
        return None
    path = root / source
    try:
        scenario_file = load_scenario_file(path)
    except (ValueError, RuntimeError):
        return None
    vectors = {key: scenario_file.vector(key) for key in ("cpr_pct", "cer_pct", "sofr_pct")}
    flat = {key: v.value_pct for key, v in vectors.items() if isinstance(v, FlatVector)}
    if len(flat) != len(vectors):
        return None
    unchanged = (
        flat["cpr_pct"].scaleb(-2) == scenario.cpr
        and flat["cer_pct"].scaleb(-2) == scenario.cer
        and flat["sofr_pct"].scaleb(-2) == scenario.sofr_rate
        and scenario_file.early_redemption == scenario.early_redemption
        and scenario_file.delinquency_test_satisfied == scenario.delinquency_test_satisfied
    )
    return path if unchanged else None


def run_form(form_json: str) -> str:
    """Run the scenario described by the form; on any refusal return the error verbatim."""
    started = time.perf_counter()
    session = _session()
    try:
        form = json.loads(form_json)
        if not isinstance(form, dict):
            raise TypeError("the form must be a JSON object")
        scenario = scenario_from_values(
            cpr_pct=_percent(form, "cpr_pct"),
            cer_pct=_percent(form, "cer_pct"),
            sofr_pct=_percent(form, "sofr_pct"),
            early_redemption=_flag(form, "early_redemption"),
            delinquency_test_satisfied=_flag(form, "delinquency_test_satisfied"),
        )
        name = str(form.get("name") or "").strip() or "ad-hoc"
        result = run_scenario(
            scenario,
            project_root=session.root,
            inputs=session.inputs,
            pool_cache=session.pool_cache,
            scenario_name=name,
            scenario_source=_cites_file(form, scenario, session.root),
        )
    except Exception as error:  # noqa: BLE001 - relayed verbatim, never swallowed
        return json.dumps({"ok": False, "error": f"{type(error).__name__}: {error}"})
    _keep(session, result)
    payload = _result_payload(result)
    payload["elapsed_s"] = format(time.perf_counter() - started, ".2f")
    return json.dumps(payload)


def _keep(session: Session, result: RunResult) -> None:
    session.results[result.manifest.run_id] = result
    while len(session.results) > MAX_KEPT_RESULTS:
        del session.results[next(iter(session.results))]


def _result_payload(result: RunResult) -> dict[str, Any]:
    structure = result.structure
    return {
        "ok": True,
        "run_id": result.manifest.run_id,
        "manifest": result.manifest.to_dict(),
        "label": result.scenario.label(),
        "summary": [
            {
                "note": s.note,
                "original_balance": money(s.original_balance),
                "wal_years": wal(s.wal_years),
                "first_principal": _window_cell(
                    s.first_principal_payment_date_number, s.first_principal_payment_date
                ),
                "last_principal": _window_cell(
                    s.last_principal_payment_date_number, s.last_principal_payment_date
                ),
                "total_principal": money(s.total_principal),
                "total_interest": money(s.total_interest),
                "total_write_downs": money(s.total_write_downs),
                "total_write_ups": money(s.total_write_ups),
                "final_balance": money(s.final_balance),
            }
            for s in result.note_summaries
        ],
        "tranche_summary": [
            {
                "tranche": t.tranche,
                "initial_class_notional_amount": money(t.initial_class_notional_amount),
                "initial_pct_of_pool": percent_of_fraction(t.initial_pct_of_pool),
                "total_principal": money(t.total_principal),
                "total_write_downs": money(t.total_write_downs),
                "total_write_ups": money(t.total_write_ups),
                "total_increases": money(t.total_increases),
                "final_balance": money(t.final_balance),
            }
            for t in result.tranche_summaries
        ],
        "pool_totals": _pool_totals_rows(result),
        "payment_dates": [
            {"n": row.payment_date_number, "date": row.payment_date.isoformat()}
            for row in structure
        ],
        "tranche_order": list(TRANCHE_ORDER),
        "balances_after": {
            t: [exact(row.balances_after[t]) for row in structure] for t in TRANCHE_ORDER
        },
        "write_downs": {
            t: [exact(row.write_down_allocated[t]) for row in structure] for t in TRANCHE_ORDER
        },
        "cumulative_write_downs": {
            t: [exact(row.cumulative_write_down[t]) for row in structure] for t in TRANCHE_ORDER
        },
        "note_flows": _note_flows(result),
        "pool_months": {
            "month": [row.month for row in result.pool_months],
            "month_end": [row.month_end.isoformat() for row in result.pool_months],
            "balance_end": [exact(row.balance_end) for row in result.pool_months],
        },
        "tables": {name: _table(result, name) for name in TABLE_NAMES},
        "files": {
            "csv_zip": _bundle_file_name(result),
            "xlsx": _workbook_file_name(result),
        },
    }


def _pool_totals_rows(result: RunResult) -> list[list[str]]:
    totals = result.pool_totals
    return [
        ["Cut-off Date Balance", money(totals.cut_off_date_balance)],
        [
            "Collection months",
            f"{totals.first_month}-{totals.last_month} (to {totals.last_month_end.isoformat()})",
        ],
        ["Scheduled principal", money(totals.total_scheduled_principal)],
        ["Prepayments", money(totals.total_prepayment)],
        ["Credit Event Amount", money(totals.total_credit_event_amount)],
        ["Interest", money(totals.total_interest)],
        ["Ending pool balance", money(totals.ending_balance)],
        [
            "Maturity Date",
            (
                f"PD {totals.maturity_payment_date_number} "
                f"({totals.maturity_payment_date.isoformat()}): {totals.maturity_reason}"
            ),
        ],
    ]


def _note_flows(result: RunResult) -> dict[str, dict[str, list[str]]]:
    flows: dict[str, dict[str, list[str]]] = {
        note: {"principal": [], "interest": [], "write_down": [], "balance_after": []}
        for note in NOTE_CLASSES
    }
    for row in result.note_cashflows:
        series = flows[row.note]
        series["principal"].append(exact(row.principal_paid))
        series["interest"].append(exact(row.interest))
        series["write_down"].append(exact(row.write_down))
        series["balance_after"].append(exact(row.balance_after))
    return flows


def _table(result: RunResult, name: str) -> dict[str, Any]:
    # ``_rows`` is the exact-value view ``export_csv`` writes; the page shows the digits
    # unchanged.
    rows = result._rows(name)
    columns = list(rows[0]) if rows else []
    return {"columns": columns, "rows": [[_cell(v) for v in row.values()] for row in rows]}


# --------------------------------------------------------------------------------------
# Downloads (bytes as base64, so the worker needs no buffer-proxy handling)
# --------------------------------------------------------------------------------------


def _result_for(run_id: str) -> RunResult:
    try:
        return _session().results[run_id]
    except KeyError:
        raise BridgeError(f"run {run_id!r} is no longer held; run the scenario again") from None


def _bundle_file_name(result: RunResult) -> str:
    from crt.gui.downloads import bundle_file_name

    return bundle_file_name(result)


def _workbook_file_name(result: RunResult) -> str:
    from crt.excel.structure_workbook import workbook_file_name

    return workbook_file_name(result)


def csv_bundle_base64(run_id: str) -> str:
    from crt.gui.downloads import csv_bundle_bytes

    return base64.b64encode(csv_bundle_bytes(_result_for(run_id))).decode("ascii")


def workbook_base64(run_id: str) -> str:
    from crt.excel.structure_workbook import structure_workbook_bytes

    return base64.b64encode(structure_workbook_bytes(_result_for(run_id))).decode("ascii")


# --------------------------------------------------------------------------------------
# The PPM tie-out (section 1 of docs/validation/tieout.md, computed here and now)
# --------------------------------------------------------------------------------------


def run_tieout() -> str:
    """All 96 PPM scenarios compared against the PPM tables; the section-1 summary.
    The report's manifest (which needs a git commit) is not built and nothing is
    written."""
    started = time.perf_counter()
    session = _session()
    try:
        runs = run_grid(session.inputs)
        results = compare_all(session.root, session.inputs, runs)
    except Exception as error:  # noqa: BLE001 - relayed verbatim, never swallowed
        return json.dumps({"ok": False, "error": f"{type(error).__name__}: {error}"})
    band_fails = sum(1 for band in results.window_bands if not band.passes)
    return json.dumps(
        {
            "ok": True,
            "scenarios": len(runs),
            "rows": [
                {
                    "family": s.family,
                    "cells": s.cells,
                    "passed": s.passes,
                    "failed": s.fails,
                    "worst_abs_diff": s.worst_abs_diff,
                    "tolerance": s.tolerance,
                    "status": s.status,
                }
                for s in results.summaries()
            ],
            "window_bands": len(results.window_bands),
            "window_band_fails": band_fails,
            "overall": "PASS" if results.overall_pass() else "FAIL",
            "elapsed_s": format(time.perf_counter() - started, ".1f"),
        }
    )
