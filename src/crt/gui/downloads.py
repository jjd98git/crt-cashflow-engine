"""In-memory payloads for the download buttons: the CSV bundle (zip) and the values
workbook (xlsx)."""

from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

from crt.api import RunResult, export_csv
from crt.excel.structure_workbook import structure_workbook_bytes, workbook_file_name

# Fixed timestamp inside the archive so that the zip bytes depend only on the file
# contents (zip headers otherwise carry the local write time).
_ZIP_ENTRY_DATETIME = (1980, 1, 1, 0, 0, 0)


def csv_bundle_bytes(result: RunResult) -> bytes:
    """``export_csv`` into a temporary directory and zip the files (deflated)."""
    buffer = io.BytesIO()
    with tempfile.TemporaryDirectory() as tmp:
        written = export_csv(result, Path(tmp))
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in written:
                info = zipfile.ZipInfo(path.name, date_time=_ZIP_ENTRY_DATETIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def bundle_file_name(result: RunResult) -> str:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in result.manifest.scenario_name)
    return f"crt_run_{safe}_{result.manifest.run_id}.zip"


def workbook_bytes(result: RunResult) -> bytes:
    """The values workbook of ``crt.excel.structure_workbook`` (no formulas; BRIEF section 9's
    live-formula workbook is a later Phase 5 deliverable)."""
    return structure_workbook_bytes(result)


def workbook_download_name(result: RunResult) -> str:
    return workbook_file_name(result)
