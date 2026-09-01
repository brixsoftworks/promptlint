"""Conflict detection rules for AI prompts.

Detects obviously contradictory instruction pairs using a curated list of
known contradiction patterns. All findings are labeled as "Potential conflict"
rather than claiming certainty — deterministic heuristic, not semantic analysis.
"""

from __future__ import annotations

import re

from promptlint.models import PromptDocument, RuleResult, Severity

# Each entry is (side_a_patterns, side_b_patterns, description).
# Both sides must match for a conflict to be reported.
_CONTRADICTION_PAIRS: list[tuple[list[str], list[str], str]] = [
    # Conciseness vs Detail
    (
        [r"\bbe\s+(?:concise|brief|short)\b", r"\bkeep\s+it\s+short\b", r"\bbriefly\b"],
        [
            r"\b(?:provide|give|write)\s+(?:a\s+)?(?:detailed|comprehensive|thorough|extensive|in-depth)\b",
            r"\belaborate\s+on\s+(?:every|each|all)\b",
            r"\bgo\s+into\s+(?:great\s+)?detail\b",
        ],
        "Conciseness vs detail",
    ),
    # Bullet points
    (
        [
            r"\b(?:do\s+not|don'?t|avoid)\s+(?:use\s+)?bullet\s*points?\b",
            r"\bno\s+bullet\s*points?\b",
        ],
        [r"\buse\s+bullet\s*points?\b", r"\bbullet(?:ed)?\s+list\b"],
        "Bullet point usage",
    ),
    # Lists
    (
        [r"\b(?:do\s+not|don'?t|avoid)\s+(?:use\s+)?lists?\b", r"\bno\s+lists?\b"],
        [r"\buse\s+(?:a\s+)?(?:numbered\s+)?lists?\b", r"\bnumbered\s+list\b"],
        "List usage",
    ),
    # Markdown/formatting
    (
        [
            r"\bno\s+(?:markdown|formatting)\b",
            r"\b(?:do\s+not|don'?t)\s+use\s+(?:markdown|formatting)\b",
        ],
        [r"\buse\s+(?:markdown|formatting)\b", r"\bformat\s+(?:in|with|using)\s+markdown\b"],
        "Markdown/formatting usage",
    ),
    # Formal vs casual tone
    (
        [r"\bbe\s+formal\b", r"\bformal\s+tone\b", r"\buse\s+formal\b"],
        [
            r"\bbe\s+(?:casual|informal|conversational)\b",
            r"\b(?:casual|informal|conversational)\s+tone\b",
        ],
        "Tone: formal vs casual",
    ),
    # Technical vs simple language
    (
        [
            r"\buse\s+(?:technical|specialized|expert)\s+language\b",
            r"\btechnical\s+(?:terms|vocabulary|jargon)\b",
        ],
        [
            r"\buse\s+(?:simple|plain|easy|basic)\s+language\b",
            r"\bavoid\s+(?:technical|specialized)\s+(?:language|terms|jargon)\b",
        ],
        "Language complexity: technical vs simple",
    ),
    # Examples
    (
        [
            r"\b(?:do\s+not|don'?t|avoid)\s+(?:include|provide|use|give)\s+examples?\b",
            r"\bno\s+examples?\b",
        ],
        [r"\b(?:include|provide|use|give)\s+examples?\b"],
        "Example inclusion",
    ),
    # Opinions
    (
        [
            r"\b(?:avoid|no)\s+(?:personal\s+)?opinions?\b",
            r"\b(?:do\s+not|don'?t)\s+(?:give|express|share|include)\s+(?:your\s+)?opinions?\b",
        ],
        [r"\b(?:give|express|share|include)\s+(?:your\s+)?opinions?\b"],
        "Opinion inclusion",
    ),
    # Questions
    (
        [
            r"\b(?:do\s+not|don'?t)\s+ask\s+(?:any\s+)?questions?\b",
            r"\bno\s+(?:follow-?up\s+)?questions?\b",
        ],
        [r"\bask\s+(?:clarifying|follow-?up)\s+questions?\b"],
        "Question asking",
    ),
    # Paragraphs vs lists
    (
        [r"\bwrite\s+in\s+paragraphs?\s+only\b", r"\bparagraph\s+form\s+only\b"],
        [r"\buse\s+(?:a\s+)?(?:numbered|bulleted)\s+list\b"],
        "Format: paragraphs vs lists",
    ),
]


def check_contradictions(doc: PromptDocument) -> list[RuleResult]:
    """CONF001: Detect potentially contradictory instructions."""
    results: list[RuleResult] = []
    lower_text = doc.text.lower()

    for side_a_patterns, side_b_patterns, description in _CONTRADICTION_PAIRS:
        match_a = None
        match_b = None

        for pattern in side_a_patterns:
            match_a = re.search(pattern, lower_text)
            if match_a:
                break

        if not match_a:
            continue

        for pattern in side_b_patterns:
            match_b = re.search(pattern, lower_text)
            if match_b:
                break

        if not match_b:
            continue

        # Both sides matched — report the conflict
        text_a = doc.text[match_a.start() : match_a.end()]
        text_b = doc.text[match_b.start() : match_b.end()]
        line_a = doc.text[: match_a.start()].count("\n") + 1
        line_b = doc.text[: match_b.start()].count("\n") + 1

        results.append(
            RuleResult(
                rule_id="CONF001",
                category="conflicts",
                severity=Severity.WARNING,
                message=(
                    f"Potential conflict ({description}): '{text_a}' (line {line_a}) vs '{text_b}' (line {line_b})."
                ),
                suggestion=(
                    "Review these instructions and remove or reconcile the contradiction. "
                    "Conflicting instructions may confuse the model."
                ),
                score_impact=-15,
                line=line_a,
            )
        )

    return results


def analyze_conflicts(document: PromptDocument) -> list[RuleResult]:
    """Run all conflict detection rules on a prompt document."""
    return check_contradictions(document)
