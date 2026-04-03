# ============================================================
# AKILI DASHBOARD — Mission Control
# Full-featured web UI for managing AKILI agents
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
                # Parse: 2026-04-03 19:51:17,786 | INFO | AKILI-CORE | [COMMAND] Justin: status
                m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \| (\w+) \| ([^\|]+) \| (.+)$", line)
                if m:
                    ts, level, source, msg = m.groups()
                    source = source.strip()
                    msg = msg.strip()
                    # Skip noise
                    if "terminated by other getUpdates" in msg:
                        continue
                    if "httpx" in source:
                        continue
                    if "HEARTBEAT" in msg and "OK" in msg:
                        continue
                    entries.append({
                        "ts": ts[11:16],  # HH:MM
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
        "twitter":   {"label": "Twitter / X", "handle": "@justin_mafie",        "icon": "𝕏",  "ok": bool(env.get("TWITTER_API_KEY"))},
        "github":    {"label": "GitHub",       "handle": "creova-gif · 8 repos", "icon": "⬡",  "ok": bool(env.get("GITHUB_TOKEN"))},
        "instagram": {"label": "Instagram",    "handle": "@creativeinnovation__", "icon": "◈",  "ok": bool(env.get("INSTAGRAM_ACCESS_TOKEN"))},
        "linkedin":  {"label": "LinkedIn",     "handle": "Justin Mafie",         "icon": "in", "ok": bool(env.get("LINKEDIN_ACCESS_TOKEN"))},
        "snapchat":  {"label": "Snapchat",     "handle": "jay-mafie",            "icon": "👻", "ok": bool(env.get("SNAPCHAT_ACCESS_TOKEN"))},
        "tiktok":    {"label": "TikTok",       "handle": "@creovamusic",         "icon": "♪",  "ok": bool(env.get("TIKTOK_ACCESS_TOKEN"))},
        "facebook":  {"label": "Facebook",     "handle": "Justin Mafie",         "icon": "f",  "ok": bool(env.get("FACEBOOK_ACCESS_TOKEN"))},
        "gmail":     {"label": "Gmail",        "handle": "personal",             "icon": "✉",  "ok": os.path.exists("config/gmail_personal_token.json")},
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
            "SHIELD": {"desc": "Security & GitHub monitor", "status": "active"},
            "PULSE":  {"desc": "Social media publisher",   "status": "active"},
            "REACH":  {"desc": "Email & outreach",         "status": "active"},
            "INTEL":  {"desc": "Market & trend analysis",  "status": "active"},
            "AMPLIFY":{"desc": "Growth & engagement",      "status": "active"},
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
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AKILI — Mission Control</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:      #080b10;
    --surface: #0d1117;
    --card:    #111820;
    --border:  #1e2a38;
    --text:    #c9d1d9;
    --muted:   #4a5568;
    --accent:  #58a6ff;
    --green:   #3fb950;
    --yellow:  #d29922;
    --red:     #f85149;
    --purple:  #bc8cff;
    --font:    'SF Mono', 'Fira Code', 'Consolas', monospace;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 13px;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* ── Header ── */
  header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .logo {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .logo-mark {{
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 900;
    color: #080b10;
    box-shadow: 0 0 16px rgba(88,166,255,0.3);
  }}
  .logo-text {{ font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 2px; }}
  .logo-sub  {{ font-size: 10px; color: var(--muted); letter-spacing: 1px; margin-top: 1px; }}
  .header-right {{ display: flex; align-items: center; gap: 16px; }}
  .live-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
  .live-label {{ font-size: 11px; color: var(--green); letter-spacing: 1px; }}
  .clock {{ color: var(--muted); font-size: 11px; }}

  /* ── Layout ── */
  .container {{
    max-width: 1280px;
    margin: 0 auto;
    padding: 24px 20px;
  }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }}
  .grid-5 {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }}
  @media(max-width:900px) {{
    .grid-3,.grid-5 {{ grid-template-columns: 1fr 1fr; }}
    .grid-4 {{ grid-template-columns: 1fr 1fr; }}
    .grid-2 {{ grid-template-columns: 1fr; }}
  }}
  @media(max-width:600px) {{
    .grid-3,.grid-4,.grid-5 {{ grid-template-columns: 1fr; }}
  }}

  /* ── Cards ── */
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.15s;
  }}
  .card:hover {{ border-color: var(--accent); transform: translateY(-1px); }}
  .card-label {{
    font-size: 9px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--muted); margin-bottom: 10px;
  }}
  .card-title {{ font-size: 22px; font-weight: 700; color: #fff; }}
  .card-sub {{ font-size: 11px; color: var(--muted); margin-top: 4px; }}

  /* ── Stat cards ── */
  .stat-card .stat-icon {{
    font-size: 28px; margin-bottom: 10px;
    display: block;
  }}
  .stat-card .stat-value {{ font-size: 30px; font-weight: 800; color: #fff; }}
  .stat-card .stat-label {{ font-size: 10px; color: var(--muted); letter-spacing: 1px; margin-top: 2px; }}
  .stat-accent-blue  {{ border-top: 2px solid var(--accent); }}
  .stat-accent-green {{ border-top: 2px solid var(--green); }}
  .stat-accent-purple{{ border-top: 2px solid var(--purple); }}

  /* ── Agent cards ── */
  .agent-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    transition: all 0.2s;
  }}
  .agent-card:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
  .agent-name {{
    font-size: 13px; font-weight: 700; color: #fff;
    letter-spacing: 1px; margin-bottom: 4px;
  }}
  .agent-desc {{ font-size: 10px; color: var(--muted); margin-bottom: 12px; }}
  .agent-status {{
    display: flex; align-items: center; gap: 6px;
    font-size: 10px; color: var(--green);
  }}
  .agent-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    animation: pulse 2s infinite;
  }}
  .agent-icon {{
    font-size: 22px; margin-bottom: 10px; display: block;
  }}

  /* ── Integration grid ── */
  .integration-item {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s;
  }}
  .integration-item:hover {{ border-color: rgba(88,166,255,0.4); }}
  .int-icon {{
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 700;
    flex-shrink: 0;
  }}
  .int-icon-ok   {{ background: rgba(63,185,80,0.15); color: var(--green); }}
  .int-icon-off  {{ background: rgba(74,85,104,0.2); color: var(--muted); }}
  .int-info {{ flex: 1; min-width: 0; }}
  .int-name {{ font-size: 11px; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .int-handle {{ font-size: 10px; color: var(--muted); }}
  .int-badge {{
    font-size: 9px; letter-spacing: 0.5px; padding: 2px 6px; border-radius: 10px;
    font-weight: 700; flex-shrink: 0;
  }}
  .badge-ok  {{ background: rgba(63,185,80,0.2); color: var(--green); }}
  .badge-off {{ background: rgba(74,85,104,0.2); color: var(--muted); }}

  /* ── Section header ── */
  .section-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px;
  }}
  .section-title {{
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted);
    display: flex; align-items: center; gap: 8px;
  }}
  .section-title::before {{ content:''; display:block; width:3px; height:12px; background:var(--accent); border-radius:2px; }}
  .section-link {{ font-size: 10px; color: var(--accent); text-decoration: none; }}
  .section-link:hover {{ text-decoration: underline; }}

  /* ── Activity feed ── */
  .activity-feed {{
    display: flex; flex-direction: column; gap: 2px;
    max-height: 280px; overflow-y: auto;
  }}
  .activity-feed::-webkit-scrollbar {{ width: 4px; }}
  .activity-feed::-webkit-scrollbar-track {{ background: transparent; }}
  .activity-feed::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}
  .activity-item {{
    display: grid;
    grid-template-columns: 42px 90px 1fr;
    gap: 8px;
    align-items: start;
    padding: 6px 8px;
    border-radius: 6px;
    transition: background 0.1s;
  }}
  .activity-item:hover {{ background: rgba(255,255,255,0.03); }}
  .act-time {{ font-size: 10px; color: var(--muted); font-variant-numeric: tabular-nums; padding-top: 1px; }}
  .act-source {{
    font-size: 9px; color: var(--accent); letter-spacing: 0.5px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding-top: 2px;
  }}
  .act-msg {{ font-size: 11px; color: var(--text); line-height: 1.4; }}
  .act-error .act-msg {{ color: var(--red); }}
  .act-warn  .act-msg {{ color: var(--yellow); }}

  /* ── Repos ── */
  .repo-item {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    display: flex; align-items: center; justify-content: space-between;
    gap: 8px;
    transition: all 0.2s;
  }}
  .repo-item:hover {{ border-color: rgba(88,166,255,0.4); }}
  .repo-name {{ font-size: 11px; font-weight: 700; color: #fff; }}
  .repo-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--green); flex-shrink: 0; }}

  /* ── Quick actions ── */
  .quick-actions {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
  }}
  .quick-action {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
  }}
  .quick-action:hover {{ border-color: var(--accent); background: rgba(88,166,255,0.06); transform: translateY(-1px); }}
  .qa-icon {{ font-size: 20px; margin-bottom: 8px; display: block; }}
  .qa-title {{ font-size: 11px; font-weight: 700; color: #fff; margin-bottom: 2px; }}
  .qa-cmd   {{ font-size: 9px; color: var(--accent); letter-spacing: 0.5px; }}

  /* ── Snap streak ── */
  .streak-number {{
    font-size: 52px; font-weight: 900;
    background: linear-gradient(135deg, #ff8c00, #ff4500);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1;
  }}
  .streak-fire {{ font-size: 36px; }}

  /* ── Setup banner ── */
  .setup-links {{
    display: flex; gap: 10px; flex-wrap: wrap;
  }}
  .setup-btn {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.3);
    color: var(--accent);
    padding: 8px 14px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 11px;
    font-family: var(--font);
    transition: all 0.2s;
    cursor: pointer;
  }}
  .setup-btn:hover {{ background: rgba(88,166,255,0.2); border-color: var(--accent); }}
  .setup-btn.done {{
    background: rgba(63,185,80,0.1);
    border-color: rgba(63,185,80,0.3);
    color: var(--green);
  }}

  /* ── Footer ── */
  footer {{
    text-align: center; padding: 28px;
    color: var(--muted); font-size: 10px; letter-spacing: 1px;
    border-top: 1px solid var(--border);
    margin-top: 12px;
  }}

  /* ── Shimmer loading ── */
  .shimmer {{ animation: shimmer 1.5s infinite; }}
  @keyframes shimmer {{ 0%,100%{{opacity:0.4}} 50%{{opacity:0.9}} }}
</style>
</head>
<body>

<!-- HEADER -->
<header>
  <div class="logo">
    <div class="logo-mark">A</div>
    <div>
      <div class="logo-text">AKILI</div>
      <div class="logo-sub">CREOVA MISSION CONTROL</div>
    </div>
  </div>
  <div class="header-right">
    <div class="live-dot"></div>
    <span class="live-label">LIVE</span>
    <span class="clock" id="clock">—</span>
  </div>
</header>

<div class="container">

  <!-- STAT ROW -->
  <div class="grid-3" style="margin-bottom:20px">
    <div class="card stat-card stat-accent-blue">
      <div class="card-label">Agents Online</div>
      <div class="stat-value" id="agents-count">5 / 5</div>
      <div class="stat-label">ALL SYSTEMS ACTIVE</div>
    </div>
    <div class="card stat-card stat-accent-green">
      <div class="card-label">Platforms Connected</div>
      <div class="stat-value" id="integrations-count" class="shimmer">—</div>
      <div class="stat-label" id="integrations-sub">LOADING…</div>
    </div>
    <div class="card stat-card stat-accent-purple">
      <div class="card-label">Uptime</div>
      <div class="stat-value" id="uptime">—</div>
      <div class="stat-label" id="timestamp">—</div>
    </div>
  </div>

  <!-- AGENTS -->
  <div class="section-header">
    <div class="section-title">Active Agents</div>
  </div>
  <div class="grid-5" style="margin-bottom:24px">
    <div class="agent-card">
      <span class="agent-icon">🛡</span>
      <div class="agent-name">SHIELD</div>
      <div class="agent-desc">Security & GitHub Monitor</div>
      <div class="agent-status"><span class="agent-dot"></span>Active · 8 repos</div>
    </div>
    <div class="agent-card">
      <span class="agent-icon">📡</span>
      <div class="agent-name">PULSE</div>
      <div class="agent-desc">Social Media Publisher</div>
      <div class="agent-status"><span class="agent-dot"></span>Active · 6 platforms</div>
    </div>
    <div class="agent-card">
      <span class="agent-icon">📬</span>
      <div class="agent-name">REACH</div>
      <div class="agent-desc">Email & Outreach</div>
      <div class="agent-status"><span class="agent-dot"></span>Active · Gmail pending</div>
    </div>
    <div class="agent-card">
      <span class="agent-icon">🔍</span>
      <div class="agent-name">INTEL</div>
      <div class="agent-desc">Market & Trend Analysis</div>
      <div class="agent-status"><span class="agent-dot"></span>Active · Monitoring</div>
    </div>
    <div class="agent-card">
      <span class="agent-icon">📈</span>
      <div class="agent-name">AMPLIFY</div>
      <div class="agent-desc">Growth & Engagement</div>
      <div class="agent-status"><span class="agent-dot"></span>Active · Evening push</div>
    </div>
  </div>

  <!-- INTEGRATIONS + STREAK side by side -->
  <div class="grid-2">
    <!-- INTEGRATIONS -->
    <div>
      <div class="section-header">
        <div class="section-title">Integrations</div>
        <span id="int-summary" style="font-size:10px;color:var(--muted)">Loading…</span>
      </div>
      <div id="integration-grid" style="display:flex;flex-direction:column;gap:8px;">
        <!-- filled by JS -->
      </div>
    </div>

    <!-- RIGHT COLUMN: STREAK + REPOS -->
    <div style="display:flex;flex-direction:column;gap:16px;">

      <!-- SNAPCHAT STREAK -->
      <div>
        <div class="section-header">
          <div class="section-title">Snapchat Streak</div>
        </div>
        <div class="card" style="display:flex;align-items:center;gap:24px;">
          <span class="streak-fire">🔥</span>
          <div>
            <div class="streak-number" id="streak-num">—</div>
            <div style="font-size:10px;color:var(--muted);margin-top:4px;">day streak</div>
            <div style="font-size:10px;color:var(--muted);margin-top:2px;">Last posted: <span id="streak-date">—</span></div>
          </div>
          <div style="margin-left:auto;text-align:right;">
            <div style="font-size:22px;color:#fff;font-weight:800;" id="streak-total">—</div>
            <div style="font-size:9px;color:var(--muted);">TOTAL DAYS</div>
          </div>
        </div>
      </div>

      <!-- GITHUB REPOS -->
      <div>
        <div class="section-header">
          <div class="section-title">GitHub — creova-gif</div>
          <span style="font-size:10px;color:var(--green);">8 active repos</span>
        </div>
        <div id="repo-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <!-- filled by JS -->
        </div>
      </div>

    </div>
  </div>

  <!-- QUICK COMMANDS -->
  <div class="section-header" style="margin-top:8px">
    <div class="section-title">Quick Commands</div>
    <span style="font-size:10px;color:var(--muted)">Send via Telegram</span>
  </div>
  <div class="quick-actions" style="margin-bottom:24px">
    <div class="quick-action" onclick="copyCmd('status')">
      <span class="qa-icon">⚡</span>
      <div class="qa-title">System Status</div>
      <div class="qa-cmd">→ status</div>
    </div>
    <div class="quick-action" onclick="copyCmd('health check')">
      <span class="qa-icon">🩺</span>
      <div class="qa-title">Health Check</div>
      <div class="qa-cmd">→ health check</div>
    </div>
    <div class="quick-action" onclick="copyCmd('snapchat plan')">
      <span class="qa-icon">👻</span>
      <div class="qa-title">Snapchat Plan</div>
      <div class="qa-cmd">→ snapchat plan</div>
    </div>
    <div class="quick-action" onclick="copyCmd('tiktok plan')">
      <span class="qa-icon">🎵</span>
      <div class="qa-title">TikTok Strategy</div>
      <div class="qa-cmd">→ tiktok plan</div>
    </div>
    <div class="quick-action" onclick="copyCmd('tweet today')">
      <span class="qa-icon">𝕏</span>
      <div class="qa-title">Tweet Today</div>
      <div class="qa-cmd">→ tweet today</div>
    </div>
    <div class="quick-action" onclick="copyCmd('github report')">
      <span class="qa-icon">⬡</span>
      <div class="qa-title">GitHub Report</div>
      <div class="qa-cmd">→ github report</div>
    </div>
    <div class="quick-action" onclick="copyCmd('my personal emails')">
      <span class="qa-icon">📧</span>
      <div class="qa-title">Check Emails</div>
      <div class="qa-cmd">→ my personal emails</div>
    </div>
    <div class="quick-action" onclick="copyCmd('morning brief')">
      <span class="qa-icon">🌅</span>
      <div class="qa-title">Morning Brief</div>
      <div class="qa-cmd">→ morning brief</div>
    </div>
  </div>

  <!-- SETUP SHORTCUTS -->
  <div class="section-header">
    <div class="section-title">Platform Setup</div>
  </div>
  <div class="card" style="margin-bottom:24px">
    <div style="margin-bottom:12px;color:var(--muted);font-size:11px;">Connect remaining platforms to unlock full AKILI capability.</div>
    <div class="setup-links">
      <a class="setup-btn done" href="#"><span>✓</span> Twitter Connected</a>
      <a class="setup-btn done" href="#"><span>✓</span> GitHub Connected</a>
      <a class="setup-btn" href="/tiktok/auth"><span>🎵</span> Connect TikTok</a>
      <a class="setup-btn" href="/gmail/auth?account=personal"><span>📧</span> Connect Gmail</a>
      <a class="setup-btn" href="/gmail/auth?account=business"><span>📧</span> Gmail Business</a>
    </div>
  </div>

  <!-- ACTIVITY FEED -->
  <div class="section-header">
    <div class="section-title">Live Activity Log</div>
    <span style="font-size:10px;color:var(--muted)">Auto-refreshes every 15s</span>
  </div>
  <div class="card" style="margin-bottom:20px;padding:0;">
    <div class="activity-feed" id="activity-feed" style="padding:12px;">
      <div style="color:var(--muted);font-size:11px;padding:8px;">Loading activity…</div>
    </div>
  </div>

</div>

<footer>
  AKILI &nbsp;·&nbsp; CREOVA AI Operating System &nbsp;·&nbsp; Justin Mafie &nbsp;·&nbsp; creova.one
</footer>

<!-- COPY TOAST -->
<div id="toast" style="
  position:fixed; bottom:24px; left:50%; transform:translateX(-50%) translateY(40px);
  background:#1e2a38; border:1px solid var(--accent); color:var(--accent);
  padding:10px 20px; border-radius:8px; font-size:11px;
  opacity:0; transition:all 0.3s; z-index:999; pointer-events:none;
">Copied to clipboard!</div>

<script>
// ── Clock ──
function updateClock() {{
  const d = new Date();
  document.getElementById('clock').textContent =
    d.toUTCString().slice(17,22) + ' UTC';
}}
setInterval(updateClock, 1000);
updateClock();

// ── Fetch status ──
async function fetchStatus() {{
  try {{
    const r = await fetch('/api/status');
    const d = await r.json();
    render(d);
  }} catch(e) {{
    console.error('Status fetch failed', e);
  }}
}}

function render(d) {{
  // Stats
  document.getElementById('integrations-count').textContent =
    d.integrations_connected + ' / 8';
  document.getElementById('integrations-sub').textContent =
    d.integrations_connected === 8 ? 'ALL PLATFORMS LIVE' : 'SOME PENDING';
  document.getElementById('uptime').textContent = d.uptime_since;
  document.getElementById('timestamp').textContent = d.timestamp;

  // Integration grid
  const grid = document.getElementById('integration-grid');
  grid.innerHTML = '';
  const icons = {{
    twitter:'𝕏', github:'⬡', instagram:'◈', linkedin:'in',
    snapchat:'👻', tiktok:'♪', facebook:'f', gmail:'✉'
  }};
  Object.entries(d.integrations).forEach(([k, v]) => {{
    const ok = v.ok;
    grid.innerHTML += `
    <div class="integration-item">
      <div class="int-icon ${{ok?'int-icon-ok':'int-icon-off'}}">${{icons[k]||'?'}}</div>
      <div class="int-info">
        <div class="int-name">${{v.label}}</div>
        <div class="int-handle">${{v.handle}}</div>
      </div>
      <span class="int-badge ${{ok?'badge-ok':'badge-off'}}">${{ok?'LIVE':'SETUP'}}</span>
    </div>`;
  }});

  // Int summary
  document.getElementById('int-summary').textContent =
    d.integrations_connected + ' connected · ' + (8-d.integrations_connected) + ' pending';

  // Streak
  const s = d.snapchat_streak;
  document.getElementById('streak-num').textContent = s.streak;
  document.getElementById('streak-date').textContent = s.last_posted;
  document.getElementById('streak-total').textContent = s.total_days;

  // Repos
  const rg = document.getElementById('repo-grid');
  rg.innerHTML = '';
  d.github_repos.forEach(r => {{
    rg.innerHTML += `
    <div class="repo-item">
      <span class="repo-name">${{r}}</span>
      <span class="repo-dot"></span>
    </div>`;
  }});

  // Activity
  const feed = document.getElementById('activity-feed');
  if (!d.activity.length) {{
    feed.innerHTML = '<div style="color:var(--muted);font-size:11px;padding:8px;">No recent activity.</div>';
    return;
  }}
  feed.innerHTML = [...d.activity].reverse().map(a => {{
    const cls = a.level === 'ERROR' ? 'act-error' : a.level === 'WARNING' ? 'act-warn' : '';
    return `<div class="activity-item ${{cls}}">
      <span class="act-time">${{a.ts}}</span>
      <span class="act-source">${{a.source}}</span>
      <span class="act-msg">${{escHtml(a.msg)}}</span>
    </div>`;
  }}).join('');
}}

function escHtml(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

// ── Copy command ──
function copyCmd(cmd) {{
  navigator.clipboard.writeText(cmd).then(() => {{
    const t = document.getElementById('toast');
    t.textContent = '✓ "' + cmd + '" — paste into Telegram';
    t.style.opacity = '1';
    t.style.transform = 'translateX(-50%) translateY(0)';
    setTimeout(() => {{
      t.style.opacity = '0';
      t.style.transform = 'translateX(-50%) translateY(40px)';
    }}, 2200);
  }});
}}

// ── Init ──
fetchStatus();
setInterval(fetchStatus, 15000);
</script>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")
