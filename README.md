# PromptLint

**The developer toolkit for AI prompts.**

Write prompts. Lint them. Test them. Ship them.

---

PromptLint is a fast, offline-first linter and quality analyzer for AI prompts. It works like ESLint or Ruff — but for LLM prompts. No API keys required. No data leaves your machine.

## Installation

```bash
pip install promptlint
```

## Quick Start

```bash
# Analyze a prompt
promptlint analyze prompt.txt

# Score only
promptlint score prompt.txt

# Security scan
promptlint security prompt.txt

# Token count
promptlint tokens prompt.txt

# Fix structural issues
promptlint fix prompt.txt

# Compare two prompts
promptlint diff old.txt new.txt

# JSON output for CI/CD
promptlint analyze prompt.txt --json
```

## Example Output

```
 PromptLint 1.0.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 QUALITY SCORE                    74/100  (Fair)

 Structure                        82
 Clarity                          68
 Ambiguity                        71
 Efficiency                       79
 Security                         91

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 ⚠ STRUCT002   Missing output format
   Specify the expected output structure.

 ⚠ CLAR001     Vague instruction: 'make it better'
   Define what 'better' means: shorter, more
   accurate, more formal, or more detailed.

 ✕ SEC001      Possible secret detected
   Remove credentials from the prompt.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 3 issues found
```

## Features

- 🔍 **Lint** — Detect structural problems, vague instructions, ambiguity, conflicts, and inefficiencies
- 🛡️ **Security** — Find accidentally leaked API keys, tokens, passwords, and prompt injection patterns
- 📊 **Score** — Get a heuristic quality score (0-100) with per-category breakdown
- 🔧 **Fix** — Apply deterministic improvements without needing an LLM
- 📈 **Diff** — Compare two prompt versions and see quality changes
- ⚡ **Fast** — Instant analysis, no network calls, no API keys
- 🔒 **Private** — Your prompts never leave your machine

## Rules

| Category | Rules | Description |
|----------|-------|-------------|
| Structure | `STRUCT001`–`STRUCT004` | Missing objective, output format, constraints |
| Clarity | `CLAR001`–`CLAR003` | Vague instructions, undefined terms, ambiguous references |
| Ambiguity | `AMB001`–`AMB003` | Vague quantities, subjective quality, unclear references |
| Conflicts | `CONF001` | Contradictory instructions |
| Efficiency | `EFF001`–`EFF003` | Repeated instructions, excessive whitespace, overly long prompts |
| Security | `SEC001`–`SEC003` | Secrets, prompt injection, untrusted content mixing |

## Scoring

The **PromptLint Quality Score** is a heuristic metric — not a scientifically objective measurement.

| Score | Rating |
|-------|--------|
| 90–100 | Excellent |
| 75–89 | Good |
| 60–74 | Fair |
| 40–59 | Needs Work |
| 0–39 | Poor |

## Python API

```python
from promptlint import analyze

report = analyze("Write a poem about Python.")
print(f"Score: {report.score}/100 ({report.rating})")
for issue in report.results:
    print(f"  {issue.rule_id}: {issue.message}")
```

## Architecture

```
                    CLI
                     │
                     ▼
               Command Layer
                     │
                     ▼
               Prompt Parser
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Quality     Security     Token
      Analyzer    Analyzer     Analyzer
          │          │          │
          └──────────┼──────────┘
                     ▼
                Score Engine
                     │
                     ▼
                Report Engine
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       Terminal               JSON
```

The core analyzer works completely offline. No network calls. No telemetry. No analytics.

## Privacy & Security

- ✅ Core analysis is 100% offline
- ✅ No telemetry or analytics
- ✅ No hidden API calls
- ✅ Your prompts never leave your machine
- ✅ MIT licensed

## Configuration

Create a `.promptlintrc.toml` file:

```toml
disabled_rules = ["EFF003"]

[severity_overrides]
STRUCT002 = "info"
```

## Roadmap

- [x] v1.0 — Core linting, scoring, fixing, diffing
- [ ] v2.0 — `promptlint test` with model adapters, benchmarking
- [ ] v3.0 — GitHub Action, VS Code extension, web playground

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
