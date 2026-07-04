# ============================================================
# AI MODELS — single source of truth for which Claude model each
# call site uses. Was previously hardcoded ("claude-sonnet-4-5",
# "claude-opus-4-5") in half a dozen files; centralizing here means
# a model upgrade is a one-line change instead of a grep-and-replace.
# ============================================================

import os

# Used by PULSE / REACH / INTEL for content generation, research, and
# web-search-backed calls.
MODEL = os.environ.get("AKILI_MODEL", "claude-sonnet-4-5")

# Used by the GENERAL fallback handler (whole-identity system prompt,
# no specific agent route matched).
GENERAL_MODEL = os.environ.get("AKILI_GENERAL_MODEL", "claude-opus-4-5")
