# 🎭 Complete Playwright API Access

<div align="center">

**Every Playwright Feature from A-Z**  
*Full control when you need it*

</div>

---

## 🎯 Overview

GA-Scrap provides **complete access** to every Playwright feature through both sync and async interfaces. You get the best of both worlds: simple GA-Scrap methods for common tasks, and full Playwright power for advanced scenarios.

---

## 🔄 Access Methods

### 1. High-Level GA-Scrap Methods
*Perfect for most use cases*

```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    scraper.screenshot("page.png")
```

### 2. Direct Playwright Object Access
*When you need specific Playwright features*

```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Get direct access to Playwright objects
    page = scraper.get_playwright_page()
    context = scraper.get_playwright_context()
    browser = scraper.get_playwright_browser()
    playwright = scraper.get_playwright_instance()
    
    # Use any Playwright method directly
    await page.evaluate("document.body.style.background = 'red'")
    cookies = await context.cookies()
    version = browser.version
```

### 3. Safe Method Execution
*Execute any Playwright method with error protection*

```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # Execute any Playwright method safely
    title = scraper.execute_playwright_method('page', 'title')
    cookies = scraper.execute_playwright_method('context', 'cookies')
    version = scraper.execute_playwright_method('browser', 'version')
    
    # Helper methods for sync interface
    title = scraper.playwright_page_method('title')
    cookies = scraper.playwright_context_method('cookies')
```

---

## 🔤 Complete A-Z Feature List

### **A** - Accessibility
```python
# Accessibility testing
tree = scraper.get_accessibility_tree()

# Direct Playwright access
page = scraper.get_playwright_page()
snapshot = await page.accessibility.snapshot()
```

### **B** - Browser Management
```python
# Browser control
browser = scraper.get_playwright_browser()
version = browser.version
contexts = browser.contexts
is_connected = browser.is_connected()
```

### **C** - Context & Cookies
```python
# Cookie management
scraper.add_cookies([{"name": "test", "value": "value", "domain": "example.com"}])
cookies = scraper.get_cookies()

# Direct context access
context = scraper.get_playwright_context()
await context.clear_cookies()
await context.set_geolocation({"latitude": 40.7128, "longitude": -74.0060})
```

### **D** - Downloads
```python
# Download handling
scraper.download_file("https://example.com/file.zip")

# Advanced download control
page = scraper.get_playwright_page()
async with page.expect_download() as download_info:
    await page.click("a[download]")
download = await download_info.value
await download.save_as("file.zip")
```

### **E** - Evaluate JavaScript
```python
# JavaScript execution
result = scraper.execute_script("return document.title")
scraper.execute_script("document.body.style.background = 'red'")

# Advanced evaluation
page = scraper.get_playwright_page()
result = await page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
```

### **F** - Forms & File Upload
```python
# Form interactions
scraper.input("input[name='username']", "user")
scraper.select_option("select", "option1")
scraper.upload_files("input[type=file]", ["file1.txt", "file2.txt"])
scraper.check("input[type=checkbox]")

# Advanced form handling
page = scraper.get_playwright_page()
await page.fill("input[name='username']", "user")
await page.set_input_files("input[type=file]", ["file1.txt", "file2.txt"])
```

### **G** - Geolocation
```python
# Geolocation control
scraper.set_geolocation(40.7128, -74.0060)

# Direct context access
context = scraper.get_playwright_context()
await context.set_geolocation({"latitude": 40.7128, "longitude": -74.0060})
await context.grant_permissions(["geolocation"])
```

### **H** - Hover & Interactions
```python
# Mouse interactions
scraper.hover("button")
scraper.click("button")
scraper.double_click("button")

# Advanced interactions
page = scraper.get_playwright_page()
await page.hover("button")
await page.click("button", button="right")
await page.drag_and_drop("source", "target")
```

### **I** - Injection (CSS/JS)
```python
# Code injection
scraper.inject_css("body { background: red; }")
scraper.execute_script("console.log('injected')")

# Advanced injection
page = scraper.get_playwright_page()
await page.add_style_tag(content="body { background: red; }")
await page.add_script_tag(url="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js")
```

### **J** - JavaScript Execution
```python
# JavaScript execution
result = scraper.execute_script("return document.title")

# Advanced JS execution
page = scraper.get_playwright_page()
await page.expose_function("pythonFunction", lambda x: x * 2)
result = await page.evaluate("pythonFunction(5)")  # Returns 10
```

### **K** - Keyboard
```python
# Keyboard control
scraper.keyboard_press("Enter")
scraper.keyboard_type("Hello World")

# Advanced keyboard
page = scraper.get_playwright_page()
await page.keyboard.press("Enter")
await page.keyboard.type("Hello World")
await page.keyboard.down("Shift")
await page.keyboard.up("Shift")
```

### **L** - Locators
```python
# Element location
element = scraper.get_locator("button")

# Advanced locators
page = scraper.get_playwright_page()
locator = page.locator("button")
await locator.click()
count = await locator.count()
```

### **M** - Mouse
```python
# Mouse operations
scraper.mouse_move(100, 100)
scraper.click_at_position(100, 100)

# Advanced mouse
page = scraper.get_playwright_page()
await page.mouse.move(100, 100)
await page.mouse.click(100, 100)
await page.mouse.wheel(0, 100)
```

### **N** - Network
```python
# Network control
scraper.block_requests(["*.png", "*.jpg"])
scraper.set_user_agent("Custom User Agent")

# Advanced network
page = scraper.get_playwright_page()
await page.route("**/*.png", lambda route: route.abort())
await page.set_extra_http_headers({"Custom": "Header"})
```

### **O** - Offline Mode
```python
# Offline simulation
scraper.set_offline(True)

# Direct context access
context = scraper.get_playwright_context()
await context.set_offline(True)
```

### **P** - PDF Generation
```python
# PDF creation
scraper.save_pdf("page.pdf")

# Advanced PDF options
page = scraper.get_playwright_page()
await page.pdf(path="page.pdf", format="A4", print_background=True)
```

### **Q** - Query Selectors
```python
# Element selection
text = scraper.get_text("h1")
texts = scraper.get_all_text(".item")

# Advanced selectors
page = scraper.get_playwright_page()
element = await page.query_selector("button")
elements = await page.query_selector_all("button")
```

### **R** - Recording
```python
# Video recording (configured at startup)
scraper = SyncGAScrap(record_video=True)

# Access video
page = scraper.get_playwright_page()
video = page.video
await video.save_as("recording.webm")
```

### **S** - Screenshots
```python
# Screenshot capture
scraper.screenshot("page.png")
scraper.screenshot_full_page("full.png")

# Advanced screenshots
page = scraper.get_playwright_page()
await page.screenshot(path="page.png", full_page=True)
element = await page.query_selector(".content")
await element.screenshot(path="element.png")
```

### **T** - Touch & Mobile
```python
# Touch simulation
scraper.simulate_touch(100, 100)

# Advanced touch
page = scraper.get_playwright_page()
await page.touchscreen.tap(100, 100)
```

### **U** - Upload
```python
# File upload
scraper.upload_files("input[type=file]", ["file1.txt", "file2.txt"])

# Advanced upload
page = scraper.get_playwright_page()
await page.set_input_files("input[type=file]", ["file1.txt", "file2.txt"])
```

### **V** - Viewport
```python
# Viewport control
scraper.set_viewport_size(1920, 1080)

# Advanced viewport
page = scraper.get_playwright_page()
await page.set_viewport_size({"width": 1920, "height": 1080})
size = page.viewport_size
```

### **W** - Waiting
```python
# Wait strategies
scraper.wait_for_selector("button")
scraper.wait_for_network_idle()

# Advanced waiting
page = scraper.get_playwright_page()
await page.wait_for_selector("button")
await page.wait_for_load_state("networkidle")
await page.wait_for_function("() => document.readyState === 'complete'")
```

### **X** - XPath
```python
# XPath selectors
text = scraper.get_text("xpath=//button[@class='submit']")

# Advanced XPath
page = scraper.get_playwright_page()
element = await page.query_selector("xpath=//button[@class='submit']")
```

### **Y** - Yielding Control
```python
# Pause execution
scraper.pause("Check the page and press Enter to continue...")

# Playwright inspector
page = scraper.get_playwright_page()
await page.pause()  # Opens Playwright Inspector
```

### **Z** - Zones (Timezone)
```python
# Timezone control
scraper = SyncGAScrap(timezone="America/New_York")

# Direct context access
context = scraper.get_playwright_context()
await context.set_timezone_id("America/New_York")
```

---

## 🛡️ Safe Execution with Sandbox Mode

All Playwright methods can be executed safely with sandbox mode:

```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # These won't crash even if they fail
    title = scraper.execute_playwright_method('page', 'title')
    cookies = scraper.execute_playwright_method('context', 'cookies')
    
    # Direct object access with error handling
    page = scraper.get_playwright_page()
    try:
        await page.click("#might-not-exist")
    except:
        pass  # Handle gracefully
```

---

## 🎯 When to Use Each Approach

### 🔄 Use GA-Scrap Methods When:
- **Learning web scraping** - Simple, intuitive API
- **Common operations** - Navigation, clicking, text extraction
- **Quick prototyping** - Fast development cycles
- **Sandbox mode benefits** - Error-resilient development

### 🎭 Use Direct Playwright When:
- **Advanced features** - Specific Playwright capabilities
- **Performance optimization** - Direct control over operations
- **Complex interactions** - Multi-step, coordinated actions
- **Integration needs** - Existing Playwright code

### 🛡️ Use Safe Execution When:
- **Unknown websites** - Unpredictable page structures
- **Development phase** - Testing different approaches
- **Error handling** - Graceful failure recovery
- **Batch operations** - Processing multiple items

---

## 🚀 Examples

### Combining All Approaches
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    # High-level GA-Scrap method
    scraper.goto("https://example.com")
    
    # Direct Playwright access for advanced features
    page = scraper.get_playwright_page()
    await page.evaluate("document.body.style.background = 'linear-gradient(45deg, red, blue)'")
    
    # Safe method execution for risky operations
    title = scraper.execute_playwright_method('page', 'title')
    
    # Back to GA-Scrap for simplicity
    scraper.screenshot("final.png")
```

### Advanced Playwright Features
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Get all Playwright objects
    page = scraper.get_playwright_page()
    context = scraper.get_playwright_context()
    browser = scraper.get_playwright_browser()
    
    # Use advanced Playwright features
    await page.expose_function("customFunction", lambda x: x.upper())
    await page.route("**/*.png", lambda route: route.abort())
    await context.grant_permissions(["geolocation", "camera"])
    
    # Execute custom JavaScript with exposed function
    result = await page.evaluate("customFunction('hello world')")
    print(result)  # "HELLO WORLD"
```

---

<div align="center">

**🎭 Complete Playwright Power at Your Fingertips!**

**Next:** [🔧 Architecture](architecture.md) • [⚡ Hot Reload](hot-reload.md)

</div>
