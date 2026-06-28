# ============================================================
# MEMORY MANAGER — Akili's knowledge and logging system
# PARA structure: Projects, Areas, Resources, Archives
# ============================================================

import os
import json
import logging
import aiofiles
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
            "projects",
            "areas",
            "resources",
            "archives",
            "logs/daily",
            "resources/content_reservoir",
            "areas/justin-mafie",
            "areas/creova-solutions",
            "areas/creova-media",
            "areas/creova-music",
            "areas/sankofa-studio",
            "resources/markets/tanzania",
            "resources/markets/kenya",
            "resources/markets/canada",
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
            "resources/agents/shield",
            "resources/agents/pulse",
            "resources/agents/reach",
            "resources/agents/intel",
            "resources/agents/amplify",
        ]
        for d in dirs:
            (AKILI_LIFE_ROOT / d).mkdir(parents=True, exist_ok=True)

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

    async def daily_log(self, entry: str):
        """Write an entry to today's daily log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = AKILI_LIFE_ROOT / "logs" / "daily" / f"{today}.md"
        timestamp = datetime.now().strftime("%H:%M:%S")
        async with aiofiles.open(log_file, "a") as f:
            await f.write(f"\n[{timestamp}] {entry}")

    async def get_yesterday_log(self) -> str:
        """Read yesterday's log for the morning brief."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        log_file = AKILI_LIFE_ROOT / "logs" / "daily" / f"{yesterday}.md"
        if log_file.exists():
            async with aiofiles.open(log_file, "r") as f:
                return await f.read()
        return "No activity logged yesterday."

    async def get_today_log(self) -> str:
        """Read today's log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = AKILI_LIFE_ROOT / "logs" / "daily" / f"{today}.md"
        if log_file.exists():
            async with aiofiles.open(log_file, "r") as f:
                return await f.read()
        return "No activity logged yet today."

    async def update_entity(self, entity_path: str, fact: str):
        """Add a new fact to an entity's items.json."""
        items_file = AKILI_LIFE_ROOT / entity_path / "items.json"
        if items_file.exists():
            async with aiofiles.open(items_file, "r") as f:
                content = await f.read()
                items = json.loads(content)
        else:
            items = []
        items.append({
            "date": datetime.now().isoformat(),
            "fact": fact,
            "source": "akili-auto"
        })
        async with aiofiles.open(items_file, "w") as f:
            await f.write(json.dumps(items, indent=2))

    async def read_entity(self, entity_path: str) -> str:
        """Read an entity's summary."""
        summary_file = AKILI_LIFE_ROOT / entity_path / "summary.md"
        if summary_file.exists():
            async with aiofiles.open(summary_file, "r") as f:
                return await f.read()
        return f"No entity found at {entity_path}"

    async def save_agent_note(self, agent: str, note: str):
        """Save a note specific to an agent's memory."""
        agent_dir = AKILI_LIFE_ROOT / "resources" / "agents" / agent.lower()
        agent_dir.mkdir(parents=True, exist_ok=True)
        notes_file = agent_dir / "notes.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        async with aiofiles.open(notes_file, "a") as f:
            await f.write(f"\n## {timestamp}\n{note}\n")

    async def save_content_draft(self, platform: str, title: str, content: str):
        """Save a generated script/draft to the content reservoir."""
        reservoir = AKILI_LIFE_ROOT / "resources" / "content_reservoir"
        reservoir.mkdir(parents=True, exist_ok=True)
        safe_title = "".join([c if c.isalnum() else "_" for c in title]).lower()
        filename = f"{datetime.now().strftime('%Y%m%d')}_{platform}_{safe_title}.md"
        draft_file = reservoir / filename
        async with aiofiles.open(draft_file, "w") as f:
            await f.write(f"# {title}\nPlatform: {platform}\nDate: {datetime.now().isoformat()}\n\n{content}")
        return str(draft_file)

    async def get_content_board(self) -> str:
        """Parse the content reservoir and return a Kanban-style summary."""
        reservoir = AKILI_LIFE_ROOT / "resources" / "content_reservoir"
        if not reservoir.exists():
            return "Content Reservoir is empty."
            
        import glob
        files = glob.glob(str(reservoir / "*.md"))
        if not files:
            return "No drafts in Content Reservoir."
            
        board = []
        for file in sorted(files, reverse=True)[:10]:
            name = os.path.basename(file)
            parts = name.replace(".md", "").split("_", 2)
            if len(parts) == 3:
                date, platform, title = parts
                board.append(f"• [{platform.upper()}] {title.replace('_', ' ').title()} ({date})")
            else:
                board.append(f"• {name}")
                
        return "📝 CONTENT BOARD (Recent Drafts):\n" + "\n".join(board)
