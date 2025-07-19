"""
Quick test of sandbox mode functionality
"""

from ga_scrap import SyncGAScrap
import time


def test_sandbox_quick():
    """Quick test of sandbox mode with fast timeouts"""
    print("🧪 Quick Sandbox Mode Test...")
    
    # Create scraper with very short timeout for fast testing
    scraper = SyncGAScrap(
        headless=True,
        sandbox_mode=True,
        timeout=1000,  # 1 second timeout
        debug=False
    )
    
    try:
        scraper.start()
        print("✅ Browser started")
        
        # Valid operation
        scraper.goto("https://httpbin.org/html")
        print("✅ Valid navigation works")
        
        # Invalid operation - should fail gracefully
        print("Testing invalid selector (1 second timeout)...")
        start_time = time.time()
        scraper.click("#definitely-does-not-exist")
        end_time = time.time()
        
        print(f"✅ Invalid selector handled in {end_time - start_time:.1f} seconds")
        print("✅ Browser is still active after error")
        
        # Recovery test
        scraper.screenshot("sandbox_recovery.png")
        print("✅ Recovery successful - screenshot taken")
        
        print("\n🎉 Quick sandbox test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        try:
            scraper.stop()
            print("✅ Clean shutdown")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


def test_error_types():
    """Test different types of errors in sandbox mode"""
    print("\n🧪 Testing Different Error Types...")
    
    scraper = SyncGAScrap(
        headless=True,
        sandbox_mode=True,
        timeout=1000,  # Fast timeout
        debug=False
    )
    
    try:
        scraper.start()
        scraper.goto("https://httpbin.org/html")
        
        # Test 1: Invalid selector
        print("1. Testing invalid selector...")
        scraper.click("#fake-element")
        print("✅ Invalid selector handled")
        
        # Test 2: Invalid input
        print("2. Testing invalid input...")
        scraper.input("#fake-input", "test")
        print("✅ Invalid input handled")
        
        # Test 3: Invalid URL (this one is fast)
        print("3. Testing invalid URL...")
        scraper.goto("invalid://not-a-url")
        print("✅ Invalid URL handled")
        
        # Test 4: Recovery
        print("4. Testing recovery...")
        scraper.goto("https://httpbin.org/html")
        scraper.screenshot("error_recovery.png")
        print("✅ Full recovery successful")
        
        print("\n🎉 All error types handled successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        try:
            scraper.stop()
        except:
            pass


def test_normal_mode_quick():
    """Quick test that normal mode still raises exceptions"""
    print("\n🧪 Quick Normal Mode Test...")
    
    scraper = SyncGAScrap(
        headless=True,
        sandbox_mode=False,  # Normal mode
        timeout=1000,
        debug=False
    )
    
    try:
        scraper.start()
        scraper.goto("https://httpbin.org/html")
        print("✅ Valid operation in normal mode")
        
        # This should raise an exception
        scraper.click("#definitely-does-not-exist")
        
        # Should not reach here
        print("❌ Normal mode should have raised exception")
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
    """Run quick tests"""
    print("🚀 GA-Scrap Quick Sandbox Tests")
    print("=" * 40)
    
    # Quick sandbox test
    sandbox_passed = test_sandbox_quick()
    
    # Error types test
    error_types_passed = test_error_types()
    
    # Normal mode test
    normal_passed = test_normal_mode_quick()
    
    print("\n📊 Quick Test Results:")
    print(f"✅ Sandbox mode: {'PASSED' if sandbox_passed else 'FAILED'}")
    print(f"✅ Error types: {'PASSED' if error_types_passed else 'FAILED'}")
    print(f"✅ Normal mode: {'PASSED' if normal_passed else 'FAILED'}")
    
    all_passed = sandbox_passed and error_types_passed and normal_passed
    
    if all_passed:
        print("\n🎉 All quick tests PASSED!")
        print("🏖️ Sandbox mode is working perfectly!")
    else:
        print("\n❌ Some tests FAILED!")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
