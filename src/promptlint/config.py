"""Minimal configuration system for PromptLint.

Looks for .promptlintrc.toml in CWD → parent directories → home directory.
Supports disabling rules and overriding severity levels.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """PromptLint configuration."""

    disabled_rules: list[str] = field(default_factory=list)
    severity_overrides: dict[str, str] = field(default_factory=dict)
    max_prompt_length: int = 50000

    @classmethod
    def load(cls, start_dir: Path | None = None) -> Config:
        """Load configuration from .promptlintrc.toml.

        Searches from start_dir up to the filesystem root, then checks
        the user's home directory. Returns default config if no file found.
        """
        config_name = ".promptlintrc.toml"
        search_dir = start_dir or Path.cwd()

        # Search upward from CWD
        current = search_dir.resolve()
        while True:
            config_path = current / config_name
            if config_path.is_file():
                return cls._from_file(config_path)
            parent = current.parent
            if parent == current:
                break
            current = parent

        # Check home directory
        home_config = Path.home() / config_name
        if home_config.is_file():
            return cls._from_file(home_config)

        return cls()

    @classmethod
    def _from_file(cls, path: Path) -> Config:
        """Parse a TOML config file into a Config object."""
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            return cls()

        return cls(
            disabled_rules=data.get("disabled_rules", []),
            severity_overrides=data.get("severity_overrides", {}),
            max_prompt_length=data.get("max_prompt_length", 50000),
        )
