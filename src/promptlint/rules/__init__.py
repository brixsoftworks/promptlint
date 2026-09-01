"""Rule engine registry.

Aggregates all rule category analyzers into a single entry point.
The analyzer module calls run_all_rules() to execute every rule
against a prompt document.
"""

from __future__ import annotations

from promptlint.models import PromptDocument, RuleResult
from promptlint.rules.ambiguity import analyze_ambiguity
from promptlint.rules.clarity import analyze_clarity
from promptlint.rules.conflicts import analyze_conflicts
from promptlint.rules.efficiency import analyze_efficiency
from promptlint.rules.security import analyze_security
from promptlint.rules.structure import analyze_structure

# Ordered list of all rule analyzers. Each takes a PromptDocument and
# returns list[RuleResult]. New categories are added here.
_ANALYZERS = [
    analyze_structure,
    analyze_clarity,
    analyze_ambiguity,
    analyze_conflicts,
    analyze_efficiency,
    analyze_security,
]


def run_all_rules(document: PromptDocument) -> list[RuleResult]:
    """Execute all registered rule analyzers against a document.

    Args:
        document: The parsed prompt to analyze.

    Returns:
        Combined list of all rule findings, in category order.
    """
    results: list[RuleResult] = []
    for analyzer in _ANALYZERS:
        results.extend(analyzer(document))
    return results
