from promptlint.fixer import fix_prompt


def test_fix_minimal():
    fixed = fix_prompt("Write a story.")
    assert "Task:" in fixed
    assert "Write a story." in fixed

def test_fix_whitespace():
    fixed = fix_prompt("Task:\n\n\n\nWrite a story.")
    assert "\n\n\n\n" not in fixed
    assert "Task:\n\n\nWrite a story." in fixed or "Task:\n\nWrite a story" in fixed or "Task:\n\n\n" in fixed

def test_fix_has_structure():
    fixed = fix_prompt("Task: Write a story.\n\nRequirements:\n- Must be 500 words.")
    # Should not add another Task header if already present
    assert fixed.count("Task:") == 1
