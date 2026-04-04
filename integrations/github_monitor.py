# ============================================================
# GITHUB MONITOR — Akili SHIELD Agent
# Monitors all 14 repos in creova-gif organization
# ============================================================

import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from config.accounts import GITHUB_CONFIG

log = logging.getLogger("SHIELD.GitHub")

BASE_URL = "https://api.github.com"
GITHUB_ORG = GITHUB_CONFIG["org"]
ALL_REPOS  = GITHUB_CONFIG["repos"]


class GitHubMonitor:

    def __init__(self):
        self.token = GITHUB_CONFIG["token"]
        log.info(f"GitHub monitor — {len(ALL_REPOS)} repos tracked in {GITHUB_ORG}")

    def _is_configured(self) -> bool:
        return bool(self.token)

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_repo_summary(self, repo_name: str) -> dict:
        if not self._is_configured():
            return {"name": repo_name, "error": "Not configured (add GITHUB_TOKEN)"}
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/repos/{GITHUB_ORG}/{repo_name}"
            async with session.get(url, headers=self._headers) as r:
                if r.status == 200:
                    data = await r.json()
                    return {
                        "name": repo_name,
                        "stars": data.get("stargazers_count", 0),
                        "open_issues": data.get("open_issues_count", 0),
                        "language": data.get("language", "Unknown"),
                        "updated": data.get("updated_at", ""),
                        "default_branch": data.get("default_branch", "main"),
                        "private": data.get("private", False),
                        "description": data.get("description", ""),
                    }
                elif r.status == 404:
                    return {"name": repo_name, "error": "Not found — may be private or different name"}
                else:
                    return {"name": repo_name, "error": f"HTTP {r.status}"}

    async def get_recent_commits(self, repo_name: str, since_hours: int = 24) -> list:
        if not self._is_configured():
            return []
        since = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat() + "Z"
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/repos/{GITHUB_ORG}/{repo_name}/commits"
            params = {"since": since, "per_page": 10}
            async with session.get(url, headers=self._headers, params=params) as r:
                if r.status == 200:
                    commits = await r.json()
                    return [
                        {
                            "sha": c["sha"][:7],
                            "message": c["commit"]["message"][:80],
                            "author": c["commit"]["author"]["name"],
                            "date": c["commit"]["author"]["date"],
                        }
                        for c in commits
                    ]
                return []

    async def get_open_issues(self, repo_name: str) -> list:
        if not self._is_configured():
            return []
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/repos/{GITHUB_ORG}/{repo_name}/issues"
            params = {"state": "open", "per_page": 5}
            async with session.get(url, headers=self._headers, params=params) as r:
                if r.status == 200:
                    issues = await r.json()
                    return [
                        {
                            "number": i["number"],
                            "title": i["title"],
                            "created": i["created_at"],
                            "labels": [lb["name"] for lb in i.get("labels", [])],
                        }
                        for i in issues if "pull_request" not in i
                    ]
                return []

    async def full_org_scan(self) -> dict:
        """Complete scan of all 14 repos — used by SHIELD heartbeat."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "repos": [],
            "alerts": [],
            "active_repos": 0,
            "total_open_issues": 0,
        }

        if not self._is_configured():
            results["alerts"].append("⚠️ GITHUB_TOKEN not set — monitoring disabled")
            return results

        for repo in ALL_REPOS:
            summary = await self.get_repo_summary(repo)
            if "error" not in summary:
                commits = await self.get_recent_commits(repo, since_hours=24)
                summary["recent_commits"] = len(commits)
                summary["latest_commit"] = commits[0]["message"] if commits else "No recent commits"

                if summary.get("open_issues", 0) > 5:
                    results["alerts"].append(f"⚠️ {repo}: {summary['open_issues']} open issues need attention")

                if commits:
                    results["active_repos"] += 1

                results["total_open_issues"] += summary.get("open_issues", 0)
            results["repos"].append(summary)
            await asyncio.sleep(0.3)

        log.info(f"[GitHub] Scan complete — {results['active_repos']} active, {results['total_open_issues']} open issues")
        return results

    async def format_status_report(self) -> str:
        if not self._is_configured():
            return (
                f"🐙 GITHUB STATUS\n"
                f"  ⚪ Not configured (add GITHUB_TOKEN secret)\n"
                f"  Repos to monitor: {len(ALL_REPOS)}"
            )
        scan = await self.full_org_scan()
        lines = [
            f"🐙 <b>GITHUB — creova-gif</b>",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"<b>{len(ALL_REPOS)} repos</b> · {scan['active_repos']} active (24h) · {scan['total_open_issues']} open issues",
            "",
        ]

        if scan["alerts"]:
            lines.append("🚨 <b>ALERTS:</b>")
            lines.extend(scan["alerts"])
            lines.append("")

        lines.append("📊 <b>REPOS:</b>")
        for repo in scan["repos"]:
            if "error" in repo:
                lines.append(f"  ❌ <b>{repo['name']}</b>: {repo['error']}")
            else:
                commits  = repo.get("recent_commits", 0)
                issues   = repo.get("open_issues", 0)
                lang     = repo.get("language") or "—"
                desc     = repo.get("description") or ""
                updated  = repo.get("updated", "")
                # Format last-updated date (YYYY-MM-DDTHH:MM:SSZ → MM-DD)
                try:
                    d = datetime.strptime(updated[:10], "%Y-%m-%d")
                    last = d.strftime("%b %d")
                except Exception:
                    last = "—"
                activity = "🟢" if commits > 0 else "⚪"
                detail   = f"{lang} · last push {last}"
                if desc:
                    detail += f" · {desc[:40]}"
                commit_txt = f"{commits} commit{'s' if commits != 1 else ''}/24h" if commits else "no recent commits"
                issue_txt  = f"{issues} issue{'s' if issues != 1 else ''}" if issues else "no issues"
                lines.append(f"  {activity} <b>{repo['name']}</b> — {commit_txt} · {issue_txt}")
                lines.append(f"       <i>{detail}</i>")

        lines.append("")
        lines.append("⚡ Say <code>kaya repo</code> / <code>gridos repo</code> etc. for a deep dive on any one.")
        return "\n".join(lines)

    async def watch_repo(self, repo_name: str) -> str:
        """Deep dive on a single repo — rich formatted Telegram output."""
        summary = await self.get_repo_summary(repo_name)
        if "error" in summary:
            return f"🐙 <b>{repo_name}</b>\n❌ {summary['error']}"

        commits = await self.get_recent_commits(repo_name, since_hours=72)
        issues  = await self.get_open_issues(repo_name)

        lang    = summary.get("language") or "—"
        desc    = summary.get("description") or "No description"
        stars   = summary.get("stars", 0)
        n_iss   = summary.get("open_issues", 0)
        updated = summary.get("updated", "")
        branch  = summary.get("default_branch", "main")
        private = "🔒 Private" if summary.get("private") else "🌐 Public"

        try:
            d    = datetime.strptime(updated[:10], "%Y-%m-%d")
            last = d.strftime("%B %d, %Y")
        except Exception:
            last = updated[:10] if updated else "—"

        lines = [
            f"🔍 <b>{repo_name}</b> — Deep Scan",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"▸ <i>{desc}</i>",
            f"▸ Language: <b>{lang}</b> · {private}",
            f"▸ Branch: <code>{branch}</code> · ⭐ {stars} · 🐛 {n_iss} open issues",
            f"▸ Last push: {last}",
            f"▸ GitHub: <code>github.com/{GITHUB_ORG}/{repo_name}</code>",
            "",
        ]

        lines.append(f"📝 <b>Recent commits (72h): {len(commits)}</b>")
        if commits:
            for c in commits[:5]:
                msg = c["message"].split("\n")[0][:70]
                lines.append(f"  ▸ <code>[{c['sha']}]</code> {msg}")
        else:
            lines.append("  ⚪ No commits in the last 72 hours")

        if issues:
            lines.append(f"\n🐛 <b>Open issues ({len(issues)}):</b>")
            for i in issues[:5]:
                labels = f" [{', '.join(i['labels'])}]" if i["labels"] else ""
                lines.append(f"  ▸ #{i['number']}: {i['title']}{labels}")

        lines.append(f"\n⚡ <code>github scan</code> to see all 8 repos at once.")
        return "\n".join(lines)
