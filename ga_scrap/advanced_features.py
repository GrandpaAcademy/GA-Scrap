"""
GA-Scrap Advanced Features Module
Contains every advanced Playwright feature for comprehensive web scraping
"""

import asyncio
import json
import base64
import mimetypes
import re
from typing import Optional, Dict, Any, List, Union, Callable, Pattern
from pathlib import Path
from datetime import datetime
from playwright.async_api import (
    Page, BrowserContext, ElementHandle, Locator, Request, Response,
    Route, Download, Video, CDPSession, FileChooser, Dialog
)


class AdvancedPlaywrightFeatures:
    """Mixin class containing every advanced Playwright feature"""
    
    # ==================== NETWORK INTERCEPTION ====================
    
    async def intercept_requests(self, url_pattern: Union[str, Pattern], handler: Callable = None):
        """
        Intercept and modify requests
        
        Args:
            url_pattern: URL pattern to intercept (string or regex)
            handler: Custom handler function for requests
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
        
        async def default_handler(route: Route, request: Request):
            # Log the intercepted request
            self.log(f"🔍 Intercepted: {request.method} {request.url}", "debug")
            
            # Call custom handler if provided
            if handler:
                await handler(route, request)
            else:
                # Continue with original request
                await route.continue_()
        
        await self.context.route(url_pattern, default_handler)
        self.log(f"🕸️ Request interception set up for: {url_pattern}", "info")
    
    async def block_requests(self, resource_types: List[str] = None, url_patterns: List[str] = None):
        """
        Block specific types of requests or URLs
        
        Args:
            resource_types: List of resource types to block ('image', 'stylesheet', 'font', etc.)
            url_patterns: List of URL patterns to block
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
        
        resource_types = resource_types or []
        url_patterns = url_patterns or []
        
        async def block_handler(route: Route, request: Request):
            # Block by resource type
            if request.resource_type in resource_types:
                await route.abort()
                self.log(f"🚫 Blocked {request.resource_type}: {request.url}", "debug")
                return
            
            # Block by URL pattern
            for pattern in url_patterns:
                if re.search(pattern, request.url):
                    await route.abort()
                    self.log(f"🚫 Blocked URL: {request.url}", "debug")
                    return
            
            # Continue if not blocked
            await route.continue_()
        
        await self.context.route("**/*", block_handler)
        self.log(f"🚫 Request blocking enabled", "info")
    
    async def modify_responses(self, url_pattern: str, modifier: Callable):
        """
        Modify responses before they reach the page
        
        Args:
            url_pattern: URL pattern to modify
            modifier: Function to modify response body
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
        
        async def response_modifier(route: Route, request: Request):
            response = await route.fetch()
            body = await response.body()
            
            # Apply modifier
            modified_body = modifier(body)
            
            await route.fulfill(
                response=response,
                body=modified_body
            )
            self.log(f"✏️ Modified response: {request.url}", "debug")
        
        await self.context.route(url_pattern, response_modifier)
        self.log(f"✏️ Response modification set up for: {url_pattern}", "info")
    
    # ==================== FILE OPERATIONS ====================
    
    async def upload_files(self, selector: str, file_paths: List[str], page: Optional[Page] = None):
        """
        Upload files to a file input
        
        Args:
            selector: CSS selector for file input
            file_paths: List of file paths to upload
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.set_input_files(selector, file_paths)
            self.log(f"📤 Uploaded {len(file_paths)} files", "success")
        except Exception as e:
            self.log(f"Could not upload files: {e}", "error")
    
    async def download_file(self, url: str, filename: str = None) -> str:
        """
        Download a file directly
        
        Args:
            url: URL to download
            filename: Local filename (auto-generated if not provided)
            
        Returns:
            Path to downloaded file
        """
        if not filename:
            filename = url.split('/')[-1] or f"download_{int(datetime.now().timestamp())}"
        
        filepath = Path(self.downloads_path) / filename
        
        try:
            # Use page.goto with a download expectation
            async with self.page.expect_download() as download_info:
                await self.page.goto(url)
            
            download = await download_info.value
            await download.save_as(filepath)
            
            self.log(f"⬇️ Downloaded: {filename}", "success")
            return str(filepath)
            
        except Exception as e:
            self.log(f"Could not download file: {e}", "error")
            return None
    
    async def save_page_as_pdf(self, filename: str = None, options: Dict[str, Any] = None, page: Optional[Page] = None) -> str:
        """
        Save page as PDF
        
        Args:
            filename: PDF filename
            options: PDF generation options
            page: Page to use (default: main page)
            
        Returns:
            Path to PDF file
        """
        target_page = page or self.page
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_{timestamp}.pdf"
        
        filepath = Path(self.downloads_path) / filename
        
        pdf_options = {
            "path": str(filepath),
            "format": "A4",
            "print_background": True,
            **(options or {})
        }
        
        try:
            await target_page.pdf(**pdf_options)
            self.log(f"📄 PDF saved: {filename}", "success")
            return str(filepath)
        except Exception as e:
            self.log(f"Could not save PDF: {e}", "error")
            return None
    
    # ==================== ADVANCED INTERACTIONS ====================
    
    async def drag_and_drop(self, source_selector: str, target_selector: str, page: Optional[Page] = None):
        """
        Perform drag and drop operation
        
        Args:
            source_selector: CSS selector for source element
            target_selector: CSS selector for target element
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.drag_and_drop(source_selector, target_selector)
            self.log(f"🖱️ Drag and drop: {source_selector} → {target_selector}", "success")
        except Exception as e:
            self.log(f"Could not perform drag and drop: {e}", "error")
    
    async def hover_and_click(self, hover_selector: str, click_selector: str, page: Optional[Page] = None):
        """
        Hover over one element and click another
        
        Args:
            hover_selector: CSS selector for element to hover
            click_selector: CSS selector for element to click
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.hover(hover_selector)
            await target_page.click(click_selector)
            self.log(f"🖱️ Hover and click: {hover_selector} → {click_selector}", "success")
        except Exception as e:
            self.log(f"Could not perform hover and click: {e}", "error")
    
    async def scroll_to_element(self, selector: str, page: Optional[Page] = None):
        """
        Scroll to a specific element
        
        Args:
            selector: CSS selector for element
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        try:
            await target_page.locator(selector).scroll_into_view_if_needed()
            self.log(f"📜 Scrolled to: {selector}", "success")
        except Exception as e:
            self.log(f"Could not scroll to element: {e}", "error")
    
    async def infinite_scroll(self, max_scrolls: int = 10, delay: float = 1.0, page: Optional[Page] = None):
        """
        Perform infinite scrolling
        
        Args:
            max_scrolls: Maximum number of scrolls
            delay: Delay between scrolls in seconds
            page: Page to use (default: main page)
        """
        target_page = page or self.page
        
        for i in range(max_scrolls):
            try:
                # Get current scroll position
                prev_height = await target_page.evaluate("document.body.scrollHeight")
                
                # Scroll to bottom
                await target_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # Wait for new content
                await asyncio.sleep(delay)
                
                # Check if new content loaded
                new_height = await target_page.evaluate("document.body.scrollHeight")
                
                if new_height == prev_height:
                    self.log(f"📜 Infinite scroll completed after {i+1} scrolls", "info")
                    break
                    
                self.log(f"📜 Scroll {i+1}/{max_scrolls}", "debug")
                
            except Exception as e:
                self.log(f"Error during infinite scroll: {e}", "error")
                break
    
    # ==================== ADVANCED ELEMENT OPERATIONS ====================
    
    async def get_element_attributes(self, selector: str, page: Optional[Page] = None) -> Dict[str, str]:
        """
        Get all attributes of an element
        
        Args:
            selector: CSS selector
            page: Page to use (default: main page)
            
        Returns:
            Dictionary of attributes
        """
        target_page = page or self.page
        
        try:
            attributes = await target_page.evaluate(f"""
                () => {{
                    const element = document.querySelector('{selector}');
                    if (!element) return {{}};
                    
                    const attrs = {{}};
                    for (let attr of element.attributes) {{
                        attrs[attr.name] = attr.value;
                    }}
                    return attrs;
                }}
            """)
            return attributes
        except Exception as e:
            self.log(f"Could not get attributes for '{selector}': {e}", "warning")
            return {}
    
    async def get_element_styles(self, selector: str, page: Optional[Page] = None) -> Dict[str, str]:
        """
        Get computed styles of an element
        
        Args:
            selector: CSS selector
            page: Page to use (default: main page)
            
        Returns:
            Dictionary of computed styles
        """
        target_page = page or self.page
        
        try:
            styles = await target_page.evaluate(f"""
                () => {{
                    const element = document.querySelector('{selector}');
                    if (!element) return {{}};
                    
                    const computedStyles = window.getComputedStyle(element);
                    const styles = {{}};
                    for (let prop of computedStyles) {{
                        styles[prop] = computedStyles.getPropertyValue(prop);
                    }}
                    return styles;
                }}
            """)
            return styles
        except Exception as e:
            self.log(f"Could not get styles for '{selector}': {e}", "warning")
            return {}
    
    async def wait_for_network_idle(self, timeout: int = 30000, page: Optional[Page] = None):
        """
        Wait for network to be idle (no requests for 500ms)

        Args:
            timeout: Timeout in milliseconds
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.wait_for_load_state("networkidle", timeout=timeout)
            self.log("🌐 Network idle", "info")
        except Exception as e:
            self.log(f"Network idle timeout: {e}", "warning")

    # ==================== JAVASCRIPT EXECUTION ====================

    async def execute_script(self, script: str, *args, page: Optional[Page] = None) -> Any:
        """
        Execute JavaScript in the page context

        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            page: Page to use (default: main page)

        Returns:
            Result of script execution
        """
        target_page = page or self.page

        try:
            result = await target_page.evaluate(script, *args)
            self.log("🔧 JavaScript executed", "debug")
            return result
        except Exception as e:
            self.log(f"JavaScript execution failed: {e}", "error")
            return None

    async def inject_script(self, script_path: str, page: Optional[Page] = None):
        """
        Inject a JavaScript file into the page

        Args:
            script_path: Path to JavaScript file
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.add_script_tag(path=script_path)
            self.log(f"💉 Script injected: {script_path}", "success")
        except Exception as e:
            self.log(f"Could not inject script: {e}", "error")

    async def inject_css(self, css_path: str = None, css_content: str = None, page: Optional[Page] = None):
        """
        Inject CSS into the page

        Args:
            css_path: Path to CSS file
            css_content: CSS content as string
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            if css_path:
                await target_page.add_style_tag(path=css_path)
                self.log(f"🎨 CSS file injected: {css_path}", "success")
            elif css_content:
                await target_page.add_style_tag(content=css_content)
                self.log("🎨 CSS content injected", "success")
        except Exception as e:
            self.log(f"Could not inject CSS: {e}", "error")

    # ==================== MOBILE & DEVICE FEATURES ====================

    async def emulate_device(self, device_name: str):
        """
        Emulate a specific device

        Args:
            device_name: Device name (e.g., 'iPhone 12', 'Pixel 5')
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            device = self.playwright.devices.get(device_name)
            if device:
                # Create new context with device settings
                await self.context.close()
                self.context = await self.browser.new_context(**device)
                await self._setup_event_listeners()

                # Recreate main page
                self.page = await self.context.new_page()
                await self._setup_page_listeners(self.page)

                self.log(f"📱 Device emulated: {device_name}", "success")
            else:
                self.log(f"⚠️ Unknown device: {device_name}", "warning")
        except Exception as e:
            self.log(f"Could not emulate device: {e}", "error")

    async def rotate_device(self, landscape: bool = True, page: Optional[Page] = None):
        """
        Rotate device orientation

        Args:
            landscape: True for landscape, False for portrait
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            current_viewport = target_page.viewport_size
            if landscape:
                new_viewport = {"width": max(current_viewport["width"], current_viewport["height"]),
                              "height": min(current_viewport["width"], current_viewport["height"])}
            else:
                new_viewport = {"width": min(current_viewport["width"], current_viewport["height"]),
                              "height": max(current_viewport["width"], current_viewport["height"])}

            await target_page.set_viewport_size(new_viewport)
            orientation = "landscape" if landscape else "portrait"
            self.log(f"🔄 Device rotated to {orientation}", "info")
        except Exception as e:
            self.log(f"Could not rotate device: {e}", "error")

    async def simulate_touch(self, x: int, y: int, page: Optional[Page] = None):
        """
        Simulate touch interaction

        Args:
            x: X coordinate
            y: Y coordinate
            page: Page to use (default: main page)
        """
        target_page = page or self.page

        try:
            await target_page.touchscreen.tap(x, y)
            self.log(f"👆 Touch simulated at ({x}, {y})", "debug")
        except Exception as e:
            self.log(f"Could not simulate touch: {e}", "error")

    # ==================== ACCESSIBILITY FEATURES ====================

    async def get_accessibility_tree(self, page: Optional[Page] = None) -> Dict[str, Any]:
        """
        Get the accessibility tree of the page

        Args:
            page: Page to use (default: main page)

        Returns:
            Accessibility tree data
        """
        target_page = page or self.page

        try:
            accessibility = await target_page.accessibility.snapshot()
            self.log("♿ Accessibility tree captured", "info")
            return accessibility
        except Exception as e:
            self.log(f"Could not get accessibility tree: {e}", "error")
            return {}

    async def check_accessibility(self, page: Optional[Page] = None) -> List[Dict[str, Any]]:
        """
        Perform basic accessibility checks

        Args:
            page: Page to use (default: main page)

        Returns:
            List of accessibility issues
        """
        target_page = page or self.page
        issues = []

        try:
            # Check for images without alt text
            images_without_alt = await target_page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images.filter(img => !img.alt).map(img => ({
                        tag: 'img',
                        src: img.src,
                        issue: 'Missing alt attribute'
                    }));
                }
            """)
            issues.extend(images_without_alt)

            # Check for buttons without accessible names
            buttons_without_names = await target_page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    return buttons.filter(btn => !btn.textContent.trim() && !btn.getAttribute('aria-label')).map(btn => ({
                        tag: 'button',
                        issue: 'Button without accessible name'
                    }));
                }
            """)
            issues.extend(buttons_without_names)

            # Check for form inputs without labels
            inputs_without_labels = await target_page.evaluate("""
                () => {
                    const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea'));
                    return inputs.filter(input => {
                        const id = input.id;
                        const hasLabel = id && document.querySelector(`label[for="${id}"]`);
                        const hasAriaLabel = input.getAttribute('aria-label');
                        return !hasLabel && !hasAriaLabel;
                    }).map(input => ({
                        tag: input.tagName.toLowerCase(),
                        type: input.type,
                        issue: 'Input without label'
                    }));
                }
            """)
            issues.extend(inputs_without_labels)

            self.log(f"♿ Accessibility check completed: {len(issues)} issues found", "info")
            return issues

        except Exception as e:
            self.log(f"Could not perform accessibility check: {e}", "error")
            return []
