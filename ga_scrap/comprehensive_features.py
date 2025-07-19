"""
GA-Scrap Comprehensive Features Module
Contains EVERY remaining Playwright feature for the most complete scraping tool
"""

import asyncio
import json
import base64
import time
import re
from typing import Optional, Dict, Any, List, Union, Callable, Tuple, Pattern
from pathlib import Path
from datetime import datetime
from playwright.async_api import (
    Page, BrowserContext, ElementHandle, Locator, Request, Response,
    Route, Download, Video, CDPSession, FileChooser, Dialog, Worker, WebSocket
)


class ComprehensivePlaywrightFeatures:
    """Mixin class containing EVERY remaining Playwright feature"""
    
    # ==================== VIDEO & RECORDING ====================
    
    async def start_video_recording(self, page: Optional[Page] = None) -> Video:
        """
        Start video recording for a page
        
        Args:
            page: Page to record (default: main page)
            
        Returns:
            Video object
        """
        target_page = page or self.page
        
        try:
            video = target_page.video
            if video:
                self.log("🎥 Video recording started", "info")
                return video
            else:
                self.log("⚠️ Video recording not enabled in context", "warning")
                return None
        except Exception as e:
            self.log(f"Could not start video recording: {e}", "error")
            return None
    
    async def save_video(self, filename: str = None, page: Optional[Page] = None) -> str:
        """
        Save recorded video
        
        Args:
            filename: Video filename
            page: Page to save video from (default: main page)
            
        Returns:
            Path to saved video
        """
        target_page = page or self.page
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.webm"
        
        filepath = Path(self.downloads_path) / filename
        
        try:
            video = target_page.video
            if video:
                await video.save_as(str(filepath))
                self.log(f"🎥 Video saved: {filename}", "success")
                return str(filepath)
            else:
                self.log("⚠️ No video to save", "warning")
                return None
        except Exception as e:
            self.log(f"Could not save video: {e}", "error")
            return None
    
    # ==================== COVERAGE & PERFORMANCE ====================
    
    async def start_css_coverage(self, page: Optional[Page] = None):
        """
        Start CSS coverage tracking
        
        Args:
            page: Page to track (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.coverage.start_css_coverage()
            self.log("📊 CSS coverage tracking started", "info")
        except Exception as e:
            self.log(f"Could not start CSS coverage: {e}", "error")
    
    async def start_js_coverage(self, page: Optional[Page] = None):
        """
        Start JavaScript coverage tracking
        
        Args:
            page: Page to track (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.coverage.start_js_coverage()
            self.log("📊 JavaScript coverage tracking started", "info")
        except Exception as e:
            self.log(f"Could not start JS coverage: {e}", "error")
    
    async def stop_css_coverage(self, page: Optional[Page] = None) -> List[Dict[str, Any]]:
        """
        Stop CSS coverage and get results
        
        Args:
            page: Page to stop tracking (default: main page)
            
        Returns:
            CSS coverage data
        """
        target_page = page or self.page
        
        try:
            coverage = await target_page.coverage.stop_css_coverage()
            self.log(f"📊 CSS coverage stopped: {len(coverage)} entries", "info")
            return coverage
        except Exception as e:
            self.log(f"Could not stop CSS coverage: {e}", "error")
            return []
    
    async def stop_js_coverage(self, page: Optional[Page] = None) -> List[Dict[str, Any]]:
        """
        Stop JavaScript coverage and get results
        
        Args:
            page: Page to stop tracking (default: main page)
            
        Returns:
            JavaScript coverage data
        """
        target_page = page or self.page
        
        try:
            coverage = await target_page.coverage.stop_js_coverage()
            self.log(f"📊 JavaScript coverage stopped: {len(coverage)} entries", "info")
            return coverage
        except Exception as e:
            self.log(f"Could not stop JS coverage: {e}", "error")
            return []
    
    # ==================== ADVANCED LOCATORS ====================
    
    def get_locator(self, selector: str, page: Optional[Page] = None) -> Locator:
        """
        Get a Playwright locator for advanced element operations
        
        Args:
            selector: CSS selector or other locator
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        return target_page.locator(selector)
    
    def get_locator_by_text(self, text: str, exact: bool = False, page: Optional[Page] = None) -> Locator:
        """
        Get locator by text content
        
        Args:
            text: Text to search for
            exact: Whether to match exact text
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        if exact:
            return target_page.get_by_text(text, exact=True)
        else:
            return target_page.get_by_text(text)
    
    def get_locator_by_role(self, role: str, name: str = None, page: Optional[Page] = None) -> Locator:
        """
        Get locator by ARIA role
        
        Args:
            role: ARIA role (button, link, textbox, etc.)
            name: Accessible name
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        if name:
            return target_page.get_by_role(role, name=name)
        else:
            return target_page.get_by_role(role)
    
    def get_locator_by_label(self, label: str, exact: bool = False, page: Optional[Page] = None) -> Locator:
        """
        Get locator by label text
        
        Args:
            label: Label text
            exact: Whether to match exact text
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        return target_page.get_by_label(label, exact=exact)
    
    def get_locator_by_placeholder(self, placeholder: str, exact: bool = False, page: Optional[Page] = None) -> Locator:
        """
        Get locator by placeholder text
        
        Args:
            placeholder: Placeholder text
            exact: Whether to match exact text
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        return target_page.get_by_placeholder(placeholder, exact=exact)
    
    def get_locator_by_test_id(self, test_id: str, page: Optional[Page] = None) -> Locator:
        """
        Get locator by test ID attribute
        
        Args:
            test_id: Test ID value
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        return target_page.get_by_test_id(test_id)
    
    def get_locator_by_title(self, title: str, exact: bool = False, page: Optional[Page] = None) -> Locator:
        """
        Get locator by title attribute
        
        Args:
            title: Title text
            exact: Whether to match exact text
            page: Page to use (default: main page)
            
        Returns:
            Locator object
        """
        target_page = page or self.page
        return target_page.get_by_title(title, exact=exact)
    
    # ==================== FRAME OPERATIONS ====================
    
    async def get_frame_by_name(self, name: str, page: Optional[Page] = None):
        """
        Get frame by name
        
        Args:
            name: Frame name
            page: Page to search in (default: main page)
            
        Returns:
            Frame object or None
        """
        target_page = page or self.page
        
        try:
            frame = target_page.frame(name=name)
            if frame:
                self.log(f"🖼️ Frame found: {name}", "debug")
            return frame
        except Exception as e:
            self.log(f"Could not find frame '{name}': {e}", "warning")
            return None
    
    async def get_frame_by_url(self, url_pattern: str, page: Optional[Page] = None):
        """
        Get frame by URL pattern
        
        Args:
            url_pattern: URL pattern to match
            page: Page to search in (default: main page)
            
        Returns:
            Frame object or None
        """
        target_page = page or self.page
        
        try:
            frame = target_page.frame(url=url_pattern)
            if frame:
                self.log(f"🖼️ Frame found by URL: {url_pattern}", "debug")
            return frame
        except Exception as e:
            self.log(f"Could not find frame by URL '{url_pattern}': {e}", "warning")
            return None
    
    async def list_frames(self, page: Optional[Page] = None) -> List[str]:
        """
        List all frames in the page
        
        Args:
            page: Page to search in (default: main page)
            
        Returns:
            List of frame URLs
        """
        target_page = page or self.page
        
        try:
            frames = target_page.frames
            frame_urls = [frame.url for frame in frames]
            self.log(f"🖼️ Found {len(frames)} frames", "info")
            return frame_urls
        except Exception as e:
            self.log(f"Could not list frames: {e}", "error")
            return []
    
    # ==================== KEYBOARD & MOUSE ADVANCED ====================
    
    async def keyboard_press_sequence(self, keys: List[str], delay: float = 0.1, page: Optional[Page] = None):
        """
        Press a sequence of keys with delay
        
        Args:
            keys: List of keys to press
            delay: Delay between key presses in seconds
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            for key in keys:
                await target_page.keyboard.press(key)
                if delay > 0:
                    await asyncio.sleep(delay)
            self.log(f"⌨️ Key sequence pressed: {' + '.join(keys)}", "debug")
        except Exception as e:
            self.log(f"Could not press key sequence: {e}", "error")
    
    async def type_with_delay(self, text: str, delay: float = 0.1, page: Optional[Page] = None):
        """
        Type text with delay between characters
        
        Args:
            text: Text to type
            delay: Delay between characters in seconds
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.keyboard.type(text, delay=delay * 1000)  # Convert to milliseconds
            self.log(f"⌨️ Typed with delay: {text[:50]}...", "debug")
        except Exception as e:
            self.log(f"Could not type with delay: {e}", "error")
    
    async def mouse_move_smooth(self, x: int, y: int, steps: int = 10, page: Optional[Page] = None):
        """
        Move mouse smoothly to coordinates
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            steps: Number of intermediate steps
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            # Get current mouse position (assume center of viewport)
            viewport = target_page.viewport_size
            current_x = viewport["width"] // 2
            current_y = viewport["height"] // 2
            
            # Calculate step increments
            step_x = (x - current_x) / steps
            step_y = (y - current_y) / steps
            
            # Move in steps
            for i in range(steps):
                intermediate_x = current_x + (step_x * i)
                intermediate_y = current_y + (step_y * i)
                await target_page.mouse.move(intermediate_x, intermediate_y)
                await asyncio.sleep(0.01)  # Small delay for smooth movement
            
            # Final move to exact position
            await target_page.mouse.move(x, y)
            self.log(f"🖱️ Mouse moved smoothly to ({x}, {y})", "debug")
            
        except Exception as e:
            self.log(f"Could not move mouse smoothly: {e}", "error")

    # ==================== STORAGE & SESSION ====================

    async def save_storage_state(self, filename: str = None) -> Dict[str, Any]:
        """
        Save browser storage state (cookies, localStorage, sessionStorage)

        Args:
            filename: File to save state to

        Returns:
            Storage state data
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            storage_state = await self.context.storage_state()

            if filename:
                with open(filename, 'w') as f:
                    json.dump(storage_state, f, indent=2)
                self.log(f"💾 Storage state saved: {filename}", "success")

            return storage_state

        except Exception as e:
            self.log(f"Could not save storage state: {e}", "error")
            return {}

    async def load_storage_state(self, filename: str):
        """
        Load browser storage state from file

        Args:
            filename: File to load state from
        """
        try:
            with open(filename, 'r') as f:
                storage_state = json.load(f)

            # Create new context with loaded state
            if self.context:
                await self.context.close()

            self.context = await self.browser.new_context(storage_state=storage_state)
            await self._setup_event_listeners()

            # Recreate main page
            self.page = await self.context.new_page()
            await self._setup_page_listeners(self.page)

            self.log(f"💾 Storage state loaded: {filename}", "success")

        except Exception as e:
            self.log(f"Could not load storage state: {e}", "error")

    async def clear_storage(self, page: Optional[Page] = None):
        """
        Clear all browser storage (localStorage, sessionStorage, indexedDB)

        Args:
            page: Page to clear storage for (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.evaluate("""
                () => {
                    // Clear localStorage
                    if (window.localStorage) {
                        window.localStorage.clear();
                    }

                    // Clear sessionStorage
                    if (window.sessionStorage) {
                        window.sessionStorage.clear();
                    }

                    // Clear indexedDB
                    if (window.indexedDB) {
                        indexedDB.databases().then(databases => {
                            databases.forEach(db => {
                                indexedDB.deleteDatabase(db.name);
                            });
                        });
                    }
                }
            """)
            self.log("🗑️ Browser storage cleared", "info")
        except Exception as e:
            self.log(f"Could not clear storage: {e}", "error")

    # ==================== CLIPBOARD OPERATIONS ====================

    async def copy_to_clipboard(self, text: str, page: Optional[Page] = None):
        """
        Copy text to clipboard

        Args:
            text: Text to copy
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.evaluate(f"navigator.clipboard.writeText('{text}')")
            self.log(f"📋 Copied to clipboard: {text[:50]}...", "info")
        except Exception as e:
            self.log(f"Could not copy to clipboard: {e}", "error")

    async def paste_from_clipboard(self, page: Optional[Page] = None) -> str:
        """
        Get text from clipboard

        Args:
            page: Page to use (default: main page)

        Returns:
            Clipboard text
        """
        target_page = page or self.page

        try:
            text = await target_page.evaluate("navigator.clipboard.readText()")
            self.log(f"📋 Pasted from clipboard: {text[:50]}...", "info")
            return text
        except Exception as e:
            self.log(f"Could not paste from clipboard: {e}", "error")
            return ""

    # ==================== ADVANCED WAITING ====================

    async def wait_for_function(self, js_function: str, timeout: int = 30000, polling: Union[int, str] = "raf", page: Optional[Page] = None):
        """
        Wait for a JavaScript function to return truthy value

        Args:
            js_function: JavaScript function to evaluate
            timeout: Timeout in milliseconds
            polling: Polling interval ('raf' for requestAnimationFrame, or milliseconds)
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.wait_for_function(js_function, timeout=timeout, polling=polling)
            self.log("⏳ Function condition met", "info")
        except Exception as e:
            self.log(f"Function wait timeout: {e}", "warning")

    async def wait_for_url(self, url_pattern: Union[str, Pattern], timeout: int = 30000, page: Optional[Page] = None):
        """
        Wait for URL to match pattern

        Args:
            url_pattern: URL pattern to wait for
            timeout: Timeout in milliseconds
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.wait_for_url(url_pattern, timeout=timeout)
            self.log(f"🔗 URL matched: {url_pattern}", "info")
        except Exception as e:
            self.log(f"URL wait timeout: {e}", "warning")

    async def wait_for_console_message(self, predicate: Callable = None, timeout: int = 30000, page: Optional[Page] = None):
        """
        Wait for console message

        Args:
            predicate: Function to filter console messages
            timeout: Timeout in milliseconds
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            async with target_page.expect_console_message(predicate=predicate, timeout=timeout) as message_info:
                pass
            message = await message_info.value
            self.log(f"🖥️ Console message received: {message.text}", "info")
            return message
        except Exception as e:
            self.log(f"Console message wait timeout: {e}", "warning")
            return None

    # ==================== BROWSER CONTEXT MANAGEMENT ====================

    async def create_new_context(self, **options) -> BrowserContext:
        """
        Create a new browser context with options

        Args:
            **options: Context options

        Returns:
            New browser context
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            new_context = await self.browser.new_context(**options)
            self.log("🆕 New browser context created", "info")
            return new_context
        except Exception as e:
            self.log(f"Could not create new context: {e}", "error")
            return None

    async def switch_context(self, context: BrowserContext):
        """
        Switch to a different browser context

        Args:
            context: Browser context to switch to
        """
        try:
            self.context = context
            # Get the first page from the new context or create one
            pages = context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await context.new_page()

            self.log("🔄 Switched browser context", "info")
        except Exception as e:
            self.log(f"Could not switch context: {e}", "error")
