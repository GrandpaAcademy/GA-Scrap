"""
Super Simple GA-Scrap Example
The easiest way to scrape websites!
"""

import asyncio
import sys
import os

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import SimpleScraper, scrape, scrape_all, scrape_data

async def example_1_simple_scraper():
    """Example 1: Using SimpleScraper class"""
    print("🚀 Example 1: Simple Scraper Class")
    
    async with SimpleScraper() as scraper:
        # Go to a website
        await scraper.go("https://quotes.toscrape.com")
        
        # Get the page title
        title = await scraper.get("title")
        scraper.log(f"Page title: {title}")
        
        # Get the first quote
        first_quote = await scraper.get(".quote .text")
        scraper.log(f"First quote: {first_quote}")
        
        # Get all quotes
        all_quotes = await scraper.get_all(".quote .text")
        scraper.log(f"Found {len(all_quotes)} quotes")
        
        # Pause to see the browser
        await scraper.pause("Check out the browser! Press Enter to continue...")

async def example_2_one_liner():
    """Example 2: One-liner scraping"""
    print("\n🚀 Example 2: One-liner Scraping")
    
    # Get page title in one line
    title = await scrape("https://example.com", "h1")
    print(f"Page title: {title}")
    
    # Get all quotes in one line
    quotes = await scrape_all("https://quotes.toscrape.com", ".quote .text")
    print(f"Found {len(quotes)} quotes:")
    for i, quote in enumerate(quotes[:3], 1):  # Show first 3
        print(f"  {i}. {quote[:50]}...")

async def example_3_structured_data():
    """Example 3: Scrape structured data"""
    print("\n🚀 Example 3: Structured Data Scraping")
    
    # Define what data to scrape
    selectors = {
        "title": "title",
        "quotes": ".quote .text[]",  # [] means get all matching elements
        "authors": ".quote .author[]",
        "first_quote": ".quote .text"  # No [] means get just the first one
    }
    
    # Scrape all data at once
    data = await scrape_data("https://quotes.toscrape.com", selectors)
    
    print(f"Page title: {data['title']}")
    print(f"First quote: {data['first_quote']}")
    print(f"Found {len(data['quotes'])} quotes and {len(data['authors'])} authors")
    
    # Show first few quotes with authors
    for quote, author in zip(data['quotes'][:3], data['authors'][:3]):
        print(f"  '{quote[:40]}...' - {author}")

async def example_4_interactive():
    """Example 4: Interactive scraping with clicks and typing"""
    print("\n🚀 Example 4: Interactive Scraping")
    
    async with SimpleScraper() as scraper:
        # Go to a search page
        await scraper.go("https://httpbin.org/forms/post")
        
        # Fill out a form
        await scraper.type("input[name='custname']", "John Doe")
        await scraper.type("input[name='custtel']", "123-456-7890")
        await scraper.type("input[name='custemail']", "john@example.com")
        
        scraper.log("Form filled out!")
        
        # Take a screenshot
        await scraper.screenshot("form_filled.png")
        
        # Pause to see the result
        await scraper.pause("Form is filled! Check the screenshot. Press Enter to continue...")

async def main():
    """Run all examples"""
    print("🎉 GA-Scrap Super Simple Examples")
    print("=" * 50)
    
    try:
        await example_1_simple_scraper()
        await example_2_one_liner()
        await example_3_structured_data()
        await example_4_interactive()
        
        print("\n" + "=" * 50)
        print("🎉 All examples completed!")
        print("\n💡 Try these one-liners in your terminal:")
        print("   ga-scrap quick 'https://quotes.toscrape.com' '.quote .text' --all")
        print("   ga-scrap quick 'https://example.com' 'h1'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
