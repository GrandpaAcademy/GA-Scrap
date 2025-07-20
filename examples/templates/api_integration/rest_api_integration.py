"""
REST API Integration Template
Demonstrates how to combine GA-Scrap with REST APIs for enhanced data processing
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class APIIntegratedScraper:
    """Template for scraping data and integrating with REST APIs"""
    
    def __init__(self, api_base_url: str, api_key: Optional[str] = None):
        """
        Initialize API integrated scraper
        
        Args:
            api_base_url: Base URL for the REST API
            api_key: Optional API key for authentication
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set up authentication headers
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
    
    def scrape_and_enrich_with_api(self, urls: List[str], selectors: Dict[str, str],
                                  api_enrichment_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape data and enrich it using API calls
        
        Args:
            urls: List of URLs to scrape
            selectors: Dictionary of field names and CSS selectors
            api_enrichment_config: Configuration for API enrichment
            
        Returns:
            List of enriched data items
        """
        enriched_data = []
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🔗 Starting API-integrated scraping...", "info")
            
            for i, url in enumerate(urls):
                try:
                    scraper.log(f"📄 Processing {i+1}/{len(urls)}: {url}", "info")
                    
                    # Scrape basic data
                    scraped_data = self._scrape_url(scraper, url, selectors)
                    
                    if scraped_data:
                        # Enrich with API data
                        enriched_item = self._enrich_with_api(scraped_data, api_enrichment_config)
                        enriched_data.append(enriched_item)
                        
                        scraper.log(f"✅ Enriched item {i+1}", "success")
                    else:
                        scraper.log(f"⚠️ No data extracted from {url}", "warning")
                        
                except Exception as e:
                    scraper.log(f"❌ Error processing {url}: {e}", "error")
        
        scraper.log(f"🎉 Completed! Processed {len(enriched_data)} items", "success")
        return enriched_data
    
    def _scrape_url(self, scraper: SyncGAScrap, url: str, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Scrape data from a single URL"""
        # Navigate to URL
        scraper.goto(url)
        
        # Handle popups
        popup_selectors = [
            ".cookie-accept", ".modal-close", ".popup-close"
        ]
        for selector in popup_selectors:
            scraper.click(selector)
        
        # Extract data
        data = {
            "source_url": url,
            "scraped_at": datetime.now().isoformat(),
            "page_title": scraper.get_text("title")
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
                scraper.log(f"⚠️ Could not extract {field_name}: {e}", "warning")
                data[field_name] = None
        
        # Return data if we extracted meaningful content
        meaningful_fields = [k for k, v in data.items() 
                           if v and k not in ["source_url", "scraped_at", "page_title"]]
        return data if meaningful_fields else None
    
    def _enrich_with_api(self, scraped_data: Dict[str, Any], 
                        enrichment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich scraped data with API calls"""
        enriched_data = scraped_data.copy()
        enriched_data["api_enrichments"] = {}
        
        for enrichment_name, config in enrichment_config.items():
            try:
                api_data = self._make_api_call(config, scraped_data)
                if api_data:
                    enriched_data["api_enrichments"][enrichment_name] = api_data
                    
                    # Merge specific fields if configured
                    if "merge_fields" in config:
                        for api_field, target_field in config["merge_fields"].items():
                            if api_field in api_data:
                                enriched_data[target_field] = api_data[api_field]
                
                # Rate limiting
                if "rate_limit_delay" in config:
                    time.sleep(config["rate_limit_delay"])
                    
            except Exception as e:
                print(f"⚠️ API enrichment failed for {enrichment_name}: {e}")
                enriched_data["api_enrichments"][enrichment_name] = {"error": str(e)}
        
        return enriched_data
    
    def _make_api_call(self, config: Dict[str, Any], scraped_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make an API call based on configuration"""
        endpoint = config["endpoint"]
        method = config.get("method", "GET").upper()
        
        # Build URL
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        
        # Prepare parameters/data
        params = {}
        data = {}
        
        if "params" in config:
            for param_name, param_config in config["params"].items():
                if isinstance(param_config, str):
                    # Direct value
                    params[param_name] = param_config
                elif isinstance(param_config, dict) and "from_scraped" in param_config:
                    # Value from scraped data
                    field_path = param_config["from_scraped"]
                    value = self._get_nested_value(scraped_data, field_path)
                    if value:
                        params[param_name] = value
        
        if "data" in config:
            for data_name, data_config in config["data"].items():
                if isinstance(data_config, str):
                    data[data_name] = data_config
                elif isinstance(data_config, dict) and "from_scraped" in data_config:
                    field_path = data_config["from_scraped"]
                    value = self._get_nested_value(scraped_data, field_path)
                    if value:
                        data[data_name] = value
        
        # Make API call
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, params=params, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            return None
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def scrape_with_real_time_api_validation(self, urls: List[str], selectors: Dict[str, str],
                                           validation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape data and validate it in real-time using API"""
        validated_data = []
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🔍 Starting real-time API validation scraping...", "info")
            
            for i, url in enumerate(urls):
                try:
                    # Scrape data
                    scraped_data = self._scrape_url(scraper, url, selectors)
                    
                    if scraped_data:
                        # Validate with API
                        validation_result = self._validate_with_api(scraped_data, validation_config)
                        
                        scraped_data["validation"] = validation_result
                        
                        # Only include if validation passes
                        if validation_result.get("is_valid", False):
                            validated_data.append(scraped_data)
                            scraper.log(f"✅ Item {i+1} validated and included", "success")
                        else:
                            scraper.log(f"❌ Item {i+1} failed validation", "warning")
                    
                except Exception as e:
                    scraper.log(f"❌ Error processing {url}: {e}", "error")
        
        return validated_data
    
    def _validate_with_api(self, scraped_data: Dict[str, Any], 
                          validation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scraped data using API"""
        try:
            api_data = self._make_api_call(validation_config, scraped_data)
            
            if api_data:
                # Check validation criteria
                validation_rules = validation_config.get("validation_rules", {})
                is_valid = True
                validation_details = {}
                
                for rule_name, rule_config in validation_rules.items():
                    rule_result = self._apply_validation_rule(api_data, rule_config)
                    validation_details[rule_name] = rule_result
                    
                    if not rule_result.get("passed", False):
                        is_valid = False
                
                return {
                    "is_valid": is_valid,
                    "api_response": api_data,
                    "validation_details": validation_details
                }
            else:
                return {
                    "is_valid": False,
                    "error": "API call failed"
                }
                
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }
    
    def _apply_validation_rule(self, api_data: Dict[str, Any], 
                              rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single validation rule"""
        rule_type = rule_config.get("type")
        field = rule_config.get("field")
        expected_value = rule_config.get("expected_value")
        
        if rule_type == "equals":
            actual_value = self._get_nested_value(api_data, field)
            passed = actual_value == expected_value
            return {
                "passed": passed,
                "actual_value": actual_value,
                "expected_value": expected_value
            }
        
        elif rule_type == "exists":
            actual_value = self._get_nested_value(api_data, field)
            passed = actual_value is not None
            return {
                "passed": passed,
                "field_exists": passed
            }
        
        elif rule_type == "range":
            actual_value = self._get_nested_value(api_data, field)
            min_val = rule_config.get("min")
            max_val = rule_config.get("max")
            
            try:
                actual_num = float(actual_value)
                passed = (min_val is None or actual_num >= min_val) and \
                        (max_val is None or actual_num <= max_val)
                return {
                    "passed": passed,
                    "actual_value": actual_num,
                    "min": min_val,
                    "max": max_val
                }
            except (ValueError, TypeError):
                return {
                    "passed": False,
                    "error": "Value is not numeric"
                }
        
        return {"passed": False, "error": "Unknown rule type"}

# Example usage functions
def example_news_sentiment_analysis():
    """Example: Scrape news and analyze sentiment using API"""
    print("📰 News Scraper with Sentiment Analysis API")
    print("=" * 50)
    
    # Initialize scraper with sentiment analysis API
    scraper = APIIntegratedScraper(
        api_base_url="https://api.textrazor.com",  # Example API
        api_key="your-api-key-here"
    )
    
    # URLs to scrape
    urls = [
        "https://news.ycombinator.com",
        "https://techcrunch.com"
    ]
    
    # Selectors for news data
    selectors = {
        "headline": "h1",
        "content": ".article-content",
        "author": ".author",
        "publish_date": ".publish-date"
    }
    
    # API enrichment configuration
    enrichment_config = {
        "sentiment_analysis": {
            "endpoint": "/v1/analyze",
            "method": "POST",
            "data": {
                "text": {"from_scraped": "content"},
                "extractors": "sentiment"
            },
            "merge_fields": {
                "sentiment": "sentiment_score",
                "confidence": "sentiment_confidence"
            },
            "rate_limit_delay": 1.0
        }
    }
    
    # Scrape and enrich
    enriched_articles = scraper.scrape_and_enrich_with_api(urls, selectors, enrichment_config)
    
    print(f"\n📊 Results: {len(enriched_articles)} articles analyzed")
    for article in enriched_articles[:3]:  # Show first 3
        print(f"Headline: {article.get('headline', 'N/A')}")
        print(f"Sentiment: {article.get('sentiment_score', 'N/A')}")
        print("-" * 30)

def example_product_price_validation():
    """Example: Scrape products and validate prices using API"""
    print("🛒 Product Scraper with Price Validation API")
    print("=" * 50)
    
    scraper = APIIntegratedScraper(
        api_base_url="https://api.pricevalidation.com",
        api_key="your-api-key"
    )
    
    # Product URLs
    urls = [
        "https://example-store.com/product/123",
        "https://example-store.com/product/456"
    ]
    
    # Product selectors
    selectors = {
        "name": "h1",
        "price": ".price",
        "sku": ".sku",
        "brand": ".brand"
    }
    
    # Validation configuration
    validation_config = {
        "endpoint": "/v1/validate-price",
        "method": "POST",
        "data": {
            "product_name": {"from_scraped": "name"},
            "price": {"from_scraped": "price"},
            "sku": {"from_scraped": "sku"}
        },
        "validation_rules": {
            "price_reasonable": {
                "type": "range",
                "field": "price_score",
                "min": 0.7,
                "max": 1.0
            },
            "product_exists": {
                "type": "exists",
                "field": "product_id"
            }
        }
    }
    
    # Scrape with validation
    validated_products = scraper.scrape_with_real_time_api_validation(
        urls, selectors, validation_config
    )
    
    print(f"\n📊 Results: {len(validated_products)} products validated")

def example_content_translation():
    """Example: Scrape content and translate using API"""
    print("🌐 Content Scraper with Translation API")
    print("=" * 50)
    
    scraper = APIIntegratedScraper(
        api_base_url="https://api.mymemory.translated.net",
        api_key=None  # Free API
    )
    
    urls = ["https://example-foreign-site.com"]
    
    selectors = {
        "title": "h1",
        "content": ".main-content"
    }
    
    # Translation enrichment
    enrichment_config = {
        "translation": {
            "endpoint": "/get",
            "method": "GET",
            "params": {
                "q": {"from_scraped": "content"},
                "langpair": "es|en"  # Spanish to English
            },
            "merge_fields": {
                "responseData.translatedText": "translated_content"
            }
        }
    }
    
    # Scrape and translate
    translated_content = scraper.scrape_and_enrich_with_api(urls, selectors, enrichment_config)
    
    print(f"\n📊 Results: {len(translated_content)} items translated")

def main():
    """Main function to demonstrate API integration"""
    print("🔗 GA-Scrap REST API Integration Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. News sentiment analysis")
    print("2. Product price validation")
    print("3. Content translation")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        example_news_sentiment_analysis()
    elif choice == "2":
        example_product_price_validation()
    elif choice == "3":
        example_content_translation()
    else:
        print("Invalid choice. Running sentiment analysis example...")
        example_news_sentiment_analysis()

if __name__ == "__main__":
    main()
