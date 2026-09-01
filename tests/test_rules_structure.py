from promptlint.parser import parse_prompt
from promptlint.rules.structure import (
    check_context_without_instruction,
    check_missing_constraints,
    check_missing_objective,
    check_missing_output_format,
)


def test_struct001_missing_objective():
    doc = parse_prompt("The capital of France is Paris. The weather is nice today.")
    res = check_missing_objective(doc)
    assert len(res) == 1
    assert res[0].rule_id == "STRUCT001"

    doc2 = parse_prompt("Summarize the text.")
    res2 = check_missing_objective(doc2)
    assert len(res2) == 0


def test_struct002_missing_format():
    doc = parse_prompt(
        "Write a story about a brave knight. It should be very interesting and long. Make sure to describe the dragon in detail."
    )
    res = check_missing_output_format(doc)
    assert len(res) == 1
    assert res[0].rule_id == "STRUCT002"

    doc2 = parse_prompt(
        "Write a story about a brave knight. It should be very interesting and long. Make sure to describe the dragon in detail. Output in markdown format."
    )
    res2 = check_missing_output_format(doc2)
    assert len(res2) == 0


def test_struct003_missing_constraints():
    doc = parse_prompt(" ".join(["Word"] * 55))  # Over 50 words
    res = check_missing_constraints(doc)
    assert len(res) == 1
    assert res[0].rule_id == "STRUCT003"

    doc2 = parse_prompt(" ".join(["Word"] * 55) + " You must avoid using letter e.")
    res2 = check_missing_constraints(doc2)
    assert len(res2) == 0


def test_struct004_context_no_instruction():
    doc = parse_prompt("Here is some context about a project. The project is called Apollo. It was very successful.")
    res = check_context_without_instruction(doc)
    assert len(res) == 1
    assert res[0].rule_id == "STRUCT004"


def test_struct005_missing_delimiters():
    from promptlint.rules.structure import check_missing_delimiters

    doc = parse_prompt(
        "Please analyze the following document in detail and extract all key takeaways, action items, and structural risks for the leadership team."
    )
    res = check_missing_delimiters(doc)
    assert len(res) == 1
    assert res[0].rule_id == "STRUCT005"

    doc2 = parse_prompt("Please summarize the following document:\n```\nSome document content here...\n```")
    res2 = check_missing_delimiters(doc2)
    assert len(res2) == 0
