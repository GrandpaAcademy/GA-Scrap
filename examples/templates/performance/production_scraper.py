"""
Production-Ready Scraper Template
Demonstrates robust scraping patterns with error handling, retry mechanisms, and monitoring
"""

import asyncio
import sys
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
import random
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class ScrapingStatus(Enum):
    """Enumeration for scraping status"""
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"

@dataclass
class ScrapingResult:
    """Data class for scraping results"""
    url: str
    status: ScrapingStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 1
    duration: float = 0.0
    timestamp: str = ""

class ProductionScraper:
    """Production-ready scraper with comprehensive error handling and monitoring"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize production scraper
        
        Args:
            config: Configuration dictionary for scraper settings
        """
        self.config = config or self._get_default_config()
        self.results = []
        self.stats = {
            "total_urls": 0,
            "successful": 0,
            "failed": 0,
            "retried": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None
        }
        
        # Setup logging
        self._setup_logging()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "max_retries": 3,
            "retry_delay": 2.0,
            "retry_backoff": 2.0,
            "request_delay": 1.0,
            "timeout": 30000,
            "user_agent_rotation": True,
            "proxy_rotation": False,
            "concurrent_limit": 1,
            "error_threshold": 0.1,  # Stop if error rate exceeds 10%
            "save_screenshots_on_error": True,
            "save_html_on_error": True,
            "log_level": "INFO",
            "output_dir": "scraping_output"
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config["log_level"].upper())
        
        # Create output directory
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("ProductionScraper")
        self.logger.setLevel(log_level)
        
        # File handler
        log_file = os.path.join(self.config["output_dir"], f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def scrape_urls(self, urls: List[str], selectors: Dict[str, str],
                   custom_handler: Optional[Callable] = None) -> List[ScrapingResult]:
        """
        Scrape multiple URLs with production-ready error handling
        
        Args:
            urls: List of URLs to scrape
            selectors: Dictionary of field names and CSS selectors
            custom_handler: Optional custom handler for data processing
            
        Returns:
            List of scraping results
        """
        self.stats["total_urls"] = len(urls)
        self.stats["start_time"] = datetime.now()
        
        self.logger.info(f"Starting production scraping of {len(urls)} URLs")
        
        with SyncGAScrap(
            headless=True,  # Production mode - headless
            sandbox_mode=True,  # Error resilient
            debug=False,  # Reduce noise in production
            timeout=self.config["timeout"]
        ) as scraper:
            
            for i, url in enumerate(urls):
                # Check error threshold
                if self._should_stop_due_to_errors():
                    self.logger.warning("Stopping scraping due to high error rate")
                    break
                
                self.logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
                
                # Scrape single URL with retries
                result = self._scrape_single_url_with_retries(scraper, url, selectors, custom_handler)
                self.results.append(result)
                
                # Update statistics
                self._update_stats(result)
                
                # Rate limiting
                if i < len(urls) - 1:  # Don't delay after last URL
                    delay = self._calculate_delay()
                    if delay > 0:
                        self.logger.debug(f"Waiting {delay:.2f} seconds before next request")
                        time.sleep(delay)
        
        self.stats["end_time"] = datetime.now()
        self._log_final_stats()
        self._save_results()
        
        return self.results
    
    def _scrape_single_url_with_retries(self, scraper: SyncGAScrap, url: str,
                                       selectors: Dict[str, str],
                                       custom_handler: Optional[Callable]) -> ScrapingResult:
        """Scrape a single URL with retry mechanism"""
        max_retries = self.config["max_retries"]
        retry_delay = self.config["retry_delay"]
        retry_backoff = self.config["retry_backoff"]
        
        for attempt in range(max_retries + 1):
            start_time = time.time()
            
            try:
                self.logger.debug(f"Attempt {attempt + 1} for {url}")
                
                # Navigate to URL
                scraper.goto(url)
                
                # Handle common issues
                self._handle_common_issues(scraper)
                
                # Extract data
                data = self._extract_data(scraper, url, selectors)
                
                # Apply custom handler if provided
                if custom_handler:
                    data = custom_handler(data, scraper)
                
                duration = time.time() - start_time
                
                result = ScrapingResult(
                    url=url,
                    status=ScrapingStatus.SUCCESS,
                    data=data,
                    attempts=attempt + 1,
                    duration=duration,
                    timestamp=datetime.now().isoformat()
                )
                
                self.logger.info(f"Successfully scraped {url} in {duration:.2f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {error_msg}")
                
                # Save error artifacts
                if self.config["save_screenshots_on_error"]:
                    self._save_error_screenshot(scraper, url, attempt)
                
                if self.config["save_html_on_error"]:
                    self._save_error_html(scraper, url, attempt)
                
                # If this was the last attempt, return failure
                if attempt == max_retries:
                    result = ScrapingResult(
                        url=url,
                        status=ScrapingStatus.FAILED,
                        error=error_msg,
                        attempts=attempt + 1,
                        duration=duration,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    self.logger.error(f"Failed to scrape {url} after {attempt + 1} attempts")
                    return result
                
                # Wait before retry with exponential backoff
                wait_time = retry_delay * (retry_backoff ** attempt)
                self.logger.debug(f"Waiting {wait_time:.2f}s before retry")
                time.sleep(wait_time)
        
        # This should never be reached, but just in case
        return ScrapingResult(
            url=url,
            status=ScrapingStatus.FAILED,
            error="Unknown error",
            attempts=max_retries + 1,
            timestamp=datetime.now().isoformat()
        )
    
    def _handle_common_issues(self, scraper: SyncGAScrap):
        """Handle common website issues"""
        # Handle popups
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close",
            ".newsletter-popup .close", ".gdpr-accept"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
        
        # Handle rate limiting indicators
        rate_limit_indicators = [
            ".rate-limit", ".too-many-requests", ".please-wait"
        ]
        
        for indicator in rate_limit_indicators:
            if scraper.get_element(indicator):
                self.logger.warning("Rate limiting detected, waiting longer")
                time.sleep(10)
                break
        
        # Handle CAPTCHA
        captcha_indicators = [
            ".captcha", ".recaptcha", ".hcaptcha"
        ]
        
        for indicator in captcha_indicators:
            if scraper.get_element(indicator):
                self.logger.warning("CAPTCHA detected - may need manual intervention")
                break
    
    def _extract_data(self, scraper: SyncGAScrap, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using provided selectors"""
        data = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "page_title": scraper.get_text("title") or "",
            "page_load_time": scraper.page.evaluate("performance.timing.loadEventEnd - performance.timing.navigationStart")
        }
        
        # Extract fields using selectors
        for field_name, selector in selectors.items():
            try:
                if selector.endswith("[]"):
                    # Multiple elements
                    selector = selector[:-2]
                    values = scraper.get_all_text(selector)
                    data[field_name] = values
                elif selector.startswith("@"):
                    # Attribute extraction
                    attr_selector, attr_name = selector[1:].split("@")
                    value = scraper.get_attribute(attr_selector, attr_name)
                    data[field_name] = value
                else:
                    # Single element text
                    value = scraper.get_text(selector)
                    data[field_name] = value
                    
            except Exception as e:
                self.logger.warning(f"Could not extract {field_name} from {url}: {e}")
                data[field_name] = None
        
        return data
    
    def _save_error_screenshot(self, scraper: SyncGAScrap, url: str, attempt: int):
        """Save screenshot on error"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_{timestamp}_{attempt}_{url.replace('/', '_').replace(':', '')[:50]}.png"
            filepath = os.path.join(self.config["output_dir"], filename)
            scraper.screenshot(filepath)
            self.logger.debug(f"Error screenshot saved: {filepath}")
        except Exception as e:
            self.logger.warning(f"Could not save error screenshot: {e}")
    
    def _save_error_html(self, scraper: SyncGAScrap, url: str, attempt: int):
        """Save HTML content on error"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_{timestamp}_{attempt}_{url.replace('/', '_').replace(':', '')[:50]}.html"
            filepath = os.path.join(self.config["output_dir"], filename)
            
            html_content = scraper.page.content()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            self.logger.debug(f"Error HTML saved: {filepath}")
        except Exception as e:
            self.logger.warning(f"Could not save error HTML: {e}")
    
    def _calculate_delay(self) -> float:
        """Calculate delay between requests"""
        base_delay = self.config["request_delay"]
        
        # Add random jitter to avoid being detected as bot
        jitter = random.uniform(0.5, 1.5)
        
        return base_delay * jitter
    
    def _should_stop_due_to_errors(self) -> bool:
        """Check if scraping should stop due to high error rate"""
        if len(self.results) < 10:  # Need minimum sample size
            return False
        
        error_rate = self.stats["failed"] / len(self.results)
        threshold = self.config["error_threshold"]
        
        return error_rate > threshold
    
    def _update_stats(self, result: ScrapingResult):
        """Update scraping statistics"""
        if result.status == ScrapingStatus.SUCCESS:
            self.stats["successful"] += 1
        elif result.status == ScrapingStatus.FAILED:
            self.stats["failed"] += 1
        elif result.status == ScrapingStatus.RETRY:
            self.stats["retried"] += 1
        elif result.status == ScrapingStatus.SKIPPED:
            self.stats["skipped"] += 1
    
    def _log_final_stats(self):
        """Log final scraping statistics"""
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        self.logger.info("=" * 50)
        self.logger.info("SCRAPING COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f"Total URLs: {self.stats['total_urls']}")
        self.logger.info(f"Successful: {self.stats['successful']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Success Rate: {(self.stats['successful'] / self.stats['total_urls'] * 100):.1f}%")
        self.logger.info(f"Total Duration: {duration}")
        self.logger.info(f"Average Time per URL: {duration.total_seconds() / self.stats['total_urls']:.2f}s")
        
        # Calculate average attempts
        total_attempts = sum(result.attempts for result in self.results)
        avg_attempts = total_attempts / len(self.results) if self.results else 0
        self.logger.info(f"Average Attempts per URL: {avg_attempts:.1f}")
    
    def _save_results(self):
        """Save scraping results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = os.path.join(self.config["output_dir"], f"results_{timestamp}.json")
        results_data = {
            "stats": self.stats,
            "config": self.config,
            "results": [
                {
                    "url": r.url,
                    "status": r.status.value,
                    "data": r.data,
                    "error": r.error,
                    "attempts": r.attempts,
                    "duration": r.duration,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }
        
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Results saved to: {results_file}")
        
        # Save successful data only
        successful_data = [r.data for r in self.results if r.status == ScrapingStatus.SUCCESS and r.data]
        if successful_data:
            data_file = os.path.join(self.config["output_dir"], f"data_{timestamp}.json")
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(successful_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Successful data saved to: {data_file}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.results:
            return {"error": "No results available"}
        
        successful_results = [r for r in self.results if r.status == ScrapingStatus.SUCCESS]
        failed_results = [r for r in self.results if r.status == ScrapingStatus.FAILED]
        
        # Calculate performance metrics
        durations = [r.duration for r in successful_results]
        attempts = [r.attempts for r in self.results]
        
        report = {
            "summary": {
                "total_urls": len(self.results),
                "successful": len(successful_results),
                "failed": len(failed_results),
                "success_rate": len(successful_results) / len(self.results) * 100
            },
            "performance": {
                "avg_duration": sum(durations) / len(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "avg_attempts": sum(attempts) / len(attempts) if attempts else 0
            },
            "errors": {
                "error_rate": len(failed_results) / len(self.results) * 100,
                "common_errors": self._get_common_errors(failed_results)
            }
        }
        
        return report
    
    def _get_common_errors(self, failed_results: List[ScrapingResult]) -> Dict[str, int]:
        """Get most common error types"""
        error_counts = {}
        
        for result in failed_results:
            if result.error:
                # Simplify error message to get error type
                error_type = result.error.split(":")[0] if ":" in result.error else result.error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Sort by frequency
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# Example usage functions
def example_news_scraping():
    """Example: Production news scraping"""
    print("📰 Production News Scraping")
    print("=" * 50)
    
    # Configuration for production scraping
    config = {
        "max_retries": 3,
        "retry_delay": 2.0,
        "request_delay": 1.5,
        "timeout": 30000,
        "error_threshold": 0.15,
        "save_screenshots_on_error": True,
        "log_level": "INFO"
    }
    
    scraper = ProductionScraper(config)
    
    # URLs to scrape
    urls = [
        "https://news.ycombinator.com",
        "https://techcrunch.com",
        "https://arstechnica.com",
        "https://invalid-url-for-testing.com"  # This will fail
    ]
    
    # Selectors for news data
    selectors = {
        "headlines": ".titleline > a[]",
        "main_headline": "h1",
        "description": "meta[name='description']@content"
    }
    
    # Custom data handler
    def news_handler(data, scraper):
        """Custom handler to process news data"""
        if data.get("headlines"):
            data["headline_count"] = len(data["headlines"])
            data["top_headline"] = data["headlines"][0] if data["headlines"] else None
        return data
    
    # Scrape with production settings
    results = scraper.scrape_urls(urls, selectors, news_handler)
    
    # Generate performance report
    report = scraper.get_performance_report()
    
    print(f"\n📊 Performance Report:")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Average Duration: {report['performance']['avg_duration']:.2f}s")
    print(f"Average Attempts: {report['performance']['avg_attempts']:.1f}")

def example_ecommerce_monitoring():
    """Example: E-commerce product monitoring"""
    print("🛒 Production E-commerce Monitoring")
    print("=" * 50)
    
    # High-reliability configuration
    config = {
        "max_retries": 5,
        "retry_delay": 3.0,
        "retry_backoff": 1.5,
        "request_delay": 2.0,
        "timeout": 45000,
        "error_threshold": 0.05,  # Very low tolerance for errors
        "save_screenshots_on_error": True,
        "save_html_on_error": True,
        "log_level": "DEBUG"
    }
    
    scraper = ProductionScraper(config)
    
    # Product URLs to monitor
    urls = [
        "https://example-store.com/product/123",
        "https://example-store.com/product/456",
        "https://example-store.com/product/789"
    ]
    
    # Product data selectors
    selectors = {
        "name": "h1",
        "price": ".price",
        "availability": ".stock-status",
        "rating": ".rating",
        "reviews_count": ".reviews-count"
    }
    
    # Custom handler for price monitoring
    def price_monitor_handler(data, scraper):
        """Custom handler for price monitoring"""
        if data.get("price"):
            # Extract numeric price
            import re
            price_text = data["price"]
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                try:
                    data["price_numeric"] = float(price_match.group().replace(',', ''))
                except:
                    data["price_numeric"] = None
        
        # Check availability
        if data.get("availability"):
            availability_text = data["availability"].lower()
            data["in_stock"] = "in stock" in availability_text or "available" in availability_text
        
        return data
    
    # Monitor products
    results = scraper.scrape_urls(urls, selectors, price_monitor_handler)
    
    # Show monitoring results
    successful_products = [r for r in results if r.status == ScrapingStatus.SUCCESS]
    print(f"\n📦 Monitored {len(successful_products)} products successfully")
    
    for result in successful_products:
        if result.data:
            print(f"Product: {result.data.get('name', 'Unknown')}")
            print(f"Price: {result.data.get('price', 'N/A')}")
            print(f"In Stock: {result.data.get('in_stock', 'Unknown')}")
            print("-" * 30)

def main():
    """Main function to demonstrate production scraping"""
    print("🏭 GA-Scrap Production Scraping Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Production news scraping")
    print("2. E-commerce product monitoring")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_news_scraping()
    elif choice == "2":
        example_ecommerce_monitoring()
    else:
        print("Invalid choice. Running news scraping example...")
        example_news_scraping()

if __name__ == "__main__":
    main()
