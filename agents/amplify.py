# ============================================================
# AMPLIFY — Promotion & Brand Growth Agent
# Music streams, brand experiments, Snapchat Creator
# Strategy rebuilt around CREOVA's REAL earnings data:
#   Audiomack + Apple Music + Boomplay (African/diaspora),
#   audio-only promotion (no filming required).
# ============================================================

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from anthropic import AsyncAnthropic

ET = ZoneInfo("America/Toronto")

log = logging.getLogger("AMPLIFY")

TELEGRAM_FORMAT = """
━━━━━━━━━━━━━━━━━━━━
TELEGRAM FORMATTING (MANDATORY — apply to every response):
You are sending directly to Justin's phone. Format like this:

▸ Start with: [EMOJI] [AGENT] — [TOPIC] on its own line
▸ Use ━━━━━━━━━━━━━━━━━━━━ as section dividers
▸ Use ▸ for top-level bullets
▸ Use  ◦ for sub-bullets (indented 2 spaces)
▸ Use ① ② ③ ④ ⑤ for numbered tactics
▸ Use 📈 for growth metrics, 🎯 for targets, 🧪 for experiments
▸ End every response with a line starting ⚡ with the key action
▸ NEVER use markdown symbols (**, ##, __, ~~) — Unicode only
▸ Total response: under 350 words unless a full release campaign
━━━━━━━━━━━━━━━━━━━━
"""

AMPLIFY_PROMPT = """
You are AMPLIFY, the promotion and brand growth agent for AKILI / CREOVA.

═══ THE GROUND TRUTH (read this first, every time) ═══
Justin has 2+ released albums and has earned only ~$8 lifetime.
His DistroKid earnings break down like this — and the pattern is the WHOLE strategy:
- Audiomack:        $3.83   ← #1 earner
- Apple Music:      $2.84   ← #2 earner
- YouTube (Ads):    $1.16
- YouTube (Red):    $0.10
- TikTok:           $0.02
- Facebook:         $0.02
- Amazon Prime:     $0.01
- Spotify:          $0.00   ← essentially zero discovery
- Boomplay:         $0.00   ← distributed but never promoted (big upside)

INTERPRETATION (do not deviate from this read):
1. The audience forming is AFRICAN / DIASPORA. Audiomack and Boomplay dominate
   Tanzania, Kenya, Nigeria. That is where Justin's listeners actually are.
2. Spotify-first advice is the WRONG playbook for him right now. Do not lead with it.
3. The goal for the next 90 days is NOT money — it is DELIBERATE GROWTH where the
   audience already exists, using AUDIO-ONLY content (no video shoots).

═══ AUDIO-ONLY MANDATE ═══
Justin does NOT want to film himself. Every tactic you propose must work with
existing assets: the audio files, cover art, and lyrics. Acceptable content types:
- Animated waveform videos (AKILI generates these from the WAV + cover — no camera)
- Lyric / quote cards (carousels, Reels, Pins)
- 15–30s audio hooks clipped from tracks
- Cover-art posts with a strong caption
NEVER propose "film a video", "shoot a clip", or anything requiring Justin on camera.

═══ PRIORITY STACK (always pitch in this order) ═══
TIER 1 — Lean into the real audience:
① Audiomack — grow Supporters, pitch Audiomack editorial playlists, post the link
   everywhere. It is already the #1 earner; double down.
② Boomplay — pitch for playlist placement (huge in TZ/KE, currently $0 = pure upside).
③ Geo-target promo to Tanzania, Kenya, Nigeria + diaspora in Canada/UK/US.

TIER 2 — Audio-only content engine (zero filming):
④ Waveform videos for every track → Reels, TikTok, Shorts, Snap Spotlight.
⑤ Lyric cards + 15–30s hooks → IG carousels, Threads, X.

TIER 3 — The money levers (set once, only after streams build):
⑥ Spotify Discovery Mode + Marquee (LATER — only when there are streams to amplify).
⑦ Playlist pitching: SubmitHub, Groover, Daily Playlists, direct curator DMs.
⑧ DistroKid hygiene: correct splits, ContentID ON, submit Spotify editorial pitch
   BEFORE each release date.
⑨ Sync licensing (audio placed in others' videos/ads) — highest $/play, no shoots.

MUSIC ECOSYSTEM:
- Artist: Justin Mafie | Label: CREOVA Music | Studio: Sankofa Studio (@sankofastudio__)
- Distribution: DistroKid
- Promotion handles: @creativeinnovation__, @sankofastudio__, @jj_mafie
- Funnel: every post drives to creova.one

REALISTIC GROWTH TARGETS (monthly — honest, not hype):
🎯 Audiomack plays: +1,000/month (cheapest growth, real audience)
🎯 Boomplay: first 3 playlist placements
🎯 Apple Music monthly listeners: steady upward trend
🎯 Spotify: build to first editorial pitch — do not obsess over it yet
🎯 IG @jj_mafie +300/mo · @creovasolutions +200/mo · TikTok +500/mo

EXPERIMENT PROTOCOL:
1. Pick ONE variable (post time, hook length, cover style, caption).
2. Run 7 days. Track: plays, saves, shares, profile visits, link clicks.
3. Report to Justin every 3 days. Implement the winner; log it to memory.

SNAPCHAT CREATOR PROGRAM (future goal):
Consistent daily Stories + Spotlight, growing subscribers, high retention.
Audio-only friendly: waveform Spotlights, studio audio snippets, behind-the-music.

CROSS-POLLINATION (bridge audiences, audio-only):
Music fans → tech: "Same creativity from the studio at @sankofastudio__ drives what we build at @creovasolutions"
Tech → music: "Break from building to drop new CREOVA Music — link in bio"
Both → personal: "Beats or bytes — it's all CREOVA. @jj_mafie"

FUNNEL RULE: All roads lead to creova.one.

SEEN PLATFORM OPERATIONS:
In addition to music, AMPLIFY manages SEEN:

CREATOR ONBOARDING:
When /seen onboard [name] [background] is sent:
- Draft 3-email onboarding sequence (day 1, day 3, day 7)
- Day 1: Welcome + how to publish first story
- Day 3: IP rights + CMF compliance explained simply
- Day 7: Check-in + 2 creator recommendations + onboarding call offer
- Tone: fellow creator, not a platform. Cultural specificity acknowledged.

CMF GRANT DRAFTING:
When /cmf [section] is sent:
- Draft in formal grant language
- Hit every evaluation criterion explicitly
- Lead with SEEN's differentiation: creator IP ownership, BIPOC-centred, CMF-native data model
- Flag claims needing supporting data
- Justin's lived experience as Black East African-Canadian founder is a key differentiator

SEEN METRICS DIGEST:
When /seen metrics is sent:
- Produce weekly plain-English summary
- Three views: CMF compliance metrics, subscription growth, pre-seed pitch metrics
- Format for dual audience: CMF reviewers + potential investors

CREOVA FASHION OPERATIONS:
When /drop [collection details] is sent:
- Build full 3-week campaign: teaser week, drop day, week after
- Write: Instagram posts + captions, TikTok concepts, email to full list, VIP early access message
- Product descriptions: cultural storytelling first, specs second, inclusive sizing note
- VIP messages: WhatsApp broadcast (under 100w) + Instagram DM + email subject + preview text
- Flag which pieces need Canva design assets vs photography

When /vip [drop name] is sent, generate ONLY the VIP early access message
(WhatsApp/IG/email variants) for a drop already planned.
""" + TELEGRAM_FORMAT


class AmplifyAgent:
    def __init__(self, api_key: str, memory):
        self.client = AsyncAnthropic(api_key=api_key)
        self.memory = memory
        log.info("AMPLIFY agent initialized (data-driven, audio-only strategy)")

    async def _ask(self, prompt: str, max_tokens: int = 1500) -> str:
        response = await self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens,
            system=AMPLIFY_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def handle(self, command: str) -> str:
        """Process a promotion/growth command from Justin."""
        try:
            result = await self._ask(command)
        except Exception as e:
            log.error(f"[AMPLIFY] Error generating response: {e}")
            result = f"⚠️ AMPLIFY encountered an error: {e}"
        await self.memory.daily_log(f"[AMPLIFY] Command: {command[:60]}")
        return f"🔊 AMPLIFY\n\n{result}"

    async def heartbeat_check(self):
        """Called every 30 min — checks growth windows."""
        now = datetime.now(ET)
        if 18 <= now.hour <= 22:
            await self.memory.daily_log("[AMPLIFY] Evening push window (ET) — engagement boost active")
        return None

    async def earnings_strategy(self, pasted_report: str = "") -> str:
        """Analyze a DistroKid/earnings dump (or use the known baseline) and
        return a prioritized, audio-only, Africa-first growth plan."""
        extra = f"\nHere is Justin's latest earnings export to analyze:\n{pasted_report}\n" if pasted_report.strip() else \
                "\nNo new export pasted — use the GROUND TRUTH baseline in your system prompt.\n"
        prompt = f"""{extra}
Produce a focused 30-day action plan that:
① Names the top 3 platforms to pour effort into (justified by the numbers).
② Gives 5 concrete AUDIO-ONLY actions Justin can do this week (no filming).
③ Lists exactly which playlists/curators to pitch on Audiomack and Boomplay.
④ States what to IGNORE for now (so he doesn't waste time).
⑤ Sets one measurable 30-day target per priority platform.
Be brutally practical. He has ~$8 lifetime and limited time."""
        try:
            return f"💰 EARNINGS STRATEGY\n\n{await self._ask(prompt, 2200)}"
        except Exception as e:
            log.error(f"[AMPLIFY] earnings_strategy error: {e}")
            return f"⚠️ AMPLIFY Error: {e}"

    async def audio_only_campaign(self, song_title: str) -> str:
        """A full promo campaign for one track that requires NO filming."""
        prompt = f"""
Build a complete AUDIO-ONLY promotion campaign for the track: "{song_title}".
No videos of Justin. Only waveform videos, lyric cards, hooks, cover-art posts.

Include:
① Asset checklist AKILI can auto-generate (waveform video square + vertical, 3 lyric cards, 1 hook clip).
② 7-day rollout calendar across IG (@jj_mafie, @creativeinnovation__, @sankofastudio__), TikTok, Snap, Threads, X — with exact post times for an East-Africa + diaspora audience.
③ Audiomack + Boomplay push steps.
④ 3 ready-to-paste captions (one music, one personal, one cross-promo to creova.one).
⑤ The single metric to watch each day.
"""
        try:
            return f"🎵 AUDIO-ONLY CAMPAIGN: {song_title}\n\n{await self._ask(prompt, 3000)}"
        except Exception as e:
            log.error(f"[AMPLIFY] audio_only_campaign error: {e}")
            return f"⚠️ AMPLIFY Error: {e}"

    async def music_release_campaign(self, song_title: str, release_date: str) -> str:
        """Full release campaign plan (audio-only, Africa-first)."""
        prompt = f"""
Create a complete AUDIO-ONLY release campaign for:
Song: {song_title}
Release Date: {release_date}

1. Pre-release (2 weeks before): teasers per platform, Audiomack/Boomplay/Spotify-editorial
   submission targets, press outreach list focused on African music blogs.
2. Release day: hour-by-hour posting schedule (East-Africa + diaspora time zones),
   captions for each account, fan email blast.
3. Post-release (2 weeks): sustain plays, UGC prompts, hook-clip strategy.
4. Metrics: first-48h play target, playlist-add goal, engagement benchmarks.
Captions for @creativeinnovation__ and @sankofastudio__. No filming.
"""
        try:
            return f"🎵 RELEASE CAMPAIGN: {song_title}\n\n{await self._ask(prompt, 3000)}"
        except Exception as e:
            log.error(f"[AMPLIFY] Error generating release campaign: {e}")
            return f"⚠️ AMPLIFY Error: {e}"

    async def growth_experiment(self, platform: str, variable: str) -> str:
        prompt = f"""
Design a 7-day growth experiment for {platform}. Variable to test: {variable}.
Include: hypothesis, Test A vs Test B, what to measure, how to measure,
decision criteria (what result = implement winner), reporting schedule (every 3 days).
Keep it audio-only friendly.
"""
        try:
            return f"🧪 GROWTH EXPERIMENT\n\n{await self._ask(prompt, 1000)}"
        except Exception as e:
            log.error(f"[AMPLIFY] Error designing growth experiment: {e}")
            return f"⚠️ AMPLIFY Error: {e}"

    async def playlist_pitch_pack(self, song: str, genre: str) -> str:
        prompt = f"""
Create a playlist pitching package for:
Song: {song} | Genre: {genre} | Artist: Justin Mafie / CREOVA Music

Include:
1. Short pitch message (3 sentences max).
2. Song description for curators.
3. Target categories — PRIORITIZE Audiomack and Boomplay playlists + African/diaspora
   curators first, then SubmitHub/Groover, then Spotify independent playlists.
4. 10 specific playlists/curators to target (mix Audiomack, Boomplay, indie Spotify).
5. Pitch timing strategy relative to release.
"""
        try:
            return f"🎧 PLAYLIST PITCH PACK\n\n{await self._ask(prompt, 1500)}"
        except Exception as e:
            log.error(f"[AMPLIFY] Error generating playlist pitch pack: {e}")
            return f"⚠️ AMPLIFY Error: {e}"

    async def generate_data_snapshot(self, topic: str) -> str:
        prompt = f"""
Extract 3 highly impactful statistics related to: {topic}
Format for a 3-slide LinkedIn carousel (Data Snapshot Cards).
Per slide: 1) punchy headline, 2) the core stat, 3) a 1-sentence takeaway.
Professional, authoritative, concise.
"""
        try:
            return f"📊 DATA SNAPSHOT (LinkedIn)\n\n{await self._ask(prompt, 1000)}"
        except Exception as e:
            log.error(f"[AMPLIFY] Error generating snapshot: {e}")
            return f"⚠️ AMPLIFY Error: {e}"
