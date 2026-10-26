# EU AI Act Risk Check

[![tests](https://github.com/gifmaster/ai-act-risk-check/actions/workflows/tests.yml/badge.svg)](https://github.com/gifmaster/ai-act-risk-check/actions/workflows/tests.yml)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-act-risk-check.streamlit.app)

**Find out where an AI system sits under the EU AI Act, and see exactly why.**

Answer a set of yes/no questions about an AI system. The tool tells you its risk tier (prohibited, high risk, transparency, minimal or out of scope), the article behind every conclusion, and a checklist of what you need to do as a provider or deployer.

Up to date with the **Digital Omnibus on AI** (Regulation (EU) 2026/1744), including the new high-risk dates and the two new prohibitions.

![Screenshot: a CV screening tool classified as high risk](docs/screenshot.png)

**[Try it live](https://ai-act-risk-check.streamlit.app)**

---

## Why rules, not an LLM

A compliance tool that cannot explain its own answer undermines the very thing it is checking for.

So the classification is done by **transparent rules**, not by a language model guessing. The rules live in one readable file ([`eu_ai_act.yaml`](src/riskcheck/rulebooks/eu_ai_act.yaml)), and each one looks like this:

```yaml
- id: high.employment
  when: {all: [a3_employment, $no_exception]}
  tier: high
  cite: Art. 6(2), Annex III point 4
  applies_from: "2027-12-02"
  reason: AI used in recruitment or decisions about workers is high risk.
```

That means:

- **Same answers, same result.** Every time.
- **Every result is traceable** to a rule and an article.
- **A lawyer can review the logic** without reading Python.
- **The rules are tested.** Real cases (CV screening, credit scoring, chatbots, deepfakes) are pinned down in [`tests/test_scenarios.py`](tests/test_scenarios.py), so a change that breaks the law's logic fails the build.

## What it covers

| Area | Articles |
|---|---|
| Scope exclusions (military, research, personal use, pre-market) | Art. 2 |
| Prohibited practices, incl. the two added in 2026 | Art. 5 |
| High risk through regulated products | Art. 6(1), Annex I |
| High risk through use area (HR, credit, education, insurance ...) | Art. 6(2), Annex III |
| The "not high risk after all" exception, and why profiling cancels it | Art. 6(3)-(4) |
| Provider and deployer obligations, incl. fundamental rights impact assessment | Arts. 9-17, 26, 27, 43-49, 72-73, 86 |
| Transparency for chatbots, generated content and deepfakes | Art. 50 |
| General-purpose AI model providers | Arts. 53, 55 |
| AI literacy | Art. 4 |

Results can be downloaded as a Markdown report with a checklist, ready to drop into an AI register or a ticket.

## How it works

```mermaid
flowchart LR
    Q[Yes/no answers] --> E[Rules engine]
    R[(Rulebook YAML)] --> E
    E --> T[Risk tier]
    E --> W[Why: rule + article]
    E --> O[Obligations by role]
    T & W & O --> M[Markdown report]
```

The engine (`src/riskcheck/engine.py`) knows nothing about the AI Act. It reads a rulebook, checks it for mistakes (unknown questions, missing citations, duplicate rules), and evaluates it. **Swap the rulebook and the same engine screens a different regulation.** A DORA rulebook is next.

## Run it locally

```bash
git clone https://github.com/gifmaster/ai-act-risk-check.git
cd ai-act-risk-check
pip install -r requirements.txt
streamlit run app.py
```

Or use the engine from Python:

```python
from riskcheck import Rulebook, evaluate

rb = Rulebook.builtin("eu_ai_act")
result = evaluate(rb, {"a3_credit": True}, role="deployer")

print(result.tier.label)                 # High risk
for rule in result.reasons:
    print(rule.cite, "-", rule.reason)
```

## Tests

```bash
pip install pytest
pytest
```

The suite covers the engine, rulebook validation, about 20 real-world scenarios, and a smoke test of the app itself.

## Project structure

```
app.py                              Streamlit interface
src/riskcheck/engine.py             Generic rules engine + validation
src/riskcheck/report.py             Markdown report
src/riskcheck/rulebooks/eu_ai_act.yaml   The EU AI Act, as rules
tests/                              Engine, scenario and app tests
docs/METHOD.md                      How the rules were built and their limits
```

## Limitations

This is a **screening tool, not legal advice**. It simplifies some provisions (for example the narrow law-enforcement exceptions in Art. 5(1)(h) and the open-source exemptions) and relies on honest answers. See [docs/METHOD.md](docs/METHOD.md) for the full list. Confirm any high-risk or prohibited result with a qualified lawyer.

## Roadmap

- [ ] Optional LLM helper that reads a plain-text description and pre-fills the answers (the rules still decide)
- [ ] Danish language version
- [ ] DORA readiness rulebook on the same engine
- [ ] Export results straight into an AI use case register

## About

Built by **Alexander Senderovitz**, AI governance and digital transformation, Copenhagen.
I help organisations put the EU AI Act into practice. [alexander@senderovitz.eu](mailto:alexander@senderovitz.eu)

Licensed under the MIT License.
