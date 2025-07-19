# GA-Scrap Synchronous Interface

## 🚀 No More async/await!

GA-Scrap now provides a **synchronous wrapper** that eliminates the need for `async`/`await` syntax, making web scraping as simple as regular Python code!

## 📖 Quick Start

### Basic Usage

```python
from ga_scrap import SyncGAScrap

# Create scraper - no async needed!
scraper = SyncGAScrap()

# Start browser
scraper.start()

# Navigate and scrape - simple as that!
scraper.goto("https://example.com")
title = scraper.get_text("h1")
scraper.screenshot("page.png")

# Stop browser
scraper.stop()

print(f"Title: {title}")
```

### Context Manager (Recommended)

```python
from ga_scrap import SyncGAScrap

# Automatic start/stop with context manager
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    scraper.screenshot("page.png")
    print(f"Title: {title}")
# Browser automatically closed
```

### Even Simpler Function Interface

```python
from ga_scrap import create_scraper

# One-line scraper creation
scraper = create_scraper(headless=False)

with scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    print(f"Title: {title}")
```

## 🔗 Method Chaining

Chain multiple operations for fluent interface:

```python
with SyncGAScrap() as scraper:
    (scraper
     .goto("https://example.com")
     .scroll_to_bottom()
     .screenshot("bottom.png")
     .scroll_to_top()
     .screenshot("top.png"))
```

## 📄 Multiple Pages

```python
with SyncGAScrap() as scraper:
    # Main page
    scraper.goto("https://example.com")
    
    # New page
    page2 = scraper.new_page()
    scraper.goto("https://another-site.com", page=page2)
    
    # Take screenshots of both
    scraper.screenshot("page1.png")
    scraper.screenshot("page2.png", page=page2)
    
    # Clean up extra pages
    scraper.close_all_pages()
```

## 🎯 Common Operations

### Form Interaction
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com/form")
    scraper.input("input[name='username']", "john_doe")
    scraper.input("input[name='password']", "secret123")
    scraper.click("button[type='submit']")
    scraper.screenshot("form_submitted.png")
```

### Scrolling
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Scroll operations
    scraper.scroll_to_bottom()
    scraper.scroll_to_top()
    scraper.scroll_to_element(".target-element")
    
    # Infinite scroll
    scraper.infinite_scroll(max_scrolls=5)
```

### Data Extraction
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://news-site.com")
    
    # Single element
    headline = scraper.get_text("h1")
    
    # Multiple elements
    article_titles = scraper.get_texts(".article-title")
    
    print(f"Headline: {headline}")
    print(f"Articles: {len(article_titles)}")
```

## 📱 Mobile Emulation

```python
with SyncGAScrap() as scraper:
    # Emulate iPhone
    scraper.emulate_device("iPhone 12")
    scraper.goto("https://mobile-site.com")
    scraper.screenshot("mobile_view.png")
```

## 🌟 Advanced Features

### JavaScript Execution
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Execute custom JavaScript
    page_info = scraper.execute_script("""
        () => ({
            title: document.title,
            url: window.location.href,
            links: document.querySelectorAll('a').length
        })
    """)
    
    print(f"Page info: {page_info}")
```

### CSS Injection
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Inject custom styles
    scraper.inject_css(css_content="""
        body { 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
            border: 5px solid gold !important;
        }
    """)
    
    scraper.screenshot("styled_page.png")
```

### File Operations
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    
    # Save as PDF
    pdf_path = scraper.save_pdf("page.pdf", {
        "format": "A4",
        "print_background": True
    })
    
    # Upload files
    scraper.upload_files("input[type='file']", ["file1.txt", "file2.txt"])
```

### Cookie Management
```python
with SyncGAScrap() as scraper:
    # Add cookies
    scraper.add_cookies([{
        "name": "session_id",
        "value": "abc123",
        "domain": "example.com",
        "path": "/"
    }])
    
    scraper.goto("https://example.com")
    
    # Get cookies
    cookies = scraper.get_cookies()
    print(f"Total cookies: {len(cookies)}")
```

### Network Control
```python
with SyncGAScrap() as scraper:
    # Block images and ads for faster loading
    scraper.block_requests(
        resource_types=["image", "stylesheet"],
        url_patterns=[".*ads.*", ".*analytics.*"]
    )
    
    scraper.goto("https://example.com")
    scraper.wait_for_network_idle()
```

## 🎛️ Configuration Options

```python
scraper = SyncGAScrap(
    headless=False,           # Visible browser
    browser_type="chromium",  # Browser type
    viewport={"width": 1920, "height": 1080},
    user_agent="Custom Agent",
    timeout=30000,           # 30 seconds
    slow_mo=100,             # Slow down for debugging
    proxy={"server": "http://proxy:8080"},
    downloads_path="./downloads",
    record_video=True,       # Record session
    record_har=True,         # Record network activity
    permissions=["geolocation", "camera"],
    locale="en-US",
    timezone_id="America/New_York",
    geolocation={"latitude": 40.7128, "longitude": -74.0060}
)
```

## 🔍 Monitoring & Debugging

```python
with SyncGAScrap(debug=True) as scraper:
    scraper.goto("https://example.com")
    
    # Access captured data
    print(f"Requests: {len(scraper.requests)}")
    print(f"Responses: {len(scraper.responses)}")
    print(f"Console messages: {len(scraper.console_messages)}")
    print(f"Downloads: {len(scraper.downloads)}")
    
    # Manual logging
    scraper.log("Custom log message", "info")
    
    # Pause for inspection
    scraper.pause("Check the page and press Enter...")
```

## 🆚 Comparison: Async vs Sync

### Before (Async)
```python
import asyncio
from ga_scrap import GAScrap

async def scrape():
    scraper = GAScrap()
    await scraper.start()
    await scraper.goto("https://example.com")
    title = await scraper.get_text("h1")
    await scraper.screenshot("page.png")
    await scraper.stop()
    return title

# Need to run with asyncio
result = asyncio.run(scrape())
```

### After (Sync)
```python
from ga_scrap import SyncGAScrap

# Simple, clean code - no async needed!
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    scraper.screenshot("page.png")

print(f"Title: {title}")
```

## 🎉 Benefits

- ✅ **No async/await** - Write simple, readable code
- ✅ **Method chaining** - Fluent interface
- ✅ **Context manager** - Automatic cleanup
- ✅ **All features available** - Every Playwright capability
- ✅ **Thread-safe** - Handles async operations internally
- ✅ **Easy debugging** - Visible browser by default
- ✅ **Familiar syntax** - Like regular Python libraries

## 🚀 Get Started

```bash
# Install GA-Scrap
pip install -e .

# Install Playwright browsers
playwright install

# Start scraping!
python your_scraper.py
```

The synchronous interface makes GA-Scrap accessible to everyone, regardless of async/await experience!
