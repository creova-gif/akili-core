# ============================================================
# AKILI — MASTER ACCOUNTS CONFIG
# Single source of truth for ALL Justin Mafie + CREOVA handles
# Every integration imports from here
# ============================================================

import os

# ── INSTAGRAM (4 accounts) ────────────────────────────────────
INSTAGRAM_ACCOUNTS = {
    "creativeinnovation": {
        "handle": "@creativeinnovation__",
        "purpose": "CREOVA Music + Media — primary music/creative account",
        "ig_user_id": os.environ.get("IG_USER_ID_CREATIVE", ""),
        "page_id":    os.environ.get("IG_PAGE_ID_CREATIVE", ""),
        "token":      os.environ.get("IG_TOKEN_CREATIVE", ""),
    },
    "jj_mafie": {
        "handle": "@jj_mafie",
        "purpose": "Justin Mafie personal brand",
        "ig_user_id": os.environ.get("IG_USER_ID_JJ", ""),
        "page_id":    os.environ.get("IG_PAGE_ID_JJ", ""),
        "token":      os.environ.get("IG_TOKEN_JJ", ""),
    },
    "sankofastudio": {
        "handle": "@sankofastudio__",
        "purpose": "Sankofa Studio — production studio",
        "ig_user_id": os.environ.get("IG_USER_ID_SANKOFA", ""),
        "page_id":    os.environ.get("IG_PAGE_ID_SANKOFA", ""),
        "token":      os.environ.get("IG_TOKEN_SANKOFA", ""),
    },
    "creovasolutions": {
        "handle": "@creovasolutions",
        "purpose": "CREOVA Solutions — emerging global tech company",
        "ig_user_id": os.environ.get("IG_USER_ID_SOLUTIONS", ""),
        "page_id":    os.environ.get("IG_PAGE_ID_SOLUTIONS", ""),
        "token":      os.environ.get("IG_TOKEN_SOLUTIONS", ""),
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
        "address": os.environ.get("GMAIL_PERSONAL_ADDRESS", ""),
        "credentials_path": "config/gmail_personal_credentials.json",
        "token_path":       "config/gmail_personal_token.json",
    },
    "business": {
        "label": "CREOVA business email",
        "address": os.environ.get("GMAIL_BUSINESS_ADDRESS", ""),
        "credentials_path": "config/gmail_business_credentials.json",
        "token_path":       "config/gmail_business_token.json",
    },
}

# ── GITHUB ────────────────────────────────────────────────────
GITHUB_CONFIG = {
    "org": "creova-gif",
    "token": os.environ.get("GITHUB_TOKEN", ""),
    "repos": [
        "GoPay", "KayaYourPropertyAI", "Darsme", "MentalPath",
        "QuickBookSample", "AIHealthSupport", "GridOS", "KilimoAI",
        "BudgetEaseApp", "HealthFitness", "RecommendedPeptides",
        "SEEN", "WazaWealth", "Mskniagara",
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
