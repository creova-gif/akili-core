# ============================================================
# SNAPCHAT INTEGRATION — Akili PULSE Agent
# Account: jay-mafie
# Goal: Build toward Snapchat Creator program
# ============================================================

import logging
from datetime import datetime
from config.accounts import SNAPCHAT_ACCOUNT

log = logging.getLogger("PULSE.Snapchat")

CREATOR_PROGRAM_TARGETS = {
    "subscribers_needed": 50,
    "daily_posting_streak": 28,
    "min_story_views": 100,
    "spotlight_submissions_per_week": 3,
}

SNAP_CONTENT_PILLARS = {
    "studio":   {"description": "Sankofa Studio sessions — raw, unfiltered", "frequency": "3x/week", "hook": "Behind the beats 🎙️"},
    "founder":  {"description": "Founder day-in-life — office, meetings, builds", "frequency": "2x/week", "hook": "Building CREOVA from the inside 🔥"},
    "music":    {"description": "Unreleased music previews, studio snippets", "frequency": "2x/week", "hook": "Exclusive on Snap first 🎵"},
    "tech":     {"description": "Product builds, GoPay, Kaya, team moments", "frequency": "1x/week", "hook": "The tech side of CREOVA 💡"},
    "personal": {"description": "Lifestyle, travel, Halton Hills → Tanzania moments", "frequency": "Daily", "hook": "Real life. No filter."},
}

DAY_PILLAR_MAP = {
    "monday": "music", "tuesday": "tech", "wednesday": "founder",
    "thursday": "studio", "friday": "music", "saturday": "studio", "sunday": "personal",
}

CAPTIONS = {
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


class SnapchatClient:
    """
    Snapchat integration for jay-mafie.

    Note: Snapchat's organic posting API is limited. This client generates
    daily content plans and sends them to Justin via Telegram. Justin posts
    manually from his phone. This is standard practice for all Snapchat tools.
    """

    def __init__(self):
        self.account = SNAPCHAT_ACCOUNT
        self.handle = "jay-mafie"
        log.info(f"Snapchat: {self.handle} — Creator program mode")

    async def generate_daily_content(self) -> dict:
        """Generate today's Snapchat content plan."""
        day = datetime.now().strftime("%A").lower()
        pillar_key = DAY_PILLAR_MAP.get(day, "personal")
        pillar = SNAP_CONTENT_PILLARS[pillar_key]

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "handle": f"@{self.handle}",
            "pillar": pillar_key,
            "stories": [
                {
                    "slot": "Morning (10AM)",
                    "concept": f"{pillar['hook']} — {pillar['description']}",
                    "caption": CAPTIONS.get(f"{pillar_key}_morning", "Building CREOVA 🌍 @jj_mafie"),
                    "type": "Story",
                },
                {
                    "slot": "Afternoon (2PM)",
                    "concept": "Check-in / behind scenes moment",
                    "caption": CAPTIONS.get("personal_afternoon", ""),
                    "type": "Story",
                },
                {
                    "slot": "Evening (8PM)",
                    "concept": "Day wrap / CREOVA update",
                    "caption": CAPTIONS.get(f"{pillar_key}_evening", ""),
                    "type": "Story",
                },
            ],
            "spotlight": {
                "concept": f"30-second clip: {pillar['description']}",
                "caption": f"#{pillar_key.capitalize()} | @creovasolutions | creova.one",
                "submit": day in ["tuesday", "thursday", "saturday"],
            },
        }

    def format_telegram_reminder(self, content_plan: dict) -> str:
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

        lines.append("\n📊 Creator Program: Keep posting daily to maintain streak!")
        return "\n".join(lines)

    def creator_program_checklist(self) -> str:
        return (
            f"👻 SNAPCHAT CREATOR CHECKLIST\n"
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
            f"  💡 Organic posting API limited — content plans sent via Telegram"
        )
