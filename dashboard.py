# ============================================================
# AKILI DASHBOARD — Mission Control
# New OS-style UI with sidebar, agent modals, live feed
# ============================================================

import os
import json
import re
import logging
from datetime import datetime, date
from aiohttp import web

log = logging.getLogger("AKILI.Dashboard")

# ── Data helpers ─────────────────────────────────────────────

def _streak_data() -> dict:
    try:
        with open("akili-life/logs/snapchat_streak.json") as f:
            return json.load(f)
    except Exception:
        return {"streak": 0, "last_posted": "—", "total_days": 0}


def _recent_activity(n: int = 12) -> list[dict]:
    entries = []
    try:
        with open("logs/akili.log") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \| (\w+) \| ([^\|]+) \| (.+)$", line)
                if m:
                    ts, level, source, msg = m.groups()
                    source = source.strip()
                    msg = msg.strip()
                    if "terminated by other getUpdates" in msg:
                        continue
                    if "httpx" in source:
                        continue
                    if "HEARTBEAT" in msg and "OK" in msg:
                        continue
                    entries.append({
                        "ts": ts[11:16],
                        "date": ts[:10],
                        "level": level,
                        "source": source,
                        "msg": msg[:90] + ("…" if len(msg) > 90 else ""),
                    })
    except Exception:
        pass
    return entries[-n:]


def _integration_status() -> dict:
    env = os.environ
    return {
        "twitter":   {"label": "Twitter / X",  "handle": "@justin_mafie",        "icon": "𝕏",  "ok": bool(env.get("TWITTER_API_KEY"))},
        "github":    {"label": "GitHub",        "handle": "creova-gif · 8 repos", "icon": "🐙", "ok": bool(env.get("GITHUB_TOKEN"))},
        "instagram": {"label": "Instagram",     "handle": "4 accounts",           "icon": "📸", "ok": os.path.exists("config/instagram_token.json")},
        "linkedin":  {"label": "LinkedIn",      "handle": "Justin + CREOVA",      "icon": "💼", "ok": bool(env.get("LINKEDIN_ACCESS_TOKEN"))},
        "snapchat":  {"label": "Snapchat",      "handle": "jay-mafie",            "icon": "👻", "ok": bool(env.get("SNAPCHAT_ACCESS_TOKEN"))},
        "tiktok":    {"label": "TikTok",        "handle": "@creovamusic",         "icon": "🎵", "ok": bool(env.get("TIKTOK_ACCESS_TOKEN"))},
        "facebook":  {"label": "Facebook",      "handle": "Justin + CREOVA Biz",  "icon": "📘", "ok": bool(env.get("FACEBOOK_ACCESS_TOKEN"))},
        "gmail":     {"label": "Gmail",         "handle": "Personal + Business",  "icon": "📧", "ok": os.path.exists("config/gmail_business_token.json")},
    }


def _github_repos() -> list[str]:
    return ["Gopay", "KayaYourpropertyai", "Darsme", "Mentalpath",
            "Aihealthsupport", "GridOs", "Kilimoai", "Budgeteaseapp"]


# ── API endpoint ─────────────────────────────────────────────

async def handle_api_status(request: web.Request) -> web.Response:
    streak = _streak_data()
    integrations = _integration_status()
    activity = _recent_activity(15)
    connected = sum(1 for v in integrations.values() if v["ok"])

    payload = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "uptime_since": _uptime(),
        "agents": {
            "SHIELD":  {"desc": "Security & GitHub monitor", "status": "active"},
            "PULSE":   {"desc": "Social media publisher",    "status": "active"},
            "REACH":   {"desc": "Email & outreach",          "status": "active"},
            "INTEL":   {"desc": "Market & trend analysis",   "status": "active"},
            "AMPLIFY": {"desc": "Growth & engagement",       "status": "active"},
        },
        "integrations": integrations,
        "integrations_connected": connected,
        "snapchat_streak": streak,
        "github_repos": _github_repos(),
        "activity": activity,
    }
    return web.json_response(payload)


_start_time = datetime.utcnow()
def _uptime() -> str:
    delta = datetime.utcnow() - _start_time
    h, rem = divmod(int(delta.total_seconds()), 3600)
    m = rem // 60
    return f"{h}h {m}m"


# ── Main dashboard page ───────────────────────────────────────

async def handle_dashboard(request: web.Request) -> web.Response:
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8080")
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="tiktok-developers-site-verification" content="ZOEgJ9JW9DI1DsSJngcQTHQLHJcMe7Ob"/>
<title>AKILI — Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
:root {
  --bg:      #080A0F;
  --bg2:     #0D1018;
  --bg3:     #131720;
  --border:  rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.13);
  --text:    #F0EDE8;
  --muted:   #6B7280;
  --accent:  #E8C547;
  --accent2: #4ECDC4;
  --accent3: #FF6B6B;
  --green:   #22C55E;
  --orange:  #F97316;
  --purple:  #A78BFA;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;min-height:100vh;overflow-x:hidden}
.mono{font-family:'JetBrains Mono',monospace}

body::before{
  content:'';position:fixed;inset:0;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events:none;z-index:0;opacity:0.4;
}

.shell{display:grid;grid-template-columns:72px 1fr;min-height:100vh;position:relative;z-index:1}

/* Sidebar */
.sidebar{
  background:var(--bg2);border-right:1px solid var(--border);
  display:flex;flex-direction:column;align-items:center;padding:24px 0;gap:8px;
  position:sticky;top:0;height:100vh;
}
.sidebar-logo{
  width:40px;height:40px;border-radius:10px;
  background:linear-gradient(135deg,var(--accent),#F59E0B);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;font-weight:800;color:#000;margin-bottom:16px;letter-spacing:-1px;
}
.nav-btn{
  width:44px;height:44px;border-radius:10px;border:none;background:transparent;
  color:var(--muted);cursor:pointer;display:flex;align-items:center;justify-content:center;
  font-size:18px;transition:all 0.15s;position:relative;
}
.nav-btn:hover{background:var(--bg3);color:var(--text)}
.nav-btn.active{background:rgba(232,197,71,0.12);color:var(--accent)}
.nav-btn.active::before{
  content:'';position:absolute;left:0;top:50%;transform:translateY(-50%);
  width:3px;height:20px;background:var(--accent);border-radius:0 3px 3px 0;
}
.sidebar-bottom{margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:8px}
.live-dot{
  width:8px;height:8px;border-radius:50%;background:var(--green);
  box-shadow:0 0 8px var(--green);animation:pulse-dot 2s infinite;
}
@keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.6;transform:scale(0.85)}}

/* Main */
.main{padding:32px;display:flex;flex-direction:column;gap:28px;overflow-y:auto}

/* Top bar */
.topbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
.topbar-left h1{font-size:28px;font-weight:800;letter-spacing:-0.5px}
.topbar-left h1 span{color:var(--accent)}
.topbar-sub{font-size:12px;color:var(--muted);margin-top:3px;font-family:'JetBrains Mono',monospace}
.topbar-right{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.status-chip{
  display:flex;align-items:center;gap:6px;padding:6px 12px;
  border:1px solid var(--border2);border-radius:20px;font-size:11px;color:var(--text);
  font-family:'JetBrains Mono',monospace;
}
.status-chip .dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse-dot 2s infinite}
.cmd-pill{
  padding:8px 16px;background:var(--accent);color:#000;border:none;
  border-radius:20px;font-size:12px;font-weight:700;cursor:pointer;
  font-family:'Syne',sans-serif;letter-spacing:0.02em;transition:all 0.15s;
}
.cmd-pill:hover{background:#F0CF4A;transform:translateY(-1px)}

/* Metrics */
.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}}
@media(max-width:700px){.metrics{grid-template-columns:1fr 1fr}}
.metric{
  background:var(--bg2);border:1px solid var(--border);border-radius:16px;
  padding:18px 20px;position:relative;overflow:hidden;transition:border-color 0.2s;
}
.metric:hover{border-color:var(--border2)}
.metric::after{
  content:'';position:absolute;top:0;right:0;width:60px;height:60px;
  border-radius:0 16px 0 60px;opacity:0.06;
}
.metric.gold::after{background:var(--accent)}
.metric.teal::after{background:var(--accent2)}
.metric.red::after{background:var(--accent3)}
.metric.green::after{background:var(--green)}
.metric.purple::after{background:var(--purple)}
.metric-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;font-family:'JetBrains Mono',monospace}
.metric-val{font-size:26px;font-weight:800;letter-spacing:-1px}
.metric-val.gold{color:var(--accent)}
.metric-val.teal{color:var(--accent2)}
.metric-val.red{color:var(--accent3)}
.metric-val.green{color:var(--green)}
.metric-val.purple{color:var(--purple)}
.metric-delta{font-size:11px;color:var(--muted);margin-top:4px;font-family:'JetBrains Mono',monospace}

/* Section title */
.section-title{font-size:11px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}

/* Agents */
.agents{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
@media(max-width:1100px){.agents{grid-template-columns:repeat(3,1fr)}}
@media(max-width:700px){.agents{grid-template-columns:1fr 1fr}}
.agent-card{
  background:var(--bg2);border:1px solid var(--border);border-radius:16px;
  padding:20px;cursor:pointer;transition:all 0.2s;position:relative;overflow:hidden;
}
.agent-card:hover{border-color:var(--border2);transform:translateY(-2px)}
.agent-card.selected{border-color:var(--accent);background:rgba(232,197,71,0.04)}
.agent-glyph{
  width:40px;height:40px;border-radius:10px;display:flex;align-items:center;
  justify-content:center;font-size:18px;margin-bottom:12px;
}
.agent-name{font-size:15px;font-weight:700;margin-bottom:3px}
.agent-role{font-size:11px;color:var(--muted);line-height:1.4;margin-bottom:12px}
.agent-status{display:flex;align-items:center;gap:5px;font-size:10px;font-family:'JetBrains Mono',monospace}
.agent-status .dot{width:5px;height:5px;border-radius:50%}
.dot-green{background:var(--green);box-shadow:0 0 6px var(--green)}
.dot-amber{background:var(--orange)}
.agent-tasks{margin-top:12px;border-top:1px solid var(--border);padding-top:12px;display:flex;flex-direction:column;gap:4px}
.agent-task{font-size:10px;color:var(--muted);display:flex;align-items:center;gap:5px;font-family:'JetBrains Mono',monospace}
.agent-task::before{content:'›';color:var(--accent);font-size:12px}
.agent-bar{height:2px;background:var(--border);border-radius:1px;margin-top:12px;overflow:hidden}
.agent-bar-fill{height:100%;border-radius:1px;transition:width 1s ease}

/* Bottom grid */
.bottom-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:900px){.bottom-grid{grid-template-columns:1fr}}

/* Platforms */
.platforms-panel,.activity-panel{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:22px}
.platforms-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}
.platform{
  background:var(--bg3);border:1px solid var(--border);border-radius:10px;
  padding:12px;display:flex;align-items:center;gap:10px;
  transition:border-color 0.15s;cursor:pointer;
}
.platform:hover{border-color:var(--border2)}
.platform-icon{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0}
.platform-name{font-size:12px;font-weight:600}
.platform-handle{font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace}
.platform-badge{margin-left:auto;font-size:9px;padding:2px 6px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-weight:500}
.badge-live{background:rgba(34,197,94,0.15);color:var(--green)}
.badge-soon{background:rgba(249,115,22,0.15);color:var(--orange)}

/* Activity feed */
.feed{display:flex;flex-direction:column;gap:0;margin-top:14px;max-height:360px;overflow-y:auto}
.feed::-webkit-scrollbar{width:3px}
.feed::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.feed-item{
  display:grid;grid-template-columns:28px 1fr auto;gap:10px;align-items:flex-start;
  padding:10px 0;border-bottom:1px solid var(--border);
}
.feed-item:last-child{border-bottom:none}
.feed-icon{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;margin-top:1px}
.feed-text{font-size:12px;line-height:1.5}
.feed-text b{color:var(--text);font-weight:600}
.feed-text span{color:var(--muted)}
.feed-time{font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;white-space:nowrap}

/* Command bar */
.command-bar{
  background:var(--bg2);border:1px solid var(--border);border-radius:16px;
  padding:20px;display:flex;align-items:center;gap:12px;
}
.command-prompt{font-size:14px;color:var(--accent);font-family:'JetBrains Mono',monospace;white-space:nowrap}
.command-input{
  flex:1;background:transparent;border:none;outline:none;
  font-size:14px;color:var(--text);font-family:'JetBrains Mono',monospace;
  caret-color:var(--accent);
}
.command-input::placeholder{color:var(--muted)}
.command-send{
  padding:8px 20px;background:var(--accent);color:#000;border:none;
  border-radius:10px;font-size:12px;font-weight:700;cursor:pointer;
  font-family:'Syne',sans-serif;transition:all 0.15s;white-space:nowrap;
}
.command-send:hover{background:#F0CF4A}
.command-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.chip{
  padding:5px 12px;border:1px solid var(--border);border-radius:20px;
  font-size:11px;color:var(--muted);cursor:pointer;transition:all 0.15s;
  font-family:'JetBrains Mono',monospace;
}
.chip:hover{border-color:var(--accent);color:var(--accent)}

/* Modal */
.modal-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(4px);
  z-index:100;display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity 0.2s;
}
.modal-overlay.open{opacity:1;pointer-events:all}
.modal{
  background:var(--bg2);border:1px solid var(--border2);border-radius:20px;
  width:540px;max-width:92vw;padding:28px;position:relative;
  transform:translateY(16px);transition:transform 0.2s;
}
.modal-overlay.open .modal{transform:translateY(0)}
.modal-close{
  position:absolute;top:16px;right:16px;width:28px;height:28px;
  border-radius:8px;border:1px solid var(--border);background:transparent;
  color:var(--muted);cursor:pointer;font-size:14px;
  display:flex;align-items:center;justify-content:center;transition:all 0.15s;
}
.modal-close:hover{border-color:var(--border2);color:var(--text)}
.modal-header{display:flex;align-items:center;gap:14px;margin-bottom:20px}
.modal-glyph{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px}
.modal-title{font-size:20px;font-weight:800}
.modal-subtitle{font-size:12px;color:var(--muted);margin-top:2px;font-family:'JetBrains Mono',monospace}
.modal-section{margin-bottom:18px}
.modal-section-label{font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:8px;font-family:'JetBrains Mono',monospace}
.modal-tasks{display:flex;flex-direction:column;gap:6px}
.modal-task{display:flex;align-items:center;gap:8px;padding:8px 10px;background:var(--bg3);border-radius:8px;font-size:12px;font-family:'JetBrains Mono',monospace}
.modal-task::before{content:'›';color:var(--accent)}
.modal-actions{display:flex;gap:8px;margin-top:20px}
.btn-primary{flex:1;padding:10px;background:var(--accent);color:#000;border:none;border-radius:10px;font-size:12px;font-weight:700;cursor:pointer;font-family:'Syne',sans-serif;transition:all 0.15s}
.btn-primary:hover{background:#F0CF4A}
.btn-secondary{flex:1;padding:10px;background:transparent;color:var(--text);border:1px solid var(--border2);border-radius:10px;font-size:12px;font-weight:600;cursor:pointer;font-family:'Syne',sans-serif;transition:all 0.15s}
.btn-secondary:hover{background:var(--bg3)}

/* Toast */
#toast{
  position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(40px);
  background:var(--bg2);border:1px solid var(--accent);color:var(--accent);
  padding:10px 20px;border-radius:10px;font-size:12px;font-family:'JetBrains Mono',monospace;
  opacity:0;transition:all 0.3s;z-index:999;pointer-events:none;
}

/* Animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.main > *{animation:fadeUp 0.4s ease both}
.main > *:nth-child(1){animation-delay:0.05s}
.main > *:nth-child(2){animation-delay:0.10s}
.main > *:nth-child(3){animation-delay:0.15s}
.main > *:nth-child(4){animation-delay:0.20s}
.main > *:nth-child(5){animation-delay:0.25s}
.main > *:nth-child(6){animation-delay:0.30s}

::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
</style>
</head>
<body>
<div class="shell">

  <!-- SIDEBAR -->
  <nav class="sidebar">
    <div class="sidebar-logo">A</div>
    <button class="nav-btn active" title="Dashboard">⚡</button>
    <button class="nav-btn" title="Agents">🤖</button>
    <button class="nav-btn" title="Social">📡</button>
    <button class="nav-btn" title="Inbox">📨</button>
    <button class="nav-btn" title="Research">🔍</button>
    <button class="nav-btn" title="Music">🎵</button>
    <button class="nav-btn" title="Security">🛡</button>
    <div class="sidebar-bottom">
      <div class="live-dot"></div>
    </div>
  </nav>

  <!-- MAIN -->
  <main class="main">

    <!-- TOP BAR -->
    <div class="topbar">
      <div class="topbar-left">
        <h1>AKILI <span>OS</span></h1>
        <div class="topbar-sub mono" id="clock">Loading...</div>
      </div>
      <div class="topbar-right">
        <div class="status-chip"><div class="dot"></div>All agents active</div>
        <div class="status-chip">🌍 Africa + Canada</div>
        <button class="cmd-pill" onclick="openModal('shield')">⚡ Run Health Check</button>
      </div>
    </div>

    <!-- METRICS -->
    <div class="metrics">
      <div class="metric gold">
        <div class="metric-label">Platforms</div>
        <div class="metric-val gold" id="m-platforms">—</div>
        <div class="metric-delta" id="m-platforms-sub">Loading…</div>
      </div>
      <div class="metric teal">
        <div class="metric-label">Active Agents</div>
        <div class="metric-val teal">5</div>
        <div class="metric-delta">Shield · Pulse · Reach · Intel · Amplify</div>
      </div>
      <div class="metric green">
        <div class="metric-label">GitHub Repos</div>
        <div class="metric-val green">8</div>
        <div class="metric-delta">creova-gif monitored</div>
      </div>
      <div class="metric purple">
        <div class="metric-label">Snap Streak</div>
        <div class="metric-val purple" id="m-streak">—</div>
        <div class="metric-delta" id="m-streak-sub">day streak · jay-mafie</div>
      </div>
      <div class="metric red">
        <div class="metric-label">Morning Brief</div>
        <div class="metric-val red">8AM</div>
        <div class="metric-delta">Daily → Telegram</div>
      </div>
    </div>

    <!-- AGENTS -->
    <div>
      <div class="section-title">5 Specialized Agents</div>
      <div class="agents">

        <div class="agent-card" onclick="openModal('shield')">
          <div class="agent-glyph" style="background:rgba(249,115,22,0.12)">🛡</div>
          <div class="agent-name">SHIELD</div>
          <div class="agent-role">Security, repos &amp; infrastructure protection</div>
          <div class="agent-status"><div class="dot dot-green"></div>Active · 30min scan</div>
          <div class="agent-tasks">
            <div class="agent-task">8 repos monitored</div>
            <div class="agent-task">creova.one uptime</div>
            <div class="agent-task">API key protection</div>
          </div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:92%;background:var(--orange)"></div></div>
        </div>

        <div class="agent-card" onclick="openModal('pulse')">
          <div class="agent-glyph" style="background:rgba(78,205,196,0.12)">📡</div>
          <div class="agent-name">PULSE</div>
          <div class="agent-role">All social media — posting, scheduling, growth</div>
          <div class="agent-status"><div class="dot dot-green"></div>Active · 4–6 posts/day</div>
          <div class="agent-tasks">
            <div class="agent-task">10 social accounts</div>
            <div class="agent-task">Weekly content cal</div>
            <div class="agent-task">A/B experiments</div>
          </div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:78%;background:var(--accent2)"></div></div>
        </div>

        <div class="agent-card" onclick="openModal('reach')">
          <div class="agent-glyph" style="background:rgba(232,197,71,0.10)">📨</div>
          <div class="agent-name">REACH</div>
          <div class="agent-role">Email, DMs, WhatsApp &amp; content repurposing</div>
          <div class="agent-status"><div class="dot dot-green"></div>Active · watching inbox</div>
          <div class="agent-tasks">
            <div class="agent-task">Personal + biz Gmail</div>
            <div class="agent-task">DM auto-reply</div>
            <div class="agent-task">Content repurpose</div>
          </div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:65%;background:var(--accent)"></div></div>
        </div>

        <div class="agent-card" onclick="openModal('intel')">
          <div class="agent-glyph" style="background:rgba(167,139,250,0.12)">🔍</div>
          <div class="agent-name">INTEL</div>
          <div class="agent-role">Research, leads, VC tracking &amp; daily briefs</div>
          <div class="agent-status"><div class="dot dot-green"></div>Active · brief at 8AM</div>
          <div class="agent-tasks">
            <div class="agent-task">GoPay VC tracker</div>
            <div class="agent-task">Lead generation</div>
            <div class="agent-task">Competitor intel</div>
          </div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:55%;background:var(--purple)"></div></div>
        </div>

        <div class="agent-card" onclick="openModal('amplify')">
          <div class="agent-glyph" style="background:rgba(255,107,107,0.12)">🔊</div>
          <div class="agent-name">AMPLIFY</div>
          <div class="agent-role">Music promo, brand growth &amp; Snap Creator</div>
          <div class="agent-status"><div class="dot dot-green"></div>Active · stream tracking</div>
          <div class="agent-tasks">
            <div class="agent-task">DistroKid analytics</div>
            <div class="agent-task">Playlist pitching</div>
            <div class="agent-task">Snapchat Creator</div>
          </div>
          <div class="agent-bar"><div class="agent-bar-fill" style="width:44%;background:var(--accent3)"></div></div>
        </div>

      </div>
    </div>

    <!-- BOTTOM GRID: PLATFORMS + FEED -->
    <div class="bottom-grid">

      <div class="platforms-panel">
        <div class="section-title">Platform Connections</div>
        <div class="platforms-grid" id="platform-grid">
          <!-- filled by JS -->
        </div>
      </div>

      <div class="activity-panel">
        <div class="section-title">Live Activity Feed</div>
        <div class="feed" id="feed">
          <div class="feed-item">
            <div class="feed-icon" style="background:rgba(232,197,71,0.10)">⚡</div>
            <div class="feed-text"><b>AKILI</b> <span>loading activity…</span></div>
            <div class="feed-time">now</div>
          </div>
        </div>
      </div>

    </div>

    <!-- COMMAND BAR -->
    <div>
      <div class="section-title">Command Akili</div>
      <div class="command-bar">
        <div class="command-prompt">› akili</div>
        <input class="command-input" id="cmdInput"
               placeholder="Tell Akili what to do… (same as Telegram)"
               onkeydown="handleCmd(event)"/>
        <button class="command-send" onclick="fireCmd()">Execute ↗</button>
      </div>
      <div class="command-chips">
        <div class="chip" onclick="copyCmd('generate this week content calendar for all accounts')">📅 Weekly calendar</div>
        <div class="chip" onclick="copyCmd('run GitHub org scan for all 8 repos')">🐙 GitHub scan</div>
        <div class="chip" onclick="copyCmd('check both Gmail inboxes and flag urgent emails')">📧 Check inboxes</div>
        <div class="chip" onclick="copyCmd('generate GoPay VC tracker with top 5 investors')">💰 GoPay VC tracker</div>
        <div class="chip" onclick="copyCmd('create Snapchat story script for today')">👻 Snap script</div>
        <div class="chip" onclick="copyCmd('run integration health check for all platforms')">🔌 Health check</div>
        <div class="chip" onclick="copyCmd('generate a music release campaign for CREOVA Music')">🎵 Music campaign</div>
        <div class="chip" onclick="copyCmd('generate leads for CREOVA Solutions this week')">🎯 Lead gen</div>
      </div>
    </div>

  </main>
</div>

<!-- AGENT MODALS -->
<div class="modal-overlay" id="modal" onclick="closeModal(event)">
  <div class="modal" id="modalContent">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="modal-header">
      <div class="modal-glyph" id="mGlyph"></div>
      <div>
        <div class="modal-title" id="mTitle"></div>
        <div class="modal-subtitle" id="mSub"></div>
      </div>
    </div>
    <div class="modal-section">
      <div class="modal-section-label">Responsibilities</div>
      <div class="modal-tasks" id="mTasks"></div>
    </div>
    <div class="modal-section">
      <div class="modal-section-label">Model</div>
      <div style="font-size:12px;font-family:'JetBrains Mono',monospace;color:var(--muted)" id="mModel"></div>
    </div>
    <div class="modal-actions">
      <button class="btn-primary" onclick="modalAction1()">Copy Command ↗</button>
      <button class="btn-secondary" onclick="closeModal()">Close</button>
    </div>
  </div>
</div>

<div id="toast">Copied to clipboard!</div>

<script>
// ── Clock ──────────────────────────────────────────────────
function updateClock(){
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleDateString('en-CA',{weekday:'long',year:'numeric',month:'long',day:'numeric'}) +
    ' · ' + now.toLocaleTimeString('en-CA',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
}
updateClock(); setInterval(updateClock, 1000);

// ── Platform config ────────────────────────────────────────
const PLATFORM_CONFIG = {
  twitter:   {icon:'𝕏',  bg:'rgba(29,161,242,0.10)',  name:'Twitter / X',  handle:'@justin_mafie',       cmd:'show Twitter analytics for @justin_mafie'},
  github:    {icon:'🐙', bg:'rgba(255,255,255,0.06)', name:'GitHub',        handle:'creova-gif · 8 repos', cmd:'run GitHub org scan for all 8 repos'},
  instagram: {icon:'📸', bg:'rgba(225,48,108,0.12)',  name:'Instagram',     handle:'4 accounts',           cmd:'show Instagram insights for all 4 accounts'},
  linkedin:  {icon:'💼', bg:'rgba(10,102,194,0.12)',  name:'LinkedIn',      handle:'Justin + CREOVA',      cmd:'show LinkedIn stats for Justin Mafie and CREOVA page'},
  snapchat:  {icon:'👻', bg:'rgba(255,252,0,0.08)',   name:'Snapchat',      handle:'jay-mafie',            cmd:'show Snapchat Creator tracker for jay-mafie'},
  tiktok:    {icon:'🎵', bg:'rgba(255,0,80,0.12)',    name:'TikTok',        handle:'@creovamusic',         cmd:'show TikTok analytics for @creovamusic'},
  facebook:  {icon:'📘', bg:'rgba(24,119,242,0.12)',  name:'Facebook',      handle:'Justin + CREOVA Biz',  cmd:'show Facebook page stats'},
  gmail:     {icon:'📧', bg:'rgba(234,67,53,0.12)',   name:'Gmail',         handle:'Personal + Business',  cmd:'check both Gmail inboxes for urgent emails'},
};

// ── Agent data ─────────────────────────────────────────────
const AGENTS = {
  shield: {
    icon:'🛡', color:'rgba(249,115,22,0.15)', name:'SHIELD',
    sub:'Security · Infrastructure · GitHub Monitor',
    tasks:['Monitor all 8 creova-gif repos every 30 min','Check creova.one + all product uptime','Protect all API keys and credentials','Instant Telegram alert on any breach','Never delete without 2x Justin confirmation'],
    model:'claude-sonnet-4-5 · Fast monitoring loops',
    cmd:'run GitHub org scan for all 8 repos and report'
  },
  pulse: {
    icon:'📡', color:'rgba(78,205,196,0.15)', name:'PULSE',
    sub:'Social Media · 10 accounts · 4–6 posts/day',
    tasks:['@creativeinnovation__ @jj_mafie @sankofastudio__ @creovasolutions','@justin_mafie (X) · Justin Mafie + CREOVA (LinkedIn)','jay-mafie (Snapchat) · @creovamusic (TikTok)','Justin + CREOVA (Facebook) · Weekly content calendar','A/B posting experiments + growth tracking'],
    model:'claude-sonnet-4-5 · High-volume content generation',
    cmd:'generate this week content calendar for all accounts'
  },
  reach: {
    icon:'📨', color:'rgba(232,197,71,0.12)', name:'REACH',
    sub:'Email · DMs · WhatsApp · Content Repurposing',
    tasks:['Monitor personal Gmail + CREOVA business email','Auto-reply DMs in Justin Mafie voice on all platforms','Flag urgent emails instantly to Telegram','Repurpose 1 piece of content into all platform formats','Draft email campaigns for music + CREOVA Solutions'],
    model:'claude-sonnet-4-5 · Fast comms and classification',
    cmd:'check both Gmail inboxes and flag urgent emails'
  },
  intel: {
    icon:'🔍', color:'rgba(167,139,250,0.15)', name:'INTEL',
    sub:'Research · Leads · VC Tracking · Daily Briefs',
    tasks:['Daily 8AM brief → Telegram: market news + priorities','Lead gen for CREOVA Solutions + CREOVA Music deals','GoPay VC tracker: Partech, TLcom, Novastar + more','Deep product research for all 14 CREOVA builds','Competitor monitoring across all markets'],
    model:'claude-sonnet-4-5 · Deep research and synthesis',
    cmd:'generate GoPay VC tracker with top 5 East Africa investors'
  },
  amplify: {
    icon:'🔊', color:'rgba(255,107,107,0.15)', name:'AMPLIFY',
    sub:'Music Promo · Brand Growth · Snap Creator',
    tasks:['DistroKid + Spotify for Artists stream tracking','Playlist pitching for CREOVA Music releases','Snapchat Creator program score + daily script','Cross-pollinate: music fans ↔ tech audience ↔ personal brand','Posting time experiments + growth optimization'],
    model:'claude-sonnet-4-5 · Creative promotion and growth',
    cmd:'create a music release campaign plan for CREOVA Music'
  },
};

let currentAgent = null;

// ── Fetch live status ──────────────────────────────────────
async function fetchStatus(){
  try{
    const r = await fetch('/api/status');
    const d = await r.json();
    render(d);
  }catch(e){ console.error('Status fetch failed',e); }
}

function escHtml(s){
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function timeAgo(ts){
  // ts is HH:MM from today's log
  return ts;
}

function render(d){
  // Metrics
  const conn = d.integrations_connected;
  document.getElementById('m-platforms').textContent = conn + '/8';
  document.getElementById('m-platforms-sub').textContent = conn === 8 ? 'all platforms live' : (8-conn) + ' still pending';

  const s = d.snapchat_streak;
  document.getElementById('m-streak').textContent = s.streak || '0';
  document.getElementById('m-streak-sub').textContent = 'day streak · last: ' + (s.last_posted || '—');

  // Platform grid
  const pg = document.getElementById('platform-grid');
  pg.innerHTML = '';
  Object.entries(d.integrations).forEach(([k, v]) => {
    const cfg = PLATFORM_CONFIG[k] || {};
    const live = v.ok;
    pg.innerHTML += `
    <div class="platform" onclick="copyCmd('${cfg.cmd||''}')">
      <div class="platform-icon" style="background:${cfg.bg||'rgba(255,255,255,0.06)'}">${cfg.icon||'?'}</div>
      <div>
        <div class="platform-name">${v.label}</div>
        <div class="platform-handle">${v.handle}</div>
      </div>
      <div class="platform-badge ${live?'badge-live':'badge-soon'}">${live?'LIVE':'SETUP'}</div>
    </div>`;
  });

  // Activity feed
  const feed = document.getElementById('feed');
  const agentColors = {
    'SHIELD':'rgba(249,115,22,0.12)', 'PULSE':'rgba(78,205,196,0.12)',
    'REACH':'rgba(232,197,71,0.10)', 'INTEL':'rgba(167,139,250,0.12)',
    'AMPLIFY':'rgba(255,107,107,0.12)'
  };
  const agentIcons = {
    'SHIELD':'🛡','PULSE':'📡','REACH':'📨','INTEL':'🔍','AMPLIFY':'🔊'
  };
  if(d.activity && d.activity.length){
    const items = [...d.activity].reverse().slice(0,8);
    feed.innerHTML = items.map(a => {
      const src = a.source.toUpperCase();
      const agentKey = Object.keys(agentColors).find(k => src.includes(k)) || 'AKILI';
      const icon = agentIcons[agentKey] || '⚡';
      const color = agentColors[agentKey] || 'rgba(232,197,71,0.10)';
      return `<div class="feed-item">
        <div class="feed-icon" style="background:${color}">${icon}</div>
        <div class="feed-text"><b>${escHtml(a.source)}</b> <span>${escHtml(a.msg)}</span></div>
        <div class="feed-time">${a.ts}</div>
      </div>`;
    }).join('');
  }
}

// ── Command bar ────────────────────────────────────────────
function handleCmd(e){ if(e.key==='Enter') fireCmd(); }

function fireCmd(){
  const v = document.getElementById('cmdInput').value.trim();
  if(!v) return;
  copyCmd(v);
  document.getElementById('cmdInput').value = '';
}

function copyCmd(cmd){
  if(!cmd) return;
  navigator.clipboard.writeText(cmd).then(() => {
    const t = document.getElementById('toast');
    t.textContent = '✓ Copied — paste into Telegram';
    t.style.opacity = '1';
    t.style.transform = 'translateX(-50%) translateY(0)';
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateX(-50%) translateY(40px)';
    }, 2200);
  });
}

// ── Agent modals ───────────────────────────────────────────
function openModal(key){
  const a = AGENTS[key];
  if(!a) return;
  currentAgent = key;
  const g = document.getElementById('mGlyph');
  g.textContent = a.icon;
  g.style.background = a.color;
  document.getElementById('mTitle').textContent = a.name;
  document.getElementById('mSub').textContent = a.sub;
  document.getElementById('mModel').textContent = a.model;
  document.getElementById('mTasks').innerHTML = a.tasks.map(t=>`<div class="modal-task">${t}</div>`).join('');
  document.getElementById('modal').classList.add('open');
}

function modalAction1(){
  const a = AGENTS[currentAgent];
  if(a) copyCmd(a.cmd);
  closeModal();
}

function closeModal(e){
  if(e && e.target !== document.getElementById('modal')) return;
  document.getElementById('modal').classList.remove('open');
}

// ── Sidebar nav ────────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', function(){
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
  });
});

// ── Init ───────────────────────────────────────────────────
fetchStatus();
setInterval(fetchStatus, 15000);
</script>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")
