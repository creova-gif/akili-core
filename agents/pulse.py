# ============================================================
# PULSE — Social Media Management Agent (Phase 5 Enhanced)
# Carousel builder · Hashtag intelligence · A/B tracking
# Full cross-platform content engine for CREOVA
# ============================================================

import logging
import json
from datetime import datetime
from anthropic import AsyncAnthropic
from skills.shared.telegram_formatter import formatter, DIVIDER
from config.knowledge_loader import get_knowledge_for_agent
from config.creova_services import get_service_context_for_agent, SERVICE_INJECTION_PROMPTS

log = logging.getLogger("PULSE")

HASHTAG_SETS = {
    "music":    ["#CREOVAMusic", "#JustinMafie", "#AfricanMusic", "#SankofaStudio",
                 "#NewMusic", "#AfroBeats", "#IndependentArtist", "#MusicProducer"],
    "tech":     ["#CREOVA", "#CREOVASolutions", "#AfricanTech", "#EmergingMarkets",
                 "#Founder", "#StartupAfrica", "#TechInnovation", "#BuildingInAfrica"],
    "personal": ["#JustinMafie", "#CREOVA", "#FounderLife", "#AfricanFounder",
                 "#CreativeTech", "#PanAfrican", "#YouthEntrepreneur"],
    "studio":   ["#SankofaStudio", "#CREOVAMusic", "#StudioLife", "#MusicProduction",
                 "#BeatMaker", "#AfricanStudio", "#RecordingStudio"],
    "branding": ["#Branding", "#CreativeAgency", "#CREOVA", "#BrandStrategy",
                 "#DesignThinking", "#VisualIdentity", "#CREOVASolutions"],
}

PULSE_PROMPT = """
You are PULSE, the social media management agent for AKILI / CREOVA.

YOUR ACCOUNTS:
JUSTIN MAFIE (personal brand):
- Instagram: @jj_mafie
- Twitter/X: @justin_mafie
- LinkedIn: Justin Mafie
- Snapchat: jay-mafie
- TikTok: @jj_mafie

CREOVA SOLUTIONS (global tech company):
- Instagram: @creovasolutions
- LinkedIn: CREOVA Solutions

CREOVA MEDIA / MUSIC:
- Instagram: @creativeinnovation__

SANKOFA STUDIO (production):
- Instagram: @sankofastudio__

TikTok Music: @creovamusic
Facebook: Justin Mafie personal + CREOVA Business

CONTENT CALENDAR (weekly rotation):
- Monday: Music Monday — new releases, behind scenes, studio
- Tuesday: Tech Tuesday — CREOVA Solutions innovations, product updates
- Wednesday: Wisdom Wednesday — branding tips, founder advice, lessons
- Thursday: Throwback Thursday — journey, past projects, growth story
- Friday: Fresh Friday — new music, upcoming projects, announcements
- Saturday: Studio Saturday — production content, creative process
- Sunday: Founder Sunday — personal brand, vision, reflection

CONTENT MIX:
- 30% Music (CREOVA Music, Sankofa Studio, streams, studio sessions)
- 30% Tech/Innovation (CREOVA Solutions, 14 products, African tech)
- 20% Personal brand (Justin Mafie founder journey, lifestyle)
- 20% Educational (branding tips, music production, tech insights)

CROSS-PROMOTION (MANDATORY — every post must include at least one):
- @creativeinnovation__ OR @creovasolutions OR @sankofastudio__
- www.creova.one in bio or caption
- #CREOVA #JustinMafie #CREOVAMusic #CREOVASolutions #AfricanTech

VOICE: Authentic. Visionary. African excellence. Creative-tech founder.
Never robotic. Never generic. Always Justin Mafie's real voice.

BILINGUAL OUTPUT RULE:
For any content targeting @creativeinnovation__ or East African/diaspora audiences:
- Always produce English caption first
- Then Swahili caption below it (labeled 🇹🇿 Kiswahili:)
- Flag any Swahili phrases that need native speaker review with [REVIEW]
- Three Swahili registers: formal (government/corporate), everyday (market Swahili), casual (Instagram)
- Ask Justin which register before generating if unclear
- Never machine-translate — write in natural Swahili

CAMPAIGN BUILDER:
When Justin says /drop or asks for a campaign:
1. Pull sales data context Justin provides
2. Identify slow periods or revenue dips
3. Draft full promotional strategy: target audience, offer, channels, timing
4. Write all copy: Instagram posts, TikTok hooks, email subject lines, WhatsApp broadcast
5. Flag which assets need Canva design vs photography
6. Include seasonal calendar awareness: grad season (Apr-May), back-to-school (Sep), holiday (Nov-Dec)

TELEGRAM OUTPUT FORMAT:
- Use HTML tags: <b>bold</b>, <i>italic</i>, <code>code</code>
- Use ━━━━━━━━━━━━━━━━━━━━ as section dividers
- Use ▸ for bullets
- End every response with ⚡ + the key action Justin should take
- Keep mobile-friendly — short paragraphs
""" + "\n\n" + get_knowledge_for_agent("PULSE") + "\n\n" + get_service_context_for_agent("PULSE") + "\n\n" + SERVICE_INJECTION_PROMPTS.get("PULSE", "")


class PulseAgent:
    def __init__(self, api_key: str, memory):
        self.client  = AsyncAnthropic(api_key=api_key)
        self.memory  = memory
        self.ab_data = {}
        log.info("PULSE agent initialized")

    async def handle(self, command: str) -> str:
        """Process a social media command from Justin — routes to best skill."""
        lower = command.lower()

        if "carousel" in lower:
            topic = command.split("carousel", 1)[-1].strip() or "CREOVA"
            return await self.build_carousel(topic)

        if "hashtag" in lower:
            vert = ("tech" if "tech" in lower else
                    "music" if "music" in lower else
                    "studio" if "studio" in lower else
                    "branding" if "brand" in lower else "personal")
            return self._format_hashtags(vert)

        if "ab test" in lower or "experiment" in lower:
            return await self.run_ab_experiment(command)

        if ("week" in lower and "calendar" in lower) or "7 day" in lower:
            return await self.generate_weekly_calendar()

        if "image" in lower or "visual" in lower:
            return await self.generate_image_brief(command)

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1500,
                system=PULSE_PROMPT,
                messages=[{"role": "user", "content": command}]
            )
            result = response.content[0].text
        except Exception as e:
            log.error(f"[PULSE] Error generating response: {e}")
            result = f"⚠️ PULSE encountered an error: {e}"
        await self.memory.daily_log(f"[PULSE] Command: {command[:60]}")
        return f"📡 PULSE\n\n{result}"

    async def heartbeat_check(self):
        """Called every 30 min — checks scheduled content queue."""
        now  = datetime.now()
        hour = now.hour
        day  = now.strftime("%A").lower()
        await self.memory.daily_log(f"[PULSE] Heartbeat — {day} {hour:02d}:00")
        return None

    async def generate_content_package(self, topic: str, day: str = None) -> str:
        """Generate a full cross-platform content package for a topic."""
        if not day:
            day = datetime.now().strftime("%A")

        prompt = f"""
Topic: {topic}
Day: {day}

Generate a full cross-platform content package. Return as JSON:
{{
  "instagram_jj":     {{ "caption": "...", "hook": "first line that stops scroll", "hashtags": [...] }},
  "instagram_creova": {{ "caption": "...", "hashtags": [...] }},
  "instagram_music":  {{ "caption": "...", "hashtags": [...] }},
  "twitter":          {{ "tweet": "...", "thread": ["t1","t2","t3"] }},
  "linkedin_justin":  "...",
  "linkedin_creova":  "...",
  "tiktok":           {{ "caption": "...", "video_concept": "..." }},
  "snapchat":         {{ "shots": ["shot1","shot2","shot3"] }},
  "visual_direction": "What image/video to pair with this",
  "best_time":        "Best time to post ET for max reach"
}}
Only JSON.
"""
        try:
            r = await self.client.messages.create(
                model="claude-sonnet-4-5", max_tokens=2000,
                system=PULSE_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = r.content[0].text.strip().replace("```json","").replace("```","").strip()
        except Exception as e:
            log.error(f"[PULSE] Error generating content package: {e}")
            return f"⚠️ PULSE Error: {e}"
        try:
            data = json.loads(raw)
            return formatter.format("PULSE", "approval", {
                "platform":    "ALL PLATFORMS",
                "accounts":    [],
                "handle":      "All 10 accounts",
                "theme":       topic,
                "caption":     data.get("instagram_jj", {}).get("caption", ""),
                "hashtags":    data.get("instagram_jj", {}).get("hashtags", []),
                "visual_note": data.get("visual_direction", ""),
                "goal":        "Cross-platform reach and brand building",
                "best_time":   data.get("best_time", "Check platform analytics"),
                "approval_id": f"multi_{datetime.now().strftime('%H%M')}",
            })
        except Exception:
            return await formatter.ai_enhance(raw, "PULSE", topic)

    # ── Instagram carousel builder ────────────────────────────
    async def build_carousel(self, topic: str) -> str:
        prompt = f"""
Build a 7-slide Instagram carousel for Justin Mafie on: {topic}

For each slide provide:
- Slide number + title (4 words max)
- Content (2-3 sentences or bullet points)
- Visual direction

Slide structure:
1. Hook — bold statement or problem
2-5. Value — the meat
6. Summary — key takeaways
7. CTA — follow @creovasolutions / @jj_mafie / creova.one

Justin's voice. African futurism aesthetic. Educational but engaging.
"""
        try:
            r = await self.client.messages.create(
                model="claude-sonnet-4-5", max_tokens=1500,
                system=PULSE_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return await formatter.ai_enhance(
                f"📱 CAROUSEL — {topic}\n\n{r.content[0].text}", "PULSE", "carousel"
            )
        except Exception as e:
            log.error(f"[PULSE] Error building carousel: {e}")
            return f"⚠️ PULSE Error: {e}"

    # ── Image generation brief ────────────────────────────────
    async def generate_image_brief(self, request: str) -> str:
        prompt = f"""
Create a DALL-E 3 image prompt for this request: {request}

The image must:
- Match CREOVA's African futurism aesthetic (bold, modern, premium)
- Work well as a social media post (square or portrait)
- Not include text
- Reference Justin Mafie / CREOVA visual identity if relevant

Return ONLY the DALL-E prompt (under 200 words).
"""
        try:
            r = await self.client.messages.create(
                model="claude-sonnet-4-5", max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            dalle_prompt = r.content[0].text.strip()
        except Exception as e:
            log.error(f"[PULSE] Error generating image brief: {e}")
            return f"⚠️ PULSE Error: {e}"

        import os
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            try:
                import openai
                openai.api_key = openai_key
                img = openai.images.generate(
                    model="dall-e-3", prompt=dalle_prompt,
                    size="1024x1024", quality="standard", n=1,
                )
                url = img.data[0].url
                return (
                    f"🎨 <b>PULSE — Image Generated</b>\n\n"
                    f"{DIVIDER}\n"
                    f"<b>Prompt:</b>\n<i>{dalle_prompt[:150]}</i>\n\n"
                    f"<b>Image URL:</b>\n<code>{url}</code>\n\n"
                    f"{DIVIDER}\n"
                    f"<i>Save this image and post it with your approved caption.</i>\n"
                    f"<i>Cost: ~$0.04 (DALL-E 3 standard)</i>"
                )
            except Exception as e:
                log.error(f"[PULSE] Image gen error: {e}")

        return (
            f"🎨 <b>PULSE — Image Brief</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>DALL-E 3 prompt ready:</b>\n<i>{dalle_prompt}</i>\n\n"
            f"{DIVIDER}\n"
            f"<i>Add OPENAI_API_KEY to Replit Secrets to auto-generate.</i>\n"
            f"<i>Or paste this prompt at: chat.openai.com</i>"
        )

    # ── Hashtag intelligence ──────────────────────────────────
    def _format_hashtags(self, vertical: str) -> str:
        tags = HASHTAG_SETS.get(vertical, HASHTAG_SETS["personal"])
        return (
            f"#️⃣ <b>PULSE — Hashtag Set: {vertical.upper()}</b>\n\n"
            f"{DIVIDER}\n"
            f"<b>Recommended tags:</b>\n"
            f"{' '.join(tags)}\n\n"
            f"<b>Usage:</b> Add to any {vertical} post across all accounts.\n"
            f"<b>Rotate:</b> Change 2-3 tags per post to avoid shadow banning.\n"
            f"{DIVIDER}\n"
            f"<i>Tip: Use 8-12 hashtags on Instagram, 2-3 on Twitter, 3-5 on LinkedIn</i>"
        )

    def get_hashtag_list(self, vertical: str) -> list:
        return HASHTAG_SETS.get(vertical, HASHTAG_SETS["personal"])

    # ── A/B experiment ────────────────────────────────────────
    async def run_ab_experiment(self, request: str) -> str:
        platform = "instagram" if "instagram" in request.lower() else "twitter"
        variable = "caption style" if "caption" in request.lower() else "posting time"
        prompt = f"""
Design a 7-day A/B experiment for Justin Mafie on {platform}.
Variable testing: {variable}

Include:
- Hypothesis
- Version A vs Version B (what exactly changes)
- How to measure success (specific metric + target number)
- Decision criteria after 7 days
- How to implement the winner

Be specific — real numbers, real metrics.
"""
        try:
            r = await self.client.messages.create(
                model="claude-sonnet-4-5", max_tokens=800,
                system=PULSE_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return await formatter.ai_enhance(
                f"🧪 A/B EXPERIMENT — {platform.upper()}\n\n{r.content[0].text}", "PULSE"
            )
        except Exception as e:
            log.error(f"[PULSE] Error running A/B experiment: {e}")
            return f"⚠️ PULSE Error: {e}"

    # ── Weekly content calendar ───────────────────────────────
    async def generate_weekly_calendar(self) -> str:
        prompt = """
Generate a complete 7-day social media content calendar for Justin Mafie and CREOVA.
For each day: theme, 1 Instagram concept, 1 Twitter angle, 1 LinkedIn angle, 1 TikTok concept, 1 Snapchat moment.
Make each day distinct. Real specifics. Justin's authentic voice.
"""
        try:
            r = await self.client.messages.create(
                model="claude-sonnet-4-5", max_tokens=2500,
                system=PULSE_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return await formatter.ai_enhance(r.content[0].text, "PULSE", "weekly calendar")
        except Exception as e:
            log.error(f"[PULSE] Error generating weekly calendar: {e}")
            return f"⚠️ PULSE Error: {e}"
