# ============================================================
# INTEL LEAD ENGINE — Phase 5
# VC intelligence + lead generation for CREOVA
#
# OpenVC    → VC database (FREE, 9,000+ investors, Africa data)
# Apollo.io → Lead gen + contact data (FREE: 50 credits/month)
# Hunter.io → Email finder (FREE: 25 searches/month)
#
# No Crunchbase needed — these beat it for CREOVA's use case
# ============================================================

import os
import logging
import aiohttp
import asyncio
from datetime import datetime
from core.ai_client import get_client
from config.ai_models import MODEL
from skills.shared.telegram_formatter import formatter, DIVIDER

log = logging.getLogger("INTEL.LeadEngine")

ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")
HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY", "")
OPENVC_API_KEY = os.environ.get("OPENVC_API_KEY", "")


class IntelLeadEngine:
    """
    INTEL's lead generation and VC intelligence layer.
    Uses Apollo, OpenVC, and Hunter — all free tiers.
    Falls back to Anthropic web search if APIs not configured.
    """

    def __init__(self, telegram_app, memory):
        self.app    = telegram_app
        self.memory = memory
        self.client = get_client(ANTHROPIC_KEY, "INTEL")
        configured  = [k for k, v in [
            ("Apollo", APOLLO_API_KEY), ("Hunter", HUNTER_API_KEY), ("OpenVC", OPENVC_API_KEY)
        ] if v]
        log.info(f"INTEL LeadEngine initialized — {', '.join(configured) if configured else 'web search mode (add API keys to unlock more)'}")

    # ── Apollo.io lead search ─────────────────────────────────
    async def apollo_search(self, query: dict) -> list:
        """
        Search Apollo for leads. Free tier: 50 credits/month.
        Each search = 1 credit. Results include verified emails.
        """
        if not APOLLO_API_KEY:
            return []

        url = "https://api.apollo.io/v1/mixed_people/search"
        headers = {
            "Content-Type":  "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key":     APOLLO_API_KEY,
        }
        payload = {**query, "page": 1, "per_page": 10}

        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, json=payload, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status == 200:
                        data   = await r.json()
                        people = data.get("people", [])
                        log.info(f"[Apollo] Found {len(people)} leads")
                        return people
                    log.warning(f"[Apollo] Status {r.status}")
                    return []
        except Exception as e:
            log.error(f"[Apollo] Error: {e}")
            return []

    # ── Hunter.io email finder ────────────────────────────────
    async def hunter_find_email(self, domain: str, first_name: str = "",
                                 last_name: str = "") -> dict:
        """Find decision-maker email at a company domain. Free: 25/month."""
        if not HUNTER_API_KEY:
            return {}

        params = {
            "domain": domain, "first_name": first_name,
            "last_name": last_name, "api_key": HUNTER_API_KEY,
        }
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get("https://api.hunter.io/v2/email-finder",
                                  params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data.get("data", {})
                    return {}
        except Exception as e:
            log.error(f"[Hunter] Error: {e}")
            return {}

    async def hunter_domain_search(self, domain: str) -> list:
        """Get all public emails found at a domain."""
        if not HUNTER_API_KEY:
            return []

        params = {"domain": domain, "api_key": HUNTER_API_KEY, "limit": 5}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get("https://api.hunter.io/v2/domain-search",
                                  params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data.get("data", {}).get("emails", [])
                    return []
        except Exception as e:
            log.error(f"[Hunter] Error: {e}")
            return []

    # ── OpenVC investor search ────────────────────────────────
    async def openvc_search_investors(self, filters: dict = None) -> list:
        """
        Search OpenVC for investors. FREE — 9,000+ investors with Africa data.
        Falls back to web search if API unavailable.
        """
        if not OPENVC_API_KEY:
            return await self._vc_web_search(filters or {})

        params  = filters or {"stage": "seed,pre-seed", "location": "Africa,Canada", "focus": "fintech,healthtech"}
        headers = {"Authorization": f"Bearer {OPENVC_API_KEY}"}

        try:
            async with aiohttp.ClientSession() as s:
                async with s.get("https://api.openvc.com/v1/investors",
                                  params=params, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status == 200:
                        data      = await r.json()
                        investors = data.get("investors", [])
                        log.info(f"[OpenVC] Found {len(investors)} investors")
                        return investors
                    return await self._vc_web_search(params)
        except Exception as e:
            log.error(f"[OpenVC] Error: {e} — using web fallback")
            return await self._vc_web_search(filters or {})

    async def _vc_web_search(self, filters: dict) -> list:
        """Fallback: use Anthropic web search to find VC data."""
        focus    = filters.get("focus", "African tech fintech")
        stage    = filters.get("stage", "seed pre-seed")
        location = filters.get("location", "Africa Canada")

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1200,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content":
                    f"Find 5 VCs actively investing in {focus} at {stage} stage in {location} in 2026. "
                    f"For each: fund name, managing partner, check size, notable portfolio companies, "
                    f"best pitch angle for a Black founder, contact/website."}]
            )
            result = ""
            for block in response.content:
                if hasattr(block, "text"):
                    result += block.text
            return [{"source": "web_search", "data": result}]
        except Exception as e:
            log.error(f"[INTEL] VC web search error: {e}")
            return []

    # ── Generate leads for CREOVA Solutions ──────────────────
    async def generate_creova_leads(self, service: str = "tech development",
                                     market: str = "Canada") -> str:
        """Generate real, actionable leads using Apollo + Hunter."""
        log.info(f"[INTEL] Generating leads — {service} in {market}")

        search_configs = {
            "tech development + Canada": {
                "person_titles":    ["CTO", "Founder", "CEO", "Head of Technology"],
                "person_locations": ["Canada", "Ontario", "Toronto"],
                "q_keywords":       "startup tech product build",
            },
            "branding + Canada": {
                "person_titles":    ["Founder", "CEO", "Marketing Director", "Creative Director"],
                "person_locations": ["Canada"],
                "q_keywords":       "BIPOC business brand identity",
            },
            "tech development + East Africa": {
                "person_titles":    ["Founder", "CEO", "CTO"],
                "person_locations": ["Kenya", "Tanzania", "Uganda"],
                "q_keywords":       "startup fintech agritech healthtech",
            },
        }

        key    = f"{service} + {market}"
        config = search_configs.get(key, search_configs["tech development + Canada"])
        people = await self.apollo_search(config)

        if not people:
            return await self._ai_lead_gen(service, market)

        lead_lines = []
        for i, person in enumerate(people[:5], 1):
            name    = f"{person.get('first_name','')} {person.get('last_name','')}".strip()
            title   = person.get("title", "Unknown role")
            company = person.get("organization", {}).get("name", "Unknown")
            email   = person.get("email", "")

            if not email and person.get("organization", {}).get("website_url"):
                domain = (person["organization"]["website_url"]
                          .replace("https://","").replace("http://","").split("/")[0])
                hr = await self.hunter_find_email(domain, person.get("first_name",""), person.get("last_name",""))
                email = hr.get("email", "")

            angle = self._outreach_angle(service, title, company)
            lead_lines.append(
                f"  <b>{i}. {name}</b>\n"
                f"     {title} @ {company}\n"
                f"     📧 <code>{email or 'email not found'}</code>\n"
                f"     💡 Angle: {angle}"
            )

        await self.memory.daily_log(f"[INTEL] Generated {len(people)} leads — {service} / {market}")

        return formatter.format("INTEL", "research", {
            "query":        f"Lead gen: {service} in {market}",
            "source_count": "Apollo + Hunter",
            "findings":     [f"Found {len(people)} qualified leads"] + lead_lines[:3],
            "creova_angle": f"CREOVA Solutions offers {service} — pitch these decision-makers directly",
            "action":       "Reply <code>outreach [name] [company]</code> to generate a personalized pitch",
            "confidence":   "High — Apollo verified contacts",
        })

    async def _ai_lead_gen(self, service: str, market: str) -> str:
        """Fallback lead gen using Anthropic web search when Apollo not configured."""
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1200,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content":
                    f"Find 5 specific companies or founders in {market} who would benefit from CREOVA's "
                    f"{service} services. Include: company name, founder/decision-maker name, "
                    f"why they need {service}, and how to contact them. Be specific with real companies."}]
            )
            result = ""
            for block in response.content:
                if hasattr(block, "text"):
                    result += block.text
        except Exception as e:
            log.error(f"[INTEL] AI lead gen error: {e}")
            result = "Lead generation failed due to API error."

        await self.memory.daily_log(f"[INTEL] Lead gen via web search — {service} / {market}")
        return await formatter.ai_enhance(
            f"🎯 CREOVA LEADS — {service.upper()} | {market}\n\n{result}",
            "INTEL", f"lead generation {service}"
        )

    def _outreach_angle(self, service: str, title: str, company: str) -> str:
        angles = {
            "tech":    f"'{company} needs a tech partner who builds for real emerging markets'",
            "brand":   f"'Position {company} with an identity that actually stands out'",
            "social":  f"'Your social presence doesn't match the quality of what you build'",
            "music":   f"'CREOVA Music can help {company} reach new audiences through sound'",
        }
        for key, angle in angles.items():
            if key in service.lower():
                return angle
        return f"'CREOVA can unlock the next growth chapter for {company}'"

    # ── VC tracker for GoPay ─────────────────────────────────
    async def vc_tracker(self, product: str = "GoPay") -> str:
        """Find active VCs investing in products like the one specified."""
        filters = {
            "focus":    "fintech Africa East Africa",
            "stage":    "seed pre-seed series-A",
            "location": "Africa Canada UK USA",
        }
        if "mental" in product.lower() or "health" in product.lower():
            filters["focus"] = "healthtech BIPOC mental health Canada"
        elif "kaya" in product.lower() or "property" in product.lower():
            filters["focus"] = "proptech real estate Africa Canada"
        elif "kilimo" in product.lower() or "agri" in product.lower():
            filters["focus"] = "agritech Africa East Africa"

        investors = await self.openvc_search_investors(filters)

        if not investors:
            return "⚠️ VC tracker: no results. Try <code>vc tracker gopay</code> or add OPENVC_API_KEY secret."

        if isinstance(investors, list) and investors and investors[0].get("source") == "web_search":
            raw = investors[0].get("data", "")
            return await formatter.ai_enhance(
                f"🏦 VC TRACKER — {product.upper()}\n\n{raw}", "INTEL", f"VC research {product}"
            )

        lines = [f"🏦 <b>VC TRACKER — {product.upper()}</b>", DIVIDER]
        for inv in investors[:6]:
            name  = inv.get("name", "Unknown fund")
            focus = inv.get("focus", "")
            stage = inv.get("stage", "")
            lines.append(f"  ▸ <b>{name}</b> — {stage} · {focus}")

        lines.append(f"\n{DIVIDER}")
        lines.append(f"⚡ <code>leads tech East Africa</code> to find their portfolio companies as warm intros")
        await self.memory.daily_log(f"[INTEL] VC tracker ran for {product}")
        return "\n".join(lines)
