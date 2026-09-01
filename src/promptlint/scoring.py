"""Scoring engine for PromptLint.

Computes an overall PromptLint Quality Score and per-category scores
from rule results. The score is a heuristic developer-assistance metric,
not a scientifically objective measurement of prompt quality.
"""

from __future__ import annotations

import math

from promptlint.models import (
    CategoryScore,
    PromptDocument,
    PromptStatistics,
    RuleResult,
)

# Display names for rule categories. Keys are the lowercase category strings
# used in RuleResult.category.
_CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    "structure": "Structure",
    "clarity": "Clarity",
    "ambiguity": "Ambiguity",
    "efficiency": "Efficiency",
    "security": "Security",
    "conflicts": "Conflicts",
}

# All categories that receive a score, in display order.
_SCORED_CATEGORIES = ["structure", "clarity", "ambiguity", "conflicts", "efficiency", "security"]


def get_rating(score: int) -> str:
    """Convert a numeric score (0-100) to a human-readable rating."""
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Fair"
    if score >= 40:
        return "Needs Work"
    return "Poor"


def _estimate_tokens(word_count: int) -> int:
    """Estimate token count from word count.

    Uses ~1.3 tokens per word for English text. This is a rough heuristic —
    exact counts require a model-specific tokenizer (e.g., tiktoken for GPT,
    SentencePiece for others).
    """
    return math.ceil(word_count * 1.3)


def calculate_score(
    results: list[RuleResult],
    document: PromptDocument,
) -> tuple[int, str, list[CategoryScore], PromptStatistics]:
    """Calculate overall score, rating, category scores, and statistics.

    Args:
        results: All rule findings from analysis.
        document: The parsed prompt document.

    Returns:
        Tuple of (score, rating, category_scores, statistics).
    """
    # --- Overall score ---
    total_deduction = sum(r.effective_score_impact() for r in results)
    overall_score = max(0, min(100, 100 + total_deduction))

    # --- Per-category scores ---
    category_scores: list[CategoryScore] = []
    for cat_key in _SCORED_CATEGORIES:
        cat_results = [r for r in results if r.category == cat_key]
        cat_deduction = sum(r.effective_score_impact() for r in cat_results)
        cat_score = max(0, min(100, 100 + cat_deduction))
        display_name = _CATEGORY_DISPLAY_NAMES.get(cat_key, cat_key.title())
        category_scores.append(CategoryScore(name=display_name, score=cat_score))

    # --- Rating ---
    rating = get_rating(overall_score)

    # --- Statistics ---
    statistics = PromptStatistics(
        character_count=document.character_count,
        word_count=document.word_count,
        line_count=document.line_count,
        estimated_tokens=_estimate_tokens(document.word_count),
    )

    return overall_score, rating, category_scores, statistics
