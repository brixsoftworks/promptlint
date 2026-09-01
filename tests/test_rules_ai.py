from unittest.mock import patch

from promptlint.parser import parse_prompt
from promptlint.rules.ai import analyze_with_ai


@patch("promptlint.rules.ai.is_llm_available", return_value=True)
@patch("promptlint.rules.ai.evaluate_prompt")
def test_ai_rule_detects_flaw(mock_evaluate, mock_is_available):
    mock_evaluate.return_value = {
        "issues": [
            {
                "rule_id": "AI001",
                "severity": "ERROR",
                "message": "Missing persona.",
                "suggestion": "Add a persona.",
                "score_impact": -10,
            }
        ]
    }

    # Must be > 10 words to trigger AI
    doc = parse_prompt("This is a long enough prompt that the AI should analyze it and find flaws.")
    results = analyze_with_ai(doc)

    assert len(results) == 1
    assert results[0].rule_id == "AI001"
    assert results[0].message == "[AI] Missing persona."


@patch("promptlint.rules.ai.is_llm_available", return_value=True)
def test_ai_rule_skips_short_prompts(mock_is_available):
    doc = parse_prompt("Too short.")
    results = analyze_with_ai(doc)
    assert len(results) == 0


@patch("promptlint.rules.ai.is_llm_available", return_value=False)
def test_ai_rule_graceful_degrade(mock_is_available):
    doc = parse_prompt("This is a long enough prompt that the AI should analyze it and find flaws.")
    results = analyze_with_ai(doc)
    assert len(results) == 0
