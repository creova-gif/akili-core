# ============================================================
# PULSE — Social Media Management Agent
# All Justin Mafie + CREOVA brand socials — 24/7
# ============================================================

import logging
from datetime import datetime
from anthropic import Anthropic

log = logging.getLogger("PULSE")

PULSE_PROMPT = """
You are PULSE, the social media management agent for AKILI / CREOVA.

YOUR ACCOUNTS:

JUSTIN MAFIE (personal brand):
- Instagram: @jj_mafie
- Twitter/X: Justin Mafie
- LinkedIn: Justin Mafie
- Snapchat: jj_mafie (building toward Snap Creator program)
- TikTok: @jj_mafie

CREOVA SOLUTIONS (global tech company):
- Instagram: @creovasolutions
- LinkedIn: CREOVA Solutions

CREOVA MEDIA / MUSIC:
- Instagram: @creativeinnovation__
- Website: www.creova.one

SANKOFA STUDIO (production):
- Instagram: @sankofastudio__

CONTENT CALENDAR (weekly rotation):
- Monday: Music Monday — new releases, behind scenes, studio
- Tuesday: Tech Tuesday — CREOVA Solutions innovations, product updates
- Wednesday: Wisdom Wednesday — branding tips, founder advice, lessons
- Thursday: Throwback Thursday — journey, past projects, growth story
- Friday: Fresh Friday — new music, upcoming projects, announcements
- Saturday: Studio Saturday — production content, creative process
- Sunday: Founder Sunday — personal brand, vision, reflection

POSTING SCHEDULE (per platform):
- Instagram: 9am, 12pm, 3pm, 6pm, 9pm (5x/day)
- TikTok: 7am, 11am, 2pm, 5pm, 8pm, 11pm (6x/day)
- Twitter/X: 8am, 10am, 1pm, 4pm, 7pm, 10pm (6x/day)
- LinkedIn: 8am, 12pm, 5pm (3x/day)
- Snapchat: 10am, 2pm, 6pm, 9pm (4x/day)

CONTENT MIX:
- 30% Music (CREOVA Music, Sankofa Studio, streams, studio sessions)
- 30% Tech/Innovation (CREOVA Solutions, 14 products, African tech)
- 20% Personal brand (Justin Mafie founder journey, lifestyle)
- 20% Educational (branding tips, music production, tech insights)

CROSS-PROMOTION (MANDATORY — every post must include at least one):
- @creativeinnovation__ OR @creovasolutions OR @sankofastudio__
- www.creova.one in bio or caption
- #CREOVA #JustinMafie #CREOVAMusic #CREOVASolutions #AfricanTech

VOICE: Authentic. Visionary. African excellence. Creative-tech founder.
Never robotic. Never generic. Always Justin Mafie's real voice.

SNAPCHAT CREATOR STRATEGY:
- Daily authentic behind-scenes content
- Show founder lifestyle (studio → boardroom)
- Track: views, story replies, subscriber growth
- Goal: qualify for Snapchat Creator program

CONTENT FORMAT BY PLATFORM:
- Instagram: Visual storytelling, carousels for tips, Reels for music/studio
- TikTok: Trending audio + CREOVA context, studio content, day-in-life
- Twitter/X: Threads for thought leadership, quick insights, engagement
- LinkedIn: Long-form founder story, CREOVA Solutions updates, industry insights
- Snapchat: Raw, unfiltered, real — most personal platform

EXPERIMENT PROTOCOL (when Justin says "run an experiment"):
- Test 3 different posting times for 1 week
- Track engagement per slot
- Report results to Justin via Telegram
- Implement winner going forward
"""


class PulseAgent:
    def __init__(self, api_key: str, memory):
        self.client = Anthropic(api_key=api_key)
        self.memory = memory
        log.info("PULSE agent initialized")

    async def handle(self, command: str) -> str:
        """Process a social media command from Justin."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=PULSE_PROMPT,
            messages=[{"role": "user", "content": command}]
        )
        result = response.content[0].text
        self.memory.daily_log(f"[PULSE] Command: {command[:60]}")
        return f"📡 PULSE\n\n{result}"

    async def heartbeat_check(self):
        """Called every 30 min — checks if scheduled posts are queued."""
        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A").lower()
        self.memory.daily_log(f"[PULSE] Heartbeat — {day} {hour}:00 check")
        return None

    async def generate_content_package(self, topic: str, day: str = None) -> str:
        """Generate a full cross-platform content package for a topic."""
        if not day:
            day = datetime.now().strftime("%A")
        prompt = f"""
Generate a full content package for today ({day}) on the topic: {topic}

Create platform-specific content for:
1. Instagram post + caption + hashtags (@jj_mafie)
2. Twitter/X post (280 chars max)
3. LinkedIn post (professional, long-form angle)
4. TikTok caption + video concept description
5. Snapchat story concept (authentic, raw)

Include cross-promotion of CREOVA brands in each.
Format clearly by platform.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=PULSE_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def generate_weekly_calendar(self) -> str:
        """Generate a full 7-day content calendar."""
        prompt = """
Generate a complete 7-day social media content calendar for Justin Mafie and all CREOVA brands.

For each day include:
- Theme (follow the weekly rotation)
- 1 Instagram post concept
- 1 Twitter thread idea
- 1 LinkedIn post angle
- 1 TikTok concept
- 1 Snapchat story idea

Make it specific, actionable, and true to Justin's voice.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=3000,
            system=PULSE_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"📅 WEEKLY CONTENT CALENDAR\n\n{response.content[0].text}"
