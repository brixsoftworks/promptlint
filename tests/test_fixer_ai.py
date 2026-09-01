from unittest.mock import patch

import pytest

from promptlint.fixer_ai import fix_prompt_magic


@patch("promptlint.fixer_ai.is_llm_available", return_value=True)
@patch("promptlint.fixer_ai.evaluate_prompt")
def test_fix_magic_success(mock_evaluate, mock_is_available):
    mock_evaluate.return_value = "<context>\nYou are a pro.\n</context>"

    fixed = fix_prompt_magic("Be a pro.")
    assert fixed == "<context>\nYou are a pro.\n</context>"
    mock_evaluate.assert_called_once()

@patch("promptlint.fixer_ai.is_llm_available", return_value=False)
def test_fix_magic_fails_without_llm(mock_is_available):
    with pytest.raises(RuntimeError):
        fix_prompt_magic("Be a pro.")
