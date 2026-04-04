# ============================================================
# REACH AUTO-RESPONDER — Phase 3B
# Monitors Gmail every 30 min, classifies, auto-replies
# Flags urgent emails to Justin on Telegram instantly
# ============================================================

import asyncio
import logging
import os
from datetime import datetime
from anthropic import Anthropic

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
        self.client = Anthropic(api_key=ANTHROPIC_KEY)
        self.replied = set()
        log.info("REACH AutoResponder initialized")

    def _gmail_ready(self) -> bool:
        """Returns True only if Gmail is configured AND has a get_unread method."""
        if not self.gmail:
            return False
        if not os.environ.get("GMAIL_PERSONAL_ADDRESS"):
            return False
        if not hasattr(self.gmail, "get_unread"):
            return False
        return True

    async def run(self):
        if not self._gmail_ready():
            log.info("[REACH] Gmail not fully configured — auto-responder in standby. "
                     "Add GMAIL_PERSONAL_ADDRESS + GMAIL_BUSINESS_ADDRESS secrets to activate.")
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
            emails = await self.gmail.get_unread(account=account, max_results=15)
        except Exception as e:
            log.error(f"[REACH] Could not fetch {account} inbox: {e}")
            return

        new_count    = 0
        urgent_count = 0

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
                await self._auto_reply(email, classification, account)

            await asyncio.sleep(3)

        if new_count > 0:
            log.info(f"[REACH] {account}: {new_count} emails — {urgent_count} urgent")

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
            f"🚨 REACH — URGENT EMAIL\n\n"
            f"Inbox: {inbox}\n"
            f"From: {sender}\n"
            f"Subject: {subject}\n\n"
            f"Preview:\n{snippet}\n\n"
            f"⚡ Needs YOUR reply. Send: DRAFT REPLY [summary] to draft one."
        )
        await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=msg)

    async def _auto_reply(self, email: dict, classification: str, account: str):
        sender  = email.get("from", "")
        subject = email.get("subject", "")
        body    = email.get("body", email.get("snippet", ""))[:400]
        msg_id  = email.get("id", "")

        if any(w in sender.lower() for w in NO_AUTO_REPLY):
            return

        style  = AUTO_REPLY_STYLES.get(classification, AUTO_REPLY_STYLES["general"])
        prompt = f"""Write a reply email for Justin Mafie.
From: {sender}
Subject: {subject}
Message: {body}
Classification: {classification}
Style: {style}
Write ONLY the email body, under 120 words. Sign as: Justin | CREOVA · creova.one"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
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
                log.info(f"[REACH] Auto-replied to {sender[:40]} ({classification})")
        except Exception as e:
            log.error(f"[REACH] Auto-reply error: {e}")

    async def draft_reply(self, context: str) -> str:
        prompt = f"""Justin needs to reply to: {context}
Write a complete email reply from Justin Mafie. Under 150 words.
Sign as: Justin | CREOVA · creova.one
Return ONLY the email body."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            system=JUSTIN_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )
        draft = response.content[0].text.strip()
        return f"📨 REACH — Draft reply:\n\n{draft}\n\n✏️ Edit and send yourself, or copy into Gmail."

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
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1200,
            system=JUSTIN_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"♻️ REACH — Repurposed:\n\n{response.content[0].text}"
