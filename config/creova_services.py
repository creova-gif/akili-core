# ============================================================
# CREOVA.ONE SERVICE EMBEDDINGS
# Maps every creova.one service into the right agent
# So Akili promotes, pitches, and sells CREOVA services
# in every interaction — authentically, not like an ad
# ============================================================

SERVICE_CATALOG = {

    # ── CREATIVE SERVICES ─────────────────────────────────────
    "brand_identity": {
        "name":        "Brand Identity & Strategy",
        "description": "Logo, brand guidelines, visual identity, brand voice — built for BIPOC businesses and African startups",
        "target":      "BIPOC-owned businesses Canada, African startups, tech founders",
        "price_hint":  "Custom quote",
        "agent":       "PULSE",
        "embed_how":   "PULSE showcases CREOVA's branding work via @creovasolutions posts. Every brand transformation is a case study that attracts clients.",
        "proof":       "Justin's own CREOVA brand is the portfolio piece",
        "cta":         "creova.one/branding",
    },

    "photography_video": {
        "name":        "Photography & Video Production",
        "description": "Commercial shoots, brand videos, content creation — African futurism aesthetic",
        "target":      "Brands, artists, events, product launches",
        "price_hint":  "Day rate or package",
        "agent":       "PULSE + AMPLIFY",
        "embed_how":   "Behind-scenes content from shoots goes on @jj_mafie and @sankofastudio__. Shows capability without a sales pitch.",
        "proof":       "CREOVA Music music videos, SEEN fashion shoots",
        "cta":         "creova.one/production",
    },

    "social_media_management": {
        "name":        "Social Media Management",
        "description": "Full-service social media management — strategy, content, posting, engagement — the PULSE service",
        "target":      "SMEs, founders, artists, BIPOC businesses",
        "price_hint":  "$500-$2,000/month",
        "agent":       "PULSE + REACH",
        "embed_how":   "PULSE literally IS this service running for Justin. Every piece of content Akili creates is proof of what CREOVA can do for a client.",
        "proof":       "Tassia Gabbidon (CREOVA's first social media client)",
        "cta":         "creova.one/social",
    },

    "content_creation": {
        "name":        "Content Creation & Copywriting",
        "description": "Blog posts, newsletters, LinkedIn articles, email campaigns — storytelling rooted in cultural identity",
        "target":      "Brands, founders, healthcare providers, NGOs",
        "price_hint":  "Per piece or retainer",
        "agent":       "REACH + PULSE",
        "embed_how":   "Every thought leadership article REACH drafts for Justin becomes a sample. INTEL's research becomes a service offering.",
        "proof":       "This very content strategy",
        "cta":         "creova.one/content",
    },

    # ── TECH SERVICES ─────────────────────────────────────────
    "web_app_development": {
        "name":        "Web & Mobile App Development",
        "description": "Full-stack apps built for emerging markets — React, Next.js, Supabase, React Native. Offline-first. M-Pesa ready.",
        "target":      "African startups, NGOs, SMEs needing tech, Canadian businesses",
        "price_hint":  "$5,000-$50,000+ per project",
        "agent":       "INTEL + SHIELD",
        "embed_how":   "INTEL's product research identifies client needs. The 14 CREOVA products are the portfolio. SHIELD's GitHub monitoring is proof of technical rigor.",
        "proof":       "GoPay, Kaya, MentalPath, WazaWealth, KilimoAI — all live repos",
        "cta":         "creova.one/tech",
    },

    "ai_integration": {
        "name":        "AI Integration & Automation",
        "description": "Building AI agents, automations, and Claude integrations into existing products",
        "target":      "Startups wanting to add AI, businesses wanting automation",
        "price_hint":  "$3,000-$20,000",
        "agent":       "INTEL",
        "embed_how":   "Akili itself is the pitch. 'We built this for ourselves — we can build it for you.' INTEL tracks AI opportunities to sell this service.",
        "proof":       "Akili AI OS is the case study",
        "cta":         "creova.one/ai",
    },

    "startup_consulting": {
        "name":        "Startup Strategy & Go-to-Market",
        "description": "GTM strategy, fundraising prep, competitive analysis, pitch decks for African and Canadian startups",
        "target":      "Pre-seed and seed stage startups in Africa and Canada",
        "price_hint":  "$2,000-$10,000 engagements",
        "agent":       "INTEL",
        "embed_how":   "Every GoPay VC deck INTEL builds is a consulting deliverable. INTEL's market research IS the product. Thought leadership content attracts founders.",
        "proof":       "GoPay investor materials, all 14 product GTM strategies",
        "cta":         "creova.one/consulting",
    },

    # ── MUSIC SERVICES ────────────────────────────────────────
    "music_production": {
        "name":        "Music Production (Sankofa Studio)",
        "description": "Beat production, mixing, mastering, full production services out of Sankofa Studio",
        "target":      "Independent African artists, Canadian artists, emerging musicians",
        "price_hint":  "Beat licensing from $50, full production custom quote",
        "agent":       "AMPLIFY",
        "embed_how":   "Every @sankofastudio__ post attracts artists. AMPLIFY's release campaigns demonstrate what Sankofa delivers. Behind-scenes studio content builds credibility.",
        "proof":       "CREOVA Music catalog",
        "cta":         "creova.one/studio",
    },

    "artist_development": {
        "name":        "Artist Development & Music Marketing",
        "description": "Release strategy, playlist pitching, press outreach, social media for independent artists",
        "target":      "Independent artists in Africa and Canada",
        "price_hint":  "$500-$2,000/month or per-release",
        "agent":       "AMPLIFY + PULSE",
        "embed_how":   "Justin's own music career is the case study. Every milestone Akili hits for Justin's music is a service demo.",
        "proof":       "CREOVA Music stream growth, release campaigns",
        "cta":         "creova.one/artists",
    },
}


def get_service_context_for_agent(agent: str) -> str:
    """Returns the service context for a specific agent's system prompt."""
    services = [s for s in SERVICE_CATALOG.values() if agent in s.get("agent", "")]
    if not services:
        return ""
    lines = ["CREOVA.ONE SERVICES YOU REPRESENT (weave in naturally — never like an ad):"]
    for s in services:
        lines.append(f"• {s['name']}: {s['description']}")
        lines.append(f"  Proof: {s['proof']} | Link: {s['cta']}")
    return "\n".join(lines)


def get_all_services_summary() -> str:
    """Summary of all services — for INTEL and general Akili awareness."""
    lines = ["CREOVA.ONE FULL SERVICE CATALOG:"]
    categories = {
        "Creative": ["brand_identity", "photography_video", "social_media_management", "content_creation"],
        "Tech":     ["web_app_development", "ai_integration", "startup_consulting"],
        "Music":    ["music_production", "artist_development"],
    }
    for category, keys in categories.items():
        lines.append(f"\n{category.upper()}:")
        for key in keys:
            if key in SERVICE_CATALOG:
                s = SERVICE_CATALOG[key]
                lines.append(f"  • {s['name']} — {s['price_hint']} — {s['cta']}")
    return "\n".join(lines)


SERVICE_INJECTION_PROMPTS = {
    "PULSE": """
When creating content, naturally reference CREOVA services where relevant:
- Branding post? Mention creova.one/branding
- Tech content? @creovasolutions builds apps and AI for Africa
- Studio content? Sankofa Studio takes bookings — creova.one/studio
Never make it feel like an ad. 1 CTA per post maximum.
""",
    "REACH": """
When replying to business inquiries, qualify the lead:
- If they need branding → propose CREOVA brand identity service
- If they need tech → propose CREOVA app development
- If they're an artist → propose Sankofa Studio or artist development
- Always direct to creova.one for more info
- Never quote prices — say 'Let's set up a quick call to scope this out'
""",
    "INTEL": """
When researching leads, flag potential CREOVA clients:
- Startups that need tech built → web_app_development service
- Brands without strong identity → brand_identity service
- Artists without digital strategy → artist_development service
- Businesses wanting AI → ai_integration service
Tag every lead with which CREOVA service fits them best.
""",
    "AMPLIFY": """
Every milestone, release, and campaign is proof of CREOVA Music services.
When reporting streaming wins, include: 'This campaign is available for other artists — creova.one/artists'
Sankofa Studio content should always mention booking availability.
""",
}


# ============================================================
# CREOVA MEDIA — AGENCY OPERATIONS CONTEXT
# Read by agents/creova_media.py and scheduler/creova_os.py.
# Business context that used to live in MEMORY.md before that
# file was scrubbed from this (now public) repo's history.
# ============================================================

CREOVA_MEDIA_CONTEXT = """
CREOVA MEDIA BUSINESS CONTEXT:
- Type: Black-owned creative agency + platform company
- Location: Ontario, Canada (Niagara / GTHA region)
- Founded: April 2025 by Justin Mafie
- Status: Revenue generating, bootstrapped
- Website: creova.one | IG: @creativeinnovation__

THREE BUSINESS LINES:
1. Creative Agency — photography, videography, branding, social media management
2. SEEN — audio-first streaming platform for Canadian equity-deserving creators (MVP complete)
3. CREOVA Fashion — culturally-rooted lifestyle clothing brand (Shopify)
4. CREOVA Music — distributed via DistroKid (live on all DSPs)

FINANCIAL OPERATING RULES:
- Invoicing: Wave (waveapps.com) — Justin exports CSV weekly to data/wave_export.csv
- Payment terms: 50% deposit + Net-15 balance
- 2026 revenue target: $50,000+ creative agency
- Monthly close: runs 1st of month via the CREOVA OS scheduler
- Invoice chaser: runs every Monday 8:15 AM ET

KEY 2026 DEADLINES:
- CMF Convergent Stream application: June 2026
- CREOVA Inc federal incorporation: Q2 2026 (target May)
- IRAP application: after incorporation
- BDC Black Entrepreneur Program: ongoing
- SEEN soft launch: Q3 2026

AUTOMATION SCHEDULE (CREOVAOSScheduler):
- Monday 8:15 AM: invoice chaser + capacity monitor + compliance check
- Tuesday 9:00 AM: 10 outreach DMs drafted and sent to Telegram
- Friday 9:00 AM: next-week content calendar
- Friday 9:30 AM: caption + hashtag batch
- Last Friday of month: newsletter draft
- 1st of month: monthly financial close

PRIVACY / BLAST RADIUS (never violate):
- CREOVA client data stays in Notion — Akili bridges but never stores PII in its own logs
- Wave financial data is processed in-memory for a response only, never written to akili.log
- Creator demographics for SEEN: never stored in Akili memory, only on the SEEN platform itself
"""

# Services & rates (used by CREOVAMediaAgent for proposals/quotes)
CREOVA_MEDIA_SERVICES = """
CREOVA MEDIA SERVICES & RATES:
- Event photography half-day: $300-500 CAD
- Event photography full-day: $600-900 CAD
- Event videography (highlight reel): $600-1,000 CAD
- Brand photography session: $400-800 CAD
- Logo design package: $300-600 CAD
- Full brand identity kit: $800-1,500 CAD
- Social media management starter (8 posts/mo): $500/mo
- Social media management growth (16 posts/mo): $800/mo
- Social media management premium (30 posts + stories): $1,500/mo
- Full content creation package: $1,500-4,000 CAD

PAYMENT TERMS: 50% deposit to confirm, balance due on delivery (Net-15)
PORTFOLIO: creova.one | Instagram: @creativeinnovation__
"""

# Capacity thresholds — SHIELD's financial-ops prompt and CREOVAMediaAgent
# both reference these; kept in one place so they can't drift apart.
CAPACITY_THRESHOLDS = {
    "max_shoot_days_per_week":  3,
    "max_retainer_clients":     5,
    "max_work_hours_per_week": 50,
}
