"""Structure analysis rules for AI prompts.

Detects structural issues: missing objectives, missing output format,
missing constraints, and context without instruction. Uses heuristic
keyword analysis — not NLP or ML. Precision is prioritized over recall.
"""

from __future__ import annotations

import re

from promptlint.models import PromptDocument, RuleResult, Severity

# Action verbs that indicate the prompt has a clear task/objective.
_ACTION_VERBS = {
    "write", "create", "explain", "analyze", "generate", "summarize",
    "translate", "describe", "compare", "build", "design", "implement",
    "develop", "draft", "compose", "rewrite", "edit", "revise", "review",
    "evaluate", "assess", "outline", "plan", "suggest", "recommend",
    "calculate", "compute", "solve", "find", "identify", "classify",
    "categorize", "extract", "parse", "convert", "transform", "format",
    "optimize", "improve", "refactor", "debug", "fix", "test", "check",
    "verify", "validate", "define", "list", "enumerate", "rank", "sort",
    "filter", "search", "research", "investigate", "explore", "map",
    "diagram", "illustrate", "visualize", "model", "simulate", "predict",
    "estimate", "measure", "count", "name", "tell", "show", "give",
    "provide", "make", "help", "answer", "respond", "reply", "say",
    "act", "pretend", "imagine", "assume", "consider", "think",
    "determine", "decide", "choose", "select", "pick", "prioritize",
    "organize", "structure", "arrange", "group", "combine", "merge",
    "split", "separate", "divide", "break", "simplify", "elaborate",
    "expand", "shorten", "condense", "paraphrase", "rephrase",
    "proofread", "correct", "update", "modify", "adjust", "adapt",
    "customize", "configure", "setup", "install", "deploy", "run",
    "execute", "perform", "complete", "finish", "continue", "start",
    "begin", "prepare", "produce", "deliver", "present", "report",
    "document", "log", "record", "track", "monitor", "watch", "observe",
    "note", "highlight", "emphasize", "focus", "summarise", "analyse",
    "categorise", "organise", "optimise", "maximise", "minimise",
}

# Question words that indicate the prompt has a clear intent.
_QUESTION_WORDS = {"what", "how", "why", "when", "where", "who", "which", "whom", "whose"}

# Keywords indicating output format specification.
_FORMAT_KEYWORDS = {
    "format", "structure", "output", "response", "return", "result",
    "bullet point", "bullet points", "bulleted", "numbered", "list",
    "table", "json", "markdown", "csv", "xml", "yaml", "html",
    "paragraph", "paragraphs", "steps", "step-by-step", "section",
    "heading", "header", "template", "schema", "example output",
    "respond with", "respond in", "reply with", "reply in",
    "provide as", "in the form of", "formatted as", "output as",
    "return as", "give me", "present as",
}

# Keywords indicating constraints or boundaries.
_CONSTRAINT_KEYWORDS = {
    "must", "should", "shall", "limit", "maximum", "minimum", "max",
    "min", "at most", "at least", "no more than", "no fewer than",
    "no less than", "within", "between", "only", "exactly", "precisely",
    "constraint", "requirement", "restrict", "restriction", "boundary",
    "avoid", "do not", "don't", "never", "always", "ensure", "require",
    "mandatory", "optional", "forbidden", "prohibited", "allowed",
    "acceptable", "unacceptable", "exclude", "include only",
    "not allowed", "not permitted", "unless", "except",
}


def _has_action_verb(text: str) -> bool:
    """Check if text contains an action verb at a word boundary."""
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    return bool(words & _ACTION_VERBS)


def _has_question_word(text: str) -> bool:
    """Check if text contains a question word, typically at sentence start."""
    lower = text.lower()
    # Check for question marks
    if "?" in text:
        return True
    # Check for question words at sentence boundaries
    for word in _QUESTION_WORDS:
        if re.search(rf"(?:^|[.!?]\s+){word}\b", lower):
            return True
    return False


def _has_format_keywords(text: str) -> bool:
    """Check if text specifies an output format."""
    lower = text.lower()
    return any(kw in lower for kw in _FORMAT_KEYWORDS)


def _has_constraint_keywords(text: str) -> bool:
    """Check if text contains constraint language."""
    lower = text.lower()
    return any(kw in lower for kw in _CONSTRAINT_KEYWORDS)


def check_missing_objective(doc: PromptDocument) -> list[RuleResult]:
    """STRUCT001: Detect prompts without a clear objective or task."""
    # Skip empty or very short prompts (1-4 words are often valid commands)
    if doc.word_count < 5:
        return []

    if _has_action_verb(doc.text) or _has_question_word(doc.text):
        return []

    return [
        RuleResult(
            rule_id="STRUCT001",
            category="structure",
            severity=Severity.WARNING,
            message="Prompt does not appear to contain a clear objective or task.",
            suggestion=(
                "Add an explicit instruction verb (e.g., 'Explain', 'Write', "
                "'Analyze', 'Create') or phrase the prompt as a question."
            ),
            score_impact=-10,
        )
    ]


def check_missing_output_format(doc: PromptDocument) -> list[RuleResult]:
    """STRUCT002: Detect prompts missing output format specification."""
    # Only flag non-trivial prompts
    if doc.word_count <= 15:
        return []

    if _has_format_keywords(doc.text):
        return []

    return [
        RuleResult(
            rule_id="STRUCT002",
            category="structure",
            severity=Severity.WARNING,
            message="Prompt has no explicit output format.",
            suggestion=(
                "Specify the expected output structure (e.g., bullet points, "
                "numbered list, JSON, table, or paragraph format)."
            ),
            score_impact=-8,
        )
    ]


def check_missing_constraints(doc: PromptDocument) -> list[RuleResult]:
    """STRUCT003: Detect complex prompts without constraints."""
    # Only flag substantial prompts
    if doc.word_count <= 50:
        return []

    if _has_constraint_keywords(doc.text):
        return []

    return [
        RuleResult(
            rule_id="STRUCT003",
            category="structure",
            severity=Severity.INFO,
            message="Complex prompt has no explicit constraints or boundaries.",
            suggestion=(
                "Consider adding constraints such as length limits, scope "
                "boundaries, or behavioral requirements (e.g., 'must', "
                "'avoid', 'limit to')."
            ),
            score_impact=-5,
        )
    ]


def check_context_without_instruction(doc: PromptDocument) -> list[RuleResult]:
    """STRUCT004: Detect prompts that provide context but no instruction."""
    # Need enough text to distinguish context from a command
    if doc.word_count < 10:
        return []

    # If the prompt has action verbs or questions, it has an instruction
    if _has_action_verb(doc.text) or _has_question_word(doc.text):
        return []

    return [
        RuleResult(
            rule_id="STRUCT004",
            category="structure",
            severity=Severity.WARNING,
            message="Prompt appears to provide context but no explicit instruction.",
            suggestion=(
                "Add a clear instruction telling the model what to do with "
                "the provided context (e.g., 'Summarize the above', "
                "'Based on this context, answer...')."
            ),
            score_impact=-10,
        )
    ]


def analyze_structure(document: PromptDocument) -> list[RuleResult]:
    """Run all structure analysis rules on a prompt document."""
    results: list[RuleResult] = []
    results.extend(check_missing_objective(document))
    results.extend(check_missing_output_format(document))
    results.extend(check_missing_constraints(document))
    # Only check context-without-instruction if STRUCT001 didn't fire
    # (they overlap: both detect missing action verbs)
    if not any(r.rule_id == "STRUCT001" for r in results):
        results.extend(check_context_without_instruction(document))
    return results
