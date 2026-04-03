# ============================================================
# FACEBOOK INTEGRATION — Akili PULSE Agent
# Accounts: Justin Mafie (personal) + CREOVA (business)
# ============================================================

import logging
import aiohttp
import asyncio
from config.accounts import FACEBOOK_ACCOUNTS

log = logging.getLogger("PULSE.Facebook")

BASE_URL = "https://graph.facebook.com/v18.0"


class FacebookClient:

    def __init__(self):
        self.accounts = FACEBOOK_ACCOUNTS
        log.info("Facebook: Justin Mafie personal + CREOVA business")

    def _is_configured(self, key: str) -> bool:
        acc = self.accounts.get(key, {})
        return bool(acc.get("page_id") and acc.get("token"))

    def _get_account(self, key: str) -> dict:
        acc = self.accounts.get(key)
        if not acc:
            raise ValueError(f"Unknown FB account: {key}. Valid: {list(self.accounts.keys())}")
        if not acc["page_id"] or not acc["token"]:
            raise ValueError(f"Missing credentials for {acc['label']} — add to Replit Secrets")
        return acc

    async def post_text(self, account_key: str, message: str) -> dict:
        acc = self._get_account(account_key)
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{BASE_URL}/{acc['page_id']}/feed",
                data={"message": message, "access_token": acc["token"]},
            ) as r:
                data = await r.json()
                if "id" in data:
                    log.info(f"[Facebook] ✅ Posted to {acc['label']}")
                    return {"success": True, "post_id": data["id"], "account": acc["label"]}
                log.error(f"[Facebook] Error for {acc['label']}: {data}")
                return {"error": data, "account": acc["label"]}

    async def post_photo(self, account_key: str, image_url: str, caption: str) -> dict:
        acc = self._get_account(account_key)
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{BASE_URL}/{acc['page_id']}/photos",
                data={"url": image_url, "caption": caption, "access_token": acc["token"]},
            ) as r:
                data = await r.json()
                if "id" in data:
                    log.info(f"[Facebook] ✅ Photo posted to {acc['label']}")
                    return {"success": True, "post_id": data["id"], "account": acc["label"]}
                return {"error": data, "account": acc["label"]}

    async def post_link(self, account_key: str, link: str, message: str) -> dict:
        acc = self._get_account(account_key)
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{BASE_URL}/{acc['page_id']}/feed",
                data={"link": link, "message": message, "access_token": acc["token"]},
            ) as r:
                data = await r.json()
                if "id" in data:
                    log.info(f"[Facebook] ✅ Link post to {acc['label']}")
                    return {"success": True, "post_id": data["id"]}
                return {"error": data}

    async def post_to_both(self, justin_message: str, creova_message: str) -> list:
        results = []
        r1 = await self.post_text("justin_personal", justin_message)
        results.append(r1)
        await asyncio.sleep(5)
        r2 = await self.post_text("creova_business", creova_message)
        results.append(r2)
        return results

    async def get_page_insights(self, account_key: str) -> dict:
        acc = self._get_account(account_key)
        url = (
            f"{BASE_URL}/{acc['page_id']}"
            f"?fields=name,fan_count,followers_count"
            f"&access_token={acc['token']}"
        )
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()
                data["account_label"] = acc["label"]
                return data

    async def format_status(self) -> str:
        lines = ["📘 FACEBOOK STATUS\n"]
        for key, acc in self.accounts.items():
            if not self._is_configured(key):
                lines.append(f"  ⚪ {acc['label']} — not configured (add FB_* secrets)")
                continue
            try:
                insights = await self.get_page_insights(key)
                name = insights.get("name", acc["label"])
                fans = insights.get("fan_count", "N/A")
                followers = insights.get("followers_count", "N/A")
                lines.append(f"  ✅ {name} — {fans} fans · {followers} followers")
            except Exception as e:
                lines.append(f"  ❌ {acc['label']} — {str(e)[:50]}")
        return "\n".join(lines)
