# ============================================================
# TIKTOK INTEGRATION — Akili PULSE Agent
# Account: @creovamusic
# ============================================================

import logging
import aiohttp
import asyncio
from datetime import datetime
from config.accounts import TIKTOK_ACCOUNT, MUSIC_CONFIG

log = logging.getLogger("PULSE.TikTok")

BASE_URL = "https://open.tiktokapis.com/v2"

# Content strategy for @creovamusic
TIKTOK_CONTENT_TYPES = {
    "music_snippet": {
        "description": "15-30 second unreleased music preview",
        "hashtags": "#CREOVAMusic #NewMusic #JustinMafie #AfricanMusic #SankofaStudio #MusicProducer",
        "hook": "Drop everything 🎵",
    },
    "studio_session": {
        "description": "Studio process — beat making, recording, mixing",
        "hashtags": "#StudioSession #BehindTheBeats #MusicProduction #SankofaStudio #CREOVA",
        "hook": "Inside the studio at @sankofastudio__ 🎙️",
    },
    "founder_music": {
        "description": "The crossover — founder who makes music",
        "hashtags": "#FounderWhoMakesMusic #CREOVA #JustinMafie #AfricanFounder #MusicAndTech",
        "hook": "CEO by day. Producer by night. 🌍",
    },
    "trending_audio": {
        "description": "CREOVA content on trending TikTok audio",
        "hashtags": "#CREOVA #CREOVAMusic #fyp #foryoupage #JustinMafie",
        "hook": "CREOVA on the trending sounds 🔥",
    },
    "music_release": {
        "description": "New music announcement and push",
        "hashtags": "#NewMusic #CREOVAMusic #JustinMafie #OutNow #Stream #Spotify",
        "hook": "OUT NOW 🚨",
    },
}


class TikTokClient:

    def __init__(self):
        self.account = TIKTOK_ACCOUNT
        self.handle = "@creovamusic"
        self.headers = {
            "Authorization": f"Bearer {self.account['access_token']}",
            "Content-Type": "application/json; charset=UTF-8",
        }
        log.info(f"TikTok: {self.handle} connected")

    async def post_video(
        self,
        video_url: str,
        content_type: str = "music_snippet",
        custom_caption: str = None,
        disable_duet: bool = False,
        disable_stitch: bool = False,
    ) -> dict:
        """Post a video to @creovamusic."""
        if not self.account["access_token"]:
            return {"error": "Missing TIKTOK_ACCESS_TOKEN — check Replit Secrets"}

        content = TIKTOK_CONTENT_TYPES.get(content_type, TIKTOK_CONTENT_TYPES["music_snippet"])
        if custom_caption:
            caption = f"{custom_caption}\n\n{content['hashtags']}"
        else:
            caption = f"{content['hook']}\n\n{content['description']}\n\n{content['hashtags']}"

        payload = {
            "post_info": {
                "title": caption[:150],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
                "disable_comment": False,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url,
            },
        }

        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{BASE_URL}/post/publish/video/init/",
                json=payload,
                headers=self.headers,
            ) as r:
                data = await r.json()
                err = data.get("error", {})
                if err.get("code") != "ok":
                    log.error(f"[TikTok] Post error: {err.get('message')}")
                    return {"error": err.get("message"), "account": self.handle}
                publish_id = data.get("data", {}).get("publish_id")
                log.info(f"[TikTok] ✅ Video submitted to {self.handle} — {publish_id}")
                return {"success": True, "publish_id": publish_id, "account": self.handle}

    async def check_status(self, publish_id: str) -> dict:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{BASE_URL}/post/publish/status/fetch/",
                json={"publish_id": publish_id},
                headers=self.headers,
            ) as r:
                data = await r.json()
                return {"publish_id": publish_id, "status": data.get("data", {}).get("status")}

    async def get_account_info(self) -> dict:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{BASE_URL}/user/info/",
                params={"fields": "display_name,follower_count,following_count,likes_count,video_count"},
                headers=self.headers,
            ) as r:
                data = await r.json()
                return data.get("data", {}).get("user", {})

    async def get_video_analytics(self, max_count: int = 10) -> list:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{BASE_URL}/video/list/",
                json={"fields": ["id", "title", "view_count", "like_count", "share_count", "comment_count"], "max_count": max_count},
                headers=self.headers,
            ) as r:
                data = await r.json()
                return data.get("data", {}).get("videos", [])

    def build_music_release_plan(self, song_title: str, release_date: str) -> dict:
        """TikTok-specific plan for a CREOVA Music release."""
        return {
            "song": song_title,
            "account": self.handle,
            "release_date": release_date,
            "pre_release": [
                {"days_before": 14, "type": "teaser", "concept": f"🔊 Something dropping soon... {song_title} preview"},
                {"days_before": 7,  "type": "snippet", "concept": f"7 days. @creovamusic 🎵 #{song_title.replace(' ','')}"},
                {"days_before": 3,  "type": "countdown", "concept": f"3 days until {song_title} 🚨 @creovamusic"},
                {"days_before": 1,  "type": "hype", "concept": f"Tomorrow. {song_title}. @creovamusic 🔥"},
            ],
            "release_day": {
                "type": "music_release",
                "caption": f"OUT NOW 🚨 {song_title} by @creovamusic\n\nStream everywhere 🌍\nLink in bio\n\n#CREOVAMusic #JustinMafie #NewMusic #OutNow #Stream",
            },
            "post_release": [
                {"days_after": 3,  "concept": "React to listeners' comments about the song"},
                {"days_after": 7,  "concept": "Behind the scenes of making this track at @sankofastudio__"},
                {"days_after": 14, "concept": f"Streaming milestone update for {song_title}"},
            ],
        }

    async def format_status(self) -> str:
        try:
            info = await self.get_account_info()
            followers = info.get("follower_count", "N/A")
            videos = info.get("video_count", "N/A")
            likes = info.get("likes_count", "N/A")
            return (
                f"🎵 TIKTOK STATUS\n"
                f"  ✅ {self.handle} — {followers} followers · {videos} videos · {likes} likes"
            )
        except Exception as e:
            return f"🎵 TIKTOK — ❌ {str(e)[:60]}"
