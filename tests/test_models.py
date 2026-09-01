from promptlint.models import PromptDocument, RuleResult, Severity


def test_severity_enum():
    assert Severity.INFO == "info"
    assert Severity.WARNING == "warning"
    assert Severity.ERROR == "error"
    assert Severity.CRITICAL == "critical"

def test_rule_result_effective_score_impact():
    # Uses default
    res1 = RuleResult(rule_id="T001", category="test", severity=Severity.WARNING, message="test")
    assert res1.effective_score_impact() == -10

    # Overrides default
    res2 = RuleResult(rule_id="T002", category="test", severity=Severity.WARNING, message="test", score_impact=-5)
    assert res2.effective_score_impact() == -5

def test_prompt_document_creation():
    doc = PromptDocument(text="hello", lines=["hello"], character_count=5, word_count=1, line_count=1)
    assert doc.text == "hello"
    assert doc.word_count == 1
