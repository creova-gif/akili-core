# ============================================================
# AKILI — MASTER ACCOUNTS CONFIG
# Single source of truth for ALL Justin Mafie + CREOVA handles
# Every integration imports from here
# ============================================================

import os
import json

# ── INSTAGRAM (4 accounts) ────────────────────────────────────
# Credentials load in priority order:
#   1. Replit Secrets (IG_USER_ID_*, IG_TOKEN_*)
#   2. config/instagram_token.json  (written by /instagram/callback)

def _load_ig_token_file() -> dict:
    """Return {username: {ig_id, page_id, page_token}} from the OAuth token file."""
    path = "config/instagram_token.json"
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        result = {}
        for acc in data.get("accounts", []):
            uname = acc.get("username", "").lstrip("@").lower()
            result[uname] = {
                "ig_id":      acc.get("ig_id", ""),
                "page_id":    acc.get("page_id", ""),
                "page_token": acc.get("page_token", ""),
            }
        return result
    except Exception:
        return {}

def _ig_creds(handle_key: str, uname_variant: list[str]) -> tuple[str, str, str]:
    """Return (ig_user_id, page_id, token) from env vars or token file."""
    env_map = {
        "creativeinnovation": ("IG_USER_ID_CREATIVE__",  "IG_PAGE_ID_CREATIVE__",  "IG_TOKEN_CREATIVE__"),
        "jj_mafie":           ("IG_USER_ID_JJ_MAFIE",   "IG_PAGE_ID_JJ_MAFIE",    "IG_TOKEN_JJ_MAFIE"),
        "sankofastudio":      ("IG_USER_ID_SANKOFASTUDIO__", "IG_PAGE_ID_SANKOFASTUDIO__", "IG_TOKEN_SANKOFASTUDIO__"),
        "creovasolutions":    ("IG_USER_ID_CREOVASOLUTIONS", "IG_PAGE_ID_CREOVASOLUTIONS", "IG_TOKEN_CREOVASOLUTIONS"),
    }
    uid_key, pid_key, tok_key = env_map.get(handle_key, ("","",""))
    uid = os.environ.get(uid_key, "")
    pid = os.environ.get(pid_key, "")
    tok = os.environ.get(tok_key, "")
    if uid and tok:
        return uid, pid, tok
    # Fall back to token file
    file_data = _load_ig_token_file()
    for variant in uname_variant:
        if variant in file_data:
            d = file_data[variant]
            return d["ig_id"], d["page_id"], d["page_token"]
    return "", "", ""

_creative_uid, _creative_pid, _creative_tok = _ig_creds(
    "creativeinnovation", ["creativeinnovation__", "creativeinnovation"])
_jj_uid, _jj_pid, _jj_tok = _ig_creds(
    "jj_mafie", ["jj_mafie"])
_sankofa_uid, _sankofa_pid, _sankofa_tok = _ig_creds(
    "sankofastudio", ["sankofastudio__", "sankofastudio"])
_solutions_uid, _solutions_pid, _solutions_tok = _ig_creds(
    "creovasolutions", ["creovasolutions"])

INSTAGRAM_ACCOUNTS = {
    "creativeinnovation": {
        "handle": "@creativeinnovation__",
        "purpose": "CREOVA Music + Media — primary music/creative account",
        "ig_user_id": _creative_uid,
        "page_id":    _creative_pid,
        "token":      _creative_tok,
    },
    "jj_mafie": {
        "handle": "@jj_mafie",
        "purpose": "Justin Mafie personal brand",
        "ig_user_id": _jj_uid,
        "page_id":    _jj_pid,
        "token":      _jj_tok,
    },
    "sankofastudio": {
        "handle": "@sankofastudio__",
        "purpose": "Sankofa Studio — production studio",
        "ig_user_id": _sankofa_uid,
        "page_id":    _sankofa_pid,
        "token":      _sankofa_tok,
    },
    "creovasolutions": {
        "handle": "@creovasolutions",
        "purpose": "CREOVA Solutions — emerging global tech company",
        "ig_user_id": _solutions_uid,
        "page_id":    _solutions_pid,
        "token":      _solutions_tok,
    },
}

# ── LINKEDIN (2 accounts) ─────────────────────────────────────
LINKEDIN_ACCOUNTS = {
    "justin_mafie": {
        "label": "Justin Mafie",
        "type": "personal",
        "urn":   os.environ.get("LINKEDIN_PERSON_URN", ""),
        "token": os.environ.get("LINKEDIN_ACCESS_TOKEN", ""),
    },
    "creova_page": {
        "label": "CREOVA (company page)",
        "type": "company",
        "urn":   os.environ.get("LINKEDIN_COMPANY_URN", ""),
        "token": os.environ.get("LINKEDIN_ACCESS_TOKEN", ""),
    },
}

# ── TWITTER / X (1 account) ───────────────────────────────────
TWITTER_ACCOUNT = {
    "handle": "@justin_mafie",
    "label": "Justin Mafie",
    "api_key":             os.environ.get("TWITTER_API_KEY", ""),
    "api_secret":          os.environ.get("TWITTER_API_SECRET", ""),
    "access_token":        os.environ.get("TWITTER_ACCESS_TOKEN", ""),
    "access_token_secret": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", ""),
    "bearer_token":        os.environ.get("TWITTER_BEARER_TOKEN", ""),
}

# ── SNAPCHAT (1 account) ──────────────────────────────────────
SNAPCHAT_ACCOUNT = {
    "handle": "jay-mafie",
    "label": "Justin Mafie Snapchat",
    "goal": "Snapchat Creator program",
    "client_id":     os.environ.get("SNAPCHAT_CLIENT_ID", ""),
    "client_secret": os.environ.get("SNAPCHAT_CLIENT_SECRET", ""),
    "access_token":  os.environ.get("SNAPCHAT_ACCESS_TOKEN", ""),
}

# ── FACEBOOK (2 accounts) ─────────────────────────────────────
FACEBOOK_ACCOUNTS = {
    "justin_personal": {
        "label": "Justin Mafie (personal)",
        "type": "personal",
        "page_id": os.environ.get("FB_PAGE_ID_JUSTIN", ""),
        "token":   os.environ.get("FB_TOKEN_JUSTIN", ""),
    },
    "creova_business": {
        "label": "CREOVA (business account)",
        "type": "business",
        "page_id": os.environ.get("FB_PAGE_ID_CREOVA", ""),
        "token":   os.environ.get("FB_TOKEN_CREOVA", ""),
    },
}

# ── TIKTOK (1 account) ────────────────────────────────────────
TIKTOK_ACCOUNT = {
    "handle": "@creovamusic",
    "label": "CREOVA Music TikTok",
    "client_key":    os.environ.get("TIKTOK_CLIENT_KEY", ""),
    "client_secret": os.environ.get("TIKTOK_CLIENT_SECRET", ""),
    "access_token":  os.environ.get("TIKTOK_ACCESS_TOKEN", ""),
    "open_id":       os.environ.get("TIKTOK_OPEN_ID", ""),
}

# ── EMAIL (2 accounts) ────────────────────────────────────────
EMAIL_ACCOUNTS = {
    "personal": {
        "label": "Justin Mafie personal Gmail",
        "address": os.environ.get("GMAIL_PERSONAL_ADDRESS", "ayoubjustin2@gmail.com"),
        "credentials_path": "config/gmail_personal_credentials.json",
        "token_path":       "config/gmail_personal_token.json",
    },
    "business": {
        "label": "CREOVA business email",
        "address": os.environ.get("GMAIL_BUSINESS_ADDRESS", "creativeinnovationspace@gmail.com"),
        "credentials_path": "config/gmail_business_credentials.json",
        "token_path":       "config/gmail_business_token.json",
    },
}

# ── GITHUB ────────────────────────────────────────────────────
GITHUB_CONFIG = {
    "org": "creova-gif",
    "token": os.environ.get("GITHUB_TOKEN", ""),
    # Active repos in the creova-gif account (8 confirmed live)
    "repos": [
        "Gopay",
        "KayaYourpropertyai",
        "Darsme",
        "Mentalpath",
        "Aihealthsupport",
        "GridOs",
        "Kilimoai",
        "Budgeteaseapp",
        # Repos to be created: QuickBookSample, HealthFitness, RecommendedPeptides,
        #                       SEEN, WazaWealth, Mskniagara
    ],
}

# ── MUSIC DISTRIBUTION ────────────────────────────────────────
MUSIC_CONFIG = {
    "artist_name": "Justin Mafie",
    "label": "CREOVA Music",
    "studio": "Sankofa Studio",
    "distributor": "DistroKid",
    "platforms": ["Spotify", "Apple Music", "TikTok", "YouTube Music", "Amazon Music"],
    "primary_promo_handles": ["@creativeinnovation__", "@sankofastudio__", "@creovamusic"],
}

# ── WEBSITE ───────────────────────────────────────────────────
CREOVA_WEBSITE = "https://creova.one"

# ── CONTENT CROSS-PROMOTION RULE ─────────────────────────────
CROSS_PROMO_TAGS = [
    "@creativeinnovation__",
    "@creovasolutions",
    "@sankofastudio__",
    "@creovamusic",
    "creova.one",
]

# ── POSTING SCHEDULE (optimal times per platform) ─────────────
POSTING_SCHEDULE = {
    "instagram":  ["9:00", "12:00", "15:00", "18:00", "21:00"],
    "twitter":    ["8:00", "10:00", "13:00", "16:00", "19:00", "22:00"],
    "linkedin":   ["8:00", "12:00", "17:00"],
    "tiktok":     ["7:00", "11:00", "14:00", "17:00", "20:00", "23:00"],
    "snapchat":   ["10:00", "14:00", "18:00", "21:00"],
    "facebook":   ["9:00", "13:00", "18:00"],
}

# ── WEEKLY CONTENT THEMES ─────────────────────────────────────
WEEKLY_THEMES = {
    "monday":    {"name": "Music Monday",     "focus": "new releases, studio sessions, CREOVA Music"},
    "tuesday":   {"name": "Tech Tuesday",     "focus": "CREOVA Solutions, products, African tech innovation"},
    "wednesday": {"name": "Wisdom Wednesday", "focus": "branding tips, founder lessons, creative insights"},
    "thursday":  {"name": "Throwback",        "focus": "journey, growth story, past milestones"},
    "friday":    {"name": "Fresh Friday",     "focus": "new drops, announcements, upcoming projects"},
    "saturday":  {"name": "Studio Saturday",  "focus": "Sankofa Studio, production process, behind scenes"},
    "sunday":    {"name": "Founder Sunday",   "focus": "Justin Mafie personal brand, vision, reflection"},
}

# ── CONTENT MIX ───────────────────────────────────────────────
CONTENT_MIX = {
    "music":     0.30,
    "tech":      0.30,
    "personal":  0.20,
    "education": 0.20,
}
