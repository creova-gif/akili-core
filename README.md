# Akili Core

**A multi-agent automation platform — modular agents for monitoring, outreach, and operational tasks, coordinated through a central dispatcher.**

[![Status](https://img.shields.io/badge/status-active_development-yellow)]()
[![License](https://img.shields.io/badge/license-proprietary-red)]()

> **This is a personal automation tool, not a product for external users.** This README intentionally describes architecture and capability without exposing operational specifics (which accounts, what cadence, what's actually being monitored) — that stays out of version control by design.

## Overview

A modular multi-agent system: independent Python agents, each responsible for one category of task, coordinated through a shared dispatcher and API layer.

## Problem

Running several small automations (monitoring, outreach, operational tasks) independently means duplicating scheduling, auth, and boilerplate for each one.

## Solution

A shared dispatcher and API layer that agents plug into, so each new automation only needs its own task logic — not its own scheduling/auth/credential handling.

## Architecture

- `agents/` — each agent is a self-contained module (monitoring, outreach, system health, content, research), addable/removable independently
- `api/` — shared request handling across agents
- Dispatcher pattern — agents are invoked through a common interface rather than managing their own scheduling/auth

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python (`uv` for dependency management) |
| LLM | Anthropic Claude |
| Messaging | Telegram Bot API |
| Scheduling | `schedule` |
| System monitoring | `psutil` |

## Testing

`test_apis.py` and `test_system.py` exist but are manual diagnostic/smoke-test scripts (print-based output, no assertions, no pytest fixtures) — not an automated test suite. Treat this repo as Level 1 maturity on testing, not higher, until real pytest coverage exists.

## Security

This repo went through a real hardening pass: a previously-committed API key was found in git history (not current code) and has been purged from history and rotated. Personal operational data (logs, activity tracking) has been removed from git history entirely and is now git-ignored going forward. Never commit `.env`, credentials, or any file under a personal-data path.

## Getting Started

```bash
git clone https://github.com/creova-gif/akili-core.git
cd akili-core
uv sync
cp .env.example .env
# fill in your own keys in .env — this file is git-ignored
```

## Project Status

Active development. Real, working automation infrastructure; testing maturity is genuinely Level 1 (manual scripts, not automated assertions) — don't overstate it.

## Contributing

Personal, proprietary project. External contributions are not accepted at this time.

## License

Proprietary — All Rights Reserved. See `LICENSE`.

## Author / Organization

Built by [Justin Mafie](https://github.com/creova-gif).

## Documentation

See `CLAUDE.md` for AI-agent-specific notes on the testing-maturity distinction.
