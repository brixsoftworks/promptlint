<div align="center">

# ⚡ PromptLint

### *Write prompts. Lint them. Test them. Ship them.*

The developer toolkit for testing, analyzing, optimizing, and versioning AI prompts.

[Live Playground](https://brixsoftworks.github.io/promptlint/) • [Documentation](docs/rules.md) • [VS Code Extension](extensions/vscode/) • [Report Bug](https://github.com/brixsoftworks/promptlint/issues)

[![Tests](https://github.com/brixsoftworks/promptlint/actions/workflows/tests.yml/badge.svg)](https://github.com/brixsoftworks/promptlint/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/promptlint/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](pyproject.toml)
[![MCP Server](https://img.shields.io/badge/MCP-Compatible-purple.svg)](src/promptlint/mcp_server.py)
[![VS Code](https://img.shields.io/badge/VS_Code-Extension-007ACC.svg)](extensions/vscode/)

<br>

```text
  PROMPTLINT
      │
┌─────┼─────┐
↓     ↓     ↓
LINT  FIX  TEST
│     │     │
└─────┼─────┘
      ↓
 SCORE ENGINE ── (Quality • Security • Cost)
```

</div>

---

## 🚀 Quickstart

Install PromptLint in seconds:

```bash
pip install promptlint
```

### 1. Score a Prompt File
```bash
promptlint score prompt.txt
```

### 2. Full Diagnostic Analysis
```bash
promptlint analyze prompt.txt
```

### 3. Security Scan (Offline API Key & Injection Protection)
```bash
promptlint security prompt.txt
```

### 4. Auto-Fix Prompt
```bash
promptlint fix prompt.txt --output fixed_prompt.txt
```

---

## 🔥 Features at a Glance

| Feature | Description |
| :--- | :--- |
| 🛡️ **Zero-Data Leak Security** | 100% offline scanner for AWS/OpenAI/GitHub secrets and prompt injection attacks. |
| ⚡ **Sub-10ms Rule Engine** | 25+ deterministic rules covering structure, clarity, ambiguity, conflicts, and cost. |
| 🤖 **Native MCP Server** | Exposes `lint_prompt` and `auto_fix_prompt` to **Claude Code**, **Antigravity**, and **Cursor**. |
| 🔌 **VS Code Extension** | Real-time red squiggly lint diagnostics in your IDE via Language Server Protocol (LSP). |
| 🐍 **Python AST Extractor** | Automatically extracts and lints prompt strings directly out of `.py` source code. |
| ✨ **Magic AI Rewriter** | Optional `--magic` flag to trigger LLM-driven prompt architecture optimization. |

---

## 🛠️ Usage & Commands

```text
Usage: promptlint [OPTIONS] COMMAND [ARGS]...

Commands:
  analyze     Analyze a prompt and report quality issues.
  score       Show only the quality score for a prompt.
  security    Run a security scan on a prompt.
  tokens      Show token count and size statistics.
  fix         Apply deterministic or magic improvements to a prompt.
  diff        Compare two prompt versions and show quality changes.
  mcp         Start the Model Context Protocol (MCP) Server.
  lsp         Start the Language Server Protocol (LSP) Server.
```

### Pipe & Stdin Support
```bash
echo "Write a blog post about AI. Make it good." | promptlint analyze -
```

### Interactive Mode (No Arguments)
Simply type `promptlint` in your terminal to launch the interactive terminal wizard:
```bash
promptlint
```

---

## 🤖 AI Agent Integration (MCP Server)

PromptLint implements the **Model Context Protocol (MCP)** natively. 

Add PromptLint to your MCP client configuration (Claude Code, Antigravity, Cursor):

```json
{
  "mcpServers": {
    "promptlint": {
      "command": "promptlint",
      "args": ["mcp"]
    }
  }
}
```

Now your AI coding agents can automatically lint their own generated prompts before running them!

---

## 📊 Rules Reference Matrix

| Rule ID | Category | Severity | Description |
| :--- | :--- | :--- | :--- |
| `SEC001` | Security | `CRITICAL` | Hardcoded secret key (AWS, OpenAI, GitHub, Anthropic) |
| `SEC002` | Security | `ERROR` | Potential prompt injection attempt / system override |
| `STRUCT001`| Structure | `WARNING` | Missing objective or clear task verb |
| `STRUCT002`| Structure | `WARNING` | Missing explicit output format specification |
| `STRUCT005`| Structure | `INFO` | Input context referenced without delimiter tags (`<context>` / ```) |
| `CLAR001` | Clarity | `WARNING` | Vague quality instructions (*"make it good"*, *"do your best"*) |
| `AMB004`  | Ambiguity | `WARNING` | Hallucination risk (*"feel free to guess"*, *"invent facts"*) |
| `CONF001` | Conflicts | `WARNING` | Contradictory instructions (e.g. JSON vs Markdown, Concise vs Detailed) |
| `EFF001`  | Efficiency | `WARNING` | Repeated instructions wasting tokens |
| `EFF004`  | Efficiency | `WARNING` | Negative constraint overload (4+ *"do not"* statements) |

---

## 🌐 Live Web Playground

Try PromptLint directly in your browser without installing anything:  
👉 **[brixsoftworks.github.io/promptlint](https://brixsoftworks.github.io/promptlint/)**

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
