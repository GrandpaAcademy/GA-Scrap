"""
Webhook Integration Scraper Template
Demonstrates how to integrate GA-Scrap with webhooks for real-time data processing
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class WebhookScraper:
    """Template for scraping data and sending it via webhooks"""
    
    def __init__(self, webhook_url: str, webhook_secret: Optional[str] = None):
        """
        Initialize webhook scraper
        
        Args:
            webhook_url: URL to send webhook data to
            webhook_secret: Optional secret for webhook authentication
        """
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret
        self.scraped_data = []
        
    def scrape_and_send(self, urls: List[str], selectors: Dict[str, str], 
                       batch_size: int = 10) -> Dict[str, Any]:
        """
        Scrape data from URLs and send via webhook
        
        Args:
            urls: List of URLs to scrape
            selectors: Dictionary of field names and CSS selectors
            batch_size: Number of items to send per webhook call
            
        Returns:
            Summary of scraping and webhook results
        """
        results = {
            "total_urls": len(urls),
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "webhook_calls": 0,
            "webhook_failures": 0,
            "start_time": datetime.now().isoformat()
        }
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🕷️ Starting webhook scraper...", "info")
            
            batch_data = []
            
            for i, url in enumerate(urls):
                try:
                    scraper.log(f"📄 Scraping {i+1}/{len(urls)}: {url}", "info")
                    
                    # Navigate to URL
                    scraper.goto(url)
                    
                    # Handle common popups
                    self._handle_popups(scraper)
                    
                    # Extract data using provided selectors
                    scraped_item = self._extract_data(scraper, url, selectors)
                    
                    if scraped_item:
                        batch_data.append(scraped_item)
                        results["successful_scrapes"] += 1
                        
                        # Send batch when it reaches batch_size
                        if len(batch_data) >= batch_size:
                            webhook_success = self._send_webhook(batch_data)
                            if webhook_success:
                                results["webhook_calls"] += 1
                            else:
                                results["webhook_failures"] += 1
                            batch_data = []
                    else:
                        results["failed_scrapes"] += 1
                        
                except Exception as e:
                    scraper.log(f"❌ Error scraping {url}: {e}", "error")
                    results["failed_scrapes"] += 1
            
            # Send remaining data in final batch
            if batch_data:
                webhook_success = self._send_webhook(batch_data)
                if webhook_success:
                    results["webhook_calls"] += 1
                else:
                    results["webhook_failures"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        scraper.log(f"✅ Scraping complete! {results['successful_scrapes']} successful, {results['failed_scrapes']} failed", "success")
        
        return results
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common website popups"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close",
            ".newsletter-popup .close", ".age-verification button"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def _extract_data(self, scraper: SyncGAScrap, url: str, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data using provided selectors"""
        data = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "page_title": scraper.get_text("title")
        }
        
        # Extract data for each selector
        for field_name, selector in selectors.items():
            try:
                if selector.endswith("[]"):  # Multiple elements
                    selector = selector[:-2]
                    values = scraper.get_all_text(selector)
                    data[field_name] = values
                elif selector.startswith("@"):  # Attribute
                    attr_selector, attr_name = selector[1:].split("@")
                    value = scraper.get_attribute(attr_selector, attr_name)
                    data[field_name] = value
                else:  # Single element text
                    value = scraper.get_text(selector)
                    data[field_name] = value
                    
            except Exception as e:
                scraper.log(f"⚠️ Could not extract {field_name} using {selector}: {e}", "warning")
                data[field_name] = None
        
        # Only return data if we extracted something meaningful
        meaningful_fields = [k for k, v in data.items() if v and k not in ["url", "scraped_at", "page_title"]]
        return data if meaningful_fields else None
    
    def _send_webhook(self, data: List[Dict[str, Any]]) -> bool:
        """Send data via webhook"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "data_count": len(data),
                "data": data,
                "source": "ga-scrap-webhook-scraper"
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "GA-Scrap-Webhook-Scraper/1.0"
            }
            
            # Add webhook signature if secret is provided
            if self.webhook_secret:
                payload_json = json.dumps(payload, sort_keys=True)
                signature = hashlib.sha256(
                    (self.webhook_secret + payload_json).encode()
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Webhook sent successfully: {len(data)} items")
                return True
            else:
                print(f"❌ Webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return False
    
    def scrape_with_real_time_webhook(self, urls: List[str], selectors: Dict[str, str]) -> Dict[str, Any]:
        """Scrape and send each item immediately via webhook"""
        results = {
            "total_urls": len(urls),
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "webhook_calls": 0,
            "webhook_failures": 0,
            "start_time": datetime.now().isoformat()
        }
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🚀 Starting real-time webhook scraper...", "info")
            
            for i, url in enumerate(urls):
                try:
                    scraper.log(f"📄 Processing {i+1}/{len(urls)}: {url}", "info")
                    
                    # Navigate and extract
                    scraper.goto(url)
                    self._handle_popups(scraper)
                    scraped_item = self._extract_data(scraper, url, selectors)
                    
                    if scraped_item:
                        # Send immediately
                        webhook_success = self._send_webhook([scraped_item])
                        if webhook_success:
                            results["webhook_calls"] += 1
                            results["successful_scrapes"] += 1
                        else:
                            results["webhook_failures"] += 1
                            results["failed_scrapes"] += 1
                    else:
                        results["failed_scrapes"] += 1
                        
                except Exception as e:
                    scraper.log(f"❌ Error processing {url}: {e}", "error")
                    results["failed_scrapes"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        return results

class WebhookReceiver:
    """Simple webhook receiver for testing"""
    
    def __init__(self, port: int = 8080):
        """
        Initialize webhook receiver
        
        Args:
            port: Port to listen on
        """
        self.port = port
        self.received_data = []
    
    def start_server(self):
        """Start a simple webhook receiver server"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class WebhookHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                try:
                    data = json.loads(post_data.decode('utf-8'))
                    self.server.webhook_receiver.received_data.append({
                        "timestamp": datetime.now().isoformat(),
                        "data": data,
                        "headers": dict(self.headers)
                    })
                    
                    print(f"📨 Received webhook: {data.get('data_count', 0)} items")
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "success"}')
                    
                except Exception as e:
                    print(f"❌ Error processing webhook: {e}")
                    self.send_response(400)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress default logging
        
        server = HTTPServer(('localhost', self.port), WebhookHandler)
        server.webhook_receiver = self
        
        print(f"🎯 Webhook receiver started on http://localhost:{self.port}")
        print("Press Ctrl+C to stop")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopping webhook receiver...")
            server.shutdown()

# Example usage functions
def example_news_scraper():
    """Example: Scrape news articles and send via webhook"""
    print("📰 News Scraper with Webhook Integration")
    print("=" * 50)
    
    # Initialize webhook scraper
    webhook_url = "http://localhost:8080/webhook"  # Replace with your webhook URL
    scraper = WebhookScraper(webhook_url, webhook_secret="your-secret-key")
    
    # Define URLs to scrape
    news_urls = [
        "https://news.ycombinator.com",
        "https://techcrunch.com",
        "https://arstechnica.com"
    ]
    
    # Define what data to extract
    selectors = {
        "headlines": ".titleline > a[]",  # Multiple headlines
        "main_headline": "h1",           # Single main headline
        "description": "meta[name='description']@content",  # Meta description
        "links": "a[href*='article']@href[]"  # Article links
    }
    
    # Scrape and send via webhook
    results = scraper.scrape_and_send(news_urls, selectors, batch_size=5)
    
    print(f"\n📊 Results:")
    print(f"Successful scrapes: {results['successful_scrapes']}")
    print(f"Failed scrapes: {results['failed_scrapes']}")
    print(f"Webhook calls: {results['webhook_calls']}")
    print(f"Webhook failures: {results['webhook_failures']}")

def example_product_monitor():
    """Example: Monitor product prices and send alerts via webhook"""
    print("🛒 Product Price Monitor with Webhooks")
    print("=" * 50)
    
    webhook_url = "https://your-api.com/price-alerts"  # Replace with your webhook URL
    scraper = WebhookScraper(webhook_url)
    
    # Product URLs to monitor
    product_urls = [
        "https://example-store.com/product/123",
        "https://example-store.com/product/456"
    ]
    
    # Extract price and product info
    selectors = {
        "product_name": "h1",
        "current_price": ".price",
        "original_price": ".original-price",
        "availability": ".stock-status",
        "rating": ".rating"
    }
    
    # Use real-time webhook for immediate price alerts
    results = scraper.scrape_with_real_time_webhook(product_urls, selectors)
    
    print(f"\n📊 Monitoring Results:")
    print(f"Products checked: {results['total_urls']}")
    print(f"Alerts sent: {results['webhook_calls']}")

def test_webhook_receiver():
    """Test the webhook receiver"""
    print("🎯 Starting Webhook Receiver Test")
    print("=" * 50)
    
    receiver = WebhookReceiver(port=8080)
    receiver.start_server()

def main():
    """Main function to demonstrate webhook integration"""
    print("🔗 GA-Scrap Webhook Integration Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. News scraper with webhook")
    print("2. Product price monitor")
    print("3. Start webhook receiver (for testing)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        example_news_scraper()
    elif choice == "2":
        example_product_monitor()
    elif choice == "3":
        test_webhook_receiver()
    else:
        print("Invalid choice. Running news scraper example...")
        example_news_scraper()

if __name__ == "__main__":
    main()
