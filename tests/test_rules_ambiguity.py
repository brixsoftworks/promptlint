from promptlint.parser import parse_prompt
from promptlint.rules.ambiguity import (
    _check_amb001_vague_quantities,
    _check_amb002_subjective_quality,
    _check_amb003_undefined_references,
)


def test_amb001_vague_quantities():
    doc = parse_prompt("Provide a few examples.")
    res = _check_amb001_vague_quantities(doc)
    assert len(res) == 1
    assert res[0].rule_id == "AMB001"

    doc2 = parse_prompt("Provide 3 examples.")
    res2 = _check_amb001_vague_quantities(doc2)
    assert len(res2) == 0

def test_amb002_subjective_quality():
    doc = parse_prompt("Write a high quality essay.")
    res = _check_amb002_subjective_quality(doc)
    assert len(res) == 1
    assert res[0].rule_id == "AMB002"

    doc2 = parse_prompt("Write an essay with 500 words.")
    res2 = _check_amb002_subjective_quality(doc2)
    assert len(res2) == 0

def test_amb003_undefined_references():
    doc = parse_prompt("It should be processed properly.")
    res = _check_amb003_undefined_references(doc)
    assert len(res) == 1
    assert res[0].rule_id == "AMB003"

    doc2 = parse_prompt("The data should be processed properly.")
    res2 = _check_amb003_undefined_references(doc2)
    assert len(res2) == 0
