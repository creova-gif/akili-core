# ============================================================
# TWITTER / X INTEGRATION — Akili PULSE + REACH Agent
# Account: @justin_mafie
# ============================================================

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from config.accounts import TWITTER_ACCOUNT

log = logging.getLogger("PULSE.Twitter")


class TwitterClient:

    def __init__(self):
        self.client = None
        self.api = None
        self._init()

    def _init(self):
        if not TWITTER_ACCOUNT["api_key"]:
            log.info("Twitter: not configured (add TWITTER_* secrets to enable)")
            return
        try:
            import tweepy
            auth = tweepy.OAuth1UserHandler(
                TWITTER_ACCOUNT["api_key"],
                TWITTER_ACCOUNT["api_secret"],
                TWITTER_ACCOUNT["access_token"],
                TWITTER_ACCOUNT["access_token_secret"],
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            self.client = tweepy.Client(
                bearer_token=TWITTER_ACCOUNT["bearer_token"],
                consumer_key=TWITTER_ACCOUNT["api_key"],
                consumer_secret=TWITTER_ACCOUNT["api_secret"],
                access_token=TWITTER_ACCOUNT["access_token"],
                access_token_secret=TWITTER_ACCOUNT["access_token_secret"],
                wait_on_rate_limit=True,
            )
            log.info("Twitter: @justin_mafie connected")
        except ImportError:
            log.warning("tweepy not installed")
        except Exception as e:
            log.error(f"Twitter init error: {e}")

    def _is_configured(self) -> bool:
        return self.client is not None

    def _trim(self, text: str, limit: int = 280) -> str:
        return text if len(text) <= limit else text[:limit - 3] + "..."

    async def post_tweet(self, text: str, reply_to: Optional[str] = None) -> dict:
        if not self._is_configured():
            return {"error": "Twitter not configured — add TWITTER_* secrets"}
        try:
            kwargs = {"text": self._trim(text)}
            if reply_to:
                kwargs["in_reply_to_tweet_id"] = reply_to
            r = self.client.create_tweet(**kwargs)
            tweet_id = r.data["id"]
            log.info(f"[Twitter] ✅ Tweeted — {tweet_id}")
            return {"success": True, "tweet_id": tweet_id}
        except Exception as e:
            log.error(f"[Twitter] Post error: {e}")
            return {"error": str(e)}

    async def post_thread(self, tweets: list) -> list:
        """Post a numbered thread."""
        results = []
        reply_to = None
        total = len(tweets)
        for i, text in enumerate(tweets, 1):
            numbered = f"{i}/{total} {text}" if total > 1 else text
            r = await self.post_tweet(numbered, reply_to=reply_to)
            results.append(r)
            if "tweet_id" in r:
                reply_to = r["tweet_id"]
            await asyncio.sleep(3)
        log.info(f"[Twitter] ✅ Thread posted — {total} tweets")
        return results

    async def get_mentions(self, since_hours: int = 1) -> list:
        if not self._is_configured():
            return []
        try:
            me = self.client.get_me()
            start_time = datetime.utcnow() - timedelta(hours=since_hours)
            result = self.client.get_users_mentions(
                id=me.data.id,
                start_time=start_time,
                tweet_fields=["author_id", "created_at", "text"],
                max_results=20,
            )
            if result.data:
                return [{"id": m.id, "text": m.text, "author_id": m.author_id} for m in result.data]
            return []
        except Exception as e:
            log.error(f"[Twitter] Mentions error: {e}")
            return []

    async def reply_to(self, tweet_id: str, text: str) -> dict:
        return await self.post_tweet(text, reply_to=tweet_id)

    async def get_analytics(self) -> dict:
        if not self._is_configured():
            return {}
        try:
            me = self.client.get_me(user_fields=["public_metrics"])
            m = me.data.public_metrics
            return {
                "handle": "@justin_mafie",
                "followers": m["followers_count"],
                "following": m["following_count"],
                "tweets": m["tweet_count"],
            }
        except Exception as e:
            log.error(f"[Twitter] Analytics error: {e}")
            return {}

    def build_tweet(self, message: str, include_tags: bool = True) -> str:
        base = message.strip()
        tags = "\n\n#JustinMafie #CREOVA #AfricanFounder #CREOVAMusic" if include_tags else ""
        return self._trim(f"{base}{tags}")

    def build_thread_from_topic(self, topic: str, points: list) -> list:
        opener = f"🧵 {topic} — a thread by @justin_mafie | CREOVA Founder"
        closer = (
            "That's the CREOVA way.\n\n"
            "Music. Tech. Africa + Canada.\n\n"
            "Follow @justin_mafie for the full journey 🌍\n\n"
            "#CREOVA #AfricanFounder #CREOVAMusic creova.one"
        )
        return [opener] + points + [closer]

    async def format_status(self) -> str:
        if not self._is_configured():
            return "🐦 TWITTER — ⚪ Not configured (add TWITTER_* secrets)"
        analytics = await self.get_analytics()
        if analytics:
            return (
                f"🐦 TWITTER STATUS\n"
                f"  ✅ @justin_mafie — {analytics['followers']} followers · {analytics['tweets']} tweets"
            )
        return "🐦 TWITTER — ❌ Connection failed"
