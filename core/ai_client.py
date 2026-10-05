# ============================================================
# AI CLIENT — thin metering wrapper around AsyncAnthropic
#
# Every agent used to do `AsyncAnthropic(api_key=...)` directly, which
# meant token spend was invisible until the Anthropic console. get_client()
# returns a client that behaves identically for callers (same
# `.messages.create(...)` surface) but records input/output tokens and an
# estimated cost against the calling agent on every call — success or
# failure — into the shared `usage_log`. main.py's /costs command and the
# daily brief read `usage_log.today_summary()` to surface it.
# ============================================================

import json
import logging
import os
from collections import defaultdict
from datetime import date, datetime, timezone

import aiofiles
from anthropic import AsyncAnthropic

log = logging.getLogger("CORE.AIClient")

USAGE_LOG_DIR = os.environ.get("AKILI_MEMORY_PATH", "./akili-life") + "/logs/usage"

# Published Anthropic per-million-token pricing (USD), matched by model
# family substring. Used only to give Justin a spend estimate — not a
# billing source of truth (actual invoices come from the Anthropic console).
_PRICING_PER_MTOK = {
    "opus":   {"input": 15.00, "output": 75.00},
    "sonnet": {"input": 3.00,  "output": 15.00},
    "haiku":  {"input": 0.80,  "output": 4.00},
}
_DEFAULT_PRICING = _PRICING_PER_MTOK["sonnet"]


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    model_l = (model or "").lower()
    pricing = next((p for key, p in _PRICING_PER_MTOK.items() if key in model_l), _DEFAULT_PRICING)
    return (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]


class UsageLog:
    """In-memory per-agent daily aggregation, with best-effort JSONL
    persistence so a restart doesn't lose the day's numbers if the process
    reloads today's file (kept simple — not read back on init since the
    in-memory state only needs to survive one process lifetime)."""

    def __init__(self):
        self._today = date.today()
        self._by_agent = defaultdict(lambda: {
            "calls": 0, "errors": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
        })
        os.makedirs(USAGE_LOG_DIR, exist_ok=True)

    def _roll_if_new_day(self):
        today = date.today()
        if today != self._today:
            self._today = today
            self._by_agent = defaultdict(lambda: {
                "calls": 0, "errors": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
            })

    async def record(self, agent: str, model: str, input_tokens: int, output_tokens: int, error: bool = False):
        self._roll_if_new_day()
        cost = _estimate_cost(model, input_tokens, output_tokens)
        a = self._by_agent[agent]
        a["calls"] += 1
        a["input_tokens"] += input_tokens
        a["output_tokens"] += output_tokens
        a["cost_usd"] += cost
        if error:
            a["errors"] += 1
        try:
            record = {
                "ts": datetime.now(timezone.utc).isoformat(), "agent": agent, "model": model,
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "cost_usd": round(cost, 6), "error": error,
            }
            async with aiofiles.open(f"{USAGE_LOG_DIR}/{self._today.isoformat()}.jsonl", "a") as f:
                await f.write(json.dumps(record) + "\n")
        except Exception:
            log.exception("[UsageLog] Failed to persist usage record (in-memory total still accurate)")

    def today_summary(self) -> dict:
        self._roll_if_new_day()
        total_cost  = sum(a["cost_usd"] for a in self._by_agent.values())
        total_calls = sum(a["calls"] for a in self._by_agent.values())
        errors      = sum(a["errors"] for a in self._by_agent.values())
        return {
            "date": self._today.isoformat(),
            "total_cost_usd": total_cost,
            "total_calls": total_calls,
            "errors": errors,
            "by_agent": {k: dict(v) for k, v in self._by_agent.items()},
        }


usage_log = UsageLog()


class _TrackedMessages:
    def __init__(self, messages, agent: str):
        self._messages = messages
        self._agent    = agent

    async def create(self, *, model: str, **kwargs):
        try:
            response = await self._messages.create(model=model, **kwargs)
        except Exception:
            await usage_log.record(self._agent, model, 0, 0, error=True)
            raise
        usage = getattr(response, "usage", None)
        input_tokens  = getattr(usage, "input_tokens", 0) or 0
        output_tokens = getattr(usage, "output_tokens", 0) or 0
        await usage_log.record(self._agent, model, input_tokens, output_tokens)
        return response


class _TrackedClient:
    """Proxies everything to the real AsyncAnthropic client except
    `.messages`, which is wrapped for metering. Attribute access falls
    through so this is a drop-in replacement wherever `self.client` was
    an AsyncAnthropic instance."""

    def __init__(self, client: AsyncAnthropic, agent: str):
        self._client = client
        self.messages = _TrackedMessages(client.messages, agent)

    def __getattr__(self, name):
        return getattr(self._client, name)


def get_client(api_key: str, agent: str) -> _TrackedClient:
    """Returns an AsyncAnthropic-compatible client scoped to `agent` for
    usage tracking. Replaces `AsyncAnthropic(api_key=...)` at every call site."""
    return _TrackedClient(AsyncAnthropic(api_key=api_key), agent)
