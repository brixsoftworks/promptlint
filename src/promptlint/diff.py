"""Prompt diff engine.

Compares two prompts by running analysis on both and computing
score deltas and diagnostic changes. Uses difflib for text diffs.
"""

from __future__ import annotations

from dataclasses import dataclass

from promptlint.analyzer import analyze_prompt
from promptlint.models import AnalysisReport
from promptlint.parser import parse_prompt


@dataclass
class DiffResult:
    """Result of comparing two prompts."""

    old_report: AnalysisReport
    new_report: AnalysisReport
    score_delta: int
    old_name: str
    new_name: str


def diff_prompts(
    old_text: str,
    new_text: str,
    old_name: str = "old",
    new_name: str = "new",
) -> DiffResult:
    """Compare two prompts and return analysis diff.

    Args:
        old_text: The original prompt text.
        new_text: The updated prompt text.
        old_name: Display name for the original (e.g., filename).
        new_name: Display name for the updated.

    Returns:
        A DiffResult with both reports and the score delta.
    """
    old_doc = parse_prompt(old_text)
    new_doc = parse_prompt(new_text)

    old_report = analyze_prompt(old_doc)
    new_report = analyze_prompt(new_doc)

    return DiffResult(
        old_report=old_report,
        new_report=new_report,
        score_delta=new_report.score - old_report.score,
        old_name=old_name,
        new_name=new_name,
    )
