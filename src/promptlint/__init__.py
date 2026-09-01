"""PromptLint — The developer toolkit for AI prompts.

Write prompts. Lint them. Test them. Ship them.

PromptLint analyzes AI prompts and identifies structural problems, ambiguity,
missing constraints, conflicting instructions, possible secrets, and other
prompt-quality issues. It works completely offline — no API keys required.
"""

__version__ = "1.0.0"

from promptlint.analyzer import analyze_prompt
from promptlint.models import AnalysisReport, PromptDocument
from promptlint.parser import parse_prompt


def analyze(text: str) -> AnalysisReport:
    """Analyze an AI prompt and return a full quality report.

    This is the primary public API. It parses the prompt, runs all rules,
    computes scores, and returns a structured report.

    Args:
        text: The raw prompt text to analyze.

    Returns:
        An AnalysisReport with scores, diagnostics, and suggestions.
    """
    document = parse_prompt(text)
    return analyze_prompt(document)


# Alias for convenience
lint = analyze

__all__ = [
    "__version__",
    "analyze",
    "lint",
    "parse_prompt",
    "analyze_prompt",
    "PromptDocument",
    "AnalysisReport",
]
