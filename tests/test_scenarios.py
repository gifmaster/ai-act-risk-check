"""Real-world scenarios with their expected classification.

Each test reads like a short case: what the system does, and what the AI Act
says. If a rulebook change breaks one of these, the change needs a second look.
"""

import pytest

from riskcheck import Rulebook, evaluate


@pytest.fixture(scope="module")
def rb():
    return Rulebook.builtin()


def tier(rb, role="both", **answers):
    return evaluate(rb, answers, role).tier.id


def cites(result):
    return {r.cite for r in result.reasons}


# --- Minimal ---------------------------------------------------------------- #

def test_spam_filter_is_minimal(rb):
    result = evaluate(rb, {})
    assert result.tier.id == "minimal"
    # AI literacy still applies to everyone in scope
    assert any("Art. 4" in o.cite for o in result.obligations)


# --- Transparency ----------------------------------------------------------- #

def test_customer_service_chatbot_is_limited(rb):
    result = evaluate(rb, {"t_interacts": True, "t_generates": True}, role="provider")
    assert result.tier.id == "limited"
    assert {"Art. 50(1)", "Art. 50(2)"} <= cites(result)


def test_marketing_deepfake_needs_disclosure_by_deployer(rb):
    result = evaluate(rb, {"t_deepfake": True}, role="deployer")
    assert result.tier.id == "limited"
    assert any(o.cite == "Art. 50(4)" for o in result.obligations)


# --- High risk -------------------------------------------------------------- #

def test_cv_screening_is_high_risk(rb):
    result = evaluate(rb, {"a3_employment": True}, role="deployer")
    assert result.tier.id == "high"
    assert "Art. 6(2), Annex III point 4" in cites(result)
    assert any(o.cite == "Art. 26(7)" for o in result.obligations)  # inform workers


def test_credit_scoring_triggers_fria_for_deployer(rb):
    result = evaluate(rb, {"a3_credit": True}, role="deployer")
    assert result.tier.id == "high"
    assert any(o.cite == "Art. 27" for o in result.obligations)


def test_private_hr_tool_needs_no_fria(rb):
    result = evaluate(rb, {"a3_employment": True}, role="deployer")
    assert not any(o.cite == "Art. 27" for o in result.obligations)


def test_medical_device_with_notified_body_is_high_risk(rb):
    result = evaluate(rb, {"a1_product": True, "a1_third_party": True})
    assert result.tier.id == "high"
    assert any(r.applies_from and r.applies_from.year == 2028 for r in result.reasons)


def test_annex_i_product_without_third_party_assessment_is_not_high(rb):
    assert tier(rb, a1_product=True) == "minimal"


def test_high_risk_dates_follow_the_2026_omnibus(rb):
    result = evaluate(rb, {"a3_education": True})
    (rule,) = result.reasons
    assert rule.applies_from.isoformat() == "2027-12-02"


# --- Art. 6(3) exception ---------------------------------------------------- #

def test_document_sorter_in_hr_uses_exception(rb):
    result = evaluate(rb, {"a3_employment": True, "d_narrow_task": True}, role="provider")
    assert result.tier.id == "minimal"
    provider_cites = {o.cite for o in result.obligations}
    assert {"Art. 6(4)", "Art. 49(2)"} <= provider_cites


def test_profiling_cancels_the_exception(rb):
    assert tier(rb, a3_employment=True, d_preparatory=True, profiling=True) == "high"


def test_profiling_alone_is_not_high_risk(rb):
    assert tier(rb, profiling=True) == "minimal"


# --- Prohibited ------------------------------------------------------------- #

@pytest.mark.parametrize(
    "practice",
    ["p_social_scoring", "p_emotion_work_education", "p_face_scraping", "p_csam"],
)
def test_prohibited_practices(rb, practice):
    result = evaluate(rb, {practice: True})
    assert result.tier.id == "prohibited"
    assert any(o.cite == "Art. 99(3)" for o in result.obligations)


def test_prohibited_beats_everything_else(rb):
    assert tier(rb, p_social_scoring=True, a3_credit=True, t_interacts=True) == "prohibited"


# --- Scope ------------------------------------------------------------------ #

def test_military_is_out_of_scope_even_if_other_boxes_ticked(rb):
    result = evaluate(rb, {"scope_military": True, "a3_biometrics": True})
    assert result.tier.id == "out_of_scope"
    assert result.obligations == []


# --- Roles ------------------------------------------------------------------ #

def test_role_filters_obligations(rb):
    answers = {"a3_employment": True}
    provider = evaluate(rb, answers, role="provider").obligations
    deployer = evaluate(rb, answers, role="deployer").obligations
    assert all(o.who in ("provider", "all") for o in provider)
    assert all(o.who in ("deployer", "all") for o in deployer)
    both = evaluate(rb, answers, role="both").obligations
    assert len(both) == len(provider) + len(deployer) - sum(o.who == "all" for o in provider)


def test_gpai_provider_gets_model_obligations(rb):
    result = evaluate(rb, {"ctx_gpai_provider": True}, role="provider")
    assert any(o.cite == "Art. 53(1)(c)" for o in result.obligations)
