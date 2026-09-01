from promptlint.models import RuleResult, Severity
from promptlint.parser import parse_prompt
from promptlint.scoring import _estimate_tokens, calculate_score, get_rating


def test_get_rating():
    assert get_rating(95) == "Excellent"
    assert get_rating(80) == "Good"
    assert get_rating(65) == "Fair"
    assert get_rating(50) == "Needs Work"
    assert get_rating(20) == "Poor"

def test_estimate_tokens():
    assert _estimate_tokens(100) == 130

def test_calculate_score_perfect():
    doc = parse_prompt("Hello world.")
    score, rating, cat_scores, stats = calculate_score([], doc)
    assert score == 100
    assert rating == "Excellent"
    assert all(c.score == 100 for c in cat_scores)

def test_calculate_score_degraded():
    doc = parse_prompt("Hello world.")
    res1 = RuleResult(rule_id="STRUCT001", category="structure", severity=Severity.WARNING, message="test")
    res2 = RuleResult(rule_id="CLAR001", category="clarity", severity=Severity.ERROR, message="test")

    score, rating, cat_scores, stats = calculate_score([res1, res2], doc)

    # -10 for warning, -15 for error = -25
    assert score == 75
    assert rating == "Good"

    struct_score = next(c for c in cat_scores if c.name == "Structure")
    clarity_score = next(c for c in cat_scores if c.name == "Clarity")
    assert struct_score.score == 90
    assert clarity_score.score == 85

def test_calculate_score_clamping():
    doc = parse_prompt("Hello world.")
    # Add many critical errors to push score below 0
    results = [
        RuleResult(rule_id="X", category="structure", severity=Severity.CRITICAL, message="test")
        for _ in range(5)
    ]
    score, rating, cat_scores, stats = calculate_score(results, doc)
    assert score == 0

    struct_score = next(c for c in cat_scores if c.name == "Structure")
    assert struct_score.score == 0
