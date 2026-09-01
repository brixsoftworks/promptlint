from promptlint.parser import parse_prompt
from promptlint.rules.clarity import (
    check_ambiguous_references,
    check_undefined_terminology,
    check_vague_instructions,
)


def test_clar001_vague_instructions():
    doc = parse_prompt("Please make it better.")
    res = check_vague_instructions(doc)
    assert len(res) == 1
    assert res[0].rule_id == "CLAR001"

    doc2 = parse_prompt("Rewrite this to be more concise.")
    res2 = check_vague_instructions(doc2)
    assert len(res2) == 0


def test_clar002_undefined_terminology():
    doc = parse_prompt("Use the DFR technique to solve this.")
    res = check_undefined_terminology(doc)
    assert len(res) == 1
    assert res[0].rule_id == "CLAR002"

    doc2 = parse_prompt("Use the DFR (Data Flow Routing) technique.")
    res2 = check_undefined_terminology(doc2)
    assert len(res2) == 0


def test_clar003_ambiguous_references():
    doc = parse_prompt("We have a new system.\n\nIt should be fast.")
    res = check_ambiguous_references(doc)
    assert len(res) == 1
    assert res[0].rule_id == "CLAR003"

    doc2 = parse_prompt("We have a new system.\n\nThe system should be fast.")
    res2 = check_ambiguous_references(doc2)
    assert len(res2) == 0
