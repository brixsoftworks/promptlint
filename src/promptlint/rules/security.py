"""Security rules wrapper for the lint pipeline.

Thin layer that converts SecurityFinding objects from the core security
engine into RuleResult objects that the analyzer and scorer understand.
"""

from __future__ import annotations

import re

from promptlint.models import PromptDocument, RuleResult, Severity
from promptlint.security import detect_injection_patterns, detect_secrets


def _check_untrusted_content(doc: PromptDocument) -> list[RuleResult]:
    """SEC003: Detect user input placeholders mixed with system instructions.

    Flags patterns like {{input}}, {user_input}, {USER_MESSAGE}, etc.
    that appear without clear separation from system-level instructions.
    """
    results: list[RuleResult] = []

    # Patterns for user input placeholders
    placeholder_pattern = re.compile(
        r"\{\{?\s*(?:user[_\s]?(?:input|message|query|prompt|text)|input|message|query)\s*\}?\}",
        re.IGNORECASE,
    )

    for match in placeholder_pattern.finditer(doc.text):
        line = doc.text[:match.start()].count("\n") + 1
        placeholder = match.group()

        results.append(
            RuleResult(
                rule_id="SEC003",
                category="security",
                severity=Severity.WARNING,
                message=f"User input placeholder '{placeholder}' found in prompt.",
                suggestion=(
                    "Separate user input from system instructions using clear delimiters "
                    "(e.g., XML tags, triple quotes, or section headers) to reduce "
                    "prompt injection risk."
                ),
                score_impact=-10,
                line=line,
            )
        )

    return results


def analyze_security(document: PromptDocument) -> list[RuleResult]:
    """Run all security analysis rules on a prompt document."""
    results: list[RuleResult] = []

    # SEC001: Secrets
    for finding in detect_secrets(document.text):
        results.append(
            RuleResult(
                rule_id="SEC001",
                category="security",
                severity=Severity.CRITICAL,
                message=f"{finding.description} ({finding.match_preview}).",
                suggestion=(
                    "Remove the credential from the prompt. Use environment variables "
                    "or a secrets manager instead. Never include secrets in prompts."
                ),
                score_impact=-25,
                line=finding.line,
            )
        )

    # SEC002: Injection patterns
    for finding in detect_injection_patterns(document.text):
        results.append(
            RuleResult(
                rule_id="SEC002",
                category="security",
                severity=Severity.ERROR,
                message=f"{finding.description} ({finding.match_preview}).",
                suggestion=(
                    "Review this pattern carefully. If this is a legitimate test or "
                    "security exercise, consider documenting it. If unintentional, "
                    "remove the injection-like language."
                ),
                score_impact=-15,
                line=finding.line,
            )
        )

    # SEC003: Untrusted content mixing
    results.extend(_check_untrusted_content(document))

    return results
