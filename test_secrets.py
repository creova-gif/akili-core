"""Env-var checks for secrets that must not live in the repo.

Run: python test_secrets.py
"""
import asyncio
import os

from aiohttp import web

from api.handlers import handle_api_command
from integrations.linkedin import linkedin_setup_error
from main import missing_required_secrets


def test_missing_required_names():
    missing = missing_required_secrets({})
    assert missing == ["TELEGRAM_TOKEN", "ANTHROPIC_API_KEY", "JUSTIN_CHAT_ID"], missing


def test_present_required_names():
    env = {
        "TELEGRAM_TOKEN": "present",
        "ANTHROPIC_API_KEY": "present",
        "JUSTIN_CHAT_ID": "present",
    }
    assert missing_required_secrets(env) == []


def test_blank_values_are_missing():
    env = {
        "TELEGRAM_TOKEN": "   ",
        "ANTHROPIC_API_KEY": "",
        "JUSTIN_CHAT_ID": "1",
    }
    assert missing_required_secrets(env) == ["TELEGRAM_TOKEN", "ANTHROPIC_API_KEY"]


def test_linkedin_error_names_exact_variables():
    err = linkedin_setup_error("", "")
    assert err is not None
    assert "LINKEDIN_ACCESS_TOKEN" in err
    assert "LINKEDIN_CLIENT_SECRET" in err

    # An access token is enough for existing Bearer API calls.
    assert linkedin_setup_error("token", "") is None
    assert linkedin_setup_error("token", "secret") is None

    token_only = linkedin_setup_error("", "secret")
    assert token_only is not None
    assert "LINKEDIN_ACCESS_TOKEN" in token_only
    assert "LINKEDIN_CLIENT_SECRET" not in token_only


async def test_command_api_rejects_missing_secret():
    saved = os.environ.pop("AKILI_API_SECRET", None)

    class _Request:
        async def json(self):
            return {"secret": "not-the-env-value", "command": "ping"}

    try:
        response = await handle_api_command(_Request())
    finally:
        if saved is not None:
            os.environ["AKILI_API_SECRET"] = saved

    assert isinstance(response, web.Response)
    assert response.status == 500
    body = response.body.decode() if isinstance(response.body, (bytes, bytearray)) else str(response.body)
    assert "AKILI_API_SECRET" in body
    assert "not-the-env-value" not in body


def main():
    test_missing_required_names()
    test_present_required_names()
    test_blank_values_are_missing()
    test_linkedin_error_names_exact_variables()
    asyncio.run(test_command_api_rejects_missing_secret())
    print("test_secrets: ok")


if __name__ == "__main__":
    main()
