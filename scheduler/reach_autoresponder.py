# ============================================================
# REACH AUTO-RESPONDER — Phase 3B
# Monitors Gmail every 30 min, classifies, auto-replies
# Flags urgent emails to Justin on Telegram instantly
# ============================================================

import asyncio
import html
import logging
import os
from datetime import datetime
from core.ai_client import get_client
from core.outcome_tracker import tracker as outcome_tracker
from config.ai_models import MODEL

log = logging.getLogger("REACH.AutoResponder")

ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
JUSTIN_CHAT_ID = os.environ.get("JUSTIN_CHAT_ID", "")

JUSTIN_VOICE = """You are writing on behalf of Justin Mafie — founder of CREOVA.
VOICE: Direct. Warm. Confident. Never robotic. Real founder energy.
NEVER: "I hope this email finds you well", stiff/formal language, reveal it's automated.
ALWAYS: Sound like Justin, reference CREOVA naturally, clear next step.
Sign as: Justin | CREOVA · creova.one"""

URGENT_KEYWORDS = [
    "investment", "investor", "vc ", "funding", "series a", "term sheet",
    "partnership offer", "media interview", "press", "journalist",
    "legal", "lawsuit", "compliance", "urgent", "time sensitive",
    "board", "acquisition", "due diligence",
]

AUTO_REPLY_STYLES = {
    "fan":      "warm, grateful, personal — thank them, point to music and @creativeinnovation__",
    "collab":   "interested but measured — ask what they're building, mention CREOVA Solutions",
    "business": "professional, direct — what does CREOVA offer them specifically",
    "press":    "media-ready — brief CREOVA story, offer interview scheduling",
    "general":  "friendly, brief — acknowledge and point to creova.one",
}

NO_AUTO_REPLY = ["noreply", "no-reply", "donotreply", "notifications", "mailer-daemon"]


class ReachAutoResponder:
    def __init__(self, telegram_app, gmail_client=None):
        self.app    = telegram_app
        self.gmail  = gmail_client
        self.client = get_client(ANTHROPIC_KEY, "REACH")
        self.replied = set()
        log.info("REACH AutoResponder initialized")

    def _gmail_ready(self) -> bool:
        """Returns True if Gmail client has at least one authenticated service."""
        if not self.gmail:
            return False
        if not hasattr(self.gmail, "get_unread"):
            return False
        # Check if any services are actually authenticated
        if hasattr(self.gmail, "services") and self.gmail.services:
            return True
        # Fallback: env var check
        from config.accounts import EMAIL_ACCOUNTS
        for acc in EMAIL_ACCOUNTS.values():
            if acc.get("address"):
                return True
        return False

    async def run(self):
        if not self._gmail_ready():
            log.info("[REACH] Gmail not connected — auto-responder in standby.")
            return
        while True:
            log.info("[REACH] Checking inboxes...")
            try:
                await self._check_inbox("personal")
                await asyncio.sleep(5)
                await self._check_inbox("business")
            except Exception as e:
                log.error(f"[REACH] Inbox error: {e}")
            await asyncio.sleep(1800)

    async def _check_inbox(self, account: str):
        try:
            emails = await self.gmail.get_unread(account_key=account, max_results=15)
        except Exception as e:
            log.error(f"[REACH] Could not fetch {account} inbox: {e}")
            return

        new_count    = 0
        urgent_count = 0
        auto_replied: list[dict] = []

        for email in emails:
            msg_id = email.get("id", "")
            if msg_id in self.replied:
                continue

            classification = self._classify(email)
            self.replied.add(msg_id)
            new_count += 1

            if classification == "urgent":
                urgent_count += 1
                await self._flag_urgent(email, account)
            else:
                result = await self._auto_reply(email, classification, account)
                if result:
                    auto_replied.append(result)

            await asyncio.sleep(3)

        if new_count > 0:
            log.info(f"[REACH] {account}: {new_count} emails — {urgent_count} urgent")

        # Digest of auto-replies actually sent — one batched message per run
        # instead of zero visibility. This is the audit trail Justin actually sees.
        if auto_replied and self.app and JUSTIN_CHAT_ID:
            inbox = "Personal" if account == "personal" else "CREOVA Business"
            lines = [f"📨 <b>REACH — Auto-Replied ({inbox})</b>", "━━━━━━━━━━━━━━━━━━━━"]
            for r in auto_replied:
                sender  = html.escape(r['sender'][:35])
                preview = html.escape(r['reply_preview'])
                lines.append(
                    f"▸ <code>{r['action_id']}</code> {sender} "
                    f"[{r['classification']}]\n   \"{preview}...\""
                )
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("Wrong tone on any of these? Reply: <code>outcome [id] bad_reply=1</code>")
            try:
                await self.app.bot.send_message(
                    chat_id=JUSTIN_CHAT_ID, text="\n".join(lines), parse_mode="HTML"
                )
            except Exception as e:
                log.error(f"[REACH] Failed to send digest: {e}")

    def _classify(self, email: dict) -> str:
        combined = (
            email.get("subject", "") + " " +
            email.get("snippet", "") + " " +
            email.get("from", "")
        ).lower()
        if any(kw in combined for kw in URGENT_KEYWORDS):
            return "urgent"
        if any(w in combined for w in ["fan", "love your music", "big fan", "love what you do"]):
            return "fan"
        if any(w in combined for w in ["collab", "collaborate", "partnership", "work together"]):
            return "collab"
        if any(w in combined for w in ["interview", "journalist", "media", "press"]):
            return "press"
        if any(w in combined for w in ["invoice", "payment", "proposal", "quote", "hire"]):
            return "business"
        return "general"

    async def _flag_urgent(self, email: dict, account: str):
        sender  = email.get("from", "Unknown")
        subject = email.get("subject", "No subject")
        snippet = email.get("snippet", "")[:200]
        inbox   = "Personal" if account == "personal" else "CREOVA Business"

        msg = (
            f"🚨 <b>REACH — URGENT EMAIL</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Inbox:</b> {inbox}\n"
            f"👤 <b>From:</b> <code>{sender}</code>\n"
            f"📌 <b>Subject:</b> {subject}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>{snippet}</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Needs YOUR reply — not auto-handled.\n"
            f"Send: <code>DRAFT REPLY [summary]</code> to draft one."
        )
        await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=msg, parse_mode="HTML")

    async def _auto_reply(self, email: dict, classification: str, account: str) -> dict | None:
        """Sends the auto-reply and logs it as a sensed action. Returns a dict
        with sender/classification/action_id/reply_preview for the caller to
        surface to Justin — this is the audit trail for the one path in AKILI
        that sends real outbound communication with no human in the loop."""
        sender  = email.get("from", "")
        subject = email.get("subject", "")
        body    = email.get("body", email.get("snippet", ""))[:400]
        msg_id  = email.get("id", "")

        if any(w in sender.lower() for w in NO_AUTO_REPLY):
            return None

        style  = AUTO_REPLY_STYLES.get(classification, AUTO_REPLY_STYLES["general"])
        prompt = f"""Write a reply email for Justin Mafie.
From: {sender}
Subject: {subject}
Message: {body}
Classification: {classification}
Style: {style}
Write ONLY the email body, under 120 words. Sign as: Justin | CREOVA · creova.one"""

        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=300,
                system=JUSTIN_VOICE,
                messages=[{"role": "user", "content": prompt}]
            )
            reply_body = response.content[0].text.strip()

            if hasattr(self.gmail, 'send_email'):
                await self.gmail.send_email(
                    to=sender,
                    subject=f"Re: {subject}",
                    body=reply_body,
                    account=account,
                    reply_to_id=msg_id,
                )
                action_id = await outcome_tracker.log_action(
                    "REACH", "auto_reply_email",
                    summary=f"Replied to {sender[:50]} ({classification})",
                    metadata={"account": account, "sender": sender, "subject": subject,
                              "classification": classification, "reply_body": reply_body},
                )
                log.info(f"[REACH] Auto-replied to {sender[:40]} ({classification}) — action {action_id}")
                return {"sender": sender, "classification": classification,
                        "action_id": action_id, "reply_preview": reply_body[:100]}
        except Exception as e:
            log.error(f"[REACH] Auto-reply error: {e}")
        return None

    async def draft_reply(self, context: str) -> str:
        prompt = f"""Justin needs to reply to: {context}
Write a complete email reply from Justin Mafie. Under 150 words.
Sign as: Justin | CREOVA · creova.one
Return ONLY the email body."""
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=400,
                system=JUSTIN_VOICE,
                messages=[{"role": "user", "content": prompt}]
            )
            draft = response.content[0].text.strip()
            return f"📨 REACH — Draft reply:\n\n{draft}\n\n✏️ Edit and send yourself, or copy into Gmail."
        except Exception as e:
            log.error(f"[REACH] Draft reply error: {e}")
            return f"⚠️ REACH Error: {e}"

    async def repurpose(self, original: str, source: str = "original") -> str:
        prompt = f"""Original content from {source}:
{original}

Repurpose into ALL 5 platforms:
1. Instagram caption + hashtags (150 chars + 8-10 tags)
2. Twitter/X (260 chars max, 2-3 hashtags)
3. LinkedIn (professional, 100-150 words)
4. TikTok caption + video concept in [brackets]
5. Facebook (casual, 80-100 words)

Justin's voice throughout. Cross-mention CREOVA handles naturally in each."""
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1200,
                system=JUSTIN_VOICE,
                messages=[{"role": "user", "content": prompt}]
            )
            return f"♻️ REACH — Repurposed:\n\n{response.content[0].text}"
        except Exception as e:
            log.error(f"[REACH] Repurpose error: {e}")
            return f"⚠️ REACH Error: {e}"
