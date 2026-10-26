"""Streamlit front end for the EU AI Act risk check.

Run locally:  streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from riskcheck import Rulebook, evaluate, to_markdown  # noqa: E402
from riskcheck.report import ROLE_LABELS, WHO_LABELS  # noqa: E402

# Change this to your own repository once it is on GitHub.
REPO_URL = "https://github.com/gifmaster/ai-act-risk-check"

TIER_STYLE = {
    "minimal": ("🟢", "success"),
    "limited": ("🔵", "info"),
    "high": ("🟠", "warning"),
    "prohibited": ("🔴", "error"),
    "out_of_scope": ("⚪", "info"),
}

EXAMPLES = {
    "Start from scratch": {},
    "Customer service chatbot": {"t_interacts": True, "t_generates": True},
    "CV screening tool": {"a3_employment": True, "profiling": True},
    "Credit scoring model": {"a3_credit": True, "profiling": True},
    "Invoice sorting in HR": {"a3_employment": True, "d_narrow_task": True},
    "Emotion tracking of employees": {"p_emotion_work_education": True},
}

st.set_page_config(page_title="EU AI Act risk check", page_icon="⚖️", layout="wide")


@st.cache_resource
def load_rulebook() -> Rulebook:
    return Rulebook.builtin("eu_ai_act")


rb = load_rulebook()

# --- Header ------------------------------------------------------------------
st.title("EU AI Act risk check")
st.caption(
    f"Rulebook v{rb.version}, reviewed {rb.last_reviewed}. {rb.source}. "
    "Every result shows the rule and article behind it."
)

# --- Sidebar: setup ------------------------------------------------------------
with st.sidebar:
    st.header("Setup")
    system_name = st.text_input("Name of the AI system", placeholder="e.g. CV screening assistant")
    role = st.radio(
        "Your role",
        options=["deployer", "provider", "both"],
        format_func=lambda r: ROLE_LABELS[r],
        help="\n\n".join(rb.roles.values()),
    )
    example = st.selectbox("Load an example", list(EXAMPLES), key="example")
    st.divider()
    st.markdown(
        f"**How it works.** You answer yes/no questions. Transparent rules, written in a "
        f"[readable YAML file]({REPO_URL}/blob/main/src/riskcheck/rulebooks/eu_ai_act.yaml), decide the outcome. No AI guesses the answer."
    )
    st.caption("Screening tool, not legal advice.")

# Apply an example by pre-setting the checkbox state once per selection.
if st.session_state.get("_applied_example") != example:
    for qid in rb.questions:
        st.session_state[f"q_{qid}"] = bool(EXAMPLES[example].get(qid, False))
    st.session_state["_applied_example"] = example

# --- Questionnaire -------------------------------------------------------------
left, right = st.columns([3, 2], gap="large")

with left:
    for section in rb.sections:
        questions = rb.questions_in(section.id)
        ticked = sum(st.session_state.get(f"q_{q.id}", False) for q in questions)
        label = f"{section.title}" + (f"  ·  {ticked} ticked" if ticked else "")
        with st.expander(label, expanded=section.id in ("scope", "annex_iii") or ticked > 0):
            if section.intro:
                st.caption(section.intro)
            for q in questions:
                st.checkbox(f"{q.text}  `{q.cite}`", key=f"q_{q.id}", help=q.help or None)

answers = {qid: st.session_state.get(f"q_{qid}", False) for qid in rb.questions}
result = evaluate(rb, answers, role)

# --- Result --------------------------------------------------------------------
with right:
    icon, kind = TIER_STYLE.get(result.tier.id, ("", "info"))
    getattr(st, kind)(f"### {icon} {result.tier.label}\n{result.tier.summary}")

    st.subheader("Why")
    if result.reasons:
        for rule in result.reasons:
            when = f" · applies from {rule.applies_from.day} {rule.applies_from:%b %Y}" if rule.applies_from else ""
            st.markdown(f"**{rule.cite}**{when}  \n{rule.reason}")
            if rule.note:
                st.caption(rule.note)
    else:
        st.markdown("None of the prohibited, high-risk or transparency triggers apply.")

    st.subheader(f"What you need to do ({len(result.obligations)})")
    for ob in result.obligations:
        st.markdown(f"- **{WHO_LABELS[ob.who]}:** {ob.text} `{ob.cite}`")

    st.download_button(
        "Download report (Markdown)",
        data=to_markdown(result, rb, system_name),
        file_name=f"ai-act-check-{(system_name or 'system').lower().replace(' ', '-')}.md",
        mime="text/markdown",
        width="stretch",
    )
