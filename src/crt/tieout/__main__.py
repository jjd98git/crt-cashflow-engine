"""``python -m crt.tieout``: regenerate docs/validation/tieout.md and print the summary."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from crt.tieout.run import DEFAULT_PROJECT_ROOT, MANIFEST_PATH, REPORT_PATH, write_tieout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STACR 2026-DNA1 PPM tie-out")
    parser.add_argument(
        "--root", type=Path, default=DEFAULT_PROJECT_ROOT, help="project root (default: repo)"
    )
    args = parser.parse_args(argv)
    started = time.perf_counter()
    run = write_tieout(args.root)
    elapsed = time.perf_counter() - started
    for summary in run.results.summaries():
        print(
            f"{summary.family:28s} cells {summary.cells:4d}  pass {summary.passes:4d}  "
            f"fail {summary.fails:4d}  worst |diff| {summary.worst_abs_diff:>8s}  {summary.status}"
        )
    overall = run.results.overall_pass()
    print(f"Overall: {'PASS' if overall else 'FAIL'}  ({elapsed:.1f} s)")
    print(f"Report:   {args.root / REPORT_PATH}")
    print(f"Manifest: {args.root / MANIFEST_PATH}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
