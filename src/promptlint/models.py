"""Data models for PromptLint.

All typed data structures used throughout the application. Models are decoupled
from analysis logic, CLI rendering, and rule implementations. This module is
the shared vocabulary of the entire system.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity level for a rule finding.

    Ordered from least to most severe. Each level has a default score impact
    used by the scoring engine when a rule does not specify a custom impact.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Default score deductions per severity level.
# Rules can override these via RuleResult.score_impact.
SEVERITY_SCORE_IMPACT: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.WARNING: -10,
    Severity.ERROR: -15,
    Severity.CRITICAL: -25,
}


class RuleResult(BaseModel):
    """A single diagnostic finding from a lint rule.

    Every rule produces zero or more of these. The structure is intentionally
    generic so hundreds of rules can be added without changing the data model.
    """

    rule_id: str = Field(description="Unique rule identifier, e.g. STRUCT001")
    category: str = Field(description="Rule category, e.g. 'structure', 'clarity'")
    severity: Severity = Field(description="How severe the finding is")
    message: str = Field(description="Human-readable description of the issue")
    suggestion: str = Field(default="", description="Actionable suggestion to fix the issue")
    score_impact: int = Field(
        default=0,
        description="Custom score impact. If 0, the default for the severity level is used.",
    )
    line: int | None = Field(default=None, description="1-based line number, if applicable")
    column: int | None = Field(default=None, description="1-based column number, if applicable")

    def effective_score_impact(self) -> int:
        """Return the actual score deduction for this finding."""
        if self.score_impact != 0:
            return self.score_impact
        return SEVERITY_SCORE_IMPACT.get(self.severity, 0)


class PromptDocument(BaseModel):
    """Parsed representation of a prompt.

    Created by the parser from raw text. Provides pre-computed properties
    that rules can inspect without re-parsing.
    """

    text: str = Field(description="Original prompt text")
    lines: list[str] = Field(description="Lines of text (split on newlines)")
    character_count: int = Field(description="Total character count")
    word_count: int = Field(description="Total word count")
    line_count: int = Field(description="Total line count")


class CategoryScore(BaseModel):
    """Quality score for a single category (e.g. structure, clarity)."""

    name: str = Field(description="Category name")
    score: int = Field(ge=0, le=100, description="Score from 0 to 100")


class SecurityStatus(BaseModel):
    """Summary of security analysis findings."""

    has_secrets: bool = Field(default=False, description="Whether potential secrets were found")
    has_injection: bool = Field(default=False, description="Whether prompt injection patterns were found")
    finding_count: int = Field(default=0, description="Total number of security findings")


class PromptStatistics(BaseModel):
    """Token and size statistics for a prompt."""

    character_count: int
    word_count: int
    line_count: int
    estimated_tokens: int = Field(description="Approximate token count. Not exact without a real tokenizer.")


class AnalysisReport(BaseModel):
    """Complete analysis report for a prompt.

    This is the top-level output of the analysis pipeline. It aggregates
    all rule findings, computes scores, and includes metadata.
    """

    score: int = Field(ge=0, le=100, description="Overall PromptLint Quality Score (0-100)")
    rating: str = Field(description="Human-readable rating (Poor/Needs Work/Fair/Good/Excellent)")
    results: list[RuleResult] = Field(default_factory=list, description="All rule findings")
    category_scores: list[CategoryScore] = Field(default_factory=list, description="Per-category scores")
    statistics: PromptStatistics = Field(description="Prompt size/token statistics")
    security_status: SecurityStatus = Field(default_factory=SecurityStatus, description="Security analysis summary")

    @property
    def issue_count(self) -> int:
        """Total number of issues found (excludes info-level)."""
        return sum(1 for r in self.results if r.severity != Severity.INFO)

    @property
    def has_critical(self) -> bool:
        """Whether any critical-severity finding exists."""
        return any(r.severity == Severity.CRITICAL for r in self.results)
