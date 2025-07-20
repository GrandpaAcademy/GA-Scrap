"""
Infinite Scroll Scraper Template
Demonstrates how to handle infinite scroll, dynamic content loading, and pagination
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class InfiniteScrollScraper:
    """Template for scraping infinite scroll and dynamic content"""
    
    def __init__(self, scroll_config: Dict[str, Any] = None):
        """
        Initialize infinite scroll scraper
        
        Args:
            scroll_config: Configuration for scrolling behavior
        """
        self.scroll_config = scroll_config or self._get_default_scroll_config()
        self.scraped_items = []
        self.seen_items = set()
        
    def _get_default_scroll_config(self) -> Dict[str, Any]:
        """Get default scrolling configuration"""
        return {
            "scroll_method": "bottom",  # "bottom", "element", "pixels"
            "scroll_pause": 2.0,  # Seconds to wait after each scroll
            "max_scrolls": 10,  # Maximum number of scrolls
            "scroll_pixels": 1000,  # Pixels to scroll (if method is "pixels")
            "load_timeout": 10.0,  # Timeout for content to load
            "duplicate_threshold": 3,  # Stop if this many consecutive duplicates
            "content_selector": ".item, .post, .product",  # Selector for content items
            "loading_indicator": ".loading, .spinner",  # Loading indicator selector
            "end_indicator": ".end-of-content, .no-more-items"  # End of content indicator
        }
    
    def scrape_infinite_scroll(self, url: str, item_selectors: Dict[str, str],
                              custom_scroll_handler: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Scrape content from infinite scroll page
        
        Args:
            url: URL of the page with infinite scroll
            item_selectors: Selectors for extracting data from each item
            custom_scroll_handler: Optional custom scrolling logic
            
        Returns:
            List of scraped items
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🔄 Starting infinite scroll scraping...", "info")
            
            # Navigate to page
            scraper.goto(url)
            
            # Handle initial popups
            self._handle_popups(scraper)
            
            # Wait for initial content to load
            scraper.wait_for_selector(self.scroll_config["content_selector"], timeout=10000)
            
            scroll_count = 0
            consecutive_duplicates = 0
            
            while scroll_count < self.scroll_config["max_scrolls"]:
                scraper.log(f"📜 Scroll {scroll_count + 1}/{self.scroll_config['max_scrolls']}", "info")
                
                # Extract items before scrolling
                items_before = len(self.scraped_items)
                
                # Extract current visible items
                new_items = self._extract_visible_items(scraper, item_selectors)
                
                # Check for duplicates
                new_unique_items = 0
                for item in new_items:
                    item_id = self._generate_item_id(item)
                    if item_id not in self.seen_items:
                        self.seen_items.add(item_id)
                        self.scraped_items.append(item)
                        new_unique_items += 1
                
                scraper.log(f"📦 Found {new_unique_items} new items", "info")
                
                # Check for consecutive duplicates
                if new_unique_items == 0:
                    consecutive_duplicates += 1
                    if consecutive_duplicates >= self.scroll_config["duplicate_threshold"]:
                        scraper.log("🛑 Stopping due to consecutive duplicates", "warning")
                        break
                else:
                    consecutive_duplicates = 0
                
                # Check for end of content indicator
                if self._check_end_of_content(scraper):
                    scraper.log("🏁 Reached end of content", "info")
                    break
                
                # Perform scroll
                if custom_scroll_handler:
                    scroll_success = custom_scroll_handler(scraper, scroll_count)
                else:
                    scroll_success = self._perform_scroll(scraper)
                
                if not scroll_success:
                    scraper.log("❌ Scroll failed, stopping", "warning")
                    break
                
                # Wait for new content to load
                self._wait_for_content_load(scraper)
                
                scroll_count += 1
            
            scraper.log(f"✅ Infinite scroll complete! Scraped {len(self.scraped_items)} items", "success")
            return self.scraped_items
    
    def _extract_visible_items(self, scraper: SyncGAScrap, item_selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract data from currently visible items"""
        items = []
        
        # Get all item containers
        item_containers = scraper.get_all_elements(self.scroll_config["content_selector"])
        
        for i in range(len(item_containers)):
            try:
                item_data = self._extract_single_item(scraper, i, item_selectors)
                if item_data:
                    items.append(item_data)
            except Exception as e:
                scraper.log(f"⚠️ Error extracting item {i}: {e}", "warning")
                continue
        
        return items
    
    def _extract_single_item(self, scraper: SyncGAScrap, index: int, 
                           item_selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data from a single item"""
        base_selector = f"{self.scroll_config['content_selector']}:nth-child({index + 1})"
        
        item_data = {
            "scraped_at": datetime.now().isoformat(),
            "item_index": index
        }
        
        # Extract each field
        for field_name, selector in item_selectors.items():
            try:
                # Combine base selector with field selector
                full_selector = f"{base_selector} {selector}"
                
                if selector.endswith("[]"):
                    # Multiple elements
                    full_selector = full_selector[:-2]
                    values = scraper.get_all_text(full_selector)
                    item_data[field_name] = values
                elif selector.startswith("@"):
                    # Attribute extraction
                    attr_selector, attr_name = selector[1:].split("@")
                    full_selector = f"{base_selector} {attr_selector}"
                    value = scraper.get_attribute(full_selector, attr_name)
                    item_data[field_name] = value
                else:
                    # Single element text
                    value = scraper.get_text(full_selector)
                    item_data[field_name] = value
                    
            except Exception as e:
                scraper.log(f"⚠️ Could not extract {field_name}: {e}", "debug")
                item_data[field_name] = None
        
        # Only return item if we extracted meaningful data
        meaningful_fields = [k for k, v in item_data.items() 
                           if v and k not in ["scraped_at", "item_index"]]
        return item_data if meaningful_fields else None
    
    def _generate_item_id(self, item: Dict[str, Any]) -> str:
        """Generate unique ID for an item to detect duplicates"""
        # Use a combination of fields to create unique ID
        id_fields = []
        
        # Common fields that might be unique
        for field in ["title", "url", "id", "link", "text"]:
            if field in item and item[field]:
                id_fields.append(str(item[field])[:100])  # Limit length
        
        if not id_fields:
            # Fallback to all non-metadata fields
            for key, value in item.items():
                if key not in ["scraped_at", "item_index"] and value:
                    id_fields.append(str(value)[:50])
        
        return "|".join(id_fields)
    
    def _perform_scroll(self, scraper: SyncGAScrap) -> bool:
        """Perform scrolling action"""
        try:
            scroll_method = self.scroll_config["scroll_method"]
            
            if scroll_method == "bottom":
                # Scroll to bottom of page
                scraper.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
            elif scroll_method == "pixels":
                # Scroll by specific number of pixels
                pixels = self.scroll_config["scroll_pixels"]
                scraper.page.evaluate(f"window.scrollBy(0, {pixels})")
                
            elif scroll_method == "element":
                # Scroll to a specific element (like "Load More" button)
                load_more_selectors = [
                    ".load-more", ".show-more", ".next-page",
                    "button:contains('Load More')", "button:contains('Show More')"
                ]
                
                for selector in load_more_selectors:
                    if scraper.click(selector):
                        return True
                
                # If no button found, scroll to bottom as fallback
                scraper.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for scroll to complete
            time.sleep(self.scroll_config["scroll_pause"])
            return True
            
        except Exception as e:
            scraper.log(f"❌ Scroll error: {e}", "error")
            return False
    
    def _wait_for_content_load(self, scraper: SyncGAScrap):
        """Wait for new content to load after scrolling"""
        # Wait for loading indicator to disappear
        loading_selector = self.scroll_config["loading_indicator"]
        if loading_selector:
            try:
                # Wait for loading indicator to appear (if it exists)
                scraper.wait_for_selector(loading_selector, timeout=2000)
                # Then wait for it to disappear
                scraper.wait_for_selector(loading_selector, state="hidden", timeout=self.scroll_config["load_timeout"] * 1000)
            except:
                # Loading indicator might not appear, that's okay
                pass
        
        # Additional wait for content to stabilize
        time.sleep(1)
    
    def _check_end_of_content(self, scraper: SyncGAScrap) -> bool:
        """Check if we've reached the end of content"""
        end_indicator = self.scroll_config["end_indicator"]
        if end_indicator:
            return bool(scraper.get_element(end_indicator))
        return False
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common popups that might interfere with scrolling"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close",
            ".newsletter-popup .close", ".gdpr-accept"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def scrape_paginated_content(self, base_url: str, item_selectors: Dict[str, str],
                                max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape paginated content (traditional pagination)
        
        Args:
            base_url: Base URL with {page} placeholder
            item_selectors: Selectors for extracting data from each item
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped items
        """
        all_items = []
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"📄 Starting paginated scraping (max {max_pages} pages)...", "info")
            
            for page in range(1, max_pages + 1):
                scraper.log(f"📄 Scraping page {page}/{max_pages}", "info")
                
                # Navigate to page
                if "{page}" in base_url:
                    url = base_url.format(page=page)
                else:
                    url = f"{base_url}?page={page}"
                
                scraper.goto(url)
                self._handle_popups(scraper)
                
                # Wait for content
                try:
                    scraper.wait_for_selector(self.scroll_config["content_selector"], timeout=10000)
                except:
                    scraper.log(f"⚠️ No content found on page {page}, stopping", "warning")
                    break
                
                # Extract items from current page
                page_items = self._extract_visible_items(scraper, item_selectors)
                
                if not page_items:
                    scraper.log(f"⚠️ No items found on page {page}, stopping", "warning")
                    break
                
                all_items.extend(page_items)
                scraper.log(f"📦 Found {len(page_items)} items on page {page}", "info")
                
                # Check if there's a next page
                if not self._has_next_page(scraper):
                    scraper.log("🏁 No more pages available", "info")
                    break
            
            scraper.log(f"✅ Pagination complete! Scraped {len(all_items)} items", "success")
            return all_items
    
    def _has_next_page(self, scraper: SyncGAScrap) -> bool:
        """Check if there's a next page available"""
        next_page_selectors = [
            ".pagination .next:not(.disabled)",
            ".pagination .next-page",
            ".pager .next",
            "a[aria-label='Next page']",
            ".next-page-link"
        ]
        
        for selector in next_page_selectors:
            if scraper.get_element(selector):
                return True
        
        return False
    
    def save_results(self, filename: str = None) -> str:
        """Save scraped results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infinite_scroll_results_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.scraped_items, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(self.scraped_items)} items to {filename}")
        return filename

# Example usage functions
def example_social_media_feed():
    """Example: Scrape social media infinite scroll feed"""
    print("📱 Social Media Feed Scraping")
    print("=" * 50)
    
    # Configure for social media scrolling
    scroll_config = {
        "scroll_method": "bottom",
        "scroll_pause": 3.0,  # Longer pause for social media
        "max_scrolls": 20,
        "duplicate_threshold": 5,
        "content_selector": ".post, .feed-item, .story",
        "loading_indicator": ".loading-spinner"
    }
    
    scraper = InfiniteScrollScraper(scroll_config)
    
    # Selectors for social media posts
    item_selectors = {
        "author": ".author-name, .username",
        "content": ".post-content, .post-text",
        "timestamp": ".timestamp, .post-time",
        "likes": ".like-count",
        "shares": ".share-count",
        "image": "img@src"
    }
    
    # Example URL (replace with actual social media URL)
    url = "https://example-social-media.com/feed"
    
    # Custom scroll handler for social media
    def social_media_scroll_handler(scraper, scroll_count):
        """Custom scrolling for social media that might have ads"""
        # Close any ads that might appear
        ad_selectors = [".ad-close", ".sponsored-close", ".promotion-close"]
        for selector in ad_selectors:
            scraper.click(selector)
        
        # Perform normal scroll
        scraper.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)  # Wait longer for social media content
        return True
    
    # Scrape feed
    items = scraper.scrape_infinite_scroll(url, item_selectors, social_media_scroll_handler)
    
    # Save results
    scraper.save_results("social_media_feed.json")
    
    print(f"\n📊 Results:")
    print(f"Total posts scraped: {len(items)}")
    if items:
        print(f"Sample post: {items[0].get('content', 'N/A')[:100]}...")

def example_ecommerce_products():
    """Example: Scrape e-commerce product listings with infinite scroll"""
    print("🛒 E-commerce Product Scraping")
    print("=" * 50)
    
    # Configure for e-commerce scrolling
    scroll_config = {
        "scroll_method": "bottom",
        "scroll_pause": 2.0,
        "max_scrolls": 15,
        "duplicate_threshold": 3,
        "content_selector": ".product-item, .product-card",
        "loading_indicator": ".products-loading",
        "end_indicator": ".no-more-products"
    }
    
    scraper = InfiniteScrollScraper(scroll_config)
    
    # Selectors for product data
    item_selectors = {
        "name": ".product-name, .product-title",
        "price": ".price, .product-price",
        "original_price": ".original-price, .was-price",
        "rating": ".rating, .stars",
        "image": ".product-image img@src",
        "link": "a@href",
        "availability": ".stock-status, .availability"
    }
    
    # Example e-commerce URL
    url = "https://example-store.com/products"
    
    # Scrape products
    items = scraper.scrape_infinite_scroll(url, item_selectors)
    
    # Save results
    scraper.save_results("ecommerce_products.json")
    
    print(f"\n📊 Results:")
    print(f"Total products scraped: {len(items)}")
    
    # Show price range
    prices = []
    for item in items:
        price_text = item.get("price", "")
        if price_text:
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                try:
                    prices.append(float(price_match.group().replace(',', '')))
                except:
                    pass
    
    if prices:
        print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")

def example_news_pagination():
    """Example: Scrape news articles with traditional pagination"""
    print("📰 News Articles Pagination Scraping")
    print("=" * 50)
    
    # Configure for news pagination
    scroll_config = {
        "content_selector": ".article, .news-item",
    }
    
    scraper = InfiniteScrollScraper(scroll_config)
    
    # Selectors for news articles
    item_selectors = {
        "headline": ".headline, .article-title",
        "summary": ".summary, .article-excerpt",
        "author": ".author, .byline",
        "date": ".date, .publish-date",
        "category": ".category, .section",
        "link": "a@href"
    }
    
    # Base URL with page placeholder
    base_url = "https://example-news.com/articles?page={page}"
    
    # Scrape paginated content
    items = scraper.scrape_paginated_content(base_url, item_selectors, max_pages=5)
    
    # Save results
    scraper.save_results("news_articles.json")
    
    print(f"\n📊 Results:")
    print(f"Total articles scraped: {len(items)}")
    if items:
        print(f"Sample headline: {items[0].get('headline', 'N/A')}")

def main():
    """Main function to demonstrate infinite scroll scraping"""
    print("🔄 GA-Scrap Infinite Scroll & Dynamic Content Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Social media feed (infinite scroll)")
    print("2. E-commerce products (infinite scroll)")
    print("3. News articles (pagination)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        example_social_media_feed()
    elif choice == "2":
        example_ecommerce_products()
    elif choice == "3":
        example_news_pagination()
    else:
        print("Invalid choice. Running social media example...")
        example_social_media_feed()

if __name__ == "__main__":
    main()
