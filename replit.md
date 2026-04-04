# AKILI AI — CREOVA Autonomous Operating System

## Overview
AKILI is a multi-agent AI operating system for Justin Mafie and the CREOVA ecosystem. It runs as a Telegram bot and uses Claude to power 5 specialized agents. **Phase 3 active** — PULSE auto-scheduler, REACH auto-responder, INTEL live brief, and dashboard command API all running.

## Architecture

### Orchestrator
- **AKILI CORE** (`main.py`) — Routes commands to the right agent, runs heartbeat every 30 min, sends daily brief at 8AM, wires the IntegrationHub

### 5 Agents
- **SHIELD** (`agents/shield.py`) — Security, site uptime, API key protection; uses GitHubMonitor in heartbeat
- **PULSE** (`agents/pulse.py`) — Social media content + strategy for all CREOVA accounts
- **REACH** (`agents/reach.py`) — Email, DMs, content repurposing, outreach campaigns
- **INTEL** (`agents/intel.py`) — Market research, lead generation, daily briefs, VC tracking
- **AMPLIFY** (`agents/amplify.py`) — Music promotion, stream growth, brand experiments

### Integration Hub (`integrations/`)
- **Instagram** (`integrations/instagram.py`) — 4 accounts: @creativeinnovation__, @jj_mafie, @sankofastudio__, @creovasolutions
- **Twitter** (`integrations/twitter.py`) — @justin_mafie — Tweepy OAuth1 + client v2
- **LinkedIn** (`integrations/linkedin.py`) — Justin Mafie personal + CREOVA company page
- **Snapchat** (`integrations/snapchat.py`) — jay-mafie Creator program; content plans via Telegram
- **Facebook** (`integrations/facebook.py`) — Justin personal + CREOVA business
- **TikTok** (`integrations/tiktok.py`) — @creovamusic — music release planner
- **Gmail** (`integrations/gmail.py`) — Personal + business; email classification; first-auth helper
- **GitHub Monitor** (`integrations/github_monitor.py`) — 14 repos in creova-gif org; alerting in heartbeat

### Config (`config/accounts.py`)
- Single source of truth: all handles, credentials, schedules, content themes, cross-promo rules

### Memory System
- **MEMORY MANAGER** (`memory/manager.py`) — PARA structure (Projects/Areas/Resources/Archives)
- Stored at `./akili-life/`

## Required Secrets (add in Replit Secrets tab)
- `TELEGRAM_TOKEN` — From @BotFather
- `ANTHROPIC_API_KEY` — Anthropic key
- `JUSTIN_CHAT_ID` — Your Telegram user ID (from @userinfobot)

## Platform Secrets (optional — add to unlock each integration)
| Platform | Secrets needed |
|---|---|
| Instagram | `IG_USER_ID_*`, `IG_PAGE_ID_*`, `IG_TOKEN_*` (x4 accounts) |
| Twitter/X | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`, `TWITTER_BEARER_TOKEN` |
| LinkedIn | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_URN`, `LINKEDIN_COMPANY_URN` |
| Facebook | `FB_PAGE_ID_JUSTIN`, `FB_TOKEN_JUSTIN`, `FB_PAGE_ID_CREOVA`, `FB_TOKEN_CREOVA` |
| TikTok | `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`, `TIKTOK_OPEN_ID` |
| Gmail personal | Upload `config/gmail_personal_credentials.json`, run `python integrations/gmail.py personal` |
| Gmail business | Upload `config/gmail_business_credentials.json`, run `python integrations/gmail.py business` |
| GitHub | `GITHUB_TOKEN` |
| Snapchat | `SNAPCHAT_CLIENT_ID`, `SNAPCHAT_CLIENT_SECRET`, `SNAPCHAT_ACCESS_TOKEN` |

## Running
The workflow `Start application` runs `python main.py`.

## Telegram Commands
- `/start` — AKILI status + Phase 2 command list
- `/status` — Full system status from SHIELD
- Any natural language message → auto-routed

## Natural Language Routing (Phase 1 + Phase 2)
- `health check` / `integration status` → full platform status
- `follower count` / `follower snapshot` → cross-platform follower counts
- `github scan` / `github status` → 14-repo org scan
- `snapchat plan` / `snapchat content today` → today's Snapchat content
- `snapchat checklist` → Creator program tracker
- security/github/repo/uptime → SHIELD
- post/instagram/twitter/social/content/calendar → PULSE
- email/dm/repurpose/campaign → REACH
- research/lead/vc/investor/market/brief → INTEL
- music/stream/spotify/promote/growth/release → AMPLIFY
- anything else → AKILI general (Claude Opus)

## CREOVA Ventures Managed
1. Justin Mafie personal brand (@jj_mafie)
2. CREOVA Solutions (@creovasolutions)
3. CREOVA Media (creova.one)
4. CREOVA Music (@creativeinnovation__, @creovamusic)
5. Sankofa Studio (@sankofastudio__)
6. CREOVA Tech (14 GitHub repos at github.com/creova-gif)

## Markets
Tanzania, Kenya, Canada (St. Catharines, Ontario)

## Content Rules
- 30% Music / 30% Tech / 20% Personal / 20% Education
- Every post must mention at least one of: @creativeinnovation__, @creovasolutions, @sankofastudio__, creova.one
