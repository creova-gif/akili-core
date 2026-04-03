# ============================================================
# SNAPCHAT INTEGRATION — Akili PULSE Agent
# Account: jay-mafie
# Goal: Build toward Snapchat Creator program
# ============================================================

import os
import logging
import aiohttp
import asyncio
from datetime import datetime
from config.accounts import SNAPCHAT_ACCOUNT

log = logging.getLogger("PULSE.Snapchat")

# Snapchat Marketing API
BASE_URL = "https://adsapi.snapchat.com/v1"
AUTH_URL = "https://accounts.snapchat.com/login/oauth2/access_token"

# ── Snapchat Creator Program Requirements ────────────────────
# To qualify for Snapchat Creator program:
# ✅ 50+ subscribers
# ✅ Consistent daily posting (Stories + Spotlight)
# ✅ High view retention
# ✅ Authentic engagement
# ✅ 28-day posting streak recommended

CREATOR_PROGRAM_TARGETS = {
    "subscribers_needed": 50,
    "daily_posting_streak": 28,
    "min_story_views": 100,
    "spotlight_submissions_per_week": 3,
}

# Content pillars for jay-mafie on Snapchat
SNAP_CONTENT_PILLARS = {
    "studio": {
        "description": "Sankofa Studio sessions — raw, unfiltered",
        "frequency": "3x/week",
        "hook": "Behind the beats 🎙️",
    },
    "founder": {
        "description": "Founder day-in-life — office, meetings, builds",
        "frequency": "2x/week",
        "hook": "Building CREOVA from the inside 🔥",
    },
    "music": {
        "description": "Unreleased music previews, studio snippets",
        "frequency": "2x/week",
        "hook": "Exclusive on Snap first 🎵",
    },
    "tech": {
        "description": "Product builds, GoPay, Kaya, team moments",
        "frequency": "1x/week",
        "hook": "The tech side of CREOVA 💡",
    },
    "personal": {
        "description": "Lifestyle, travel, Halton Hills → Tanzania moments",
        "frequency": "Daily",
        "hook": "Real life. No filter.",
    },
}


class SnapchatClient:
    """
    Snapchat integration for jay-mafie.
    
    NOTE: Snapchat's public API (Marketing API) is designed for ads.
    For organic Story posting, Snapchat requires their Snap Kit SDK
    or manual posting. This client handles:
    1. Content planning and scheduling (AI-generated concepts)
    2. Spotlight submission tracking
    3. Creator program progress monitoring
    4. Analytics via Snapchat Insights (when available)
    
    For actual posting: Snapchat does NOT have a full organic posting API
    like Instagram/Twitter. Akili will generate content concepts + captions
    and remind Justin via Telegram with the content ready to post.
    This is standard for all social tools — Snapchat's organic API is limited.
    """

    def __init__(self):
        self.account = SNAPCHAT_ACCOUNT
        self.handle = "jay-mafie"
        log.info(f"Snapchat: {self.handle} — Creator program mode")

    async def generate_daily_content(self) -> dict:
        """
        Generate today's Snapchat content plan.
        Returns ready-to-use content Akili sends to Justin via Telegram.
        """
        day = datetime.now().strftime("%A").lower()
        hour = datetime.now().hour

        # Pick content pillar based on day
        day_pillar_map = {
            "monday":    "music",
            "tuesday":   "tech",
            "wednesday": "founder",
            "thursday":  "studio",
            "friday":    "music",
            "saturday":  "studio",
            "sunday":    "personal",
        }
        pillar_key = day_pillar_map.get(day, "personal")
        pillar = SNAP_CONTENT_PILLARS[pillar_key]

        content_plan = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "handle": f"@{self.handle}",
            "pillar": pillar_key,
            "stories": [
                {
                    "slot": "Morning (10AM)",
                    "concept": f"{pillar['hook']} — {pillar['description']}",
                    "caption": self._build_caption(pillar_key, "morning"),
                    "type": "Story",
                },
                {
                    "slot": "Afternoon (2PM)",
                    "concept": "Check-in / behind scenes moment",
                    "caption": self._build_caption("personal", "afternoon"),
                    "type": "Story",
                },
                {
                    "slot": "Evening (8PM)",
                    "concept": "Day wrap / CREOVA update",
                    "caption": self._build_caption(pillar_key, "evening"),
                    "type": "Story",
                },
            ],
            "spotlight": {
                "concept": f"30-second clip: {pillar['description']}",
                "caption": f"#{pillar_key.capitalize()} | @creovasolutions | creova.one",
                "submit": day in ["tuesday", "thursday", "saturday"],
            },
        }
        return content_plan

    def _build_caption(self, pillar: str, time_of_day: str) -> str:
        captions = {
            "studio_morning":    "Early in the studio 🎙️ @sankofastudio__ — new music coming",
            "studio_evening":    "Long session but worth it 🔥 @creativeinnovation__",
            "music_morning":     "Can't stop listening to this 🎵 @creativeinnovation__",
            "music_evening":     "This one's almost ready 👀 @creativeinnovation__",
            "founder_morning":   "Building day 💻 @creovasolutions — creova.one",
            "founder_evening":   "Shipped something today. CREOVA growing 🌍",
            "tech_morning":      "GoPay. Kaya. MentalPath. One team. @creovasolutions",
            "tech_evening":      "The tech stack is live. More soon 💡 creova.one",
            "personal_morning":  "Another day. Another opportunity. Let's go 🌅",
            "personal_afternoon":"Taking a break but the mind never stops 🧠 #CREOVA",
            "personal_evening":  "Real life is the content 🎬 @jj_mafie",
        }
        key = f"{pillar}_{time_of_day}"
        return captions.get(key, f"Building CREOVA from the ground up 🌍 — @jj_mafie | creova.one")

    def format_telegram_reminder(self, content_plan: dict) -> str:
        """Format content plan as Telegram message for Justin."""
        lines = [
            f"👻 SNAPCHAT CONTENT — {content_plan['date']}",
            f"Handle: {content_plan['handle']}",
            f"Today's pillar: {content_plan['pillar'].upper()}",
            "",
            "📱 STORIES TO POST:",
        ]
        for story in content_plan["stories"]:
            lines.append(f"\n⏰ {story['slot']}")
            lines.append(f"   Concept: {story['concept']}")
            lines.append(f"   Caption: {story['caption']}")

        if content_plan["spotlight"]["submit"]:
            lines.append("\n🌟 SPOTLIGHT SUBMISSION TODAY:")
            lines.append(f"   Concept: {content_plan['spotlight']['concept']}")
            lines.append(f"   Caption: {content_plan['spotlight']['caption']}")

        lines.append(f"\n📊 Creator Program Progress:")
        lines.append(f"   Keep posting daily to maintain streak!")
        return "\n".join(lines)

    def creator_program_checklist(self) -> str:
        """Weekly checklist for Snapchat Creator program progress."""
        return (
            "👻 SNAPCHAT CREATOR CHECKLIST\n"
            f"Handle: {self.handle}\n\n"
            "This week:\n"
            "  □ Post Stories daily (min 1/day)\n"
            "  □ Submit 3 Spotlight videos\n"
            "  □ Reply to all Snap replies\n"
            "  □ Use trending sounds where relevant\n"
            "  □ Mention @jj_mafie and creova.one\n\n"
            "Creator Program Targets:\n"
            f"  → {CREATOR_PROGRAM_TARGETS['subscribers_needed']}+ subscribers\n"
            f"  → {CREATOR_PROGRAM_TARGETS['daily_posting_streak']}-day posting streak\n"
            f"  → {CREATOR_PROGRAM_TARGETS['min_story_views']}+ Story views avg\n"
            f"  → {CREATOR_PROGRAM_TARGETS['spotlight_submissions_per_week']}x Spotlight/week"
        )

    async def format_status(self) -> str:
        return (
            f"👻 SNAPCHAT STATUS\n"
            f"  ✅ {self.handle} — content planning active\n"
            f"  📌 Goal: Snapchat Creator program\n"
            f"  💡 Note: Organic posting API limited — content sent via Telegram reminders"
        )
