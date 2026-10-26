"""Acceptance tests: real-world scenarios from tests/acceptance_cases.yaml.

The same file drives the manual test plan in docs/TEST-PLAN.md, so what a
human checks in the app and what CI checks are always the same cases.
"""

from pathlib import Path

import pytest
import yaml

from riskcheck import Rulebook, evaluate

CASES = yaml.safe_load((Path(__file__).parent / "acceptance_cases.yaml").read_text(encoding="utf-8"))["cases"]
RB = Rulebook.builtin()


def test_case_ids_are_unique():
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids))


def test_every_case_only_ticks_real_questions():
    for case in CASES:
        unknown = set(case["tick"]) - set(RB.questions)
        assert not unknown, f"{case['id']} ticks unknown questions: {unknown}"


@pytest.mark.parametrize("case", CASES, ids=[f"{c['id']} {c['title']}" for c in CASES])
def test_acceptance(case):
    expect = case["expect"]
    result = evaluate(RB, {q: True for q in case["tick"]}, case["role"])

    assert result.tier.id == expect["tier"], (
        f"{case['id']}: expected {expect['tier']}, got {result.tier.id}"
    )

    why = {r.cite for r in result.reasons}
    for cite in expect.get("cites", []):
        assert cite in why, f"{case['id']}: '{cite}' missing from Why. Got {sorted(why)}"

    todo = {o.cite for o in result.obligations}
    for cite in expect.get("must_do", []):
        assert cite in todo, f"{case['id']}: obligation '{cite}' missing. Got {sorted(todo)}"
    for cite in expect.get("must_not_do", []):
        assert cite not in todo, f"{case['id']}: obligation '{cite}' should not apply"

    if "applies_from" in expect:
        dates = {r.applies_from.isoformat() for r in result.reasons if r.applies_from}
        assert expect["applies_from"] in dates, f"{case['id']}: expected date {expect['applies_from']}, got {dates}"


def test_manual_test_plan_is_up_to_date():
    """docs/TEST-PLAN.md must be regenerated when cases or the rulebook change."""
    import subprocess, sys

    root = Path(__file__).parents[1]
    plan = root / "docs" / "TEST-PLAN.md"
    before = plan.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(root / "scripts" / "make_test_plan.py")], check=True, capture_output=True)
    after = plan.read_text(encoding="utf-8")
    plan.write_text(before, encoding="utf-8")
    assert before == after, "docs/TEST-PLAN.md is out of date. Run: python scripts/make_test_plan.py"
