# ============================================================
# AKILI CORE — main.py (Phase 3 — FULL VERSION)
# Orchestrator + 5 agents + auto-scheduler + auto-responder
# + live intel + API server — all running together
# ============================================================

import os
import asyncio
import logging
import threading
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from agents.shield   import ShieldAgent
from agents.pulse    import PulseAgent
from agents.reach    import ReachAgent
from agents.intel    import IntelAgent
from agents.amplify  import AmplifyAgent
from memory.manager  import MemoryManager

# Phase 3 modules
from scheduler.pulse_scheduler   import PulseScheduler
from scheduler.reach_autoresponder import ReachAutoResponder
from scheduler.intel_live        import IntelLiveBrief

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("logs/akili.log"), logging.StreamHandler()]
)
log = logging.getLogger("AKILI-CORE")

TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_KEY    = os.environ["ANTHROPIC_API_KEY"]
JUSTIN_CHAT_ID   = os.environ["JUSTIN_CHAT_ID"]


class AkiliCore:
    def __init__(self):
        self.memory   = MemoryManager()

        # 5 base agents
        self.shield   = ShieldAgent(ANTHROPIC_KEY, self.memory)
        self.pulse    = PulseAgent(ANTHROPIC_KEY, self.memory)
        self.reach    = ReachAgent(ANTHROPIC_KEY, self.memory)
        self.intel    = IntelAgent(ANTHROPIC_KEY, self.memory)
        self.amplify  = AmplifyAgent(ANTHROPIC_KEY, self.memory)

        # Phase 3 — live modules (set after app is created)
        self.scheduler   = None
        self.responder   = None
        self.live_intel  = None

        log.info("AKILI CORE (Phase 3) initialized")

    def init_phase3(self, app, integrations=None):
        """Called after Telegram app is ready."""
        self.scheduler  = PulseScheduler(app, integrations)
        self.live_intel = IntelLiveBrief(app, self.memory)

        # REACH auto-responder needs gmail — graceful if not configured
        try:
            from integrations import IntegrationHub
            hub = integrations or IntegrationHub()
            self.responder = ReachAutoResponder(app, hub.gmail)
        except Exception as e:
            log.warning(f"REACH responder not fully loaded: {e}")

        log.info("Phase 3 modules initialized")

    async def route_command(self, text: str) -> str:
        lower = text.lower()

        # ── Approval commands (PULSE scheduler) ──────────────
        if self.scheduler and any(text.upper().startswith(k) for k in ["POST ", "SKIP ", "EDIT "]):
            result = await self.scheduler.handle_approval(text)
            if result:
                return result

        # ── Draft reply (REACH) ───────────────────────────────
        if lower.startswith("draft reply"):
            context = text[len("draft reply"):].strip()
            if self.responder:
                return await self.responder.draft_reply(context)

        # ── Repurpose content ─────────────────────────────────
        if lower.startswith("repurpose"):
            content = text[9:].strip()
            if self.responder:
                return await self.responder.repurpose(content, "original source")

        # ── Pending posts ─────────────────────────────────────
        if "pending" in lower and "post" in lower:
            if self.scheduler:
                return self.scheduler.list_pending()

        # ── Live research ─────────────────────────────────────
        if lower.startswith("research") or lower.startswith("search"):
            query = text.split(" ", 1)[1] if " " in text else text
            if self.live_intel:
                return await self.live_intel.live_research(query)

        # ── VC tracker ────────────────────────────────────────
        if "vc tracker" in lower or ("gopay" in lower and "vc" in lower):
            if self.live_intel:
                return await self.live_intel.live_vc_tracker()

        # ── Competitor intel ──────────────────────────────────
        if "competitor" in lower:
            product = text.split("competitor", 1)[-1].strip() or "GoPay"
            if self.live_intel:
                return await self.live_intel.competitor_monitor(product)

        # ── Agent routing ─────────────────────────────────────
        if any(w in lower for w in ["security", "github", "repo", "uptime", "scan"]):
            return await self.shield.handle(text)

        elif any(w in lower for w in ["post", "instagram", "twitter", "linkedin", "tiktok", "social", "calendar", "content", "schedule"]):
            return await self.pulse.handle(text)

        elif any(w in lower for w in ["email", "dm", "reply", "message", "repurpose", "draft"]):
            return await self.reach.handle(text)

        elif any(w in lower for w in ["lead", "investor", "market", "brief", "intel"]):
            return await self.intel.handle(text)

        elif any(w in lower for w in ["music", "stream", "spotify", "distrokid", "playlist", "amplify", "snapchat creator"]):
            return await self.amplify.handle(text)

        else:
            return await self._general(text)

    async def _general(self, text: str) -> str:
        from anthropic import Anthropic
        c = Anthropic(api_key=ANTHROPIC_KEY)
        r = c.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            system="You are Akili, the autonomous AI OS for Justin Mafie and CREOVA. Answer concisely and helpfully.",
            messages=[{"role": "user", "content": text}]
        )
        return r.content[0].text

    async def status_report(self) -> str:
        shield_status = await self.shield.status()
        platform_count = 8
        lines = [
            "⚡ AKILI STATUS — Full Report",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "AGENTS: SHIELD · PULSE · REACH · INTEL · AMPLIFY — all active",
            f"Platforms connected: {platform_count}",
            "Phase 3: Auto-scheduler + Auto-responder + Live Intel — ACTIVE",
            "",
            shield_status,
        ]
        return "\n".join(lines)

    # ── Heartbeat ─────────────────────────────────────────────
    async def heartbeat(self, app):
        while True:
            log.info(f"[HEARTBEAT] {datetime.now().strftime('%H:%M')}")
            try:
                alert = await self.shield.heartbeat_check()
                if alert:
                    await app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=alert)
                await self.amplify.heartbeat_check()
                if self.pulse:
                    await self.pulse.heartbeat_check()
                self.memory.daily_log(f"Heartbeat OK at {datetime.now().isoformat()}")
            except Exception as e:
                log.error(f"[HEARTBEAT] Error: {e}")
            await asyncio.sleep(1800)


# ── Global instance ───────────────────────────────────────────
akili = AkiliCore()


# ── Telegram handlers ─────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != JUSTIN_CHAT_ID:
        return
    msg = (
        "⚡ AKILI OS — Phase 3 Online\n\n"
        "5 agents active:\n"
        "🛡 SHIELD · 📡 PULSE · 📨 REACH · 🔍 INTEL · 🔊 AMPLIFY\n\n"
        "New in Phase 3:\n"
        "• Posts auto-generated + sent for approval\n"
        "• Emails auto-replied while you're offline\n"
        "• Morning brief uses live web search\n"
        "• Dashboard connected to live agents\n\n"
        "Send me anything, Justin."
    )
    await update.message.reply_text(msg)

async def status_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != JUSTIN_CHAT_ID:
        return
    report = await akili.status_report()
    await update.message.reply_text(report)

async def pending_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != JUSTIN_CHAT_ID:
        return
    if akili.scheduler:
        await update.message.reply_text(akili.scheduler.list_pending())
    else:
        await update.message.reply_text("PULSE scheduler not yet initialized.")

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != JUSTIN_CHAT_ID:
        return
    text = update.message.text
    log.info(f"[COMMAND] Justin: {text}")
    await update.message.reply_text("⚙️ Processing...")
    try:
        response = await akili.route_command(text)
        await update.message.reply_text(response)
        akili.memory.daily_log(f"Command: {text[:60]} | Handled")
    except Exception as e:
        log.error(f"[ERROR] {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}\nLogged — investigating.")


# ── Start API server in background thread ─────────────────────
def start_api_server():
    try:
        import uvicorn
        from api.server import app as fastapi_app
        uvicorn.run(fastapi_app, host="0.0.0.0", port=8080, log_level="warning")
    except ImportError:
        log.warning("uvicorn not installed — dashboard API not available. pip install fastapi uvicorn")
    except Exception as e:
        log.error(f"API server error: {e}")


# ── Entry point ───────────────────────────────────────────────
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("status",  status_cmd))
    app.add_handler(CommandHandler("pending", pending_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Init Phase 3 modules
    akili.init_phase3(app)

    # Start background tasks
    asyncio.create_task(akili.heartbeat(app))
    asyncio.create_task(akili.live_intel.run())

    if akili.scheduler:
        asyncio.create_task(akili.scheduler.run())

    if akili.responder:
        asyncio.create_task(akili.responder.run())

    # Start API server in background thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()

    log.info("AKILI OS Phase 3 — all systems running")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
