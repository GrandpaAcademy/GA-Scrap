"""
Advanced GA-Scrap Example
Demonstrates advanced features like multiple pages, data export, and configuration
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import GAScrap

async def scrape_news_site(scraper):
    """Scrape news articles from a demo site"""
    
    # Navigate to news site
    await scraper.goto("https://news.ycombinator.com/")
    
    # Wait for content to load
    await scraper.page.wait_for_selector(".athing")
    
    # Extract articles
    articles = await scraper.page.query_selector_all(".athing")
    scraper.log(f"📰 Found {len(articles)} articles", "info")
    
    article_data = []
    
    for i, article in enumerate(articles[:10]):  # First 10 articles
        try:
            # Get article title and link
            title_element = await article.query_selector(".titleline > a")
            if title_element:
                title = await title_element.inner_text()
                link = await title_element.get_attribute("href")
                
                # Get score (points)
                article_id = await article.get_attribute("id")
                score_element = await scraper.page.query_selector(f"#score_{article_id}")
                score = await score_element.inner_text() if score_element else "0 points"
                
                article_info = {
                    "id": i + 1,
                    "title": title,
                    "link": link,
                    "score": score
                }
                article_data.append(article_info)
                
                scraper.log(f"Article {i+1}: {title[:50]}...", "info")
                
        except Exception as e:
            scraper.log(f"Error extracting article {i+1}: {e}", "warning")
    
    return article_data

async def scrape_with_multiple_pages(scraper):
    """Demonstrate scraping across multiple pages"""
    
    scraper.log("🔄 Demonstrating multi-page scraping...", "info")
    
    # Create a new page for parallel scraping
    page2 = await scraper.new_page()
    
    # Navigate both pages simultaneously
    await asyncio.gather(
        scraper.goto("https://httpbin.org/html"),
        page2.goto("https://httpbin.org/json")
    )
    
    # Extract data from both pages
    html_title = await scraper.page.title()
    json_content = await page2.content()
    
    scraper.log(f"Page 1 title: {html_title}", "info")
    scraper.log(f"Page 2 content length: {len(json_content)} chars", "info")
    
    return {
        "page1_title": html_title,
        "page2_content_length": len(json_content)
    }

def save_data_to_file(data, filename):
    """Save scraped data to JSON file"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / f"{filename}.json"
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Data saved to: {filepath}")

async def main():
    """Advanced scraping example with multiple features"""
    
    # Initialize GA-Scrap with custom configuration
    scraper = GAScrap(
        headless=False,  # Keep browser visible
        browser_type="chromium",
        viewport={"width": 1920, "height": 1080},
        timeout=30000,
        slow_mo=500,  # Slow down for demonstration
        debug=True
    )
    
    try:
        scraper.log("🚀 Starting advanced scraping example...", "info")
        await scraper.start()
        
        # Example 1: Scrape news articles
        scraper.log("📰 Scraping news articles...", "info")
        articles = await scrape_news_site(scraper)
        
        # Example 2: Multi-page scraping
        multi_page_data = await scrape_with_multiple_pages(scraper)
        
        # Example 3: Using context manager for temporary pages
        async with scraper.context.new_page() as temp_page:
            await temp_page.goto("https://httpbin.org/user-agent")
            user_agent_info = await temp_page.text_content("body")
            scraper.log(f"🕵️ User agent info: {user_agent_info[:100]}...", "info")
        
        # Combine all data
        all_data = {
            "articles": articles,
            "multi_page": multi_page_data,
            "user_agent": user_agent_info,
            "scraping_timestamp": scraper.page.url,
            "total_articles": len(articles)
        }
        
        # Save data to file
        save_data_to_file(all_data, "advanced_scraping_results")
        
        # Display summary
        scraper.log("📊 Scraping Summary:", "success")
        scraper.log(f"   • Articles scraped: {len(articles)}", "info")
        scraper.log(f"   • Pages used: {len(scraper.pages)}", "info")
        scraper.log(f"   • Data saved to: output/advanced_scraping_results.json", "info")
        
        # Wait for user
        scraper.log("✨ Advanced scraping complete! Press Enter to close...", "success")
        input()
        
    except Exception as e:
        scraper.log(f"❌ Error: {e}", "error")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
