"""
Comprehensive Playwright Features Example
Demonstrates EVERY Playwright feature available in GA-Scrap
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import GAScrap


async def demonstrate_all_features():
    """Demonstrate every single Playwright feature"""
    
    # Initialize with advanced options
    scraper = GAScrap(
        headless=False,  # Visible browser for demonstration
        browser_type="chromium",
        viewport={"width": 1920, "height": 1080},
        record_video=True,
        record_har=True,
        accept_downloads=True,
        permissions=["geolocation", "camera", "microphone"],
        locale="en-US",
        timezone_id="America/New_York",
        color_scheme="light",
        geolocation={"latitude": 40.7128, "longitude": -74.0060}
    )
    
    try:
        await scraper.start()
        scraper.log("🚀 Starting comprehensive Playwright features demonstration", "success")
        
        # ==================== BASIC NAVIGATION ====================
        scraper.log("📍 1. Basic Navigation & Page Operations", "info")
        await scraper.goto("https://httpbin.org/html")
        
        # Take screenshot with options
        await scraper.screenshot("demo_basic.png", full_page=True)
        
        # Get page title and content
        title = await scraper.page.title()
        scraper.log(f"Page title: {title}", "info")
        
        # ==================== NETWORK FEATURES ====================
        scraper.log("🌐 2. Network Interception & Monitoring", "info")
        
        # Block images and stylesheets for faster loading
        await scraper.block_requests(resource_types=["image", "stylesheet"])
        
        # Intercept API requests
        async def log_api_requests(route, request):
            if "api" in request.url:
                scraper.log(f"API Request intercepted: {request.url}", "debug")
            await route.continue_()
        
        await scraper.intercept_requests("**/api/**", log_api_requests)
        
        # Emulate slow network
        await scraper.emulate_network_conditions(
            download_throughput=1000000,  # 1MB/s
            upload_throughput=500000,     # 500KB/s
            latency=100                   # 100ms
        )
        
        # ==================== DEVICE EMULATION ====================
        scraper.log("📱 3. Device Emulation & Mobile Features", "info")
        
        # Emulate iPhone
        await scraper.emulate_device("iPhone 12")
        await scraper.goto("https://httpbin.org/user-agent")
        
        # Simulate touch
        await scraper.simulate_touch(100, 100)
        
        # Rotate device
        await scraper.rotate_device(landscape=True)
        
        # ==================== ADVANCED INTERACTIONS ====================
        scraper.log("🖱️ 4. Advanced Mouse & Keyboard Interactions", "info")
        
        await scraper.goto("https://httpbin.org/forms/post")
        
        # Advanced typing with delay
        await scraper.type_with_delay("Test input with delay", delay=0.1)
        
        # Keyboard shortcuts
        await scraper.keyboard_press_sequence(["Control", "a"], delay=0.1)
        
        # Smooth mouse movement
        await scraper.mouse_move_smooth(500, 300, steps=20)
        
        # ==================== LOCATORS & ELEMENT OPERATIONS ====================
        scraper.log("🎯 5. Advanced Locators & Element Operations", "info")
        
        # Use different locator strategies
        text_input = scraper.get_locator_by_placeholder("Enter text here")
        submit_button = scraper.get_locator_by_role("button", name="Submit")
        
        # Get element attributes and styles
        if await text_input.count() > 0:
            attrs = await scraper.get_element_attributes("input[type='text']")
            scraper.log(f"Input attributes: {attrs}", "debug")
        
        # ==================== FILE OPERATIONS ====================
        scraper.log("📁 6. File Upload/Download Operations", "info")
        
        # Create a test file for upload
        test_file = Path("test_upload.txt")
        test_file.write_text("This is a test file for upload demonstration")
        
        # Note: File upload would work if there was a file input on the page
        # await scraper.upload_files("input[type='file']", [str(test_file)])
        
        # Save page as PDF
        pdf_path = await scraper.save_page_as_pdf("demo_page.pdf", {
            "format": "A4",
            "print_background": True,
            "margin": {"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
        })
        scraper.log(f"PDF saved: {pdf_path}", "success")
        
        # ==================== JAVASCRIPT EXECUTION ====================
        scraper.log("🔧 7. JavaScript Execution & Injection", "info")
        
        # Execute custom JavaScript
        page_info = await scraper.execute_script("""
            () => {
                return {
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    },
                    cookies: document.cookie
                };
            }
        """)
        scraper.log(f"Page info: {page_info}", "debug")
        
        # Inject custom CSS
        await scraper.inject_css(css_content="""
            body { 
                border: 5px solid red !important; 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
            }
        """)
        
        # ==================== PERFORMANCE & COVERAGE ====================
        scraper.log("📊 8. Performance Monitoring & Coverage", "info")
        
        # Start coverage tracking
        await scraper.start_css_coverage()
        await scraper.start_js_coverage()
        
        # Navigate to a page with resources
        await scraper.goto("https://httpbin.org/html")
        
        # Stop coverage and get results
        css_coverage = await scraper.stop_css_coverage()
        js_coverage = await scraper.stop_js_coverage()
        
        scraper.log(f"CSS coverage entries: {len(css_coverage)}", "info")
        scraper.log(f"JS coverage entries: {len(js_coverage)}", "info")
        
        # Get performance metrics
        metrics = await scraper.save_performance_metrics("performance_demo.json")
        scraper.log(f"Performance metrics saved", "success")
        
        # ==================== STORAGE & COOKIES ====================
        scraper.log("🍪 9. Storage & Cookie Management", "info")
        
        # Add custom cookies
        await scraper.add_cookies([
            {
                "name": "demo_cookie",
                "value": "demo_value",
                "domain": "httpbin.org",
                "path": "/"
            }
        ])
        
        # Get all cookies
        cookies = await scraper.get_cookies()
        scraper.log(f"Total cookies: {len(cookies)}", "info")
        
        # Save storage state
        storage_state = await scraper.save_storage_state("demo_storage.json")
        
        # ==================== ACCESSIBILITY ====================
        scraper.log("♿ 10. Accessibility Testing", "info")
        
        # Get accessibility tree
        accessibility_tree = await scraper.get_accessibility_tree()
        scraper.log("Accessibility tree captured", "info")
        
        # Check for accessibility issues
        accessibility_issues = await scraper.check_accessibility()
        scraper.log(f"Accessibility issues found: {len(accessibility_issues)}", "info")
        
        # ==================== ADVANCED WAITING ====================
        scraper.log("⏳ 11. Advanced Waiting Strategies", "info")
        
        # Wait for network idle
        await scraper.wait_for_network_idle(timeout=10000)
        
        # Wait for custom function
        await scraper.wait_for_function("() => document.readyState === 'complete'", timeout=5000)
        
        # ==================== FRAMES ====================
        scraper.log("🖼️ 12. Frame Operations", "info")
        
        # List all frames
        frame_urls = await scraper.list_frames()
        scraper.log(f"Frames found: {len(frame_urls)}", "info")
        
        # ==================== VIDEO RECORDING ====================
        scraper.log("🎥 13. Video Recording", "info")
        
        # Video recording was started automatically
        video = await scraper.start_video_recording()
        if video:
            scraper.log("Video recording active", "info")
        
        # ==================== MULTIPLE PAGES ====================
        scraper.log("📄 14. Multiple Page Management", "info")
        
        # Create additional pages
        page2 = await scraper.new_page()
        page3 = await scraper.new_page()
        
        # Navigate different pages simultaneously
        await asyncio.gather(
            scraper.goto("https://httpbin.org/json", page=page2),
            scraper.goto("https://httpbin.org/xml", page=page3)
        )
        
        scraper.log(f"Total pages: {len(scraper.pages)}", "info")
        
        # ==================== INFINITE SCROLL ====================
        scraper.log("📜 15. Infinite Scroll Simulation", "info")
        
        # Go to a page that might have scrollable content
        await scraper.goto("https://httpbin.org/html")
        
        # Simulate infinite scroll (limited for demo)
        await scraper.infinite_scroll(max_scrolls=3, delay=1.0)
        
        # ==================== FINAL SCREENSHOT ====================
        final_screenshot = await scraper.screenshot("demo_final.png", full_page=True)
        scraper.log(f"Final screenshot: {final_screenshot}", "success")
        
        # Save video if recording
        video_path = await scraper.save_video("demo_session.webm")
        if video_path:
            scraper.log(f"Video saved: {video_path}", "success")
        
        scraper.log("🎉 Comprehensive Playwright features demonstration completed!", "success")
        scraper.log(f"📊 Network requests captured: {len(scraper.requests)}", "info")
        scraper.log(f"📡 Network responses captured: {len(scraper.responses)}", "info")
        scraper.log(f"🖥️ Console messages captured: {len(scraper.console_messages)}", "info")
        scraper.log(f"⬇️ Downloads captured: {len(scraper.downloads)}", "info")
        
        # Cleanup test file
        if test_file.exists():
            test_file.unlink()
        
    except Exception as e:
        scraper.log(f"❌ Error during demonstration: {str(e)}", "error")
        
    finally:
        await scraper.stop()


if __name__ == "__main__":
    print("🚀 GA-Scrap Comprehensive Playwright Features Demo")
    print("=" * 60)
    print("This demo showcases EVERY Playwright feature available!")
    print("Watch the browser window to see all features in action.")
    print("=" * 60)
    
    asyncio.run(demonstrate_all_features())
