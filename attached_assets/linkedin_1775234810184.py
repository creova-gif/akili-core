# ============================================================
# LINKEDIN INTEGRATION — Akili PULSE Agent
# Accounts: Justin Mafie (personal) + CREOVA (company page)
# ============================================================

import logging
import aiohttp
import asyncio
import base64
from config.accounts import LINKEDIN_ACCOUNTS

log = logging.getLogger("PULSE.LinkedIn")

BASE_URL = "https://api.linkedin.com/v2"

ACCOUNT_VOICE = {
    "justin_mafie": {
        "tone": "Founder. Visionary. Personal insights from building CREOVA.",
        "sign_off": "\n\n— Justin Mafie | Founder, CREOVA\n🌍 creova.one",
        "hashtags": "#JustinMafie #CREOVA #AfricanFounder #Entrepreneurship #MusicAndTech #BuildingInAfrica",
    },
    "creova_page": {
        "tone": "Professional. Innovative. Emerging markets tech leader.",
        "sign_off": "\n\n📌 Learn more: creova.one\n@creovasolutions",
        "hashtags": "#CREOVASolutions #AfricanTech #EmergingMarkets #GlobalTech #Innovation #StartupAfrica",
    },
}


class LinkedInClient:

    def __init__(self):
        self.accounts = LINKEDIN_ACCOUNTS
        self.token = LINKEDIN_ACCOUNTS["justin_mafie"]["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        log.info("LinkedIn: Justin Mafie personal + CREOVA company page")

    def _build_post_payload(self, author_urn: str, text: str) -> dict:
        return {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

    async def post_text(self, account_key: str, text: str) -> dict:
        """Post a text update. account_key: 'justin_mafie' or 'creova_page'"""
        acc = self.accounts.get(account_key)
        if not acc:
            return {"error": f"Unknown LinkedIn account: {account_key}"}
        if not acc["urn"] or not acc["token"]:
            return {"error": f"Missing credentials for {acc['label']} — add to Replit Secrets"}

        # Append voice/hashtags
        voice = ACCOUNT_VOICE.get(account_key, {})
        full_text = f"{text}{voice.get('sign_off', '')}\n\n{voice.get('hashtags', '')}"

        payload = self._build_post_payload(acc["urn"], full_text)

        async with aiohttp.ClientSession() as s:
            async with s.post(f"{BASE_URL}/ugcPosts", json=payload, headers=self.headers) as r:
                if r.status in (200, 201):
                    data = await r.json()
                    log.info(f"[LinkedIn] ✅ Posted as {acc['label']}")
                    return {"success": True, "post_id": data.get("id"), "account": acc["label"]}
                err = await r.text()
                log.error(f"[LinkedIn] Post error ({r.status}): {err}")
                return {"error": err, "status": r.status}

    async def post_to_both(self, justin_text: str, creova_text: str) -> list:
        """
        Coordinated post to both accounts.
        Different copy — Justin's personal take + CREOVA professional angle.
        """
        results = []
        r1 = await self.post_text("justin_mafie", justin_text)
        results.append(r1)
        await asyncio.sleep(5)
        r2 = await self.post_text("creova_page", creova_text)
        results.append(r2)
        log.info("[LinkedIn] ✅ Dual post — Justin Mafie + CREOVA page")
        return results

    async def get_profile(self) -> dict:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{BASE_URL}/me?projection=(id,firstName,lastName,numConnections)",
                headers=self.headers
            ) as r:
                if r.status == 200:
                    return await r.json()
                return {"error": f"HTTP {r.status}"}

    def build_thought_leadership_post(self, topic: str, insight: str, lesson: str) -> str:
        """
        Build a LinkedIn long-form post in Justin's voice.
        topic: "Building fintech in Tanzania"
        insight: "Most founders ignore local payment rails..."
        lesson: "Here's what I learned building GoPay..."
        """
        return (
            f"🌍 {topic}\n\n"
            f"{insight}\n\n"
            f"{lesson}\n\n"
            f"This is what building CREOVA taught me.\n\n"
            f"If you're building in Africa or emerging markets — follow along."
        )

    async def format_status(self) -> str:
        profile = await self.get_profile()
        if "error" not in profile:
            name = f"{profile.get('firstName', {}).get('localized', {}).get('en_US', '')} {profile.get('lastName', {}).get('localized', {}).get('en_US', '')}"
            return f"💼 LINKEDIN STATUS\n  ✅ {name} (personal) + CREOVA page — connected"
        return f"💼 LINKEDIN — ❌ {profile.get('error', 'Not connected')}"
