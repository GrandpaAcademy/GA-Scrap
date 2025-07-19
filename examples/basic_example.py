"""
Basic GA-Scrap Example
Demonstrates core functionality with a simple scraper
"""

import asyncio
import sys
import os

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import GAScrap

async def main():
    """Basic scraping example"""
    
    # Initialize GA-Scrap with visible browser (default behavior)
    scraper = GAScrap(
        headless=False,  # Browser will be visible - great for development!
        browser_type="chromium",
        debug=True
    )
    
    try:
        # Start the browser
        scraper.log("🚀 Starting basic scraping example...", "info")
        await scraper.start()
        
        # Navigate to a test website
        await scraper.goto("https://quotes.toscrape.com/")
        
        # Get page title
        title = await scraper.page.title()
        scraper.log(f"📄 Page title: {title}", "success")
        
        # Extract quotes
        quotes = await scraper.page.query_selector_all(".quote")
        scraper.log(f"📝 Found {len(quotes)} quotes", "info")
        
        # Extract data from each quote
        quote_data = []
        for i, quote in enumerate(quotes[:3]):  # Just first 3 quotes
            text_element = await quote.query_selector(".text")
            author_element = await quote.query_selector(".author")
            
            if text_element and author_element:
                text = await text_element.inner_text()
                author = await author_element.inner_text()
                
                quote_info = {
                    "text": text,
                    "author": author
                }
                quote_data.append(quote_info)
                
                scraper.log(f"Quote {i+1}: {text[:50]}... - {author}", "info")
        
        # Wait for user to see the results
        scraper.log("✨ Scraping complete! Press Enter to close browser...", "success")
        input()
        
    except Exception as e:
        scraper.log(f"❌ Error: {e}", "error")
    
    finally:
        # Always cleanup
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
