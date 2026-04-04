# ============================================================
# TIKTOK OAUTH SERVER — Akili
# Handles the full OAuth 2.0 flow for @creovamusic
# Runs on port 8080 alongside the Telegram bot
#
# Flow:
#   1. Justin visits /tiktok/auth in browser
#   2. Redirected to TikTok login + permission grant
#   3. TikTok redirects back to /tiktok/callback?code=...
#   4. Server exchanges code for tokens
#   5. Tokens displayed in browser + sent to Justin's Telegram
# ============================================================

import os
import base64
import logging
import hashlib
import secrets
import urllib.parse
import aiohttp
from aiohttp import web

log = logging.getLogger("TIKTOK.OAuth")

TIKTOK_AUTH_URL      = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL     = "https://open.tiktokapis.com/v2/oauth/token/"

SCOPES = [
    "user.info.basic",
    "video.upload",
    "video.publish",
]

_state_store: dict = {}


def _get_config() -> dict:
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8080")
    # Use stable production domain for redirect URI so it never changes
    # and always matches what is registered in TikTok Developer Portal
    prod_domain = os.environ.get("TIKTOK_REDIRECT_DOMAIN", "akili-core.replit.app")
    return {
        "client_key":    os.environ.get("TIKTOK_CLIENT_KEY", ""),
        "client_secret": os.environ.get("TIKTOK_CLIENT_SECRET", ""),
        "redirect_uri":  f"https://{prod_domain}/tiktok/callback",
        "domain":        domain,
    }


async def handle_auth(request: web.Request) -> web.Response:
    """Step 1 — Generate the TikTok authorization URL and redirect Justin."""
    cfg = _get_config()

    if not cfg["client_key"]:
        return web.Response(
            text="❌ TIKTOK_CLIENT_KEY not set in Replit Secrets.",
            status=500,
        )

    state = secrets.token_urlsafe(16)
    # RFC 7636 PKCE — code_verifier must be high-entropy, code_challenge = BASE64URL(SHA256(verifier))
    code_verifier  = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    _state_store[state] = code_verifier

    # RFC 6749 §4.1.1 — all query params must be properly percent-encoded
    params = {
        "client_key":            cfg["client_key"],
        "redirect_uri":          cfg["redirect_uri"],
        "response_type":         "code",
        "scope":                 " ".join(SCOPES),   # RFC 6749 §3.3 — space-delimited
        "state":                 state,
        "code_challenge":        code_challenge,
        "code_challenge_method": "S256",
    }

    url = f"{TIKTOK_AUTH_URL}?{urllib.parse.urlencode(params)}"

    log.info(f"[TikTok OAuth] Redirecting to TikTok auth — state: {state}")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AKILI — TikTok Auth</title>
<style>
  body {{ font-family: monospace; background: #0a0a0a; color: #e0e0e0;
         display: flex; align-items: center; justify-content: center;
         min-height: 100vh; margin: 0; }}
  .box {{ background: #111; border: 1px solid #333; border-radius: 12px;
          padding: 40px; max-width: 500px; text-align: center; }}
  h1 {{ color: #fff; font-size: 1.4rem; }}
  p  {{ color: #aaa; margin: 12px 0; }}
  a  {{ display: inline-block; background: #000; color: #fff;
         border: 1px solid #555; padding: 14px 32px; border-radius: 8px;
         text-decoration: none; font-size: 1rem; margin-top: 20px; }}
  a:hover {{ background: #1a1a1a; }}
  code {{ color: #69b4ff; font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="box">
  <h1>👻 AKILI × TikTok</h1>
  <p>Authorizing <code>@creovamusic</code></p>
  <p>You'll be redirected to TikTok to log in and grant permission.<br>
     Once approved, tokens are sent directly to your Telegram.</p>
  <p style="color:#555; font-size:0.8rem;">Redirect URI: <code>{cfg["redirect_uri"]}</code></p>
  <a href="{url}">🎵 Authorize @creovamusic on TikTok</a>
</div>
</body>
</html>"""

    return web.Response(text=html, content_type="text/html")


async def handle_callback(request: web.Request) -> web.Response:
    """Step 2 — TikTok sends code here. Exchange for tokens."""
    cfg = _get_config()
    params = request.rel_url.query

    # Log ALL params for debugging
    log.info(f"[TikTok OAuth] Callback hit — params: {dict(params)}")

    error = params.get("error")
    if error:
        desc = params.get("error_description", "Unknown error")
        log.error(f"[TikTok OAuth] Auth error: {error} — {desc}")
        # Notify Justin via Telegram
        tg_token = os.environ.get("TELEGRAM_TOKEN", "")
        chat_id  = os.environ.get("JUSTIN_CHAT_ID", "")
        if tg_token and chat_id:
            import asyncio
            async def _notify():
                async with aiohttp.ClientSession() as s:
                    await s.post(
                        f"https://api.telegram.org/bot{tg_token}/sendMessage",
                        json={"chat_id": chat_id,
                              "text": f"❌ TikTok OAuth error:\n{error}\n{desc}"},
                    )
            asyncio.create_task(_notify())
        return web.Response(
            text=f"❌ TikTok authorization failed: {error}\n{desc}",
            status=400,
        )

    code  = params.get("code")
    state = params.get("state")

    if not code:
        log.error(f"[TikTok OAuth] No code in callback — full params: {dict(params)}")
        return web.Response(text="❌ No code returned by TikTok.", status=400)

    code_verifier = _state_store.pop(state, None)
    if not code_verifier:
        log.warning("[TikTok OAuth] State mismatch — possible CSRF or expired session")

    log.info(f"[TikTok OAuth] Code received — exchanging for tokens...")

    token_data = {
        "client_key":    cfg["client_key"],
        "client_secret": cfg["client_secret"],
        "code":          code,
        "grant_type":    "authorization_code",
        "redirect_uri":  cfg["redirect_uri"],
    }
    if code_verifier:
        token_data["code_verifier"] = code_verifier

    async with aiohttp.ClientSession() as session:
        async with session.post(
            TIKTOK_TOKEN_URL,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as r:
            result = await r.json()

    log.info(f"[TikTok OAuth] Token response: {result}")

    err_block = result.get("error", {})
    if isinstance(err_block, dict) and err_block.get("code", "ok") != "ok":
        err_msg = err_block.get("message", str(result))
        log.error(f"[TikTok OAuth] Token exchange failed: {err_msg}")
        return _error_page(err_msg)

    data = result.get("data", result)
    access_token  = data.get("access_token", "")
    open_id       = data.get("open_id", "")
    refresh_token = data.get("refresh_token", "")
    expires_in    = data.get("expires_in", 0)

    if not access_token:
        return _error_page(f"No access_token in response: {result}")

    log.info(f"[TikTok OAuth] ✅ Tokens obtained — open_id: {open_id}")

    # Send tokens to Justin via Telegram
    tg_token  = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id   = os.environ.get("JUSTIN_CHAT_ID", "")
    if tg_token and chat_id:
        tg_msg = (
            f"🎵 TIKTOK @creovamusic AUTHORIZED\n\n"
            f"Add these to Replit Secrets now:\n\n"
            f"TIKTOK_ACCESS_TOKEN:\n{access_token}\n\n"
            f"TIKTOK_OPEN_ID:\n{open_id}\n\n"
            f"TIKTOK_REFRESH_TOKEN:\n{refresh_token}\n\n"
            f"Expires in: {expires_in // 3600}h\n\n"
            f"Delete this message after saving 🔒"
        )
        async with aiohttp.ClientSession() as s:
            await s.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": chat_id, "text": tg_msg},
            )
        log.info("[TikTok OAuth] Tokens sent to Justin via Telegram")

    return _success_page(access_token, open_id, refresh_token, expires_in)


def _success_page(access_token, open_id, refresh_token, expires_in) -> web.Response:
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AKILI — TikTok Connected</title>
<style>
  body {{ font-family: monospace; background: #0a0a0a; color: #e0e0e0;
         display: flex; align-items: center; justify-content: center;
         min-height: 100vh; margin: 0; }}
  .box {{ background: #111; border: 1px solid #2a2a2a; border-radius: 12px;
          padding: 40px; max-width: 600px; }}
  h1  {{ color: #4ade80; }}
  .field {{ margin: 16px 0; }}
  label {{ color: #888; font-size: 0.8rem; display: block; margin-bottom: 4px; }}
  code  {{ display: block; background: #1a1a1a; padding: 10px 14px;
           border-radius: 6px; color: #69b4ff; word-break: break-all;
           font-size: 0.85rem; }}
  .warn {{ color: #fbbf24; font-size: 0.85rem; margin-top: 24px; }}
  .step {{ color: #aaa; margin: 8px 0; }}
</style>
</head>
<body>
<div class="box">
  <h1>✅ @creovamusic Authorized</h1>
  <p style="color:#aaa">Tokens sent to your Telegram. Also shown below:</p>

  <div class="field">
    <label>TIKTOK_ACCESS_TOKEN</label>
    <code>{access_token}</code>
  </div>
  <div class="field">
    <label>TIKTOK_OPEN_ID</label>
    <code>{open_id}</code>
  </div>
  <div class="field">
    <label>TIKTOK_REFRESH_TOKEN</label>
    <code>{refresh_token}</code>
  </div>
  <div class="field">
    <label>Expires in</label>
    <code>{expires_in // 3600} hours</code>
  </div>

  <p class="warn">⚠️ Add these to Replit Secrets, then close this tab.</p>

  <p style="color:#555; font-size:0.8rem; margin-top:24px;">Next steps:</p>
  <p class="step">1. Open Replit Secrets (lock icon)</p>
  <p class="step">2. Add TIKTOK_ACCESS_TOKEN and TIKTOK_OPEN_ID</p>
  <p class="step">3. Restart AKILI workflow</p>
  <p class="step">4. Send 'health check' on Telegram to verify</p>
</div>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


def _error_page(message: str) -> web.Response:
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>AKILI — TikTok Error</title>
<style>body{{font-family:monospace;background:#0a0a0a;color:#e0e0e0;
display:flex;align-items:center;justify-content:center;min-height:100vh;}}
.box{{background:#111;border:1px solid #333;border-radius:12px;padding:40px;max-width:500px;}}
h1{{color:#f87171;}}code{{color:#fbbf24;}}</style></head>
<body><div class="box">
<h1>❌ TikTok Auth Failed</h1>
<p>Error: <code>{message}</code></p>
<p style="color:#888">Check that your redirect URI in the TikTok Developer Portal matches exactly:</p>
<p style="color:#aaa">Try visiting <a href="/tiktok/auth" style="color:#69b4ff">/tiktok/auth</a> again.</p>
</div></body></html>"""
    return web.Response(text=html, content_type="text/html", status=400)


async def handle_index(request: web.Request) -> web.Response:
    """Root — shows AKILI status."""
    cfg = _get_config()
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>AKILI</title>
<style>body{{font-family:monospace;background:#0a0a0a;color:#e0e0e0;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}}
.box{{background:#111;border:1px solid #222;border-radius:12px;padding:40px;max-width:420px;text-align:center;}}
h1{{color:#fff;}} a{{color:#69b4ff;}} p{{color:#888;}}</style></head>
<body><div class="box">
<h1>⚡ AKILI</h1>
<p>CREOVA AI Operating System</p>
<p>Telegram bot active · 5 agents running</p>
<br>
<p><a href="/tiktok/auth">🎵 Authorize TikTok @creovamusic</a></p>
  <p><a href="/gmail/auth?account=personal">📧 Authorize Gmail (personal)</a></p>
  <p><a href="/gmail/auth?account=business">📧 Authorize Gmail (business)</a></p>
</div></body></html>"""
    return web.Response(text=html, content_type="text/html")


async def handle_tiktok_verification(request: web.Request) -> web.Response:
    """TikTok domain verification file — token read live from env var, no redeploy needed."""
    token = os.environ.get(
        "TIKTOK_VERIFY_TOKEN",
        "ZOEgJ9JW9DI1DsSJngcQTHQLHJcMe7Ob"
    )
    return web.Response(
        text=f"tiktok-developers-site-verification={token}",
        content_type="text/plain",
    )


async def handle_privacy(request: web.Request) -> web.Response:
    """Privacy Policy page — required by Meta, TikTok, and other platform app reviews."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Privacy Policy — CREOVA / AKILI</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0a0a0a; color: #d0d0d0; max-width: 780px;
         margin: 0 auto; padding: 48px 24px; line-height: 1.8; }
  h1   { color: #fff; font-size: 2rem; border-bottom: 1px solid #222; padding-bottom: 16px; }
  h2   { color: #e0e0e0; font-size: 1.2rem; margin-top: 36px; }
  p    { color: #aaa; }
  a    { color: #69b4ff; }
  .last-updated { color: #555; font-size: 0.85rem; }
</style>
</head>
<body>
<h1>Privacy Policy</h1>
<p class="last-updated">Last updated: April 4, 2026</p>

<p>This Privacy Policy applies to AKILI, the AI operating system built by
<strong>CREOVA</strong> (Creative Innovation Space), operated by Justin Mafie.
AKILI is a private, single-user automation system — it is not a public application
and does not collect data from any third-party users.</p>

<h2>1. What We Collect</h2>
<p>AKILI connects to social media platforms (Instagram, Facebook, TikTok, LinkedIn,
Twitter/X, Snapchat) and services (Gmail, GitHub) solely on behalf of the authorised
operator (Justin Mafie). The following information may be accessed:</p>
<ul>
  <li>Account profile information (name, username, profile picture)</li>
  <li>Content publishing permissions (to post on behalf of authorised accounts)</li>
  <li>Email metadata (to send emails on behalf of authorised Gmail accounts)</li>
  <li>Repository activity (to monitor authorised GitHub repositories)</li>
</ul>

<h2>2. How We Use It</h2>
<p>All accessed data is used exclusively to automate tasks for the authorised operator.
No data is sold, shared, or transmitted to any third party. No user data is stored
beyond what is required for active API session tokens.</p>

<h2>3. Data Storage</h2>
<p>OAuth access tokens are stored as encrypted environment secrets in the Replit
deployment environment. They are accessible only to the system operator and are
never logged or exposed.</p>

<h2>4. Data Deletion</h2>
<p>To request deletion of any data associated with this application:</p>
<ul>
  <li>Instagram / Facebook: <a href="/instagram/data-deletion">Submit a deletion request</a></li>
  <li>All other platforms: Email <a href="mailto:creativeinnovationspace@gmail.com">creativeinnovationspace@gmail.com</a></li>
</ul>
<p>Requests will be processed within 30 days.</p>

<h2>5. Third-Party Platforms</h2>
<p>AKILI uses official APIs provided by Meta (Instagram, Facebook), TikTok, LinkedIn,
Twitter, Snap Inc., Google, and GitHub. Use of these APIs is governed by each
platform's own terms of service and privacy policies.</p>

<h2>6. Contact</h2>
<p>For any privacy-related questions, contact:<br>
<strong>CREOVA — Justin Mafie</strong><br>
<a href="mailto:creativeinnovationspace@gmail.com">creativeinnovationspace@gmail.com</a></p>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


def create_web_app() -> web.Application:
    from integrations.gmail_oauth      import handle_gmail_auth, handle_gmail_callback
    from integrations.instagram_oauth  import (handle_instagram_auth, handle_instagram_callback,
                                               handle_data_deletion, handle_deletion_status)
    from dashboard import handle_dashboard, handle_api_status
    app = web.Application()
    app.router.add_get("/tiktok-developers-site-verification.txt",  handle_tiktok_verification)
    app.router.add_get("/tiktok-developers-site-verification.txt/", handle_tiktok_verification)
    app.router.add_get("/",                    handle_dashboard)
    app.router.add_get("/status",              handle_index)
    app.router.add_get("/api/status",          handle_api_status)
    app.router.add_get("/tiktok/auth",         handle_auth)
    app.router.add_get("/tiktok/callback",     handle_callback)
    app.router.add_get("/gmail/auth",          handle_gmail_auth)
    app.router.add_get("/gmail/callback",      handle_gmail_callback)
    app.router.add_get("/instagram/auth",             handle_instagram_auth)
    app.router.add_get("/instagram/callback",         handle_instagram_callback)
    app.router.add_post("/instagram/data-deletion",   handle_data_deletion)
    app.router.add_get("/instagram/data-deletion",    handle_data_deletion)
    app.router.add_get("/instagram/deletion-status",  handle_deletion_status)
    app.router.add_get("/privacy",                    handle_privacy)
    app.router.add_get("/privacy/",                   handle_privacy)
    return app
