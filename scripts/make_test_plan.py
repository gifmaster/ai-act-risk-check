"""Generate docs/TEST-PLAN.md from tests/acceptance_cases.yaml.

Run:  python scripts/make_test_plan.py
The question wording is pulled from the rulebook, so the plan always matches the app.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from riskcheck import Rulebook, evaluate  # noqa: E402
CASES = yaml.safe_load((ROOT / "tests" / "acceptance_cases.yaml").read_text(encoding="utf-8"))["cases"]
RB = Rulebook.builtin()
ROLE = {"provider": "Provider", "deployer": "Deployer", "both": "Provider and deployer"}
SECTION = {s.id: s.title for s in RB.sections}


def fmt_date(iso: str) -> str:
    from datetime import date

    d = date.fromisoformat(iso)
    return f"{d.day} {d:%B %Y}"


lines = [
    "# Test plan: EU AI Act Risk Check",
    "",
    f"Rulebook v{RB.version}. Generated from `tests/acceptance_cases.yaml` by `scripts/make_test_plan.py`.",
    "The same cases run automatically on every push (`tests/test_acceptance.py`).",
    "",
    "## How to run a case",
    "",
    "1. Reload the app so every box is unticked.",
    "2. Set **Your role** as listed.",
    "3. Open the section named before each question and tick only the boxes listed.",
    "4. Compare the result panel with **Expected**. Tick the case off if everything matches.",
    "",
    "## Before you start: app checks",
    "",
    "- [ ] The app loads without errors and shows **Minimal risk** with nothing ticked",
    "- [ ] **Load an example** fills in the boxes (try *CV screening tool*: should show **High risk**)",
    "- [ ] Switching **Your role** changes the list under *What you need to do*",
    "- [ ] **Download report** gives a Markdown file with the result, citations, a checklist and the line *not legal advice*",
    "- [ ] The *readable YAML file* link in the sidebar opens the rulebook on GitHub",
    "- [ ] The app works on a phone (questions stack above the result)",
    "",
    "## Scenarios",
    "",
]

for case in CASES:
    exp = case["expect"]
    tier = RB.tiers[exp["tier"]].label
    lines += [f"### {case['id']} {case['title']}", "", f"*{case['story']}*", "", f"**Role:** {ROLE[case['role']]}", ""]
    if case["tick"]:
        lines.append("**Tick:**")
        for qid in case["tick"]:
            q = RB.questions[qid]
            lines.append(f"- {SECTION[q.section]}: *{q.text}*")
    else:
        lines.append("**Tick:** nothing")
    lines += ["", f"**Expected:** {tier}"]
    if exp.get("cites"):
        lines.append(f"- Why shows: {', '.join(exp['cites'])}")
    if exp.get("applies_from"):
        lines.append(f"- Applies from {fmt_date(exp['applies_from'])}")
    if exp.get("must_do"):
        lines.append(f"- To-do list includes: {', '.join(exp['must_do'])}")
    if exp.get("must_not_do"):
        lines.append(f"- To-do list does **not** include: {', '.join(exp['must_not_do'])}")
    n = len(evaluate(RB, {q: True for q in case["tick"]}, case["role"]).obligations)
    lines += [f"- {n} item(s) under *What you need to do*", "", "- [ ] Pass", ""]

lines += [
    "## If a case fails",
    "",
    "Note the case id, what you ticked and what the app showed, and open an issue on GitHub.",
    "If the law has changed, update the rulebook, bump its version, and update the expected result in `tests/acceptance_cases.yaml`.",
    "",
]

out = ROOT / "docs" / "TEST-PLAN.md"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out.relative_to(ROOT)} with {len(CASES)} cases")
