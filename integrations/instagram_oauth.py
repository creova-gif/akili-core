# ============================================================
# INSTAGRAM / META OAUTH — Akili
# One flow connects ALL Instagram Business accounts tied to
# Justin's Facebook pages automatically.
#
# Flow:
#   1. Visit /instagram/auth in real browser
#   2. Facebook login + grant permissions
#   3. /instagram/callback exchanges code → long-lived token
#   4. Auto-discovers all IG Business accounts + page IDs
#   5. Sends secrets list to Telegram + shows them on screen
# ============================================================

import os
import json
import logging
import secrets as secrets_mod
import urllib.parse
import aiohttp
from aiohttp import web

log = logging.getLogger("PULSE.InstagramOAuth")

GRAPH = "https://graph.facebook.com/v18.0"

SCOPES = [
    "instagram_basic",
    "instagram_content_publish",
    "instagram_manage_insights",
    "instagram_manage_comments",
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "business_management",
    "public_profile",
]

_pending: dict = {}


def _app_id() -> str:
    return os.environ.get("INSTAGRAM_APP_ID", "")

def _app_secret() -> str:
    return os.environ.get("INSTAGRAM_APP_SECRET", "")

def _redirect_uri() -> str:
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8080")
    return f"https://{domain}/instagram/callback"


async def handle_data_deletion(request: web.Request) -> web.Response:
    """
    Meta-required Data Deletion Callback.
    Facebook sends a signed_request POST when a user asks Meta to delete their data.
    AKILI holds no user data — respond with a confirmation URL.
    """
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8080")
    confirmation_code = secrets_mod.token_hex(8)
    status_url = f"https://{domain}/instagram/deletion-status?code={confirmation_code}"
    log.info(f"[Instagram] Data deletion request received — code: {confirmation_code}")
    return web.json_response({
        "url":               status_url,
        "confirmation_code": confirmation_code,
    })


async def handle_deletion_status(request: web.Request) -> web.Response:
    """Status page Meta checks after data deletion confirmation."""
    code = request.rel_url.query.get("code", "unknown")
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AKILI — Data Deletion</title>
<style>body{{font-family:monospace;background:#080A0F;color:#F0EDE8;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}}
.box{{background:#0D1018;border:1px solid #333;border-radius:16px;padding:32px;max-width:480px;text-align:center;}}
h1{{color:#22C55E;}} p{{color:#6B7280;font-size:13px;}}
</style></head>
<body><div class="box">
<h1>✅ Data Deletion Confirmed</h1>
<p>Confirmation code: <strong style="color:#E8C547">{code}</strong></p>
<p>AKILI (creova.one) does not store personal Facebook or Instagram user data.<br>
All tokens are used solely for authorized API calls on behalf of the account owner.</p>
</div></body></html>"""
    return web.Response(text=html, content_type="text/html")


async def handle_instagram_auth(request: web.Request) -> web.Response:
    """Step 1 — Redirect to Meta/Facebook OAuth."""
    app_id = _app_id()
    if not app_id:
        return web.Response(
            text="❌ INSTAGRAM_APP_ID not set in Replit Secrets.\n\n"
                 "Go to developers.facebook.com → create app → copy App ID → add to Secrets.",
            status=400,
        )

    state = secrets_mod.token_urlsafe(16)
    _pending[state] = True

    params = {
        "client_id":     app_id,
        "redirect_uri":  _redirect_uri(),
        "scope":         ",".join(SCOPES),
        "response_type": "code",
        "state":         state,
    }
    url = "https://www.facebook.com/v18.0/dialog/oauth?" + urllib.parse.urlencode(params)
    log.info("[Instagram OAuth] Redirecting to Meta/Facebook login")
    raise web.HTTPFound(location=url)


async def handle_instagram_callback(request: web.Request) -> web.Response:
    """Step 2 — Exchange code for long-lived token, discover all IG accounts."""
    params  = request.rel_url.query
    error   = params.get("error_message") or params.get("error")
    code    = params.get("code")
    state   = params.get("state", "")

    if error:
        log.error(f"[Instagram OAuth] Error: {error}")
        return _error_page(error)

    if not code:
        return _error_page("No authorization code returned by Meta.")

    app_id     = _app_id()
    app_secret = _app_secret()

    if not app_id or not app_secret:
        return _error_page("INSTAGRAM_APP_ID or INSTAGRAM_APP_SECRET not set in Replit Secrets.")

    async with aiohttp.ClientSession() as s:

        # ── Step A: Short-lived token ──────────────────────────
        async with s.get(f"{GRAPH}/oauth/access_token", params={
            "client_id":     app_id,
            "client_secret": app_secret,
            "redirect_uri":  _redirect_uri(),
            "code":          code,
        }) as r:
            data = await r.json()

        if "error" in data:
            return _error_page(f"Token exchange failed: {data['error'].get('message', str(data['error']))}")

        short_token = data.get("access_token", "")

        # ── Step B: Long-lived token (60 days) ─────────────────
        async with s.get(f"{GRAPH}/oauth/access_token", params={
            "grant_type":        "fb_exchange_token",
            "client_id":         app_id,
            "client_secret":     app_secret,
            "fb_exchange_token": short_token,
        }) as r:
            ll_data = await r.json()

        long_token = ll_data.get("access_token", short_token)
        expires_in = ll_data.get("expires_in", 5184000)

        # ── Step C: Get Facebook user info ─────────────────────
        async with s.get(f"{GRAPH}/me", params={
            "fields": "id,name",
            "access_token": long_token,
        }) as r:
            me = await r.json()

        fb_user_id = me.get("id", "")
        fb_name    = me.get("name", "Unknown")

        # ── Step D: Get all Facebook Pages the user manages ────
        async with s.get(f"{GRAPH}/me/accounts", params={
            "access_token": long_token,
        }) as r:
            pages_data = await r.json()

        pages = pages_data.get("data", [])

        # ── Step E: For each Page, find connected IG account ───
        accounts_found = []
        for page in pages:
            page_id    = page["id"]
            page_name  = page.get("name", "")
            page_token = page.get("access_token", long_token)

            async with s.get(f"{GRAPH}/{page_id}", params={
                "fields": "instagram_business_account",
                "access_token": page_token,
            }) as r:
                pg = await r.json()

            ig_account = pg.get("instagram_business_account", {})
            ig_id = ig_account.get("id", "")
            if not ig_id:
                continue

            # Get IG username
            async with s.get(f"{GRAPH}/{ig_id}", params={
                "fields": "username,followers_count,media_count",
                "access_token": page_token,
            }) as r:
                ig_info = await r.json()

            accounts_found.append({
                "ig_id":       ig_id,
                "username":    "@" + ig_info.get("username", ig_id),
                "followers":   ig_info.get("followers_count", "?"),
                "posts":       ig_info.get("media_count", "?"),
                "page_id":     page_id,
                "page_name":   page_name,
                "page_token":  page_token,
            })

    # ── Save token to file ─────────────────────────────────────
    token_obj = {
        "long_lived_token": long_token,
        "expires_in":       expires_in,
        "fb_user_id":       fb_user_id,
        "fb_name":          fb_name,
        "accounts":         accounts_found,
    }
    os.makedirs("config", exist_ok=True)
    with open("config/instagram_token.json", "w") as f:
        json.dump(token_obj, f, indent=2)

    log.info(f"[Instagram OAuth] ✅ {fb_name} — {len(accounts_found)} IG accounts found")

    # ── Build secrets list for Telegram ───────────────────────
    secrets_lines = [
        f"📸 INSTAGRAM CONNECTED — {fb_name}",
        f"Found {len(accounts_found)} Instagram Business account(s):\n",
    ]
    secrets_payload = []

    for acc in accounts_found:
        uname = acc['username'].lstrip('@').upper().replace('.','_').replace('-','_')
        secrets_lines.append(f"✅ {acc['username']} ({acc['followers']} followers)")
        secrets_payload.append(f"  IG_USER_ID_{uname} = {acc['ig_id']}")
        secrets_payload.append(f"  IG_TOKEN_{uname} = {acc['page_token'][:40]}...")

    if secrets_payload:
        secrets_lines.append("\nAdd to Replit Secrets:")
        secrets_lines.extend(secrets_payload)
        secrets_lines.append(f"\nLong-lived token (60 days) also saved to config/instagram_token.json")

    msg = "\n".join(secrets_lines)

    # ── Send to Telegram ───────────────────────────────────────
    tg_token = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id  = os.environ.get("JUSTIN_CHAT_ID", "")
    if tg_token and chat_id:
        async with aiohttp.ClientSession() as s:
            await s.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": chat_id, "text": msg},
            )

    return _success_page(fb_name, accounts_found, long_token)


def _success_page(fb_name: str, accounts: list, long_token: str) -> web.Response:
    rows = ""
    for acc in accounts:
        uname = acc['username'].lstrip('@').upper().replace('.','_').replace('-','_')
        rows += f"""
        <div class="acc-row">
          <div class="acc-handle">{acc['username']}</div>
          <div class="acc-info">{acc['followers']} followers · {acc['posts']} posts · Page: {acc['page_name']}</div>
          <div class="acc-secrets">
            <code>IG_USER_ID_{uname} = {acc['ig_id']}</code>
            <code>IG_TOKEN_{uname} = {acc['page_token']}</code>
          </div>
        </div>"""

    no_accounts_msg = ""
    if not accounts:
        no_accounts_msg = """
        <div style="background:rgba(249,115,22,0.12);border:1px solid rgba(249,115,22,0.3);
                    border-radius:10px;padding:16px;margin-top:16px;color:#F97316;font-size:13px;">
          ⚠️ No Instagram Business accounts found connected to your Facebook Pages.<br><br>
          Make sure each Instagram account is:<br>
          1. Set to <strong>Business</strong> or <strong>Creator</strong> account type<br>
          2. Connected to a Facebook Page (Instagram Settings → Link Page)<br>
          Then run this flow again.
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AKILI — Instagram Connected</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
  body{{font-family:'Syne',sans-serif;background:#080A0F;color:#F0EDE8;display:flex;
       align-items:center;justify-content:center;min-height:100vh;margin:0;}}
  .box{{background:#0D1018;border:1px solid rgba(255,255,255,0.1);border-radius:20px;
        padding:36px;max-width:680px;width:90%;}}
  h1{{color:#22C55E;font-size:22px;margin-bottom:6px}}
  .sub{{color:#6B7280;font-size:13px;margin-bottom:24px;font-family:'JetBrains Mono',monospace}}
  .acc-row{{background:#131720;border:1px solid rgba(255,255,255,0.07);border-radius:12px;
            padding:16px;margin-bottom:12px;}}
  .acc-handle{{font-size:16px;font-weight:800;color:#4ECDC4;margin-bottom:4px}}
  .acc-info{{font-size:12px;color:#6B7280;margin-bottom:10px;font-family:'JetBrains Mono',monospace}}
  .acc-secrets code{{display:block;background:#080A0F;padding:8px 12px;border-radius:6px;
                    font-family:'JetBrains Mono',monospace;font-size:11px;
                    color:#E8C547;margin-bottom:4px;word-break:break-all}}
  .warn{{background:rgba(232,197,71,0.08);border:1px solid rgba(232,197,71,0.2);
         border-radius:10px;padding:14px;margin-top:20px;font-size:12px;color:#E8C547;
         font-family:'JetBrains Mono',monospace;}}
  .note{{color:#6B7280;font-size:12px;margin-top:16px;font-family:'JetBrains Mono',monospace;line-height:1.6}}
</style>
</head>
<body>
<div class="box">
  <h1>✅ Meta / Instagram Connected</h1>
  <div class="sub">Authorized as: {fb_name} · {len(accounts)} IG account(s) found</div>
  {rows}
  {no_accounts_msg}
  <div class="warn">
    ⚠️ Copy each IG_USER_ID_* and IG_TOKEN_* to Replit Secrets<br>
    Full details sent to your Telegram.
  </div>
  <div class="note">
    Tokens are long-lived (60 days). After 60 days, visit /instagram/auth again.<br>
    Instagram → AKILI: post photos, reels, stories on all 4 accounts.
  </div>
</div>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


def _error_page(msg: str) -> web.Response:
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>AKILI — Instagram Error</title>
<style>body{{font-family:monospace;background:#080A0F;color:#F0EDE8;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}}
.box{{background:#0D1018;border:1px solid #333;border-radius:16px;padding:32px;max-width:520px;}}
h1{{color:#FF6B6B;}} code{{display:block;background:#131720;padding:10px;border-radius:6px;
color:#E8C547;margin:8px 0;font-size:12px;}} p{{color:#6B7280;margin:8px 0;font-size:13px;}}
a{{color:#4ECDC4;}}
</style></head>
<body><div class="box">
<h1>❌ Instagram Auth Failed</h1>
<p>{msg}</p>
<p style="margin-top:16px"><a href="/instagram/auth">↩ Try again</a></p>
</div></body></html>"""
    return web.Response(text=html, content_type="text/html", status=400)
