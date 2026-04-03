# ============================================================
# GMAIL INTEGRATION — Akili REACH Agent
# Accounts: Justin Mafie personal Gmail + CREOVA business email
# ============================================================

import os
import logging
import base64
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config.accounts import EMAIL_ACCOUNTS

log = logging.getLogger("REACH.Gmail")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

SIGNATURES = {
    "personal": (
        "\n\n— Justin Mafie"
        "\nFounder | CREOVA"
        "\n🌍 creova.one | 📸 @jj_mafie | 🎵 @creativeinnovation__"
    ),
    "business": (
        "\n\nJustin Mafie"
        "\nFounder & CEO | CREOVA Solutions"
        "\n🌍 creova.one | 📸 @creovasolutions | 💼 linkedin.com/in/justin-mafie"
        "\n\n—"
        "\nCREOVA Solutions — Emerging global tech for Africa + Canada"
    ),
}

EMAIL_CLASSIFIERS = {
    "urgent":   ["investment", "investor", "vc", "funding", "legal", "partnership", "media", "interview", "urgent", "press"],
    "fan":      ["love your music", "biggest fan", "stream", "amazing artist", "huge fan", "obsessed"],
    "collab":   ["collaborate", "collab", "feature", "remix", "work together", "joint", "project together"],
    "press":    ["journalist", "article", "interview", "coverage", "feature story", "blog post", "podcast guest"],
    "business": ["services", "quote", "proposal", "branding", "agency", "hire", "contract", "retainer"],
    "client":   ["creova", "project update", "invoice", "deliverable", "timeline"],
}


class GmailClient:

    def __init__(self):
        self.services = {}
        self._init_all()

    def _init_service(self, account_key: str) -> bool:
        acc = EMAIL_ACCOUNTS.get(account_key)
        if not acc or not acc.get("address"):
            log.info(f"Gmail ({account_key}): not configured (add GMAIL_* secrets)")
            return False
        if not os.path.exists(acc["credentials_path"]):
            log.info(f"Gmail ({account_key}): credentials file not found at {acc['credentials_path']}")
            return False
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = None
            if os.path.exists(acc["token_path"]):
                creds = Credentials.from_authorized_user_file(acc["token_path"], SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    log.info(f"Gmail ({account_key}): needs browser auth — run: python integrations/gmail.py")
                    return False
                with open(acc["token_path"], "w") as f:
                    f.write(creds.to_json())

            self.services[account_key] = build("gmail", "v1", credentials=creds)
            log.info(f"Gmail ✅ {acc['label']} — {acc['address']}")
            return True

        except ImportError:
            log.warning("Google libraries not installed — run: pip install google-api-python-client google-auth-oauthlib")
            return False
        except Exception as e:
            log.error(f"Gmail init error ({account_key}): {e}")
            return False

    def _init_all(self):
        for key in EMAIL_ACCOUNTS:
            self._init_service(key)

    def _get_service(self, account_key: str):
        svc = self.services.get(account_key)
        if not svc:
            raise ValueError(f"Gmail not initialized for '{account_key}'. Add credentials and run auth.")
        return svc

    async def get_unread(self, account_key: str, max_results: int = 20) -> list:
        svc = self._get_service(account_key)
        try:
            result = svc.users().messages().list(
                userId="me", q="is:unread", maxResults=max_results
            ).execute()
            messages = result.get("messages", [])
            emails = []
            for msg in messages:
                detail = svc.users().messages().get(userId="me", id=msg["id"], format="full").execute()
                headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
                body = self._extract_body(detail["payload"])
                emails.append({
                    "id": msg["id"],
                    "account": account_key,
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": detail.get("snippet", ""),
                    "body": body[:600],
                })
            return emails
        except Exception as e:
            log.error(f"[Gmail] Get unread error ({account_key}): {e}")
            return []

    def _extract_body(self, payload: dict) -> str:
        if "body" in payload and payload["body"].get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        return ""

    async def send_email(
        self,
        account_key: str,
        to: str,
        subject: str,
        body: str,
        reply_to_id: Optional[str] = None,
    ) -> dict:
        svc = self._get_service(account_key)
        acc = EMAIL_ACCOUNTS[account_key]
        sig = SIGNATURES.get(account_key, "")
        try:
            msg = MIMEMultipart("alternative")
            msg["to"] = to
            msg["subject"] = subject
            msg["from"] = acc["address"]
            if reply_to_id:
                msg["In-Reply-To"] = reply_to_id
                msg["References"] = reply_to_id
            msg.attach(MIMEText(f"{body}{sig}", "plain"))
            encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            result = svc.users().messages().send(userId="me", body={"raw": encoded}).execute()
            log.info(f"[Gmail] ✅ Sent from {acc['label']} to {to}")
            return {"success": True, "message_id": result["id"], "from": acc["address"], "to": to}
        except Exception as e:
            log.error(f"[Gmail] Send error ({account_key}): {e}")
            return {"error": str(e)}

    def classify_email(self, email: dict) -> str:
        combined = f"{email.get('from','')} {email.get('subject','')} {email.get('body','')}".lower()
        for category, triggers in EMAIL_CLASSIFIERS.items():
            if any(t in combined for t in triggers):
                return category
        return "general"

    async def get_all_unread(self) -> dict:
        all_emails = {}
        for key in EMAIL_ACCOUNTS:
            if key in self.services:
                emails = await self.get_unread(key)
                all_emails[key] = emails
        return all_emails

    async def mark_read(self, account_key: str, message_id: str):
        svc = self._get_service(account_key)
        try:
            svc.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
        except Exception as e:
            log.error(f"[Gmail] Mark read error: {e}")

    def route_reply(self, email: dict) -> str:
        classification = self.classify_email(email)
        if classification in ["business", "client", "urgent", "press"]:
            return "business"
        return "personal"

    async def send_campaign(self, account_key: str, recipients: list, subject: str, body: str) -> list:
        results = []
        for recipient in recipients:
            r = await self.send_email(account_key, recipient, subject, body)
            results.append(r)
            await asyncio.sleep(2)
        log.info(f"[Gmail] Campaign sent: {len(results)} emails from {account_key}")
        return results

    async def format_status(self) -> str:
        lines = ["📧 GMAIL STATUS\n"]
        for key, acc in EMAIL_ACCOUNTS.items():
            if not acc.get("address"):
                lines.append(f"  ⚪ {acc['label']} — not configured (add GMAIL_*_ADDRESS secret)")
                continue
            if not os.path.exists(acc["credentials_path"]):
                lines.append(f"  ⚪ {acc['label']} — credentials file missing (upload to {acc['credentials_path']})")
                continue
            connected = key in self.services and self.services[key] is not None
            icon = "✅" if connected else "❌"
            lines.append(f"  {icon} {acc['label']} — {acc['address']}")
        return "\n".join(lines)


# ── First-time auth helper ────────────────────────────────────
def run_first_auth(account_key: str = "personal"):
    """Run this once in the Replit Shell to authorize Gmail access."""
    acc = EMAIL_ACCOUNTS.get(account_key)
    if not acc:
        print(f"Unknown account: {account_key}")
        return
    if not os.path.exists(acc["credentials_path"]):
        print(f"Credentials file not found: {acc['credentials_path']}")
        print("Download it from Google Cloud Console and upload to Replit.")
        return
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(acc["credentials_path"], SCOPES)
        creds = flow.run_local_server(port=0)
        with open(acc["token_path"], "w") as f:
            f.write(creds.to_json())
        print(f"✅ Gmail authorized for {acc['label']} — token saved to {acc['token_path']}")
    except Exception as e:
        print(f"Auth error: {e}")


if __name__ == "__main__":
    import sys
    key = sys.argv[1] if len(sys.argv) > 1 else "personal"
    run_first_auth(key)
