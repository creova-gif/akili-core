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
            f"🐙 GITHUB STATUS — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Org: {GITHUB_ORG} | {len(ALL_REPOS)} repos monitored",
            f"Active (24h): {scan['active_repos']} repos",
            f"Open issues total: {scan['total_open_issues']}",
            "",
        ]

        if scan["alerts"]:
            lines.append("🚨 ALERTS:")
            lines.extend(scan["alerts"])
            lines.append("")

        lines.append("📊 REPO ACTIVITY:")
        for repo in scan["repos"]:
            if "error" in repo:
                lines.append(f"  ❌ {repo['name']}: {repo['error']}")
            else:
                commits = repo.get("recent_commits", 0)
                issues = repo.get("open_issues", 0)
                activity = "🟢" if commits > 0 else "⚪"
                lines.append(f"  {activity} {repo['name']} — {commits} commits/24h · {issues} issues")

        return "\n".join(lines)

    async def watch_repo(self, repo_name: str) -> str:
        """Deep dive on a single repo."""
        summary = await self.get_repo_summary(repo_name)
        commits = await self.get_recent_commits(repo_name, since_hours=72)
        issues = await self.get_open_issues(repo_name)

        lines = [
            f"🔍 {repo_name} — Deep Scan",
            f"Language: {summary.get('language', 'N/A')}",
            f"Open issues: {summary.get('open_issues', 0)}",
            f"Last updated: {summary.get('updated', 'N/A')[:10]}",
            "",
            f"Recent commits (72h): {len(commits)}",
        ]
        for c in commits[:3]:
            lines.append(f"  • [{c['sha']}] {c['message']}")

        if issues:
            lines.append(f"\nOpen issues ({len(issues)}):")
            for i in issues[:3]:
                lines.append(f"  #{i['number']}: {i['title']}")

        return "\n".join(lines)
