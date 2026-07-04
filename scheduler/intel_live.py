# ============================================================
# INTEL LIVE BRIEF — Phase 3D
# Real web search for 8AM morning brief + on-demand research
# Uses Anthropic web search tool for live data
# ============================================================

import asyncio
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from core.ai_client import get_client
from config.ai_models import MODEL

ET = ZoneInfo("America/Toronto")

log = logging.getLogger("INTEL.LiveBrief")

ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
JUSTIN_CHAT_ID = os.environ.get("JUSTIN_CHAT_ID", "")

VC_WATCH_LIST = [
    "Partech Africa",
    "TLcom Capital",
    "Novastar Ventures",
    "Timon Capital",
    "Y Combinator Africa",
    "500 Global emerging markets",
]


class IntelLiveBrief:
    def __init__(self, telegram_app, memory):
        self.app    = telegram_app
        self.memory = memory
        self.client = get_client(ANTHROPIC_KEY, "INTEL")
        log.info("INTEL LiveBrief initialized — web search enabled")

    async def run(self):
        while True:
            now = datetime.now(ET)       # Eastern Time — auto EDT/EST
            if now.hour == 8 and now.minute == 0:
                log.info("[INTEL] Generating live morning brief (8:00 ET)...")
                brief = await self.generate_live_brief()
                await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=brief)
                await self.memory.daily_log("[INTEL] Morning brief sent at 08:00 ET")
            await asyncio.sleep(60)

    async def generate_live_brief(self) -> str:
        today = datetime.now().strftime("%A, %B %d, %Y")
        yesterday_log = ""
        try:
            yesterday_log = self.memory.get_yesterday_log()
        except Exception:
            pass

        prompt = f"""Today is {today}. Generate Justin Mafie's morning brief.

Search for and include:
1. Latest African tech / East Africa news (last 24 hours)
2. Mobile money or fintech news in Tanzania or Kenya
3. Canadian startup/tech news relevant to a founder
4. Music streaming or African music industry news
5. Recent moves from: {', '.join(VC_WATCH_LIST[:3])}

Yesterday's activity:
{yesterday_log[:500] if yesterday_log else 'First day — no history yet'}

Format EXACTLY as:

☀️ AKILI MORNING BRIEF — {today}

📊 YESTERDAY:
[2-3 lines from logs]

🌍 MARKET INTEL:
[3 bullet points of real news — cite source]

🎯 TODAY'S PRIORITIES:
[Top 3 specific actions for Justin]

💡 OPPORTUNITY:
[One specific actionable opportunity from the news]

📈 PRODUCT SPOTLIGHT:
[One CREOVA product + one competitive insight]

Under 400 words total. Actionable, not fluffy."""

        return await self._search_and_respond(prompt, fallback_fn=self._fallback_brief)

    async def _fallback_brief(self) -> str:
        today = datetime.now().strftime("%A, %B %d, %Y")
        prompt = f"""Generate a morning brief for Justin Mafie — founder of CREOVA.
Date: {today}
Include: 3 priorities (CREOVA + content), 1 GoPay VC pitch tip, 1 music action item.
Format with ☀️ AKILI MORNING BRIEF header. Under 300 words. Real and actionable."""
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            log.error(f"[INTEL] Fallback brief error: {e}")
            return f"⚠️ INTEL: Brief generation failed: {e}"

    async def _search_and_respond(self, prompt: str, fallback_fn=None) -> str:
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1200,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": prompt}]
            )
            result = ""
            for block in response.content:
                if hasattr(block, "text"):
                    result += block.text
            if result.strip():
                return result
        except Exception as e:
            log.warning(f"[INTEL] Web search unavailable: {e}")

        if fallback_fn:
            return await fallback_fn()
        return "⚠️ INTEL: Search unavailable. Check Anthropic API limits."

    async def live_research(self, query: str) -> str:
        prompt = f"""Research this for Justin Mafie / CREOVA: {query}

Provide:
1. Key findings (3-5 bullet points with sources)
2. What this means for CREOVA specifically
3. One actionable recommendation

Concise and tactical. Justin is a busy founder."""

        result = await self._search_and_respond(prompt)
        return f"🔍 INTEL RESEARCH\n\n{result}"

    async def live_vc_tracker(self) -> str:
        prompt = f"""Search for the latest news from these VCs:
{chr(10).join(f'- {vc}' for vc in VC_WATCH_LIST)}

For GoPay Tanzania pitch, provide:
1. Which VCs recently invested in East Africa fintech?
2. Their typical check size and stage
3. Portfolio companies to reference as comparables
4. Best pitch angle for each RIGHT NOW (2026)

Format as a tactical outreach guide."""

        result = await self._search_and_respond(prompt)
        return f"💰 GOPAY VC TRACKER (LIVE)\n\n{result}"

    async def competitor_monitor(self, product: str) -> str:
        prompt = f"""Search for competitor news for: {product}

Find:
1. Top 3 competitors right now
2. Recent funding, launches, or moves by competitors
3. Market gaps CREOVA can exploit
4. One specific differentiator Justin should highlight

Be specific and current."""

        result = await self._search_and_respond(prompt)
        return f"🕵️ COMPETITOR INTEL — {product}\n\n{result}"
