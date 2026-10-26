"""riskcheck: a transparent, rule-based compliance screening engine."""

from .engine import Obligation, Result, Rule, Rulebook, RulebookError, Tier, evaluate
from .report import to_markdown

__all__ = [
    "Obligation",
    "Result",
    "Rule",
    "Rulebook",
    "RulebookError",
    "Tier",
    "evaluate",
    "to_markdown",
]
__version__ = "0.1.0"
