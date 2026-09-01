"""LLM adapter for PromptLint V2.

Provides a unified interface for interacting with LiteLLM to support
OpenAI, Anthropic, Gemini, and Ollama. This module isolates the AI
dependencies so the core linter can still run offline.
"""

from __future__ import annotations

import json
from typing import Any

try:
    from litellm import completion

    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class LLMError(Exception):
    """Raised when LLM interaction fails."""

    pass


def is_llm_available() -> bool:
    """Check if the optional litellm dependency is installed."""
    return LITELLM_AVAILABLE


def evaluate_prompt(
    prompt_text: str,
    system_prompt: str,
    model: str = "gpt-4o-mini",
    response_format: dict[str, Any] | None = None,
) -> Any:
    """Send a prompt to an LLM for evaluation.

    Args:
        prompt_text: The user's prompt to evaluate.
        system_prompt: Instructions for the evaluator model.
        model: The LiteLLM model identifier.
        response_format: Optional JSON schema for structured output.

    Returns:
        The evaluated response, parsed as JSON if response_format was provided,
        otherwise the raw string.
    """
    if not LITELLM_AVAILABLE:
        raise LLMError("LiteLLM is not installed. Please install with `pip install promptlint[ai]` to use AI features.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_text},
    ]

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
    }

    if response_format:
        kwargs["response_format"] = response_format

    try:
        response = completion(**kwargs)
        content = response.choices[0].message.content

        if response_format:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise LLMError(f"Failed to parse LLM JSON response: {e}")
        return content
    except Exception as e:
        raise LLMError(f"LLM API request failed: {e}")
