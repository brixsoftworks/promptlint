import json

from promptlint.analyzer import analyze_prompt
from promptlint.parser import parse_prompt
from promptlint.reporter import report_to_json


def test_report_to_json():
    doc = parse_prompt("Write a story.")
    report = analyze_prompt(doc)

    json_str = report_to_json(report)
    data = json.loads(json_str)

    assert "score" in data
    assert "rating" in data
    assert "results" in data
    assert "category_scores" in data
    assert "statistics" in data
    assert "security_status" in data
