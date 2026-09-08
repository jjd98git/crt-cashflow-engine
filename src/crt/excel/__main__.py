"""``python -m crt.excel <scenario.yaml> <out.xlsx> [--cpr X] [--cer X] [--sofr X]
[--early on|off]``: run one scenario and write the values workbook.

The overrides mirror the ``Scenario`` fields and are percentages, like the scenario file
(``--cpr 5`` is 5 % CPR).  When any override is given the run is named
``<file name>+overrides`` and the manifest records no scenario source file, because the
scenario run is then not the file's.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path

from crt.api import run_scenario
from crt.excel.structure_workbook import export_structure_workbook
from crt.money import percent_to_fraction
from crt.scenarios.loader import load_scenario_file
from crt.scenarios.scenario import ScenarioError
from crt.tieout.run import DEFAULT_PROJECT_ROOT


def _percent(text: str) -> Decimal:
    try:
        return Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number") from None


def _on_off(text: str) -> bool:
    lowered = text.strip().lower()
    if lowered in ("on", "true", "yes", "1"):
        return True
    if lowered in ("off", "false", "no", "0"):
        return False
    raise argparse.ArgumentTypeError(f"{text!r} is not on/off")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m crt.excel",
        description="Run a scenario and export the structure workbook (engine values).",
    )
    parser.add_argument("scenario", type=Path, help="scenario YAML file")
    parser.add_argument("out", type=Path, help="workbook path to write (.xlsx)")
    parser.add_argument("--cpr", type=_percent, help="CPR override, percent (e.g. 10)")
    parser.add_argument("--cer", type=_percent, help="CER override, percent (e.g. 2.5)")
    parser.add_argument("--sofr", type=_percent, help="flat SOFR Rate override, percent")
    parser.add_argument("--early", type=_on_off, help="early redemption: on or off")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=DEFAULT_PROJECT_ROOT,
        help="project root holding data/ and docs/ (default: the installed checkout)",
    )
    args = parser.parse_args(argv)

    try:
        scenario_file = load_scenario_file(args.scenario)
        scenario = scenario_file.to_scenario()
        overridden = any(v is not None for v in (args.cpr, args.cer, args.sofr, args.early))
        if overridden:
            # Each field keeps the file's value unless its flag was given; the result is
            # re-validated by Scenario.__post_init__.
            scenario = replace(
                scenario,
                cpr=scenario.cpr if args.cpr is None else percent_to_fraction(args.cpr),
                cer=scenario.cer if args.cer is None else percent_to_fraction(args.cer),
                sofr_rate=(
                    scenario.sofr_rate if args.sofr is None else percent_to_fraction(args.sofr)
                ),
                early_redemption=(
                    scenario.early_redemption if args.early is None else args.early
                ),
            )
            name = f"{scenario_file.name}+overrides"
            source: Path | None = None
        else:
            name = scenario_file.name
            source = args.scenario
        result = run_scenario(
            scenario, project_root=args.project_root, scenario_name=name, scenario_source=source
        )
        export_structure_workbook(result, args.out)
    except (ScenarioError, ValueError, RuntimeError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(
        f"wrote {args.out} ({args.out.stat().st_size:,} bytes): run {result.manifest.run_id}, "
        f"{result.scenario.label()}, Maturity Date PD {result.manifest.maturity_payment_date_number}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
