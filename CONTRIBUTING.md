# Contributing to PromptLint

Thank you for your interest in contributing to PromptLint!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/promptlint/promptlint.git
cd promptlint

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/ tests/
```

## Adding a New Rule

1. Choose the appropriate category module in `src/promptlint/rules/`.
2. Create a function that accepts a `PromptDocument` and returns `list[RuleResult]`.
3. Register the function in `src/promptlint/rules/__init__.py`.
4. Add tests in `tests/`.
5. Document the rule in `docs/rules.md`.

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Write tests for any new functionality.
3. Ensure all tests pass: `pytest`
4. Ensure code passes linting: `ruff check src/ tests/`
5. Format code: `ruff format src/ tests/`
6. Submit a pull request with a clear description.

## Code Style

- Use type annotations for all function signatures.
- Follow existing naming conventions.
- Keep functions small and focused.
- Write docstrings for public APIs.
- Prefer readable code over clever code.

## Reporting Issues

- Use GitHub Issues.
- Include the PromptLint version (`promptlint --version`).
- Include a minimal reproducible example when possible.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
