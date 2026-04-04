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

ANTHROPIC_KEY  = os.environ["ANTHROPIC_API_KEY"]
JUSTIN_CHAT_ID = os.environ["JUSTIN_CHAT_ID"]

# ── Justin's voice for all auto-replies ──────────────────────
JUSTIN_VOICE = """
You are writing replies on behalf of Justin Mafie — founder of CREOVA.

VOICE: Direct. Warm. Confident. Never robotic. Never corporate.
Real Justin energy — like texting a smart, busy founder who cares.

NEVER:
- Use "I hope this email finds you well"
- Sound stiff or overly formal
- Promise things Justin hasn't confirmed
- Reveal that this is automated

ALWAYS:
- Sound like Justin wrote it himself
- Reference CREOVA naturally
- End with a clear next step
- Sign as: Justin | CREOVA · creova.one

CREOVA HANDLES TO REFERENCE:
- creova.one (main website)
- @creovasolutions (tech company)
- @creativeinnovation__ (music)
- @justin_mafie (Twitter/X)
"""

# ── Classification rules ──────────────────────────────────────
URGENT_KEYWORDS = [
    "investment", "investor", "vc ", "funding", "series a", "term sheet",
    "partnership offer", "media interview", "press", "journalist",
    "legal", "lawsuit", "compliance", "urgent", "time sensitive",
    "board", "acquisition", "due diligence",
]

AUTO_REPLY_TYPES = {
    "fan":      "warm, grateful, personal — thank them, point to music",
    "collab":   "interested but measured — ask what they're building",
    "business": "professional, direct — what does CREOVA offer them",
    "press":    "media-ready — brief CREOVA story, offer interview scheduling",
    "general":  "friendly, brief — acknowledge and point to creova.one",
}

# Emails that should NEVER get auto-replied (only flagged)
NEVER_AUTO_REPLY = ["urgent", "legal", "vc", "investment", "acquisition"]


class ReachAutoResponder:
    """
    Runs every 30 minutes alongside main.py.
    Checks both Gmail inboxes, classifies every unread email,
    auto-replies to non-urgent ones, instantly flags urgent ones.
    """

    def __init__(self, telegram_app, gmail_client):
        self.app     = telegram_app
        self.gmail   = gmail_client
        self.client  = Anthropic(api_key=ANTHROPIC_KEY)
        self.replied  = set()   # Track message IDs already handled
        log.info("REACH AutoResponder initialized")

    # ── Main loop ─────────────────────────────────────────────
    async def run(self):
        """Check inboxes every 30 minutes."""
        while True:
            log.info("[REACH] Checking inboxes...")
            try:
                await self._check_inbox("personal")
                await asyncio.sleep(5)
                await self._check_inbox("business")
            except Exception as e:
                log.error(f"[REACH] Inbox check error: {e}")
            await asyncio.sleep(1800)   # 30 minutes

    # ── Check one inbox ───────────────────────────────────────
    async def _check_inbox(self, account: str):
        emails = await self.gmail.get_unread(account=account, max_results=15)

        new_count  = 0
        urgent_count = 0

        for email in emails:
            msg_id = email.get("id", "")
            if msg_id in self.replied:
                continue   # Already handled

            classification = self.gmail.classify_email(email)
            self.replied.add(msg_id)
            new_count += 1

            if classification == "urgent":
                urgent_count += 1
                await self._flag_urgent(email, account)
            else:
                await self._auto_reply(email, classification, account)
                await self.gmail.mark_read(msg_id, account=account)

            await asyncio.sleep(3)   # Avoid rate limits between replies

        if new_count > 0:
            log.info(f"[REACH] {account}: {new_count} new emails — {urgent_count} urgent")

    # ── Flag urgent to Telegram ───────────────────────────────
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
            f"⚡ This needs YOUR reply — not auto-handled.\n"
            f"Reply to Akili: DRAFT REPLY [email summary] to draft one for you."
        )
        await self.app.bot.send_message(chat_id=JUSTIN_CHAT_ID, text=msg)
        log.info(f"[REACH] Urgent flagged: {subject[:50]}")

    # ── Auto-reply to non-urgent emails ───────────────────────
    async def _auto_reply(self, email: dict, classification: str, account: str):
        sender  = email.get("from", "")
        subject = email.get("subject", "")
        body    = email.get("body", "")[:400]
        msg_id  = email.get("id", "")

        # Don't auto-reply to no-reply addresses
        if any(w in sender.lower() for w in ["noreply", "no-reply", "donotreply", "notifications", "mailer-daemon"]):
            return

        reply_style = AUTO_REPLY_TYPES.get(classification, AUTO_REPLY_TYPES["general"])

        prompt = f"""
Write a reply email for Justin Mafie.

Original email:
From: {sender}
Subject: {subject}
Message: {body}

Classification: {classification}
Reply style: {reply_style}

Write ONLY the email body — no subject line.
Keep it under 120 words. Sound like Justin wrote it himself.
End with: Justin | CREOVA · creova.one
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                system=JUSTIN_VOICE,
                messages=[{"role": "user", "content": prompt}]
            )
            reply_body = response.content[0].text.strip()

            # Send the reply
            result = await self.gmail.send_email(
                to=sender,
                subject=f"Re: {subject}",
                body=reply_body,
                account=account,
                reply_to_id=msg_id,
            )

            if result.get("success"):
                log.info(f"[REACH] Auto-replied to {sender[:40]} ({classification})")
                # Silently log — don't spam Justin's Telegram for every reply
            else:
                log.error(f"[REACH] Reply failed: {result.get('error')}")

        except Exception as e:
            log.error(f"[REACH] Auto-reply error: {e}")

    # ── Draft a reply on Justin's command ─────────────────────
    async def draft_reply(self, context: str) -> str:
        """Justin says: DRAFT REPLY [context] — Akili drafts it."""
        prompt = f"""
Justin needs to reply to this situation: {context}

Write a complete email reply from Justin Mafie.
Professional but real. Under 150 words.
Sign as: Justin | CREOVA · creova.one

Return ONLY the email body.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            system=JUSTIN_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )
        draft = response.content[0].text.strip()
        return f"📨 REACH — Draft reply:\n\n{draft}\n\n✏️ Reply SENDDRAFT to send this, or edit and send yourself."

    # ── DM auto-reply generator ───────────────────────────────
    async def generate_dm_reply(self, platform: str, message: str, sender_type: str = "fan") -> str:
        """Generate a DM reply in Justin's voice for any platform."""
        style = AUTO_REPLY_TYPES.get(sender_type, AUTO_REPLY_TYPES["general"])
        prompt = f"""
Platform: {platform}
Someone sent: "{message}"
They are: {sender_type}
Reply style: {style}

Write a short, genuine reply from Justin Mafie.
Max 2-3 sentences. Real energy. No corporate speak.
Platform-appropriate length ({platform} = {'short' if platform in ['twitter','instagram'] else 'medium'}).
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=150,
            system=JUSTIN_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    # ── Repurpose content ─────────────────────────────────────
    async def repurpose(self, original: str, source: str) -> str:
        """Take one piece of content and reformat it for all platforms."""
        prompt = f"""
Original content from {source}:
{original}

Repurpose into:
1. Instagram caption + hashtags (150 chars + tags)
2. Twitter/X (260 chars max, 2-3 hashtags)
3. LinkedIn (professional, 100-150 words)
4. TikTok caption + video concept in [brackets]
5. Facebook (casual, 80-100 words)

Format clearly by platform. Justin's voice throughout.
Cross-mention CREOVA handles naturally in each.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1200,
            system=JUSTIN_VOICE,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"♻️ REACH — Repurposed content:\n\n{response.content[0].text}"
