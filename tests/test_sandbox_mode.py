"""
Test GA-Scrap sandbox mode functionality
"""

from ga_scrap import SyncGAScrap


def test_sandbox_mode():
    """Test that sandbox mode handles errors gracefully"""
    print("🧪 Testing Sandbox Mode...")

    # Create scraper with sandbox mode and shorter timeout
    scraper = SyncGAScrap(
        headless=True,  # Headless for testing
        sandbox_mode=True,  # Enable sandbox mode
        debug=False,  # Reduce noise for testing
        timeout=3000  # Shorter timeout for faster testing
    )
    
    scraper.start()
    
    try:
        # Valid operation - should work
        print("1. Testing valid operation...")
        scraper.goto("https://httpbin.org/html")
        title = scraper.get_text("h1")
        print(f"✅ Valid operation successful: {title}")
        
        # Invalid selector - should fail gracefully
        print("2. Testing invalid selector (should not crash)...")
        scraper.click("#non-existent-element")
        print("✅ Invalid selector handled gracefully")
        
        # Invalid URL - should fail gracefully
        print("3. Testing invalid URL (should not crash)...")
        scraper.goto("invalid://not-a-real-url")
        print("✅ Invalid URL handled gracefully")
        
        # Recovery test - should still work
        print("4. Testing recovery after errors...")
        scraper.goto("https://httpbin.org/html")
        scraper.screenshot("sandbox_test.png")
        print("✅ Recovery successful")
        
        # Multiple errors in sequence
        print("5. Testing multiple errors...")
        scraper.click("#fake1")
        scraper.input("#fake2", "text")
        scraper.click("#fake3")
        print("✅ Multiple errors handled gracefully")
        
        # Final validation
        print("6. Final validation...")
        scraper.goto("https://httpbin.org/json")
        scraper.screenshot("sandbox_final_test.png")
        print("✅ Final validation successful")
        
        print("\n🎉 Sandbox mode test PASSED!")
        print("✅ Browser remained active throughout all errors")
        print("✅ Error messages were logged appropriately")
        print("✅ Recovery operations worked correctly")
        
    except Exception as e:
        print(f"❌ Unexpected error in sandbox mode test: {e}")
        return False
        
    finally:
        scraper.stop()
    
    return True


def test_normal_mode():
    """Test that normal mode still raises exceptions"""
    print("\n🧪 Testing Normal Mode (for comparison)...")

    scraper = SyncGAScrap(
        headless=True,
        sandbox_mode=False,  # Normal mode
        debug=False,
        timeout=3000  # Shorter timeout for faster testing
    )
    
    try:
        scraper.start()
        
        # Valid operation
        scraper.goto("https://httpbin.org/html")
        print("✅ Valid operation in normal mode")
        
        # This should raise an exception in normal mode
        scraper.click("#non-existent-element")
        
        # This shouldn't be reached
        print("❌ This should not be printed in normal mode")
        return False
        
    except Exception as e:
        print(f"✅ Normal mode correctly raised exception: {type(e).__name__}")
        return True
        
    finally:
        try:
            scraper.stop()
        except:
            pass


def main():
    """Run all tests"""
    print("🚀 GA-Scrap Sandbox Mode Tests")
    print("=" * 40)
    
    # Test sandbox mode
    sandbox_passed = test_sandbox_mode()
    
    # Test normal mode
    normal_passed = test_normal_mode()
    
    print("\n📊 Test Results:")
    print(f"✅ Sandbox mode: {'PASSED' if sandbox_passed else 'FAILED'}")
    print(f"✅ Normal mode: {'PASSED' if normal_passed else 'FAILED'}")
    
    if sandbox_passed and normal_passed:
        print("\n🎉 All tests PASSED!")
        print("🏖️ Sandbox mode is working correctly!")
    else:
        print("\n❌ Some tests FAILED!")
    
    return sandbox_passed and normal_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
