# 🏖️ Sandbox Mode

<div align="center">

**Error-Resilient Development Made Easy**  
*Never crash again during development!*

</div>

---

## 🎯 What is Sandbox Mode?

Sandbox mode is GA-Scrap's **game-changing feature** that makes web scraping development completely crash-proof. When enabled, errors are logged and handled gracefully instead of stopping your scraper.

### 🆚 Traditional vs Sandbox Mode

<table>
<tr>
<td width="50%">

### 🚨 **Traditional Scraping**
```python
scraper.goto("https://example.com")
scraper.click("#button")  # ❌ Element not found
# 💥 CRASH! Script stops here
scraper.screenshot("never_reached.png")
```

**Result:** Script crashes, browser closes, you lose progress.

</td>
<td width="50%">

### 🏖️ **Sandbox Mode**
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    scraper.click("#button")  # ❌ Error logged, continues
    scraper.screenshot("still_works.png")  # ✅ Works!
```

**Result:** Error logged, script continues, browser stays open.

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Enable Sandbox Mode
```python
from ga_scrap import SyncGAScrap

# Enable sandbox mode - that's it!
with SyncGAScrap(sandbox_mode=True) as scraper:
    # Your scraping code here
    pass
```

### Both Interfaces Support Sandbox Mode
```python
# Synchronous interface
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")

# Asynchronous interface  
async with GAScrap(sandbox_mode=True) as scraper:
    await scraper.goto("https://example.com")
```

---

## 🛡️ Error Handling Examples

### Example 1: Element Not Found
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # These selectors might not exist
    scraper.click("#non-existent-button")
    scraper.input("#fake-input", "test")
    scraper.hover("#missing-element")
    
    # This still works perfectly!
    scraper.screenshot("debug.png")
    title = scraper.get_text("h1")  # This works
    print(f"Page title: {title}")
```

**Console Output:**
```
❌ Error in click: Page.click: Timeout 30000ms exceeded.
🏖️ Sandbox mode: Continuing despite error in click
💡 Fix the issue and try again. Browser remains active.

❌ Error in type_text: Page.fill: Timeout 30000ms exceeded.
🏖️ Sandbox mode: Continuing despite error in type_text
💡 Fix the issue and try again. Browser remains active.

📸 Screenshot saved: debug.png
Page title: Example Domain
```

### Example 2: Network Errors
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    # Valid page
    scraper.goto("https://httpbin.org/html")
    scraper.screenshot("valid_page.png")
    
    # Invalid URLs - won't crash!
    scraper.goto("https://definitely-not-a-real-site-12345.com")
    scraper.goto("invalid://protocol")
    
    # Recovery - back to valid page
    scraper.goto("https://httpbin.org/json")
    scraper.screenshot("recovered.png")
    print("✅ Successfully recovered from errors!")
```

### Example 3: Timeout Errors
```python
with SyncGAScrap(sandbox_mode=True, timeout=1000) as scraper:  # 1 second timeout
    scraper.goto("https://httpbin.org/html")
    
    # These will timeout quickly but won't crash
    scraper.click("#definitely-does-not-exist")
    scraper.wait_for_selector("#also-does-not-exist")
    
    # Immediate recovery
    scraper.screenshot("after_timeouts.png")
    print("✅ Timeouts handled gracefully!")
```

---

## 🧪 Development Workflow

### Perfect for Iterative Development
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # Try different selectors until you find the right one
    scraper.click("#submit-btn")        # Might not work
    scraper.click(".submit-button")     # Might not work  
    scraper.click("input[type=submit]") # This works!
    
    # Browser stays open for inspection
    scraper.screenshot("final_state.png")
```

### Debugging Unknown Websites
```python
with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
    scraper.goto("https://unknown-website.com")
    
    # Explore the page structure safely
    scraper.click(".popup-close")      # Handle popups
    scraper.click(".cookie-accept")    # Handle cookies
    scraper.click(".newsletter-close") # Handle newsletters
    
    # Extract data once page is clean
    data = scraper.get_all_text(".content")
    print(f"Found {len(data)} content elements")
```

---

## ⚙️ Configuration Options

### Sandbox Mode Settings
```python
scraper = SyncGAScrap(
    sandbox_mode=True,     # Enable sandbox mode
    timeout=5000,          # Faster timeouts for development
    debug=True,            # Detailed error logging
    headless=False         # Keep browser visible for debugging
)
```

### Production vs Development
```python
import os

# Use environment variable to control mode
is_development = os.getenv("ENVIRONMENT") == "development"

scraper = SyncGAScrap(
    sandbox_mode=is_development,  # Sandbox only in development
    headless=not is_development,  # Visible only in development
    debug=is_development          # Debug only in development
)
```

---

## 🎯 Best Practices

### ✅ When to Use Sandbox Mode

**Perfect for:**
- 🧪 **Development & Testing** - Try different approaches safely
- 🔍 **Exploring Unknown Sites** - Handle unexpected page structures
- 🎓 **Learning Web Scraping** - Experiment without fear of crashes
- 🐛 **Debugging Issues** - Keep browser open for inspection

### ⚠️ When to Disable Sandbox Mode

**Use normal mode for:**
- 🚀 **Production Deployments** - Fail fast on real errors
- 📊 **Data Quality Assurance** - Ensure all data is captured
- 🔄 **Automated Pipelines** - Stop on critical failures

### 🛠️ Development Workflow
```python
# Development phase - sandbox mode enabled
with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
    # Develop and test your scraper
    pass

# Production phase - sandbox mode disabled  
with SyncGAScrap(sandbox_mode=False) as scraper:
    # Run your proven scraper
    pass
```

---

## 🔧 Advanced Features

### Error Recovery Patterns
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # Try multiple strategies
    success = False
    
    # Strategy 1: Try ID selector
    if scraper.click("#submit-button"):
        success = True
    
    # Strategy 2: Try class selector
    if not success and scraper.click(".submit-btn"):
        success = True
        
    # Strategy 3: Try text content
    if not success and scraper.click_text("Submit"):
        success = True
        
    if success:
        print("✅ Successfully clicked submit button!")
    else:
        print("❌ Could not find submit button")
```

### Conditional Error Handling
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # Handle optional elements gracefully
    scraper.click(".cookie-banner .accept")  # Might not exist
    scraper.click(".popup .close")           # Might not exist
    scraper.click(".newsletter .dismiss")    # Might not exist
    
    # Continue with main scraping logic
    data = scraper.get_text(".main-content")
    print(f"Content: {data}")
```

---

## 📊 Error Types Handled

Sandbox mode gracefully handles **all types of errors**:

| Error Type | Example | Sandbox Behavior |
|------------|---------|------------------|
| **Element Not Found** | `click("#missing")` | ❌ Logged, ✅ Continues |
| **Timeout Errors** | `wait_for_selector("#slow")` | ❌ Logged, ✅ Continues |
| **Network Errors** | `goto("invalid://url")` | ❌ Logged, ✅ Continues |
| **JavaScript Errors** | `execute_script("invalid.js")` | ❌ Logged, ✅ Continues |
| **Navigation Failures** | `goto("https://404-site.com")` | ❌ Logged, ✅ Continues |

---

## 🎉 Success Stories

### Before Sandbox Mode
```
❌ Spent hours restarting scrapers after crashes
❌ Lost progress when single element wasn't found  
❌ Difficult to debug unknown website structures
❌ Fear of trying new selectors or approaches
```

### After Sandbox Mode
```
✅ Continuous development without interruptions
✅ Browser stays open for immediate debugging
✅ Safe experimentation with different strategies
✅ Faster iteration and learning cycles
```

---

<div align="center">

**🏖️ Sandbox Mode: Making Web Scraping Development Enjoyable!**

**Next:** [🔄 Sync Interface](sync-interface.md) • [🎭 Playwright API](playwright-api.md)

</div>
