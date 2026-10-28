"""Turn a Result into a Markdown report someone can save, share or file."""

from __future__ import annotations

from datetime import date

from .engine import Result, Rulebook

ROLE_LABELS = {"provider": "Provider", "deployer": "Deployer", "both": "Provider and deployer"}
WHO_LABELS = {"provider": "Provider", "deployer": "Deployer", "all": "Everyone"}


def to_markdown(
    result: Result,
    rulebook: Rulebook,
    system_name: str = "",
    today: date | None = None,
    rationale: str = "",
) -> str:
    today = today or date.today()
    name = system_name.strip() or "Unnamed AI system"
    lines = [
        f"# {rulebook.title}: {name}",
        "",
        f"- **Result:** {result.tier.label}",
        f"- **Role assessed:** {ROLE_LABELS[result.role]}"
        + (f" (your answers make you {ROLE_LABELS[result.effective_role].lower()}, Art. 25)" if result.role_shifted else ""),
        f"- **Date:** {today.isoformat()}",
        f"- **Rulebook:** {rulebook.id} v{rulebook.version} (last reviewed {rulebook.last_reviewed})",
        f"- **Legal basis:** {rulebook.source}",
        "",
        f"> {result.tier.summary}",
        "",
    ]
    for w in result.warnings:
        lines += [f"> **Check ({w.cite}):** {w.text}", ""]
    lines += ["## Why", ""]
    if result.reasons:
        for rule in result.reasons:
            when = f" Applies from {rule.applies_from.day} {rule.applies_from:%B %Y}." if rule.applies_from else ""
            lines.append(f"- **{rule.cite}.** {rule.reason}{when}")
            if rule.note:
                lines.append(f"  - Note: {rule.note}")
    else:
        lines.append("- None of the listed prohibited, high-risk or transparency triggers apply.")

    if rationale.strip() and any(r.id == "high.exception_applied" for r in result.matched):
        lines += ["", "## Art. 6(4) assessment note", "", rationale.strip()]

    lines += ["", "## What you need to do", ""]
    if result.obligations:
        for ob in result.obligations:
            lines.append(f"- [ ] **{WHO_LABELS[ob.who]}:** {ob.text} *({ob.cite})*")
    else:
        lines.append("- No AI Act obligations identified.")

    lines += ["", "## Answers given", ""]
    if result.answers:
        for qid in result.answers:
            q = rulebook.questions[qid]
            lines.append(f"- {q.text} *({q.cite})*")
    else:
        lines.append("- No boxes ticked.")

    lines += [
        "",
        "---",
        "",
        "*This is a screening result based on the answers above, not legal advice. "
        "Confirm high-risk and prohibited results with a qualified lawyer.*",
        "",
    ]
    return "\n".join(lines)
