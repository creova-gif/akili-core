# ============================================================
# INTEGRATION HUB — Akili Phase 2
# Wires all platforms into Akili agents
# ============================================================

import logging
from integrations.instagram   import InstagramClient
from integrations.twitter     import TwitterClient
from integrations.linkedin    import LinkedInClient
from integrations.snapchat    import SnapchatClient
from integrations.facebook    import FacebookClient
from integrations.tiktok      import TikTokClient
from integrations.gmail       import GmailClient
from integrations.github_monitor import GitHubMonitor

log = logging.getLogger("HUB")


class IntegrationHub:
    """All platforms wired in one place. Imported by agent classes."""

    def __init__(self):
        log.info("Initializing Akili integration hub...")
        self.instagram = InstagramClient()
        self.twitter   = TwitterClient()
        self.linkedin  = LinkedInClient()
        self.snapchat  = SnapchatClient()
        self.facebook  = FacebookClient()
        self.tiktok    = TikTokClient()
        self.gmail     = GmailClient()
        self.github    = GitHubMonitor()
        log.info("Hub ready — 8 integrations loaded")

    async def full_health_check(self) -> str:
        """Run status checks on all platforms — send to Justin via Telegram."""
        lines = ["🔌 AKILI INTEGRATION STATUS\n"]

        ig_status    = await self.instagram.format_status()
        tw_status    = await self.twitter.format_status()
        li_status    = await self.linkedin.format_status()
        snap_status  = await self.snapchat.format_status()
        fb_status    = await self.facebook.format_status()
        tt_status    = await self.tiktok.format_status()
        gm_status    = await self.gmail.format_status()
        gh_status    = f"🐙 GITHUB — creova-gif org · 14 repos monitored"

        lines += [ig_status, "", tw_status, "", li_status, "",
                  snap_status, "", fb_status, "", tt_status, "",
                  gm_status, "", gh_status]
        return "\n".join(lines)

    async def get_all_follower_counts(self) -> str:
        """Quick follower snapshot across all platforms."""
        lines = ["📊 FOLLOWER SNAPSHOT\n"]
        try:
            ig = await self.instagram.get_all_insights()
            for acc in ig:
                h = acc.get("handle", "?")
                f = acc.get("followers_count", "N/A")
                lines.append(f"  {h}: {f}")
        except Exception as e:
            lines.append(f"  Instagram: error — {e}")

        try:
            tw = await self.twitter.get_analytics()
            lines.append(f"  {tw.get('handle','@justin_mafie')}: {tw.get('followers','N/A')} followers")
        except Exception as e:
            lines.append(f"  Twitter: error — {e}")

        try:
            tt = await self.tiktok.get_account_info()
            lines.append(f"  @creovamusic (TikTok): {tt.get('follower_count','N/A')} followers")
        except Exception as e:
            lines.append(f"  TikTok: error — {e}")

        return "\n".join(lines)
