# Akili Core

**A multi-agent automation platform — modular agents for monitoring, outreach, and operational tasks, coordinated through a central dispatcher.**

[![Status](https://img.shields.io/badge/status-active_development-yellow)]()
[![License](https://img.shields.io/badge/license-proprietary-red)]()

> **This is a personal automation tool, not a product for external users.** The README below intentionally describes architecture and capability at a level that doesn't expose operational specifics (which accounts, what cadence, what's actually being monitored) — that information stays out of version control by design. See `SECURITY.md` conventions below before contributing to or forking this pattern.

---

## What this is

Akili Core is a modular multi-agent system: a set of independent Python agents, each responsible for one category of task, coordinated through a shared dispatcher and API layer. It's built as a personal automation platform, not a SaaS product — think of it as infrastructure for running several small, focused automations without duplicating boilerplate for each one.

---

## Architecture

- **Agents** (`agents/`) — each agent is a self-contained module handling one responsibility (monitoring, outreach, system health, content, research). Agents are designed to be added or removed independently.
- **API layer** (`api/`) — request handling shared across agents
- **Dispatcher pattern** — agents are invoked through a common interface rather than each managing their own scheduling/auth independently

This structure is the actual reusable/interesting part of this repo — a clean pattern for running multiple small automated agents against a shared credential and scheduling layer, if you're building something similar.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| LLM | Anthropic Claude |
| Messaging | Telegram Bot API |
| Scheduling | `schedule` |
| System monitoring | `psutil` |

*(Specific third-party integrations beyond what's listed above are intentionally not detailed here.)*

---

## Security Notes (read before touching this repo)

This repo went through a security hardening pass:
- A previously-committed API key was found in git history (not current code) and has been **purged from all history and rotated**.
- Personal operational data (logs, activity tracking) has been **removed from git history entirely** and is now git-ignored going forward — this repo's history no longer contains that data at any point.
- If you fork or extend this: **never commit `.env`, credentials, or any file under a personal-data path.** Check `.gitignore` before adding new data-producing agents.

---

## Getting Started (Local Dev)

### Prerequisites
- Python 3.10+
- Your own API keys (Anthropic, Telegram Bot token, any other integration you enable) — **never commit these**

### Installation

```bash
git clone https://github.com/creova-gif/Akili-Core.git
cd Akili-Core
pip install -r requirements.txt
cp .env.example .env
# fill in your own keys in .env — this file is git-ignored
```

---

## Contributing

This is a personal, proprietary project. External contributions are not accepted at this time.

## License

Proprietary — All Rights Reserved. See `LICENSE`.

## Credits

Built by Justin Mafie / CREOVA.
