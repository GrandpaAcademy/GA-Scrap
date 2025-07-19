"""
GA-Scrap Core Module
Main scraper helper class with browser management and default headful mode
Enhanced with EVERY Playwright feature for comprehensive web scraping
"""

import asyncio
import logging
import time
import base64
import mimetypes
from typing import Optional, Dict, Any, List, Callable, Union, Tuple, Pattern
from pathlib import Path
import json
import yaml
import re
from datetime import datetime
from playwright.async_api import (
    async_playwright, Browser, BrowserContext, Page, Playwright,
    ElementHandle, Locator, Request, Response, Route, FileChooser,
    Download, Video, ConsoleMessage, Dialog, Worker, WebSocket,
    CDPSession, BrowserType, Error as PlaywrightError
)
from colorama import Fore, Style, init
from .advanced_features import AdvancedPlaywrightFeatures
from .comprehensive_features import ComprehensivePlaywrightFeatures

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class GAScrap(AdvancedPlaywrightFeatures, ComprehensivePlaywrightFeatures):
    """
    GA-Scrap: A comprehensive Playwright-based scraper helper with EVERY feature

    Features:
    - Always runs browser by default (headful mode)
    - Complete browser and context management
    - Advanced network interception and monitoring
    - File upload/download handling
    - Mobile device emulation
    - Geolocation and permissions
    - Video recording and screenshots
    - Performance monitoring
    - WebSocket and Worker support
    - Cookie and storage management
    - PDF generation
    - Accessibility testing
    - Network throttling
    - Request/response modification
    - And much more!
    """

    def __init__(
        self,
        headless: bool = False,
        browser_type: str = "chromium",
        viewport: Dict[str, int] = None,
        user_agent: str = None,
        timeout: int = 30000,
        slow_mo: int = 0,
        debug: bool = False,
        # Advanced browser options
        proxy: Dict[str, str] = None,
        downloads_path: str = None,
        record_video: bool = False,
        record_har: bool = False,
        ignore_https_errors: bool = False,
        java_script_enabled: bool = True,
        accept_downloads: bool = True,
        # Device emulation
        device_name: str = None,
        # Geolocation
        geolocation: Dict[str, float] = None,
        # Permissions
        permissions: List[str] = None,
        # Locale and timezone
        locale: str = None,
        timezone_id: str = None,
        # Color scheme
        color_scheme: str = None,
        # Reduced motion
        reduced_motion: str = None,
        # Force prefers-color-scheme
        forced_colors: str = None
    ):
        """
        Initialize GA-Scrap with comprehensive Playwright features

        Args:
            headless: Run browser in headless mode (default: False - visible browser)
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
            viewport: Browser viewport size {'width': 1920, 'height': 1080}
            user_agent: Custom user agent string
            timeout: Default timeout for operations in milliseconds
            slow_mo: Slow down operations by specified milliseconds
            debug: Enable debug logging
            proxy: Proxy configuration {'server': 'http://proxy:8080', 'username': 'user', 'password': 'pass'}
            downloads_path: Directory for downloads
            record_video: Enable video recording
            record_har: Enable HAR (HTTP Archive) recording
            ignore_https_errors: Ignore HTTPS certificate errors
            java_script_enabled: Enable/disable JavaScript
            accept_downloads: Accept downloads automatically
            device_name: Device to emulate (e.g., 'iPhone 12', 'Pixel 5')
            geolocation: Geolocation {'latitude': 40.7128, 'longitude': -74.0060}
            permissions: List of permissions to grant ['geolocation', 'camera', 'microphone']
            locale: Locale (e.g., 'en-US', 'de-DE')
            timezone_id: Timezone (e.g., 'America/New_York')
            color_scheme: 'light', 'dark', or 'no-preference'
            reduced_motion: 'reduce' or 'no-preference'
            forced_colors: 'active' or 'none'
        """
        # Basic configuration
        self.headless = headless
        self.browser_type = browser_type
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.user_agent = user_agent
        self.timeout = timeout
        self.slow_mo = slow_mo
        self.debug = debug

        # Advanced configuration
        self.proxy = proxy
        self.downloads_path = downloads_path or str(Path.cwd() / "downloads")
        self.record_video = record_video
        self.record_har = record_har
        self.ignore_https_errors = ignore_https_errors
        self.java_script_enabled = java_script_enabled
        self.accept_downloads = accept_downloads
        self.device_name = device_name
        self.geolocation = geolocation
        self.permissions = permissions or []
        self.locale = locale
        self.timezone_id = timezone_id
        self.color_scheme = color_scheme
        self.reduced_motion = reduced_motion
        self.forced_colors = forced_colors

        # Internal state
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.pages: List[Page] = []
        self.downloads: List[Download] = []
        self.requests: List[Request] = []
        self.responses: List[Response] = []
        self.console_messages: List[ConsoleMessage] = []
        self.dialogs: List[Dialog] = []
        self.workers: List[Worker] = []
        self.websockets: List[WebSocket] = []
        self.routes: List[Route] = []
        self.cdp_sessions: List[CDPSession] = []

        # Performance tracking
        self.performance_metrics = {}
        self.network_activity = []
        self.coverage_data = {}

        # Setup logging
        self._setup_logging()

        # Configuration
        self.config = {}

        # Create downloads directory
        Path(self.downloads_path).mkdir(parents=True, exist_ok=True)

        self.log(f"🚀 GA-Scrap initialized with {browser_type} browser", "info")
        if not headless:
            self.log("👁️  Browser will run in VISIBLE mode (headful)", "info")
        if device_name:
            self.log(f"📱 Device emulation: {device_name}", "info")
        if record_video:
            self.log("🎥 Video recording enabled", "info")
        if record_har:
            self.log("📊 HAR recording enabled", "info")
    
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
        Start the browser and create initial context with all advanced features

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

            # Prepare browser launch options
            launch_options = {
                "headless": self.headless,
                "slow_mo": self.slow_mo,
                "proxy": self.proxy,
                "downloads_path": self.downloads_path,
                "ignore_default_args": [],
                "args": []
            }

            # Add browser-specific arguments
            if self.browser_type == "chromium":
                launch_options["args"].extend([
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox" if self.headless else ""
                ])

            # Remove None values and empty strings
            launch_options = {k: v for k, v in launch_options.items() if v is not None and v != ""}
            launch_options["args"] = [arg for arg in launch_options["args"] if arg]

            # Launch browser
            self.log(f"🌐 Launching {self.browser_type} browser...", "info")
            self.browser = await browser_launcher.launch(**launch_options)

            # Prepare context options with ALL Playwright features
            context_options = {
                "viewport": self.viewport,
                "user_agent": self.user_agent,
                "ignore_https_errors": self.ignore_https_errors,
                "java_script_enabled": self.java_script_enabled,
                "accept_downloads": self.accept_downloads,
                "proxy": self.proxy,
                "locale": self.locale,
                "timezone_id": self.timezone_id,
                "geolocation": self.geolocation,
                "permissions": self.permissions,
                "color_scheme": self.color_scheme,
                "reduced_motion": self.reduced_motion,
                "forced_colors": self.forced_colors,
                "record_video_dir": str(Path(self.downloads_path) / "videos") if self.record_video else None,
                "record_video_size": self.viewport if self.record_video else None,
                "record_har_path": str(Path(self.downloads_path) / f"session_{int(time.time())}.har") if self.record_har else None,
                "record_har_omit_content": False if self.record_har else None
            }

            # Device emulation
            if self.device_name:
                device = self.playwright.devices.get(self.device_name)
                if device:
                    context_options.update(device)
                    self.log(f"📱 Emulating device: {self.device_name}", "info")
                else:
                    self.log(f"⚠️  Unknown device: {self.device_name}", "warning")

            # Remove None values
            context_options = {k: v for k, v in context_options.items() if v is not None}

            # Create context
            self.context = await self.browser.new_context(**context_options)
            self.context.set_default_timeout(self.timeout)

            # Set up event listeners for comprehensive monitoring
            await self._setup_event_listeners()

            # Create initial page
            self.page = await self.context.new_page()
            self.pages.append(self.page)

            # Set up page-specific event listeners
            await self._setup_page_listeners(self.page)

            self.log("✅ Browser started successfully!", "success")
            return self

        except Exception as e:
            self.log(f"❌ Failed to start browser: {str(e)}", "error")
            await self.stop()
            raise
    
    async def _setup_event_listeners(self):
        """Set up comprehensive event listeners for monitoring"""
        if not self.context:
            return

        # Request/Response monitoring
        self.context.on("request", self._on_request)
        self.context.on("response", self._on_response)
        self.context.on("requestfailed", self._on_request_failed)
        self.context.on("requestfinished", self._on_request_finished)

        # Page events
        self.context.on("page", self._on_new_page)

        # Background page events (for service workers)
        self.context.on("backgroundpage", self._on_background_page)

        # Service worker events
        self.context.on("serviceworker", self._on_service_worker)

        self.log("🔗 Event listeners configured", "debug")

    async def _setup_page_listeners(self, page: Page):
        """Set up page-specific event listeners"""
        # Console messages
        page.on("console", self._on_console)

        # Dialog handling
        page.on("dialog", self._on_dialog)

        # File chooser
        page.on("filechooser", self._on_file_chooser)

        # Download handling
        page.on("download", self._on_download)

        # Page errors
        page.on("pageerror", self._on_page_error)

        # Crash handling
        page.on("crash", self._on_page_crash)

        # Close handling
        page.on("close", self._on_page_close)

        # DOM content loaded
        page.on("domcontentloaded", self._on_dom_content_loaded)

        # Load event
        page.on("load", self._on_page_load)

        # Frame events
        page.on("frameattached", self._on_frame_attached)
        page.on("framedetached", self._on_frame_detached)
        page.on("framenavigated", self._on_frame_navigated)

        # Worker events
        page.on("worker", self._on_worker)

        # WebSocket events
        page.on("websocket", self._on_websocket)

        # Popup handling
        page.on("popup", self._on_popup)

        self.log(f"📄 Page listeners configured for page {len(self.pages)}", "debug")

    async def stop(self):
        """Stop the browser and cleanup resources"""
        try:
            # Save performance metrics if available
            if self.page and self.performance_metrics:
                await self._save_performance_metrics()

            # Close all pages
            for page in self.pages:
                try:
                    await page.close()
                except:
                    pass

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
            self.downloads = []
            self.requests = []
            self.responses = []
            self.console_messages = []
            self.dialogs = []
            self.workers = []
            self.websockets = []
            self.routes = []
            self.cdp_sessions = []

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

    async def screenshot(self, filename: str = None, page: Optional[Page] = None, **options):
        """
        Take a screenshot with advanced options

        Args:
            filename: Screenshot filename (default: auto-generated)
            page: Page to use (default: main page)
            **options: Additional screenshot options (full_page, clip, quality, etc.)
        """
        target_page = page or self.page
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        try:
            await target_page.screenshot(path=filename, **options)
            self.log(f"📸 Screenshot saved: {filename}", "success")
            return filename
        except Exception as e:
            self.log(f"Could not take screenshot: {e}", "error")
            return None

    # ==================== EVENT HANDLERS ====================

    def _on_request(self, request: Request):
        """Handle request events"""
        self.requests.append(request)

        # Safely get post data
        try:
            post_data = request.post_data
        except (UnicodeDecodeError, Exception):
            post_data = "<binary data>"

        self.network_activity.append({
            "type": "request",
            "url": request.url,
            "method": request.method,
            "timestamp": time.time(),
            "headers": request.headers,
            "post_data": post_data
        })
        if self.debug:
            self.log(f"🌐 Request: {request.method} {request.url}", "debug")

    def _on_response(self, response: Response):
        """Handle response events"""
        self.responses.append(response)
        self.network_activity.append({
            "type": "response",
            "url": response.url,
            "status": response.status,
            "timestamp": time.time(),
            "headers": response.headers
        })
        if self.debug:
            self.log(f"📡 Response: {response.status} {response.url}", "debug")

    def _on_request_failed(self, request: Request):
        """Handle failed request events"""
        self.log(f"❌ Request failed: {request.url}", "warning")

    def _on_request_finished(self, request: Request):
        """Handle finished request events"""
        if self.debug:
            self.log(f"✅ Request finished: {request.url}", "debug")

    def _on_new_page(self, page: Page):
        """Handle new page events"""
        self.pages.append(page)
        asyncio.create_task(self._setup_page_listeners(page))
        self.log(f"📄 New page created (total: {len(self.pages)})", "info")

    def _on_background_page(self, page: Page):
        """Handle background page events"""
        self.log("🔄 Background page created", "debug")

    def _on_service_worker(self, worker: Worker):
        """Handle service worker events"""
        self.workers.append(worker)
        self.log("⚙️ Service worker created", "debug")

    def _on_console(self, message: ConsoleMessage):
        """Handle console messages"""
        self.console_messages.append(message)
        level_map = {
            "error": "error",
            "warning": "warning",
            "info": "info",
            "log": "debug"
        }
        log_level = level_map.get(message.type, "debug")
        self.log(f"🖥️ Console [{message.type}]: {message.text}", log_level)

    def _on_dialog(self, dialog: Dialog):
        """Handle dialog events"""
        self.dialogs.append(dialog)
        self.log(f"💬 Dialog [{dialog.type}]: {dialog.message}", "info")
        # Auto-accept dialogs by default
        asyncio.create_task(dialog.accept())

    def _on_file_chooser(self, file_chooser: FileChooser):
        """Handle file chooser events"""
        self.log("📁 File chooser opened", "info")

    def _on_download(self, download: Download):
        """Handle download events"""
        self.downloads.append(download)
        self.log(f"⬇️ Download started: {download.suggested_filename}", "info")

    def _on_page_error(self, error):
        """Handle page errors"""
        self.log(f"� Page error: {error}", "error")

    def _on_page_crash(self, page: Page):
        """Handle page crashes"""
        self.log("💥 Page crashed!", "error")

    def _on_page_close(self, page: Page):
        """Handle page close events"""
        if page in self.pages:
            self.pages.remove(page)
        self.log(f"🔒 Page closed (remaining: {len(self.pages)})", "info")

    def _on_dom_content_loaded(self, page: Page):
        """Handle DOM content loaded events"""
        if self.debug:
            self.log("📄 DOM content loaded", "debug")

    def _on_page_load(self, page: Page):
        """Handle page load events"""
        if self.debug:
            self.log("✅ Page loaded", "debug")

    def _on_frame_attached(self, frame):
        """Handle frame attached events"""
        if self.debug:
            self.log(f"🖼️ Frame attached: {frame.url}", "debug")

    def _on_frame_detached(self, frame):
        """Handle frame detached events"""
        if self.debug:
            self.log(f"🖼️ Frame detached: {frame.url}", "debug")

    def _on_frame_navigated(self, frame):
        """Handle frame navigated events"""
        if self.debug:
            self.log(f"🖼️ Frame navigated: {frame.url}", "debug")

    def _on_worker(self, worker: Worker):
        """Handle worker events"""
        self.workers.append(worker)
        self.log("👷 Worker created", "debug")

    def _on_websocket(self, websocket: WebSocket):
        """Handle WebSocket events"""
        self.websockets.append(websocket)
        self.log(f"🔌 WebSocket connected: {websocket.url}", "info")

    def _on_popup(self, page: Page):
        """Handle popup events"""
        self.pages.append(page)
        asyncio.create_task(self._setup_page_listeners(page))
        self.log("🪟 Popup opened", "info")
    
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
    
    # ==================== ADVANCED PLAYWRIGHT FEATURES ====================

    async def save_performance_metrics(self, filename: str = None) -> Dict[str, Any]:
        """Save performance metrics to file"""
        if not self.page:
            return {}

        try:
            # Get performance metrics
            metrics = await self.page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    const paint = performance.getEntriesByType('paint');
                    const resources = performance.getEntriesByType('resource');

                    return {
                        navigation: navigation ? {
                            domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                            loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                            domInteractive: navigation.domInteractive - navigation.navigationStart,
                            firstByte: navigation.responseStart - navigation.requestStart,
                            dns: navigation.domainLookupEnd - navigation.domainLookupStart,
                            tcp: navigation.connectEnd - navigation.connectStart,
                            ssl: navigation.connectEnd - navigation.secureConnectionStart
                        } : null,
                        paint: paint.map(p => ({name: p.name, startTime: p.startTime})),
                        resources: resources.length,
                        memory: performance.memory ? {
                            used: performance.memory.usedJSHeapSize,
                            total: performance.memory.totalJSHeapSize,
                            limit: performance.memory.jsHeapSizeLimit
                        } : null
                    }
                }
            """)

            self.performance_metrics = metrics

            if filename:
                with open(filename, 'w') as f:
                    json.dump(metrics, f, indent=2)
                self.log(f"📊 Performance metrics saved: {filename}", "success")

            return metrics

        except Exception as e:
            self.log(f"Could not get performance metrics: {e}", "warning")
            return {}

    async def _save_performance_metrics(self):
        """Internal method to save performance metrics on stop"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = str(Path(self.downloads_path) / f"performance_{timestamp}.json")
        await self.save_performance_metrics(filename)

    async def emulate_network_conditions(self, offline: bool = False, download_throughput: int = None,
                                       upload_throughput: int = None, latency: int = None):
        """
        Emulate network conditions

        Args:
            offline: Set to offline mode
            download_throughput: Download speed in bytes/sec
            upload_throughput: Upload speed in bytes/sec
            latency: Latency in milliseconds
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.context.set_offline(offline)

            if any([download_throughput, upload_throughput, latency]):
                # Use CDP for network throttling
                cdp = await self.context.new_cdp_session(self.page)
                await cdp.send('Network.enable')

                conditions = {}
                if download_throughput is not None:
                    conditions['downloadThroughput'] = download_throughput
                if upload_throughput is not None:
                    conditions['uploadThroughput'] = upload_throughput
                if latency is not None:
                    conditions['latency'] = latency

                await cdp.send('Network.emulateNetworkConditions', {
                    'offline': offline,
                    **conditions
                })

                self.cdp_sessions.append(cdp)

            status = "offline" if offline else "online"
            self.log(f"🌐 Network conditions set: {status}", "info")

        except Exception as e:
            self.log(f"Could not set network conditions: {e}", "error")

    async def set_geolocation(self, latitude: float, longitude: float, accuracy: float = 100):
        """
        Set geolocation

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            accuracy: Accuracy in meters
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.context.set_geolocation({
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            })
            self.log(f"📍 Geolocation set: {latitude}, {longitude}", "info")
        except Exception as e:
            self.log(f"Could not set geolocation: {e}", "error")

    async def grant_permissions(self, permissions: List[str], origin: str = None):
        """
        Grant permissions to the page

        Args:
            permissions: List of permissions ('geolocation', 'camera', 'microphone', etc.)
            origin: Origin to grant permissions for (default: current page)
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.context.grant_permissions(permissions, origin=origin)
            self.log(f"🔐 Permissions granted: {', '.join(permissions)}", "info")
        except Exception as e:
            self.log(f"Could not grant permissions: {e}", "error")

    async def clear_permissions(self):
        """Clear all granted permissions"""
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.context.clear_permissions()
            self.log("🔐 Permissions cleared", "info")
        except Exception as e:
            self.log(f"Could not clear permissions: {e}", "error")

    async def add_cookies(self, cookies: List[Dict[str, Any]]):
        """
        Add cookies to the browser context

        Args:
            cookies: List of cookie dictionaries
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.context.add_cookies(cookies)
            self.log(f"🍪 Added {len(cookies)} cookies", "info")
        except Exception as e:
            self.log(f"Could not add cookies: {e}", "error")

    async def get_cookies(self, urls: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get cookies from the browser context

        Args:
            urls: List of URLs to get cookies for (default: all)

        Returns:
            List of cookie dictionaries
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            cookies = await self.context.cookies(urls)
            self.log(f"🍪 Retrieved {len(cookies)} cookies", "info")
            return cookies
        except Exception as e:
            self.log(f"Could not get cookies: {e}", "error")
            return []

    async def clear_cookies(self):
        """Clear all cookies"""
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.context.clear_cookies()
            self.log("🍪 Cookies cleared", "info")
        except Exception as e:
            self.log(f"Could not clear cookies: {e}", "error")

    async def __aenter__(self):
        """Async context manager entry"""
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
