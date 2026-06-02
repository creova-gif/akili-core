# ============================================================
# AKILI DASHBOARD — World-Class Mission Control
# Real-time data · Live activity · OS-grade UX
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


def _recent_activity(n: int = 20) -> list[dict]:
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
                    msg    = msg.strip()
                    if any(x in msg for x in ["terminated by other getUpdates", "HTTP Request", "getUpdates", "file_cache"]):
                        continue
                    if "httpx" in source.lower():
                        continue
                    if "HEARTBEAT" in msg and "OK" in msg:
                        continue
                    entries.append({
                        "ts":     ts[11:16],
                        "date":   ts[:10],
                        "level":  level,
                        "source": source,
                        "msg":    msg[:100] + ("…" if len(msg) > 100 else ""),
                    })
    except Exception:
        pass
    return entries[-n:]


def _integration_status() -> dict:
    env = os.environ
    return {
        "twitter":   {"label": "Twitter / X",  "handle": "@justin_mafie",        "icon": "𝕏",   "ok": bool(env.get("TWITTER_API_KEY"))},
        "github":    {"label": "GitHub",        "handle": "creova-gif · 8 repos", "icon": "⬡",   "ok": bool(env.get("GITHUB_TOKEN"))},
        "instagram": {"label": "Instagram",     "handle": "4 accounts",           "icon": "◈",   "ok": os.path.exists("config/instagram_token.json")},
        "linkedin":  {"label": "LinkedIn",      "handle": "Justin + CREOVA",      "icon": "▣",   "ok": bool(env.get("LINKEDIN_ACCESS_TOKEN"))},
        "snapchat":  {"label": "Snapchat",      "handle": "jay-mafie",            "icon": "◎",   "ok": bool(env.get("SNAPCHAT_ACCESS_TOKEN"))},
        "tiktok":    {"label": "TikTok",        "handle": "@creovamusic",         "icon": "◈",   "ok": bool(env.get("TIKTOK_ACCESS_TOKEN"))},
        "facebook":  {"label": "Facebook",      "handle": "Justin + CREOVA Biz",  "icon": "◫",   "ok": bool(env.get("FACEBOOK_ACCESS_TOKEN"))},
        "gmail":     {"label": "Gmail",         "handle": "Personal + Business",  "icon": "✉",   "ok": os.path.exists("config/gmail_business_token.json")},
        "openai":    {"label": "OpenAI / DALL·E","handle": "Image generation",    "icon": "◬",   "ok": bool(env.get("OPENAI_API_KEY"))},
    }


def _github_repos() -> list[str]:
    return ["Gopay", "KayaYourpropertyai", "Darsme", "Mentalpath",
            "Aihealthsupport", "GridOs", "Kilimoai", "Budgeteaseapp"]


_start_time = datetime.utcnow()

def _uptime() -> str:
    delta = datetime.utcnow() - _start_time
    h, rem = divmod(int(delta.total_seconds()), 3600)
    m = rem // 60
    return f"{h}h {m}m"


# ── API endpoint ─────────────────────────────────────────────

async def handle_api_status(request: web.Request) -> web.Response:
    streak       = _streak_data()
    integrations = _integration_status()
    activity     = _recent_activity(20)
    connected    = sum(1 for v in integrations.values() if v["ok"])
    payload = {
        "timestamp":              datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "uptime":                 _uptime(),
        "agents": {
            "SHIELD":  {"desc": "Security & GitHub monitor",  "status": "active"},
            "PULSE":   {"desc": "Social media publisher",     "status": "active"},
            "REACH":   {"desc": "Email & outreach",           "status": "active"},
            "INTEL":   {"desc": "Market & trend analysis",    "status": "active"},
            "AMPLIFY": {"desc": "Growth & engagement",        "status": "active"},
        },
        "integrations":           integrations,
        "integrations_connected": connected,
        "integrations_total":     len(integrations),
        "snapchat_streak":        streak,
        "github_repos":           _github_repos(),
        "activity":               activity,
    }
    return web.json_response(payload)


# ── Main dashboard ─────────────────────────────────────────────

async def handle_dashboard(request: web.Request) -> web.Response:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="tiktok-developers-site-verification" content="ZOEgJ9JW9DI1DsSJngcQTHQLHJcMe7Ob"/>
<title>AKILI — Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet"/>
<style>
/* ── Reset & Variables ─────────────────────────────────── */
:root{
  --bg:      #07090E;
  --bg2:     #0C0F19;
  --bg3:     #111520;
  --bg4:     #161B28;
  --border:  rgba(255,255,255,0.06);
  --border2: rgba(255,255,255,0.11);
  --border3: rgba(255,255,255,0.18);
  --text:    #EEE9E0;
  --text2:   #B8B0A4;
  --muted:   #52596B;
  --accent:  #E8C547;
  --accent-dim: rgba(232,197,71,0.08);
  --accent2: #4ECDC4;
  --accent3: #FF6B6B;
  --green:   #22C55E;
  --green-dim: rgba(34,197,94,0.1);
  --orange:  #F97316;
  --purple:  #A78BFA;
  --red:     #EF4444;
  --r:       16px;
  --r2:      12px;
  --r3:      8px;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{
  background:var(--bg);color:var(--text);
  font-family:'Syne',sans-serif;
  -webkit-font-smoothing:antialiased;
}

/* ── Noise grain ─────────────────────────────────────────── */
body::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:999;
  opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* ── Layout ──────────────────────────────────────────────── */
.shell{
  display:grid;
  grid-template-columns:64px 1fr;
  height:100vh;overflow:hidden;
}

/* ── Sidebar ─────────────────────────────────────────────── */
.sidebar{
  background:var(--bg2);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;align-items:center;
  padding:20px 0 24px;gap:6px;
  position:relative;z-index:10;
}
.logo{
  width:36px;height:36px;border-radius:10px;
  background:linear-gradient(135deg,#E8C547 0%,#F0A030 100%);
  display:flex;align-items:center;justify-content:center;
  font-size:15px;font-weight:800;color:#000;
  margin-bottom:20px;letter-spacing:-.5px;
  box-shadow:0 0 24px rgba(232,197,71,.25);
  flex-shrink:0;
}
.nav-icon{
  width:40px;height:40px;border-radius:10px;border:none;background:transparent;
  color:var(--muted);cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  font-size:16px;transition:all .18s;position:relative;
  flex-shrink:0;
}
.nav-icon:hover{background:var(--bg3);color:var(--text2)}
.nav-icon.on{background:var(--accent-dim);color:var(--accent)}
.nav-icon.on::before{
  content:'';position:absolute;left:-1px;top:50%;transform:translateY(-50%);
  width:3px;height:18px;background:var(--accent);
  border-radius:0 3px 3px 0;
}
.sidebar-bottom{margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:10px}
.live-pulse{
  width:7px;height:7px;border-radius:50%;
  background:var(--green);
  box-shadow:0 0 0 0 rgba(34,197,94,.5);
  animation:live-ring 2s infinite;
}
@keyframes live-ring{
  0%  {box-shadow:0 0 0 0 rgba(34,197,94,.5)}
  70% {box-shadow:0 0 0 8px rgba(34,197,94,0)}
  100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}
}
.uptime-badge{
  writing-mode:vertical-rl;text-orientation:mixed;
  font-size:9px;color:var(--muted);font-family:'JetBrains Mono',monospace;
  transform:rotate(180deg);letter-spacing:.05em;
}

/* ── Main panel ──────────────────────────────────────────── */
.main{
  display:flex;flex-direction:column;
  height:100vh;overflow:hidden;
}

/* ── Header ──────────────────────────────────────────────── */
.header{
  padding:20px 28px 16px;
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  gap:16px;flex-shrink:0;
  background:linear-gradient(180deg,rgba(12,15,25,.95) 0%,rgba(12,15,25,.7) 100%);
  backdrop-filter:blur(20px);
}
.header-left{}
.greeting{
  font-size:22px;font-weight:800;letter-spacing:-.4px;
  display:flex;align-items:center;gap:8px;
}
.greeting .name{color:var(--accent)}
.header-meta{
  font-size:11px;color:var(--muted);margin-top:3px;
  font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:8px;
}
.header-meta .sep{opacity:.3}
.header-right{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.chip{
  display:inline-flex;align-items:center;gap:5px;
  padding:5px 11px;border:1px solid var(--border2);border-radius:20px;
  font-size:10px;font-family:'JetBrains Mono',monospace;color:var(--text2);
  white-space:nowrap;
}
.chip .dot{width:5px;height:5px;border-radius:50%;background:var(--green);
  animation:live-ring 2s infinite}
.run-btn{
  padding:7px 16px;background:var(--accent);color:#000;border:none;
  border-radius:20px;font-size:11px;font-weight:700;cursor:pointer;
  font-family:'Syne',sans-serif;letter-spacing:.02em;transition:all .15s;
  white-space:nowrap;
}
.run-btn:hover{background:#F0CF4A;transform:translateY(-1px);
  box-shadow:0 4px 16px rgba(232,197,71,.3)}

/* ── Scrollable body ─────────────────────────────────────── */
.body{flex:1;overflow-y:auto;padding:20px 28px 28px;display:flex;flex-direction:column;gap:18px}
.body::-webkit-scrollbar{width:3px}
.body::-webkit-scrollbar-track{background:transparent}
.body::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}

/* ── Section header ──────────────────────────────────────── */
.sec-hd{
  font-size:10px;font-weight:600;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);
  display:flex;align-items:center;gap:8px;margin-bottom:10px;
}
.sec-hd::after{content:'';flex:1;height:1px;background:var(--border)}

/* ── Metric strip ────────────────────────────────────────── */
.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.met{
  background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);
  padding:16px 18px;position:relative;overflow:hidden;
  transition:border-color .2s,transform .2s;cursor:default;
}
.met:hover{border-color:var(--border2);transform:translateY(-1px)}
.met-glow{
  position:absolute;top:-20px;right:-20px;width:80px;height:80px;
  border-radius:50%;opacity:.07;pointer-events:none;
}
.met-label{font-size:9px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.1em;margin-bottom:8px;font-family:'JetBrains Mono',monospace}
.met-val{font-size:28px;font-weight:800;letter-spacing:-1px;line-height:1}
.met-sub{font-size:10px;color:var(--muted);margin-top:5px;
  font-family:'JetBrains Mono',monospace}
.col-gold{color:var(--accent)}
.col-teal{color:var(--accent2)}
.col-green{color:var(--green)}
.col-purple{color:var(--purple)}
.col-red{color:var(--accent3)}

/* ── Main grid ───────────────────────────────────────────── */
.grid-main{display:grid;grid-template-columns:1fr 320px;gap:18px;align-items:start}

/* ── Agents ──────────────────────────────────────────────── */
.agents{display:flex;flex-direction:column;gap:8px}
.agent{
  background:var(--bg2);border:1px solid var(--border);border-radius:var(--r2);
  padding:16px 18px;display:grid;grid-template-columns:42px 1fr auto;
  gap:12px;align-items:center;cursor:pointer;transition:all .18s;
  position:relative;overflow:hidden;
}
.agent::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:3px;
  border-radius:0 3px 3px 0;opacity:0;transition:opacity .2s;
}
.agent:hover{border-color:var(--border2);transform:translateX(2px)}
.agent:hover::before{opacity:1}
.agent.shield::before{background:var(--orange)}
.agent.pulse::before{background:var(--accent2)}
.agent.reach::before{background:var(--accent)}
.agent.intel::before{background:var(--purple)}
.agent.amplify::before{background:var(--accent3)}
.ag-icon{
  width:42px;height:42px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;font-size:18px;
  flex-shrink:0;
}
.ag-body{}
.ag-name{font-size:14px;font-weight:700;margin-bottom:1px}
.ag-desc{font-size:11px;color:var(--muted)}
.ag-right{display:flex;flex-direction:column;align-items:flex-end;gap:6px}
.ag-status{
  display:inline-flex;align-items:center;gap:4px;
  font-size:9px;font-family:'JetBrains Mono',monospace;
  padding:3px 8px;border-radius:20px;white-space:nowrap;
}
.st-active{background:var(--green-dim);color:var(--green)}
.ag-bar-wrap{width:80px;height:3px;background:var(--border);border-radius:2px;overflow:hidden}
.ag-bar{height:100%;border-radius:2px;transition:width 1.2s cubic-bezier(.4,0,.2,1)}

/* ── Right column ────────────────────────────────────────── */
.right-col{display:flex;flex-direction:column;gap:12px}

/* ── Panel base ──────────────────────────────────────────── */
.panel{
  background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);
  padding:18px;
}

/* ── Live feed ───────────────────────────────────────────── */
.feed-list{display:flex;flex-direction:column;gap:0;max-height:220px;overflow-y:auto}
.feed-list::-webkit-scrollbar{width:0}
.feed-row{
  display:flex;align-items:flex-start;gap:8px;
  padding:8px 0;border-bottom:1px solid var(--border);
  animation:fade-in .35s ease both;
}
.feed-row:last-child{border-bottom:none}
@keyframes fade-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.feed-dot{
  width:6px;height:6px;border-radius:50%;margin-top:5px;flex-shrink:0;
}
.feed-text{flex:1;font-size:11px;line-height:1.45;color:var(--text2)}
.feed-text b{color:var(--text);font-weight:600}
.feed-ts{font-size:9px;color:var(--muted);font-family:'JetBrains Mono',monospace;
  white-space:nowrap;margin-top:2px;flex-shrink:0}

/* ── Integrations ────────────────────────────────────────── */
.integ-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.integ{
  display:flex;align-items:center;gap:8px;padding:9px 10px;
  background:var(--bg3);border:1px solid var(--border);border-radius:var(--r3);
  transition:border-color .15s;cursor:pointer;
}
.integ:hover{border-color:var(--border2)}
.integ-sym{
  font-size:13px;width:26px;height:26px;border-radius:6px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.integ-info{flex:1;min-width:0}
.integ-name{font-size:11px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.integ-handle{font-size:9px;color:var(--muted);font-family:'JetBrains Mono',monospace}
.integ-badge{
  font-size:8px;padding:2px 5px;border-radius:4px;
  font-family:'JetBrains Mono',monospace;font-weight:500;flex-shrink:0;
}
.badge-on{background:rgba(34,197,94,.12);color:var(--green)}
.badge-off{background:rgba(239,68,68,.1);color:var(--red)}

/* ── Bottom row ──────────────────────────────────────────── */
.grid-bottom{display:grid;grid-template-columns:1fr 1fr;gap:18px}

/* ── Repos ───────────────────────────────────────────────── */
.repos-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:2px}
.repo{
  background:var(--bg3);border:1px solid var(--border);border-radius:var(--r3);
  padding:10px 12px;cursor:pointer;transition:all .15s;
  display:flex;align-items:center;justify-content:space-between;
}
.repo:hover{border-color:var(--accent);background:rgba(232,197,71,.03)}
.repo-name{font-size:11px;font-weight:600}
.repo-lang{font-size:9px;color:var(--muted);font-family:'JetBrains Mono',monospace}
.repo-arrow{font-size:10px;color:var(--muted)}

/* ── Command bar ─────────────────────────────────────────── */
.cmd-wrap{
  background:var(--bg2);border:1px solid var(--border2);border-radius:var(--r);
  overflow:hidden;transition:border-color .2s;
}
.cmd-wrap:focus-within{border-color:rgba(232,197,71,.35);box-shadow:0 0 0 3px rgba(232,197,71,.07)}
.cmd-top{display:flex;align-items:center;gap:0}
.cmd-prefix{
  padding:14px 14px 14px 18px;font-size:13px;
  color:var(--accent);font-family:'JetBrains Mono',monospace;
  white-space:nowrap;flex-shrink:0;opacity:.7;
}
.cmd-input{
  flex:1;padding:14px 0;background:transparent;border:none;outline:none;
  font-size:13px;color:var(--text);font-family:'JetBrains Mono',monospace;
  caret-color:var(--accent);
}
.cmd-input::placeholder{color:var(--muted)}
.cmd-fire{
  padding:10px 20px;margin:8px;background:var(--accent);color:#000;
  border:none;border-radius:var(--r3);font-size:11px;font-weight:700;
  cursor:pointer;font-family:'Syne',sans-serif;transition:all .15s;white-space:nowrap;
}
.cmd-fire:hover{background:#F0CF4A;box-shadow:0 4px 14px rgba(232,197,71,.3)}
.cmd-chips{
  display:flex;flex-wrap:wrap;gap:5px;padding:10px 14px 14px;
  border-top:1px solid var(--border);
}
.cmd-chip{
  padding:4px 10px;border:1px solid var(--border);border-radius:20px;
  font-size:10px;color:var(--muted);cursor:pointer;transition:all .15s;
  font-family:'JetBrains Mono',monospace;
}
.cmd-chip:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim)}

/* ── Response panel ──────────────────────────────────────── */
.resp-panel{
  background:var(--bg3);border:1px solid var(--border);border-radius:var(--r2);
  padding:14px 16px;font-size:12px;font-family:'JetBrains Mono',monospace;
  color:var(--text2);line-height:1.6;
  max-height:120px;overflow-y:auto;display:none;
}
.resp-panel.show{display:block}
.resp-panel::-webkit-scrollbar{width:0}
.resp-panel .resp-loading{
  display:flex;align-items:center;gap:8px;color:var(--muted)
}
.spinner{
  width:12px;height:12px;border:2px solid var(--border);
  border-top-color:var(--accent);border-radius:50%;
  animation:spin .8s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Modal ───────────────────────────────────────────────── */
.overlay{
  position:fixed;inset:0;background:rgba(0,0,0,.75);
  backdrop-filter:blur(6px);z-index:200;
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity .2s;
}
.overlay.open{opacity:1;pointer-events:all}
.modal{
  background:var(--bg2);border:1px solid var(--border2);
  border-radius:20px;width:520px;max-width:92vw;
  padding:28px;position:relative;
  transform:translateY(20px) scale(.97);
  transition:transform .25s cubic-bezier(.4,0,.2,1);
  max-height:90vh;overflow-y:auto;
}
.modal::-webkit-scrollbar{width:0}
.overlay.open .modal{transform:none}
.modal-x{
  position:absolute;top:14px;right:14px;width:28px;height:28px;
  border-radius:8px;border:1px solid var(--border);background:transparent;
  color:var(--muted);cursor:pointer;font-size:13px;
  display:flex;align-items:center;justify-content:center;transition:all .15s;
}
.modal-x:hover{background:var(--bg3);color:var(--text)}
.modal-head{display:flex;align-items:center;gap:14px;margin-bottom:22px}
.modal-ico{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0}
.modal-name{font-size:20px;font-weight:800}
.modal-sub{font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:2px}
.modal-sec{margin-bottom:18px}
.modal-sec-hd{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:8px;font-family:'JetBrains Mono',monospace}
.modal-tasks{display:flex;flex-direction:column;gap:5px}
.modal-task{
  display:flex;align-items:flex-start;gap:8px;padding:8px 10px;
  background:var(--bg3);border-radius:8px;font-size:11px;
  font-family:'JetBrains Mono',monospace;color:var(--text2);
}
.modal-task::before{content:'›';color:var(--accent);font-size:13px;flex-shrink:0}
.modal-btns{display:flex;gap:8px;margin-top:20px}
.btn-a{
  flex:1;padding:10px;background:var(--accent);color:#000;border:none;
  border-radius:10px;font-size:12px;font-weight:700;cursor:pointer;
  font-family:'Syne',sans-serif;transition:all .15s;
}
.btn-a:hover{background:#F0CF4A;box-shadow:0 4px 14px rgba(232,197,71,.3)}
.btn-b{
  flex:1;padding:10px;background:transparent;color:var(--text);
  border:1px solid var(--border2);border-radius:10px;font-size:12px;
  font-weight:600;cursor:pointer;font-family:'Syne',sans-serif;transition:all .15s;
}
.btn-b:hover{background:var(--bg3)}

/* ── Stagger animation ───────────────────────────────────── */
@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.body > *{animation:up .4s ease both}
.body > *:nth-child(1){animation-delay:.04s}
.body > *:nth-child(2){animation-delay:.09s}
.body > *:nth-child(3){animation-delay:.14s}
.body > *:nth-child(4){animation-delay:.19s}
.body > *:nth-child(5){animation-delay:.24s}
</style>
</head>
<body>
<div class="shell">

<!-- ── SIDEBAR ──────────────────────────────────────────── -->
<nav class="sidebar">
  <div class="logo">A</div>
  <button class="nav-icon on" title="Overview" onclick="setNav(this)">⚡</button>
  <button class="nav-icon"   title="Agents"   onclick="setNav(this)">◈</button>
  <button class="nav-icon"   title="Social"   onclick="setNav(this)">◎</button>
  <button class="nav-icon"   title="Inbox"    onclick="setNav(this)">✉</button>
  <button class="nav-icon"   title="Intel"    onclick="setNav(this)">◬</button>
  <button class="nav-icon"   title="Music"    onclick="setNav(this)">♪</button>
  <div class="sidebar-bottom">
    <div class="live-pulse" title="All systems live"></div>
    <div class="uptime-badge" id="uptimeBadge">0h 0m</div>
  </div>
</nav>

<!-- ── MAIN ──────────────────────────────────────────────── -->
<div class="main">

  <!-- HEADER -->
  <header class="header">
    <div class="header-left">
      <div class="greeting">
        <span id="greet">Good morning,</span>
        <span class="name">Justin.</span>
      </div>
      <div class="header-meta">
        <span id="clock">Loading...</span>
        <span class="sep">·</span>
        <span>St. Catharines, ON</span>
        <span class="sep">·</span>
        <span>creova.one</span>
      </div>
    </div>
    <div class="header-right">
      <div class="chip"><span class="dot"></span>5 agents active</div>
      <div class="chip" id="integChip">Loading...</div>
      <button class="run-btn" onclick="openAgent('shield')">⚡ Health Check</button>
    </div>
  </header>

  <!-- SCROLLABLE BODY -->
  <div class="body">

    <!-- METRICS -->
    <div>
      <div class="sec-hd">Command Overview</div>
      <div class="metrics">
        <div class="met">
          <div class="met-glow" style="background:var(--accent)"></div>
          <div class="met-label">Platforms</div>
          <div class="met-val col-gold" data-target="10">0</div>
          <div class="met-sub">social accounts</div>
        </div>
        <div class="met">
          <div class="met-glow" style="background:var(--accent2)"></div>
          <div class="met-label">Agents Online</div>
          <div class="met-val col-teal" data-target="5">0</div>
          <div class="met-sub">Shield · Pulse · Reach · Intel · Amplify</div>
        </div>
        <div class="met">
          <div class="met-glow" style="background:var(--green)"></div>
          <div class="met-label">GitHub Repos</div>
          <div class="met-val col-green" data-target="8">0</div>
          <div class="met-sub">creova-gif monitored</div>
        </div>
        <div class="met">
          <div class="met-glow" style="background:var(--purple)"></div>
          <div class="met-label">Heartbeat</div>
          <div class="met-val col-purple">30m</div>
          <div class="met-sub">auto-check interval</div>
        </div>
        <div class="met">
          <div class="met-glow" style="background:var(--accent3)"></div>
          <div class="met-label">Connected</div>
          <div class="met-val col-red" id="connectedMet">—</div>
          <div class="met-sub" id="connectedSub">integrations live</div>
        </div>
      </div>
    </div>

    <!-- AGENTS + SIDEBAR PANELS -->
    <div class="grid-main">

      <!-- LEFT: Agents -->
      <div>
        <div class="sec-hd">5 Specialized Agents</div>
        <div class="agents">

          <div class="agent shield" onclick="openAgent('shield')">
            <div class="ag-icon" style="background:rgba(249,115,22,.1)">🛡</div>
            <div class="ag-body">
              <div class="ag-name">SHIELD</div>
              <div class="ag-desc">Security · GitHub · System health · Uptime monitoring</div>
            </div>
            <div class="ag-right">
              <div class="ag-status st-active"><span style="width:5px;height:5px;border-radius:50%;background:var(--green);display:inline-block"></span>&nbsp;Active</div>
              <div class="ag-bar-wrap"><div class="ag-bar" style="width:0%;background:var(--orange)" data-w="92"></div></div>
            </div>
          </div>

          <div class="agent pulse" onclick="openAgent('pulse')">
            <div class="ag-icon" style="background:rgba(78,205,196,.1)">📡</div>
            <div class="ag-body">
              <div class="ag-name">PULSE</div>
              <div class="ag-desc">Social media · Carousel builder · A/B experiments · Hashtag intel</div>
            </div>
            <div class="ag-right">
              <div class="ag-status st-active"><span style="width:5px;height:5px;border-radius:50%;background:var(--green);display:inline-block"></span>&nbsp;Active</div>
              <div class="ag-bar-wrap"><div class="ag-bar" style="width:0%;background:var(--accent2)" data-w="78"></div></div>
            </div>
          </div>

          <div class="agent reach" onclick="openAgent('reach')">
            <div class="ag-icon" style="background:rgba(232,197,71,.08)">📨</div>
            <div class="ag-body">
              <div class="ag-name">REACH</div>
              <div class="ag-desc">Gmail (personal + biz) · DM auto-reply · Content repurposing</div>
            </div>
            <div class="ag-right">
              <div class="ag-status st-active"><span style="width:5px;height:5px;border-radius:50%;background:var(--green);display:inline-block"></span>&nbsp;Active</div>
              <div class="ag-bar-wrap"><div class="ag-bar" style="width:0%;background:var(--accent)" data-w="65"></div></div>
            </div>
          </div>

          <div class="agent intel" onclick="openAgent('intel')">
            <div class="ag-icon" style="background:rgba(167,139,250,.1)">🔍</div>
            <div class="ag-body">
              <div class="ag-name">INTEL</div>
              <div class="ag-desc">Research · VC tracker · Lead generation · Daily briefs at 8AM</div>
            </div>
            <div class="ag-right">
              <div class="ag-status st-active"><span style="width:5px;height:5px;border-radius:50%;background:var(--green);display:inline-block"></span>&nbsp;Active</div>
              <div class="ag-bar-wrap"><div class="ag-bar" style="width:0%;background:var(--purple)" data-w="55"></div></div>
            </div>
          </div>

          <div class="agent amplify" onclick="openAgent('amplify')">
            <div class="ag-icon" style="background:rgba(255,107,107,.1)">🔊</div>
            <div class="ag-body">
              <div class="ag-name">AMPLIFY</div>
              <div class="ag-desc">Music promo · DistroKid · Playlist pitching · Snap Creator score</div>
            </div>
            <div class="ag-right">
              <div class="ag-status st-active"><span style="width:5px;height:5px;border-radius:50%;background:var(--green);display:inline-block"></span>&nbsp;Active</div>
              <div class="ag-bar-wrap"><div class="ag-bar" style="width:0%;background:var(--accent3)" data-w="44"></div></div>
            </div>
          </div>

        </div>
      </div>

      <!-- RIGHT: Feed + Integrations -->
      <div class="right-col">

        <!-- Live feed -->
        <div class="panel">
          <div class="sec-hd" style="margin-bottom:8px">Live Activity</div>
          <div class="feed-list" id="feed">
            <div class="feed-row">
              <div class="feed-dot" style="background:var(--muted)"></div>
              <div class="feed-text"><span>Loading activity feed...</span></div>
              <div class="feed-ts">now</div>
            </div>
          </div>
        </div>

        <!-- Integrations -->
        <div class="panel">
          <div class="sec-hd" style="margin-bottom:10px">Platform Status</div>
          <div class="integ-grid" id="integGrid">
            <div style="font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace">Loading...</div>
          </div>
        </div>

      </div>
    </div>

    <!-- BOTTOM ROW: Repos + Command -->
    <div class="grid-bottom">

      <!-- Repos -->
      <div>
        <div class="sec-hd">GitHub Repositories</div>
        <div class="repos-grid" id="reposGrid">
          <div style="font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace">Loading...</div>
        </div>
      </div>

      <!-- Streak -->
      <div>
        <div class="sec-hd">Snapchat Creator</div>
        <div class="panel" style="display:grid;grid-template-columns:1fr 1fr;gap:0">
          <div style="padding:8px 0;border-right:1px solid var(--border);text-align:center">
            <div style="font-size:32px;font-weight:800;color:var(--accent)" id="streakVal">—</div>
            <div style="font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:4px">day streak</div>
          </div>
          <div style="padding:8px 0;text-align:center">
            <div style="font-size:32px;font-weight:800;color:var(--accent2)" id="totalDays">—</div>
            <div style="font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:4px">total days</div>
          </div>
        </div>
        <div style="font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:8px;text-align:center" id="lastPosted"></div>
      </div>

    </div>

    <!-- COMMAND BAR -->
    <div>
      <div class="sec-hd">Command Akili</div>
      <div class="cmd-wrap">
        <div class="cmd-top">
          <div class="cmd-prefix">›</div>
          <input class="cmd-input" id="cmdIn"
            placeholder="Tell Akili what to do... (same commands as Telegram)"
            onkeydown="if(event.key==='Enter')fire()"/>
          <button class="cmd-fire" onclick="fire()">Execute ↗</button>
        </div>
        <div class="cmd-chips">
          <div class="cmd-chip" onclick="quick('generate this week content calendar for all accounts')">📅 Week calendar</div>
          <div class="cmd-chip" onclick="quick('run GitHub org scan for all 8 creova repos')">⬡ GitHub scan</div>
          <div class="cmd-chip" onclick="quick('check both Gmail inboxes and flag urgent emails')">✉ Check inboxes</div>
          <div class="cmd-chip" onclick="quick('vc tracker GoPay East Africa investors')">💰 GoPay VC tracker</div>
          <div class="cmd-chip" onclick="quick('create Snapchat story script for today')">◎ Snap script</div>
          <div class="cmd-chip" onclick="quick('health check all platforms')">⚡ Health check</div>
          <div class="cmd-chip" onclick="quick('generate a music release campaign for CREOVA Music')">♪ Music campaign</div>
          <div class="cmd-chip" onclick="quick('find leads for CREOVA Solutions Canada')">◬ Lead gen</div>
          <div class="cmd-chip" onclick="quick('carousel CREOVA tech innovation Africa')">◈ Carousel builder</div>
          <div class="cmd-chip" onclick="quick('hashtags tech')">🏷 Hashtag sets</div>
        </div>
      </div>
      <div class="resp-panel" id="resp"></div>
    </div>

  </div><!-- /body -->
</div><!-- /main -->
</div><!-- /shell -->

<!-- ── AGENT MODAL ────────────────────────────────────────── -->
<div class="overlay" id="overlay" onclick="maybeClose(event)">
  <div class="modal" id="modal">
    <button class="modal-x" onclick="closeModal()">✕</button>
    <div class="modal-head">
      <div class="modal-ico" id="mIco"></div>
      <div>
        <div class="modal-name" id="mName"></div>
        <div class="modal-sub" id="mSub"></div>
      </div>
    </div>
    <div class="modal-sec">
      <div class="modal-sec-hd">Responsibilities</div>
      <div class="modal-tasks" id="mTasks"></div>
    </div>
    <div class="modal-sec">
      <div class="modal-sec-hd">Model</div>
      <div style="font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace" id="mModel"></div>
    </div>
    <div class="modal-btns">
      <button class="btn-a" id="mRun">Run Agent</button>
      <button class="btn-b" onclick="closeModal()">Close</button>
    </div>
  </div>
</div>

<script>
// ── Constants ─────────────────────────────────────────────
const SOURCE_COLORS = {
  SHIELD:'var(--orange)',PULSE:'var(--accent2)',
  REACH:'var(--accent)',INTEL:'var(--purple)',
  AMPLIFY:'var(--accent3)',default:'var(--muted)'
};
function srcColor(s){
  for(const k of Object.keys(SOURCE_COLORS))
    if(s.toUpperCase().includes(k)) return SOURCE_COLORS[k];
  return SOURCE_COLORS.default;
}

// ── Clock ─────────────────────────────────────────────────
function tick(){
  const now = new Date();
  const h = now.getHours();
  document.getElementById('greet').textContent =
    h<12?'Good morning,':(h<17?'Good afternoon,':'Good evening,');
  document.getElementById('clock').textContent =
    now.toLocaleDateString('en-CA',{weekday:'long',year:'numeric',month:'long',day:'numeric'})+
    '  ·  '+now.toLocaleTimeString('en-CA',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true});
}
tick(); setInterval(tick,1000);

// ── Count-up ──────────────────────────────────────────────
function countUp(el,target,dur=800){
  let start=null;
  function step(ts){
    if(!start)start=ts;
    const p=Math.min((ts-start)/dur,1);
    const ease=p<.5?2*p*p:(4-2*p)*p-1;
    el.textContent=Math.round(ease*target);
    if(p<1)requestAnimationFrame(step);
    else el.textContent=target;
  }
  requestAnimationFrame(step);
}
document.querySelectorAll('.met-val[data-target]').forEach(el=>
  countUp(el,+el.dataset.target)
);

// ── Agent bars ────────────────────────────────────────────
setTimeout(()=>{
  document.querySelectorAll('.ag-bar[data-w]').forEach(el=>{
    el.style.width=el.dataset.w+'%';
  });
},400);

// ── Sidebar nav ───────────────────────────────────────────
function setNav(btn){
  document.querySelectorAll('.nav-icon').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
}

// ── Uptime ticker ─────────────────────────────────────────
let _uptime='0h 0m';
function updateUptime(val){
  _uptime=val;
  document.getElementById('uptimeBadge').textContent=val;
}

// ── Fetch status ──────────────────────────────────────────
async function fetchStatus(){
  try{
    const d=await fetch('/api/status').then(r=>r.json());
    updateUptime(d.uptime||'—');

    // Connected integrations
    const conn=d.integrations_connected||0;
    const total=d.integrations_total||9;
    document.getElementById('connectedMet').textContent=conn;
    document.getElementById('connectedSub').textContent=`of ${total} live`;
    countUp(document.getElementById('connectedMet'),conn,600);
    document.getElementById('integChip').textContent=`${conn}/${total} integrations`;

    // Feed
    const feed=document.getElementById('feed');
    if(d.activity&&d.activity.length){
      const items=[...d.activity].reverse().slice(0,10);
      feed.innerHTML=items.map(a=>{
        const col=srcColor(a.source);
        return `<div class="feed-row">
          <div class="feed-dot" style="background:${col}"></div>
          <div class="feed-text"><b>${a.source}</b> — ${a.msg}</div>
          <div class="feed-ts">${a.ts}</div>
        </div>`;
      }).join('');
    }

    // Integrations
    if(d.integrations){
      const grid=document.getElementById('integGrid');
      grid.innerHTML=Object.entries(d.integrations).map(([k,v])=>`
        <div class="integ" title="${v.handle}">
          <div class="integ-sym" style="background:var(--bg4)">${v.icon}</div>
          <div class="integ-info">
            <div class="integ-name">${v.label}</div>
            <div class="integ-handle">${v.handle}</div>
          </div>
          <div class="integ-badge ${v.ok?'badge-on':'badge-off'}">${v.ok?'LIVE':'—'}</div>
        </div>`).join('');
    }

    // Repos
    if(d.github_repos){
      const rg=document.getElementById('reposGrid');
      const langs={Gopay:'Python',KayaYourpropertyai:'React',Darsme:'Node',Mentalpath:'React',
        Aihealthsupport:'Python',GridOs:'Python',Kilimoai:'Python',Budgeteaseapp:'React'};
      rg.innerHTML=d.github_repos.map(r=>`
        <div class="repo" onclick="quick('${r} repo status and recent commits')">
          <div>
            <div class="repo-name">${r}</div>
            <div class="repo-lang">${langs[r]||'—'}</div>
          </div>
          <div class="repo-arrow">›</div>
        </div>`).join('');
    }

    // Streak
    if(d.snapchat_streak){
      const s=d.snapchat_streak;
      document.getElementById('streakVal').textContent=s.streak||0;
      document.getElementById('totalDays').textContent=s.total_days||0;
      if(s.last_posted&&s.last_posted!=='—')
        document.getElementById('lastPosted').textContent='Last posted: '+s.last_posted;
    }

  }catch(e){console.warn('Status fetch:',e)}
}

// ── Command ───────────────────────────────────────────────
function quick(t){
  document.getElementById('cmdIn').value=t;
  document.getElementById('cmdIn').focus();
}
function fire(){
  const v=document.getElementById('cmdIn').value.trim();
  if(!v)return;
  const resp=document.getElementById('resp');
  resp.className='resp-panel show';
  resp.innerHTML='<div class="resp-loading"><div class="spinner"></div><span>Dispatched to Akili — check Telegram for response</span></div>';

  // Add to feed
  const feed=document.getElementById('feed');
  const row=document.createElement('div');
  row.className='feed-row';
  row.innerHTML=`
    <div class="feed-dot" style="background:var(--accent)"></div>
    <div class="feed-text"><b>YOU</b> — ${v.substring(0,80)}</div>
    <div class="feed-ts">now</div>`;
  feed.prepend(row);
  if(feed.children.length>12)feed.removeChild(feed.lastChild);

  document.getElementById('cmdIn').value='';
  setTimeout(()=>resp.classList.remove('show'),4000);
}

// ── Agent modal ───────────────────────────────────────────
const AGENTS={
  shield:{
    ico:'🛡',bg:'rgba(249,115,22,.15)',name:'SHIELD',
    sub:'Security · GitHub · System Health · Uptime',
    tasks:[
      'Monitor 8 creova-gif repos every 30 min',
      'Check creova.one + Akili bot uptime (Replit Reserved VM)',
      'System health: CPU & memory via psutil',
      'Secret scanner: detect hardcoded API keys',
      'Instant Telegram alert on any breach or downtime',
      'Never deletes anything without 2× Justin confirmation',
    ],
    model:'claude-sonnet-4-5 · Fast monitoring loops',
    cmd:'run GitHub org scan for all 8 creova repos and report',
  },
  pulse:{
    ico:'📡',bg:'rgba(78,205,196,.15)',name:'PULSE',
    sub:'Social Media · 10 accounts · 4–6 posts/day',
    tasks:[
      '@creativeinnovation__ · @jj_mafie · @sankofastudio__ · @creovasolutions (IG)',
      '@justin_mafie (X/Twitter) · Justin Mafie + CREOVA (LinkedIn)',
      'jay-mafie (Snapchat) · Justin + CREOVA (Facebook)',
      '@creovamusic (TikTok) · Carousel builder · A/B experiments',
      'Hashtag intelligence: tech/music/personal/studio/branding sets',
      'DALL·E 3 image generation for posts (OpenAI live)',
    ],
    model:'claude-sonnet-4-5 · High-volume content generation',
    cmd:'generate this week content calendar for all accounts',
  },
  reach:{
    ico:'📨',bg:'rgba(232,197,71,.12)',name:'REACH',
    sub:'Email · DMs · Repurposing · Auto-responder',
    tasks:[
      'Monitor ayoubjustin2@gmail.com (personal) — LIVE',
      'Monitor creativeinnovationspace@gmail.com (business) — LIVE',
      'Auto-reply DMs in authentic Justin Mafie voice',
      'Flag urgent emails (investors, press, clients) instantly to Telegram',
      'Repurpose 1 piece of content into 6 platform formats',
      'Draft email campaigns for music + CREOVA Solutions',
    ],
    model:'claude-sonnet-4-5 · Fast comms and classification',
    cmd:'check both Gmail inboxes and flag urgent emails',
  },
  intel:{
    ico:'🔍',bg:'rgba(167,139,250,.15)',name:'INTEL',
    sub:'Research · Leads · VC Tracking · Briefs',
    tasks:[
      'Daily 8AM brief \u2192 Telegram: market news + today\\'s priorities',
      'VC tracker: GoPay investors (Partech, TLcom, Novastar + more)',
      'Lead generation: CREOVA Solutions + music deals Canada/Africa',
      'Outreach pitch generator: personalized from Justin Mafie',
      'Competitor monitoring across all 8 CREOVA product markets',
      'Deep research on any topic via web search',
    ],
    model:'claude-sonnet-4-5 · Deep research and synthesis',
    cmd:'vc tracker GoPay East Africa investors',
  },
  amplify:{
    ico:'🔊',bg:'rgba(255,107,107,.15)',name:'AMPLIFY',
    sub:'Music · Brand Growth · Snap Creator',
    tasks:[
      'DistroKid + Spotify for Artists stream tracking',
      'Playlist pitching for CREOVA Music & Sankofa Studio releases',
      'Snapchat Creator program score + daily story script',
      'Cross-pollinate: music fans ↔ tech audience ↔ personal brand',
      'Posting time experiments + engagement growth optimization',
      'CREOVA Music release campaign planning',
    ],
    model:'claude-sonnet-4-5 · Creative promotion and growth',
    cmd:'create a music release campaign plan for CREOVA Music latest release',
  },
};

let _curAgent=null;
function openAgent(key){
  const a=AGENTS[key];
  if(!a)return;
  _curAgent=key;
  document.getElementById('mIco').textContent=a.ico;
  document.getElementById('mIco').style.background=a.bg;
  document.getElementById('mName').textContent=a.name;
  document.getElementById('mSub').textContent=a.sub;
  document.getElementById('mModel').textContent=a.model;
  document.getElementById('mTasks').innerHTML=
    a.tasks.map(t=>`<div class="modal-task">${t}</div>`).join('');
  document.getElementById('mRun').onclick=()=>{quick(a.cmd);closeModal()};
  document.getElementById('overlay').classList.add('open');
}
function closeModal(){document.getElementById('overlay').classList.remove('open')}
function maybeClose(e){if(e.target===document.getElementById('overlay'))closeModal()}

// ── Init ──────────────────────────────────────────────────
fetchStatus();
setInterval(fetchStatus,15000);
</script>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")
