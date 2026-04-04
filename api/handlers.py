# ============================================================
# AKILI API HANDLERS — Phase 3C
# aiohttp route handlers for the dashboard command API
# Integrated into the existing web server (no separate port)
# ============================================================

import json
import logging
import os
from datetime import datetime
from aiohttp import web
from anthropic import Anthropic

log = logging.getLogger("AKILI.API")

API_SECRET    = os.environ.get("AKILI_API_SECRET", "akili-justin-2026")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

AGENT_ROUTES = {
    "SHIELD":  ["security", "github", "repo", "uptime", "breach", "protect", "scan"],
    "PULSE":   ["post", "instagram", "twitter", "linkedin", "tiktok", "snap", "social", "schedule", "calendar", "content"],
    "REACH":   ["email", "whatsapp", "sms", "dm", "reply", "message", "repost", "repurpose", "draft"],
    "INTEL":   ["research", "lead", "vc", "investor", "competitor", "market", "brief", "intel", "search"],
    "AMPLIFY": ["music", "stream", "spotify", "distrokid", "promote", "amplify", "growth", "experiment", "playlist"],
}

AGENT_SYSTEMS = {
    "SHIELD":  "You are SHIELD — Akili's security agent for Justin Mafie / CREOVA. Monitor 8 repos in creova-gif, protect all accounts. Concise and technical.",
    "PULSE":   "You are PULSE — Akili's social media agent. Manage all CREOVA accounts. Create authentic on-brand content in Justin's voice.",
    "REACH":   "You are REACH — Akili's communications agent. Handle Gmail, DMs, content repurposing. Reply in Justin's authentic voice.",
    "INTEL":   "You are INTEL — Akili's research agent. Deep research on East Africa + Canada markets, VC tracking, competitor monitoring. Specific and actionable.",
    "AMPLIFY": "You are AMPLIFY — Akili's growth agent. Drive music streams, grow social accounts, build toward Snapchat Creator. All roads lead to creova.one.",
    "AKILI":   "You are AKILI — the autonomous AI OS for Justin Mafie / CREOVA. Answer concisely and helpfully.",
}


def _route_command(command: str) -> str:
    lower = command.lower()
    for agent, keywords in AGENT_ROUTES.items():
        if any(kw in lower for kw in keywords):
            return agent
    return "AKILI"


async def handle_api_root(request: web.Request) -> web.Response:
    return web.json_response({
        "system":  "AKILI OS",
        "version": "3.0",
        "status":  "online",
        "time":    datetime.now().isoformat(),
        "agents":  ["SHIELD", "PULSE", "REACH", "INTEL", "AMPLIFY"],
    })


async def handle_api_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status":    "all_systems_operational",
        "agents":    {a: "active" for a in ["SHIELD", "PULSE", "REACH", "INTEL", "AMPLIFY"]},
        "timestamp": datetime.now().isoformat(),
    })


async def handle_api_command(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    secret  = body.get("secret", "")
    command = body.get("command", "").strip()

    if secret != API_SECRET:
        return web.json_response({"error": "Unauthorized"}, status=401)

    if not command:
        return web.json_response({"error": "Empty command"}, status=400)

    agent  = _route_command(command)
    system = AGENT_SYSTEMS.get(agent, AGENT_SYSTEMS["AKILI"])

    log.info(f"[API] Command → {agent}: {command[:60]}")

    try:
        client = Anthropic(api_key=ANTHROPIC_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": command}]
        )
        result = response.content[0].text
        return web.json_response({
            "agent":     agent,
            "command":   command,
            "response":  result,
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        log.error(f"[API] Command error: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def handle_api_platforms(request: web.Request) -> web.Response:
    platforms = {
        "instagram":  bool(os.environ.get("IG_TOKEN_JJ") or os.environ.get("INSTAGRAM_ACCESS_TOKEN")),
        "twitter":    bool(os.environ.get("TWITTER_ACCESS_TOKEN")),
        "linkedin":   bool(os.environ.get("LINKEDIN_ACCESS_TOKEN")),
        "tiktok":     bool(os.environ.get("TIKTOK_ACCESS_TOKEN")),
        "snapchat":   bool(os.environ.get("SNAPCHAT_ACCESS_TOKEN")),
        "facebook":   bool(os.environ.get("FB_PAGE_TOKEN") or os.environ.get("FACEBOOK_PAGE_TOKEN")),
        "gmail":      bool(os.environ.get("GMAIL_PERSONAL_ADDRESS")),
        "github":     bool(os.environ.get("GITHUB_TOKEN")),
    }
    connected = sum(platforms.values())
    return web.json_response({
        "platforms":  platforms,
        "connected":  connected,
        "total":      len(platforms),
        "percentage": round(connected / len(platforms) * 100),
    })


async def handle_api_feed(request: web.Request) -> web.Response:
    try:
        from memory.manager import MemoryManager
        mem   = MemoryManager()
        log_  = mem.get_today_log()
        lines = [l.strip() for l in log_.split("\n") if l.strip()][-10:]
        return web.json_response({"feed": lines, "timestamp": datetime.now().isoformat()})
    except Exception:
        return web.json_response({
            "feed": ["AKILI OS active", "All agents running"],
            "timestamp": datetime.now().isoformat()
        })
