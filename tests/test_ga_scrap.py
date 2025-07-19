"""
Test script for GA-Scrap
Quick test to verify installation and basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ga_scrap import GAScrap

async def test_basic_functionality():
    """Test basic GA-Scrap functionality"""
    
    print("🧪 Testing GA-Scrap basic functionality...")
    
    # Test 1: Initialize GA-Scrap
    print("1. Initializing GA-Scrap...")
    scraper = GAScrap(
        headless=True,  # Use headless for testing
        browser_type="chromium",
        debug=True
    )
    
    try:
        # Test 2: Start browser
        print("2. Starting browser...")
        await scraper.start()
        print("   ✅ Browser started successfully")
        
        # Test 3: Navigate to a page
        print("3. Navigating to test page...")
        await scraper.goto("https://httpbin.org/html")
        print("   ✅ Navigation successful")
        
        # Test 4: Extract page title
        print("4. Extracting page title...")
        title = await scraper.page.title()
        print(f"   ✅ Page title: {title}")
        
        # Test 5: Extract content
        print("5. Extracting content...")
        h1_element = await scraper.page.query_selector("h1")
        if h1_element:
            h1_text = await h1_element.inner_text()
            print(f"   ✅ H1 text: {h1_text}")
        else:
            print("   ⚠️  No H1 element found")
        
        # Test 6: Create new page
        print("6. Testing multiple pages...")
        page2 = await scraper.new_page()
        await page2.goto("https://httpbin.org/json")
        print(f"   ✅ Created new page, total pages: {len(scraper.pages)}")
        
        print("\n🎉 All tests passed! GA-Scrap is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Test 7: Cleanup
        print("7. Cleaning up...")
        await scraper.stop()
        print("   ✅ Cleanup successful")
    
    return True

async def test_context_manager():
    """Test context manager functionality"""
    
    print("\n🧪 Testing context manager...")
    
    try:
        async with GAScrap(headless=True, debug=True) as scraper:
            await scraper.goto("https://httpbin.org/user-agent")
            title = await scraper.page.title()
            print(f"   ✅ Context manager test passed: {title}")
        
        print("   ✅ Context manager cleanup successful")
        return True
        
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported"""
    
    print("🧪 Testing imports...")
    
    try:
        from ga_scrap import GAScrap
        print("   ✅ GAScrap imported")
        
        from ga_scrap import AppManager
        print("   ✅ AppManager imported")
        
        from ga_scrap import HotReloader
        print("   ✅ HotReloader imported")
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("🚀 GA-Scrap Test Suite")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed. Check your installation.")
        return
    
    # Test basic functionality
    if not await test_basic_functionality():
        print("\n❌ Basic functionality tests failed.")
        return
    
    # Test context manager
    if not await test_context_manager():
        print("\n❌ Context manager tests failed.")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! GA-Scrap is ready to use.")
    print("\n💡 Next steps:")
    print("   1. Try: ga-scrap create my-first-scraper")
    print("   2. Or run: python examples/basic_example.py")
    print("   3. Check out: ga-scrap examples")

if __name__ == "__main__":
    asyncio.run(main())
