# ============================================================
# INTEL LIVE BRIEF — Phase 3D
# Real web search feeds into the 8AM morning brief
# Uses Anthropic web search tool for live data
# ============================================================

import asyncio
import logging
import os
from datetime import datetime
from anthropic import Anthropic

log = logging.getLogger("INTEL.LiveBrief")

ANTHROPIC_KEY  = os.environ["ANTHROPIC_API_KEY"]
JUSTIN_CHAT_ID = os.environ["JUSTIN_CHAT_ID"]

# Topics INTEL always monitors
SEARCH_TOPICS = [
    "African tech startups funding 2026",
    "East Africa fintech news",
    "Tanzania Kenya technology",
    "CREOVA competitors branding agency Canada",
    "Spotify African music streaming trends",
    "Canadian startup ecosystem news",
    "GoPay Tanzania mobile money",
]

VC_WATCH_LIST = [
    "Partech Africa",
    "TLcom Capital",
    "Novastar Ventures",
    "Timon Capital",
    "Y Combinator Africa",
    "500 Global emerging markets",
]


class IntelLiveBrief:
    """
    Generates the 8AM daily brief using LIVE web search.
    Searches real news → synthesizes → sends to Justin via Telegram.
    """

    def __init__(self, telegram_app, memory):
        self.app    = telegram_app
        self.memory = memory
        self.client = Anthropic(api_key=ANTHROPIC_KEY)
        log.info("INTEL LiveBrief initialized — web search enabled")

    # ── Main loop: send brief at 8AM daily ───────────────────
    async def run(self):
        while True:
            now = datetime.now()
            if now.hour == 8 and now.minute == 0:
                log.info("[INTEL] Generating live morning brief...")
                brief = await self.generate_live_brief()
                await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=brief)
                self.memory.daily_log(f"[INTEL] Morning brief sent at 08:00")
            await asyncio.sleep(60)

    # ── Generate live brief with web search ──────────────────
    async def generate_live_brief(self) -> str:
        today = datetime.now().strftime("%A, %B %d, %Y")
        yesterday_log = self.memory.get_yesterday_log()

        prompt = f"""
Today is {today}. Generate Justin Mafie's morning brief.

Search for and include:
1. Latest African tech / East Africa news (last 24 hours)
2. Any news about mobile money or fintech in Tanzania or Kenya
3. Canadian startup or tech news relevant to a founder
4. Any music streaming or African music industry news
5. Check if any of these VCs have made recent moves: {', '.join(VC_WATCH_LIST[:3])}

Yesterday's activity summary:
{yesterday_log[:500] if yesterday_log else 'First day — no history yet'}

Format the brief EXACTLY like this:

☀️ AKILI MORNING BRIEF — {today}

📊 YESTERDAY:
[2-3 lines on what Akili did yesterday based on logs]

🌍 MARKET INTEL:
[3 bullet points of real news you found — cite source]

🎯 TODAY'S PRIORITIES:
[Top 3 specific things Justin should focus on today]

💡 OPPORTUNITY:
[One specific actionable opportunity from the news]

📈 PRODUCT SPOTLIGHT:
[One CREOVA product + one competitive insight about it]

Keep it tight. Under 400 words total. Actionable, not fluffy.
"""

        try:
            # Use Anthropic web search tool for live data
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                }],
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract text from response (may include tool use blocks)
            brief_text = ""
            for block in response.content:
                if block.type == "text":
                    brief_text += block.text

            if not brief_text:
                brief_text = await self._fallback_brief(today, yesterday_log)

            return brief_text

        except Exception as e:
            log.error(f"[INTEL] Live brief error: {e}")
            return await self._fallback_brief(today, yesterday_log)

    # ── Fallback brief (no web search available) ──────────────
    async def _fallback_brief(self, today: str, yesterday_log: str) -> str:
        prompt = f"""
Generate a morning brief for Justin Mafie — founder of CREOVA.
Date: {today}
Yesterday log: {yesterday_log[:300] if yesterday_log else 'N/A'}

Include:
- 3 priorities for today (focused on CREOVA products + content)
- 1 GoPay VC pitch update or suggestion
- 1 music promotion action item
- Motivational close in Justin's voice

Format with the ☀️ AKILI MORNING BRIEF header.
Under 300 words. Real and actionable.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    # ── On-demand research ────────────────────────────────────
    async def live_research(self, query: str) -> str:
        """Justin asks: research [topic] — INTEL searches and reports."""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1500,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                }],
                messages=[{
                    "role": "user",
                    "content": f"""
Research this for Justin Mafie / CREOVA: {query}

Provide:
1. Key findings (3-5 bullet points with sources)
2. What this means for CREOVA specifically
3. One actionable recommendation

Keep it concise and tactical. Justin is a busy founder.
"""
                }]
            )

            result = ""
            for block in response.content:
                if block.type == "text":
                    result += block.text

            return f"🔍 INTEL RESEARCH\n\n{result}"

        except Exception as e:
            log.error(f"[INTEL] Live research error: {e}")
            return f"🔍 INTEL: Search failed — {str(e)}\nTry again or check API limits."

    # ── VC tracker with live data ─────────────────────────────
    async def live_vc_tracker(self) -> str:
        """Live VC intelligence for GoPay pitch."""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1200,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                }],
                messages=[{
                    "role": "user",
                    "content": f"""
Search for the latest news and investments from these VCs:
{chr(10).join(f'- {vc}' for vc in VC_WATCH_LIST)}

For GoPay Tanzania pitch — I need:
1. Which of these VCs have recently invested in East Africa fintech?
2. Their typical check size and stage
3. Any portfolio companies I can reference as comparables
4. Best angle to pitch each one RIGHT NOW (what they care about in 2026)

Format as a tactical outreach guide — not an essay.
"""
                }]
            )

            result = ""
            for block in response.content:
                if block.type == "text":
                    result += block.text

            return f"💰 GOPAY VC TRACKER (LIVE)\n\n{result}"

        except Exception as e:
            log.error(f"[INTEL] VC tracker error: {e}")
            return f"💰 VC Tracker: Search unavailable — {str(e)}"

    # ── Competitor monitor ────────────────────────────────────
    async def competitor_monitor(self, product: str) -> str:
        """Search for competitor news for a specific CREOVA product."""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=800,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                }],
                messages=[{
                    "role": "user",
                    "content": f"""
Search for competitor news and market updates for: {product}

Find:
1. Who are the top 3 competitors right now?
2. Any recent funding, launches, or moves by competitors?
3. Market gaps CREOVA can exploit?
4. One specific differentiator Justin should highlight?

Be specific and current. Sources matter.
"""
                }]
            )

            result = ""
            for block in response.content:
                if block.type == "text":
                    result += block.text

            return f"🕵️ COMPETITOR INTEL — {product}\n\n{result}"

        except Exception as e:
            return f"🕵️ Competitor monitor error: {str(e)}"
