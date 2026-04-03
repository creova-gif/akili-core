# ============================================================
# AMPLIFY — Promotion & Brand Growth Agent
# Music streams, brand experiments, Snapchat Creator
# ============================================================

import logging
from datetime import datetime
from anthropic import Anthropic

log = logging.getLogger("AMPLIFY")

AMPLIFY_PROMPT = """
You are AMPLIFY, the promotion and brand growth agent for AKILI / CREOVA.

YOUR MISSION:
1. Maximize music streams (Spotify, Apple Music, TikTok, YouTube Music)
2. Grow followers across all Justin Mafie and CREOVA accounts
3. Drive traffic to www.creova.one
4. Run posting time and content experiments
5. Build toward Snapchat Creator program eligibility
6. Cross-pollinate audiences between music, tech, and personal brand

MUSIC ECOSYSTEM:
- Artist: Justin Mafie
- Label: CREOVA Music
- Studio: Sankofa Studio (@sankofastudio__)
- Distribution: DistroKid
- Primary: Spotify, Apple Music, TikTok, YouTube Music
- Promotion handles: @creativeinnovation__, @sankofastudio__

GROWTH TARGETS (monthly):
- Spotify streams: +500/month → grow monthly listeners
- Instagram (@jj_mafie): +300 followers/month
- Instagram (@creovasolutions): +200 followers/month
- LinkedIn: +100 connections/month
- TikTok: +500 followers/month
- Snapchat Creator score: grow consistently
- creova.one traffic: +50 visits/week

STREAM GROWTH TACTICS:
1. Playlist pitching — identify and pitch independent curators
2. TikTok music strategy — use song in original content + encourage UGC
3. Instagram Reels — push songs into Reels music library
4. Release strategy — single drops with 2-week campaign each
5. Collaborations — find artists to feature/remix for cross-audience exposure
6. Press pitching — blogs, podcasts, music media that cover African artists

EXPERIMENT PROTOCOL:
When running posting experiments:
1. Pick ONE variable to test (time, format, caption length, hashtags)
2. Run for 7 days
3. Track: reach, engagement rate, saves, shares, profile visits
4. Report results to Justin via Telegram every 3 days
5. Implement winner — document in memory

SNAPCHAT CREATOR PROGRAM:
Eligibility requirements to hit:
- Consistent daily posting (Stories + Spotlight)
- Growing subscriber count
- High view retention rate
- Authentic, engaging content
Strategy: Show the founder-musician-tech builder lifestyle
Best content: Studio sessions, product builds, CREOVA behind-scenes

CROSS-POLLINATION STRATEGY (bridge audiences):
Music fans → CREOVA tech:
"The same creativity I bring to the studio at @sankofastudio__ 
drives everything we build at @creovasolutions"

Tech audience → Music:
"Taking a break from building [product] to drop something 
new from CREOVA Music — link in bio"

Both → Personal brand:
"Whether it's beats or bytes — it's all CREOVA. Follow the journey @jj_mafie"

CONTENT HOOKS THAT ALWAYS WORK:
- "Building [X] from [Y] — here's what I learned"
- "African founder. Music producer. Tech builder. This is CREOVA."
- "From Halton Hills to Dar es Salaam — we're global"
- "Nobody talks about [insight] in African tech. Let's fix that."

FUNNEL RULE: All roads lead to creova.one
Every post, story, bio, and DM should drive to creova.one
"""


class AmplifyAgent:
    def __init__(self, api_key: str, memory):
        self.client = Anthropic(api_key=api_key)
        self.memory = memory
        log.info("AMPLIFY agent initialized")

    async def handle(self, command: str) -> str:
        """Process a promotion/growth command from Justin."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=AMPLIFY_PROMPT,
            messages=[{"role": "user", "content": command}]
        )
        result = response.content[0].text
        self.memory.daily_log(f"[AMPLIFY] Command: {command[:60]}")
        return f"🔊 AMPLIFY\n\n{result}"

    async def heartbeat_check(self):
        """Called every 30 min — checks growth metrics and experiments."""
        now = datetime.now()
        # Evening push hours (6-10PM) — trigger engagement boost
        if 18 <= now.hour <= 22:
            self.memory.daily_log("[AMPLIFY] Evening push window — engagement boost active")
        return None

    async def music_release_campaign(self, song_title: str, release_date: str) -> str:
        """Generate a full music release campaign plan."""
        prompt = f"""
Create a complete release campaign for:
Song: {song_title}
Release Date: {release_date}

Generate:
1. Pre-release strategy (2 weeks before)
   - Teaser content for each platform
   - Playlist submission targets
   - Press outreach list

2. Release day plan
   - Hour-by-hour posting schedule
   - Stories, posts, tweets for each account
   - Email blast to fans

3. Post-release (2 weeks after)
   - Sustain streams strategy
   - UGC encouragement tactics
   - TikTok viral push

4. Metrics to track
   - First 48-hour stream target
   - Playlist add goal
   - Engagement benchmarks

Include specific captions and hooks for @creativeinnovation__ and @sankofastudio__
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=3000,
            system=AMPLIFY_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"🎵 RELEASE CAMPAIGN: {song_title}\n\n{response.content[0].text}"

    async def growth_experiment(self, platform: str, variable: str) -> str:
        """Design a growth experiment for a platform."""
        prompt = f"""
Design a 7-day growth experiment for {platform}.
Variable to test: {variable}

Include:
- Hypothesis
- Test A vs Test B
- What to measure
- How to measure it
- Decision criteria (what result = implement winner)
- Reporting schedule (send to Justin every 3 days)
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system=AMPLIFY_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"🧪 GROWTH EXPERIMENT\n\n{response.content[0].text}"

    async def playlist_pitch_pack(self, song: str, genre: str) -> str:
        """Generate a playlist pitching package."""
        prompt = f"""
Create a playlist pitching package for:
Song: {song}
Genre: {genre}
Artist: Justin Mafie / CREOVA Music

Include:
1. Short pitch email (3 sentences max)
2. Song description for curators
3. Target playlist categories
4. 10 specific independent playlists to target
5. Pitch timing strategy
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=AMPLIFY_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return f"🎧 PLAYLIST PITCH PACK\n\n{response.content[0].text}"
