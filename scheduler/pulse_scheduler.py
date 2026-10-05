# ============================================================
# PULSE SCHEDULER — Phase 3A
# Auto-generates content on schedule, sends to Telegram for approval
# POST / EDIT / SKIP approval flow via Telegram
# ============================================================

import asyncio
import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from core.ai_client import get_client
from core.outcome_tracker import tracker as outcome_tracker
from config.ai_models import MODEL

ET = ZoneInfo("America/Toronto")   # EDT in summer, EST in winter — auto-adjusts


def _et_now() -> datetime:
    """Current time in Eastern Time (handles DST automatically)."""
    return datetime.now(ET)

log = logging.getLogger("PULSE.Scheduler")

ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
JUSTIN_CHAT_ID = os.environ.get("JUSTIN_CHAT_ID", "")

WEEKLY_THEMES = {
    "Monday":    {"theme": "Music Monday",      "focus": "new music, studio sessions, CREOVA Music energy"},
    "Tuesday":   {"theme": "Tech Tuesday",      "focus": "CREOVA Solutions builds, African tech innovation"},
    "Wednesday": {"theme": "Wisdom Wednesday",  "focus": "founder lessons, branding tips, creative advice"},
    "Thursday":  {"theme": "Throwback Thursday","focus": "journey, growth story, past projects"},
    "Friday":    {"theme": "Fresh Friday",      "focus": "new drops, upcoming projects, hype announcements"},
    "Saturday":  {"theme": "Studio Saturday",   "focus": "Sankofa Studio production, creative process"},
    "Sunday":    {"theme": "Founder Sunday",    "focus": "Justin Mafie vision, CREOVA roadmap, reflection"},
}

# All hours are EASTERN TIME (America/Toronto)
# EDT in summer (UTC-4) · EST in winter (UTC-5) — auto-adjusted via zoneinfo
# Best times for Canada + East Africa audiences
POST_SCHEDULE = {
    "instagram": [9, 12, 18, 21],   # 9am, noon, 6pm, 9pm ET
    "twitter":   [8, 11, 17, 21],   # 8am, 11am, 5pm, 9pm ET
    "linkedin":  [8, 12, 17],       # 8am, noon, 5pm ET
    "tiktok":    [9, 14, 20],       # 9am, 2pm, 8pm ET
    "facebook":  [9, 18],           # 9am, 6pm ET
}

PLATFORM_ACCOUNTS = {
    "instagram": ["@jj_mafie", "@creovasolutions", "@creativeinnovation__", "@sankofastudio__"],
    "twitter":   ["@justin_mafie"],
    "linkedin":  ["Justin Mafie", "CREOVA"],
    "tiktok":    ["@creovamusic"],
    "facebook":  ["Justin Mafie", "CREOVA"],
}

BRAND_VOICE = """You are writing content for Justin Mafie — founder, musician, CEO of CREOVA.
VOICE: Authentic. Visionary. African excellence. Creative-tech founder. Real. Never corporate. Never generic.
MANDATORY: Every post mentions at least one of: @creativeinnovation__, @creovasolutions, @sankofastudio__, @jj_mafie, or creova.one
HASHTAG SETS:
Music: #CREOVAMusic #JustinMafie #AfricanMusic #SankofaStudio #NewMusic
Tech:  #CREOVA #CREOVASolutions #AfricanTech #EmergingMarkets #Founder
Personal: #JustinMafie #CREOVA #FounderLife #AfricanFounder #CreativeTech"""

PLATFORM_RULES = {
    "instagram": "Instagram post: engaging caption 150-220 chars, 8-12 hashtags, strong opening line, emoji where natural.",
    "twitter":   "Twitter/X: punchy tweet max 260 chars OR 4-tweet thread. Max 3 hashtags.",
    "linkedin":  "LinkedIn: professional 150-300 words. Thought leadership. 3-5 hashtags.",
    "tiktok":    "TikTok caption: short 80-120 chars, trend-aware, with video concept in [brackets].",
    "facebook":  "Facebook: conversational, community feel, 100-200 chars, link to creova.one.",
}


class PulseScheduler:
    def __init__(self, telegram_app, integrations=None):
        self.app          = telegram_app
        self.integrations = integrations
        self.client       = get_client(ANTHROPIC_KEY, "PULSE")
        self.pending      = {}
        log.info("PULSE Scheduler initialized")

    async def run(self):
        while True:
            now    = _et_now()          # Eastern Time — auto EDT/EST
            hour   = now.hour
            minute = now.minute
            day    = now.strftime("%A")

            if minute == 0:
                for platform, hours in POST_SCHEDULE.items():
                    if hour in hours:
                        await self._trigger_post(platform, day, hour)

            await asyncio.sleep(60)

    async def _trigger_post(self, platform: str, day: str, hour: int):
        theme_data = WEEKLY_THEMES.get(day, {"theme": "CREOVA", "focus": "brand story"})
        log.info(f"[Scheduler] Generating {platform} post — {day} {hour}:00")
        try:
            content     = await self._generate_content(platform, theme_data, day)
            approval_id = f"{platform}_{day}_{hour}"
            self.pending[approval_id] = {
                "platform": platform,
                "content":  content,
                "day":      day,
                "hour":     hour,
                "accounts": PLATFORM_ACCOUNTS.get(platform, []),
            }
            await self._request_approval(approval_id, platform, content, theme_data["theme"])
        except Exception as e:
            log.error(f"[Scheduler] Error generating {platform} post: {e}")

    async def _generate_content(self, platform: str, theme_data: dict, day: str) -> dict:
        prompt = f"""Today is {day}. Theme: {theme_data['theme']}. Focus: {theme_data['focus']}.
Platform: {platform}. Rule: {PLATFORM_RULES.get(platform, '')}

Write the post. Return ONLY valid JSON (no markdown):
{{"caption": "post text ready to copy-paste", "hashtags": ["tag1", "tag2"], "notes": "image/video suggestion"}}"""

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=600,
                system=BRAND_VOICE,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            log.error(f"[PULSE Scheduler] AI generation error: {e}")
            raise e

    async def _request_approval(self, approval_id: str, platform: str, content: dict, theme: str):
        caption  = content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", []))
        notes    = content.get("notes", "")
        accounts = PLATFORM_ACCOUNTS.get(platform, [])

        PLATFORM_EMOJI = {
            "instagram": "📸", "twitter": "🐦", "linkedin": "💼",
            "tiktok": "🎵", "facebook": "👤"
        }
        emoji = PLATFORM_EMOJI.get(platform, "📡")

        msg = (
            f"📡 <b>PULSE — POST APPROVAL</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{emoji} <b>{platform.upper()}</b>  ·  {theme}\n"
            f"Accounts: <code>{', '.join(accounts)}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{caption}\n\n"
            f"<i>{hashtags}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📸 <i>{notes}</i>\n\n"
            f"▸ ✅ <code>POST {approval_id}</code>\n"
            f"▸ ✏️ <code>EDIT {approval_id} [your text]</code>\n"
            f"▸ ❌ <code>SKIP {approval_id}</code>"
        )
        await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=msg, parse_mode="HTML")
        log.info(f"[Scheduler] Approval request sent: {approval_id}")

    async def handle_approval(self, text: str) -> str | None:
        text = text.strip()

        if text.upper().startswith("POST "):
            approval_id = text.split(" ", 1)[1].strip()
            if approval_id in self.pending:
                post = self.pending.pop(approval_id)
                action_id = await self._execute_post(post)
                if not action_id:
                    return f"⚠️ Failed to post to {post['platform'].upper()} — see error above."
                return f"✅ Posted to {post['platform'].upper()} — {', '.join(post['accounts'])} · tracking as {action_id}"
            return f"⚠️ No pending post: {approval_id}"

        elif text.upper().startswith("SKIP "):
            approval_id = text.split(" ", 1)[1].strip()
            if approval_id in self.pending:
                self.pending.pop(approval_id)
                return f"⏭ Skipped: {approval_id}"
            return f"⚠️ No pending post: {approval_id}"

        elif text.upper().startswith("EDIT "):
            parts = text.split(" ", 2)
            if len(parts) >= 3:
                approval_id  = parts[1]
                new_caption  = parts[2]
                if approval_id in self.pending:
                    self.pending[approval_id]["content"]["caption"] = new_caption
                    post = self.pending.pop(approval_id)
                    action_id = await self._execute_post(post)
                    if not action_id:
                        return f"⚠️ Failed to post to {post['platform'].upper()} — see error above."
                    return f"✏️ Edited + posted to {post['platform'].upper()} · tracking as {action_id}"
            return "⚠️ Edit format: EDIT [id] [new caption]"

        return None

    async def _execute_post(self, post: dict) -> str | None:
        """Publish (or hand off) the post, then log it as a sensed action.
        Returns the outcome_tracker action_id, or None if publishing failed —
        every branch here is a real-world action, so every branch gets logged.
        """
        platform = post["platform"]
        content  = post["content"]
        caption  = content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", []))
        full_text = f"{caption}\n\n{hashtags}".strip()
        accounts  = post.get("accounts", [])

        log.info(f"[Scheduler] Executing {platform} post")
        action_id = None
        try:
            if platform == "twitter" and self.integrations:
                await self.integrations.twitter.post_tweet(full_text[:280])
                action_id = await outcome_tracker.log_action(
                    "PULSE", f"{platform}_post", summary=caption[:80],
                    metadata={"platform": platform, "accounts": accounts,
                              "mode": "auto_published", "full_text": full_text[:500]},
                )

            elif platform == "linkedin" and self.integrations:
                await self.integrations.linkedin.post_text(full_text)
                action_id = await outcome_tracker.log_action(
                    "PULSE", f"{platform}_post", summary=caption[:80],
                    metadata={"platform": platform, "accounts": accounts,
                              "mode": "auto_published", "full_text": full_text[:500]},
                )

            elif platform in ("instagram", "tiktok", "facebook"):
                action_id = await outcome_tracker.log_action(
                    "PULSE", f"{platform}_post", summary=caption[:80],
                    metadata={"platform": platform, "accounts": accounts,
                              "mode": "manual_handoff", "full_text": full_text[:500]},
                )
                await self.app.bot.send_message(
                    chat_id=JUSTIN_CHAT_ID,
                    text=(
                        f"📸 {platform.upper()} approved!\n\n"
                        f"Caption:\n{full_text}\n\n"
                        f"Post manually or reply: POSTMEDIA {platform} [image_url]\n\n"
                        f"📎 Tracking as <code>{action_id}</code> — report results later with:\n"
                        f"<code>outcome {action_id} likes=.. reach=..</code>"
                    ),
                    parse_mode="HTML",
                )
            log.info(f"[Scheduler] ✅ {platform} complete (action {action_id})")
        except Exception as e:
            log.error(f"[Scheduler] Post error: {e}")
            await self.app.bot.send_message(
                chat_id=JUSTIN_CHAT_ID,
                text=f"⚠️ PULSE: Failed to post to {platform}: {e}"
            )
        return action_id

    def list_pending(self) -> str:
        if not self.pending:
            return "📡 PULSE — No posts pending approval right now."
        lines = ["📡 PULSE — Pending Approvals\n━━━━━━━━━━━━━━━━━━━━\n"]
        for aid, post in self.pending.items():
            preview = post["content"].get("caption", "")[:55]
            platform = post["platform"].upper()
            lines.append(f"▸ {platform}  ·  <code>{aid}</code>\n  {preview}...\n")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("Reply POST/EDIT/SKIP [id] to action each one.")
        return "\n".join(lines)
