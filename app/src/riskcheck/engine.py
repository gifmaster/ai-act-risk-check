"""A small, transparent rules engine.

The engine knows nothing about the EU AI Act. All regulatory knowledge lives in
a YAML rulebook (see ``rulebooks/``). That separation is deliberate:

* the logic can be read and checked by non-programmers (lawyers, compliance)
* every result points back to the exact rule and article that produced it
* the same engine can run other rulebooks (e.g. DORA) without code changes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

ROLES = ("provider", "deployer")
RULEBOOK_DIR = Path(__file__).parent / "rulebooks"


class RulebookError(ValueError):
    """Raised when a rulebook is malformed or refers to something that does not exist."""


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Tier:
    id: str
    label: str
    summary: str
    rank: int
    exclusive: bool = False  # if True, only this tier's own obligations are shown


@dataclass(frozen=True)
class Question:
    id: str
    section: str
    text: str
    cite: str = ""
    help: str = ""


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    intro: str = ""


@dataclass(frozen=True)
class Obligation:
    who: str  # "provider", "deployer" or "all"
    text: str
    cite: str

    def applies_to(self, role: str) -> bool:
        if role == "both":
            return True
        return self.who in ("all", role)


@dataclass(frozen=True)
class Rule:
    id: str
    when: Any
    tier: str | None
    cite: str = ""
    reason: str = ""
    note: str = ""
    applies_from: date | None = None
    stop: bool = False
    hidden: bool = False
    makes_provider: bool = False  # a deployer who matches this rule takes on provider duties
    obligations: tuple[Obligation, ...] = ()


@dataclass(frozen=True)
class Warning:
    """A caution shown next to the result when a condition holds. It never changes the tier."""

    id: str
    when: Any
    text: str
    cite: str = ""
    kind: str = "check"  # "check" asks the user to re-check an answer, "note" adds a pointer
    tiers: tuple[str, ...] = ()  # only for these result tiers; empty means any tier


@dataclass
class Result:
    rulebook_id: str
    rulebook_version: str
    tier: Tier
    role: str
    matched: list[Rule]
    obligations: list[Obligation]
    answers: dict[str, bool] = field(default_factory=dict)
    warnings: list[Warning] = field(default_factory=list)
    effective_role: str = ""

    @property
    def role_shifted(self) -> bool:
        """True when the answers move a deployer into the provider role (Art. 25)."""
        return bool(self.effective_role) and self.effective_role != self.role

    @property
    def reasons(self) -> list[Rule]:
        """Matched rules worth showing to a human (skips internal helper rules)."""
        return [r for r in self.matched if not r.hidden]


# --------------------------------------------------------------------------- #
# Rulebook
# --------------------------------------------------------------------------- #


class Rulebook:
    def __init__(self, data: Mapping[str, Any]):
        try:
            self.id: str = data["id"]
            self.title: str = data["title"]
            self.version: str = str(data["version"])
            self.last_reviewed: str = str(data.get("last_reviewed", ""))
            self.source: str = data.get("source", "")
            self.roles: dict[str, str] = dict(data.get("roles", {}))
            self.tiers: dict[str, Tier] = {
                t["id"]: Tier(t["id"], t["label"], t["summary"], rank, bool(t.get("exclusive", False)))
                for rank, t in enumerate(data["tiers"])
            }
            self.default_tier: str = data["default_tier"]
            self.sections: list[Section] = [Section(**s) for s in data["sections"]]
            self.questions: dict[str, Question] = {
                q["id"]: Question(**q) for q in data["questions"]
            }
            self.facts: dict[str, Any] = dict(data.get("facts", {}))
            self.rules: list[Rule] = [_parse_rule(r) for r in data["rules"]]
            self.warnings: list[Warning] = [Warning(**{**w, "tiers": tuple(w.get("tiers", ()))}) for w in data.get("warnings", [])]
            self.always: tuple[Obligation, ...] = tuple(
                Obligation(**o) for o in data.get("always", [])
            )
        except KeyError as exc:  # pragma: no cover - message is the useful part
            raise RulebookError(f"Rulebook is missing required field: {exc}") from exc
        self._validate()

    # -- loading ---------------------------------------------------------------

    @classmethod
    def from_file(cls, path: str | Path) -> "Rulebook":
        with open(path, encoding="utf-8") as fh:
            return cls(yaml.safe_load(fh))

    @classmethod
    def builtin(cls, name: str = "eu_ai_act") -> "Rulebook":
        return cls.from_file(RULEBOOK_DIR / f"{name}.yaml")

    # -- validation ------------------------------------------------------------

    def _validate(self) -> None:
        section_ids = {s.id for s in self.sections}
        for q in self.questions.values():
            if q.section not in section_ids:
                raise RulebookError(f"Question '{q.id}' uses unknown section '{q.section}'")

        if self.default_tier not in self.tiers:
            raise RulebookError(f"default_tier '{self.default_tier}' is not a defined tier")

        for name, cond in self.facts.items():
            self._check_refs(cond, f"fact '{name}'")

        for w in self.warnings:
            if not w.text:
                raise RulebookError(f"Warning '{w.id}' needs text")
            self._check_refs(w.when, f"warning '{w.id}'")
            if w.kind not in ("check", "note"):
                raise RulebookError(f"Warning '{w.id}' has unknown kind '{w.kind}'")
            for t in w.tiers:
                if t not in self.tiers:
                    raise RulebookError(f"Warning '{w.id}' names unknown tier '{t}'")

        seen: set[str] = set()
        for rule in self.rules:
            if rule.id in seen:
                raise RulebookError(f"Duplicate rule id '{rule.id}'")
            seen.add(rule.id)
            if rule.tier is not None and rule.tier not in self.tiers:
                raise RulebookError(f"Rule '{rule.id}' uses unknown tier '{rule.tier}'")
            if not rule.hidden and not rule.cite:
                raise RulebookError(f"Visible rule '{rule.id}' must cite its legal basis")
            self._check_refs(rule.when, f"rule '{rule.id}'")
            for ob in rule.obligations:
                if ob.who not in (*ROLES, "all"):
                    raise RulebookError(f"Rule '{rule.id}' has obligation for unknown role '{ob.who}'")
                if not ob.cite:
                    raise RulebookError(f"Every obligation in rule '{rule.id}' must have a citation")

    def _check_refs(self, cond: Any, where: str) -> None:
        for ref in _refs(cond):
            if ref.startswith("$"):
                if ref[1:] not in self.facts:
                    raise RulebookError(f"{where} refers to unknown fact '{ref}'")
            elif ref not in self.questions:
                raise RulebookError(f"{where} refers to unknown question '{ref}'")

    # -- helpers for user interfaces ------------------------------------------

    def questions_in(self, section_id: str) -> list[Question]:
        return [q for q in self.questions.values() if q.section == section_id]


def _parse_rule(raw: Mapping[str, Any]) -> Rule:
    applies = raw.get("applies_from")
    if isinstance(applies, str):
        applies = date.fromisoformat(applies)
    return Rule(
        id=raw["id"],
        when=raw["when"],
        tier=raw.get("tier"),
        cite=raw.get("cite", ""),
        reason=raw.get("reason", ""),
        note=raw.get("note", ""),
        applies_from=applies,
        stop=bool(raw.get("stop", False)),
        hidden=bool(raw.get("hidden", False)),
        makes_provider=bool(raw.get("makes_provider", False)),
        obligations=tuple(Obligation(**o) for o in raw.get("obligations", [])),
    )


def _refs(cond: Any) -> Iterable[str]:
    """Yield every question id or $fact referenced in a condition."""
    if isinstance(cond, str):
        yield cond
    elif isinstance(cond, Mapping):
        if len(cond) != 1:
            raise RulebookError(f"A condition must have exactly one operator, got {list(cond)}")
        (op, value), = cond.items()
        if op in ("all", "any"):
            for item in value:
                yield from _refs(item)
        elif op == "not":
            yield from _refs(value)
        else:
            raise RulebookError(f"Unknown condition operator '{op}'")
    else:
        raise RulebookError(f"Invalid condition: {cond!r}")


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #


def evaluate(rulebook: Rulebook, answers: Mapping[str, bool], role: str = "both") -> Result:
    """Run the rulebook against a set of yes/no answers.

    Unanswered questions count as "no". Unknown answer keys are rejected so a
    typo cannot silently change a result.
    """
    if role not in (*ROLES, "both"):
        raise ValueError(f"role must be one of {ROLES + ('both',)}, got '{role}'")
    unknown = set(answers) - set(rulebook.questions)
    if unknown:
        raise ValueError(f"Unknown question id(s): {sorted(unknown)}")

    clean = {qid: bool(answers.get(qid, False)) for qid in rulebook.questions}
    cache: dict[str, bool] = {}

    def check(cond: Any) -> bool:
        if isinstance(cond, str):
            if cond.startswith("$"):
                name = cond[1:]
                if name not in cache:
                    cache[name] = check(rulebook.facts[name])
                return cache[name]
            return clean[cond]
        (op, value), = cond.items()
        if op == "all":
            return all(check(c) for c in value)
        if op == "any":
            return any(check(c) for c in value)
        return not check(value)  # "not"

    matched: list[Rule] = []
    for rule in rulebook.rules:
        if check(rule.when):
            if rule.stop:
                matched = [rule]
                break
            matched.append(rule)

    tier_ids = [r.tier for r in matched if r.tier is not None]
    tier_id = max(tier_ids, key=lambda t: rulebook.tiers[t].rank, default=rulebook.default_tier)
    tier = rulebook.tiers[tier_id]

    # A deployer who takes over the provider role (Art. 25) carries both sets of duties.
    effective = role
    if role == "deployer" and any(r.makes_provider for r in matched):
        effective = "both"

    obligations: list[Obligation] = []
    seen: set[tuple[str, str]] = set()
    if tier.exclusive:
        sources = [o for r in matched if r.tier == tier_id for o in r.obligations]
    else:
        sources = [o for r in matched for o in r.obligations]
        if tier_id != "out_of_scope":
            sources += list(rulebook.always)
    for ob in sources:
        key = (ob.who, ob.text)
        if ob.applies_to(effective) and key not in seen:
            seen.add(key)
            obligations.append(ob)

    return Result(
        rulebook_id=rulebook.id,
        rulebook_version=rulebook.version,
        tier=tier,
        role=role,
        matched=matched,
        obligations=obligations,
        answers={k: v for k, v in clean.items() if v},
        warnings=[w for w in rulebook.warnings if check(w.when) and (not w.tiers or tier_id in w.tiers)],
        effective_role=effective,
    )
