from promptlint import __version__, analyze, lint, parse_prompt


def test_api_analyze():
    report = analyze("Please make it better and do a good job.")
    assert report.score < 100
    assert len(report.results) > 0

def test_api_lint():
    report = lint("Please make it better and do a good job.")
    assert report.score < 100
    assert len(report.results) > 0

def test_api_parse():
    doc = parse_prompt("Write a story.")
    assert doc.text == "Write a story."

def test_api_version():
    assert isinstance(__version__, str)
