# ============================================================
# VOICE ENGINE — AKILI "Jarvis" layer
# Speech-to-text + text-to-speech with automatic provider choice:
#   • ElevenLabs  (if ELEVENLABS_API_KEY) — best quality + voice cloning
#   • OpenAI      (if OPENAI_API_KEY)     — works out of the box
# No extra Python deps — uses aiohttp (already required).
# Degrades gracefully when no provider key is set.
# ============================================================

import os
import re
import logging
import aiohttp

log = logging.getLogger("VOICE")

ELEVEN_API = "https://api.elevenlabs.io/v1"
OPENAI_API = "https://api.openai.com/v1"
# Widely-available ElevenLabs stock voice ("Rachel") if none configured.
DEFAULT_ELEVEN_VOICE = "21m00Tcm4TlvDq8ikWAM"
# OpenAI TTS voice (deep, calm — Jarvis-like).
DEFAULT_OPENAI_VOICE = "onyx"


class VoiceEngine:
    """Jarvis voice I/O for AKILI.

    transcribe(audio_bytes, filename) -> str   (speech -> text)
    synthesize(text) -> bytes | None           (text  -> mp3 bytes)
    should_speak(was_voice_input) -> bool      (honours AKILI_VOICE_MODE)
    """

    def __init__(self):
        self.eleven_key  = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        self.eleven_vid  = os.environ.get("ELEVENLABS_VOICE_ID", "").strip() or DEFAULT_ELEVEN_VOICE
        self.openai_key  = os.environ.get("OPENAI_API_KEY", "").strip()
        self.mode        = os.environ.get("AKILI_VOICE_MODE", "auto").strip().lower()

        if self.eleven_key:
            self.provider = "elevenlabs"
        elif self.openai_key:
            self.provider = "openai"
        else:
            self.provider = None

        if self.enabled:
            log.info(f"Voice engine ready — provider={self.provider}, mode={self.mode}")
        else:
            log.warning("Voice engine disabled — set ELEVENLABS_API_KEY or OPENAI_API_KEY.")

    @property
    def enabled(self) -> bool:
        return self.provider is not None

    def should_speak(self, was_voice_input: bool) -> bool:
        if not self.enabled or self.mode == "off":
            return False
        if self.mode == "on":
            return True
        return was_voice_input  # "auto": speak only when Justin spoke first

    # ── Speech -> Text ────────────────────────────────────────
    async def transcribe(self, audio_bytes: bytes, filename: str = "voice.oga") -> str:
        if self.provider == "elevenlabs":
            return await self._eleven_stt(audio_bytes, filename)
        if self.provider == "openai":
            return await self._openai_stt(audio_bytes, filename)
        return ""

    async def _eleven_stt(self, audio_bytes: bytes, filename: str) -> str:
        form = aiohttp.FormData()
        form.add_field("model_id", "scribe_v1")
        form.add_field("file", audio_bytes, filename=filename,
                       content_type="application/octet-stream")
        return await self._post_form(f"{ELEVEN_API}/speech-to-text", form,
                                     {"xi-api-key": self.eleven_key}, key="text")

    async def _openai_stt(self, audio_bytes: bytes, filename: str) -> str:
        form = aiohttp.FormData()
        form.add_field("model", "whisper-1")
        form.add_field("file", audio_bytes, filename=filename,
                       content_type="application/octet-stream")
        return await self._post_form(f"{OPENAI_API}/audio/transcriptions", form,
                                     {"Authorization": f"Bearer {self.openai_key}"}, key="text")

    async def _post_form(self, url: str, form, headers: dict, key: str) -> str:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, data=form, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=120)) as r:
                    if r.status != 200:
                        log.error(f"STT failed [{r.status}]: {(await r.text())[:200]}")
                        return ""
                    return ((await r.json()).get(key) or "").strip()
        except Exception as e:
            log.error(f"STT error: {e}")
            return ""

    # ── Text -> Speech ────────────────────────────────────────
    async def synthesize(self, text: str) -> bytes | None:
        if not self.enabled or not text.strip():
            return None
        clean = self._clean_for_speech(text)
        if not clean:
            return None
        if self.provider == "elevenlabs":
            return await self._eleven_tts(clean)
        return await self._openai_tts(clean)

    async def _eleven_tts(self, text: str) -> bytes | None:
        url = f"{ELEVEN_API}/text-to-speech/{self.eleven_vid}"
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        headers = {"xi-api-key": self.eleven_key, "Content-Type": "application/json",
                   "Accept": "audio/mpeg"}
        return await self._post_audio(url, payload, headers)

    async def _openai_tts(self, text: str) -> bytes | None:
        url = f"{OPENAI_API}/audio/speech"
        payload = {"model": "tts-1", "voice": DEFAULT_OPENAI_VOICE,
                   "input": text, "response_format": "mp3"}
        headers = {"Authorization": f"Bearer {self.openai_key}",
                   "Content-Type": "application/json"}
        return await self._post_audio(url, payload, headers)

    async def _post_audio(self, url: str, payload: dict, headers: dict) -> bytes | None:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, json=payload, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=120)) as r:
                    if r.status != 200:
                        log.error(f"TTS failed [{r.status}]: {(await r.text())[:200]}")
                        return None
                    return await r.read()
        except Exception as e:
            log.error(f"TTS error: {e}")
            return None

    # ── Helpers ───────────────────────────────────────────────
    @staticmethod
    def _clean_for_speech(text: str, max_chars: int = 900) -> str:
        """Strip emojis, dividers, markup so speech sounds natural and short."""
        t = text
        t = re.sub(r"[━─▸◦⚡📈🎯🧪🔊🛡📡📨🔍🎵🎧📊💾⚙️⚠️🟢🐙🔔🎙🗣🎬💰]+", " ", t)
        t = re.sub(r"[*_#~`>|]", "", t)
        t = re.sub(r"https?://\S+", "", t)
        t = re.sub(r"[①②③④⑤⑥⑦⑧⑨⑩]", "", t)
        t = re.sub(r"\n{2,}", ". ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) > max_chars:
            cut = t[:max_chars]
            t = cut.rsplit(".", 1)[0] + "." if "." in cut else cut
        return t
