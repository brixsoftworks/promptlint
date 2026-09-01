"""AI-powered magic prompt fixer.

Rewrites poor prompts into highly optimized, structured, enterprise-grade
prompts using prompt engineering best practices (XML tags, few-shot, etc.).
"""

from __future__ import annotations

from promptlint.llm import evaluate_prompt, is_llm_available


def fix_prompt_magic(text: str) -> str:
    """Rewrite a prompt using an LLM.

    Args:
        text: The original, poorly written prompt.

    Returns:
        The newly structured, optimized prompt.
    """
    if not is_llm_available():
        raise RuntimeError("LiteLLM is required for magic fix. Install with `pip install promptlint[ai]`.")

    system_prompt = """You are an elite Prompt Engineer.
Your task is to take a user's rough, poorly-written prompt and rewrite it into a highly structured, enterprise-grade prompt.

Apply these best practices:
1. Define a clear persona/role at the top.
2. Separate the context, instructions, and constraints using XML tags (e.g., <context>, <instructions>, <rules>).
3. Specify a clear output format (e.g., JSON schema, markdown structure, table).
4. Remove ambiguity and make quantities/requirements explicit.
5. If helpful, add a <few_shot_examples> section for the user to fill in.

Return ONLY the new prompt text. Do not include markdown code blocks (like ```) around the entire output. Do not explain your changes.
"""

    try:
        optimized_prompt = evaluate_prompt(
            prompt_text=f"Please rewrite this prompt:\n\n{text}",
            system_prompt=system_prompt,
        )
        # Clean up in case the LLM returned it in markdown blocks anyway
        if optimized_prompt.startswith("```") and optimized_prompt.endswith("```"):
            lines = optimized_prompt.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            optimized_prompt = "\n".join(lines)

        return optimized_prompt.strip()
    except Exception as e:
        raise RuntimeError(f"Magic fix failed: {e}")
