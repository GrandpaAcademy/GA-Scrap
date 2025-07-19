"""
GA-Scrap Translator Module
Provides synchronous wrapper around async GA-Scrap for easy syntax
"""

import asyncio
import threading
from typing import Optional, Dict, Any, List, Union
from .core import GAScrap


class SyncGAScrap:
    """
    Synchronous wrapper for GA-Scrap that handles async operations automatically
    Provides simple, easy-to-use syntax without needing async/await
    """
    
    def __init__(self, **kwargs):
        """
        Initialize synchronous GA-Scrap wrapper
        
        Args:
            **kwargs: All GAScrap initialization parameters
        """
        self._scraper = GAScrap(**kwargs)
        self._loop = None
        self._thread = None
        self._started = False
    
    def _ensure_loop(self):
        """Ensure event loop is running in background thread"""
        if self._loop is None or not self._loop.is_running():
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            # Wait a bit for loop to start
            import time
            time.sleep(0.1)
    
    def _run_loop(self):
        """Run event loop in background thread"""
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        except Exception as e:
            pass  # Ignore cleanup errors
    
    def _run_async(self, coro):
        """Run async coroutine and return result"""
        self._ensure_loop()
        try:
            future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            return future.result(timeout=60)  # Add timeout to prevent hanging
        except Exception as e:
            if self._scraper.sandbox_mode:
                self.log(f"🏖️ Async operation failed in sandbox mode: {e}", "warning")
                return None
            else:
                raise
    
    # ==================== CORE METHODS ====================
    
    def start(self):
        """Start the browser"""
        if not self._started:
            self._run_async(self._scraper.start())
            self._started = True
        return self
    
    def stop(self):
        """Stop the browser"""
        if self._started:
            try:
                self._run_async(self._scraper.stop())
            except Exception as e:
                self.log(f"⚠️ Error during browser stop: {e}", "warning")

            self._started = False

            # Clean up event loop
            try:
                if self._loop and self._loop.is_running():
                    self._loop.call_soon_threadsafe(self._loop.stop)
                    if self._thread and self._thread.is_alive():
                        self._thread.join(timeout=2)  # Wait max 2 seconds
            except Exception as e:
                pass  # Ignore cleanup errors
    
    def goto(self, url: str, page=None):
        """Navigate to URL"""
        result = self._run_async(self._scraper.goto(url, page))
        if result is None and self._scraper.sandbox_mode:
            self.log(f"🏖️ Navigation to {url} failed in sandbox mode. Browser remains active.", "warning")
        return self
    
    def screenshot(self, filename: str = None, page=None, **options):
        """Take a screenshot"""
        self._run_async(self._scraper.screenshot(filename, page, **options))
        return self  # Return self for chaining
    
    def new_page(self):
        """Create a new page"""
        return self._run_async(self._scraper.new_page())
    
    # ==================== ELEMENT INTERACTIONS ====================
    
    def click(self, selector: str, page=None):
        """Click an element"""
        result = self._run_async(self._scraper.click(selector, page))
        if result is None and self._scraper.sandbox_mode:
            self.log(f"🏖️ Click on {selector} failed in sandbox mode. Browser remains active.", "warning")
        return self
    
    def input(self, selector: str, text: str, page=None):
        """Input text into an element"""
        result = self._run_async(self._scraper.type_text(selector, text, page))
        if result is None and self._scraper.sandbox_mode:
            self.log(f"🏖️ Input to {selector} failed in sandbox mode. Browser remains active.", "warning")
        return self
    
    def type_text(self, selector: str, text: str, page=None):
        """Type text into an element (alias for input)"""
        return self.input(selector, text, page)
    
    def get_text(self, selector: str, page=None) -> str:
        """Get text from an element"""
        return self._run_async(self._scraper.get_text(selector, page))
    
    def get_texts(self, selector: str, page=None) -> List[str]:
        """Get text from multiple elements"""
        return self._run_async(self._scraper.get_texts(selector, page))
    
    def wait_for(self, selector: str, timeout: int = None, page=None):
        """Wait for element to appear"""
        self._run_async(self._scraper.wait_for(selector, timeout, page))
        return self
    
    # ==================== SCROLLING ====================
    
    def scroll_to_bottom(self, page=None):
        """Scroll to bottom of page"""
        target_page = page or self._scraper.page
        self._run_async(target_page.evaluate("window.scrollTo(0, document.body.scrollHeight)"))
        return self
    
    def scroll_to_top(self, page=None):
        """Scroll to top of page"""
        target_page = page or self._scraper.page
        self._run_async(target_page.evaluate("window.scrollTo(0, 0)"))
        return self
    
    def scroll_to_element(self, selector: str, page=None):
        """Scroll to a specific element"""
        self._run_async(self._scraper.scroll_to_element(selector, page))
        return self
    
    def infinite_scroll(self, max_scrolls: int = 10, delay: float = 1.0, page=None):
        """Perform infinite scrolling"""
        self._run_async(self._scraper.infinite_scroll(max_scrolls, delay, page))
        return self
    
    # ==================== PAGE MANAGEMENT ====================
    
    def close_page(self, page=None):
        """Close a specific page"""
        target_page = page or self._scraper.page
        self._run_async(target_page.close())
        return self
    
    def close_all_pages(self):
        """Close all pages except the main one"""
        for page in self._scraper.pages[1:]:  # Keep first page
            try:
                self._run_async(page.close())
            except:
                pass
        return self
    
    def switch_to_page(self, page_index: int):
        """Switch to a specific page by index"""
        if 0 <= page_index < len(self._scraper.pages):
            self._scraper.page = self._scraper.pages[page_index]
        return self
    
    # ==================== ADVANCED FEATURES ====================
    
    def hover(self, selector: str, page=None):
        """Hover over an element"""
        target_page = page or self._scraper.page
        self._run_async(target_page.hover(selector))
        return self
    
    def drag_and_drop(self, source_selector: str, target_selector: str, page=None):
        """Perform drag and drop"""
        self._run_async(self._scraper.drag_and_drop(source_selector, target_selector, page))
        return self
    
    def upload_files(self, selector: str, file_paths: List[str], page=None):
        """Upload files"""
        self._run_async(self._scraper.upload_files(selector, file_paths, page))
        return self
    
    def save_pdf(self, filename: str = None, options: Dict[str, Any] = None, page=None):
        """Save page as PDF"""
        return self._run_async(self._scraper.save_page_as_pdf(filename, options, page))
    
    def execute_script(self, script: str, *args, page=None):
        """Execute JavaScript"""
        return self._run_async(self._scraper.execute_script(script, *args, page))
    
    def inject_css(self, css_content: str = None, css_path: str = None, page=None):
        """Inject CSS"""
        self._run_async(self._scraper.inject_css(css_path, css_content, page))
        return self
    
    def add_cookies(self, cookies: List[Dict[str, Any]]):
        """Add cookies"""
        self._run_async(self._scraper.add_cookies(cookies))
        return self
    
    def get_cookies(self, urls: List[str] = None) -> List[Dict[str, Any]]:
        """Get cookies"""
        return self._run_async(self._scraper.get_cookies(urls))
    
    def clear_cookies(self):
        """Clear all cookies"""
        self._run_async(self._scraper.clear_cookies())
        return self
    
    def set_geolocation(self, latitude: float, longitude: float, accuracy: float = 100):
        """Set geolocation"""
        self._run_async(self._scraper.set_geolocation(latitude, longitude, accuracy))
        return self
    
    def emulate_device(self, device_name: str):
        """Emulate a device"""
        self._run_async(self._scraper.emulate_device(device_name))
        return self
    
    def block_requests(self, resource_types: List[str] = None, url_patterns: List[str] = None):
        """Block requests"""
        self._run_async(self._scraper.block_requests(resource_types, url_patterns))
        return self
    
    def wait_for_network_idle(self, timeout: int = 30000, page=None):
        """Wait for network to be idle"""
        self._run_async(self._scraper.wait_for_network_idle(timeout, page))
        return self

    def get_accessibility_tree(self, page=None):
        """Get accessibility tree"""
        return self._run_async(self._scraper.get_accessibility_tree(page))

    def check_accessibility(self, page=None):
        """Check accessibility issues"""
        return self._run_async(self._scraper.check_accessibility(page))
    
    # ==================== PROPERTIES ====================
    
    @property
    def page(self):
        """Get current page"""
        return self._scraper.page
    
    @property
    def pages(self):
        """Get all pages"""
        return self._scraper.pages
    
    @property
    def requests(self):
        """Get captured requests"""
        return self._scraper.requests
    
    @property
    def responses(self):
        """Get captured responses"""
        return self._scraper.responses
    
    @property
    def console_messages(self):
        """Get console messages"""
        return self._scraper.console_messages
    
    @property
    def downloads(self):
        """Get downloads"""
        return self._scraper.downloads
    
    # ==================== CONTEXT MANAGER ====================
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
    
    # ==================== UTILITY METHODS ====================
    
    def log(self, message: str, level: str = "info"):
        """Log a message"""
        self._scraper.log(message, level)
    
    def pause(self, message: str = "Press Enter to continue..."):
        """Pause execution"""
        self._scraper.log(message, "info")
        input()
        return self

    # ==================== FULL PLAYWRIGHT API ACCESS ====================

    def get_playwright_page(self, page=None):
        """
        Get direct access to Playwright Page object for advanced operations

        Args:
            page: Specific page to get (default: main page)

        Returns:
            Playwright Page object with full API access
        """
        return self._scraper.get_playwright_page(page)

    def get_playwright_context(self):
        """
        Get direct access to Playwright BrowserContext object

        Returns:
            Playwright BrowserContext object with full API access
        """
        return self._scraper.get_playwright_context()

    def get_playwright_browser(self):
        """
        Get direct access to Playwright Browser object

        Returns:
            Playwright Browser object with full API access
        """
        return self._scraper.get_playwright_browser()

    def get_playwright_instance(self):
        """
        Get direct access to Playwright instance

        Returns:
            Playwright instance with full API access
        """
        return self._scraper.get_playwright_instance()

    def execute_playwright_method(self, obj_path: str, method_name: str, *args, **kwargs):
        """
        Execute any Playwright method directly with sandbox mode support

        Args:
            obj_path: Path to object ('page', 'context', 'browser', 'playwright')
            method_name: Method name to execute
            *args: Method arguments
            **kwargs: Method keyword arguments

        Returns:
            Method result or None if error in sandbox mode
        """
        return self._run_async(self._scraper.execute_playwright_method(obj_path, method_name, *args, **kwargs))

    # ==================== ADVANCED PLAYWRIGHT METHODS ====================

    def playwright_page_method(self, method_name: str, *args, **kwargs):
        """Execute any Page method directly"""
        return self.execute_playwright_method('page', method_name, *args, **kwargs)

    def playwright_context_method(self, method_name: str, *args, **kwargs):
        """Execute any BrowserContext method directly"""
        return self.execute_playwright_method('context', method_name, *args, **kwargs)

    def playwright_browser_method(self, method_name: str, *args, **kwargs):
        """Execute any Browser method directly"""
        return self.execute_playwright_method('browser', method_name, *args, **kwargs)

    def playwright_instance_method(self, method_name: str, *args, **kwargs):
        """Execute any Playwright instance method directly"""
        return self.execute_playwright_method('playwright', method_name, *args, **kwargs)


# Create a simple function-based interface
def create_scraper(**kwargs) -> SyncGAScrap:
    """
    Create a new synchronous GA-Scrap instance
    
    Args:
        **kwargs: GAScrap initialization parameters
        
    Returns:
        SyncGAScrap instance
    """
    return SyncGAScrap(**kwargs)
