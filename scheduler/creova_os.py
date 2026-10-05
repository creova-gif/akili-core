# ============================================================
# CREOVA OS SCHEDULER — Weekly Automation Engine
# Fires all CREOVA Media automations on schedule, alongside the
# existing PulseScheduler / ReachAutoResponder / IntelLiveBrief.
#
# Schedule (Eastern Time):
# - Monday 8:15 AM: invoice chaser + capacity monitor + compliance check
# - Tuesday 9:00 AM: outreach batch (10 targets)
# - Friday 9:00 AM: content calendar build for next week
# - Friday 9:30 AM: caption + hashtag batch
# - Last Friday of month, 10:00 AM: newsletter draft
# - 1st of month, 9:00 AM: monthly financial close
# ============================================================

import asyncio
import calendar
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from core.ai_client import get_client
from config.ai_models import MODEL

ET = ZoneInfo("America/Toronto")
log = logging.getLogger("CREOVA.OS")

JUSTIN_CHAT_ID = os.environ.get("JUSTIN_CHAT_ID", "")


class CREOVAOSScheduler:
    def __init__(self, telegram_app, memory, creova_media_agent, pulse_agent, reach_agent):
        self.app    = telegram_app
        self.memory = memory
        self.cm     = creova_media_agent   # CREOVA_MEDIA agent
        self.pulse  = pulse_agent          # PULSE agent
        self.reach  = reach_agent          # REACH agent
        self.shield_client = get_client(os.environ.get("ANTHROPIC_API_KEY", ""), "SHIELD")
        self.reach_client  = get_client(os.environ.get("ANTHROPIC_API_KEY", ""), "REACH")
        self.pulse_client  = get_client(os.environ.get("ANTHROPIC_API_KEY", ""), "PULSE")
        log.info("CREOVA OS Scheduler initialized")

    async def run(self):
        while True:
            try:
                await self._check_schedule()
            except Exception as e:
                log.error(f"[CREOVA.OS] Schedule check error: {e}")
            await asyncio.sleep(60)

    async def _check_schedule(self):
        now    = datetime.now(ET)
        day    = now.strftime("%A")
        hour   = now.hour
        minute = now.minute
        dom    = now.day

        if day == "Monday" and hour == 8 and minute == 15:
            await self._monday_ops_brief()

        if day == "Tuesday" and hour == 9 and minute == 0:
            await self._tuesday_outreach()

        if day == "Friday" and hour == 9 and minute == 0:
            await self._friday_content_build()

        if day == "Friday" and hour == 9 and minute == 30:
            await self._friday_caption_batch()

        if dom == 1 and hour == 9 and minute == 0:
            await self._monthly_close()

        last_friday = max(
            d for d in range(1, calendar.monthrange(now.year, now.month)[1] + 1)
            if datetime(now.year, now.month, d, tzinfo=ET).strftime("%A") == "Friday"
        )
        if dom == last_friday and day == "Friday" and hour == 10 and minute == 0:
            await self._monthly_newsletter()

    async def _send(self, text: str):
        if self.app and JUSTIN_CHAT_ID:
            await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=text)

    async def _monday_ops_brief(self):
        """Monday 8:15 AM — invoice chaser + capacity + compliance."""
        log.info("[CREOVA.OS] Monday ops brief firing")
        await self._send(await self.cm.run_invoice_chaser())
        await asyncio.sleep(5)
        await self._send(await self.cm.run_capacity_check())
        await asyncio.sleep(5)
        await self._compliance_check()
        await self.memory.daily_log("[CREOVA.OS] Monday ops brief ran")

    async def _tuesday_outreach(self):
        """Tuesday 9:00 AM — 10 outreach DMs drafted."""
        log.info("[CREOVA.OS] Tuesday outreach batch firing")
        prompt = """Draft this week's outreach batch for CREOVA Media.
Generate 10 personalized DM drafts targeting:
- 4 x university student organizations (BIPOC clubs at Ontario universities)
- 3 x BIPOC business owners who need photography or social content
- 2 x event organizers (cultural events in GTHA)
- 1 x potential SEEN creator (Black Canadian or francophone storyteller)

Each DM: under 80 words, peer-to-peer, references something specific,
one clear CTA. Label each: [IG DM] or [LinkedIn]."""
        try:
            response = await self.reach_client.messages.create(
                model=MODEL, max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            await self._send(f"📤 REACH — Tuesday Outreach Batch\n\n{response.content[0].text}")
        except Exception as e:
            log.error(f"[CREOVA.OS] Outreach batch error: {e}")
        await self.memory.daily_log("[CREOVA.OS] Tuesday outreach batch ran")

    async def _friday_content_build(self):
        """Friday 9:00 AM — full next-week content calendar."""
        log.info("[CREOVA.OS] Friday content calendar firing")
        now = datetime.now(ET)
        prompt = f"""Build the CREOVA content calendar for next week (week starting {now.strftime('%B %d, %Y')}).

Weekly theme rotation:
- Mon: Music Monday (CREOVA Music / Sankofa Studio)
- Tue: Tech Tuesday (CREOVA Solutions / SEEN)
- Wed: Wisdom Wednesday (founder lessons, BIPOC business tips)
- Thu: Cultural Thursday (East African roots, diaspora life in Canada)
- Fri: Showcase Friday (client work, behind-the-scenes)

Produce:
- 3 Instagram posts with concepts + captions (bilingual: English + Swahili)
- 2 TikTok video concepts with hooks
- 2 LinkedIn posts (founder perspective)
- Best posting times for each
- Which content pillar each hits

Accounts: @creativeinnovation__ @jj_mafie @creovasolutions @sankofastudio__"""
        try:
            response = await self.pulse_client.messages.create(
                model=MODEL, max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            await self._send(f"📅 PULSE — Next Week Content Calendar\n\n{response.content[0].text}")
        except Exception as e:
            log.error(f"[CREOVA.OS] Content calendar error: {e}")
        await self.memory.daily_log("[CREOVA.OS] Friday content calendar ran")

    async def _friday_caption_batch(self):
        """Friday 9:30 AM — caption + hashtag sets."""
        log.info("[CREOVA.OS] Friday caption batch firing")
        prompt = """Generate a caption + hashtag batch for this week's CREOVA content.

For each of the 3 Instagram posts from the calendar just sent:
1. Write 3 caption options (storytelling / punchy one-liner / cultural hook)
2. Generate 20 hashtags: 5 BIPOC/cultural + 5 Ontario/Canada + 5 photo/creative + 5 community
3. Flag best caption for reach vs engagement
4. Best posting time

All ready to paste directly into Later/Buffer."""
        try:
            response = await self.pulse_client.messages.create(
                model=MODEL, max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            await self._send(f"✍️ PULSE — Caption + Hashtag Batch\n\n{response.content[0].text}")
        except Exception as e:
            log.error(f"[CREOVA.OS] Caption batch error: {e}")
        await self.memory.daily_log("[CREOVA.OS] Friday caption batch ran")

    async def _monthly_close(self):
        """1st of month — financial close."""
        log.info("[CREOVA.OS] Monthly financial close firing")
        now = datetime.now(ET)
        prev_month = now.strftime("%B %Y")
        wave_data = self.cm._read_wave_export()
        prompt = f"""Run the CREOVA monthly financial close for {prev_month}.

Wave data: {wave_data[:500]}

Produce:
1. Revenue by stream: photography/video, brand shoots, social media, other
2. Expenses by category: software, equipment, marketing, professional fees
3. Net income
4. Outstanding invoices (list each + days overdue)
5. Revenue vs $50K annual target — on pace?
6. Plain-English P&L summary (4 sentences)
7. Accountant packet checklist

Flag: uncategorized expenses, invoices 30+ days overdue, unusual transactions."""
        try:
            response = await self.shield_client.messages.create(
                model=MODEL, max_tokens=1200,
                messages=[{"role": "user", "content": prompt}]
            )
            await self._send(f"💰 SHIELD — Monthly Financial Close\n\n{response.content[0].text}")
        except Exception as e:
            log.error(f"[CREOVA.OS] Monthly close error: {e}")
        await self.memory.daily_log("[CREOVA.OS] Monthly financial close ran")

    async def _monthly_newsletter(self):
        """Last Friday of month — newsletter draft."""
        log.info("[CREOVA.OS] Monthly newsletter firing")
        now = datetime.now(ET)
        prompt = f"""Draft the CREOVA monthly newsletter for {now.strftime('%B %Y')}.

Sections:
1. Client spotlight — [Justin will fill in best project this month]
2. SEEN platform update — [current status + what's coming]
3. BIPOC founder tip — one specific insight for our community
4. Service promotion — [seasonal offer — Justin will specify]
5. CTA: Book discovery call via Calendly

Format:
- 3 subject line options (one cultural hook, one founder story, one benefit-led)
- Preview text (80 chars max)
- Newsletter body under 400 words
- Tone: Justin writing to his community, not a brand newsletter

Output ready to paste into Mailchimp."""
        try:
            response = await self.reach_client.messages.create(
                model=MODEL, max_tokens=1200,
                messages=[{"role": "user", "content": prompt}]
            )
            await self._send(f"📨 REACH — Monthly Newsletter Draft\n\n{response.content[0].text}")
        except Exception as e:
            log.error(f"[CREOVA.OS] Newsletter error: {e}")
        await self.memory.daily_log("[CREOVA.OS] Monthly newsletter ran")

    async def _compliance_check(self):
        """Grant + compliance deadline check — fires Monday, part of the ops brief."""
        prompt = """Run the CREOVA compliance and grant deadline check.

Track these 2026 deadlines:
- CMF Convergent Stream: June 2026 application target
- CREOVA Inc federal incorporation: Q2 2026
- NRC IRAP: apply after incorporation
- BDC Black Entrepreneur Program: ongoing
- Ontario Creates: check current cycle

For anything due in the next 30 days:
1. What needs to be done
2. What professionals to contact (lawyer/accountant)
3. What documents to gather

Flag the CMF countdown: days until June 2026 target.
Format as a quick Monday checklist."""
        try:
            response = await self.shield_client.messages.create(
                model=MODEL, max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            await self._send(f"📋 SHIELD — Compliance + Grant Tracker\n\n{response.content[0].text}")
        except Exception as e:
            log.error(f"[CREOVA.OS] Compliance check error: {e}")
