# CLAUDE.md — akili-core

## Project Overview
Autonomous multi-agent AI OS running CREOVA's own operations (scheduling, monitoring, research agents). Python, `uv` package manager, Telegram + Anthropic API integration.

## Testing — Known Gap
`test_apis.py` and `test_system.py` exist but are **manual diagnostic/smoke-test scripts** (print-based, no `assert` statements, no pytest fixtures), not an automated test suite. Do not describe this repo as having real automated test coverage — it doesn't yet. If asked to add real tests, use `pytest` with actual assertions; don't just extend the existing print-based scripts.

## Technology Stack
Python 3.11+, `uv` for dependency management (`uv sync`), `anthropic`, `python-telegram-bot`, `aiohttp`.

## Repository Structure
`agents/` — individual agent implementations (e.g. `ShieldAgent`, `IntelAgent`). `dashboard.py` — status dashboard. `main.py` — entry point.

## CI
`uv sync` then attempts `pytest`, falling back to running `test_system.py` directly — reflects the current manual-script reality rather than pretending a real suite exists.

## AI Agent Rules
- Don't claim "Level 3" or "unit-tested" maturity for this repo — it's genuinely Level 1 (manual verification scripts only) until real pytest coverage is added.
- New agents should follow the existing agent class pattern in `agents/`.

## Definition of Done
If you add real tests, they use pytest with assertions. State clearly whether new code has real automated coverage or just a manual verification script, and don't conflate the two.
