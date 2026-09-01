"""Code extractor for PromptLint.

Parses Python files to extract string literals that might be prompts.
Uses the `ast` module to safely analyze code without executing it.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass
class ExtractedPrompt:
    """A prompt extracted from source code."""

    text: str
    line_number: int
    context_name: str | None = None  # Variable name or function call


class PromptVisitor(ast.NodeVisitor):
    """AST visitor that looks for multiline strings or variables named 'prompt'."""

    def __init__(self) -> None:
        self.prompts: list[ExtractedPrompt] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check for variable assignments like PROMPT = '''...'''."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

            # Check if assigned value is a string
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                text = node.value.value

                # Heuristic: Is it called 'prompt', 'template', or is it a multiline string?
                is_prompt_var = any(x in var_name.lower() for x in ["prompt", "template", "instruction"])
                is_multiline = "\n" in text and len(text) > 20

                if is_prompt_var or is_multiline:
                    self.prompts.append(
                        ExtractedPrompt(
                            text=text,
                            line_number=node.lineno,
                            context_name=var_name,
                        )
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for string literals passed to LLM-like function calls."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        else:
            func_name = ""

        # Check if the function name suggests an LLM call
        llm_funcs = {"completion", "generate", "chat", "predict", "analyze", "invoke"}
        is_llm_call = any(x in func_name.lower() for x in llm_funcs)

        if is_llm_call:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    self.prompts.append(
                        ExtractedPrompt(
                            text=arg.value,
                            line_number=node.lineno,
                            context_name=f"{func_name}()",
                        )
                    )

            for kwarg in node.keywords:
                if isinstance(kwarg.value, ast.Constant) and isinstance(kwarg.value.value, str):
                    if kwarg.arg in ["prompt", "messages", "content", "system_prompt"]:
                        self.prompts.append(
                            ExtractedPrompt(
                                text=kwarg.value.value,
                                line_number=node.lineno,
                                context_name=f"{func_name}({kwarg.arg}=...)",
                            )
                        )

        self.generic_visit(node)


def extract_prompts_from_python(code: str) -> list[ExtractedPrompt]:
    """Parse a Python source string and return all extracted prompts."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    visitor = PromptVisitor()
    visitor.visit(tree)
    return visitor.prompts
