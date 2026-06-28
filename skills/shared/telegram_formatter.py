# ============================================================
# TELEGRAM FORMATTER — Shared Skill (All Agents)
# Every output is creative, clear, detailed, and on-brand
# Uses HTML parse_mode — consistent with Akili codebase
# ============================================================

import os
import logging
from datetime import datetime
from anthropic import AsyncAnthropic

log = logging.getLogger("AKILI.Formatter")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

DIVIDER       = "━━━━━━━━━━━━━━━━━━━━"
LIGHT_DIVIDER = "─ ─ ─ ─ ─ ─ ─ ─ ─ ─"

AGENT_HEADERS = {
    "SHIELD":  "🛡 <b>SHIELD</b> — Security &amp; Infrastructure",
    "PULSE":   "📡 <b>PULSE</b> — Social Media &amp; Content",
    "REACH":   "📨 <b>REACH</b> — Communications &amp; Outreach",
    "INTEL":   "🔍 <b>INTEL</b> — Strategy &amp; Intelligence",
    "AMPLIFY": "🔊 <b>AMPLIFY</b> — Music &amp; Brand Growth",
    "CORE":    "⚡ <b>AKILI CORE</b> — Command Center",
}


class TelegramFormatter:
    """
    Shared formatting layer used by all 5 agents.
    Uses HTML tags (<b>, <i>, <code>) — all outputs sent with parse_mode='HTML'.
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_KEY) if ANTHROPIC_KEY else None

    def format(self, agent: str, content_type: str, data: dict) -> str:
        header = AGENT_HEADERS.get(agent.upper(), f"⚡ <b>{agent}</b>")
        ts     = datetime.now().strftime("%H:%M")

        formatters = {
            "report":      self._format_report,
            "alert":       self._format_alert,
            "approval":    self._format_approval,
            "brief":       self._format_brief,
            "campaign":    self._format_campaign,
            "research":    self._format_research,
            "reply_draft": self._format_reply_draft,
            "status":      self._format_status,
            "error":       self._format_error,
            "milestone":   self._format_milestone,
            "weekly_plan": self._format_weekly_plan,
        }

        fn   = formatters.get(content_type, self._format_generic)
        body = fn(data)
        return f"{header}\n<code>{ts}</code>\n\n{body}"

    # ── Report ────────────────────────────────────────────────
    def _format_report(self, d: dict) -> str:
        sections = []
        if d.get("summary"):
            sections.append(f"📋 <b>Summary</b>\n{d['summary']}")
        if d.get("metrics"):
            metric_lines = "\n".join([f"  ▸ {k}: <code>{v}</code>" for k, v in d["metrics"].items()])
            sections.append(f"📊 <b>Metrics</b>\n{metric_lines}")
        if d.get("issues"):
            issue_lines = "\n".join([f"  ⚠️ {i}" for i in d["issues"]])
            sections.append(f"🚨 <b>Issues Detected</b>\n{issue_lines}")
        if d.get("actions"):
            action_lines = "\n".join([f"  {i+1}. {a}" for i, a in enumerate(d["actions"])])
            sections.append(f"⚡ <b>Required Actions</b>\n{action_lines}")
        if d.get("next_check"):
            sections.append(f"🕐 <b>Next check:</b> {d['next_check']}")
        return f"\n{DIVIDER}\n".join(sections)

    # ── Alert ─────────────────────────────────────────────────
    def _format_alert(self, d: dict) -> str:
        severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        icon = severity_icons.get(d.get("severity", "high"), "🟠")
        return (
            f"{icon} <b>{d.get('severity', 'HIGH').upper()} ALERT</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>What happened:</b>\n{d.get('what', 'Unknown event')}\n\n"
            f"<b>Affected:</b> <code>{d.get('affected', 'Unknown')}</code>\n"
            f"<b>Detected at:</b> <code>{d.get('time', datetime.now().strftime('%H:%M'))}</code>\n\n"
            f"<b>Action taken:</b> {d.get('action_taken', 'Logged and monitoring')}\n\n"
            f"<b>Do you need to act?</b> {d.get('justin_action', 'No — Akili handling it')}\n"
            f"{DIVIDER}"
        )

    # ── Post approval ─────────────────────────────────────────
    def _format_approval(self, d: dict) -> str:
        platform_icons = {
            "instagram": "📸", "twitter": "🐦", "linkedin": "💼",
            "tiktok": "🎵", "facebook": "📘", "snapchat": "👻",
        }
        icon         = platform_icons.get(d.get("platform", "").lower(), "📱")
        accounts_str = " · ".join([f"@{a}" for a in d.get("accounts", [])])
        hashtags_str = " ".join(d.get("hashtags", []))
        return (
            f"{icon} <b>{d.get('platform','').upper()} — POST READY FOR APPROVAL</b>\n\n"
            f"<b>Accounts:</b> {accounts_str}\n"
            f"<b>Theme:</b> <i>{d.get('theme', '')}</i>\n"
            f"<b>Best time:</b> <code>{d.get('best_time', 'Now')}</code>\n\n"
            f"{DIVIDER}\n"
            f"{d.get('caption', '')}\n\n"
            f"<i>{hashtags_str}</i>\n"
            f"{DIVIDER}\n\n"
            f"📸 <b>Visual:</b> {d.get('visual_note', 'Choose a strong on-brand image')}\n"
            f"🎯 <b>Goal:</b> {d.get('goal', 'Engagement + brand awareness')}\n\n"
            f"Reply:\n"
            f"✅ <code>POST {d.get('approval_id', '')}</code> — publish now\n"
            f"✏️ <code>EDIT {d.get('approval_id', '')} [your version]</code> — rewrite + publish\n"
            f"❌ <code>SKIP {d.get('approval_id', '')}</code> — drop this post"
        )

    # ── Morning brief ─────────────────────────────────────────
    def _format_brief(self, d: dict) -> str:
        day = datetime.now().strftime("%A, %B %d")
        lines = [
            f"☀️ <b>GOOD MORNING, JUSTIN</b>\n<i>{day}</i>\n",
            f"{DIVIDER}\n",
        ]
        if d.get("yesterday"):
            lines.append(f"📊 <b>Yesterday's Highlights</b>\n{d['yesterday']}\n")
        if d.get("news"):
            news_items = "\n".join([f"  ▸ {n}" for n in d["news"]])
            lines.append(f"🌍 <b>Market Intel</b>\n{news_items}\n")
        if d.get("priorities"):
            pri_items = "\n".join([f"  {i+1}. {p}" for i, p in enumerate(d["priorities"])])
            lines.append(f"🎯 <b>Today's Top 3</b>\n{pri_items}\n")
        if d.get("opportunity"):
            lines.append(f"💡 <b>Opportunity</b>\n{d['opportunity']}\n")
        if d.get("product_spotlight"):
            lines.append(f"📈 <b>Product Watch</b>\n{d['product_spotlight']}\n")
        lines.append(f"{DIVIDER}\n<i>Akili is running. You focus on what only you can do.</i>")
        return "\n".join(lines)

    # ── Campaign ──────────────────────────────────────────────
    def _format_campaign(self, d: dict) -> str:
        return (
            f"🚀 <b>{d.get('title', 'CAMPAIGN')}</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>What we're launching:</b> {d.get('what', '')}\n"
            f"<b>Target:</b> {d.get('target', '')}\n"
            f"<b>Timeline:</b> {d.get('timeline', '')}\n\n"
            f"<b>Phase 1 — {d.get('phase1_label','Pre-launch')}</b>\n{d.get('phase1', '')}\n\n"
            f"<b>Phase 2 — {d.get('phase2_label','Launch')}</b>\n{d.get('phase2', '')}\n\n"
            f"<b>Phase 3 — {d.get('phase3_label','Sustain')}</b>\n{d.get('phase3', '')}\n\n"
            f"{DIVIDER}\n"
            f"🎯 <b>KPIs:</b>\n{d.get('kpis', '')}\n\n"
            f"⚡ <b>First action:</b> {d.get('first_action', 'Start now')}"
        )

    # ── Research result ───────────────────────────────────────
    def _format_research(self, d: dict) -> str:
        finding_lines = "\n".join([f"  {i+1}. {f}" for i, f in enumerate(d.get("findings", []))])
        source_lines  = " · ".join([f"[{s}]" for s in d.get("sources", [])[:4]])
        return (
            f"<b>Query:</b> <i>{d.get('query', '')}</i>\n"
            f"<b>Searched:</b> {d.get('source_count', '?')} sources\n\n"
            f"{DIVIDER}\n"
            f"📌 <b>Key Findings</b>\n{finding_lines}\n\n"
            f"💡 <b>CREOVA Angle</b>\n{d.get('creova_angle', '')}\n\n"
            f"⚡ <b>Recommended Action</b>\n{d.get('action', '')}\n\n"
            f"{DIVIDER}\n"
            f"<i>Confidence: {d.get('confidence', 'Medium')} | Sources: {source_lines}</i>"
        )

    # ── Reply draft ───────────────────────────────────────────
    def _format_reply_draft(self, d: dict) -> str:
        return (
            f"<b>From:</b> {d.get('from', 'Unknown')}\n"
            f"<b>Channel:</b> {d.get('channel', 'Email')}\n"
            f"<b>Type:</b> <i>{d.get('type', 'General')}</i> | <b>Priority:</b> {d.get('priority', '5')}/10\n\n"
            f"{DIVIDER}\n"
            f"📩 <b>Their message:</b>\n<i>{str(d.get('their_message', ''))[:200]}</i>\n\n"
            f"✍️ <b>My draft reply:</b>\n{d.get('draft', '')}\n"
            f"{DIVIDER}\n\n"
            f"Reply <code>SENDDRAFT</code> to send · <code>EDITDRAFT [changes]</code> to modify\n"
            f"Or <code>SKIP</code> to handle manually"
        )

    # ── Status ────────────────────────────────────────────────
    def _format_status(self, d: dict) -> str:
        agent_lines = "\n".join([
            f"  {'✅' if v == 'active' else '⚠️'} <b>{k}:</b> {v}"
            for k, v in d.get("agents", {}).items()
        ])
        platform_lines = "\n".join([
            f"  {'🟢' if v else '🔴'} {k}"
            for k, v in d.get("platforms", {}).items()
        ])
        return (
            f"<b>System:</b> AKILI OS — Phase 5\n"
            f"<b>Uptime:</b> {d.get('uptime', 'Running')}\n\n"
            f"{DIVIDER}\n"
            f"<b>Agents:</b>\n{agent_lines}\n\n"
            f"<b>Platforms:</b>\n{platform_lines}\n\n"
            f"{DIVIDER}\n"
            f"<b>Pending approvals:</b> {d.get('pending', 0)}\n"
            f"<b>Emails handled today:</b> {d.get('emails_today', 0)}\n"
            f"<b>Posts sent today:</b> {d.get('posts_today', 0)}\n"
            f"<b>Next heartbeat:</b> {d.get('next_heartbeat', '30 min')}"
        )

    # ── Error ─────────────────────────────────────────────────
    def _format_error(self, d: dict) -> str:
        return (
            f"⚠️ <b>Error Detected</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>Agent:</b> {d.get('agent', 'Unknown')}\n"
            f"<b>What failed:</b> {d.get('what', 'Unknown error')}\n"
            f"<b>Error:</b> <code>{str(d.get('error', ''))[:200]}</code>\n\n"
            f"<b>Auto-recovery:</b> {d.get('recovery', 'Logging and retrying in 30 min')}\n"
            f"<b>Do you need to act?</b> {d.get('justin_action', 'No — monitoring')}\n"
            f"{DIVIDER}\n"
            f"<i>Logged at {datetime.now().strftime('%H:%M')} · Full log in Replit console</i>"
        )

    # ── Milestone ─────────────────────────────────────────────
    def _format_milestone(self, d: dict) -> str:
        return (
            f"🎉 <b>MILESTONE HIT!</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>{d.get('what', '')}</b>\n\n"
            f"<i>{d.get('context', '')}</i>\n\n"
            f"📱 <b>Celebration posts ready:</b>\n{d.get('posts_preview', '')}\n\n"
            f"{DIVIDER}\n"
            f"Reply <code>CELEBRATE</code> to post across all accounts now"
        )

    # ── Weekly plan ───────────────────────────────────────────
    def _format_weekly_plan(self, d: dict) -> str:
        header = (
            f"🗓 <b>WEEK AHEAD — {d.get('week_range', '')}</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>Accounts covered:</b> 10 social accounts\n"
            f"<b>Posts planned:</b> {d.get('total_posts', 0)}\n"
            f"<b>Campaigns active:</b> {d.get('campaigns', 0)}\n\n"
        )
        day_previews = []
        for day_data in d.get("days", [])[:3]:
            day_previews.append(
                f"<b>{day_data.get('day')}</b> — <i>{day_data.get('theme')}</i>\n"
                f"  📸 IG: {str(day_data.get('ig_preview', ''))[:80]}...\n"
                f"  🐦 X: {str(day_data.get('twitter_preview', ''))[:60]}..."
            )
        return (
            header
            + "\n\n".join(day_previews)
            + f"\n\n{DIVIDER}\n<i>Full week queued. Posts sent for approval at scheduled times.</i>"
        )

    # ── Generic fallback ──────────────────────────────────────
    def _format_generic(self, d: dict) -> str:
        content = d.get("content", d.get("text", str(d)))
        return f"{DIVIDER}\n{content}\n{DIVIDER}"

    # ── AI-enhanced formatting ────────────────────────────────
    async def ai_enhance(self, raw_text: str, agent: str, context: str = "") -> str:
        """
        Pass any raw agent output through Claude to make it
        more creative, clearer, and better structured.
        Uses HTML tags (consistent with parse_mode='HTML').
        """
        if not self.client:
            return raw_text

        prompt = f"""You are formatting a response from the {agent} agent of AKILI — Justin Mafie's AI OS.

Raw output to format:
{raw_text}

Context: {context}

Rules:
1. Use Telegram HTML tags: <b>bold</b>, <i>italic</i>, <code>code</code>
2. Structure with clear sections using headers
3. Use relevant emojis (not excessive — 1-2 per section max)
4. Keep CREOVA brand voice — visionary, authentic, African excellence
5. Use the divider ━━━━━━━━━━━━━━━━━━━━ between major sections
6. End with a clear action item or next step
7. Max 3800 chars (Telegram limit)
8. Make it feel premium — this is a founder's personal AI, not a chatbot
9. IMPORTANT: Only use <b>, <i>, <code>, <pre> HTML tags — no markdown syntax like *bold* or _italic_

Return ONLY the formatted text. No explanation."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            log.error(f"[Formatter] AI enhancement error: {e}")
            return raw_text


# Global formatter instance — import this in agents
formatter = TelegramFormatter()
