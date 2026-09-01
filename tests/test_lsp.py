from unittest.mock import patch

from promptlint.lsp import PYGLS_AVAILABLE, start_language_server


def test_lsp_availability():
    # If pygls is installed, it should be available
    assert isinstance(PYGLS_AVAILABLE, bool)

@patch("promptlint.lsp.PYGLS_AVAILABLE", False)
def test_lsp_start_fails_gracefully_without_pygls(capsys):
    start_language_server()
    captured = capsys.readouterr()
    assert "Error: pygls is not installed." in captured.out
