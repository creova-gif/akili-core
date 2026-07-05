# ============================================================
# INTEL — Research & Lead Generation Agent
# Deep research, leads, daily briefs, VC tracking
# ============================================================

import logging
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from anthropic import AsyncAnthropic

log = logging.getLogger("INTEL")

TELEGRAM_FORMAT = """
━━━━━━━━━━━━━━━━━━━━
TELEGRAM FORMATTING (MANDATORY — apply to every response):
You are sending directly to Justin's phone. Format like this:

▸ Start with: [EMOJI] [AGENT] — [TOPIC] on its own line
▸ Use ━━━━━━━━━━━━━━━━━━━━ as section dividers
▸ Use ▸ for top-level bullets
▸ Use  ◦ for sub-bullets (indented 2 spaces)
▸ Use ① ② ③ ④ ⑤ for ordered steps or priorities
▸ Use 🟢 🟡 🔴 for status indicators
▸ Keep paragraphs to 2 sentences MAX — mobile screen
▸ End every response with a line starting ⚡ with the key action
▸ NEVER use markdown symbols (**, ##, __, ~~) — Unicode only
▸ Use emojis as section markers, not decoration
▸ Total response: under 350 words unless Justin asks for more
━━━━━━━━━━━━━━━━━━━━
"""

INTEL_PROMPT = """
You are INTEL, the research and intelligence agent for AKILI / CREOVA.

YOUR RESPONSIBILITIES:
1. Daily morning briefings (8AM to Justin via Telegram)
2. Deep market research for all 14 CREOVA products
3. Lead generation for CREOVA Solutions clients
4. VC and investor tracking (especially for GoPay)
5. Competitor monitoring
6. Trend identification (African tech, Canadian startups, music industry)

PRODUCTS TO RESEARCH FOR:
- GoPay Tanzania (fintech, Bank of Tanzania compliance, East Africa)
- Kaya (property management, Kenya/Ontario real estate)
- MentalPath (BIPOC mental health, Canadian regulated therapists)
- WazaWealth (investing, Africa + Canada)
- KilimoAI (agriculture, East Africa)
- GridOS (mini-grid, Tanzania energy)
- AIHealthSupport (health, Africa)
- BudgetEaseApp (SME finance, East Africa)
- SEEN (fashion, Africa futurism)
- Darsme, Mskniagara, QuickBookSample, HealthFitness, RecommendedPeptides

LEAD GENERATION TARGETS:
For CREOVA Solutions (creative agency + tech):
- BIPOC-owned businesses (Canada) needing branding
- African startups needing tech development
- Healthcare providers needing digital platforms
- NGOs and foundations in East Africa
- Canadian real estate companies

For Music (CREOVA Music / Sankofa Studio):
- Playlist curators (Spotify, Apple Music)
- Music sync licensing opportunities
- Brand partnerships for music
- Festival and event bookings

For GoPay specifically:
- VCs active in East Africa fintech (track: Partech, TLcom, Novastar, Timon Capital)
- Angel investors in Tanzania/Kenya
- Strategic partners (telecoms, banks)
- Government/regulatory contacts at Bank of Tanzania

DAILY BRIEF FORMAT (send every morning at 8AM):
☀️ AKILI MORNING BRIEF — [Date]

📊 YESTERDAY'S HIGHLIGHTS:
[Key metrics or activities from previous day]

🌍 MARKET INTEL:
[2-3 relevant news items: African tech, Canadian startups, music industry]

🎯 TODAY'S PRIORITIES:
[Top 3 things Justin should focus on today]

💡 OPPORTUNITY ALERT:
[Any leads, partnerships, or trends worth acting on]

📈 PRODUCT WATCH:
[One product spotlight with latest competitive intel]

RESEARCH DEPTH LEVELS:
- Quick scan: 5 min overview for Justin's morning brief
- Standard: Full competitive analysis for a product
- Deep dive: Investor-grade research for GoPay pitch

CMF INTELLIGENCE:
Track and brief Justin on:
- Canada Media Fund announcements, deadline changes, new streams
- Ontario Creates funding cycles
- Canadian streaming and digital media market developments
- BIPOC creator economy news in Canada
- Competing platforms to SEEN (CBC Gem, APTN+, any new audio platforms)
- Success stories from CMF-funded projects (for application evidence)

CMF APPLICATION SUPPORT:
When /cmf is routed to INTEL for research (supporting data, not the draft itself):
- Pull supporting data: market size, audience numbers, comparable platforms
- Find Canadian content statistics from CMF's own reports
- Identify letters-of-support targets (universities, cultural orgs, Archives Canada)

SUPPLY CHAIN CHECK:
When /supply [order list] is sent (CREOVA Fashion):
- Check status against typical supplier lead times
- Calculate FX impact (CAD vs supplier currency) on landed cost
- Flag anything at risk of missing a drop date
""" + TELEGRAM_FORMAT


class IntelAgent:
    def __init__(self, api_key: str, memory):
        self.client = AsyncAnthropic(api_key=api_key)
        self.memory = memory
        log.info("INTEL agent initialized")

    async def handle(self, command: str) -> str:
        """Process a research command from Justin."""
        try:
            if "scrape" in command.lower() or "analyze http" in command.lower():
                import re
                urls = re.findall(r'(https?://\S+)', command)
                if urls:
                    return await self.analyze_webpage(urls[0], command)
                    
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": command}]
            )
            result = response.content[0].text
        except Exception as e:
            log.error(f"[INTEL] Error generating response: {e}")
            result = f"⚠️ INTEL encountered an error: {e}"
        await self.memory.daily_log(f"[INTEL] Research: {command[:60]}")
        return f"🔍 INTEL\n\n{result}"

    async def daily_brief(self) -> str:
        """Generates the 8AM morning brief for Justin."""
        yesterday_log = self.memory.get_yesterday_log()
        prompt = f"""
Generate today's morning brief for Justin Mafie.
Date: {datetime.now().strftime('%A, %B %d, %Y')}
Yesterday's activity log: {yesterday_log}

Include all sections from the DAILY BRIEF FORMAT.
Be specific, actionable, and concise.
Prioritize GoPay VC pitch progress and active product builds.
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1500,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            log.error(f"[INTEL] Error generating daily brief: {e}")
            return f"⚠️ INTEL Error: {e}"

    async def research_product(self, product: str, depth: str = "standard") -> str:
        """Deep research on a specific CREOVA product market."""
        prompt = f"""
Conduct a {depth} research report on the market for: {product}

Include:
1. Market size and growth (Africa/Canada as relevant)
2. Top 3 competitors and their weaknesses
3. Target customer profile
4. Pricing benchmarks
5. Key distribution channels
6. Regulatory considerations
7. Partnership opportunities
8. Investor thesis (why this wins)

Format as a clear report Justin can use for pitch decks.
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"📊 {product.upper()} RESEARCH\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[INTEL] Error researching product: {e}")
            return f"⚠️ INTEL Error: {e}"

    async def generate_leads(self, venture: str, count: int = 10) -> str:
        """Generate leads for a specific CREOVA venture."""
        prompt = f"""
Generate {count} high-quality leads for {venture}.

For each lead provide:
- Company/Person name
- Why they're a fit for CREOVA
- Likely contact method
- Suggested outreach angle
- Priority level (High/Medium/Low)

Format as a numbered list, actionable and specific.
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"🎯 LEADS — {venture}\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[INTEL] Error generating leads: {e}")
            return f"⚠️ INTEL Error: {e}"

    async def vc_tracker(self) -> str:
        """Track VC landscape for GoPay pitch."""
        prompt = """
Provide an updated VC tracker for GoPay Tanzania pitch.

Include:
1. Top 5 VCs actively investing in East Africa fintech right now
2. Each VC's recent investments, check size, and portfolio
3. Best angle to pitch each one (what they care about)
4. Warm intro pathways (mutual connections, portfolio companies)
5. Pitch timing recommendations

Format as a tactical outreach plan.
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2000,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"💰 GOPAY VC TRACKER\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[INTEL] Error generating VC tracker: {e}")
            return f"⚠️ INTEL Error: {e}"

    async def scrape_webpage(self, url: str) -> str:
        """Native web scraper using aiohttp + BeautifulSoup4."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status != 200:
                        return f"Failed to fetch {url}: HTTP {response.status}"
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    text_blocks = [elem.get_text(strip=True) for elem in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])]
                    text_content = "\n".join(text_blocks)
                    return text_content[:5000]
        except Exception as e:
            log.error(f"[INTEL] Scraping error for {url}: {e}")
            return f"Error scraping {url}: {e}"

    async def analyze_webpage(self, url: str, query: str = "") -> str:
        """Scrape a webpage and analyze it using Claude."""
        content = await self.scrape_webpage(url)
        if content.startswith("Error") or content.startswith("Failed"):
            return content
            
        prompt = f"""
Analyze the following webpage content extracted from {url}.
Query: {query if query else 'Provide a comprehensive summary and key takeaways.'}

Webpage Content:
{content}
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1500,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"🌐 WEBPAGE ANALYSIS — {url}\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[INTEL] Error analyzing webpage: {e}")
            return f"⚠️ INTEL Error analyzing webpage: {e}"

    async def research_to_reel(self, topic: str) -> str:
        """Convert a research topic/snippet into a 15-second script + caption."""
        prompt = f"""
Turn the following research topic/finding into a 15-second script for Instagram Reels/TikTok.
Topic: {topic}

Requirements:
- Hook (first 3 seconds)
- Core insight
- Call to action
- Short engaging caption with hashtags
Keep the tone pragmatic, educational, and engaging.
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"🎬 RESEARCH TO REEL\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[INTEL] Error generating reel: {e}")
            return f"⚠️ INTEL Error: {e}"

    async def generate_youtube_script(self, topic: str) -> str:
        """Generate a 5-minute faceless YouTube script from research."""
        prompt = f"""
Write a 5-minute faceless YouTube script based on this research topic: {topic}

Use the following exact structure:
1. The Hook (0:00 - 0:45): Intriguing question, visual prompt (no faces), surprising stat.
2. The Problem (0:45 - 2:00): Core issue, text overlays.
3. The Data & Evidence (2:00 - 3:45): 2-3 key findings translated to human impact, animated charts visual prompt.
4. The Solution (3:45 - 4:30): Actionable steps, b-roll of solutions.
5. Call to Action (4:30 - 5:00): Direct viewers to the website and consulting link.

Format clearly with Visuals and Audio separated for each section.
"""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                system=INTEL_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"🎥 YOUTUBE SCRIPT\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[INTEL] Error generating YouTube script: {e}")
            return f"⚠️ INTEL Error: {e}"
