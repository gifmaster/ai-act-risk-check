"""Smoke tests for the Streamlit app using Streamlit's built-in test runner."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parents[1] / "app.py")


def run(example: str | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30).run()
    if example:
        at.selectbox(key="example").set_value(example).run()
    assert not at.exception
    return at


def all_text(at: AppTest) -> str:
    parts = [m.value for m in at.markdown]
    for kind in ("success", "info", "warning", "error"):
        parts += [e.value for e in getattr(at, kind)]
    return "\n".join(parts)


def test_app_starts_minimal():
    assert "Minimal risk" in all_text(run())


def test_cv_example_shows_high_risk_with_citation():
    text = all_text(run("CV screening tool"))
    assert "High risk" in text
    assert "Annex III point 4" in text


def test_ticking_a_prohibited_box_changes_the_result():
    at = run()
    at.checkbox(key="q_p_social_scoring").check().run()
    assert "Prohibited" in all_text(at)
