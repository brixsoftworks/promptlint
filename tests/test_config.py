from promptlint.config import Config


def test_config_defaults():
    config = Config()
    assert config.max_prompt_length == 50000
    assert config.disabled_rules == []
    assert config.severity_overrides == {}


def test_config_load_no_file(tmp_path):
    config = Config.load(tmp_path)
    assert config.max_prompt_length == 50000
    assert config.disabled_rules == []


def test_config_load_file(tmp_path):
    config_file = tmp_path / ".promptlintrc.toml"
    config_file.write_text('disabled_rules = ["STRUCT001"]\nmax_prompt_length = 1000')

    config = Config.load(tmp_path)
    assert config.disabled_rules == ["STRUCT001"]
    assert config.max_prompt_length == 1000
