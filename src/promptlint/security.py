"""Security analysis engine for PromptLint.

Detects potential secrets (API keys, tokens, passwords) and prompt injection
patterns entirely offline. NEVER transmits prompt content to external servers.

This module is the core engine. The rules/security.py wrapper converts
findings into RuleResult objects for the lint pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityFinding:
    """A single security finding from the offline scanner."""

    pattern_type: str  # "secret" or "injection"
    description: str
    line: int
    match_preview: str  # Redacted: first 4 chars + "****"


def _redact(text: str) -> str:
    """Redact a matched string, showing only the first 4 characters."""
    if len(text) <= 4:
        return text[:2] + "****"
    return text[:4] + "****"


def _find_line(text: str, pos: int) -> int:
    """Return 1-based line number for a character position."""
    return text[:pos].count("\n") + 1


# --- Secret detection patterns ---

_SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub Token", re.compile(r"gh[ps]_[a-zA-Z0-9]{36}")),
    ("GitHub OAuth Token", re.compile(r"gho_[a-zA-Z0-9]{36}")),
    ("GitHub App Token", re.compile(r"ghr_[a-zA-Z0-9]{36}")),
    ("GitHub PAT", re.compile(r"github_pat_[a-zA-Z0-9_]{22,}")),
    (
        "Private Key",
        re.compile(r"-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----"),
    ),
    ("JWT", re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}")),
    ("Slack Token", re.compile(r"xox[bpors]-[a-zA-Z0-9]{10,}")),
    (
        "Password Assignment",
        re.compile(
            r"""(?:password|passwd|pwd)\s*[=:]\s*["'][^"']{4,}["']""",
            re.IGNORECASE,
        ),
    ),
    (
        "API Key Assignment",
        re.compile(
            r"""(?:api[_-]?key|apikey|api[_-]?secret|access[_-]?key|secret[_-]?key|auth[_-]?token)\s*[=:]\s*["'][a-zA-Z0-9+/=_-]{16,}["']""",
            re.IGNORECASE,
        ),
    ),
    (
        "Generic Token Assignment",
        re.compile(
            r"""(?:token|secret|credential)\s*[=:]\s*["'][a-zA-Z0-9+/=_-]{20,}["']""",
            re.IGNORECASE,
        ),
    ),
    (
        "AWS Secret Key",
        re.compile(
            r"""(?:aws[_-]?secret|secret[_-]?access[_-]?key)\s*[=:]\s*["']?[a-zA-Z0-9+/=]{40}["']?""",
            re.IGNORECASE,
        ),
    ),
]


def detect_secrets(text: str) -> list[SecurityFinding]:
    """Scan text for potential secrets. All analysis is local."""
    findings: list[SecurityFinding] = []

    for description, pattern in _SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                SecurityFinding(
                    pattern_type="secret",
                    description=f"Possible {description}",
                    line=_find_line(text, match.start()),
                    match_preview=_redact(match.group()),
                )
            )

    return findings


# --- Prompt injection detection patterns ---

_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "Ignore instructions",
        re.compile(
            r"ignore\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+instructions?",
            re.IGNORECASE,
        ),
    ),
    (
        "Disregard instructions",
        re.compile(
            r"disregard\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+(?:instructions?|rules?|guidelines?)",
            re.IGNORECASE,
        ),
    ),
    (
        "Forget instructions",
        re.compile(
            r"forget\s+(?:all\s+|everything\s+|your\s+)?(?:previous|above|prior)\s+(?:instructions?|rules?)?",
            re.IGNORECASE,
        ),
    ),
    (
        "Reveal system prompt",
        re.compile(
            r"reveal\s+(?:your\s+|the\s+)?(?:system\s+)?(?:prompt|instructions?)",
            re.IGNORECASE,
        ),
    ),
    (
        "Bypass safety",
        re.compile(
            r"bypass\s+(?:safety|security|content)\s+(?:instructions?|filters?|policies|guidelines?|restrictions?)",
            re.IGNORECASE,
        ),
    ),
    (
        "Reveal hidden instructions",
        re.compile(
            r"reveal\s+(?:hidden|secret)\s+(?:instructions?|rules?|prompt)",
            re.IGNORECASE,
        ),
    ),
    (
        "Override instructions",
        re.compile(
            r"override\s+(?:your\s+|all\s+)?(?:instructions?|rules?|guidelines?|restrictions?)",
            re.IGNORECASE,
        ),
    ),
    (
        "Jailbreak attempt",
        re.compile(
            r"(?:you\s+are\s+now\s+in|act\s+as\s+if\s+you\s+have\s+no\s+restrictions?)",
            re.IGNORECASE,
        ),
    ),
    (
        "Pretend no restrictions",
        re.compile(
            r"pretend\s+(?:you\s+)?(?:have\s+no|don'?t\s+have\s+(?:any\s+)?)\s*(?:restrictions?|limits?|rules?|guidelines?)",
            re.IGNORECASE,
        ),
    ),
]


def detect_injection_patterns(text: str) -> list[SecurityFinding]:
    """Scan text for potential prompt injection patterns. All analysis is local."""
    findings: list[SecurityFinding] = []

    for description, pattern in _INJECTION_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                SecurityFinding(
                    pattern_type="injection",
                    description=f"Potential prompt injection: {description}",
                    line=_find_line(text, match.start()),
                    match_preview=_redact(match.group()),
                )
            )

    return findings
