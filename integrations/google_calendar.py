# ============================================================
# GOOGLE CALENDAR INTEGRATION — Akili
# ============================================================
import os
import json
import logging
import aiohttp
import aiofiles
from datetime import datetime, timezone
from aiohttp import web
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

log = logging.getLogger("REACH.GoogleCalendar")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

CREDENTIALS_PATH = "config/calendar_credentials.json"
TOKEN_PATH = "config/calendar_token.json"

_pending: dict = {}

def _redirect_uri() -> str:
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8080")
    return f"https://{domain}/calendar/callback"

async def _load_creds() -> dict | None:
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    async with aiofiles.open(CREDENTIALS_PATH) as f:
        content = await f.read()
        raw = json.loads(content)
    return raw.get("installed") or raw.get("web") or raw

async def handle_calendar_auth(request: web.Request) -> web.Response:
    creds = await _load_creds()
    if not creds:
        return web.Response(text="Credentials file not found.", status=404)

    import urllib.parse, secrets
    state = secrets.token_urlsafe(16)
    _pending[state] = True

    params = {
        "client_id":     creds["client_id"],
        "redirect_uri":  _redirect_uri(),
        "response_type": "code",
        "scope":         " ".join(SCOPES),
        "access_type":   "offline",
        "prompt":        "consent",
        "state":         state,
    }

    auth_url = creds["auth_uri"] + "?" + urllib.parse.urlencode(params)
    raise web.HTTPFound(location=auth_url)

async def handle_calendar_callback(request: web.Request) -> web.Response:
    params  = request.rel_url.query
    error   = params.get("error")
    code    = params.get("code")
    state   = params.get("state")
    
    if state not in _pending:
        return web.Response(text="Invalid state.", status=400)
    del _pending[state]

    if error or not code:
        return web.Response(text=f"Auth failed: {error}", status=400)

    creds = await _load_creds()
    token_data = {
        "code":          code,
        "client_id":     creds["client_id"],
        "client_secret": creds["client_secret"],
        "redirect_uri":  _redirect_uri(),
        "grant_type":    "authorization_code",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(creds["token_uri"], data=token_data) as r:
            result = await r.json()

    if "error" in result:
        return web.Response(text=f"Token exchange failed: {result['error']}", status=400)

    access_token  = result.get("access_token", "")
    refresh_token = result.get("refresh_token", "")

    token_obj = {
        "token":         access_token,
        "refresh_token": refresh_token,
        "token_uri":     creds["token_uri"],
        "client_id":     creds["client_id"],
        "client_secret": creds["client_secret"],
        "scopes":        SCOPES,
        "expiry":        None,
    }
    
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    async with aiofiles.open(TOKEN_PATH, "w") as f:
        await f.write(json.dumps(token_obj, indent=2))
        
    return web.Response(text="Calendar connected successfully! Token saved.")

class GoogleCalendarClient:
    def __init__(self):
        self.service = None
        self._init_service()

    def _init_service(self):
        if not os.path.exists(CREDENTIALS_PATH) or not os.path.exists(TOKEN_PATH):
            log.warning("Calendar not configured (missing credentials or token).")
            return
            
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(TOKEN_PATH, "w") as f:
                        f.write(creds.to_json())
            self.service = build("calendar", "v3", credentials=creds)
            log.info("Google Calendar initialized successfully.")
        except Exception as e:
            log.error(f"Failed to init Calendar: {e}")

    async def get_upcoming_events(self, max_results=10) -> list:
        if not self.service:
            return []
        now = datetime.now(timezone.utc).isoformat()
        try:
            events_result = self.service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception as e:
            log.error(f"Error fetching events: {e}")
            return []
            
    async def create_event(self, summary: str, description: str, start_time: str, end_time: str):
        if not self.service:
            return None
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'America/Toronto'},
            'end': {'dateTime': end_time, 'timeZone': 'America/Toronto'},
        }
        try:
            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            log.info(f"Event created: {event_result.get('htmlLink')}")
            return event_result
        except Exception as e:
            log.error(f"Error creating event: {e}")
            return None
