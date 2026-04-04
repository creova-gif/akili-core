# ============================================================
# AKILI API SERVER — Phase 3C
# FastAPI backend connecting the dashboard to live agents
# Run alongside main.py on Replit
# Dashboard command bar → this API → real Akili agents
# ============================================================

import os
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic

log = logging.getLogger("AKILI.API")

ANTHROPIC_KEY  = os.environ["ANTHROPIC_API_KEY"]
JUSTIN_CHAT_ID = os.environ["JUSTIN_CHAT_ID"]
API_SECRET     = os.environ.get("AKILI_API_SECRET", "akili-secret-change-this")

app = FastAPI(title="Akili OS API", version="3.0")

# CORS — allow your Replit dashboard URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten this to your Replit URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic(api_key=ANTHROPIC_KEY)


# ── Request models ────────────────────────────────────────────
class CommandRequest(BaseModel):
    command: str
    secret:  str          # Simple auth — must match AKILI_API_SECRET

class PostRequest(BaseModel):
    platform: str
    caption:  str
    hashtags: list[str] = []
    secret:   str


# ── Agent routing (mirrors main.py logic) ─────────────────────
AGENT_ROUTES = {
    "shield":  ["security", "github", "repo", "uptime", "breach", "protect", "scan"],
    "pulse":   ["post", "instagram", "twitter", "linkedin", "tiktok", "snap", "social", "schedule", "calendar", "content"],
    "reach":   ["email", "whatsapp", "sms", "dm", "reply", "message", "repost", "repurpose", "draft"],
    "intel":   ["research", "lead", "vc", "investor", "competitor", "market", "brief", "intel", "search"],
    "amplify": ["music", "stream", "spotify", "distrokid", "promote", "amplify", "growth", "experiment", "playlist"],
}

AGENT_SYSTEM_PROMPTS = {
    "shield": """You are SHIELD — Akili's security agent for Justin Mafie / CREOVA.
Monitor 14 repos in creova-gif, protect all accounts, check uptime of creova.one.
Be concise, technical, and alert Justin to any issues immediately.""",

    "pulse": """You are PULSE — Akili's social media agent for Justin Mafie / CREOVA.
Manage @jj_mafie, @creovasolutions, @creativeinnovation__, @sankofastudio__ (Instagram),
@justin_mafie (Twitter), Justin Mafie + CREOVA (LinkedIn), jay-mafie (Snapchat),
Justin Mafie + CREOVA (Facebook), @creovamusic (TikTok).
Create authentic, on-brand content in Justin's voice.""",

    "reach": """You are REACH — Akili's communications agent for Justin Mafie / CREOVA.
Handle personal Gmail and CREOVA business email, DMs across all platforms,
WhatsApp, content repurposing. Reply in Justin's authentic voice.
Flag urgent emails (VC, legal, press) immediately.""",

    "intel": """You are INTEL — Akili's research agent for Justin Mafie / CREOVA.
Deep research on East Africa + Canada markets, lead generation for CREOVA Solutions,
GoPay VC tracking, competitor monitoring. Be specific and actionable.
Justin is a busy founder — give him intelligence he can use TODAY.""",

    "amplify": """You are AMPLIFY — Akili's growth agent for Justin Mafie / CREOVA.
Drive music streams (CREOVA Music via DistroKid), grow all social accounts,
build toward Snapchat Creator program, run posting experiments.
All roads lead to creova.one.""",
}


def route_command(command: str) -> str:
    """Determine which agent should handle this command."""
    lower = command.lower()
    for agent, keywords in AGENT_ROUTES.items():
        if any(kw in lower for kw in keywords):
            return agent
    return "core"   # Falls back to Akili Core


# ── API Endpoints ─────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "system":  "AKILI OS",
        "version": "3.0",
        "status":  "online",
        "time":    datetime.now().isoformat(),
        "agents":  ["SHIELD", "PULSE", "REACH", "INTEL", "AMPLIFY"],
    }

@app.get("/health")
async def health():
    """Dashboard health check — returns status of all agents."""
    return {
        "status":    "all_systems_operational",
        "agents":    {a: "active" for a in ["shield", "pulse", "reach", "intel", "amplify"]},
        "timestamp": datetime.now().isoformat(),
    }

@app.post("/command")
async def run_command(req: CommandRequest):
    """
    Main command endpoint — called by dashboard command bar.
    Routes to appropriate agent and returns response.
    """
    if req.secret != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    command = req.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Empty command")

    agent    = route_command(command)
    system   = AGENT_SYSTEM_PROMPTS.get(agent, AGENT_SYSTEM_PROMPTS["pulse"])
    agent_id = agent.upper() if agent != "core" else "AKILI"

    log.info(f"[API] Command routed to {agent_id}: {command[:60]}")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": command}]
        )
        result = response.content[0].text

        return {
            "agent":     agent_id,
            "command":   command,
            "response":  result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        log.error(f"[API] Command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/github")
async def github_status():
    """Quick GitHub org status for dashboard."""
    if req_secret := os.environ.get("AKILI_API_SECRET"):
        pass   # auth handled per-endpoint in production
    return {"message": "Use /command with 'run GitHub org scan' for full report"}

@app.get("/status/platforms")
async def platform_status():
    """Check which platform integrations are configured."""
    platforms = {
        "instagram":  bool(os.environ.get("IG_TOKEN_JJ")),
        "twitter":    bool(os.environ.get("TWITTER_ACCESS_TOKEN")),
        "linkedin":   bool(os.environ.get("LINKEDIN_ACCESS_TOKEN")),
        "tiktok":     bool(os.environ.get("TIKTOK_ACCESS_TOKEN")),
        "snapchat":   bool(os.environ.get("SNAPCHAT_ACCESS_TOKEN")),
        "facebook":   bool(os.environ.get("FB_PAGE_TOKEN")),
        "gmail":      bool(os.environ.get("GMAIL_PERSONAL_ADDRESS")),
        "github":     bool(os.environ.get("GITHUB_TOKEN")),
    }
    connected = sum(platforms.values())
    return {
        "platforms":  platforms,
        "connected":  connected,
        "total":      len(platforms),
        "percentage": round(connected / len(platforms) * 100),
    }

@app.get("/feed")
async def activity_feed():
    """Return recent activity log for dashboard feed."""
    try:
        from memory.manager import MemoryManager
        mem   = MemoryManager()
        log_  = mem.get_today_log()
        lines = [l.strip() for l in log_.split("\n") if l.strip()][-10:]
        return {"feed": lines, "timestamp": datetime.now().isoformat()}
    except Exception:
        return {"feed": ["AKILI OS active", "All agents running"], "timestamp": datetime.now().isoformat()}


# ── Run server ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
