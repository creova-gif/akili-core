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
from anthropic import Anthropic

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

POST_SCHEDULE = {
    "instagram": [9, 12, 18, 21],
    "twitter":   [8, 12, 17, 21],
    "linkedin":  [8, 12, 17],
    "tiktok":    [9, 14, 20],
    "facebook":  [9, 18],
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
        self.client       = Anthropic(api_key=ANTHROPIC_KEY)
        self.pending      = {}
        log.info("PULSE Scheduler initialized")

    async def run(self):
        while True:
            now    = datetime.now()
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

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            system=BRAND_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    async def _request_approval(self, approval_id: str, platform: str, content: dict, theme: str):
        caption  = content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", []))
        notes    = content.get("notes", "")
        accounts = PLATFORM_ACCOUNTS.get(platform, [])

        msg = (
            f"📡 PULSE — Post ready for approval\n\n"
            f"Platform: {platform.upper()}\n"
            f"Theme: {theme}\n"
            f"Accounts: {', '.join(accounts)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{caption}\n\n{hashtags}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📸 Visual: {notes}\n\n"
            f"Reply:\n"
            f"✅ POST {approval_id}\n"
            f"✏️ EDIT {approval_id} [your changes]\n"
            f"❌ SKIP {approval_id}"
        )
        await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=msg)
        log.info(f"[Scheduler] Approval request sent: {approval_id}")

    async def handle_approval(self, text: str) -> str | None:
        text = text.strip()

        if text.upper().startswith("POST "):
            approval_id = text.split(" ", 1)[1].strip()
            if approval_id in self.pending:
                post = self.pending.pop(approval_id)
                await self._execute_post(post)
                return f"✅ Posted to {post['platform'].upper()} — {', '.join(post['accounts'])}"
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
                    await self._execute_post(post)
                    return f"✏️ Edited + posted to {post['platform'].upper()}"
            return "⚠️ Edit format: EDIT [id] [new caption]"

        return None

    async def _execute_post(self, post: dict):
        platform = post["platform"]
        content  = post["content"]
        caption  = content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", []))
        full_text = f"{caption}\n\n{hashtags}".strip()

        log.info(f"[Scheduler] Executing {platform} post")
        try:
            if platform == "twitter" and self.integrations:
                await self.integrations.twitter.post_tweet(full_text[:280])

            elif platform == "linkedin" and self.integrations:
                await self.integrations.linkedin.post_text(full_text)

            elif platform in ("instagram", "tiktok", "facebook"):
                await self.app.bot.send_message(
                    chat_id=JUSTIN_CHAT_ID,
                    text=(
                        f"📸 {platform.upper()} approved!\n\n"
                        f"Caption:\n{full_text}\n\n"
                        f"Post manually or reply: POSTMEDIA {platform} [image_url]"
                    )
                )
            log.info(f"[Scheduler] ✅ {platform} complete")
        except Exception as e:
            log.error(f"[Scheduler] Post error: {e}")
            await self.app.bot.send_message(
                chat_id=JUSTIN_CHAT_ID,
                text=f"⚠️ PULSE: Failed to post to {platform}: {e}"
            )

    def list_pending(self) -> str:
        if not self.pending:
            return "📡 PULSE: No posts pending approval."
        lines = ["📡 PULSE — Pending approvals:\n"]
        for aid, post in self.pending.items():
            preview = post["content"].get("caption", "")[:60]
            lines.append(f"• {aid}: {preview}...")
        return "\n".join(lines)
