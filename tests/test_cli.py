import json

from typer.testing import CliRunner

from promptlint.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "PromptLint" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_cli_analyze(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Please make it better and do a good job. We have a new system. It should be fast.")

    result = runner.invoke(app, ["analyze", str(p)])
    # issue_count > 0 returns 1
    assert result.exit_code == 1
    assert "QUALITY SCORE" in result.stdout


def test_cli_analyze_json(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Please make it better and do a good job. We have a new system. It should be fast.")

    result = runner.invoke(app, ["analyze", "--json", str(p)])
    assert result.exit_code == 1

    data = json.loads(result.stdout)
    assert "score" in data


def test_cli_score(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Write a great story.")

    result = runner.invoke(app, ["score", str(p)])
    assert result.exit_code == 0
    assert "/100" in result.stdout


def test_cli_security(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Just a normal text.")

    result = runner.invoke(app, ["security", str(p)])
    assert result.exit_code == 0
    assert "No security issues detected." in result.stdout


def test_cli_tokens(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Just a normal text.")

    result = runner.invoke(app, ["tokens", str(p)])
    assert result.exit_code == 0
    assert "Estimated Tokens" in result.stdout


def test_cli_fix(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Write a story.")

    result = runner.invoke(app, ["fix", str(p)])
    assert result.exit_code == 0
    assert "Task:" in result.stdout


def test_cli_diff(tmp_path):
    p1 = tmp_path / "test1.txt"
    p1.write_text("Write a story.")
    p2 = tmp_path / "test2.txt"
    p2.write_text("Write a story with 500 words in markdown.")

    result = runner.invoke(app, ["diff", str(p1), str(p2)])
    assert result.exit_code == 0
    assert "Prompt Diff" in result.stdout


def test_cli_file_not_found():
    result = runner.invoke(app, ["analyze", "does_not_exist.txt"])
    assert result.exit_code == 1
    assert "File not found" in result.stderr


def test_cli_stdin():
    result = runner.invoke(
        app,
        ["analyze", "-"],
        input="Please make it better and do a good job. We have a new system. It should be fast.",
    )
    assert result.exit_code == 1
    assert "QUALITY SCORE" in result.stdout
