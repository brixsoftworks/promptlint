from promptlint.parser import parse_prompt


def test_parse_empty():
    doc = parse_prompt("")
    assert doc.text == ""
    assert doc.word_count == 0
    assert doc.line_count == 0
    assert doc.character_count == 0

def test_parse_whitespace():
    doc = parse_prompt("   \n   \n")
    assert doc.text == "   \n   \n"
    assert doc.word_count == 0
    assert doc.line_count == 2
    assert doc.character_count == 8

def test_parse_normal():
    doc = parse_prompt("Hello world.\nThis is a test.")
    assert doc.word_count == 6
    assert doc.line_count == 2
    assert doc.character_count == 28

def test_parse_large():
    text = "word " * 1000
    doc = parse_prompt(text)
    assert doc.word_count == 1000

def test_parse_unicode():
    doc = parse_prompt("Hello 🌍\nПривет мир")
    assert doc.word_count == 4
    assert doc.line_count == 2
