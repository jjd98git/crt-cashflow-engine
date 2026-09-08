"""Headless smoke test of the Streamlit app (``pytest -m gui``): both modes run without
an uncaught exception, and a bad override surfaces the validation message."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.gui

streamlit_testing = pytest.importorskip("streamlit.testing.v1")

APP_PATH = Path(__file__).resolve().parents[2] / "src/crt/gui/app.py"


@pytest.fixture
def app() -> streamlit_testing.AppTest:  # type: ignore[name-defined]
    at = streamlit_testing.AppTest.from_file(str(APP_PATH), default_timeout=120)
    at.run()
    assert not at.exception
    return at


def _button(at: streamlit_testing.AppTest, label: str) -> streamlit_testing.AppTest:  # type: ignore[name-defined]
    return next(b for b in at.button if b.label == label)


EXCEL_BUTTON_LABEL = "Download Excel workbook (values)"


def _download_labels(at: streamlit_testing.AppTest) -> list[str]:  # type: ignore[name-defined]
    return [b.proto.label for b in at.download_button]


def test_single_run_renders_summary(app: streamlit_testing.AppTest) -> None:  # type: ignore[name-defined]
    app.selectbox(key="single_preset").select("pricing_speed.yaml").run()
    _button(app, "Run").click().run()
    assert not app.exception and not app.error
    summary = app.dataframe[0].value
    assert list(summary.index) == ["A-1", "M-1", "M-2A", "M-2B"]
    assert summary.loc["A-1", "WAL (years)"] == "1.59"
    assert summary.loc["M-2B", "Last principal PD"] == "60 (2031-02-25)"
    # One values-workbook download per run, next to the CSV bundle and the manifest.
    assert _download_labels(app).count(EXCEL_BUTTON_LABEL) == 1
    assert any("Phase 5" in c.value for c in app.caption)


def test_compare_mode_renders_difference_table(app: streamlit_testing.AppTest) -> None:  # type: ignore[name-defined]
    app.radio[0].set_value("Compare").run()
    app.selectbox(key="a_preset").select("pricing_speed.yaml").run()
    app.selectbox(key="b_preset").select("stress_5cpr_2_5cer.yaml").run()
    _button(app, "Run both").click().run()
    assert not app.exception and not app.error
    difference = next(d for d in app.dataframe if "B - A" in list(d.value.columns))
    write_downs = difference.value[
        (difference.value["Note"] == "M-2B") & (difference.value["Metric"] == "total_write_downs")
    ]
    assert write_downs["A"].item() == "0.00"
    assert write_downs["B - A"].item() != "0.00"
    # One workbook per scenario in compare mode.
    assert _download_labels(app).count(EXCEL_BUTTON_LABEL) == 2


def test_bad_override_shows_validation_message(app: streamlit_testing.AppTest) -> None:  # type: ignore[name-defined]
    app.selectbox(key="single_preset").select("pricing_speed.yaml").run()
    app.selectbox(key="single_pricing_speed.yaml_cpr_grid").select("Custom…").run()
    app.text_input(key="single_pricing_speed.yaml_cpr_custom").set_value("150").run()
    assert not app.exception
    assert any("CPR 1.50 must satisfy 0 <= CPR < 1" in e.value for e in app.error)
    app.text_input(key="single_pricing_speed.yaml_cpr_custom").set_value("ten").run()
    assert any("is not a number" in e.value for e in app.error)
