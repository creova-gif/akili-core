# AKILI AI — CREOVA Autonomous Operating System

## Overview
AKILI is a multi-agent AI operating system for Justin Mafie and the CREOVA ecosystem. It runs as a Telegram bot and uses Claude to power 5 specialized agents that handle security, social media, communications, research, and music promotion.

## Architecture

### Orchestrator
- **AKILI CORE** (`main.py`) — Routes commands to the right agent, runs heartbeat every 30 min, sends daily brief at 8AM

### 5 Agents
- **SHIELD** (`agents/shield.py`) — Security, GitHub repo monitoring (14 repos), site uptime, API key protection
- **PULSE** (`agents/pulse.py`) — Social media content for all Justin Mafie + CREOVA brand accounts
- **REACH** (`agents/reach.py`) — Email, WhatsApp, SMS, DMs, content repurposing
- **INTEL** (`agents/intel.py`) — Market research, lead generation, daily briefs, VC tracking
- **AMPLIFY** (`agents/amplify.py`) — Music promotion, stream growth, brand experiments

### Memory System
- **MEMORY MANAGER** (`memory/manager.py`) — PARA structure (Projects/Areas/Resources/Archives)
- Stored at `./akili-life/` directory
- Daily logs at `./akili-life/logs/daily/YYYY-MM-DD.md`

## Required Secrets (add in Replit Secrets tab)
- `TELEGRAM_TOKEN` — From @BotFather on Telegram
- `ANTHROPIC_API_KEY` — Your Anthropic API key
- `JUSTIN_CHAT_ID` — Your Telegram user ID (from @userinfobot)

## Optional Secrets
- `GITHUB_TOKEN` — For GitHub repo monitoring via SHIELD

## Dependencies
- anthropic >= 0.40.0
- python-telegram-bot >= 21.0
- aiohttp >= 3.9.0
- schedule >= 1.2.0
- python-dotenv >= 1.0.0

## Running
The workflow `Start application` runs `python main.py`. AKILI will:
1. Start if all 3 required secrets are present
2. Print clear error if secrets are missing

## Telegram Commands
- `/start` — Wake up AKILI, confirms all 5 agents are active
- `/status` — Full system status from SHIELD

## Natural Language Routing
Any message is auto-routed by keyword matching:
- security/github/repo/uptime → SHIELD
- post/instagram/twitter/social/content → PULSE
- email/whatsapp/dm/repurpose/campaign → REACH
- research/lead/vc/investor/market/brief → INTEL
- music/stream/spotify/promote/growth → AMPLIFY
- anything else → AKILI general (Claude Opus)

## CREOVA Ventures Managed
1. Justin Mafie personal brand (@jj_mafie)
2. CREOVA Solutions (@creovasolutions)
3. CREOVA Media (creova.one)
4. CREOVA Music (@creativeinnovation__)
5. Sankofa Studio (@sankofastudio__)
6. CREOVA Tech (14 GitHub repos at github.com/creova-gif)

## Markets
Tanzania, Kenya, Canada (Halton Hills, Ontario)
