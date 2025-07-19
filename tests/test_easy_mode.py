"""
Test GA-Scrap Easy Mode
Demonstrates how incredibly easy GA-Scrap has become!
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ga_scrap import SimpleScraper, scrape, scrape_all, scrape_data

async def test_one_liners():
    """Test one-liner functions"""
    print("🚀 Testing One-liner Functions")
    print("-" * 40)
    
    # Test 1: Single element
    print("1. Getting page title...")
    title = await scrape("https://example.com", "h1", headless=True)
    print(f"   ✅ Title: {title}")
    
    # Test 2: Multiple elements
    print("2. Getting all quotes...")
    quotes = await scrape_all("https://quotes.toscrape.com", ".quote .text", headless=True)
    print(f"   ✅ Found {len(quotes)} quotes")
    for i, quote in enumerate(quotes[:2], 1):
        print(f"   Quote {i}: {quote[:50]}...")
    
    # Test 3: Structured data
    print("3. Getting structured data...")
    data = await scrape_data("https://quotes.toscrape.com", {
        "title": "title",
        "quotes": ".quote .text[]",
        "authors": ".quote .author[]",
        "first_quote": ".quote .text"
    }, headless=True)
    
    print(f"   ✅ Page title: {data['title']}")
    print(f"   ✅ First quote: {data['first_quote'][:50]}...")
    print(f"   ✅ Total quotes: {len(data['quotes'])}")
    print(f"   ✅ Total authors: {len(data['authors'])}")

async def test_simple_scraper():
    """Test SimpleScraper class"""
    print("\n🚀 Testing SimpleScraper Class")
    print("-" * 40)
    
    async with SimpleScraper(headless=True) as scraper:
        # Navigate
        await scraper.go("https://httpbin.org/html")
        
        # Get title
        title = await scraper.get("title")
        print(f"1. ✅ Page title: {title}")
        
        # Get heading
        heading = await scraper.get("h1")
        print(f"2. ✅ Main heading: {heading}")
        
        # Get all paragraphs
        paragraphs = await scraper.get_all("p")
        print(f"3. ✅ Found {len(paragraphs)} paragraphs")
        
        # Take screenshot
        await scraper.screenshot("test_screenshot.png")
        print("4. ✅ Screenshot taken: test_screenshot.png")

async def test_advanced_features():
    """Test advanced SimpleScraper features"""
    print("\n🚀 Testing Advanced Features")
    print("-" * 40)
    
    async with SimpleScraper(headless=True) as scraper:
        # Go to a form page
        await scraper.go("https://httpbin.org/forms/post")
        
        # Fill out form
        await scraper.type("input[name='custname']", "Test User")
        await scraper.type("input[name='custtel']", "123-456-7890")
        print("1. ✅ Form filled out")
        
        # Wait for element (should already be there)
        await scraper.wait("input[type='submit']", seconds=1)
        print("2. ✅ Submit button found")
        
        # Take screenshot of filled form
        await scraper.screenshot("filled_form.png")
        print("3. ✅ Form screenshot taken: filled_form.png")

def show_cli_examples():
    """Show CLI command examples"""
    print("\n🚀 CLI Command Examples")
    print("-" * 40)
    print("Try these commands in your terminal:")
    print()
    print("# Get page title instantly:")
    print("ga-scrap quick 'https://example.com' 'h1'")
    print()
    print("# Get all quotes:")
    print("ga-scrap quick 'https://quotes.toscrape.com' '.quote .text' --all")
    print()
    print("# Run in headless mode:")
    print("ga-scrap quick 'https://example.com' 'h1' --headless")

async def main():
    """Run all easy mode tests"""
    print("🎉 GA-Scrap Easy Mode Test Suite")
    print("=" * 50)
    
    try:
        await test_one_liners()
        await test_simple_scraper()
        await test_advanced_features()
        show_cli_examples()
        
        print("\n" + "=" * 50)
        print("🎉 All Easy Mode tests passed!")
        print("\n✨ GA-Scrap is now SUPER EASY to use!")
        print("\n💡 Key improvements:")
        print("   • One-liner functions: scrape(), scrape_all(), scrape_data()")
        print("   • SimpleScraper class with easy methods")
        print("   • Quick CLI command: ga-scrap quick")
        print("   • Automatic browser management")
        print("   • Built-in logging and error handling")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
