"""
GA-Scrap Core Module
Main scraper helper class with browser management and default headful mode
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
import json
import yaml
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class GAScrap:
    """
    GA-Scrap: A powerful Playwright-based scraper helper
    
    Features:
    - Always runs browser by default (headful mode)
    - Easy browser and context management
    - Built-in logging and debugging
    - Configuration management
    - Helper methods for common scraping tasks
    """
    
    def __init__(
        self,
        headless: bool = False,
        browser_type: str = "chromium",
        viewport: Dict[str, int] = None,
        user_agent: str = None,
        timeout: int = 30000,
        slow_mo: int = 0,
        debug: bool = False
    ):
        """
        Initialize GA-Scrap
        
        Args:
            headless: Run browser in headless mode (default: False - visible browser)
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
            viewport: Browser viewport size {'width': 1920, 'height': 1080}
            user_agent: Custom user agent string
            timeout: Default timeout for operations in milliseconds
            slow_mo: Slow down operations by specified milliseconds
            debug: Enable debug logging
        """
        self.headless = headless
        self.browser_type = browser_type
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.user_agent = user_agent
        self.timeout = timeout
        self.slow_mo = slow_mo
        self.debug = debug
        
        # Internal state
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.pages: List[Page] = []
        
        # Setup logging
        self._setup_logging()
        
        # Configuration
        self.config = {}
        
        self.log(f"🚀 GA-Scrap initialized with {browser_type} browser", "info")
        if not headless:
            self.log("👁️  Browser will run in VISIBLE mode (headful)", "info")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GA-Scrap')
    
    def log(self, message: str, level: str = "info"):
        """
        Log message with color coding
        
        Args:
            message: Message to log
            level: Log level ('info', 'warning', 'error', 'success', 'debug')
        """
        colors = {
            'info': Fore.CYAN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'success': Fore.GREEN,
            'debug': Fore.MAGENTA
        }
        
        color = colors.get(level, Fore.WHITE)
        print(f"{color}[GA-Scrap] {message}{Style.RESET_ALL}")
        
        # Also log to logger
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'debug':
            self.logger.debug(message)
        else:
            self.logger.info(message)
    
    async def start(self) -> 'GAScrap':
        """
        Start the browser and create initial context
        
        Returns:
            Self for method chaining
        """
        try:
            self.log("🔧 Starting Playwright...", "info")
            self.playwright = await async_playwright().start()
            
            # Get browser launcher
            if self.browser_type == "chromium":
                browser_launcher = self.playwright.chromium
            elif self.browser_type == "firefox":
                browser_launcher = self.playwright.firefox
            elif self.browser_type == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Launch browser
            self.log(f"🌐 Launching {self.browser_type} browser...", "info")
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
            
            # Create context
            context_options = {
                "viewport": self.viewport,
                "user_agent": self.user_agent
            }
            # Remove None values
            context_options = {k: v for k, v in context_options.items() if v is not None}
            
            self.context = await self.browser.new_context(**context_options)
            self.context.set_default_timeout(self.timeout)
            
            # Create initial page
            self.page = await self.context.new_page()
            self.pages.append(self.page)
            
            self.log("✅ Browser started successfully!", "success")
            return self
            
        except Exception as e:
            self.log(f"❌ Failed to start browser: {str(e)}", "error")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the browser and cleanup resources"""
        try:
            if self.context:
                await self.context.close()
                self.log("🔒 Browser context closed", "info")
            
            if self.browser:
                await self.browser.close()
                self.log("🔒 Browser closed", "info")
            
            if self.playwright:
                await self.playwright.stop()
                self.log("🔒 Playwright stopped", "info")
            
            # Reset state
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
            self.pages = []
            
        except Exception as e:
            self.log(f"⚠️  Error during cleanup: {str(e)}", "warning")
    
    async def new_page(self) -> Page:
        """
        Create a new page in the current context
        
        Returns:
            New page instance
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
        
        page = await self.context.new_page()
        self.pages.append(page)
        self.log(f"📄 New page created (total: {len(self.pages)})", "info")
        return page
    
    async def goto(self, url: str, page: Optional[Page] = None) -> Page:
        """
        Navigate to URL

        Args:
            url: URL to navigate to
            page: Page to use (default: main page)

        Returns:
            Page instance
        """
        target_page = page or self.page
        if not target_page:
            raise RuntimeError("No page available. Call start() first.")

        self.log(f"🔗 Navigating to: {url}", "info")
        await target_page.goto(url)
        return target_page

    async def get_text(self, selector: str, page: Optional[Page] = None) -> str:
        """
        Quick text extraction from element

        Args:
            selector: CSS selector
            page: Page to use (default: main page)

        Returns:
            Text content or empty string if not found
        """
        target_page = page or self.page
        try:
            element = await target_page.query_selector(selector)
            if element:
                return await element.inner_text()
        except Exception as e:
            self.log(f"Could not get text for '{selector}': {e}", "warning")
        return ""

    async def get_texts(self, selector: str, page: Optional[Page] = None) -> List[str]:
        """
        Quick text extraction from multiple elements

        Args:
            selector: CSS selector
            page: Page to use (default: main page)

        Returns:
            List of text contents
        """
        target_page = page or self.page
        texts = []
        try:
            elements = await target_page.query_selector_all(selector)
            for element in elements:
                text = await element.inner_text()
                texts.append(text)
        except Exception as e:
            self.log(f"Could not get texts for '{selector}': {e}", "warning")
        return texts

    async def click(self, selector: str, page: Optional[Page] = None):
        """
        Quick click on element

        Args:
            selector: CSS selector
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        try:
            await target_page.click(selector)
            self.log(f"✅ Clicked: {selector}", "info")
        except Exception as e:
            self.log(f"Could not click '{selector}': {e}", "error")

    async def type_text(self, selector: str, text: str, page: Optional[Page] = None):
        """
        Quick text input

        Args:
            selector: CSS selector for input field
            text: Text to type
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        try:
            await target_page.fill(selector, text)
            self.log(f"✅ Typed text in: {selector}", "info")
        except Exception as e:
            self.log(f"Could not type in '{selector}': {e}", "error")

    async def wait_for(self, selector: str, timeout: int = None, page: Optional[Page] = None):
        """
        Wait for element to appear

        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds (default: use instance timeout)
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        timeout = timeout or self.timeout
        try:
            await target_page.wait_for_selector(selector, timeout=timeout)
            self.log(f"✅ Element appeared: {selector}", "info")
        except Exception as e:
            self.log(f"Element did not appear '{selector}': {e}", "warning")

    async def screenshot(self, filename: str = None, page: Optional[Page] = None):
        """
        Take a screenshot

        Args:
            filename: Screenshot filename (default: auto-generated)
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        try:
            await target_page.screenshot(path=filename)
            self.log(f"📸 Screenshot saved: {filename}", "success")
        except Exception as e:
            self.log(f"Could not take screenshot: {e}", "error")
    
    def load_config(self, config_path: str):
        """
        Load configuration from file
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
        """
        config_file = Path(config_path)
        if not config_file.exists():
            self.log(f"⚠️  Config file not found: {config_path}", "warning")
            return
        
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix.lower() in ['.yml', '.yaml']:
                    self.config = yaml.safe_load(f)
                else:
                    self.config = json.load(f)
            
            self.log(f"📋 Configuration loaded from: {config_path}", "success")
            
        except Exception as e:
            self.log(f"❌ Failed to load config: {str(e)}", "error")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return await self.start()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
