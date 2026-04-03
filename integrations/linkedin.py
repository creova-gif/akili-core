# ============================================================
# LINKEDIN INTEGRATION — Akili PULSE Agent
# Accounts: Justin Mafie (personal) + CREOVA (company page)
# ============================================================

import logging
import aiohttp
import asyncio
from config.accounts import LINKEDIN_ACCOUNTS

log = logging.getLogger("PULSE.LinkedIn")

BASE_URL = "https://api.linkedin.com/v2"

ACCOUNT_VOICE = {
    "justin_mafie": {
        "sign_off": "\n\n— Justin Mafie | Founder, CREOVA\n🌍 creova.one",
        "hashtags": "#JustinMafie #CREOVA #AfricanFounder #Entrepreneurship #MusicAndTech #BuildingInAfrica",
    },
    "creova_page": {
        "sign_off": "\n\n📌 Learn more: creova.one\n@creovasolutions",
        "hashtags": "#CREOVASolutions #AfricanTech #EmergingMarkets #GlobalTech #Innovation #StartupAfrica",
    },
}


class LinkedInClient:

    def __init__(self):
        self.accounts = LINKEDIN_ACCOUNTS
        self.token = LINKEDIN_ACCOUNTS["justin_mafie"]["token"]
        log.info("LinkedIn: Justin Mafie personal + CREOVA company page")

    def _is_configured(self) -> bool:
        return bool(self.token)

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

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

    async def post_to_both(self, justin_text: str, creova_text: str) -> list:
        results = []
        r1 = await self.post_text("justin_mafie", justin_text)
        results.append(r1)
        await asyncio.sleep(5)
        r2 = await self.post_text("creova_page", creova_text)
        results.append(r2)
        return results

    async def get_member_urn(self) -> str:
        """Fetch member URN via /v2/userinfo (requires openid scope)."""
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{BASE_URL}/userinfo", headers=self._headers) as r:
                if r.status == 200:
                    data = await r.json()
                    return f"urn:li:person:{data['sub']}"
                return ""

    async def get_profile(self) -> dict:
        if not self._is_configured():
            return {"error": "Not configured"}
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{BASE_URL}/userinfo", headers=self._headers) as r:
                if r.status == 200:
                    data = await r.json()
                    return {
                        "name": data.get("name", ""),
                        "given_name": data.get("given_name", ""),
                        "family_name": data.get("family_name", ""),
                        "email": data.get("email", ""),
                        "sub": data.get("sub", ""),
                    }
                return {"error": f"HTTP {r.status}"}

    async def post_text(self, account_key: str, text: str) -> dict:
        if not self._is_configured():
            return {"error": "LinkedIn not configured — add LINKEDIN_* secrets"}
        acc = self.accounts.get(account_key)
        if not acc:
            return {"error": f"Unknown LinkedIn account: {account_key}"}

        # For personal account, resolve URN dynamically from userinfo
        author_urn = acc["urn"]
        if account_key == "justin_mafie" and not author_urn:
            author_urn = await self.get_member_urn()
        if not author_urn:
            return {"error": f"Missing URN for {acc['label']} — cannot post"}

        voice = ACCOUNT_VOICE.get(account_key, {})
        full_text = f"{text}{voice.get('sign_off', '')}\n\n{voice.get('hashtags', '')}"
        payload = self._build_post_payload(author_urn, full_text)

        async with aiohttp.ClientSession() as s:
            async with s.post(f"{BASE_URL}/ugcPosts", json=payload, headers=self._headers) as r:
                if r.status in (200, 201):
                    data = await r.json()
                    log.info(f"[LinkedIn] ✅ Posted as {acc['label']}")
                    return {"success": True, "post_id": data.get("id"), "account": acc["label"]}
                err = await r.text()
                log.error(f"[LinkedIn] Post error ({r.status}): {err}")
                return {"error": err, "status": r.status}

    def build_thought_leadership_post(self, topic: str, insight: str, lesson: str) -> str:
        return (
            f"🌍 {topic}\n\n"
            f"{insight}\n\n"
            f"{lesson}\n\n"
            f"This is what building CREOVA taught me.\n\n"
            f"If you're building in Africa or emerging markets — follow along."
        )

    async def format_status(self) -> str:
        if not self._is_configured():
            return "💼 LINKEDIN — ⚪ Not configured (add LINKEDIN_* secrets)"
        profile = await self.get_profile()
        if "error" not in profile:
            name = profile.get("name", "Justin Mafie")
            company_urn = self.accounts["creova_page"]["urn"]
            company_ok = "✅ CREOVA page" if company_urn else "⚠️ CREOVA page missing URN"
            return f"💼 LINKEDIN STATUS\n  ✅ {name} (personal) + {company_ok} — connected"
        return f"💼 LINKEDIN — ❌ {profile.get('error', 'Not connected')}"
