"""Analysis orchestrator.

Ties together parsing, rules, and scoring into a single analyze_prompt()
function. This is the core pipeline: Document → Rules → Score → Report.
"""

from __future__ import annotations

from promptlint.models import AnalysisReport, PromptDocument, SecurityStatus
from promptlint.rules import run_all_rules
from promptlint.scoring import calculate_score


def analyze_prompt(document: PromptDocument, use_ai: bool = False) -> AnalysisReport:
    """Run the full analysis pipeline on a parsed prompt document.

    Steps:
        1. Execute all rules against the document.
        2. Calculate scores and statistics.
        3. Determine security status.
        4. Assemble and return the AnalysisReport.

    Args:
        document: A parsed PromptDocument.
        use_ai: Whether to run semantic AI rules (requires litellm).

    Returns:
        A complete AnalysisReport.
    """
    # Step 1: Run all rules
    results = run_all_rules(document)

    if use_ai:
        try:
            from promptlint.rules.ai import analyze_with_ai

            ai_results = analyze_with_ai(document)
            results.extend(ai_results)
        except ImportError:
            pass

    # Step 2: Calculate scores
    score, rating, category_scores, statistics = calculate_score(results, document)

    # Step 3: Determine security status
    security_results = [r for r in results if r.category == "security"]
    security_status = SecurityStatus(
        has_secrets=any(r.rule_id == "SEC001" for r in security_results),
        has_injection=any(r.rule_id == "SEC002" for r in security_results),
        finding_count=len(security_results),
    )

    # Step 4: Assemble report
    return AnalysisReport(
        score=score,
        rating=rating,
        results=results,
        category_scores=category_scores,
        statistics=statistics,
        security_status=security_status,
    )
