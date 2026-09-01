from promptlint.parser import parse_prompt
from promptlint.rules.conflicts import check_contradictions


def test_conf001_contradictory_instructions():
    doc = parse_prompt("Be concise. But go into great detail.")
    res = check_contradictions(doc)
    assert len(res) >= 1
    assert res[0].rule_id == "CONF001"

def test_conf001_no_contradiction():
    doc = parse_prompt("Be concise and get straight to the point.")
    res = check_contradictions(doc)
    assert len(res) == 0

def test_conf001_bullet_points():
    doc = parse_prompt("No bullet points allowed. Use bullet points.")
    res = check_contradictions(doc)
    assert len(res) >= 1
    assert res[0].rule_id == "CONF001"
