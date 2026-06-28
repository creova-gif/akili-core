import asyncio
import logging
import os
import json

# Setup basic logging
logging.basicConfig(level=logging.INFO)

async def test_shield_secret_scan():
    print("--- Testing Shield Secret Scan ---")
    from agents.shield import ShieldAgent
    class MockMemory:
        async def daily_log(self, msg): pass
    agent = ShieldAgent(api_key="dummy", memory=MockMemory())
    result = await agent._quick_secret_scan()
    print("Result:")
    print(result)
    print("----------------------------------\n")

async def test_intel_scraper():
    print("--- Testing Intel Scraper ---")
    from agents.intel import IntelAgent
    class MockMemory:
        async def daily_log(self, msg): pass
        def get_yesterday_log(self): return ""
    agent = IntelAgent(api_key="dummy", memory=MockMemory())
    # Scrape a simple reliable site
    result = await agent.scrape_webpage("https://example.com")
    print("Scrape snippet (first 200 chars):")
    print(result[:200])
    print("-----------------------------\n")

async def test_dashboard_async():
    print("--- Testing Dashboard Async I/O ---")
    from dashboard import _streak_data, _recent_activity
    # Make dummy logs
    os.makedirs("akili-life/logs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    with open("akili-life/logs/snapchat_streak.json", "w") as f:
        json.dump({"streak": 5, "last_posted": "2026-06-02", "total_days": 10}, f)
    with open("logs/akili.log", "w") as f:
        f.write("test log 1\ntest log 2\n")
        
    streak = await _streak_data()
    print(f"Streak Data: {streak}")
    activity = await _recent_activity()
    print(f"Recent Activity: {activity}")
    print("-----------------------------------\n")
    
async def test_main_import():
    print("--- Testing main.py syntax ---")
    try:
        import main
        print("main.py imported successfully! No syntax errors.")
    except Exception as e:
        print(f"Failed to import main.py: {e}")
    print("------------------------------\n")

async def main():
    await test_main_import()
    await test_shield_secret_scan()
    await test_intel_scraper()
    await test_dashboard_async()
    
if __name__ == "__main__":
    asyncio.run(main())
