# ============================================================
# INSTAGRAM INTEGRATION — Akili PULSE Agent
# Accounts: @creativeinnovation__ · @jj_mafie
#           @sankofastudio__ · @creovasolutions
# ============================================================

import logging
import aiohttp
import asyncio
from config.accounts import INSTAGRAM_ACCOUNTS, CREOVA_WEBSITE

log = logging.getLogger("PULSE.Instagram")

BASE_URL = "https://graph.facebook.com/v18.0"

ACCOUNT_VOICE = {
    "creativeinnovation": {
        "tone": "Music-first. Creative. Energetic. African futurism aesthetic.",
        "hashtags": "#CREOVAMusic #AfricanMusic #JustinMafie #NewMusic #CreativeInnovation #StudioLife #SankofaStudio",
        "cta": "🎵 Stream now — link in bio | @sankofastudio__",
    },
    "jj_mafie": {
        "tone": "Personal. Real. Founder journey. Music meets tech.",
        "hashtags": "#JustinMafie #CREOVA #FounderLife #AfricanFounder #MusicAndTech #CreativeTech",
        "cta": "🌍 Building CREOVA — creova.one | @creovasolutions",
    },
    "sankofastudio": {
        "tone": "Studio culture. Production process. Raw and authentic.",
        "hashtags": "#SankofaStudio #StudioSession #MusicProduction #CREOVA #BehindTheBeats #Recording",
        "cta": "🎙️ Book a session | @creativeinnovation__",
    },
    "creovasolutions": {
        "tone": "Professional. Visionary. Global tech with African roots.",
        "hashtags": "#CREOVASolutions #AfricanTech #EmergingMarkets #TechInnovation #StartupAfrica #GlobalTech",
        "cta": "💡 Explore our solutions — creova.one",
    },
}


class InstagramClient:

    def __init__(self):
        self.accounts = INSTAGRAM_ACCOUNTS
        log.info("Instagram: @creativeinnovation__ · @jj_mafie · @sankofastudio__ · @creovasolutions")

    def _is_configured(self, key: str) -> bool:
        acc = self.accounts.get(key, {})
        return bool(acc.get("ig_user_id") and acc.get("token"))

    def _get_account(self, key: str) -> dict:
        acc = self.accounts.get(key)
        if not acc:
            raise ValueError(f"Unknown Instagram account: '{key}'. Valid: {list(self.accounts.keys())}")
        if not acc["ig_user_id"] or not acc["token"]:
            raise ValueError(f"Missing credentials for {acc['handle']} — add to Replit Secrets")
        return acc

    async def post_photo(self, account_key: str, image_url: str, caption: str) -> dict:
        """Post a photo. image_url must be publicly accessible."""
        acc = self._get_account(account_key)
        uid, tok = acc["ig_user_id"], acc["token"]

        async with aiohttp.ClientSession() as s:
            async with s.post(f"{BASE_URL}/{uid}/media", data={
                "image_url": image_url, "caption": caption, "access_token": tok,
            }) as r:
                body = await r.json()
                if "error" in body:
                    log.error(f"[IG] Container error ({acc['handle']}): {body['error']}")
                    return {"error": body["error"], "account": acc["handle"]}
                creation_id = body["id"]

            async with s.post(f"{BASE_URL}/{uid}/media_publish", data={
                "creation_id": creation_id, "access_token": tok,
            }) as r:
                result = await r.json()
                if "id" in result:
                    log.info(f"[IG] ✅ Posted to {acc['handle']} — {result['id']}")
                    return {"success": True, "post_id": result["id"], "account": acc["handle"]}
                return {"error": result, "account": acc["handle"]}

    async def post_reel(self, account_key: str, video_url: str, caption: str) -> dict:
        """Post a Reel (video)."""
        acc = self._get_account(account_key)
        uid, tok = acc["ig_user_id"], acc["token"]

        async with aiohttp.ClientSession() as s:
            async with s.post(f"{BASE_URL}/{uid}/media", data={
                "media_type": "REELS", "video_url": video_url,
                "caption": caption, "access_token": tok,
            }) as r:
                body = await r.json()
                if "error" in body:
                    return {"error": body["error"], "account": acc["handle"]}
                creation_id = body["id"]

            for _ in range(12):
                await asyncio.sleep(15)
                async with s.get(
                    f"{BASE_URL}/{creation_id}?fields=status_code&access_token={tok}"
                ) as r:
                    st = await r.json()
                    if st.get("status_code") == "FINISHED":
                        break

            async with s.post(f"{BASE_URL}/{uid}/media_publish", data={
                "creation_id": creation_id, "access_token": tok,
            }) as r:
                result = await r.json()
                if "id" in result:
                    log.info(f"[IG] ✅ Reel posted to {acc['handle']}")
                    return {"success": True, "post_id": result["id"], "account": acc["handle"]}
                return {"error": result, "account": acc["handle"]}

    async def post_story(self, account_key: str, image_url: str) -> dict:
        """Post a Story."""
        acc = self._get_account(account_key)
        uid, tok = acc["ig_user_id"], acc["token"]

        async with aiohttp.ClientSession() as s:
            async with s.post(f"{BASE_URL}/{uid}/media", data={
                "image_url": image_url, "media_type": "STORIES", "access_token": tok,
            }) as r:
                body = await r.json()
                if "error" in body:
                    return {"error": body["error"], "account": acc["handle"]}
                creation_id = body["id"]

            async with s.post(f"{BASE_URL}/{uid}/media_publish", data={
                "creation_id": creation_id, "access_token": tok,
            }) as r:
                result = await r.json()
                if "id" in result:
                    log.info(f"[IG] ✅ Story posted to {acc['handle']}")
                    return {"success": True, "account": acc["handle"]}
                return {"error": result, "account": acc["handle"]}

    async def get_insights(self, account_key: str) -> dict:
        """Get follower count and media count."""
        acc = self._get_account(account_key)
        uid, tok = acc["ig_user_id"], acc["token"]
        url = f"{BASE_URL}/{uid}?fields=followers_count,media_count,biography&access_token={tok}"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()
                data["handle"] = acc["handle"]
                return data

    async def get_all_insights(self) -> list:
        """Insights for all 4 accounts."""
        results = []
        for key in self.accounts:
            if not self._is_configured(key):
                results.append({"handle": self.accounts[key]["handle"], "error": "Not configured"})
                continue
            try:
                insight = await self.get_insights(key)
                results.append(insight)
            except Exception as e:
                results.append({"handle": self.accounts[key]["handle"], "error": str(e)})
        return results

    def build_caption(self, account_key: str, core_message: str, include_cta: bool = True) -> str:
        """Build a complete branded caption for a specific account."""
        voice = ACCOUNT_VOICE.get(account_key, {})
        hashtags = voice.get("hashtags", "#CREOVA #JustinMafie")
        cta = voice.get("cta", f"🌍 {CREOVA_WEBSITE}") if include_cta else ""
        return f"{core_message}\n\n{cta}\n\n{hashtags}"

    async def coordinated_drop(self, image_url: str, messages: dict) -> list:
        """Post same image to multiple accounts with different captions."""
        results = []
        for account_key, message in messages.items():
            caption = self.build_caption(account_key, message)
            result = await self.post_photo(account_key, image_url, caption)
            results.append(result)
            await asyncio.sleep(8)
        return results

    async def format_status(self) -> str:
        lines = ["📸 INSTAGRAM STATUS\n"]
        for key, acc in self.accounts.items():
            if not self._is_configured(key):
                lines.append(f"  ⚪ {acc['handle']} — not configured (add secrets)")
                continue
            try:
                insight = await self.get_insights(key)
                followers = insight.get("followers_count", "N/A")
                posts = insight.get("media_count", "N/A")
                err = insight.get("error", "")
                if err:
                    lines.append(f"  ❌ {acc['handle']} — {err}")
                else:
                    lines.append(f"  ✅ {acc['handle']} — {followers} followers · {posts} posts")
            except Exception as e:
                lines.append(f"  ❌ {acc['handle']} — {str(e)[:60]}")
        return "\n".join(lines)
