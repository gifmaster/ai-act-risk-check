"""Tests for the generic engine and rulebook validation."""

import copy

import pytest

from riskcheck import Rulebook, RulebookError, evaluate, to_markdown

MINI = {
    "id": "mini",
    "title": "Mini",
    "version": "1",
    "default_tier": "low",
    "tiers": [
        {"id": "low", "label": "Low", "summary": "-"},
        {"id": "high", "label": "High", "summary": "-"},
    ],
    "sections": [{"id": "s", "title": "S"}],
    "questions": [
        {"id": "a", "section": "s", "text": "A"},
        {"id": "b", "section": "s", "text": "B"},
    ],
    "facts": {"both": {"all": ["a", "b"]}},
    "rules": [
        {"id": "r1", "when": "$both", "tier": "high", "cite": "X1", "reason": "a and b"},
        {"id": "r2", "when": {"not": "a"}, "tier": None, "cite": "X2", "reason": "not a"},
    ],
}


def test_engine_is_rulebook_agnostic():
    rb = Rulebook(MINI)
    assert evaluate(rb, {"a": True, "b": True}).tier.id == "high"
    assert evaluate(rb, {"a": True}).tier.id == "low"
    assert [r.id for r in evaluate(rb, {}).matched] == ["r2"]


def test_unknown_answer_is_rejected():
    rb = Rulebook(MINI)
    with pytest.raises(ValueError, match="Unknown question"):
        evaluate(rb, {"typo": True})


def test_bad_role_is_rejected():
    with pytest.raises(ValueError):
        evaluate(Rulebook(MINI), {}, role="owner")


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda d: d["rules"][0].update(when="missing_q"), "unknown question"),
        (lambda d: d["rules"][0].update(when="$nope"), "unknown fact"),
        (lambda d: d["rules"][0].update(tier="medium"), "unknown tier"),
        (lambda d: d["rules"][0].update(cite=""), "must cite"),
        (lambda d: d["rules"].append(dict(d["rules"][0])), "Duplicate"),
        (lambda d: d["rules"][0].update(when={"xor": ["a"]}), "Unknown condition operator"),
    ],
)
def test_validation_catches_mistakes(mutate, message):
    data = copy.deepcopy(MINI)
    mutate(data)
    with pytest.raises(RulebookError, match=message):
        Rulebook(data)


def test_builtin_rulebook_loads_and_every_question_is_used():
    rb = Rulebook.builtin()
    from riskcheck.engine import _refs

    used: set[str] = set()
    conds = [r.when for r in rb.rules] + list(rb.facts.values())
    for c in conds:
        used |= {x for x in _refs(c) if not x.startswith("$")}
    unused = set(rb.questions) - used
    assert not unused, f"Questions never used by any rule: {unused}"


def test_markdown_report_contains_result_and_citations():
    rb = Rulebook.builtin()
    result = evaluate(rb, {"a3_employment": True}, role="deployer")
    md = to_markdown(result, rb, "CV screener")
    assert "# EU AI Act risk check: CV screener" in md
    assert "High risk" in md
    assert "Annex III point 4" in md
    assert "- [ ] **Deployer:**" in md
    assert "not legal advice" in md
