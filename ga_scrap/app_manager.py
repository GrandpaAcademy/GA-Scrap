"""
GA-Scrap App Manager
System for creating and managing multiple scraper apps
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from colorama import Fore, Style

class AppManager:
    """
    Manages multiple scraper applications
    
    Features:
    - Create new scraper apps from templates
    - List and manage existing apps
    - App configuration management
    - Template system for quick setup
    """
    
    def __init__(self, workspace_dir: str = "ga_scrap_apps"):
        """
        Initialize App Manager
        
        Args:
            workspace_dir: Directory to store all scraper apps
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.apps_config_file = self.workspace_dir / "apps.json"
        self.templates_dir = Path(__file__).parent / "templates"
        
        # Load or create apps configuration
        self.apps_config = self._load_apps_config()
    
    def _load_apps_config(self) -> Dict:
        """Load apps configuration from file"""
        if self.apps_config_file.exists():
            try:
                with open(self.apps_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not load apps config: {e}{Style.RESET_ALL}")
        
        return {"apps": {}, "created_at": datetime.now().isoformat()}
    
    def _save_apps_config(self):
        """Save apps configuration to file"""
        try:
            with open(self.apps_config_file, 'w') as f:
                json.dump(self.apps_config, f, indent=2)
        except Exception as e:
            print(f"{Fore.RED}Error: Could not save apps config: {e}{Style.RESET_ALL}")
    
    def create_app(
        self,
        app_name: str,
        template: str = "basic",
        description: str = "",
        overwrite: bool = False
    ) -> bool:
        """
        Create a new scraper app
        
        Args:
            app_name: Name of the app
            template: Template to use ('basic', 'advanced', 'ecommerce', 'social')
            description: App description
            overwrite: Whether to overwrite existing app
            
        Returns:
            True if app was created successfully
        """
        app_dir = self.workspace_dir / app_name
        
        # Check if app already exists
        if app_dir.exists() and not overwrite:
            print(f"{Fore.YELLOW}App '{app_name}' already exists. Use --overwrite to replace it.{Style.RESET_ALL}")
            return False
        
        try:
            # Remove existing app if overwriting
            if app_dir.exists() and overwrite:
                shutil.rmtree(app_dir)
            
            # Create app directory
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Create app structure based on template
            self._create_app_from_template(app_dir, template, app_name)
            
            # Update apps configuration
            self.apps_config["apps"][app_name] = {
                "name": app_name,
                "description": description,
                "template": template,
                "created_at": datetime.now().isoformat(),
                "path": str(app_dir),
                "status": "created"
            }
            self._save_apps_config()
            
            print(f"{Fore.GREEN}✅ App '{app_name}' created successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📁 Location: {app_dir}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🚀 Run: cd {app_dir} && python main.py{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to create app '{app_name}': {e}{Style.RESET_ALL}")
            return False
    
    def _create_app_from_template(self, app_dir: Path, template: str, app_name: str):
        """Create app files from template"""
        
        # Basic template structure
        templates = {
            "basic": self._create_basic_template,
            "advanced": self._create_advanced_template,
            "ecommerce": self._create_ecommerce_template,
            "social": self._create_social_template
        }
        
        if template not in templates:
            template = "basic"
            print(f"{Fore.YELLOW}Unknown template, using 'basic' template{Style.RESET_ALL}")
        
        templates[template](app_dir, app_name)
    
    def _create_basic_template(self, app_dir: Path, app_name: str):
        """Create basic scraper template"""
        
        # Main script
        main_py = f'''"""
{app_name} - GA-Scrap Application
Super simple web scraper template
"""

import asyncio
import sys
import os

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ga_scrap import SimpleScraper

async def main():
    """Main scraper function - Super Easy!"""

    # Use SimpleScraper for the easiest experience
    async with SimpleScraper() as scraper:

        # Navigate to a website
        await scraper.go("https://quotes.toscrape.com")

        # Get page title (super easy!)
        title = await scraper.get("title")
        scraper.log(f"Page title: {{title}}")

        # Get the first quote
        first_quote = await scraper.get(".quote .text")
        scraper.log(f"First quote: {{first_quote}}")

        # Get all quotes (even easier!)
        all_quotes = await scraper.get_all(".quote .text")
        scraper.log(f"Found {{len(all_quotes)}} quotes")

        # Show first few quotes
        for i, quote in enumerate(all_quotes[:3], 1):
            scraper.log(f"Quote {{i}}: {{quote[:50]}}...")

        # Get all authors
        authors = await scraper.get_all(".quote .author")
        scraper.log(f"Found {{len(authors)}} authors")

        # Take a screenshot
        await scraper.screenshot("my_scraper_screenshot.png")

        # Pause to see the browser in action
        await scraper.pause("Scraping complete! Check the browser. Press Enter to finish...")

# Alternative: Even simpler one-liner examples
async def one_liner_examples():
    """Examples of one-liner scraping"""
    from ga_scrap import scrape, scrape_all, scrape_data

    # Get page title in one line
    title = await scrape("https://example.com", "h1")
    print(f"Title: {{title}}")

    # Get all quotes in one line
    quotes = await scrape_all("https://quotes.toscrape.com", ".quote .text")
    print(f"Found {{len(quotes)}} quotes")

    # Get structured data in one line
    data = await scrape_data("https://quotes.toscrape.com", {{
        "title": "title",
        "quotes": ".quote .text[]",  # [] means get all
        "authors": ".quote .author[]"
    }})
    print(f"Data: {{data}}")

if __name__ == "__main__":
    # Run the main scraper
    asyncio.run(main())

    # Uncomment to try one-liner examples
    # asyncio.run(one_liner_examples())
'''
        
        # Configuration file
        config_yaml = f'''# {app_name} Configuration
app:
  name: "{app_name}"
  version: "1.0.0"
  description: "Basic web scraper"

browser:
  headless: false
  browser_type: "chromium"
  viewport:
    width: 1920
    height: 1080
  timeout: 30000

scraping:
  delay_between_requests: 1000
  max_retries: 3
  
targets:
  - name: "example"
    url: "https://example.com"
    selectors:
      title: "h1"
      links: "a"
'''
        
        # README
        readme_md = f'''# {app_name}

A web scraper built with GA-Scrap.

## Setup

1. Make sure GA-Scrap is installed in the parent directory
2. Run the scraper:
   ```bash
   python main.py
   ```

## Configuration

Edit `config.yaml` to customize the scraper behavior.

## Features

- Visible browser by default (headful mode)
- Easy configuration
- Built-in logging and error handling
- Hot reload support (when using GA-Scrap CLI)

## Usage

The scraper will:
1. Open a visible browser window
2. Navigate to the target website
3. Extract data based on your configuration
4. Display results in the console

## Customization

Edit `main.py` to add your specific scraping logic.
'''
        
        # Write files
        (app_dir / "main.py").write_text(main_py)
        (app_dir / "config.yaml").write_text(config_yaml)
        (app_dir / "README.md").write_text(readme_md)
        (app_dir / "__init__.py").write_text("")
    
    def _create_advanced_template(self, app_dir: Path, app_name: str):
        """Create advanced scraper template with multiple pages and data export"""
        self._create_basic_template(app_dir, app_name)
        
        # Add advanced features
        advanced_py = '''"""
Advanced scraping utilities
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any

class DataExporter:
    """Export scraped data to various formats"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def to_json(self, data: List[Dict[Any, Any]], filename: str):
        """Export data to JSON"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data exported to {filepath}")
    
    def to_csv(self, data: List[Dict[Any, Any]], filename: str):
        """Export data to CSV"""
        if not data:
            return
        
        filepath = self.output_dir / f"{filename}.csv"
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data exported to {filepath}")

class ScrapingUtils:
    """Utility functions for scraping"""
    
    @staticmethod
    async def wait_for_element(page, selector: str, timeout: int = 10000):
        """Wait for element to appear"""
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    @staticmethod
    async def extract_table_data(page, table_selector: str) -> List[Dict[str, str]]:
        """Extract data from HTML table"""
        rows = await page.query_selector_all(f"{table_selector} tr")
        if not rows:
            return []
        
        # Get headers
        header_cells = await rows[0].query_selector_all("th, td")
        headers = []
        for cell in header_cells:
            text = await cell.inner_text()
            headers.append(text.strip())
        
        # Get data rows
        data = []
        for row in rows[1:]:
            cells = await row.query_selector_all("td")
            if len(cells) == len(headers):
                row_data = {}
                for i, cell in enumerate(cells):
                    text = await cell.inner_text()
                    row_data[headers[i]] = text.strip()
                data.append(row_data)
        
        return data
'''
        
        (app_dir / "utils.py").write_text(advanced_py)
    
    def _create_ecommerce_template(self, app_dir: Path, app_name: str):
        """Create e-commerce scraper template"""
        self._create_advanced_template(app_dir, app_name)
        
        ecommerce_py = '''"""
E-commerce specific scraping functions
"""

async def scrape_product_details(scraper, product_url: str) -> dict:
    """Scrape product details from e-commerce site"""
    
    await scraper.goto(product_url)
    
    # Common e-commerce selectors (customize for specific sites)
    selectors = {
        'title': 'h1, .product-title, [data-testid="product-title"]',
        'price': '.price, .product-price, [data-testid="price"]',
        'description': '.description, .product-description',
        'images': 'img[src*="product"], .product-image img',
        'rating': '.rating, .stars, [data-testid="rating"]',
        'availability': '.availability, .stock, [data-testid="availability"]'
    }
    
    product_data = {}
    
    for field, selector in selectors.items():
        try:
            if field == 'images':
                elements = await scraper.page.query_selector_all(selector)
                urls = []
                for img in elements[:5]:  # Limit to 5 images
                    src = await img.get_attribute('src')
                    if src:
                        urls.append(src)
                product_data[field] = urls
            else:
                element = await scraper.page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    product_data[field] = text.strip()
        except Exception as e:
            scraper.log(f"Could not extract {field}: {e}", "warning")
    
    return product_data

async def scrape_product_list(scraper, category_url: str, max_products: int = 50) -> list:
    """Scrape list of products from category page"""
    
    await scraper.goto(category_url)
    
    products = []
    product_links = await scraper.page.query_selector_all('a[href*="product"], .product-link')
    
    for i, link in enumerate(product_links[:max_products]):
        try:
            href = await link.get_attribute('href')
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    base_url = scraper.page.url.split('/')[0:3]
                    href = '/'.join(base_url) + href
                
                scraper.log(f"Scraping product {i+1}/{min(len(product_links), max_products)}", "info")
                product_data = await scrape_product_details(scraper, href)
                product_data['url'] = href
                products.append(product_data)
                
                # Small delay between requests
                await scraper.page.wait_for_timeout(1000)
                
        except Exception as e:
            scraper.log(f"Error scraping product {i+1}: {e}", "error")
    
    return products
'''
        
        (app_dir / "ecommerce.py").write_text(ecommerce_py)
    
    def _create_social_template(self, app_dir: Path, app_name: str):
        """Create social media scraper template"""
        self._create_advanced_template(app_dir, app_name)
        
        social_py = '''"""
Social media scraping utilities
Note: Always respect robots.txt and terms of service
"""

async def scrape_social_posts(scraper, profile_url: str, max_posts: int = 20) -> list:
    """
    Generic social media post scraper
    Customize selectors for specific platforms
    """
    
    await scraper.goto(profile_url)
    
    # Wait for content to load
    await scraper.page.wait_for_timeout(3000)
    
    posts = []
    
    # Generic selectors (customize for specific platforms)
    post_selectors = [
        'article',
        '.post',
        '[data-testid="tweet"]',
        '.feed-item',
        '.story'
    ]
    
    for selector in post_selectors:
        post_elements = await scraper.page.query_selector_all(selector)
        if post_elements:
            scraper.log(f"Found {len(post_elements)} posts with selector: {selector}", "info")
            
            for i, post in enumerate(post_elements[:max_posts]):
                try:
                    # Extract post data
                    post_data = await extract_post_data(post)
                    if post_data:
                        posts.append(post_data)
                        
                except Exception as e:
                    scraper.log(f"Error extracting post {i+1}: {e}", "warning")
            
            break  # Use first working selector
    
    return posts

async def extract_post_data(post_element) -> dict:
    """Extract data from a single post element"""
    
    post_data = {}
    
    try:
        # Text content
        text_element = await post_element.query_selector('p, .text, .content')
        if text_element:
            post_data['text'] = await text_element.inner_text()
        
        # Author
        author_element = await post_element.query_selector('.author, .username, .name')
        if author_element:
            post_data['author'] = await author_element.inner_text()
        
        # Timestamp
        time_element = await post_element.query_selector('time, .timestamp, .date')
        if time_element:
            post_data['timestamp'] = await time_element.inner_text()
        
        # Engagement metrics
        likes_element = await post_element.query_selector('.likes, [aria-label*="like"]')
        if likes_element:
            post_data['likes'] = await likes_element.inner_text()
        
        # Images
        img_elements = await post_element.query_selector_all('img')
        if img_elements:
            images = []
            for img in img_elements:
                src = await img.get_attribute('src')
                if src and 'profile' not in src.lower():  # Skip profile images
                    images.append(src)
            post_data['images'] = images
        
    except Exception as e:
        print(f"Error extracting post data: {e}")
    
    return post_data
'''
        
        (app_dir / "social.py").write_text(social_py)
    
    def list_apps(self) -> List[Dict]:
        """List all created apps"""
        return list(self.apps_config["apps"].values())
    
    def get_app_info(self, app_name: str) -> Optional[Dict]:
        """Get information about a specific app"""
        return self.apps_config["apps"].get(app_name)
    
    def delete_app(self, app_name: str) -> bool:
        """Delete an app"""
        if app_name not in self.apps_config["apps"]:
            print(f"{Fore.YELLOW}App '{app_name}' not found{Style.RESET_ALL}")
            return False
        
        try:
            app_info = self.apps_config["apps"][app_name]
            app_dir = Path(app_info["path"])
            
            if app_dir.exists():
                shutil.rmtree(app_dir)
            
            del self.apps_config["apps"][app_name]
            self._save_apps_config()
            
            print(f"{Fore.GREEN}✅ App '{app_name}' deleted successfully{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to delete app '{app_name}': {e}{Style.RESET_ALL}")
            return False
