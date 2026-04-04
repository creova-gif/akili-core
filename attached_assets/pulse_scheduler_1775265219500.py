# ============================================================
# PULSE SCHEDULER — Phase 3A
# Akili auto-generates + posts content on schedule
# Every post gets Telegram approval from Justin first
# ============================================================

import asyncio
import logging
import os
from datetime import datetime
from anthropic import Anthropic

log = logging.getLogger("PULSE.Scheduler")

ANTHROPIC_KEY  = os.environ["ANTHROPIC_API_KEY"]
JUSTIN_CHAT_ID = os.environ["JUSTIN_CHAT_ID"]

# ── Weekly content DNA ────────────────────────────────────────
WEEKLY_THEMES = {
    "Monday":    {"theme": "Music Monday",     "focus": "new music, studio sessions, CREOVA Music energy"},
    "Tuesday":   {"theme": "Tech Tuesday",     "focus": "CREOVA Solutions builds, African tech innovation"},
    "Wednesday": {"theme": "Wisdom Wednesday", "focus": "founder lessons, branding tips, creative advice"},
    "Thursday":  {"theme": "Throwback Thursday","focus": "journey, growth story, past projects"},
    "Friday":    {"theme": "Fresh Friday",     "focus": "new drops, upcoming projects, hype announcements"},
    "Saturday":  {"theme": "Studio Saturday",  "focus": "Sankofa Studio production, creative process"},
    "Sunday":    {"theme": "Founder Sunday",   "focus": "Justin Mafie vision, CREOVA roadmap, reflection"},
}

# ── Post schedule (hours in 24h) per platform ─────────────────
POST_SCHEDULE = {
    "instagram": [9, 12, 18, 21],
    "twitter":   [8, 12, 17, 21],
    "linkedin":  [8, 12, 17],
    "tiktok":    [9, 14, 20],
    "facebook":  [9, 18],
}

# ── Account routing per platform ──────────────────────────────
PLATFORM_ACCOUNTS = {
    "instagram": ["jj_mafie", "creovasolutions", "creativeinnovation", "sankofastudio"],
    "twitter":   ["justin_mafie"],
    "linkedin":  ["justin", "creova"],
    "tiktok":    ["creovamusic"],
    "facebook":  ["justin", "creova"],
}

# ── Justin's brand voice ──────────────────────────────────────
BRAND_VOICE = """
You are writing content for Justin Mafie — founder, musician, and CEO of CREOVA.

VOICE: Authentic. Visionary. African excellence. Creative-tech founder.
Real. Never corporate. Never generic. Always Justin's actual energy.

VENTURES TO CROSS-PROMOTE:
- @creativeinnovation__ (CREOVA Music)
- @jj_mafie (Justin personal)
- @sankofastudio__ (Sankofa Studio)
- @creovasolutions (CREOVA Solutions)
- @justin_mafie (Twitter/X)
- @creovamusic (TikTok)
- creova.one (always link here)

MANDATORY: Every post mentions at least one CREOVA handle or creova.one.

HASHTAG SETS:
Music: #CREOVAMusic #JustinMafie #AfricanMusic #SankofaStudio #NewMusic
Tech:  #CREOVA #CREOVASolutions #AfricanTech #EmergingMarkets #Founder
Personal: #JustinMafie #CREOVA #FounderLife #AfricanFounder #CreativeTech
"""


class PulseScheduler:
    """
    Runs continuously alongside main.py.
    Every hour it checks if a post is due.
    If yes: generates content → sends to Justin for approval → posts on confirm.
    """

    def __init__(self, telegram_app, integrations):
        self.app          = telegram_app
        self.integrations = integrations
        self.client       = Anthropic(api_key=ANTHROPIC_KEY)
        self.pending      = {}   # approval_id → post data waiting for Justin
        log.info("PULSE Scheduler initialized")

    # ── Main loop ─────────────────────────────────────────────
    async def run(self):
        """Check every 5 minutes if any post is due."""
        while True:
            now     = datetime.now()
            hour    = now.hour
            minute  = now.minute
            day     = now.strftime("%A")

            # Only act on the :00 of each scheduled hour
            if minute == 0:
                for platform, hours in POST_SCHEDULE.items():
                    if hour in hours:
                        await self._trigger_post(platform, day, hour)

            await asyncio.sleep(60)   # check every minute

    # ── Trigger a post ────────────────────────────────────────
    async def _trigger_post(self, platform: str, day: str, hour: int):
        theme_data = WEEKLY_THEMES.get(day, {"theme": "CREOVA", "focus": "brand story"})
        log.info(f"[Scheduler] Generating {platform} post — {day} {hour}:00")

        try:
            content = await self._generate_content(platform, theme_data, day)
            approval_id = f"{platform}_{day}_{hour}"

            # Store pending post
            self.pending[approval_id] = {
                "platform":  platform,
                "content":   content,
                "day":       day,
                "hour":      hour,
                "accounts":  PLATFORM_ACCOUNTS.get(platform, []),
            }

            # Send to Justin for approval
            await self._request_approval(approval_id, platform, content, theme_data["theme"])

        except Exception as e:
            log.error(f"[Scheduler] Error generating {platform} post: {e}")

    # ── Generate content ──────────────────────────────────────
    async def _generate_content(self, platform: str, theme_data: dict, day: str) -> dict:
        """Generate platform-specific content using Claude."""

        platform_rules = {
            "instagram": "Instagram post: engaging caption 150-220 chars, 8-12 hashtags, strong opening line, emoji where natural.",
            "twitter":   "Twitter/X: punchy tweet max 260 chars OR a 4-tweet thread. No hashtag spam — max 3.",
            "linkedin":  "LinkedIn: professional long-form 150-300 words. Thought leadership angle. 3-5 hashtags only.",
            "tiktok":    "TikTok caption: short 80-120 chars, trend-aware, with video concept description in [brackets].",
            "facebook":  "Facebook post: conversational, community feel, 100-200 chars, link to creova.one.",
        }

        prompt = f"""
Today is {day}. Theme: {theme_data['theme']}.
Focus: {theme_data['focus']}.
Platform: {platform}
Rule: {platform_rules.get(platform, '')}

Write the post content. Return as JSON:
{{
  "caption": "the post text ready to copy-paste",
  "hashtags": ["tag1", "tag2"],
  "notes": "one line on what image/video to pair with this"
}}

Only JSON. No markdown. No preamble.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            system=BRAND_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        text = response.content[0].text.strip()
        # Strip any accidental markdown fences
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    # ── Request Telegram approval ─────────────────────────────
    async def _request_approval(self, approval_id: str, platform: str,
                                 content: dict, theme: str):
        caption   = content.get("caption", "")
        hashtags  = " ".join(content.get("hashtags", []))
        notes     = content.get("notes", "")
        accounts  = PLATFORM_ACCOUNTS.get(platform, [])

        msg = (
            f"📡 PULSE — Post ready for approval\n\n"
            f"Platform: {platform.upper()}\n"
            f"Theme: {theme}\n"
            f"Accounts: {', '.join(accounts)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{caption}\n\n"
            f"{hashtags}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📸 Visual note: {notes}\n\n"
            f"Reply:\n"
            f"✅ POST {approval_id}\n"
            f"✏️ EDIT {approval_id} [your changes]\n"
            f"❌ SKIP {approval_id}"
        )

        await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=msg)
        log.info(f"[Scheduler] Approval request sent for {approval_id}")

    # ── Handle Justin's approval reply ───────────────────────
    async def handle_approval(self, text: str) -> str:
        """
        Called by main.py when Justin replies with POST/EDIT/SKIP.
        Returns confirmation string.
        """
        text = text.strip()

        # POST approval
        if text.upper().startswith("POST "):
            approval_id = text.split(" ", 1)[1].strip()
            if approval_id in self.pending:
                post = self.pending.pop(approval_id)
                await self._execute_post(post)
                return f"✅ Posted to {post['platform'].upper()} — {', '.join(post['accounts'])}"
            return f"⚠️ No pending post found for ID: {approval_id}"

        # SKIP
        elif text.upper().startswith("SKIP "):
            approval_id = text.split(" ", 1)[1].strip()
            if approval_id in self.pending:
                self.pending.pop(approval_id)
                return f"⏭ Skipped post: {approval_id}"
            return f"⚠️ No pending post: {approval_id}"

        # EDIT
        elif text.upper().startswith("EDIT "):
            parts = text.split(" ", 2)
            if len(parts) >= 3:
                approval_id = parts[1]
                new_caption = parts[2]
                if approval_id in self.pending:
                    self.pending[approval_id]["content"]["caption"] = new_caption
                    post = self.pending.pop(approval_id)
                    await self._execute_post(post)
                    return f"✏️ Edited + posted to {post['platform'].upper()}"
            return "⚠️ Edit format: EDIT [approval_id] [your new caption]"

        return None   # Not an approval command

    # ── Execute the actual post ───────────────────────────────
    async def _execute_post(self, post: dict):
        platform = post["platform"]
        content  = post["content"]
        caption  = content.get("caption", "")
        hashtags = " ".join(content.get("hashtags", []))
        full_text = f"{caption}\n\n{hashtags}".strip()
        accounts  = post["accounts"]

        log.info(f"[Scheduler] Executing {platform} post to {accounts}")

        try:
            if platform == "twitter":
                await self.integrations.twitter.post_tweet(full_text[:280])

            elif platform == "linkedin":
                if "justin" in accounts:
                    await self.integrations.linkedin.post_text(full_text, account_key="justin")
                if "creova" in accounts:
                    await self.integrations.linkedin.post_text(full_text, account_key="creova")

            elif platform == "facebook":
                if "justin" in accounts:
                    await self.integrations.facebook.post_text(full_text, account_key="justin")
                if "creova" in accounts:
                    await self.integrations.facebook.post_text(full_text, account_key="creova")

            elif platform in ("instagram", "tiktok"):
                # These need a media URL — log for Justin to add image
                await self.app.bot.send_message(
                    chat_id=JUSTIN_CHAT_ID,
                    text=(
                        f"📸 {platform.upper()} post approved!\n\n"
                        f"Caption ready:\n{full_text}\n\n"
                        f"⚡ To post with image, reply:\n"
                        f"POSTMEDIA {platform} [image_url]\n\n"
                        f"Or post manually via the app using the caption above."
                    )
                )

            log.info(f"[Scheduler] ✅ {platform} post complete")

        except Exception as e:
            log.error(f"[Scheduler] Post execution error: {e}")
            await self.app.bot.send_message(
                chat_id=JUSTIN_CHAT_ID,
                text=f"⚠️ PULSE: Failed to post to {platform}: {str(e)}"
            )

    def list_pending(self) -> str:
        """Show Justin what's waiting for approval."""
        if not self.pending:
            return "📡 PULSE: No posts pending approval right now."
        lines = ["📡 PULSE — Pending approvals:\n"]
        for aid, post in self.pending.items():
            caption_preview = post["content"].get("caption", "")[:60]
            lines.append(f"• {aid}\n  {caption_preview}...\n  Reply: POST {aid} or SKIP {aid}\n")
        return "\n".join(lines)
