"""
Hot Reload Example
Demonstrates GA-Scrap with hot reload functionality
Edit this file while it's running to see automatic restart!
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import GAScrap

async def main():
    """Hot reload demonstration"""
    
    # Initialize GA-Scrap
    scraper = GAScrap(
        headless=False,
        browser_type="chromium",
        debug=True
    )
    
    try:
        # Show current time to demonstrate reload
        current_time = datetime.now().strftime("%H:%M:%S")
        scraper.log(f"🕐 Script started at: {current_time}", "success")
        scraper.log("🔥 Hot reload is active! Try editing this file...", "info")
        
        await scraper.start()
        
        # Navigate to a simple page
        await scraper.goto("https://httpbin.org/html")
        
        # Get page title
        title = await scraper.page.title()
        scraper.log(f"📄 Current page: {title}", "info")
        
        # Extract some content
        h1_element = await scraper.page.query_selector("h1")
        if h1_element:
            h1_text = await h1_element.inner_text()
            scraper.log(f"📝 Main heading: {h1_text}", "info")
        
        # Show some dynamic content
        scraper.log("🎯 Try editing this message and save the file!", "success")
        scraper.log("🔄 The script will automatically restart", "info")
        
        # Keep the script running
        scraper.log("⏳ Keeping browser open... (Ctrl+C to stop)", "info")
        
        # Wait indefinitely (until hot reload restarts or user stops)
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        scraper.log("👋 Stopping script...", "warning")
    except Exception as e:
        scraper.log(f"❌ Error: {e}", "error")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
