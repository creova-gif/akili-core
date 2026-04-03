# ============================================================
# MEMORY MANAGER — Akili's knowledge and logging system
# PARA structure: Projects, Areas, Resources, Archives
# ============================================================

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger("MEMORY")

AKILI_LIFE_ROOT = Path(os.environ.get("AKILI_MEMORY_PATH", "./akili-life"))


class MemoryManager:
    def __init__(self):
        self._ensure_structure()
        log.info(f"Memory initialized at {AKILI_LIFE_ROOT}")

    def _ensure_structure(self):
        """Create the full ~/akili-life/ PARA directory structure."""
        dirs = [
            # PARA top level
            "projects",
            "areas",
            "resources",
            "archives",
            # Daily logs
            "logs/daily",
            # Ventures
            "areas/justin-mafie",
            "areas/creova-solutions",
            "areas/creova-media",
            "areas/creova-music",
            "areas/sankofa-studio",
            # Markets
            "resources/markets/tanzania",
            "resources/markets/kenya",
            "resources/markets/canada",
            # Products (all 14 repos)
            "projects/gopay",
            "projects/kaya",
            "projects/mentalpath",
            "projects/wazawealth",
            "projects/kilimo-ai",
            "projects/grid-os",
            "projects/darsme",
            "projects/ai-health-support",
            "projects/budget-ease",
            "projects/health-fitness",
            "projects/recommended-peptides",
            "projects/seen",
            "projects/mskniagara",
            "projects/quickbook-sample",
            # Agent memory
            "resources/agents/shield",
            "resources/agents/pulse",
            "resources/agents/reach",
            "resources/agents/intel",
            "resources/agents/amplify",
        ]
        for d in dirs:
            (AKILI_LIFE_ROOT / d).mkdir(parents=True, exist_ok=True)

        # Create base entity files if missing
        self._init_entity("areas/justin-mafie", "Justin Mafie", "Founder, musician, CEO of CREOVA")
        self._init_entity("areas/creova-solutions", "CREOVA Solutions", "Emerging global tech company")
        self._init_entity("areas/creova-music", "CREOVA Music", "Music label distributed via DistroKid")
        self._init_entity("areas/sankofa-studio", "Sankofa Studio", "Music production studio")
        self._init_entity("projects/gopay", "GoPay Tanzania", "Fintech super app, Bank of Tanzania compliance")

    def _init_entity(self, rel_path: str, name: str, description: str):
        """Create summary.md and items.json for an entity if missing."""
        base = AKILI_LIFE_ROOT / rel_path
        summary = base / "summary.md"
        items = base / "items.json"
        if not summary.exists():
            summary.write_text(f"# {name}\n\n{description}\n\n## Notes\n\n## Status\nActive\n")
        if not items.exists():
            items.write_text(json.dumps([
                {"date": datetime.now().isoformat(), "fact": description, "source": "init"}
            ], indent=2))

    def daily_log(self, entry: str):
        """Write an entry to today's daily log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = AKILI_LIFE_ROOT / "logs" / "daily" / f"{today}.md"
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] {entry}")

    def get_yesterday_log(self) -> str:
        """Read yesterday's log for the morning brief."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        log_file = AKILI_LIFE_ROOT / "logs" / "daily" / f"{yesterday}.md"
        if log_file.exists():
            return log_file.read_text()
        return "No activity logged yesterday."

    def get_today_log(self) -> str:
        """Read today's log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = AKILI_LIFE_ROOT / "logs" / "daily" / f"{today}.md"
        if log_file.exists():
            return log_file.read_text()
        return "No activity logged yet today."

    def update_entity(self, entity_path: str, fact: str):
        """Add a new fact to an entity's items.json."""
        items_file = AKILI_LIFE_ROOT / entity_path / "items.json"
        if items_file.exists():
            items = json.loads(items_file.read_text())
        else:
            items = []
        items.append({
            "date": datetime.now().isoformat(),
            "fact": fact,
            "source": "akili-auto"
        })
        items_file.write_text(json.dumps(items, indent=2))

    def read_entity(self, entity_path: str) -> str:
        """Read an entity's summary."""
        summary_file = AKILI_LIFE_ROOT / entity_path / "summary.md"
        if summary_file.exists():
            return summary_file.read_text()
        return f"No entity found at {entity_path}"

    def save_agent_note(self, agent: str, note: str):
        """Save a note specific to an agent's memory."""
        agent_dir = AKILI_LIFE_ROOT / "resources" / "agents" / agent.lower()
        agent_dir.mkdir(parents=True, exist_ok=True)
        notes_file = agent_dir / "notes.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(notes_file, "a") as f:
            f.write(f"\n## {timestamp}\n{note}\n")
