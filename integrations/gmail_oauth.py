# ============================================================
# GMAIL OAUTH SERVER — Akili
# Browser-based OAuth flow for Gmail accounts
#
# Flow:
#   1. Justin visits /gmail/auth?account=personal in browser
#   2. Redirected to Google login (any Gmail account — no dev link)
#   3. Google redirects back to /gmail/callback
#   4. Token saved to config/ and confirmation sent to Telegram
# ============================================================

import os
import json
import logging
import aiohttp
from aiohttp import web

log = logging.getLogger("REACH.GmailOAuth")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

CREDENTIALS = {
    "personal": "config/gmail_personal_credentials.json",
    "business": "config/gmail_business_credentials.json",
}
TOKENS = {
    "personal": "config/gmail_personal_token.json",
    "business": "config/gmail_business_token.json",
}

_pending: dict = {}


def _redirect_uri() -> str:
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8080")
    return f"https://{domain}/gmail/callback"


def _load_creds(account: str) -> dict | None:
    path = CREDENTIALS.get(account)
    if not path or not os.path.exists(path):
        return None
    with open(path) as f:
        raw = json.load(f)
    return raw.get("installed") or raw.get("web") or raw


async def handle_gmail_auth(request: web.Request) -> web.Response:
    """Step 1 — Build Google OAuth URL and redirect Justin."""
    account = request.rel_url.query.get("account", "personal")
    creds = _load_creds(account)

    if not creds:
        return web.Response(
            text=f"❌ Credentials file not found for '{account}' account.\n"
                 f"Expected: {CREDENTIALS.get(account)}",
            status=404,
        )

    import urllib.parse, secrets
    state = secrets.token_urlsafe(16)
    _pending[state] = account

    redirect_uri = _redirect_uri()

    params = {
        "client_id":     creds["client_id"],
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         " ".join(SCOPES),
        "access_type":   "offline",
        "prompt":        "consent",
        "state":         state,
    }

    auth_url = creds["auth_uri"] + "?" + urllib.parse.urlencode(params)

    log.info(f"[Gmail OAuth] Redirecting to Google auth — account: {account}")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AKILI — Gmail Auth</title>
<meta http-equiv="refresh" content="2;url={auth_url}">
<style>
  body {{ font-family: monospace; background: #0a0a0a; color: #e0e0e0;
         display: flex; align-items: center; justify-content: center;
         min-height: 100vh; margin: 0; }}
  .box {{ background: #111; border: 1px solid #333; border-radius: 12px;
          padding: 40px; max-width: 500px; text-align: center; }}
  h1 {{ color: #fff; }} p {{ color: #aaa; }}
  code {{ color: #69b4ff; font-size: 0.82rem; word-break: break-all; }}
  .note {{ color: #555; font-size: 0.78rem; margin-top: 20px; }}
</style>
</head>
<body>
<div class="box">
  <h1>📧 AKILI × Gmail</h1>
  <p>Connecting <strong>{account}</strong> Gmail account...</p>
  <p>Redirecting to Google in 2 seconds.</p>
  <p>Log in with <strong>whichever Gmail you want to connect</strong>.<br>
     Your Google Cloud account stays completely separate.</p>
  <p class="note">Redirect URI: <code>{redirect_uri}</code></p>
  <p style="margin-top:20px"><a href="{auth_url}" style="color:#69b4ff">
     → Click here if not redirected automatically</a></p>
</div>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


async def handle_gmail_callback(request: web.Request) -> web.Response:
    """Step 2 — Exchange code for tokens and save to disk."""
    params  = request.rel_url.query
    error   = params.get("error")
    code    = params.get("code")
    state   = params.get("state")
    account = _pending.pop(state, "personal")

    if error:
        log.error(f"[Gmail OAuth] Error: {error}")
        return _error_page(error, account)

    if not code:
        return _error_page("No authorization code returned by Google.", account)

    creds = _load_creds(account)
    if not creds:
        return _error_page(f"Credentials file missing for '{account}'.", account)

    redirect_uri = _redirect_uri()
    log.info(f"[Gmail OAuth] Exchanging code for tokens — account: {account}")

    token_data = {
        "code":          code,
        "client_id":     creds["client_id"],
        "client_secret": creds["client_secret"],
        "redirect_uri":  redirect_uri,
        "grant_type":    "authorization_code",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(creds["token_uri"], data=token_data) as r:
            result = await r.json()

    if "error" in result:
        err = result.get("error_description", result["error"])
        log.error(f"[Gmail OAuth] Token exchange failed: {err}")
        return _error_page(err, account)

    access_token  = result.get("access_token", "")
    refresh_token = result.get("refresh_token", "")
    expires_in    = result.get("expires_in", 3600)
    scope         = result.get("scope", "")

    # Fetch email address to confirm which account was connected
    email = ""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as r:
            profile = await r.json()
            email = profile.get("email", "unknown")

    # Save token file in google-auth format
    token_obj = {
        "token":         access_token,
        "refresh_token": refresh_token,
        "token_uri":     creds["token_uri"],
        "client_id":     creds["client_id"],
        "client_secret": creds["client_secret"],
        "scopes":        SCOPES,
        "expiry":        None,
    }
    token_path = TOKENS[account]
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w") as f:
        json.dump(token_obj, f, indent=2)

    log.info(f"[Gmail OAuth] ✅ Token saved → {token_path} | Email: {email}")

    # Send confirmation to Justin via Telegram
    tg_token = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id  = os.environ.get("JUSTIN_CHAT_ID", "")
    if tg_token and chat_id:
        msg = (
            f"📧 GMAIL CONNECTED — {account.upper()}\n\n"
            f"✅ Account: {email}\n"
            f"Token saved to: {token_path}\n\n"
            f"Add to Replit Secrets:\n"
            f"GMAIL_{account.upper()}_ADDRESS = {email}\n\n"
            f"Then restart AKILI — Gmail is live."
        )
        async with aiohttp.ClientSession() as s:
            await s.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": chat_id, "text": msg},
            )

    return _success_page(account, email, token_path)


def _success_page(account: str, email: str, token_path: str) -> web.Response:
    secret_key = f"GMAIL_{account.upper()}_ADDRESS"
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>AKILI — Gmail Connected</title>
<style>
  body {{ font-family: monospace; background: #0a0a0a; color: #e0e0e0;
         display:flex; align-items:center; justify-content:center;
         min-height:100vh; margin:0; }}
  .box {{ background:#111; border:1px solid #2a2a2a; border-radius:12px;
          padding:40px; max-width:560px; }}
  h1 {{ color:#4ade80; }} p {{ color:#aaa; }}
  code {{ display:block; background:#1a1a1a; padding:10px 14px;
          border-radius:6px; color:#69b4ff; margin:6px 0; font-size:0.85rem; }}
  .step {{ color:#ccc; margin:8px 0; }} .warn {{ color:#fbbf24; }}
</style></head>
<body><div class="box">
  <h1>✅ Gmail {account.capitalize()} Connected</h1>
  <p>Authorized account: <strong>{email}</strong></p>
  <p>Token saved to: <code>{token_path}</code></p>
  <p>Details sent to your Telegram.</p>
  <br>
  <p class="warn">⚠️ One more step — add this to Replit Secrets:</p>
  <p>Key: <code>{secret_key}</code></p>
  <p>Value: <code>{email}</code></p>
  <br>
  <p class="step">1. Open Replit Secrets (lock icon on sidebar)</p>
  <p class="step">2. Add {secret_key} = {email}</p>
  <p class="step">3. Restart AKILI workflow</p>
  <p class="step">4. Gmail read/send is now live for AKILI</p>
  <br>
  <p>Connect business email:
     <a href="/gmail/auth?account=business" style="color:#69b4ff">
     /gmail/auth?account=business</a></p>
</div></body></html>"""
    return web.Response(text=html, content_type="text/html")


def _error_page(message: str, account: str) -> web.Response:
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>AKILI — Gmail Error</title>
<style>body{{font-family:monospace;background:#0a0a0a;color:#e0e0e0;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}}
.box{{background:#111;border:1px solid #333;border-radius:12px;padding:40px;max-width:500px;}}
h1{{color:#f87171;}} code{{color:#fbbf24;background:#1a1a1a;padding:8px;border-radius:4px;display:block;}}
p{{color:#aaa;}}</style></head>
<body><div class="box">
<h1>❌ Gmail Auth Failed</h1>
<p>Error: <code>{message}</code></p>
<p>If you see a <strong>redirect_uri_mismatch</strong> error, add this to your
   Google Cloud OAuth client's authorized redirect URIs:</p>
<code>{_redirect_uri()}</code>
<p style="margin-top:20px">
  <a href="/gmail/auth?account={account}" style="color:#69b4ff">↩ Try again</a></p>
</div></body></html>"""
    return web.Response(text=html, content_type="text/html", status=400)
