"""The optional "acts on its own" question only adds a note. It never changes the result."""

from pathlib import Path

import pytest
import yaml

from riskcheck import Rulebook, evaluate, to_markdown

CASES = yaml.safe_load((Path(__file__).parent / "acceptance_cases.yaml").read_text(encoding="utf-8"))["cases"]
RB = Rulebook.builtin()
AGENT_NOTES = {"agent_high_risk", "agent_other"}


def notes(result):
    return {w.id for w in result.warnings if w.id in AGENT_NOTES}


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_ticking_it_never_changes_tier_reasons_or_obligations(case):
    base = evaluate(RB, {q: True for q in case["tick"]}, case["role"])
    agent = evaluate(RB, {**{q: True for q in case["tick"]}, "ctx_agentic": True}, case["role"])
    assert agent.tier.id == base.tier.id
    assert [r.id for r in agent.reasons] == [r.id for r in base.reasons]
    assert [(o.who, o.text) for o in agent.obligations] == [(o.who, o.text) for o in base.obligations]
    assert [w.id for w in agent.warnings if w.id not in AGENT_NOTES] == [w.id for w in base.warnings]
    assert notes(base) == set()


def test_high_risk_gets_the_oversight_and_logging_pointers():
    r = evaluate(RB, {"a3_employment": True, "ctx_agentic": True}, "deployer")
    assert r.tier.id == "high"
    assert notes(r) == {"agent_high_risk"}
    note = next(w for w in r.warnings if w.id == "agent_high_risk")
    assert note.cite == "Art. 12, 14, 26(2), 26(6)"
    for article in ("Art. 12", "Art. 14", "Art. 26(2)", "Art. 26(6)"):
        assert article in note.text


@pytest.mark.parametrize("answers, tier", [({}, "minimal"), ({"t_interacts": True}, "limited")])
def test_lower_tiers_get_the_pointer_to_transparency_and_gdpr(answers, tier):
    r = evaluate(RB, {**answers, "ctx_agentic": True}, "deployer")
    assert r.tier.id == tier
    assert notes(r) == {"agent_other"}
    assert "Art. 22" in next(w for w in r.warnings if w.id == "agent_other").text


@pytest.mark.parametrize("answers, tier", [({"p_social_scoring": True}, "prohibited"), ({"scope_military": True}, "out_of_scope")])
def test_no_note_when_banned_or_out_of_scope(answers, tier):
    r = evaluate(RB, {**answers, "ctx_agentic": True}, "deployer")
    assert r.tier.id == tier
    assert notes(r) == set()


def test_alone_it_is_not_a_use_and_does_not_trigger_the_scope_warning():
    r = evaluate(RB, {"scope_research": True, "ctx_agentic": True}, "provider")
    assert r.tier.id == "out_of_scope"
    assert [w.id for w in r.warnings] == []


def test_report_carries_the_note_and_never_the_tier_change():
    answers = {"a3_employment": True, "ctx_agentic": True}
    md = to_markdown(evaluate(RB, answers, "deployer"), RB, "CV agent")
    assert "**Note (Art. 12, 14, 26(2), 26(6)):**" in md
    plain = to_markdown(evaluate(RB, {"a3_employment": True}, "deployer"), RB, "CV agent")
    assert "**Note (" not in plain
    assert md.count("High risk") == plain.count("High risk")
