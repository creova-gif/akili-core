# ============================================================
# GITHUB MONITOR — Akili SHIELD Agent
# Monitors all 14 repos in creova-gif organization
# Uses: GitHub REST API v3 (free, no limits for reads)
# ============================================================

import os
import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Optional

log = logging.getLogger("SHIELD.GitHub")

# ── Credentials — add to Replit Secrets ──────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_ORG   = "creova-gif"

BASE_URL = "https://api.github.com"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# All 14 CREOVA repos to monitor
ALL_REPOS = [
    "GoPay",
    "KayaYourPropertyAI",
    "Darsme",
    "MentalPath",
    "QuickBookSample",
    "AIHealthSupport",
    "GridOS",
    "KilimoAI",
    "BudgetEaseApp",
    "HealthFitness",
    "RecommendedPeptides",
    "SEEN",
    "WazaWealth",
    "Mskniagara",
]


class GitHubMonitor:
    """
    Monitors all 14 creova-gif repos for:
    - New commits (progress)
    - Open issues (bugs/blockers)
    - Pull requests (code changes)
    - Deployment status
    - Repo health
    Sends alerts to SHIELD → Telegram when action needed.
    """

    def __init__(self):
        self.token = GITHUB_TOKEN
        self.headers = HEADERS
        log.info(f"GitHub monitor initialized — {len(ALL_REPOS)} repos tracked")

    async def get_repo_summary(self, repo_name: str) -> dict:
        """Get complete summary for one repo."""
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/repos/{GITHUB_ORG}/{repo_name}"
            async with session.get(url, headers=self.headers) as r:
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
        """Get commits in the last N hours."""
        since = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat() + "Z"
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/repos/{GITHUB_ORG}/{repo_name}/commits"
            params = {"since": since, "per_page": 10}
            async with session.get(url, headers=self.headers, params=params) as r:
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
        """Get open issues — identifies blockers."""
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/repos/{GITHUB_ORG}/{repo_name}/issues"
            params = {"state": "open", "per_page": 5}
            async with session.get(url, headers=self.headers, params=params) as r:
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
        """
        Complete scan of all 14 repos.
        Called by SHIELD heartbeat every 30 min.
        Returns summary + any alerts.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "repos": [],
            "alerts": [],
            "active_repos": 0,
            "total_open_issues": 0,
        }

        for repo in ALL_REPOS:
            summary = await self.get_repo_summary(repo)
            if "error" not in summary:
                # Check for recent activity (last 24h)
                commits = await self.get_recent_commits(repo, since_hours=24)
                summary["recent_commits"] = len(commits)
                summary["latest_commit"] = commits[0]["message"] if commits else "No recent commits"

                # Count open issues
                if summary.get("open_issues", 0) > 5:
                    results["alerts"].append(f"⚠️ {repo}: {summary['open_issues']} open issues need attention")

                if commits:
                    results["active_repos"] += 1

                results["total_open_issues"] += summary.get("open_issues", 0)
            results["repos"].append(summary)
            await asyncio.sleep(0.5)  # Rate limit courtesy

        log.info(f"[GitHub] Org scan complete — {results['active_repos']} active repos, {results['total_open_issues']} open issues")
        return results

    async def format_status_report(self) -> str:
        """Format a human-readable status report for Telegram."""
        scan = await self.full_org_scan()
        lines = [
            f"🐙 GITHUB STATUS — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Org: creova-gif | {len(ALL_REPOS)} repos monitored",
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
        """Deep dive on a single repo — called by Justin's command."""
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


# ── Standalone test ───────────────────────────────────────────
async def test_github():
    monitor = GitHubMonitor()
    report = await monitor.format_status_report()
    print(report)


if __name__ == "__main__":
    asyncio.run(test_github())
