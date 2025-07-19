"""
Test the synchronous GA-Scrap interface
"""

from ga_scrap import SyncGAScrap, create_scraper


def test_basic_sync():
    """Test basic synchronous operations"""
    print("🧪 Testing basic synchronous interface...")
    
    # Test basic usage
    scraper = SyncGAScrap(headless=True)
    scraper.start()
    
    # Basic operations
    scraper.goto("https://httpbin.org/html")
    title = scraper.get_text("h1")
    scraper.screenshot("sync_test.png")
    
    print(f"✅ Title extracted: {title}")
    print(f"✅ Screenshot taken")
    print(f"✅ Requests captured: {len(scraper.requests)}")
    
    scraper.stop()
    print("✅ Basic sync test completed!")


def test_context_manager():
    """Test context manager interface"""
    print("\n🧪 Testing context manager...")
    
    with SyncGAScrap(headless=True) as scraper:
        scraper.goto("https://httpbin.org/json")
        scraper.screenshot("sync_context.png")
        
        # Test chaining
        scraper.scroll_to_bottom().screenshot("sync_bottom.png")
        
        print("✅ Context manager works!")


def test_method_chaining():
    """Test method chaining"""
    print("\n🧪 Testing method chaining...")
    
    with SyncGAScrap(headless=True) as scraper:
        # Chain multiple operations
        (scraper
         .goto("https://httpbin.org/html")
         .screenshot("sync_chain1.png")
         .scroll_to_bottom()
         .screenshot("sync_chain2.png"))
        
        print("✅ Method chaining works!")


def test_create_scraper_function():
    """Test the create_scraper function"""
    print("\n🧪 Testing create_scraper function...")
    
    scraper = create_scraper(headless=True)
    
    with scraper:
        scraper.goto("https://httpbin.org/html")
        title = scraper.get_text("h1")
        print(f"✅ Function interface works! Title: {title}")


def test_multiple_pages():
    """Test multiple page management"""
    print("\n🧪 Testing multiple pages...")
    
    with SyncGAScrap(headless=True) as scraper:
        # Main page
        scraper.goto("https://httpbin.org/html")
        
        # New page
        page2 = scraper.new_page()
        scraper.goto("https://httpbin.org/json", page=page2)
        
        print(f"✅ Multiple pages: {len(scraper.pages)} pages")
        
        # Close extra pages
        scraper.close_all_pages()
        print("✅ Pages cleaned up")


def main():
    """Run all tests"""
    print("🚀 Testing GA-Scrap Synchronous Interface")
    print("=" * 50)
    
    try:
        test_basic_sync()
        test_context_manager()
        test_method_chaining()
        test_create_scraper_function()
        test_multiple_pages()
        
        print("\n🎉 All synchronous interface tests passed!")
        print("✅ No async/await needed - simple and clean!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
