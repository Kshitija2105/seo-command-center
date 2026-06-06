# SEO Command Center

A Claude Code agent pipeline that ingests a Screaming Frog SEO export, runs a 
12-rule audit, generates prioritised fixes, and delivers a client-ready report 
in HTML, PDF, and PPTX — all orchestrated through a live dashboard.

Built for nmg.labs Forge Sprint 01 · June 2026.

## Quick Start

```bash
pip install mcp
python run.py sample-export/
# Dashboard live at http://localhost:7700
# Outputs land in outputs/report.json, report.html, report.pdf, report.pptx
```

## Architecture

A central SKILL (`skills/seo-audit/SKILL.md`) coordinates four sub-agents:

- **Ingest agent** — parses the Screaming Frog CSV export into structured JSON
- **Auditor agent** — runs 12 deterministic SEO checks against the rulebook
- **Fixer agent** — generates title rewrites and a 301 redirect map for champion-tier fixes
- **Reporter agent** — renders the live dashboard and exports all three report formats

Ollama web search is used during the audit phase to validate live page status 
and redirect chains.

## Issue Types Detected

| Severity | Issue |
|----------|-------|
| High | Duplicate Title, Broken Link |
| Medium | Title Too Long, Duplicate Meta, Missing H1, Redirect, Missing Alt Text, Non-Indexable But Linked |
| Low | Title Too Short, Meta Too Long, Duplicate H1, Thin Content, Slow Page |

## Outputs

| File | Description |
|------|-------------|
| `outputs/report.json` | Raw audit results |
| `outputs/report.html` | Styled client-ready HTML report |
| `outputs/report.pdf` | Print-ready PDF |
| `outputs/report.pptx` | Executive summary slide deck |
| `outputs/fixes/title_rewrites.csv` | Suggested title fixes |
| `outputs/fixes/redirect_map.csv` | 301 redirect map |

## Stack

- Claude Code + Ollama (`gemma4:31b-cloud` / `qwen3.5:9b` local)
- `OLLAMA_CONTEXT_LENGTH=65536`
- Python · Shell · HTML · JavaScript

## Repo Structure

```
seo-command-center/
├── .claude-plugin/plugin.json     plugin manifest
├── .claude/                       audit hooks + settings
├── skills/seo-audit/SKILL.md      master orchestrator
├── agents/                        ingest, auditor, fixer, reporter
├── commands/seo-audit.md          the /seo-audit command
├── seo/detector.py                12-rule issue detector
├── mcp/server.py                  MCP server + dashboard host
├── dashboard/                     live cockpit (localhost:7700)
├── scripts/                       export-transcript + utilities
├── run.py                         headless runner (auto-tester entry point)
└── outputs/                       generated reports
```
## Memory Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project memory and agent instructions |
| `PROMPTS.md` | Key prompts used during the build |
| `DECISIONS.md` | Build decisions and fixes log |
| `agent-log.md` | Exported Claude Code session transcript |
| `.claude/audit.jsonl` | Auto-written tool call log |
