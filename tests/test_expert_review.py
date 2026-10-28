"""Regression tests for the fixes that came out of the devil's-advocate review."""

from riskcheck import Rulebook, evaluate, to_markdown

RB = Rulebook.builtin()


def cites(result):
    return {o.cite for o in result.obligations}


def test_prohibited_shows_only_the_ban():
    r = evaluate(RB, {"p_social_scoring": True}, "deployer")
    assert r.tier.id == "prohibited"
    assert cites(r) == {"Art. 5", "Art. 99(3)"}


def test_prohibited_beats_high_risk_without_high_risk_checklist():
    r = evaluate(RB, {"p_social_scoring": True, "a3_employment": True, "profiling": True}, "provider")
    assert r.tier.id == "prohibited"
    assert "Art. 9" not in cites(r)


def test_deployer_who_rebrands_gets_provider_duties():
    answers = {"a3_employment": True, "profiling": True}
    plain = evaluate(RB, answers, "deployer")
    shifted = evaluate(RB, {**answers, "ctx_role_change": True}, "deployer")
    assert "Art. 9" not in cites(plain) and not plain.role_shifted
    assert "Art. 9" in cites(shifted) and "Art. 26(1)" in cites(shifted)
    assert shifted.role_shifted and shifted.effective_role == "both"


def test_role_change_without_high_risk_changes_nothing():
    r = evaluate(RB, {"ctx_role_change": True}, "deployer")
    assert not r.role_shifted
    assert r.tier.id == "minimal"


def test_scope_conflict_warns():
    r = evaluate(RB, {"scope_research": True, "a3_employment": True}, "provider")
    assert r.tier.id == "out_of_scope"
    assert [w.id for w in r.warnings] == ["scope_conflict"]


def test_clean_scope_exclusion_has_no_warning():
    assert evaluate(RB, {"scope_military": True}, "provider").warnings == []


def test_exception_reason_says_it_is_self_assessed():
    r = evaluate(RB, {"a3_employment": True, "d_narrow_task": True}, "provider")
    rule = next(x for x in r.matched if x.id == "high.exception_applied")
    assert "Art. 80" in rule.note


def test_report_carries_rationale_and_warning():
    r = evaluate(RB, {"a3_employment": True, "d_narrow_task": True}, "provider")
    md = to_markdown(r, RB, "Invoice sorter", rationale="Only sorts invoices into folders.")
    assert "Art. 6(4) assessment note" in md and "Only sorts invoices" in md
    r2 = evaluate(RB, {"scope_research": True, "a3_credit": True}, "provider")
    assert "Check (Recital 24, Art. 2)" in to_markdown(r2, RB, "x")


def test_report_omits_rationale_when_exception_not_used():
    r = evaluate(RB, {}, "provider")
    assert "assessment note" not in to_markdown(r, RB, "x", rationale="ignored")
