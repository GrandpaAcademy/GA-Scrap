"""
GA-Scrap Easy Syntax Example
Demonstrates how simple it is to use GA-Scrap without async/await
"""

import sys
import os

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import SyncGAScrap, create_scraper


def basic_example():
    """Basic scraping example - no async needed!"""
    print("🚀 Basic Example - No async/await required!")
    
    # Create scraper instance
    scraper = SyncGAScrap(headless=False)  # Visible browser
    
    # Start browser
    scraper.start()
    
    # Navigate and interact - simple as that!
    scraper.goto("https://httpbin.org/html")
    scraper.screenshot("easy_basic.png")
    
    # Get text content
    title = scraper.get_text("h1")
    print(f"Page title: {title}")
    
    # Stop browser
    scraper.stop()
    
    print("✅ Basic example completed!")


def context_manager_example():
    """Using context manager for automatic cleanup"""
    print("\n🔄 Context Manager Example")
    
    # Automatic start/stop with context manager
    with SyncGAScrap(headless=False) as scraper:
        scraper.goto("https://httpbin.org/forms/post")
        scraper.screenshot("easy_form.png")
        
        # Fill out a form
        scraper.input("input[name='custname']", "John Doe")
        scraper.input("input[name='custtel']", "123-456-7890")
        scraper.input("input[name='custemail']", "john@example.com")
        
        # Take screenshot of filled form
        scraper.screenshot("easy_form_filled.png")
        
        print("✅ Form filled and screenshot taken!")
    
    # Browser automatically closed when exiting context


def multi_page_example():
    """Multiple pages made easy"""
    print("\n📄 Multi-Page Example")
    
    scraper = SyncGAScrap(headless=False)
    scraper.start()
    
    # Page 1
    scraper.goto("https://httpbin.org/html")
    scraper.screenshot("easy_page1.png")
    
    # Page 2
    page2 = scraper.new_page()
    scraper.goto("https://httpbin.org/json", page=page2)
    scraper.screenshot("easy_page2.png", page=page2)
    
    # Page 3
    page3 = scraper.new_page()
    scraper.goto("https://httpbin.org/xml", page=page3)
    scraper.screenshot("easy_page3.png", page=page3)
    
    print(f"Total pages: {len(scraper.pages)}")
    
    # Close all extra pages
    scraper.close_all_pages()
    scraper.stop()
    
    print("✅ Multi-page example completed!")


def advanced_features_example():
    """Advanced features with easy syntax"""
    print("\n🌟 Advanced Features Example")
    
    with SyncGAScrap(headless=False) as scraper:
        # Navigate
        scraper.goto("https://httpbin.org/html")
        
        # Scroll operations
        scraper.scroll_to_bottom()
        scraper.screenshot("easy_bottom.png")
        
        scraper.scroll_to_top()
        scraper.screenshot("easy_top.png")
        
        # JavaScript execution
        page_info = scraper.execute_script("""
            () => ({
                title: document.title,
                url: window.location.href,
                userAgent: navigator.userAgent
            })
        """)
        print(f"Page info: {page_info}")
        
        # CSS injection
        scraper.inject_css(css_content="""
            body { 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
                border: 5px solid gold !important;
            }
        """)
        scraper.screenshot("easy_styled.png")
        
        # Cookie management
        scraper.add_cookies([{
            "name": "demo_cookie",
            "value": "easy_value",
            "domain": "httpbin.org",
            "path": "/"
        }])
        
        cookies = scraper.get_cookies()
        print(f"Cookies: {len(cookies)}")
        
        # PDF generation
        pdf_path = scraper.save_pdf("easy_page.pdf")
        print(f"PDF saved: {pdf_path}")
        
        # Wait for network idle
        scraper.wait_for_network_idle()
        
        print("✅ Advanced features example completed!")


def mobile_example():
    """Mobile device emulation"""
    print("\n📱 Mobile Example")
    
    # Create scraper with mobile device
    scraper = SyncGAScrap(headless=False)
    scraper.start()
    
    # Emulate iPhone
    scraper.emulate_device("iPhone 12")
    scraper.goto("https://httpbin.org/user-agent")
    scraper.screenshot("easy_mobile.png")
    
    # Get user agent to verify mobile emulation
    user_agent = scraper.execute_script("() => navigator.userAgent")
    print(f"Mobile user agent: {user_agent}")
    
    scraper.stop()
    print("✅ Mobile example completed!")


def chaining_example():
    """Method chaining for fluent interface"""
    print("\n🔗 Method Chaining Example")
    
    with SyncGAScrap(headless=False) as scraper:
        # Chain multiple operations
        (scraper
         .goto("https://httpbin.org/html")
         .scroll_to_bottom()
         .screenshot("easy_chain1.png")
         .scroll_to_top()
         .screenshot("easy_chain2.png")
         .inject_css(css_content="body { filter: sepia(100%) !important; }")
         .screenshot("easy_chain3.png"))
        
        print("✅ Method chaining example completed!")


def simple_function_interface():
    """Using the simple function interface"""
    print("\n🎯 Simple Function Interface")
    
    # Even simpler - one function call
    scraper = create_scraper(headless=False)
    
    with scraper:
        scraper.goto("https://httpbin.org/html")
        title = scraper.get_text("h1")
        scraper.screenshot("easy_simple.png")
        
        print(f"Title: {title}")
        print("✅ Simple function interface completed!")


def main():
    """Run all examples"""
    print("🚀 GA-Scrap Easy Syntax Examples")
    print("=" * 50)
    print("No async/await needed - just simple, clean code!")
    print("=" * 50)
    
    try:
        basic_example()
        context_manager_example()
        multi_page_example()
        advanced_features_example()
        mobile_example()
        chaining_example()
        simple_function_interface()
        
        print("\n🎉 All examples completed successfully!")
        print("📸 Check the generated screenshots and PDF files")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
