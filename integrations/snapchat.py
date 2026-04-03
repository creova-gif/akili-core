# ============================================================
# SNAPCHAT INTEGRATION — Akili PULSE Agent
# Account: jay-mafie | Goal: Snapchat Creator program
#
# Snapchat's organic posting API is not available for third-party
# apps — this is industry-wide. Strategy: AKILI generates rich
# content briefs, visual direction, and Spotlight scripts and
# delivers them to Justin's Telegram automatically every morning.
# Justin shoots and posts from his phone. AKILI handles strategy.
# ============================================================

import os
import json
import logging
from datetime import datetime, timedelta
from config.accounts import SNAPCHAT_ACCOUNT

log = logging.getLogger("PULSE.Snapchat")

STREAK_FILE = "akili-life/logs/snapchat_streak.json"

CREATOR_TARGETS = {
    "subscribers_needed":         50,
    "daily_posting_streak":       28,
    "min_story_views":           100,
    "spotlight_submissions_week":  3,
}

CONTENT_PILLARS = {
    "music": {
        "theme":       "Music Monday / Fresh Friday",
        "description": "Unreleased music previews, studio snippets, listening sessions",
        "hook":        "Exclusive on Snap first 🎵",
        "visual":      "Close-up of speakers / headphones / studio screen with waveform",
        "filter":      "Keep it raw — minimal filter. Maybe a warm tone.",
        "text_style":  "Bold white text, bottom third: caption + @creativeinnovation__",
        "duration":    "10–15 sec Story / 30 sec Spotlight",
        "audio":       "Your own unreleased track playing in background",
        "cta":         "Tap to listen 👆 | Full release @creativeinnovation__",
    },
    "studio": {
        "theme":       "Studio Sessions",
        "description": "Sankofa Studio process — recording, mixing, beat-making",
        "hook":        "Behind the beats 🎙️",
        "visual":      "Wide shot of studio booth OR overhead of mixing board",
        "filter":      "Slightly desaturated / moody — feels authentic",
        "text_style":  "Handwritten-style font: 'Day X in the studio'",
        "duration":    "10–20 sec — fast cuts work well",
        "audio":       "Ambient studio sound or beat playing softly",
        "cta":         "Book a session → @sankofastudio__ | creova.one",
    },
    "founder": {
        "theme":       "Founder Life",
        "description": "Day-in-life building CREOVA — meetings, code, decisions",
        "hook":        "Building CREOVA from the inside 🔥",
        "visual":      "Screen recordings of product + face cam reaction / desk setup",
        "filter":      "Bright, natural light — professional but real",
        "text_style":  "Clean sans-serif: 'Founder mode 💻 @creovasolutions'",
        "duration":    "15–30 sec — show don't tell",
        "audio":       "Lo-fi instrumental or your own music quietly",
        "cta":         "Follow the journey → @creovasolutions | creova.one",
    },
    "tech": {
        "theme":       "Tech Tuesday",
        "description": "CREOVA products — GoPay, Kaya, MentalPath, WazaWealth",
        "hook":        "The tech side of CREOVA 💡",
        "visual":      "Phone screen recording of the app / laptop with code",
        "filter":      "Cool blue tone — techy feel",
        "text_style":  "Bold text: Product name + '@creovasolutions'",
        "duration":    "15 sec — quick demo style",
        "audio":       "Upbeat track — feels like a product launch",
        "cta":         "Try it → creova.one",
    },
    "personal": {
        "theme":       "Real Life",
        "description": "Lifestyle moments — Halton Hills, Tanzania, travel, food, thoughts",
        "hook":        "Real life. No filter. 🌍",
        "visual":      "POV shots, selfie, street views — whatever is actually happening",
        "filter":      "No filter or subtle warmth — keep it real",
        "text_style":  "Casual: whatever comes to mind in the moment",
        "duration":    "Any length — this is the most natural",
        "audio":       "Ambient sound or trending audio",
        "cta":         "Follow @jj_mafie for the full journey",
    },
}

DAY_PILLAR = {
    "monday":    "music",
    "tuesday":   "tech",
    "wednesday": "founder",
    "thursday":  "studio",
    "friday":    "music",
    "saturday":  "studio",
    "sunday":    "personal",
}

SPOTLIGHT_SCRIPTS = {
    "music": (
        "0–3s:  Hook — play the most addictive part of the track loud\n"
        "3–10s: Show yourself nodding / vibing — make it feel real\n"
        "10–20s: Quick studio clip or listening party vibe\n"
        "20–28s: Text overlay: 'Full track dropping soon @creativeinnovation__'\n"
        "28–30s: End on the beat drop or big lyric moment"
    ),
    "studio": (
        "0–3s:  Wide shot walking into the studio — establish the vibe\n"
        "3–10s: Close-up of hands on keys or board\n"
        "10–20s: Play a snippet of what you're working on\n"
        "20–28s: Face cam reaction to playback — show the emotion\n"
        "28–30s: Text: 'Sankofa Studio 🎙️ @sankofastudio__'"
    ),
    "founder": (
        "0–3s:  Morning desk setup or laptop opening — 'Let's build'\n"
        "3–10s: Quick screen recording of CREOVA product or dashboard\n"
        "10–20s: Speak to camera: one sentence about what you shipped today\n"
        "20–28s: Text overlay: 'Building CREOVA for Africa + the world 🌍'\n"
        "28–30s: End on creova.one"
    ),
    "tech": (
        "0–3s:  App open on phone — logo reveal moment\n"
        "3–10s: Fast demo of the core feature\n"
        "10–20s: Text: problem → solution in 2 lines\n"
        "20–28s: 'Built by @creovasolutions | creova.one'\n"
        "28–30s: CTA: 'Check it out → link in bio'"
    ),
    "personal": (
        "0–3s:  Wherever you are right now — show it\n"
        "3–15s: One honest thought about the day / journey\n"
        "15–25s: Something visually interesting nearby\n"
        "25–30s: 'Follow @jj_mafie for the real journey 🌍'"
    ),
}


class SnapchatClient:
    """
    Snapchat strategy engine for jay-mafie.
    Delivers daily content briefs, weekly queues, Spotlight scripts,
    and streak tracking to Justin via Telegram.
    """

    def __init__(self):
        self.account = SNAPCHAT_ACCOUNT
        self.handle = "jay-mafie"
        os.makedirs("akili-life/logs", exist_ok=True)
        log.info(f"Snapchat: {self.handle} — Creator program mode (enhanced)")

    # ── Streak Tracking ───────────────────────────────────────

    def load_streak(self) -> dict:
        if os.path.exists(STREAK_FILE):
            try:
                with open(STREAK_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"streak": 0, "last_posted": None, "total_days": 0, "spotlight_this_week": 0}

    def save_streak(self, data: dict):
        with open(STREAK_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def mark_posted(self, include_spotlight: bool = False) -> str:
        data = self.load_streak()
        today = datetime.now().strftime("%Y-%m-%d")
        last = data.get("last_posted")

        if last == today:
            return f"👻 Already marked today ({today}) as posted. Streak: {data['streak']} days."

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last == yesterday:
            data["streak"] += 1
        elif last is None:
            data["streak"] = 1
        else:
            data["streak"] = 1

        data["last_posted"] = today
        data["total_days"] = data.get("total_days", 0) + 1
        if include_spotlight:
            data["spotlight_this_week"] = data.get("spotlight_this_week", 0) + 1

        self.save_streak(data)
        needed = CREATOR_TARGETS["daily_posting_streak"]
        remaining = max(0, needed - data["streak"])
        msg = f"✅ Day marked! Streak: {data['streak']} days"
        if remaining > 0:
            msg += f" ({remaining} more for Creator program)"
        else:
            msg += " — Creator program target reached! 🎉"
        return msg

    def get_streak_status(self) -> str:
        data = self.load_streak()
        streak = data.get("streak", 0)
        last = data.get("last_posted", "never")
        total = data.get("total_days", 0)
        spotlight = data.get("spotlight_this_week", 0)
        needed = CREATOR_TARGETS["daily_posting_streak"]
        pct = min(100, int((streak / needed) * 100))

        bar_filled = int(pct / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        lines = [
            f"👻 SNAPCHAT STREAK TRACKER",
            f"Handle: @{self.handle}",
            f"",
            f"🔥 Current streak: {streak} days",
            f"📅 Last posted:    {last}",
            f"📊 Total days:     {total}",
            f"🌟 Spotlight/week: {spotlight}/{CREATOR_TARGETS['spotlight_submissions_week']}",
            f"",
            f"Creator Program Progress:",
            f"[{bar}] {pct}%",
            f"Target: {needed}-day streak",
            f"",
        ]

        if streak == 0:
            lines.append("⚠️  No streak active — post today to start!")
        elif streak < 7:
            lines.append(f"Keep going! {needed - streak} more days to Creator program.")
        elif streak < 14:
            lines.append(f"Solid! One week down. {needed - streak} to go.")
        elif streak < 28:
            lines.append(f"Almost there — {needed - streak} days left. Don't break it now!")
        else:
            lines.append("🏆 Creator program target reached!")

        lines.append("\nTo log today's post: send 'snapchat posted'")
        lines.append("To log a Spotlight: send 'snapchat spotlight posted'")
        return "\n".join(lines)

    # ── Rich Daily Content ────────────────────────────────────

    async def generate_rich_daily_content(self, day_override: str = None) -> dict:
        day = day_override or datetime.now().strftime("%A").lower()
        pillar_key = DAY_PILLAR.get(day, "personal")
        pillar = CONTENT_PILLARS[pillar_key]
        is_spotlight_day = day in ["tuesday", "thursday", "saturday"]
        streak = self.load_streak()

        return {
            "date":        datetime.now().strftime("%Y-%m-%d"),
            "day":         day.capitalize(),
            "handle":      f"@{self.handle}",
            "pillar":      pillar_key,
            "theme":       pillar["theme"],
            "stories": [
                {
                    "slot":      "Morning (10AM)",
                    "hook":      pillar["hook"],
                    "concept":   pillar["description"],
                    "visual":    pillar["visual"],
                    "filter":    pillar["filter"],
                    "text":      pillar["text_style"],
                    "audio":     pillar["audio"],
                    "duration":  pillar["duration"],
                    "caption":   self._morning_caption(pillar_key),
                    "cta":       pillar["cta"],
                },
                {
                    "slot":      "Afternoon (2PM)",
                    "hook":      "Check-in moment 📍",
                    "concept":   "Wherever you are right now — make it interesting",
                    "visual":    "POV or surroundings — real and unplanned",
                    "filter":    "Whatever feels right in the moment",
                    "text":      "One honest line about the day so far",
                    "audio":     "Ambient sound works perfectly here",
                    "duration":  "5–10 sec — quick and real",
                    "caption":   "Taking a break but the mind never stops 🧠 #CREOVA",
                    "cta":       "Follow @jj_mafie",
                },
                {
                    "slot":      "Evening (8PM)",
                    "hook":      "Day wrap 🌙",
                    "concept":   "What got done today — CREOVA update or reflection",
                    "visual":    "Evening vibe — home, office, or wherever the day ends",
                    "filter":    "Warm, golden hour or low light",
                    "text":      "One win from today or what's coming tomorrow",
                    "audio":     "Your own music or calm lo-fi",
                    "duration":  "10–15 sec",
                    "caption":   self._evening_caption(pillar_key),
                    "cta":       "Tomorrow we go again 🔥 @creovasolutions | creova.one",
                },
            ],
            "spotlight": {
                "submit_today":  is_spotlight_day,
                "script":        SPOTLIGHT_SCRIPTS.get(pillar_key, SPOTLIGHT_SCRIPTS["personal"]),
                "caption":       f"{pillar['hook']} | @creovasolutions | creova.one | #{pillar_key.capitalize()}",
                "tips":          self._spotlight_tips(),
            },
            "cross_platform": self._cross_platform_repurpose(pillar_key),
            "streak":            streak,
        }

    def _morning_caption(self, pillar: str) -> str:
        captions = {
            "music":   "Can't stop listening to this 🎵 @creativeinnovation__",
            "studio":  "Early in the studio 🎙️ @sankofastudio__ — new music coming",
            "founder": "Building day 💻 @creovasolutions — creova.one",
            "tech":    "GoPay. Kaya. MentalPath. One team. @creovasolutions",
            "personal":"Another day. Another opportunity. Let's go 🌅",
        }
        return captions.get(pillar, "CREOVA. Always building 🌍")

    def _evening_caption(self, pillar: str) -> str:
        captions = {
            "music":   "This one's almost ready 👀 @creativeinnovation__",
            "studio":  "Long session but worth it 🔥 @sankofastudio__",
            "founder": "Shipped something today. CREOVA growing 🌍",
            "tech":    "The tech stack is live. More soon 💡 creova.one",
            "personal":"Real life is the content 🎬 @jj_mafie",
        }
        return captions.get(pillar, "Day done. CREOVA never stops 🌙")

    def _spotlight_tips(self) -> list:
        return [
            "Hook in the first 2 seconds — no slow intros",
            "Vertical 9:16 only — fills the whole screen",
            "Add text overlay so it works with sound off",
            "Use trending audio if it fits (boosts discovery)",
            "Submit between 6–9PM for best reach",
            "Don't repost the same clip as both Story and Spotlight",
        ]

    def _cross_platform_repurpose(self, pillar: str) -> dict:
        repurpose = {
            "music": {
                "tiktok":    "Post the same 30-sec clip to @creovamusic TikTok — different caption",
                "instagram": "Reel on @creativeinnovation__ — same video, branded caption",
                "twitter":   "Post the audio link + 'On Snap first 👀 @jay-mafie'",
            },
            "studio": {
                "tiktok":    "Studio process content performs well on TikTok — post immediately",
                "instagram": "Reel on @sankofastudio__ with full studio tour caption",
                "twitter":   "Behind the beats thread — link to Snap for full video",
            },
            "founder": {
                "tiktok":    "Founder day-in-life — post same clip to TikTok with #FounderLife",
                "instagram": "@jj_mafie or @creovasolutions Reel — add longer caption",
                "linkedin":  "Screenshot the key insight as a LinkedIn text post",
            },
            "tech": {
                "tiktok":    "App demo performs great on TikTok — post same clip",
                "instagram": "@creovasolutions Reel — add product description in caption",
                "linkedin":  "Share the product update as a LinkedIn post for B2B audience",
            },
            "personal": {
                "instagram": "Personal story or casual post on @jj_mafie",
                "twitter":   "Quote the moment in a tweet — link back to Snap",
            },
        }
        return repurpose.get(pillar, {})

    # ── Weekly Queue ──────────────────────────────────────────

    async def generate_weekly_queue(self) -> str:
        today = datetime.now()
        lines = [
            f"👻 SNAPCHAT WEEKLY QUEUE",
            f"Week of {today.strftime('%B %d, %Y')}",
            f"Handle: @{self.handle}",
            f"",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        today_name = today.strftime("%A").lower()
        today_idx = days.index(today_name) if today_name in days else 0

        for i, day in enumerate(days):
            pillar_key = DAY_PILLAR[day]
            pillar = CONTENT_PILLARS[pillar_key]
            is_spotlight = day in ["tuesday", "thursday", "saturday"]
            date = today + timedelta(days=(i - today_idx))

            marker = " ← TODAY" if i == today_idx else ""
            lines.append(f"\n📅 {day.capitalize()} {date.strftime('%b %d')}{marker}")
            lines.append(f"   Pillar: {pillar['theme']}")
            lines.append(f"   Hook: {pillar['hook']}")
            lines.append(f"   Visual: {pillar['visual']}")
            if is_spotlight:
                lines.append(f"   🌟 SPOTLIGHT DAY — 30-sec script ready")
            lines.append(f"   Caption: {self._morning_caption(pillar_key)}")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"\n🌟 Spotlight days: Tuesday, Thursday, Saturday")
        lines.append(f"📊 Creator targets: {CREATOR_TARGETS['spotlight_submissions_week']}x Spotlight/week · {CREATOR_TARGETS['daily_posting_streak']}-day streak")
        lines.append(f"\nSend 'snapchat [day]' for full brief on any day")
        lines.append("Send 'snapchat posted' after each day to track streak")
        return "\n".join(lines)

    # ── Telegram Formatting ───────────────────────────────────

    def format_rich_brief(self, plan: dict) -> str:
        p = plan
        streak_data = p.get("streak", {})
        streak_count = streak_data.get("streak", 0)

        lines = [
            f"👻 SNAPCHAT BRIEF — {p['day']} {p['date']}",
            f"Pillar: {p['theme'].upper()}",
            f"🔥 Streak: {streak_count} days",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        for story in p["stories"]:
            lines.append(f"\n⏰ {story['slot']}")
            lines.append(f"   Hook:    {story['hook']}")
            lines.append(f"   Shoot:   {story['visual']}")
            lines.append(f"   Filter:  {story['filter']}")
            lines.append(f"   Text:    {story['text']}")
            lines.append(f"   Audio:   {story['audio']}")
            lines.append(f"   Length:  {story['duration']}")
            lines.append(f"   Caption: {story['caption']}")
            lines.append(f"   CTA:     {story['cta']}")

        spot = p["spotlight"]
        if spot["submit_today"]:
            lines.append(f"\n🌟 SPOTLIGHT — SUBMIT TODAY")
            lines.append(f"   Script:")
            for line in spot["script"].split("\n"):
                lines.append(f"   {line}")
            lines.append(f"\n   Caption: {spot['caption']}")
            lines.append(f"\n   Tips:")
            for tip in spot["tips"][:3]:
                lines.append(f"   • {tip}")
        else:
            lines.append(f"\n⚪ No Spotlight today — next: Tue/Thu/Sat")

        if p.get("cross_platform"):
            lines.append(f"\n🔄 CROSS-POST THIS CONTENT:")
            for platform, instruction in p["cross_platform"].items():
                lines.append(f"   {platform.capitalize()}: {instruction}")

        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("✅ Done posting? Send 'snapchat posted' to log your streak")
        return "\n".join(lines)

    # ── Status ────────────────────────────────────────────────

    async def format_status(self) -> str:
        streak = self.load_streak()
        return (
            f"👻 SNAPCHAT STATUS\n"
            f"  ✅ @{self.handle} — strategy engine active\n"
            f"  🔥 Streak: {streak.get('streak', 0)} days\n"
            f"  📌 Goal: Snapchat Creator program ({CREATOR_TARGETS['daily_posting_streak']}-day streak)\n"
            f"  📬 Auto-brief: daily at 9AM via Telegram\n"
            f"  💡 Organic API limited — briefs + manual posting strategy"
        )
