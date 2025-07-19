"""
Simple Scraper - Ultra-easy scraping interface
"""

import asyncio
from typing import List, Dict, Any, Optional
from .core import GAScrap

class SimpleScraper:
    """
    Ultra-simple scraper interface
    
    Perfect for beginners or quick scraping tasks
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize simple scraper
        
        Args:
            headless: Run browser in headless mode (default: False - visible)
        """
        self.scraper = GAScrap(headless=headless, debug=True)
        self.started = False
    
    async def __aenter__(self):
        """Start scraper when entering context"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop scraper when exiting context"""
        await self.stop()
    
    async def start(self):
        """Start the scraper"""
        if not self.started:
            await self.scraper.start()
            self.started = True
    
    async def stop(self):
        """Stop the scraper"""
        if self.started:
            await self.scraper.stop()
            self.started = False
    
    async def go(self, url: str):
        """
        Navigate to a URL
        
        Args:
            url: Website URL to visit
        """
        await self.scraper.goto(url)
    
    async def get(self, selector: str) -> str:
        """
        Get text from an element
        
        Args:
            selector: CSS selector (e.g., "h1", ".title", "#content")
            
        Returns:
            Text content or empty string if not found
        """
        return await self.scraper.get_text(selector)
    
    async def get_all(self, selector: str) -> List[str]:
        """
        Get text from all matching elements
        
        Args:
            selector: CSS selector
            
        Returns:
            List of text contents
        """
        return await self.scraper.get_texts(selector)
    
    async def click(self, selector: str):
        """
        Click on an element
        
        Args:
            selector: CSS selector of element to click
        """
        await self.scraper.click(selector)
    
    async def type(self, selector: str, text: str):
        """
        Type text into an input field
        
        Args:
            selector: CSS selector of input field
            text: Text to type
        """
        await self.scraper.type_text(selector, text)
    
    async def wait(self, selector: str, seconds: int = 10):
        """
        Wait for an element to appear
        
        Args:
            selector: CSS selector to wait for
            seconds: Maximum seconds to wait
        """
        await self.scraper.wait_for(selector, timeout=seconds * 1000)
    
    async def screenshot(self, filename: str = None):
        """
        Take a screenshot
        
        Args:
            filename: Screenshot filename (optional)
        """
        await self.scraper.screenshot(filename)
    
    async def pause(self, message: str = "Press Enter to continue..."):
        """
        Pause execution and wait for user input
        
        Args:
            message: Message to show user
        """
        self.scraper.log(message, "info")
        input()
    
    def log(self, message: str):
        """
        Log a message
        
        Args:
            message: Message to log
        """
        self.scraper.log(message, "info")

# Convenience functions for even simpler usage
async def scrape(url: str, selector: str, headless: bool = False) -> str:
    """
    Quick scrape - get text from one element
    
    Args:
        url: Website URL
        selector: CSS selector
        headless: Run in headless mode
        
    Returns:
        Text content
    """
    async with SimpleScraper(headless=headless) as scraper:
        await scraper.go(url)
        return await scraper.get(selector)

async def scrape_all(url: str, selector: str, headless: bool = False) -> List[str]:
    """
    Quick scrape - get text from all matching elements
    
    Args:
        url: Website URL
        selector: CSS selector
        headless: Run in headless mode
        
    Returns:
        List of text contents
    """
    async with SimpleScraper(headless=headless) as scraper:
        await scraper.go(url)
        return await scraper.get_all(selector)

async def scrape_data(url: str, selectors: Dict[str, str], headless: bool = False) -> Dict[str, Any]:
    """
    Quick scrape - get multiple data points
    
    Args:
        url: Website URL
        selectors: Dictionary of {field_name: css_selector}
        headless: Run in headless mode
        
    Returns:
        Dictionary of scraped data
    """
    async with SimpleScraper(headless=headless) as scraper:
        await scraper.go(url)
        
        data = {}
        for field, selector in selectors.items():
            if selector.endswith('[]'):  # Multiple elements
                selector = selector[:-2]
                data[field] = await scraper.get_all(selector)
            else:  # Single element
                data[field] = await scraper.get(selector)
        
        return data
