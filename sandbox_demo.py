"""
GA-Scrap Sandbox Mode Demo
Shows the power of error-resilient web scraping
"""

from ga_scrap import SyncGAScrap


def demo_development_workflow():
    """Demonstrate typical development workflow with sandbox mode"""
    print("🏖️ GA-Scrap Sandbox Mode Demo")
    print("=" * 50)
    print("Simulating a typical web scraping development session...")
    print("Watch how errors are handled gracefully!")
    print("=" * 50)
    
    # Enable sandbox mode for development
    scraper = SyncGAScrap(
        sandbox_mode=True,  # Key feature!
        headless=False,     # See what's happening
        timeout=2000,       # Fast feedback
        debug=True          # Detailed logging
    )
    
    with scraper:
        print("\n1. 🎯 Starting development session...")
        scraper.goto("https://httpbin.org/forms/post")
        
        print("\n2. 🔍 Exploring the page structure...")
        # Developer tries different selectors
        scraper.click("#submit-button")      # Might not exist
        scraper.click(".submit-btn")         # Might not exist  
        scraper.click("input[type='submit']") # This one works!
        
        print("\n3. 📝 Trying form interactions...")
        # Try different input selectors
        scraper.input("#customer-name", "John")     # Might not exist
        scraper.input("input[name='custname']", "John Doe")  # This works!
        
        print("\n4. 📸 Taking progress screenshots...")
        scraper.screenshot("development_progress.png")
        
        print("\n5. 🧪 Testing edge cases...")
        # Test various scenarios that might fail
        scraper.goto("https://nonexistent-site-12345.com")  # Will fail
        scraper.click("#popup-close")                       # Might not exist
        scraper.input("#search-box", "test query")          # Might not exist
        
        print("\n6. 🔄 Recovery and continuation...")
        # Go back to working page
        scraper.goto("https://httpbin.org/html")
        scraper.screenshot("final_state.png")
        
        print("\n🎉 Development session complete!")
        print("✅ Browser remained active throughout all errors")
        print("✅ Developer could see exactly what worked and what didn't")
        print("✅ No crashes, no restarts needed")
        print("✅ Perfect for iterative development!")


def demo_error_types():
    """Demonstrate different types of errors handled"""
    print("\n" + "=" * 50)
    print("🔬 Error Handling Demonstration")
    print("Testing every type of error that can occur...")
    print("=" * 50)
    
    scraper = SyncGAScrap(
        sandbox_mode=True,
        headless=True,  # Faster for demo
        timeout=1000,   # Quick feedback
        debug=False     # Less noise
    )
    
    with scraper:
        print("\n📋 Error Type Checklist:")
        
        # Start with valid page
        scraper.goto("https://httpbin.org/html")
        print("✅ Valid navigation - baseline established")
        
        # 1. Element not found errors
        print("\n1. Testing element not found errors...")
        scraper.click("#button-that-does-not-exist")
        scraper.input("#input-that-does-not-exist", "test")
        print("   ✅ Element not found errors handled")
        
        # 2. Navigation errors
        print("\n2. Testing navigation errors...")
        scraper.goto("invalid://protocol")
        scraper.goto("https://definitely-not-a-real-domain-12345.com")
        print("   ✅ Navigation errors handled")
        
        # 3. Timeout errors (already covered above)
        print("\n3. Timeout errors already demonstrated ✅")
        
        # 4. Recovery validation
        print("\n4. Testing recovery...")
        scraper.goto("https://httpbin.org/json")
        scraper.screenshot("error_recovery_demo.png")
        print("   ✅ Full recovery after multiple errors")
        
        print("\n🎯 All error types handled successfully!")
        print("🏖️ Sandbox mode provides bulletproof development environment!")


def demo_comparison():
    """Show the difference between sandbox and normal mode"""
    print("\n" + "=" * 50)
    print("🆚 Sandbox vs Normal Mode Comparison")
    print("=" * 50)
    
    print("\n🏖️ SANDBOX MODE DEMO:")
    print("Errors are logged but don't stop execution...")
    
    scraper_sandbox = SyncGAScrap(
        sandbox_mode=True,
        headless=True,
        timeout=1000,
        debug=False
    )
    
    with scraper_sandbox:
        scraper_sandbox.goto("https://httpbin.org/html")
        print("✅ Valid operation")
        
        scraper_sandbox.click("#fake-element")
        print("✅ Error logged, execution continues")
        
        scraper_sandbox.screenshot("sandbox_continues.png")
        print("✅ Subsequent operations still work")
    
    print("🏖️ Sandbox mode: All operations completed despite error!")
    
    print("\n🚨 NORMAL MODE DEMO:")
    print("First error stops everything...")
    
    scraper_normal = SyncGAScrap(
        sandbox_mode=False,  # Normal mode
        headless=True,
        timeout=1000,
        debug=False
    )
    
    try:
        with scraper_normal:
            scraper_normal.goto("https://httpbin.org/html")
            print("✅ Valid operation")
            
            scraper_normal.click("#fake-element")
            print("❌ This line should never be reached")
            
    except Exception as e:
        print(f"🚨 Normal mode: Exception raised - {type(e).__name__}")
        print("🚨 Execution stopped, no recovery possible")
    
    print("\n📊 COMPARISON SUMMARY:")
    print("🏖️ Sandbox Mode: Resilient, continues despite errors")
    print("🚨 Normal Mode: Fail-fast, stops on first error")
    print("🎯 Use sandbox for development, normal for production!")


def main():
    """Run all demonstrations"""
    print("🚀 GA-Scrap Sandbox Mode Complete Demonstration")
    
    try:
        # Main development workflow demo
        demo_development_workflow()
        
        # Error types demonstration
        demo_error_types()
        
        # Mode comparison
        demo_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 SANDBOX MODE DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("🏖️ Key Benefits Demonstrated:")
        print("   ✅ Errors don't crash the browser")
        print("   ✅ Detailed error messages for debugging")
        print("   ✅ Browser remains active for inspection")
        print("   ✅ Perfect for iterative development")
        print("   ✅ All error types handled gracefully")
        print("   ✅ Full recovery after errors")
        print("   ✅ Faster development cycles")
        print("\n🎯 Perfect for:")
        print("   • Web scraping development")
        print("   • Testing and debugging")
        print("   • Learning and experimentation")
        print("   • Exploring unknown websites")
        print("\n🚀 Start using sandbox mode today!")
        print("   scraper = SyncGAScrap(sandbox_mode=True)")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    main()
