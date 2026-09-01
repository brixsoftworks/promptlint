from promptlint.diff import diff_prompts


def test_diff_prompts():
    old = "Please make it better and do a good job."
    new = "Write a story. The story must be 500 words. Format as a markdown list."

    result = diff_prompts(old, new)
    assert result.score_delta > 0
    assert result.old_name == "old"
    assert result.new_name == "new"

def test_diff_regression():
    old = "Write a story. The story must be 500 words. Format as a markdown list."
    new = "Please make it better and do a good job."

    result = diff_prompts(old, new)
    assert result.score_delta < 0
