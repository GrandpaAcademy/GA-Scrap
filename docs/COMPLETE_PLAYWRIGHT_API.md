# 🎯 Complete Playwright API Access in GA-Scrap

## 🚀 Full Playwright A-Z Access

GA-Scrap provides **complete access** to every Playwright feature through both async and sync interfaces, with sandbox mode support for both!

## 🔄 Both Interfaces Support Everything

### ✅ Async Interface (with Sandbox Mode)
```python
import asyncio
from ga_scrap import GAScrap

async def async_scraping():
    scraper = GAScrap(sandbox_mode=True)  # Sandbox mode for async!
    
    async with scraper:
        # All Playwright features available
        await scraper.goto("https://example.com")
        
        # Direct Playwright object access
        page = scraper.get_playwright_page()
        context = scraper.get_playwright_context()
        browser = scraper.get_playwright_browser()
        playwright = scraper.get_playwright_instance()
        
        # Execute any Playwright method with sandbox protection
        result = await scraper.execute_playwright_method('page', 'title')

asyncio.run(async_scraping())
```

### ✅ Sync Interface (with Sandbox Mode)
```python
from ga_scrap import SyncGAScrap

# Same features, no async needed!
scraper = SyncGAScrap(sandbox_mode=True)  # Sandbox mode for sync!

with scraper:
    # All Playwright features available
    scraper.goto("https://example.com")
    
    # Direct Playwright object access
    page = scraper.get_playwright_page()
    context = scraper.get_playwright_context()
    browser = scraper.get_playwright_browser()
    playwright = scraper.get_playwright_instance()
    
    # Execute any Playwright method with sandbox protection
    result = scraper.execute_playwright_method('page', 'title')
```

## 🎯 Direct Playwright Object Access

### 📄 Page Object Access
```python
# Get direct access to Playwright Page
page = scraper.get_playwright_page()

# Use ANY Page method directly
await page.evaluate("console.log('Direct access!')")  # Async
page.evaluate("console.log('Direct access!')")        # Sync (auto-handled)

# Examples of direct Page methods
await page.add_script_tag(url="https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js")
await page.add_style_tag(content="body { background: red; }")
await page.bring_to_front()
await page.emulate_media(media="print")
await page.expose_function("myFunction", lambda x: x * 2)
await page.pdf(path="page.pdf")
await page.reload()
await page.route("**/*.png", lambda route: route.abort())
await page.set_extra_http_headers({"Custom-Header": "value"})
await page.set_viewport_size({"width": 1280, "height": 720})
```

### 🌐 Context Object Access
```python
# Get direct access to BrowserContext
context = scraper.get_playwright_context()

# Use ANY BrowserContext method directly
await context.add_cookies([{"name": "test", "value": "value", "url": "https://example.com"}])
await context.add_init_script("window.customProperty = 'value'")
await context.clear_cookies()
await context.clear_permissions()
await context.grant_permissions(["geolocation"], origin="https://example.com")
await context.route("**/*", lambda route: route.continue_())
await context.set_default_navigation_timeout(60000)
await context.set_default_timeout(30000)
await context.set_extra_http_headers({"Authorization": "Bearer token"})
await context.set_geolocation({"latitude": 59.95, "longitude": 30.31667})
await context.set_offline(True)
```

### 🖥️ Browser Object Access
```python
# Get direct access to Browser
browser = scraper.get_playwright_browser()

# Use ANY Browser method directly
contexts = browser.contexts
version = browser.version
await browser.new_context(viewport={"width": 800, "height": 600})
await browser.new_page()
browser.is_connected()
```

### ⚙️ Playwright Instance Access
```python
# Get direct access to Playwright instance
playwright = scraper.get_playwright_instance()

# Use ANY Playwright method directly
devices = playwright.devices
chromium = playwright.chromium
firefox = playwright.firefox
webkit = playwright.webkit
selectors = playwright.selectors
```

## 🛡️ Safe Method Execution

### Execute Any Playwright Method with Sandbox Protection
```python
# Both async and sync interfaces support this
result = await scraper.execute_playwright_method('page', 'title')  # Async
result = scraper.execute_playwright_method('page', 'title')        # Sync

# Try risky operations safely
scraper.execute_playwright_method('page', 'click', '#might-not-exist')
# In sandbox mode: logs error, continues execution
# In normal mode: raises exception
```

### Helper Methods for Common Objects
```python
# Sync interface provides convenient helpers
result = scraper.playwright_page_method('title')
result = scraper.playwright_context_method('cookies')
result = scraper.playwright_browser_method('version')
result = scraper.playwright_instance_method('devices')
```

## 🔤 Complete Playwright Feature List

### A - Accessibility
```python
# Accessibility testing
tree = await scraper.get_accessibility_tree()
issues = await scraper.check_accessibility()

# Direct access
page = scraper.get_playwright_page()
snapshot = await page.accessibility.snapshot()
```

### B - Browser Management
```python
# Browser control
browser = scraper.get_playwright_browser()
version = browser.version
contexts = browser.contexts
await browser.close()
```

### C - Context & Cookies
```python
# Context management
context = scraper.get_playwright_context()
await context.add_cookies([...])
await context.clear_cookies()
await context.set_geolocation({...})
```

### D - Downloads
```python
# Download handling
async with page.expect_download() as download_info:
    await page.click("a[download]")
download = await download_info.value
await download.save_as("file.zip")
```

### E - Evaluate JavaScript
```python
# JavaScript execution
result = await page.evaluate("() => document.title")
await page.evaluate_handle("() => document.body")
await page.add_script_tag(content="console.log('injected')")
```

### F - Forms & File Upload
```python
# Form interactions
await page.fill("input[name='username']", "user")
await page.select_option("select", "option1")
await page.set_input_files("input[type=file]", "file.txt")
await page.check("input[type=checkbox]")
```

### G - Geolocation
```python
# Geolocation control
await context.set_geolocation({"latitude": 40.7128, "longitude": -74.0060})
await context.grant_permissions(["geolocation"])
```

### H - Hover & Interactions
```python
# Mouse interactions
await page.hover("button")
await page.click("button", button="right")
await page.dblclick("button")
await page.drag_and_drop("source", "target")
```

### I - Injection (CSS/JS)
```python
# Code injection
await page.add_style_tag(content="body { background: red; }")
await page.add_script_tag(url="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js")
```

### J - JavaScript Execution
```python
# Advanced JS execution
await page.expose_function("pythonFunction", lambda x: x * 2)
result = await page.evaluate("pythonFunction(5)")  # Returns 10
```

### K - Keyboard
```python
# Keyboard control
await page.keyboard.press("Enter")
await page.keyboard.type("Hello World")
await page.keyboard.down("Shift")
await page.keyboard.up("Shift")
```

### L - Locators
```python
# Advanced locators
locator = page.locator("button")
await locator.click()
await locator.fill("text")
count = await locator.count()
```

### M - Mouse
```python
# Mouse control
await page.mouse.move(100, 100)
await page.mouse.click(100, 100)
await page.mouse.wheel(0, 100)
```

### N - Network
```python
# Network control
await page.route("**/*.png", lambda route: route.abort())
await context.set_offline(True)
await page.set_extra_http_headers({"Custom": "Header"})
```

### O - Offline Mode
```python
# Offline simulation
await context.set_offline(True)
await context.set_offline(False)
```

### P - PDF Generation
```python
# PDF creation
await page.pdf(path="page.pdf", format="A4")
```

### Q - Query Selectors
```python
# Element selection
element = await page.query_selector("button")
elements = await page.query_selector_all("button")
```

### R - Recording
```python
# Video recording (configured at context creation)
video = page.video
await video.save_as("recording.webm")
```

### S - Screenshots
```python
# Screenshot capture
await page.screenshot(path="page.png", full_page=True)
await element.screenshot(path="element.png")
```

### T - Touch & Mobile
```python
# Touch simulation
await page.touchscreen.tap(100, 100)
await context.set_viewport_size({"width": 375, "height": 667})
```

### U - Upload
```python
# File upload
await page.set_input_files("input[type=file]", ["file1.txt", "file2.txt"])
```

### V - Viewport
```python
# Viewport control
await page.set_viewport_size({"width": 1920, "height": 1080})
size = page.viewport_size
```

### W - Waiting
```python
# Wait strategies
await page.wait_for_selector("button")
await page.wait_for_load_state("networkidle")
await page.wait_for_function("() => document.readyState === 'complete'")
await page.wait_for_timeout(1000)
```

### X - XPath
```python
# XPath selectors
element = await page.query_selector("xpath=//button[@class='submit']")
```

### Y - Yielding Control
```python
# Pause execution
await page.pause()  # Opens Playwright Inspector
```

### Z - Zones (Timezone)
```python
# Timezone control
await context.set_timezone_id("America/New_York")
```

## 🎉 Summary

**Every single Playwright feature is available in GA-Scrap:**

✅ **Both async and sync interfaces**
✅ **Sandbox mode for both interfaces**  
✅ **Direct object access**
✅ **Safe method execution**
✅ **Complete A-Z feature coverage**
✅ **No limitations or restrictions**

**You have complete control over Playwright through GA-Scrap!** 🚀
