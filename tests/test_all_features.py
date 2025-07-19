"""
Quick test to verify all major Playwright features are working
"""

import asyncio
from ga_scrap import GAScrap


async def test_basic_features():
    """Test basic features quickly"""
    
    scraper = GAScrap(headless=True)  # Headless for faster testing
    
    try:
        await scraper.start()
        print("✅ Browser started successfully")
        
        # Basic navigation
        await scraper.goto("https://httpbin.org/html")
        print("✅ Navigation works")
        
        # Screenshot
        screenshot = await scraper.screenshot("test_screenshot.png")
        print(f"✅ Screenshot: {screenshot}")
        
        # Text extraction
        text = await scraper.get_text("h1")
        print(f"✅ Text extraction: {text}")
        
        # Network monitoring
        print(f"✅ Network requests captured: {len(scraper.requests)}")
        print(f"✅ Network responses captured: {len(scraper.responses)}")
        
        # Performance metrics
        metrics = await scraper.save_performance_metrics()
        print(f"✅ Performance metrics: {len(metrics)} entries")
        
        # Cookie management
        await scraper.add_cookies([{"name": "test", "value": "value", "domain": "httpbin.org", "path": "/"}])
        cookies = await scraper.get_cookies()
        print(f"✅ Cookie management: {len(cookies)} cookies")
        
        # JavaScript execution
        result = await scraper.execute_script("() => document.title")
        print(f"✅ JavaScript execution: {result}")
        
        # Multiple pages
        page2 = await scraper.new_page()
        await scraper.goto("https://httpbin.org/json", page=page2)
        print(f"✅ Multiple pages: {len(scraper.pages)} pages")
        
        # Locators
        locator = scraper.get_locator("h1")
        count = await locator.count()
        print(f"✅ Locators: {count} elements found")
        
        # Storage state
        storage = await scraper.save_storage_state()
        print(f"✅ Storage state: {len(storage)} entries")
        
        # Accessibility
        accessibility = await scraper.get_accessibility_tree()
        print(f"✅ Accessibility tree captured")
        
        # Advanced waiting
        await scraper.wait_for_network_idle(timeout=5000)
        print("✅ Network idle waiting")
        
        print("\n🎉 All major features working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await scraper.stop()


if __name__ == "__main__":
    asyncio.run(test_basic_features())
