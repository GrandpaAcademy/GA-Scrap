"""
GA-Scrap Sandbox Mode Example
Demonstrates error handling that doesn't shutdown the browser
"""

import sys
import os

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import SyncGAScrap


def demonstrate_sandbox_mode():
    """Demonstrate sandbox mode error handling"""
    print("🏖️ GA-Scrap Sandbox Mode Demo")
    print("=" * 50)
    print("In sandbox mode, errors don't shutdown the browser!")
    print("Perfect for development and testing.")
    print("=" * 50)
    
    # Create scraper with sandbox mode enabled
    scraper = SyncGAScrap(
        headless=False,  # Visible browser
        sandbox_mode=True,  # Enable sandbox mode
        debug=True  # Show detailed logs
    )
    
    scraper.start()
    
    try:
        print("\n1. ✅ Valid operation - should work")
        scraper.goto("https://httpbin.org/html")
        scraper.screenshot("sandbox_valid.png")
        print("✅ Valid operations completed successfully!")
        
        print("\n2. ❌ Invalid selector - should fail gracefully")
        # This will fail but browser stays open
        scraper.click("#non-existent-element")
        print("🏖️ Browser is still running despite the error!")
        
        print("\n3. ❌ Invalid URL - should fail gracefully")
        # This will fail but browser stays open
        scraper.goto("invalid://not-a-real-url")
        print("🏖️ Browser is still running despite the error!")
        
        print("\n4. ❌ Invalid input selector - should fail gracefully")
        # This will fail but browser stays open
        scraper.input("#another-non-existent-element", "test text")
        print("🏖️ Browser is still running despite the error!")
        
        print("\n5. ✅ Recovery - valid operations still work")
        # Go back to a valid page
        scraper.goto("https://httpbin.org/forms/post")
        scraper.screenshot("sandbox_recovery.png")
        
        # Try valid interactions
        scraper.input("input[name='custname']", "John Doe")
        scraper.screenshot("sandbox_form_filled.png")
        print("✅ Recovery successful! Browser is fully functional!")
        
        print("\n6. 🔄 Multiple errors in sequence")
        scraper.click("#fake1")  # Error 1
        scraper.click("#fake2")  # Error 2
        scraper.input("#fake3", "text")  # Error 3
        scraper.goto("bad://url")  # Error 4
        print("🏖️ Multiple errors handled gracefully!")
        
        print("\n7. ✅ Final validation")
        scraper.goto("https://httpbin.org/html")
        title = scraper.get_text("h1")
        scraper.screenshot("sandbox_final.png")
        print(f"✅ Final test successful! Page title: {title}")
        
        print("\n🎉 Sandbox Mode Demo Complete!")
        print("Key Benefits:")
        print("- ✅ Errors don't crash the browser")
        print("- ✅ Detailed error messages shown")
        print("- ✅ Browser remains active for debugging")
        print("- ✅ Can recover and continue operations")
        print("- ✅ Perfect for development and testing")
        
        # Keep browser open for inspection
        scraper.pause("🔍 Inspect the browser and press Enter to close...")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        scraper.stop()


def demonstrate_normal_mode():
    """Demonstrate normal mode (errors cause shutdown)"""
    print("\n" + "=" * 50)
    print("🚨 Normal Mode Demo (for comparison)")
    print("In normal mode, errors will shutdown the browser")
    print("=" * 50)
    
    # Create scraper with sandbox mode disabled (default)
    scraper = SyncGAScrap(
        headless=True,  # Headless for quick demo
        sandbox_mode=False,  # Normal mode (default)
        debug=True
    )
    
    try:
        scraper.start()
        
        print("\n1. ✅ Valid operation")
        scraper.goto("https://httpbin.org/html")
        print("✅ Valid operation completed")
        
        print("\n2. ❌ This error will cause shutdown in normal mode")
        # This will raise an exception and stop execution
        scraper.click("#non-existent-element")
        
        # This line won't be reached in normal mode
        print("This won't be printed in normal mode")
        
    except Exception as e:
        print(f"❌ Error in normal mode: {e}")
        print("🚨 Browser shutdown due to error (normal behavior)")
        
    finally:
        try:
            scraper.stop()
        except:
            pass


def interactive_sandbox_demo():
    """Interactive demo where user can test error handling"""
    print("\n" + "=" * 50)
    print("🎮 Interactive Sandbox Demo")
    print("Try different operations and see error handling!")
    print("=" * 50)
    
    scraper = SyncGAScrap(
        headless=False,
        sandbox_mode=True,
        debug=True
    )
    
    scraper.start()
    scraper.goto("https://httpbin.org/html")
    
    print("\n🎮 Interactive Mode - Try these commands:")
    print("1. scraper.click('#valid-element')  # Should work")
    print("2. scraper.click('#fake-element')   # Should fail gracefully")
    print("3. scraper.goto('invalid://url')    # Should fail gracefully")
    print("4. scraper.screenshot('test.png')   # Should work")
    print("5. Type 'quit' to exit")
    
    while True:
        try:
            command = input("\n🎮 Enter command (or 'quit'): ").strip()
            
            if command.lower() == 'quit':
                break
            
            if command.startswith('scraper.'):
                # Remove 'scraper.' prefix and execute
                method_call = command[8:]
                
                if method_call.startswith('click('):
                    selector = method_call[6:-1].strip('\'"')
                    scraper.click(selector)
                elif method_call.startswith('goto('):
                    url = method_call[5:-1].strip('\'"')
                    scraper.goto(url)
                elif method_call.startswith('input('):
                    # Parse input(selector, text)
                    args = method_call[6:-1].split(',', 1)
                    if len(args) == 2:
                        selector = args[0].strip().strip('\'"')
                        text = args[1].strip().strip('\'"')
                        scraper.input(selector, text)
                elif method_call.startswith('screenshot('):
                    filename = method_call[11:-1].strip('\'"')
                    scraper.screenshot(filename)
                else:
                    print("❌ Unsupported command. Try: click, goto, input, screenshot")
            else:
                print("❌ Commands must start with 'scraper.'")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Command error: {e}")
    
    scraper.stop()
    print("🎮 Interactive demo ended!")


def main():
    """Run all sandbox mode demonstrations"""
    print("🚀 GA-Scrap Sandbox Mode Demonstrations")
    
    # Main sandbox demo
    demonstrate_sandbox_mode()
    
    # Normal mode comparison
    demonstrate_normal_mode()
    
    # Ask if user wants interactive demo
    response = input("\n🎮 Would you like to try the interactive demo? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_sandbox_demo()
    
    print("\n🎉 All demonstrations complete!")
    print("🏖️ Sandbox mode is perfect for development and testing!")


if __name__ == "__main__":
    main()
