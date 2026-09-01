from promptlint.parser import parse_prompt
from promptlint.rules.efficiency import (
    check_excessive_whitespace,
    check_prompt_length,
    check_repeated_instructions,
)


def test_eff001_repeated_instructions():
    doc = parse_prompt("Please summarize the provided text in detail. Please summarize the provided text in detail.")
    res = check_repeated_instructions(doc)
    assert len(res) >= 1
    assert res[0].rule_id == "EFF001"

    doc2 = parse_prompt("Summarize the text. Output in JSON.")
    res2 = check_repeated_instructions(doc2)
    assert len(res2) == 0


def test_eff002_excessive_whitespace():
    doc = parse_prompt("Hello.\n\n\n\nWorld.")
    res = check_excessive_whitespace(doc)
    assert len(res) >= 1
    assert res[0].rule_id == "EFF002"

    doc2 = parse_prompt("Hello.\n\nWorld.")
    res2 = check_excessive_whitespace(doc2)
    assert len(res2) == 0


def test_eff003_prompt_length():
    doc = parse_prompt("word " * 2005)
    res = check_prompt_length(doc)
    assert len(res) == 1
    assert res[0].rule_id == "EFF003"

    doc2 = parse_prompt("word " * 100)
    res2 = check_prompt_length(doc2)
    assert len(res2) == 0


def test_eff004_negative_constraints():
    from promptlint.rules.efficiency import check_negative_constraints

    doc = parse_prompt("Do not use markdown. Don't use bullet points. Never include code. Avoid long sentences.")
    res = check_negative_constraints(doc)
    assert len(res) == 1
    assert res[0].rule_id == "EFF004"

    doc2 = parse_prompt("Use plain text format and keep sentences short.")
    res2 = check_negative_constraints(doc2)
    assert len(res2) == 0
