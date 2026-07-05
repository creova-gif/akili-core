# ============================================================
# CREOVA_MEDIA — Creative Agency Operations Agent
# Inquiry triage · Proposals · Invoice chaser · Capacity monitor
# ============================================================

import logging
import os
from core.ai_client import get_client
from config.ai_models import MODEL
from config.creova_services import CREOVA_MEDIA_CONTEXT, CREOVA_MEDIA_SERVICES, CAPACITY_THRESHOLDS

log = logging.getLogger("CREOVA_MEDIA")

WAVE_EXPORT_PATH = os.environ.get("WAVE_EXPORT_PATH", "./data/wave_export.csv")

TELEGRAM_FORMAT = """
━━━━━━━━━━━━━━━━━━━━
TELEGRAM FORMATTING (MANDATORY — apply to every response):
▸ Start with: 🎨 CREOVA MEDIA — [TOPIC] on its own line
▸ Use ━━━━━━━━━━━━━━━━━━━━ as section dividers
▸ Use ▸ for bullets, ◦ for sub-bullets
▸ Use ① ② ③ for numbered steps
▸ Proposals/emails: wrap in ┌──────────┐ / └──────────┘
▸ End with a line starting ⚡ with the key action
▸ NEVER use markdown symbols (**, ##) — Unicode only
▸ Under 400 words unless generating a full proposal
━━━━━━━━━━━━━━━━━━━━
"""

CREOVA_MEDIA_PROMPT = """
You are CREOVA_MEDIA, the creative agency operations agent for AKILI.

YOU MANAGE:
1. Client inquiry triage — categorize, check availability, draft replies
2. Proposals — scope, pricing, contract terms, deposit requests
3. Invoice follow-up — Wave exports, overdue tracking, payment nudges
4. Post-delivery follow-ups — 48h check-ins, referral asks, upsells
5. Capacity monitoring — shoot days, editing hours, overextension alerts
6. Notion CRM updates — flag what to log after each client interaction

JUSTIN'S BRAND VOICE FOR ALL CLIENT COMMS:
- Warm, professional, peer-to-peer — not corporate
- Cultural storytelling roots always present in 1 sentence
- Clear next step at end of every message
- Sign off: "Justin | CREOVA · creova.one"

OVEREXTENSION RULE: If any week exceeds capacity thresholds — flag it RED and
suggest which type of contractor to bring in.
""" + "\n" + CREOVA_MEDIA_CONTEXT + "\n" + CREOVA_MEDIA_SERVICES + "\n" + TELEGRAM_FORMAT


class CREOVAMediaAgent:
    def __init__(self, api_key: str, memory):
        self.client = get_client(api_key, "CREOVA_MEDIA")
        self.memory = memory
        log.info("CREOVA_MEDIA agent initialized")

    async def handle(self, command: str) -> str:
        """Inquiry triage / proposal / follow-up conversation entry point.
        Covers /media, /inquiry, /proposal, /followup — the prompt above
        already scopes all of those use cases, same as every other agent's
        single .handle() entry point."""
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1200,
                system=CREOVA_MEDIA_PROMPT,
                messages=[{"role": "user", "content": command}],
            )
            result = response.content[0].text
        except Exception as e:
            log.error(f"[CREOVA_MEDIA] Error: {e}")
            result = f"⚠️ CREOVA_MEDIA encountered an error: {e}"
        await self.memory.daily_log(f"[CREOVA_MEDIA] Command: {command[:60]}")
        return result

    async def run_invoice_chaser(self, wave_data: str = "") -> str:
        """Monday morning automation — reads the Wave export, drafts follow-ups.
        Only a "ran" note is logged to memory, never the financial content
        itself — see the PRIVACY / BLAST RADIUS rule in creova_services.py."""
        wave_data = wave_data or self._read_wave_export()
        prompt = f"""Run the CREOVA invoice chaser. Wave data:
{wave_data}

For each overdue invoice:
- Under 7 days: friendly nudge with invoice # and amount
- 7-14 days: firm reminder referencing Net-15 terms
- 15-30 days: formal request with next steps
- 30+ days: final notice + flag for Justin

Queue all for approval. Format each invoice as its own block.
End with a summary: total outstanding CAD, number of invoices."""
        try:
            response = await self.client.messages.create(
                model=MODEL, max_tokens=1500,
                system=CREOVA_MEDIA_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.content[0].text
        except Exception as e:
            log.error(f"[CREOVA_MEDIA] Invoice chaser error: {e}")
            result = f"⚠️ Invoice chaser error: {e}"
        await self.memory.daily_log("[CREOVA_MEDIA] Invoice chaser ran")
        return f"🎨 CREOVA MEDIA — Invoice Run\n\n{result}"

    async def run_capacity_check(self, notion_data: str = "") -> str:
        """Capacity monitor — shoot days, editing hours, retainer load."""
        notion_data = notion_data or self._get_notion_summary()
        t = CAPACITY_THRESHOLDS
        prompt = f"""Run the CREOVA capacity monitor. Current projects and bookings:
{notion_data}

Calculate:
1. Total shoot days this week and next 3 weeks
2. Estimated editing hours per shoot type
3. Active retainer clients and their weekly hour load
4. SEEN dev planned hours
5. Total weekly hours — flag RED if over {t['max_work_hours_per_week']}

If any week exceeds thresholds:
- Over {t['max_shoot_days_per_week']} shoot days: flag, suggest second shooter contractor
- Over {t['max_retainer_clients']} retainers: flag, suggest social media assistant hire
- Over {t['max_work_hours_per_week']} total hours: flag red, recommend what to defer

Give a 4-week traffic light view (green/yellow/red per week)."""
        try:
            response = await self.client.messages.create(
                model=MODEL, max_tokens=800,
                system=CREOVA_MEDIA_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.content[0].text
        except Exception as e:
            log.error(f"[CREOVA_MEDIA] Capacity check error: {e}")
            result = f"⚠️ Capacity check error: {e}"
        await self.memory.daily_log("[CREOVA_MEDIA] Capacity check ran")
        return f"📊 CREOVA — Capacity Monitor\n\n{result}"

    def _read_wave_export(self) -> str:
        """Read the Wave CSV export. Justin drops this in data/ weekly."""
        try:
            with open(WAVE_EXPORT_PATH) as f:
                return f.read()[:3000]
        except OSError:
            return "[Wave export not found. Upload to data/wave_export.csv]"

    def _get_notion_summary(self) -> str:
        """No live Notion bridge yet — Justin pastes the project list after
        the command until one exists."""
        return "[No project list provided — paste your current bookings/projects after the command]"
