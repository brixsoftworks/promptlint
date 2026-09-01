"""Clarity analysis rules for AI prompts.

Detects vague instructions, undefined terminology, and ambiguous references.
Each rule provides actionable, tailored suggestions rather than generic advice.
"""

from __future__ import annotations

import re

from promptlint.models import PromptDocument, RuleResult, Severity

# Vague phrases mapped to tailored suggestions.
_VAGUE_PHRASES: dict[str, str] = {
    r"make (?:it|this|that|them) better": (
        "Define what 'better' means: shorter, more accurate, more formal, or more detailed."
    ),
    r"improve (?:it|this|that|them)": (
        "Specify what aspect to improve: accuracy, readability, performance, or completeness."
    ),
    r"make (?:it|this|that|them) good": (
        "Define measurable criteria for 'good': target audience, quality metrics, or specific goals."
    ),
    r"make (?:it|this|that|them) great": (
        "Define what 'great' looks like: specific quality benchmarks, examples, or comparison points."
    ),
    r"make (?:it|this|that|them) professional": (
        "Specify what 'professional' means: formal tone, industry-standard format, or expert-level depth."
    ),
    r"explain (?:it )?properly": (
        "Define what 'properly' means: target audience level, desired depth, or specific aspects to cover."
    ),
    r"do (?:it|this|that) (?:well|nicely)": (
        "Replace with specific quality criteria: accuracy requirements, style guidelines, or format expectations."
    ),
    r"handle (?:it|this|that) (?:well|appropriately|properly)": (
        "Specify exact handling behavior: error cases, edge cases, or expected outcomes."
    ),
    r"do a good job": (
        "Define success criteria: what does a 'good job' look like? Provide examples or metrics."
    ),
    r"optimize (?:it|this|that)": (
        "Specify the optimization target: speed, size, readability, cost, or accuracy."
    ),
    r"fix (?:it|this|that)": (
        "Describe the specific problem to fix and the expected correct behavior."
    ),
    r"clean (?:it|this|that) up": (
        "Specify what 'clean up' means: remove redundancy, improve formatting, fix errors, or restructure."
    ),
    r"make (?:it|this|that) (?:look |sound )?nice": (
        "Define the aesthetic or quality goal: specific style, tone, format, or visual layout."
    ),
}

# Common abbreviations that should NOT be flagged as undefined terminology.
_COMMON_ABBREVIATIONS = {
    "API", "URL", "HTML", "CSS", "JSON", "SQL", "HTTP", "HTTPS", "REST",
    "XML", "CSV", "PDF", "PNG", "JPG", "GIF", "SVG", "YAML", "TOML",
    "CLI", "GUI", "IDE", "SDK", "CDN", "DNS", "TCP", "UDP", "SSH",
    "SSL", "TLS", "JWT", "OAuth", "SMTP", "IMAP", "POP", "FTP", "SFTP",
    "AWS", "GCP", "CPU", "GPU", "RAM", "SSD", "HDD", "ROM", "USB",
    "CRUD", "ORM", "MVC", "MVP", "OOP", "DRY", "KISS", "SOLID",
    "CI", "CD", "TDD", "BDD", "QA", "UAT", "SLA", "KPI", "ROI",
    "CEO", "CTO", "CFO", "COO", "VP", "HR", "PR", "FAQ", "FYI",
    "USA", "UK", "EU", "UN", "GDP", "GPA", "SAT", "ACT", "MBA",
    "PhD", "MD", "AI", "ML", "NLP", "LLM", "GPT", "RGB", "HEX",
    "ISO", "IEEE", "RFC", "MIME", "UTF", "ASCII", "BASE64", "UUID",
    "CRM", "ERP", "SaaS", "PaaS", "IaaS", "VM", "VPN", "LAN", "WAN",
    "FIFO", "LIFO", "EOF", "NULL", "STDIN", "STDOUT", "STDERR",
    "TODO", "FIXME", "NOTE", "XXX", "HACK", "TEMP", "TBD", "WIP",
    "ASAP", "ETA", "POC", "CORS", "XSS", "CSRF",
    "DOS", "DDOS", "RSA", "AES", "SHA", "HMAC", "PGP", "GPG",
}


def check_vague_instructions(doc: PromptDocument) -> list[RuleResult]:
    """CLAR001: Detect vague, subjective instructions."""
    results: list[RuleResult] = []
    lower_text = doc.text.lower()

    for pattern, suggestion in _VAGUE_PHRASES.items():
        matches = list(re.finditer(pattern, lower_text))
        for match in matches:
            # Find the line number for this match
            line_num = doc.text[:match.start()].count("\n") + 1
            matched_text = doc.text[match.start():match.end()]

            results.append(
                RuleResult(
                    rule_id="CLAR001",
                    category="clarity",
                    severity=Severity.WARNING,
                    message=f"Vague instruction: '{matched_text}'.",
                    suggestion=suggestion,
                    score_impact=-8,
                    line=line_num,
                )
            )

    return results


def check_undefined_terminology(doc: PromptDocument) -> list[RuleResult]:
    """CLAR002: Detect acronyms/jargon used without definition."""
    results: list[RuleResult] = []

    # Find all-caps words (3+ characters)
    acronyms = re.findall(r"\b([A-Z]{3,})\b", doc.text)
    seen: set[str] = set()

    for acronym in acronyms:
        if acronym in seen or acronym in _COMMON_ABBREVIATIONS:
            continue
        seen.add(acronym)

        # Check if the term is defined nearby (within ~100 chars)
        # Look for patterns like "TERM (definition)" or "TERM: definition" or "TERM stands for"
        pattern = (
            rf"\b{re.escape(acronym)}\b\s*"
            rf"(?:\(|:|stands for|means|refers to|is (?:a|an|the))"
        )
        if re.search(pattern, doc.text):
            continue

        # Find line number
        match = re.search(rf"\b{re.escape(acronym)}\b", doc.text)
        line_num = doc.text[:match.start()].count("\n") + 1 if match else None

        results.append(
            RuleResult(
                rule_id="CLAR002",
                category="clarity",
                severity=Severity.INFO,
                message=f"Acronym '{acronym}' is used without definition.",
                suggestion=(
                    f"Consider defining '{acronym}' on first use, "
                    f"e.g., '{acronym} (Your Definition Here)'."
                ),
                score_impact=-3,
                line=line_num,
            )
        )

    return results


def check_ambiguous_references(doc: PromptDocument) -> list[RuleResult]:
    """CLAR003: Detect ambiguous pronoun references at paragraph starts."""
    results: list[RuleResult] = []

    # Split into paragraphs (blocks separated by blank lines)
    paragraphs: list[tuple[int, str]] = []
    current_lines: list[str] = []
    start_line = 1

    for i, line in enumerate(doc.lines, 1):
        if line.strip() == "":
            if current_lines:
                paragraphs.append((start_line, " ".join(current_lines)))
                current_lines = []
            start_line = i + 1
        else:
            if not current_lines:
                start_line = i
            current_lines.append(line.strip())

    if current_lines:
        paragraphs.append((start_line, " ".join(current_lines)))

    # Check paragraph-starting sentences for ambiguous pronouns
    # Only flag when starting a new paragraph (not mid-paragraph)
    ambiguous_starts = re.compile(
        r"^(It|This|That|These|Those)\s+(should|needs?|is|are|was|were|will|can|could|must|has|have|had)\b",
        re.IGNORECASE,
    )

    for line_num, para_text in paragraphs[1:]:  # Skip first paragraph
        match = ambiguous_starts.match(para_text.strip())
        if match:
            pronoun = match.group(1)
            results.append(
                RuleResult(
                    rule_id="CLAR003",
                    category="clarity",
                    severity=Severity.INFO,
                    message=f"Paragraph starts with ambiguous reference '{pronoun}'.",
                    suggestion=(
                        f"Replace '{pronoun}' with the specific noun it refers to "
                        f"for clarity (e.g., 'The output should...' instead of "
                        f"'{pronoun} should...')."
                    ),
                    score_impact=-3,
                    line=line_num,
                )
            )

    return results


def analyze_clarity(document: PromptDocument) -> list[RuleResult]:
    """Run all clarity analysis rules on a prompt document."""
    results: list[RuleResult] = []
    results.extend(check_vague_instructions(document))
    results.extend(check_undefined_terminology(document))
    results.extend(check_ambiguous_references(document))
    return results
