# Scoring Methodology

This document outlines the scoring methodology and rating system used by PromptLint to evaluate AI prompt quality.

---

## Heuristic Metric Notice

> **Important Notice:** The PromptLint Quality Score is a **heuristic developer-assistance metric**, not a scientifically objective or definitive measurement of prompt effectiveness.
>
> Static analysis can identify structural deficiencies, ambiguous phrasing, conflicting constraints, token waste, and potential security hazards. However, prompt performance depends heavily on the downstream model architecture, temperature settings, domain data, and task nuance. Use this score as a guide for best practices and CI/CD quality gates, not as an absolute guarantee of model reasoning performance.

---

## The 0–100 Scoring Scale

Every prompt starts with a baseline score of **100 points**. As the analysis engine evaluates the prompt against registered rules, deductions are calculated based on diagnostic findings:

$$\text{Overall Score} = \max\left(0, \min\left(100, 100 + \sum \text{Effective Score Impact}\right)\right)$$

The resulting score is clamped between `0` and `100`.

---

## Severity Deductions

Each diagnostic finding (`RuleResult`) has an associated `Severity` level with default deduction values:

| Severity Level | Default Score Impact | Intended Purpose |
| :--- | :--- | :--- |
| **`INFO`** | `0` (or -2 to -5 custom) | Stylistic suggestions, best practices, minor formatting improvements. |
| **`WARNING`** | `-10` (or -5 to -15 custom) | High-probability ambiguities, missing formats, structural gaps, or conflicts. |
| **`ERROR`** | `-15` | Critical ambiguities or high-risk injection patterns. |
| **`CRITICAL`** | `-25` | Critical security findings such as exposed API keys, private keys, or passwords. |

### Custom Rule Impacts

Individual rules can customize their deduction weight by specifying a non-zero `score_impact` in the `RuleResult`. For example:
- `EFF002` (Excessive Whitespace) specifies a light impact of `-2`.
- `CLAR002` (Undefined Terminology) specifies `-3`.
- `STRUCT002` (Missing Output Format) specifies `-8`.
- `CONF001` (Conflicting Instructions) specifies `-15`.
- `SEC001` (Exposed Secrets) specifies `-25`.

When `score_impact == 0`, the default severity deduction is applied.

---

## Rating Labels

The numeric score (0–100) maps directly to five human-readable rating tiers:

| Score Range | Rating Label | Interpretation & Recommended Action |
| :--- | :--- | :--- |
| **90 – 100** | **`Excellent`** | High quality. The prompt has clear objectives, explicit output formatting, well-defined constraints, and no detectable security issues. Ready for production. |
| **75 – 89** | **`Good`** | Solid prompt with minor opportunities for improvement (e.g., adding explicit constraints, defining acronyms, or trimming whitespace). |
| **60 – 74** | **`Fair`** | Acceptable, but contains noticeable ambiguities, vague instructions (*"make it better"*), or lacks output structure. |
| **40 – 59** | **`Needs Work`** | Substantial issues present. The prompt may lack clear objectives, contain conflicting requirements, or exhibit repetitive phrasing. |
| **0 – 39** | **`Poor`** | Critical issues found. The prompt contains severe structural failures, major contradictions, or exposed credentials/secrets. |

---

## Per-Category Scores

PromptLint computes independent scores for each rule category, allowing developers to immediately isolate areas that need attention.

Each category score begins at **100** and is calculated exclusively from the rule findings within that category:

$$\text{Category Score} = \max\left(0, \min\left(100, 100 + \sum_{\text{finding} \in \text{Category}} \text{Effective Score Impact}\right)\right)$$

### Scored Categories

1. **Structure:** Measures whether the prompt contains an actionable objective, output formatting requirements, operational boundaries, and instructional context.
2. **Clarity:** Evaluates the specificity of directives and the absence of undefined jargon and dangling pronouns.
3. **Ambiguity:** Quantifies the avoidance of subjective quality terms (*"high quality"*, *"clean"*) and imprecise quantities (*"a few"*, *"some"*).
4. **Conflicts:** Assesses internal logical consistency and the absence of contradictory instructions.
5. **Efficiency:** Measures conciseness, absence of duplicate sentences, and clean whitespace utilization.
6. **Security:** Evaluates isolation of untrusted input and absence of credential leaks or injection patterns.

---

## Token & Metric Estimation

In addition to quality scoring, PromptLint computes basic size metrics:

- **Character Count:** Exact string character count.
- **Word Count:** Total whitespace-delimited words.
- **Line Count:** Number of lines in the input.
- **Estimated Tokens:** Approximation calculated using the heuristic:

$$\text{Estimated Tokens} = \lceil \text{Word Count} \times 1.3 \rceil$$

> **Note:** Token estimation is a lightweight approximation suitable for English text. For exact token counts against specific models (e.g., GPT-4, Claude 3.5, Llama 3), use model-specific tokenizers (e.g., `tiktoken`, `tokenizers`).

---

## CI/CD Exit Codes

When running `promptlint analyze` in automated pipelines:

- **Exit Code `0`:** No warnings, errors, or critical issues found. (Info-level findings do not fail builds).
- **Exit Code `1`:** One or more issues (Warning or Error level) detected.
- **Exit Code `2`:** Critical issues found (such as exposed credentials or severe vulnerabilities).
