# ============================================================
# OUTCOME TRACKER — closes the loop on AKILI's own actions
#
# Every time an agent does something in the real world (posts to a
# platform, sends an auto-reply email), it calls log_action() and gets
# back a short action_id. Justin reports real-world results later with
# `outcome <action_id> key=value ...` (handled in main.py), which calls
# log_outcome(). pending_without_outcome() is what lets main.py nudge
# Justin about actions that never got a result logged — without it,
# this is a write-only log nobody reads.
# ============================================================

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiofiles

log = logging.getLogger("CORE.OutcomeTracker")

STORE_PATH = Path(os.environ.get("AKILI_MEMORY_PATH", "./akili-life")) / "logs" / "outcomes.json"


class OutcomeTracker:
    def __init__(self):
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._actions = self._load()

    def _load(self) -> dict:
        if STORE_PATH.exists():
            try:
                return json.loads(STORE_PATH.read_text())
            except Exception:
                log.exception("[OutcomeTracker] Failed to load store — starting fresh")
        return {}

    async def _save(self):
        """Writes to a temp file then atomically replaces the store, so a
        crash mid-write can't leave outcomes.json truncated/corrupt (which
        would otherwise silently discard every tracked action on next load)."""
        tmp_path = STORE_PATH.with_suffix(".json.tmp")
        async with aiofiles.open(tmp_path, "w") as f:
            await f.write(json.dumps(self._actions, indent=2))
        os.replace(tmp_path, STORE_PATH)

    async def log_action(self, agent: str, action_type: str, summary: str, metadata: dict | None = None) -> str:
        async with self._lock:
            action_id = uuid.uuid4().hex[:8]
            while action_id in self._actions:
                action_id = uuid.uuid4().hex[:8]
            self._actions[action_id] = {
                "id": action_id,
                "agent": agent,
                "type": action_type,
                "summary": summary,
                "metadata": metadata or {},
                "ts": datetime.now(timezone.utc).isoformat(),
                "outcome": None,
                "outcome_ts": None,
            }
            await self._save()
        log.info(f"[OutcomeTracker] logged action {action_id} ({agent}/{action_type})")
        return action_id

    async def log_outcome(self, action_id: str, metrics: dict) -> bool:
        async with self._lock:
            record = self._actions.get(action_id)
            if not record:
                return False
            record["outcome"] = metrics
            record["outcome_ts"] = datetime.now(timezone.utc).isoformat()
            await self._save()
        log.info(f"[OutcomeTracker] logged outcome for {action_id}: {metrics}")
        return True

    async def pending_without_outcome(self, agent: str, older_than_hours: int = 24) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
        async with self._lock:
            results = []
            for record in self._actions.values():
                if record["agent"] != agent or record["outcome"] is not None:
                    continue
                try:
                    ts = datetime.fromisoformat(record["ts"])
                except ValueError:
                    continue
                if ts <= cutoff:
                    results.append(record)
            return results


tracker = OutcomeTracker()
