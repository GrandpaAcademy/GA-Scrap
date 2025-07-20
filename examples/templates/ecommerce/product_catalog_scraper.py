"""
E-commerce Product Catalog Scraper Template
Demonstrates comprehensive product data extraction from e-commerce sites
"""

import asyncio
import sys
import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class ProductCatalogScraper:
    """Template for scraping product catalogs from e-commerce websites"""
    
    def __init__(self, base_url: str, output_format: str = "json"):
        """
        Initialize the product catalog scraper
        
        Args:
            base_url: Base URL of the e-commerce site
            output_format: Output format ('json', 'csv', 'both')
        """
        self.base_url = base_url
        self.output_format = output_format
        self.products = []
        
    def scrape_catalog(self, category_urls: List[str], max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape product catalog from multiple category pages
        
        Args:
            category_urls: List of category URLs to scrape
            max_pages: Maximum pages to scrape per category
            
        Returns:
            List of product dictionaries
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🛒 Starting product catalog scraping...", "info")
            
            for category_url in category_urls:
                scraper.log(f"📂 Scraping category: {category_url}", "info")
                self._scrape_category(scraper, category_url, max_pages)
            
            # Save results
            self._save_results()
            
            scraper.log(f"✅ Scraping complete! Found {len(self.products)} products", "success")
            return self.products
    
    def _scrape_category(self, scraper: SyncGAScrap, category_url: str, max_pages: int):
        """Scrape all pages in a category"""
        page = 1
        
        while page <= max_pages:
            scraper.log(f"📄 Scraping page {page}...", "info")
            
            # Navigate to category page
            page_url = f"{category_url}?page={page}" if page > 1 else category_url
            scraper.goto(page_url)
            
            # Handle common popups/overlays
            self._handle_popups(scraper)
            
            # Wait for products to load
            scraper.wait_for_selector(".product-item, .product-card, .product", timeout=10000)
            
            # Extract products from current page
            page_products = self._extract_products(scraper)
            
            if not page_products:
                scraper.log("No products found on this page, stopping category scraping", "warning")
                break
                
            self.products.extend(page_products)
            scraper.log(f"Found {len(page_products)} products on page {page}", "info")
            
            # Check if there's a next page
            if not self._has_next_page(scraper):
                scraper.log("No more pages in this category", "info")
                break
                
            page += 1
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common e-commerce popups and overlays"""
        popup_selectors = [
            ".cookie-banner .accept-button",
            ".cookie-consent button",
            ".newsletter-popup .close",
            ".modal-overlay .close",
            ".popup-close",
            "[data-testid='close-button']",
            ".age-verification .confirm",
            ".location-popup .close"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)  # Sandbox mode handles missing elements gracefully
    
    def _extract_products(self, scraper: SyncGAScrap) -> List[Dict[str, Any]]:
        """Extract product data from current page"""
        products = []
        
        # Common product container selectors
        product_selectors = [
            ".product-item",
            ".product-card", 
            ".product",
            "[data-testid='product']",
            ".grid-item"
        ]
        
        # Find product containers
        product_elements = None
        for selector in product_selectors:
            try:
                elements = scraper.get_all_elements(selector)
                if elements:
                    product_elements = elements
                    break
            except:
                continue
        
        if not product_elements:
            scraper.log("No product containers found", "warning")
            return products
        
        scraper.log(f"Found {len(product_elements)} product containers", "info")
        
        # Extract data from each product
        for i in range(len(product_elements)):
            try:
                product_data = self._extract_single_product(scraper, i)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                scraper.log(f"Error extracting product {i}: {e}", "warning")
                continue
        
        return products
    
    def _extract_single_product(self, scraper: SyncGAScrap, index: int) -> Dict[str, Any]:
        """Extract data from a single product"""
        # Common selectors for product data
        selectors = {
            "title": [
                f".product-item:nth-child({index + 1}) .product-title",
                f".product-item:nth-child({index + 1}) h2",
                f".product-item:nth-child({index + 1}) h3",
                f".product-item:nth-child({index + 1}) .title",
                f".product-card:nth-child({index + 1}) .product-name",
                f".product:nth-child({index + 1}) .name"
            ],
            "price": [
                f".product-item:nth-child({index + 1}) .price",
                f".product-item:nth-child({index + 1}) .product-price",
                f".product-card:nth-child({index + 1}) .price",
                f".product:nth-child({index + 1}) .price-current"
            ],
            "original_price": [
                f".product-item:nth-child({index + 1}) .original-price",
                f".product-item:nth-child({index + 1}) .price-old",
                f".product-card:nth-child({index + 1}) .was-price"
            ],
            "rating": [
                f".product-item:nth-child({index + 1}) .rating",
                f".product-item:nth-child({index + 1}) .stars",
                f".product-card:nth-child({index + 1}) .rating-value"
            ],
            "image": [
                f".product-item:nth-child({index + 1}) img",
                f".product-card:nth-child({index + 1}) .product-image img"
            ],
            "link": [
                f".product-item:nth-child({index + 1}) a",
                f".product-card:nth-child({index + 1}) .product-link"
            ]
        }
        
        product = {
            "scraped_at": datetime.now().isoformat(),
            "source_url": scraper.page.url
        }
        
        # Extract each field
        for field, field_selectors in selectors.items():
            value = None
            for selector in field_selectors:
                try:
                    if field == "image":
                        value = scraper.get_attribute(selector, "src")
                    elif field == "link":
                        value = scraper.get_attribute(selector, "href")
                    else:
                        value = scraper.get_text(selector)
                    
                    if value:
                        break
                except:
                    continue
            
            product[field] = value or ""
        
        # Clean and validate data
        product = self._clean_product_data(product)
        
        return product if product.get("title") else None
    
    def _clean_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize product data"""
        # Clean title
        if product.get("title"):
            product["title"] = product["title"].strip()
        
        # Clean and parse price
        if product.get("price"):
            price_text = product["price"].strip()
            # Extract numeric price (handles various formats)
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                try:
                    product["price_numeric"] = float(price_match.group().replace(',', ''))
                except:
                    product["price_numeric"] = None
        
        # Clean rating
        if product.get("rating"):
            rating_text = product["rating"].strip()
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                try:
                    product["rating_numeric"] = float(rating_match.group())
                except:
                    product["rating_numeric"] = None
        
        # Make image URL absolute
        if product.get("image") and not product["image"].startswith("http"):
            if product["image"].startswith("//"):
                product["image"] = "https:" + product["image"]
            elif product["image"].startswith("/"):
                product["image"] = self.base_url.rstrip("/") + product["image"]
        
        # Make product link absolute
        if product.get("link") and not product["link"].startswith("http"):
            if product["link"].startswith("/"):
                product["link"] = self.base_url.rstrip("/") + product["link"]
        
        return product
    
    def _has_next_page(self, scraper: SyncGAScrap) -> bool:
        """Check if there's a next page"""
        next_selectors = [
            ".pagination .next:not(.disabled)",
            ".pagination .next-page",
            ".pager .next",
            "[aria-label='Next page']",
            ".load-more"
        ]
        
        for selector in next_selectors:
            if scraper.get_element(selector):
                return True
        
        return False
    
    def _save_results(self):
        """Save scraped results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.output_format in ["json", "both"]:
            filename = f"products_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.products)} products to {filename}")
        
        if self.output_format in ["csv", "both"]:
            filename = f"products_{timestamp}.csv"
            if self.products:
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
                    writer.writeheader()
                    writer.writerows(self.products)
                print(f"💾 Saved {len(self.products)} products to {filename}")

# Example usage
def main():
    """Example usage of the product catalog scraper"""
    
    # Example: Scraping a demo e-commerce site
    scraper = ProductCatalogScraper(
        base_url="https://demo-store.com",
        output_format="both"
    )
    
    # Define categories to scrape
    categories = [
        "https://demo-store.com/electronics",
        "https://demo-store.com/clothing",
        "https://demo-store.com/books"
    ]
    
    # Scrape products
    products = scraper.scrape_catalog(categories, max_pages=3)
    
    # Display summary
    print(f"\n📊 Scraping Summary:")
    print(f"Total products: {len(products)}")
    
    if products:
        print(f"Sample product: {products[0]['title']}")
        print(f"Price range: ${min(p.get('price_numeric', 0) for p in products if p.get('price_numeric'))} - ${max(p.get('price_numeric', 0) for p in products if p.get('price_numeric'))}")

if __name__ == "__main__":
    main()
