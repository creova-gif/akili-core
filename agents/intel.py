# ============================================================
# INTEL — Research & Lead Generation Agent
# Deep research, leads, daily briefs, VC tracking
# ============================================================

import logging
from datetime import datetime
from anthropic import Anthropic

log = logging.getLogger("INTEL")

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
"""


class IntelAgent:
    def __init__(self, api_key: str, memory):
        self.client = Anthropic(api_key=api_key)
        self.memory = memory
        log.info("INTEL agent initialized")

    async def handle(self, command: str) -> str:
        """Process a research command from Justin."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=INTEL_PROMPT,
            messages=[{"role": "user", "content": command}]
        )
        result = response.content[0].text
        self.memory.daily_log(f"[INTEL] Research: {command[:60]}")
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
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=INTEL_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

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
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2500,
            system=INTEL_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"📊 {product.upper()} RESEARCH\n\n{response.content[0].text}"

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
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=INTEL_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"🎯 LEADS — {venture}\n\n{response.content[0].text}"

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
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=INTEL_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"💰 GOPAY VC TRACKER\n\n{response.content[0].text}"
