# ============================================================
# AUDIO VISUALIZER — AKILI / AMPLIFY
# Turns an audio track (+ optional cover art) into a shareable
# video with an animated waveform. NO filming required.
# Pure ffmpeg — no Python media deps. Degrades gracefully.
# ============================================================

import os
import shutil
import asyncio
import logging

log = logging.getLogger("VISUALIZER")

CREOVA_MAROON = "0x800000"   # brand accent for the waveform
BG_DARK       = "0x0b0b0b"


def ffmpeg_available() -> bool:
    return shutil.which(os.environ.get("FFMPEG_BIN", "ffmpeg")) is not None


async def make_waveform_video(
    audio_path: str,
    out_path: str,
    cover_path: str | None = None,
    vertical: bool = False,
) -> bool:
    """Render a square (1080x1080) or vertical (1080x1920) waveform video.

    - vertical=True  → Reels / TikTok / Shorts / Snap Spotlight
    - vertical=False → IG feed / square posts
    Returns True on success.
    """
    ffmpeg = os.environ.get("FFMPEG_BIN", "ffmpeg")
    if not ffmpeg_available():
        log.warning("ffmpeg not found — cannot render visualizer.")
        return False

    W, H = (1080, 1920) if vertical else (1080, 1080)
    wave_h = 360
    wave_y = "(H-h)/2" if not cover_path else (H - wave_h - 120)

    if cover_path and os.path.exists(cover_path):
        filter_complex = (
            f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},boxblur=0:0,setsar=1[bg];"
            f"[0:a]showwaves=s={W}x{wave_h}:mode=cline:colors=white:draw=full[w];"
            f"[bg][w]overlay=0:{wave_y}:shortest=1[v]"
        )
        inputs = ["-i", audio_path, "-i", cover_path]
    else:
        filter_complex = (
            f"color=c={BG_DARK}:s={W}x{H}:r=30[bg];"
            f"[0:a]showwaves=s={W}x{wave_h}:mode=cline:colors={CREOVA_MAROON}:draw=full[w];"
            f"[bg][w]overlay=(W-w)/2:(H-h)/2:shortest=1[v]"
        )
        inputs = ["-i", audio_path]

    cmd = [
        ffmpeg, "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", out_path,
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            log.error(f"ffmpeg failed: {stderr.decode()[-400:]}")
            return False
        return os.path.exists(out_path) and os.path.getsize(out_path) > 0
    except Exception as e:
        log.error(f"Visualizer error: {e}")
        return False
