"""AI-powered semantic linting rules.

These rules use an LLM to evaluate the prompt for logical flaws,
hallucination risks, and edge-case handling that regex cannot catch.
"""

from __future__ import annotations

from promptlint.llm import evaluate_prompt, is_llm_available
from promptlint.models import PromptDocument, RuleResult, Severity


def analyze_with_ai(document: PromptDocument) -> list[RuleResult]:
    """Run semantic AI analysis on the prompt.

    Args:
        document: The parsed prompt document.

    Returns:
        List of findings from the LLM evaluator.
    """
    if not is_llm_available():
        return []

    # If the prompt is too short, the LLM won't have enough context
    if document.word_count < 10:
        return []

    system_prompt = """You are an expert AI prompt engineer and linter.
Analyze the user's prompt and identify logical flaws, missing context, hallucination risks, or edge cases.
Do NOT flag formatting issues or structural issues (like missing headers). Focus purely on the semantic logic and reasoning.

If the prompt is good and has no major logical flaws, return an empty array for 'issues'.

Output JSON strictly matching this schema:
{
  "issues": [
    {
      "rule_id": "AI001", // Or AI002 for tone, AI003 for edge cases
      "severity": "WARNING", // Or INFO, ERROR
      "message": "A concise description of the logical flaw.",
      "suggestion": "How to fix it.",
      "score_impact": -5 // Integer between -1 and -20
    }
  ]
}
"""

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "lint_results",
            "schema": {
                "type": "object",
                "properties": {
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "rule_id": {"type": "string"},
                                "severity": {
                                    "type": "string",
                                    "enum": ["INFO", "WARNING", "ERROR", "CRITICAL"],
                                },
                                "message": {"type": "string"},
                                "suggestion": {"type": "string"},
                                "score_impact": {"type": "integer"},
                            },
                            "required": [
                                "rule_id",
                                "severity",
                                "message",
                                "suggestion",
                                "score_impact",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["issues"],
                "additionalProperties": False,
            },
        },
    }

    try:
        result_json = evaluate_prompt(
            prompt_text=document.text,
            system_prompt=system_prompt,
            response_format=response_format,
        )

        results: list[RuleResult] = []
        for issue in result_json.get("issues", []):
            try:
                severity = Severity[issue["severity"].upper()]
            except KeyError:
                severity = Severity.WARNING

            results.append(
                RuleResult(
                    rule_id=issue["rule_id"],
                    category="ai_semantic",
                    severity=severity,
                    message=f"[AI] {issue['message']}",
                    suggestion=issue["suggestion"],
                    score_impact=issue["score_impact"],
                )
            )
        return results

    except Exception:
        # If the LLM fails, we gracefully degrade and return no AI findings.
        return []
