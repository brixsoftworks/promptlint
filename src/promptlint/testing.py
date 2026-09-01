"""Minimal test framework for prompt evaluation.

Loads YAML test specifications and runs basic assertions. Model execution
is not implemented in V1 — the framework clearly reports when a model
backend is required. This prepares the architecture for future model adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml  # type: ignore[import-untyped]


@dataclass
class TestCase:
    """A single test case for a prompt."""

    input: str
    expected_contains: list[str] = field(default_factory=list)


@dataclass
class PromptTestSpec:
    """A complete test specification for a prompt."""

    name: str
    prompt: str
    cases: list[TestCase] = field(default_factory=list)


@dataclass
class TestResult:
    """Result of running a single test case."""

    case: TestCase
    passed: bool
    message: str


def load_test_spec(path: Path) -> PromptTestSpec:
    """Load a prompt test specification from a YAML file.

    Expected YAML format:
        name: my-prompt
        prompt: |
          Your prompt text here.
        cases:
          - input: "user input"
            expected_contains:
              - "expected word"
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    cases = []
    for case_data in data.get("cases", []):
        cases.append(
            TestCase(
                input=case_data.get("input", ""),
                expected_contains=case_data.get("expected_contains", []),
            )
        )

    return PromptTestSpec(
        name=data.get("name", path.stem),
        prompt=data.get("prompt", ""),
        cases=cases,
    )


def run_tests(spec: PromptTestSpec) -> list[TestResult]:
    """Run test cases against a prompt specification.

    NOTE: Model execution is not implemented in V1. This function will
    report that a model backend is required for each test case. The
    architecture is ready for future model adapters.
    """
    results: list[TestResult] = []

    for case in spec.cases:
        results.append(
            TestResult(
                case=case,
                passed=False,
                message=(
                    "Model execution not configured. Install a model adapter "
                    "and configure it with `promptlint config set-model` to "
                    "run prompt tests."
                ),
            )
        )

    return results
