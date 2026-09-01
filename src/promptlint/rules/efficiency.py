"""Efficiency analysis rules for AI prompts.

Detects repeated instructions, excessive whitespace, and unnecessarily
large prompts. Helps developers write tighter, more cost-effective prompts.
"""

from __future__ import annotations

import re

from promptlint.models import PromptDocument, RuleResult, Severity


def _normalize_sentence(sentence: str) -> str:
    """Normalize a sentence for comparison: lowercase, strip, collapse spaces."""
    return re.sub(r"\s+", " ", sentence.strip().lower())


def _word_set(sentence: str) -> set[str]:
    """Extract the set of meaningful words from a sentence."""
    words = re.findall(r"\b[a-z]+\b", sentence.lower())
    # Filter out very common words to focus on content words
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "to",
        "of",
        "in",
        "on",
        "at",
        "for",
        "and",
        "or",
        "but",
        "it",
        "its",
        "this",
        "that",
        "with",
        "as",
        "by",
    }
    return {w for w in words if w not in stop_words and len(w) > 1}


def _sentence_similarity(a: str, b: str) -> float:
    """Calculate word-overlap similarity between two sentences (0.0-1.0)."""
    words_a = _word_set(a)
    words_b = _word_set(b)
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


def check_repeated_instructions(doc: PromptDocument) -> list[RuleResult]:
    """EFF001: Detect duplicate or near-duplicate sentences."""
    results: list[RuleResult] = []

    # Split text into sentences (simple heuristic — split on sentence-ending punctuation)
    sentences: list[tuple[int, str]] = []
    for line_idx, line in enumerate(doc.lines, 1):
        stripped = line.strip()
        if not stripped or len(stripped) < 10:
            continue
        # Split line into sentences
        parts = re.split(r"(?<=[.!?])\s+", stripped)
        for part in parts:
            if len(part.strip()) >= 10:  # Skip very short fragments
                sentences.append((line_idx, part.strip()))

    # Compare all sentence pairs
    flagged: set[int] = set()
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            line_i, sent_i = sentences[i]
            line_j, sent_j = sentences[j]

            # Exact match after normalization
            norm_i = _normalize_sentence(sent_i)
            norm_j = _normalize_sentence(sent_j)

            if norm_i == norm_j or _sentence_similarity(sent_i, sent_j) > 0.8:
                if j not in flagged:
                    flagged.add(j)
                    results.append(
                        RuleResult(
                            rule_id="EFF001",
                            category="efficiency",
                            severity=Severity.WARNING,
                            message=(f"Repeated instruction detected on line {line_j} (similar to line {line_i})."),
                            suggestion=(
                                "Remove the duplicate instruction. Repeating instructions "
                                "wastes tokens without improving model performance."
                            ),
                            score_impact=-8,
                            line=line_j,
                        )
                    )

    return results


def check_excessive_whitespace(doc: PromptDocument) -> list[RuleResult]:
    """EFF002: Detect excessive whitespace."""
    results: list[RuleResult] = []

    # Check for 3+ consecutive blank lines
    consecutive_blank = 0
    for i, line in enumerate(doc.lines, 1):
        if line.strip() == "":
            consecutive_blank += 1
            if consecutive_blank == 3:
                results.append(
                    RuleResult(
                        rule_id="EFF002",
                        category="efficiency",
                        severity=Severity.INFO,
                        message=f"Excessive blank lines near line {i}.",
                        suggestion="Use at most 2 consecutive blank lines for readability.",
                        score_impact=-2,
                        line=i,
                    )
                )
        else:
            consecutive_blank = 0

    # Check for significant leading/trailing whitespace in the overall prompt
    if doc.text and (doc.text != doc.text.strip()):
        leading = len(doc.text) - len(doc.text.lstrip())
        trailing = len(doc.text) - len(doc.text.rstrip())
        if leading > 2 or trailing > 2:
            results.append(
                RuleResult(
                    rule_id="EFF002",
                    category="efficiency",
                    severity=Severity.INFO,
                    message="Prompt has significant leading or trailing whitespace.",
                    suggestion="Trim unnecessary whitespace from the start and end of the prompt.",
                    score_impact=-2,
                )
            )

    return results


def check_prompt_length(doc: PromptDocument) -> list[RuleResult]:
    """EFF003: Flag very large prompts."""
    if doc.word_count <= 2000:
        return []

    return [
        RuleResult(
            rule_id="EFF003",
            category="efficiency",
            severity=Severity.INFO,
            message=f"Prompt is very long ({doc.word_count} words).",
            suggestion=(
                "Review the prompt for unnecessary verbosity. Long prompts "
                "increase cost and latency. Consider whether all context is essential."
            ),
            score_impact=-3,
        )
    ]


def check_negative_constraints(doc: PromptDocument) -> list[RuleResult]:
    """EFF004: Detect negative constraint overload (4+ negative instructions)."""
    pattern = re.compile(r"\b(?:do\s+not|don'?t|never|avoid|must\s+not)\b", re.IGNORECASE)
    matches = list(pattern.finditer(doc.text))
    if len(matches) >= 4:
        return [
            RuleResult(
                rule_id="EFF004",
                category="efficiency",
                severity=Severity.WARNING,
                message=f"Negative constraint overload detected ({len(matches)} negative instructions).",
                suggestion=(
                    "LLMs process positive instructions much better than negative ones. "
                    "Reframe 'do not do X' into positive specifications of what TO do instead."
                ),
                score_impact=-10,
                line=_word_set(doc.text) and 1 or 1,
            )
        ]
    return []


def analyze_efficiency(document: PromptDocument) -> list[RuleResult]:
    """Run all efficiency analysis rules on a prompt document."""
    results: list[RuleResult] = []
    results.extend(check_repeated_instructions(document))
    results.extend(check_excessive_whitespace(document))
    results.extend(check_prompt_length(document))
    results.extend(check_negative_constraints(document))
    return results
