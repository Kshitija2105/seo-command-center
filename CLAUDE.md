# SEO Command Center — Project Memory

## Goal
Build a Claude Code plugin that audits a Screaming Frog export and produces client-ready reports.

## Architecture
- run.py → orchestrator
- seo/detector.py → all issue detection (deterministic, no model calls)
- mcp/server.py → MCP server + dashboard at localhost:7700
- outputs/report.json + outputs/report.html → deliverables

## Rules
- Never feed raw CSV rows to the model
- Detect issues in pure Python (pandas/csv)
- Always validate report.json against schema before committing
- Keep context tight, one task per prompt

## Key constraints
- 8GB RAM Intel Mac, Track A cloud quota
- Model: gemma4:31b-cloud via Ollama
