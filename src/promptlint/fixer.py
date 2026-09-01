"""Deterministic prompt fixer.

Improves obvious structural issues without using an LLM. The fixer
preserves the user's original intent and never silently invents major
requirements. All transformations are rule-based and predictable.
"""

from __future__ import annotations

import re

from promptlint.analyzer import analyze_prompt
from promptlint.parser import parse_prompt


def fix_prompt(text: str) -> str:
    """Apply deterministic improvements to a prompt.

    Improvements:
        1. Normalize excessive whitespace.
        2. Add a "Task:" header if no clear structure exists.
        3. Add a "Requirements:" section with extracted implicit requirements.
        4. Add an "Output format:" section with suggested structure.

    The fixer is conservative — it adds structure but does not change
    the user's actual instructions or intent.

    Args:
        text: Raw prompt text.

    Returns:
        Improved prompt text.
    """
    if not text or not text.strip():
        return text

    # Step 1: Normalize whitespace
    fixed = _normalize_whitespace(text.strip())

    # Run analysis to determine what's missing
    doc = parse_prompt(fixed)
    report = analyze_prompt(doc)
    rule_ids = {r.rule_id for r in report.results}

    # Step 2: If the prompt is very short and lacks structure, add it
    has_structure = _has_section_headers(fixed)

    if not has_structure and doc.word_count >= 3:
        fixed = _add_structure(fixed, rule_ids)

    return fixed


def _normalize_whitespace(text: str) -> str:
    """Remove excessive whitespace while preserving intentional formatting."""
    # Collapse 3+ consecutive blank lines to 2
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines)


def _has_section_headers(text: str) -> bool:
    """Check if the text already has section-like structure."""
    # Look for patterns like "Task:", "## Section", "1.", "- Item"
    header_patterns = [
        r"^(?:task|objective|goal|context|requirements?|instructions?|output|format|constraints?)\s*:",
        r"^#{1,3}\s+\w",
        r"^\d+\.\s+\w",
    ]
    for pattern in header_patterns:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            return True
    return False


def _add_structure(text: str, rule_ids: set[str]) -> str:
    """Add structural sections to an unstructured prompt."""
    parts: list[str] = []

    # Extract the core instruction
    core = text.strip()

    # Add Task header
    parts.append("Task:")
    parts.append(core)

    # Add Requirements section if the prompt is substantial
    words = core.split()
    if len(words) >= 5:
        parts.append("")
        parts.append("Requirements:")
        parts.append("- Accomplish the task clearly and accurately.")
        parts.append("- Provide concrete, specific information.")

        # If the task involves explanation, add explanation-specific requirements
        explain_verbs = {"explain", "describe", "summarize", "outline", "define"}
        if any(v in core.lower() for v in explain_verbs):
            parts.append("- Include relevant examples where useful.")

    # Add Output format section if missing (STRUCT002)
    if "STRUCT002" in rule_ids:
        parts.append("")
        parts.append("Output format:")

        # Suggest appropriate format based on content
        if any(w in core.lower() for w in ["list", "compare", "differences", "pros", "cons"]):
            parts.append("- Use a structured list or table.")
        elif any(w in core.lower() for w in ["explain", "describe", "what is"]):
            parts.append("- Brief summary (1-2 sentences)")
            parts.append("- Detailed explanation")
            parts.append("- Key takeaways")
        else:
            parts.append("- Structured response with clear sections.")

    return "\n".join(parts)
