"""
Ambiguity rules for PromptLint.

Detects vague quantities, subjective requirements, and potentially unclear references
to ensure AI prompts are precise and actionable. Precision is prioritized to avoid
aggressive false positives.
"""

import re

from promptlint.models import PromptDocument, RuleResult, Severity

# AMB001 - Vague Quantities
VAGUE_QUANTITIES = [
    r"a few", r"some", r"many", r"several", r"a lot of", r"a couple of",
    r"various", r"numerous", r"a number of"
]

INSTRUCTION_VERBS = [
    r"provide", r"include", r"add", r"give", r"create", r"list", r"write"
]

# Compile regexes for AMB001 and AMB002
_VAGUE_QUANTITY_PATTERN = re.compile(r"\b(" + "|".join(VAGUE_QUANTITIES) + r")\b", re.IGNORECASE)
_INSTRUCTION_VERB_PATTERN = re.compile(r"\b(" + "|".join(INSTRUCTION_VERBS) + r")\b", re.IGNORECASE)

def _check_amb001_vague_quantities(document: PromptDocument) -> list[RuleResult]:
    """
    AMB001: Detect vague quantity words used in requirements/instructions context.
    """
    results = []
    for i, line in enumerate(document.lines):
        # We only flag if there's an instructional verb in the same line
        if not _INSTRUCTION_VERB_PATTERN.search(line):
            continue

        for match in _VAGUE_QUANTITY_PATTERN.finditer(line):
            vague_word = match.group(1).lower()
            results.append(
                RuleResult(
                    rule_id="AMB001",
                    category="ambiguity",
                    severity=Severity.WARNING,
                    message=f"Vague quantity '{vague_word}' used in an instructional context.",
                    suggestion=f"Specify an exact number instead of '{vague_word}'.",
                    score_impact=-5,
                    line=i + 1,
                    column=match.start() + 1
                )
            )
    return results


# AMB002 - Subjective Quality
SUBJECTIVE_TERMS = [
    r"high quality", r"well-written", r"professional", r"elegant",
    r"clean", r"beautiful", r"nice", r"appropriate", r"suitable",
    r"relevant", r"comprehensive", r"thorough"
]

_SUBJECTIVE_PATTERN = re.compile(r"\b(" + "|".join(SUBJECTIVE_TERMS) + r")\b", re.IGNORECASE)

def _check_amb002_subjective_quality(document: PromptDocument) -> list[RuleResult]:
    """
    AMB002: Detect subjective quality terms without measurable criteria in instructions.
    """
    results = []
    for i, line in enumerate(document.lines):
        # Check if line seems to be an instruction
        if not _INSTRUCTION_VERB_PATTERN.search(line):
            continue

        for match in _SUBJECTIVE_PATTERN.finditer(line):
            term = match.group(1).lower()
            results.append(
                RuleResult(
                    rule_id="AMB002",
                    category="ambiguity",
                    severity=Severity.INFO,
                    message=f"Subjective quality requirement '{term}'.",
                    suggestion=f"Replace '{term}' with measurable criteria or specific examples.",
                    score_impact=-3,
                    line=i + 1,
                    column=match.start() + 1
                )
            )
    return results


# AMB003 - Undefined References
def _check_amb003_undefined_references(document: PromptDocument) -> list[RuleResult]:
    """
    AMB003: Detect undefined references at the start of sentences where antecedent is unclear.
    We flag when they appear at the start of a paragraph or document, as previous context is definitely missing.
    """
    results = []

    for i, line in enumerate(document.lines):
        is_first_line = (i == 0)
        is_start_of_paragraph = is_first_line or not document.lines[i-1].strip()

        # We only flag if the sentence start is at the beginning of a paragraph
        # to avoid false positives in continuous text where antecedent is likely present.
        if is_start_of_paragraph:
            match = re.match(r"^\s*(it|this|that|they|them)\b", line, re.IGNORECASE)
            if match:
                term = match.group(1).lower()
                results.append(
                    RuleResult(
                        rule_id="AMB003",
                        category="ambiguity",
                        severity=Severity.INFO,
                        message=f"Unclear reference '{term}' at the start of a paragraph.",
                        suggestion=f"Clarify what '{term}' refers to for a more precise instruction.",
                        score_impact=-3,
                        line=i + 1,
                        column=match.start(1) + 1
                    )
                )
    return results


def analyze_ambiguity(document: PromptDocument) -> list[RuleResult]:
    """
    Run all ambiguity detection rules on the given document.
    """
    return [
        *_check_amb001_vague_quantities(document),
        *_check_amb002_subjective_quality(document),
        *_check_amb003_undefined_references(document)
    ]
