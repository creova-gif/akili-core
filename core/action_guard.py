# ============================================================
# ACTION GUARD — code-level confirmation gate for destructive actions
#
# MEMORY.md's "never delete without confirming twice" rule used to live
# only in the system prompt handed to the model — a model can forget or
# be talked out of a prompt rule. This makes it a code guarantee instead:
# route_command() in main.py checks looks_destructive() on every message
# BEFORE any agent sees it, and if it matches, the action is proposed
# (not executed) and only runs if the exact CONFIRM token comes back.
# ============================================================

import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone

log = logging.getLogger("CORE.ActionGuard")

_DESTRUCTIVE_PATTERNS = [
    r"\bdelete\b", r"\bremove\b", r"\bwipe\b", r"\bdrop\b", r"\bpurge\b",
    r"\buninstall\b", r"\brevoke\b", r"\bdeactivate\b", r"\bdisable\b",
    r"\bshut ?down\b", r"\bterminate\b", r"\bunsubscribe\b", r"\bkill\b",
    r"\bforce[- ]?push\b", r"\bhard reset\b", r"\bcancel\b.*\baccount\b",
    r"\bwipe out\b", r"\berase\b",
]
_DESTRUCTIVE_RE = re.compile("|".join(_DESTRUCTIVE_PATTERNS), re.IGNORECASE)

_CONFIRM_RE = re.compile(r"^\s*confirm\s+([a-f0-9]{6,12})\s*$", re.IGNORECASE)


def looks_destructive(text: str) -> bool:
    """True if the message matches a pattern that implies an irreversible,
    real-world action (delete/wipe/revoke/etc). Deliberately broad —
    false positives just cost Justin one extra CONFIRM reply; false
    negatives are the thing MEMORY.md exists to prevent."""
    return bool(_DESTRUCTIVE_RE.search(text or ""))


def parse_confirm(text: str) -> str | None:
    """Parses `CONFIRM <token>` (case-insensitive). Returns None for
    anything else, including a bare 'confirm' with no token."""
    m = _CONFIRM_RE.match(text or "")
    return m.group(1).lower() if m else None


class ActionGuard:
    """Holds at most a handful of pending proposals, keyed by a short
    random token. A proposal only executes via confirm() with the exact
    token; any other incoming message discards all pending proposals
    (see route_command in main.py) so a stale CONFIRM can't fire days
    later against a since-changed situation."""

    def __init__(self):
        self._pending: dict[str, dict] = {}
        self._lock = asyncio.Lock()

    def has_pending(self) -> bool:
        return bool(self._pending)

    async def propose(self, description: str, agent: str, executor, requested_by_text: str) -> str:
        async with self._lock:
            token = uuid.uuid4().hex[:6]
            self._pending[token] = {
                "description": description,
                "agent": agent,
                "executor": executor,
                "requested_by_text": requested_by_text,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        log.warning(f"[ActionGuard] Proposed destructive action ({agent}): {description}")
        return (
            f"⚠️ <b>Confirmation required</b>\n"
            f"This looks like a destructive action:\n<i>{description}</i>\n\n"
            f"Reply <code>CONFIRM {token}</code> to proceed, or send anything else to cancel."
        )

    async def confirm(self, token: str) -> str:
        async with self._lock:
            pending = self._pending.pop(token, None)
        if not pending:
            return "⚠️ No matching pending action to confirm (it may have expired or already been cancelled)."
        log.warning(f"[ActionGuard] Confirmed ({pending['agent']}): {pending['description']}")
        try:
            result = await pending["executor"]()
            return result if result else "✅ Confirmed and executed."
        except Exception as e:
            log.error(f"[ActionGuard] Confirmed action failed: {e}")
            return f"⚠️ Confirmed, but execution failed: {e}"

    async def discard_all_pending(self, reason: str = ""):
        async with self._lock:
            if self._pending:
                log.info(f"[ActionGuard] Discarding {len(self._pending)} pending proposal(s): {reason}")
            self._pending.clear()
