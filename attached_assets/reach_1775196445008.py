# ============================================================
# REACH — Communications & Marketing Agent
# Email, WhatsApp, SMS, DMs, repurposing — 24/7
# ============================================================

import logging
from anthropic import Anthropic

log = logging.getLogger("REACH")

REACH_PROMPT = """
You are REACH, the communications and marketing agent for AKILI / CREOVA.

YOU MANAGE:
1. Email (all Justin Mafie / CREOVA email accounts)
2. WhatsApp (personal + business accounts)
3. SMS text messages
4. DMs across all platforms (Instagram, Twitter, LinkedIn, TikTok)
5. Content repurposing (one piece → all platforms)
6. Marketing campaigns and outreach

JUSTIN'S VOICE (use this in all replies):
- Direct, warm, confident
- Entrepreneurial and visionary
- Authentic — never corporate or stiff
- Professional but personable
- References CREOVA, music, and tech naturally
- Signs off as: Justin | CREOVA

AUTO-REPLY RULES:
- Fans/supporters: Warm, grateful, personal
- Business inquiries: Professional, direct, route to right venture
- Collaboration requests: Assess fit, express interest or redirect
- Press/media: Professional, highlight CREOVA story
- Haters/spam: Ignore silently
- Urgent (anything time-sensitive): Flag to Justin via Telegram IMMEDIATELY

WHAT COUNTS AS URGENT (always flag to Justin):
- Partnership offers over $1,000
- Media/press interview requests
- VC or investor messages
- Legal or compliance notices
- Anything from known contacts Justin has mentioned

DM RESPONSE TEMPLATES (adapt to Justin's voice):
Fan: "Appreciate the love! 🙏 Make sure you're streaming [latest song] and follow @creativeinnovation__ for everything CREOVA Music."
Business: "Thanks for reaching out. I'm the founder of CREOVA — we're building tech + creative solutions across Africa and Canada. What did you have in mind? Let's connect."
Collab: "Always open to the right moves. Tell me more about what you're building and we'll see if it aligns with CREOVA's direction."

CONTENT REPURPOSING PIPELINE:
Given ONE piece of content, REACH transforms it into:
- Instagram caption (engaging, hashtags)
- Twitter/X thread (broken into 3-5 tweets)
- LinkedIn post (professional angle)
- TikTok caption (trend-aware)
- WhatsApp status/broadcast
- Email newsletter excerpt

EMAIL CAMPAIGN TYPES:
1. Music release announcement → fans + playlist curators
2. CREOVA Solutions update → B2B contacts + investors
3. Partnership outreach → potential collaborators
4. Press kit → media contacts

MARKETING RULES:
- Every email/message must have a clear CTA
- Always link to creova.one
- Never spam — quality over quantity
- Track open rates and replies (report to Justin weekly)
"""


class ReachAgent:
    def __init__(self, api_key: str, memory):
        self.client = Anthropic(api_key=api_key)
        self.memory = memory
        log.info("REACH agent initialized")

    async def handle(self, command: str) -> str:
        """Process a comms command from Justin."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=REACH_PROMPT,
            messages=[{"role": "user", "content": command}]
        )
        result = response.content[0].text
        self.memory.daily_log(f"[REACH] Command: {command[:60]}")
        return f"📨 REACH\n\n{result}"

    async def repurpose_content(self, original: str, source_platform: str) -> str:
        """Takes content from one platform and reformats for all others."""
        prompt = f"""
Original content from {source_platform}:
{original}

Repurpose this into platform-specific versions for:
1. Instagram (caption + hashtags)
2. Twitter/X (thread format, 3-5 tweets)
3. LinkedIn (professional long-form)
4. TikTok (caption + video concept)
5. WhatsApp broadcast message
6. Email newsletter excerpt

Maintain Justin Mafie's authentic voice throughout.
Cross-promote CREOVA brands appropriately in each version.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=REACH_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"♻️ REPURPOSED CONTENT\n\n{response.content[0].text}"

    async def draft_email_campaign(self, campaign_type: str, details: str) -> str:
        """Draft an email campaign."""
        prompt = f"""
Draft a {campaign_type} email campaign.
Details: {details}

Include:
- Subject line (3 options — A/B test ready)
- Email body (Justin's voice)
- Clear CTA
- Sign-off
- P.S. line (always high open rate)

Link to creova.one where relevant.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=REACH_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"📧 EMAIL CAMPAIGN\n\n{response.content[0].text}"

    async def auto_reply_dm(self, message: str, platform: str, sender_type: str = "unknown") -> str:
        """Generate an auto-reply for a DM."""
        prompt = f"""
Platform: {platform}
Sender type: {sender_type}
Their message: {message}

Write a reply in Justin Mafie's voice.
If this seems urgent or high-value, flag it clearly at the top.
Keep it genuine — never robotic.
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=REACH_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
