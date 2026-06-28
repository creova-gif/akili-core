import os
import sys
import asyncio
import httpx
from anthropic import AsyncAnthropic

async def test_telegram_api(token):
    if not token:
        print("❌ Telegram: TELEGRAM_TOKEN not found in environment.")
        return False

    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_name = data['result']['username']
                    print(f"✅ Telegram: Connection successful. Authenticated as @{bot_name}")
                    return True
                else:
                    print(f"❌ Telegram: API returned error: {data.get('description')}")
            else:
                print(f"❌ Telegram: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Telegram: Connection failed - {e}")
    return False

async def test_anthropic_api(api_key):
    if not api_key:
        print("❌ Anthropic: ANTHROPIC_API_KEY not found in environment.")
        return False
        
    try:
        client = AsyncAnthropic(api_key=api_key)
        # Using a very basic and cheap prompt to test authentication
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'hello'"}]
        )
        if response.content:
            print(f"✅ Anthropic: Connection successful. Response: {response.content[0].text}")
            return True
        else:
            print("❌ Anthropic: Connection successful, but got empty response.")
    except Exception as e:
        print(f"❌ Anthropic: Connection failed - {e}")
    return False

async def test_github_api():
    # We can check if github client in integration hub is working
    try:
        from integrations.github_client import GitHubClient
        gh = GitHubClient()
        # Ping the org repos
        status = await gh.full_org_scan()
        repos = status.get('repos', [])
        print(f"✅ GitHub: Connection successful. Found {len(repos)} repos in creova-gif org.")
        return True
    except Exception as e:
        print(f"❌ GitHub: Connection failed or GitHub integration not setup - {e}")
    return False

async def main():
    print("====================================")
    print("AKILI CORE — API Connection Test")
    print("====================================\n")
    
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    chat_id = os.environ.get("JUSTIN_CHAT_ID")
    
    if chat_id:
        print(f"✅ Configuration: JUSTIN_CHAT_ID is set ({chat_id[:4]}...)")
    else:
        print("⚠️ Configuration: JUSTIN_CHAT_ID is missing.")

    print("\nTesting Telegram API...")
    await test_telegram_api(telegram_token)

    print("\nTesting Anthropic API...")
    await test_anthropic_api(anthropic_key)

    print("\nTesting GitHub API (Integration Hub)...")
    await test_github_api()
    
    print("\n====================================")
    print("API Connection Test Complete")
    print("====================================")

if __name__ == "__main__":
    # Ensure event loop policy for MacOS if needed
    if sys.platform == 'darwin':
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    asyncio.run(main())
