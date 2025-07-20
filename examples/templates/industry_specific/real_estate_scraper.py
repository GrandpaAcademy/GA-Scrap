"""
Real Estate Scraper Template
Specialized template for scraping property listings from real estate websites
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class RealEstateScraper:
    """Specialized scraper for real estate listings"""
    
    def __init__(self, output_dir: str = "real_estate_data"):
        """Initialize real estate scraper"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.properties = []
        
    def scrape_property_listings(self, site_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape property listings from a real estate website
        
        Args:
            site_config: Configuration for the specific real estate site
            
        Returns:
            List of property listings
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🏠 Starting property scraping from {site_config.get('name', 'Unknown')}", "info")
            
            # Build search URL with filters
            search_url = self._build_property_search_url(site_config)
            scraper.goto(search_url)
            
            # Handle real estate site popups
            self._handle_real_estate_popups(scraper)
            
            # Apply search filters
            if "filters" in site_config:
                self._apply_property_filters(scraper, site_config["filters"])
            
            # Scrape listings with pagination
            page = 1
            max_pages = site_config.get("max_pages", 10)
            
            while page <= max_pages:
                scraper.log(f"📄 Scraping page {page}/{max_pages}", "info")
                
                # Wait for property listings to load
                property_selector = site_config["selectors"]["property_container"]
                scraper.wait_for_selector(property_selector, timeout=15000)
                
                # Extract properties from current page
                page_properties = self._extract_properties_from_page(scraper, site_config["selectors"])
                
                if not page_properties:
                    scraper.log("No properties found on this page, stopping", "warning")
                    break
                
                self.properties.extend(page_properties)
                scraper.log(f"🏠 Found {len(page_properties)} properties on page {page}", "info")
                
                # Go to next page
                if not self._go_to_next_page(scraper, site_config.get("pagination", {})):
                    scraper.log("No more pages available", "info")
                    break
                
                page += 1
            
            # Get detailed property information
            if site_config.get("extract_details", False):
                self._extract_property_details(scraper, site_config)
            
            scraper.log(f"✅ Property scraping complete! Found {len(self.properties)} properties", "success")
            return self.properties
    
    def _build_property_search_url(self, config: Dict[str, Any]) -> str:
        """Build property search URL with parameters"""
        base_url = config["base_url"]
        search_params = config.get("search_params", {})
        
        if not search_params:
            return base_url
        
        # Build query string for real estate search
        params = []
        for key, value in search_params.items():
            if value is not None:
                params.append(f"{key}={value}")
        
        query_string = "&".join(params)
        separator = "&" if "?" in base_url else "?"
        
        return f"{base_url}{separator}{query_string}"
    
    def _handle_real_estate_popups(self, scraper: SyncGAScrap):
        """Handle common real estate website popups"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close",
            ".newsletter-signup .close",
            ".agent-contact-popup .close",
            ".location-popup .close",
            ".mortgage-calculator-popup .close",
            ".gdpr-accept"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def _apply_property_filters(self, scraper: SyncGAScrap, filters: Dict[str, Any]):
        """Apply property search filters"""
        for filter_type, filter_config in filters.items():
            try:
                if filter_type == "price_range":
                    min_price = filter_config.get("min_selector", "input[name='min_price']")
                    max_price = filter_config.get("max_selector", "input[name='max_price']")
                    scraper.input(min_price, str(filter_config.get("min", "")))
                    scraper.input(max_price, str(filter_config.get("max", "")))
                
                elif filter_type == "bedrooms":
                    bed_selector = filter_config.get("selector", "select[name='bedrooms']")
                    scraper.select_option(bed_selector, str(filter_config["value"]))
                
                elif filter_type == "bathrooms":
                    bath_selector = filter_config.get("selector", "select[name='bathrooms']")
                    scraper.select_option(bath_selector, str(filter_config["value"]))
                
                elif filter_type == "property_type":
                    type_selector = filter_config.get("selector", "select[name='property_type']")
                    scraper.select_option(type_selector, filter_config["value"])
                
                elif filter_type == "square_footage":
                    min_sqft = filter_config.get("min_selector", "input[name='min_sqft']")
                    max_sqft = filter_config.get("max_selector", "input[name='max_sqft']")
                    scraper.input(min_sqft, str(filter_config.get("min", "")))
                    scraper.input(max_sqft, str(filter_config.get("max", "")))
                
                elif filter_type == "location":
                    location_input = filter_config.get("selector", "input[name='location']")
                    scraper.input(location_input, filter_config["value"])
                
            except Exception as e:
                scraper.log(f"⚠️ Could not apply filter {filter_type}: {e}", "warning")
        
        # Apply filters
        filter_button = filters.get("apply_button", "button[type='submit'], .search-button")
        scraper.click(filter_button)
        scraper.wait_for_load_state("networkidle")
    
    def _extract_properties_from_page(self, scraper: SyncGAScrap, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract property listings from current page"""
        properties = []
        
        # Get all property containers
        property_containers = scraper.get_all_elements(selectors["property_container"])
        
        for i in range(len(property_containers)):
            try:
                property_data = self._extract_single_property(scraper, i, selectors)
                if property_data:
                    properties.append(property_data)
            except Exception as e:
                scraper.log(f"⚠️ Error extracting property {i}: {e}", "warning")
                continue
        
        return properties
    
    def _extract_single_property(self, scraper: SyncGAScrap, index: int, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data from a single property listing"""
        base_selector = f"{selectors['property_container']}:nth-child({index + 1})"
        
        property_data = {
            "scraped_at": datetime.now().isoformat(),
            "property_index": index
        }
        
        # Extract property information
        field_mappings = {
            "address": "address",
            "price": "price",
            "bedrooms": "bedrooms",
            "bathrooms": "bathrooms",
            "square_footage": "square_feet",
            "property_type": "property_type",
            "listing_agent": "agent_name",
            "description": "description",
            "images": "image_urls",
            "link": "property_url"
        }
        
        for field, selector_key in field_mappings.items():
            if selector_key in selectors:
                try:
                    full_selector = f"{base_selector} {selectors[selector_key]}"
                    
                    if selector_key == "property_url":
                        # Extract URL from link
                        value = scraper.get_attribute(full_selector, "href")
                    elif selector_key == "image_urls":
                        # Extract multiple image URLs
                        value = scraper.get_all_attributes(full_selector, "src")
                    else:
                        # Extract text content
                        value = scraper.get_text(full_selector)
                    
                    property_data[field] = value
                    
                except Exception as e:
                    property_data[field] = None
        
        # Clean and enhance property data
        property_data = self._clean_property_data(property_data)
        
        # Only return property if we have essential information
        if property_data.get("address") and property_data.get("price"):
            return property_data
        
        return None
    
    def _clean_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize property data"""
        # Clean address
        if property_data.get("address"):
            property_data["address"] = property_data["address"].strip()
        
        # Parse price information
        if property_data.get("price"):
            price_info = self._parse_price(property_data["price"])
            property_data.update(price_info)
        
        # Parse bedrooms and bathrooms
        for field in ["bedrooms", "bathrooms"]:
            if property_data.get(field):
                parsed_value = self._parse_numeric_field(property_data[field])
                if parsed_value is not None:
                    property_data[f"{field}_numeric"] = parsed_value
        
        # Parse square footage
        if property_data.get("square_footage"):
            sqft_info = self._parse_square_footage(property_data["square_footage"])
            property_data.update(sqft_info)
        
        # Make property URL absolute
        if property_data.get("link") and not property_data["link"].startswith("http"):
            if property_data["link"].startswith("/"):
                property_data["link"] = f"https://example-realestate.com{property_data['link']}"
        
        # Process images
        if property_data.get("images"):
            property_data["image_count"] = len(property_data["images"])
            # Make image URLs absolute
            absolute_images = []
            for img_url in property_data["images"]:
                if img_url and not img_url.startswith("http"):
                    if img_url.startswith("/"):
                        img_url = f"https://example-realestate.com{img_url}"
                absolute_images.append(img_url)
            property_data["images"] = absolute_images
        
        return property_data
    
    def _parse_price(self, price_text: str) -> Dict[str, Any]:
        """Parse price information from text"""
        price_info = {"price_text": price_text}
        
        # Remove common price prefixes/suffixes
        clean_price = re.sub(r'[^\d,.]', '', price_text)
        clean_price = clean_price.replace(',', '')
        
        try:
            price_numeric = float(clean_price)
            price_info["price_numeric"] = price_numeric
            
            # Determine if it's rent or sale price
            price_lower = price_text.lower()
            if any(keyword in price_lower for keyword in ["rent", "/month", "/mo", "monthly"]):
                price_info["listing_type"] = "rent"
            else:
                price_info["listing_type"] = "sale"
            
        except ValueError:
            price_info["price_numeric"] = None
        
        return price_info
    
    def _parse_numeric_field(self, field_text: str) -> Optional[float]:
        """Parse numeric fields like bedrooms, bathrooms"""
        # Extract first number from text
        numbers = re.findall(r'\d+\.?\d*', field_text)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None
    
    def _parse_square_footage(self, sqft_text: str) -> Dict[str, Any]:
        """Parse square footage information"""
        sqft_info = {"square_footage_text": sqft_text}
        
        # Extract numeric value
        numbers = re.findall(r'[\d,]+', sqft_text.replace(',', ''))
        if numbers:
            try:
                sqft_info["square_footage_numeric"] = int(numbers[0])
            except ValueError:
                pass
        
        return sqft_info
    
    def _go_to_next_page(self, scraper: SyncGAScrap, pagination_config: Dict[str, Any]) -> bool:
        """Navigate to next page of results"""
        next_selectors = pagination_config.get("next_selectors", [
            ".pagination .next:not(.disabled)",
            ".pager .next",
            "a[aria-label='Next page']",
            ".next-page"
        ])
        
        for selector in next_selectors:
            if scraper.click(selector):
                scraper.wait_for_load_state("networkidle")
                return True
        
        return False
    
    def _extract_property_details(self, scraper: SyncGAScrap, config: Dict[str, Any]):
        """Extract detailed information for each property"""
        scraper.log("🔍 Extracting detailed property information...", "info")
        
        for i, property_data in enumerate(self.properties):
            if property_data.get("link"):
                try:
                    scraper.log(f"🏠 Getting details for property {i+1}/{len(self.properties)}", "info")
                    
                    # Navigate to property detail page
                    scraper.goto(property_data["link"])
                    
                    # Extract additional details
                    detail_selectors = config.get("detail_selectors", {})
                    for field, selector in detail_selectors.items():
                        try:
                            if field == "amenities":
                                # Extract list of amenities
                                amenities = scraper.get_all_text(selector)
                                property_data["amenities"] = amenities
                            elif field == "neighborhood_info":
                                # Extract neighborhood information
                                neighborhood = scraper.get_text(selector)
                                property_data["neighborhood"] = neighborhood
                            elif field == "school_ratings":
                                # Extract school information
                                schools = scraper.get_all_text(selector)
                                property_data["schools"] = schools
                            else:
                                value = scraper.get_text(selector)
                                property_data[f"detail_{field}"] = value
                        except:
                            property_data[f"detail_{field}"] = None
                    
                    # Brief pause between requests
                    scraper.wait(2000)
                    
                except Exception as e:
                    scraper.log(f"⚠️ Could not get details for property {i+1}: {e}", "warning")
    
    def save_properties(self, filename: str = None) -> str:
        """Save scraped properties to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"properties_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.properties, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(self.properties)} properties to {filepath}")
        return filepath
    
    def filter_properties(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter properties based on criteria"""
        filtered_properties = []
        
        for prop in self.properties:
            matches = True
            
            # Filter by price range
            if "max_price" in criteria and prop.get("price_numeric"):
                if prop["price_numeric"] > criteria["max_price"]:
                    matches = False
            
            if "min_price" in criteria and prop.get("price_numeric"):
                if prop["price_numeric"] < criteria["min_price"]:
                    matches = False
            
            # Filter by bedrooms
            if "min_bedrooms" in criteria and prop.get("bedrooms_numeric"):
                if prop["bedrooms_numeric"] < criteria["min_bedrooms"]:
                    matches = False
            
            # Filter by square footage
            if "min_sqft" in criteria and prop.get("square_footage_numeric"):
                if prop["square_footage_numeric"] < criteria["min_sqft"]:
                    matches = False
            
            # Filter by property type
            if "property_types" in criteria:
                prop_type = prop.get("property_type", "").lower()
                if not any(ptype.lower() in prop_type for ptype in criteria["property_types"]):
                    matches = False
            
            # Filter by location keywords
            if "location_keywords" in criteria:
                address = prop.get("address", "").lower()
                if not any(keyword.lower() in address for keyword in criteria["location_keywords"]):
                    matches = False
            
            if matches:
                filtered_properties.append(prop)
        
        return filtered_properties
    
    def generate_market_report(self) -> Dict[str, Any]:
        """Generate market analysis report from scraped data"""
        if not self.properties:
            return {"error": "No properties to analyze"}
        
        # Calculate price statistics
        prices = [p.get("price_numeric") for p in self.properties if p.get("price_numeric")]
        
        report = {
            "total_properties": len(self.properties),
            "properties_with_price": len(prices),
            "generated_at": datetime.now().isoformat()
        }
        
        if prices:
            report["price_stats"] = {
                "average_price": sum(prices) / len(prices),
                "median_price": sorted(prices)[len(prices) // 2],
                "min_price": min(prices),
                "max_price": max(prices)
            }
        
        # Property type distribution
        property_types = {}
        for prop in self.properties:
            prop_type = prop.get("property_type", "Unknown")
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        report["property_type_distribution"] = property_types
        
        # Bedroom distribution
        bedroom_counts = {}
        for prop in self.properties:
            bedrooms = prop.get("bedrooms_numeric", "Unknown")
            bedroom_counts[str(bedrooms)] = bedroom_counts.get(str(bedrooms), 0) + 1
        
        report["bedroom_distribution"] = bedroom_counts
        
        return report

# Example usage
def example_residential_properties():
    """Example: Scrape residential properties"""
    print("🏠 Residential Property Scraper Example")
    print("=" * 50)
    
    scraper = RealEstateScraper()
    
    # Configuration for a hypothetical real estate site
    site_config = {
        "name": "PropertyListings",
        "base_url": "https://example-realestate.com/search",
        "search_params": {
            "location": "San Francisco, CA",
            "property_type": "house"
        },
        "max_pages": 5,
        "selectors": {
            "property_container": ".property-listing",
            "address": ".property-address",
            "price": ".property-price",
            "bedrooms": ".bedrooms",
            "bathrooms": ".bathrooms",
            "square_feet": ".square-footage",
            "property_type": ".property-type",
            "property_url": "a.property-link@href",
            "image_urls": ".property-images img@src"
        },
        "filters": {
            "price_range": {
                "min": 500000,
                "max": 1500000
            },
            "bedrooms": {
                "value": "3+"
            }
        },
        "extract_details": True,
        "detail_selectors": {
            "amenities": ".amenities-list li",
            "neighborhood_info": ".neighborhood-description",
            "school_ratings": ".school-info .rating"
        }
    }
    
    # Scrape properties
    properties = scraper.scrape_property_listings(site_config)
    
    # Filter for specific criteria
    filtered_properties = scraper.filter_properties({
        "min_bedrooms": 3,
        "max_price": 1200000,
        "property_types": ["house", "townhouse"]
    })
    
    # Generate market report
    market_report = scraper.generate_market_report()
    
    # Save results
    scraper.save_properties()
    
    print(f"\n📊 Results:")
    print(f"Total properties found: {len(properties)}")
    print(f"Filtered properties: {len(filtered_properties)}")
    print(f"Average price: ${market_report.get('price_stats', {}).get('average_price', 0):,.0f}")
    
    # Show sample properties
    for prop in properties[:3]:
        print(f"\n🏠 {prop.get('address', 'N/A')}")
        print(f"💰 {prop.get('price', 'N/A')}")
        print(f"🛏️ {prop.get('bedrooms', 'N/A')} bed, {prop.get('bathrooms', 'N/A')} bath")
        print(f"📐 {prop.get('square_footage', 'N/A')} sq ft")

if __name__ == "__main__":
    example_residential_properties()
