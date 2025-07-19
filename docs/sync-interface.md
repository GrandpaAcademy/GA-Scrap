# 🔄 Synchronous Interface

<div align="center">

**No More async/await - Just Simple Python!**  
*Web scraping as easy as regular Python code*

</div>

---

## 🎯 Why Synchronous Interface?

The synchronous interface eliminates the complexity of `async`/`await` syntax, making web scraping accessible to everyone:

<table>
<tr>
<td width="50%">

### 😵 **Traditional Async**
```python
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://example.com")
        title = await page.text_content("h1")
        await browser.close()
        return title

result = asyncio.run(scrape())
```

</td>
<td width="50%">

### 😊 **GA-Scrap Sync**
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
```

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Basic Usage
```python
from ga_scrap import SyncGAScrap

# Method 1: Context manager (recommended)
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    print(f"Title: {title}")

# Method 2: Manual start/stop
scraper = SyncGAScrap()
scraper.start()
scraper.goto("https://example.com")
title = scraper.get_text("h1")
scraper.stop()
```

### Configuration
```python
scraper = SyncGAScrap(
    headless=False,        # Show browser
    sandbox_mode=True,     # Error-resilient mode
    timeout=30000,         # 30 second timeout
    browser_type="chromium", # Browser choice
    debug=True            # Detailed logging
)
```

---

## 📖 Complete API Reference

### 🌐 Navigation
```python
# Navigate to URLs
scraper.goto("https://example.com")
scraper.go_back()
scraper.go_forward()
scraper.reload()

# Multiple pages
page2 = scraper.new_page()
scraper.goto("https://another-site.com", page=page2)
```

### 🔍 Element Selection & Interaction
```python
# Click elements
scraper.click("button")
scraper.click_text("Submit")
scraper.double_click(".item")
scraper.right_click(".menu")

# Input text
scraper.input("input[name='username']", "john_doe")
scraper.clear_input("input[name='password']")
scraper.select_option("select", "option1")

# Hover and focus
scraper.hover(".dropdown")
scraper.focus("input[type='text']")
```

### 📝 Data Extraction
```python
# Get text content
title = scraper.get_text("h1")
texts = scraper.get_all_text(".item")

# Get attributes
href = scraper.get_attribute("a", "href")
classes = scraper.get_attribute("div", "class")

# Get HTML
html = scraper.get_html(".content")
inner_html = scraper.get_inner_html(".container")
```

### 📸 Media & Files
```python
# Screenshots
scraper.screenshot("page.png")
scraper.screenshot("element.png", selector=".content")
scraper.screenshot_full_page("full.png")

# PDF generation
scraper.save_pdf("document.pdf")

# File operations
scraper.upload_files("input[type='file']", ["file1.txt", "file2.txt"])
scraper.download_file("https://example.com/file.zip")
```

### ⏳ Waiting & Timing
```python
# Wait for elements
scraper.wait_for_selector(".loading", state="hidden")
scraper.wait_for_text("Success!")
scraper.wait_for_url("https://success-page.com")

# Wait for network
scraper.wait_for_network_idle()
scraper.wait_for_load_state("domcontentloaded")

# Custom waits
scraper.wait(2000)  # Wait 2 seconds
scraper.wait_for_function("() => document.readyState === 'complete'")
```

### 🎨 Page Manipulation
```python
# JavaScript execution
result = scraper.execute_script("return document.title")
scraper.execute_script("document.body.style.background = 'red'")

# CSS injection
scraper.inject_css("body { font-size: 20px; }")

# Scrolling
scraper.scroll_to_bottom()
scraper.scroll_to_top()
scraper.scroll_to_element(".target")
```

### 📱 Device & Mobile
```python
# Device emulation
scraper = SyncGAScrap(device="iPhone 12")

# Touch simulation
scraper.simulate_touch(100, 200)
scraper.swipe(start_x=100, start_y=200, end_x=300, end_y=200)

# Viewport control
scraper.set_viewport_size(1920, 1080)
```

### 🌐 Network & Cookies
```python
# Cookie management
scraper.add_cookies([{
    "name": "session",
    "value": "abc123",
    "domain": "example.com"
}])
cookies = scraper.get_cookies()
scraper.clear_cookies()

# Network control
scraper.block_requests(["*.png", "*.jpg"])
scraper.set_user_agent("Custom User Agent")
scraper.set_geolocation(40.7128, -74.0060)
```

---

## 🔗 Method Chaining

The synchronous interface supports method chaining for fluent, readable code:

```python
with SyncGAScrap() as scraper:
    (scraper
     .goto("https://example.com")
     .input("input[name='q']", "search term")
     .click("button[type='submit']")
     .wait_for_selector(".results")
     .scroll_to_bottom()
     .screenshot("results.png"))
```

### Complex Chaining Example
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    result = (scraper
              .goto("https://quotes.toscrape.com")
              .wait_for_selector(".quote")
              .scroll_to_bottom()
              .click(".next")  # Might fail, but continues in sandbox mode
              .wait_for_selector(".quote")
              .screenshot("quotes.png")
              .get_all_text(".quote .text"))
    
    print(f"Found {len(result)} quotes")
```

---

## 🎭 Full Playwright Access

When you need the full power of Playwright, access it directly:

### Direct Object Access
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Get direct Playwright objects
    page = scraper.get_playwright_page()
    context = scraper.get_playwright_context()
    browser = scraper.get_playwright_browser()
    
    # Use any Playwright method
    viewport = page.viewport_size
    cookies = context.cookies()
    version = browser.version
```

### Safe Method Execution
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # Execute any Playwright method safely
    title = scraper.execute_playwright_method('page', 'title')
    cookies = scraper.execute_playwright_method('context', 'cookies')
    
    # Helper methods for common operations
    title = scraper.playwright_page_method('title')
    cookies = scraper.playwright_context_method('cookies')
```

---

## 🧪 Advanced Examples

### Form Handling
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com/form")
    
    # Fill complex form
    scraper.input("#username", "john_doe")
    scraper.input("#password", "secret123")
    scraper.select_option("#country", "US")
    scraper.check("#terms")
    scraper.upload_files("#avatar", ["profile.jpg"])
    
    # Submit and wait for response
    scraper.click("#submit")
    scraper.wait_for_url("**/success")
    
    message = scraper.get_text(".success-message")
    print(f"Success: {message}")
```

### Data Extraction Pipeline
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    base_url = "https://example.com"
    all_data = []
    
    for page_num in range(1, 6):  # Pages 1-5
        url = f"{base_url}/page/{page_num}"
        scraper.goto(url)
        
        # Handle potential errors gracefully
        scraper.click(".cookie-accept")  # Might not exist
        scraper.wait_for_selector(".content", timeout=5000)
        
        # Extract data
        items = scraper.get_all_text(".item-title")
        prices = scraper.get_all_text(".item-price")
        
        page_data = list(zip(items, prices))
        all_data.extend(page_data)
        
        print(f"Page {page_num}: {len(page_data)} items")
    
    print(f"Total items collected: {len(all_data)}")
```

### Multi-tab Scraping
```python
with SyncGAScrap() as scraper:
    # Main page
    scraper.goto("https://example.com/products")
    product_links = scraper.get_all_attributes("a.product", "href")
    
    # Open details in new tabs
    for i, link in enumerate(product_links[:5]):  # First 5 products
        page = scraper.new_page()
        scraper.goto(link, page=page)
        
        # Extract product details
        title = scraper.get_text("h1", page=page)
        price = scraper.get_text(".price", page=page)
        
        print(f"Product {i+1}: {title} - {price}")
        
        # Close tab
        scraper.close_page(page)
```

---

## 🔧 Configuration Options

### Browser Settings
```python
scraper = SyncGAScrap(
    browser_type="firefox",           # chromium, firefox, webkit
    headless=False,                   # Show/hide browser
    slow_mo=1000,                     # Slow down for debugging
    timeout=60000,                    # Global timeout
    viewport={"width": 1920, "height": 1080},
    user_agent="Custom User Agent",
    locale="en-US",
    timezone="America/New_York"
)
```

### Development Settings
```python
scraper = SyncGAScrap(
    sandbox_mode=True,                # Error-resilient mode
    debug=True,                       # Detailed logging
    record_video=True,                # Record sessions
    record_har=True,                  # Record network traffic
    downloads_path="./downloads"      # Download directory
)
```

---

## 🎯 Best Practices

### ✅ Recommended Patterns

```python
# Use context manager
with SyncGAScrap(sandbox_mode=True) as scraper:
    # Your scraping code here
    pass

# Enable sandbox mode for development
scraper = SyncGAScrap(sandbox_mode=True, debug=True)

# Use method chaining for readability
result = (scraper
          .goto(url)
          .wait_for_selector(".content")
          .get_text(".title"))

# Handle errors gracefully
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.click(".optional-popup-close")  # Won't crash if missing
    data = scraper.get_text(".main-content")  # Continues normally
```

### ⚠️ Things to Avoid

```python
# Don't mix async/await with sync interface
# ❌ Wrong
await scraper.goto("https://example.com")  # Don't use await

# ✅ Correct  
scraper.goto("https://example.com")  # No await needed

# Don't forget to handle optional elements
# ❌ Risky
scraper.click(".popup-close")  # Might crash if not found

# ✅ Safe
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.click(".popup-close")  # Safe in sandbox mode
```

---

<div align="center">

**🔄 Synchronous Interface: Web Scraping Made Simple!**

**Next:** [🎭 Playwright API](playwright-api.md) • [⚡ Hot Reload](hot-reload.md)

</div>
