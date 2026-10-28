# Method and limitations

## Sources

- Regulation (EU) 2024/1689 (the AI Act)
- Regulation (EU) 2026/1744, the Digital Omnibus on AI, in force since 27 July 2026

Rulebook version and review date are printed in every report. When the law or official guidance changes, the rulebook is updated, the version bumped and the scenario tests adjusted.

## Key dates used

| Date | What applies |
|---|---|
| 2 Feb 2025 | Prohibited practices (Art. 5(1)(a)-(h)), AI literacy (Art. 4) |
| 2 Aug 2025 | General-purpose AI model obligations |
| 2 Aug 2026 | Transparency obligations (Art. 50) |
| 2 Dec 2026 | New prohibitions on non-consensual intimate imagery and CSAM; Art. 50(2) marking for systems already on the market before 2 Aug 2026 |
| 2 Dec 2027 | High-risk obligations for Annex III systems |
| 2 Aug 2028 | High-risk obligations for Annex I product systems |

## How a result is reached

1. **Scope first.** If an exclusion in Art. 2 applies, evaluation stops.
2. **Every rule is checked.** A rule fires when its condition is true. Conditions combine answers with `all`, `any` and `not`, and can reuse named facts (for example `$no_exception`).
3. **The most severe tier wins**: prohibited > high > transparency > minimal. Transparency obligations still stack on top of a high-risk result.
4. **Obligations are collected** from every rule that fired, filtered by role, and de-duplicated.

## The Art. 6(3) exception

A system in an Annex III area is not high risk if it only performs a narrow procedural task, improves a completed human activity, detects patterns in past decisions, or does preparatory work. The tool applies this, but:

- if the system **profiles natural persons**, the exception never applies
- the provider still has to **document the assessment** (Art. 6(4)) and **register** the system (Art. 49(2))

## Known simplifications

- Art. 5(1)(h) real-time biometric identification: the narrow authorised exceptions are not modelled. The tool flags it as prohibited and says so.
- Open-source exemptions (Art. 2(12)) are not modelled.
- Annex III point descriptions are shortened. Points 6 and 7 (law enforcement, migration) are grouped rather than split into each sub-point.
- The fundamental rights impact assessment trigger (Art. 27) uses a simplified condition.
- Roles: importers, distributors and authorised representatives are not covered, nor the case where a deployer becomes a provider through substantial modification (Art. 25).
- Sector rules that interact with the AI Act (MDR, financial services, the machinery move to Annex I Section B) are only referenced, not modelled.

These are deliberate scope choices for a screening tool. Each could become its own rule.

## Added after an expert review (v0.2)

- **Prohibited means only the ban.** A prohibited tier shows Art. 5 and the fine, not a compliance checklist for a system that cannot be sold. Set with `exclusive: true` on a tier.
- **Role change (Art. 25).** The question "you rebrand, substantially modify or repurpose a high-risk system" turns a deployer into a provider for that system. The rule sets `makes_provider: true`, and the obligations list uses the effective role.
- **Art. 6(3) is a self-assessment.** The result says so, cites Art. 80 (authority review), and the app asks for a written reason that goes into the report as the Art. 6(4) note.
- **Scope conflicts.** Exclusions (military, research, personal, pre-market) apply to exclusive use only (Recital 24). If you tick one and also describe another use, a `warnings:` entry in the rulebook shows a caution. Warnings never change the tier.
- **Still simplified:** open-source releases, law-enforcement carve-outs, GPAI systemic risk, and sector law. The app lists these under "What this check does not cover".
