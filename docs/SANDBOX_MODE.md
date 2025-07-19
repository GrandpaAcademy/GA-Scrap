# 🏖️ GA-Scrap Sandbox Mode

## 🎯 Perfect for Development & Testing

Sandbox mode is a special error handling mode that **never shuts down the browser** when errors occur. Instead, it logs detailed error messages and continues running, making it perfect for development, testing, and debugging.

## 🚀 Quick Start

```python
from ga_scrap import SyncGAScrap

# Enable sandbox mode
scraper = SyncGAScrap(sandbox_mode=True)

with scraper:
    # These operations might fail, but browser stays active!
    scraper.goto("https://example.com")
    scraper.click("#might-not-exist")  # Error logged, continues
    scraper.input("#fake-input", "text")  # Error logged, continues
    scraper.goto("invalid://url")  # Error logged, continues
    
    # Recovery - valid operations still work
    scraper.goto("https://httpbin.org/html")  # Works fine!
    scraper.screenshot("recovered.png")  # Works fine!
```

## 🆚 Sandbox vs Normal Mode

### 🏖️ Sandbox Mode (Development)
```python
scraper = SyncGAScrap(sandbox_mode=True)

with scraper:
    scraper.goto("https://example.com")
    scraper.click("#non-existent")  # ❌ Error logged, continues
    scraper.screenshot("still_works.png")  # ✅ Still works!
    # Browser remains active for debugging
```

**Output:**
```
❌ Error in click: Page.click: Timeout 30000ms exceeded.
🏖️ Sandbox mode: Continuing despite error in click
💡 Fix the issue and try again. Browser remains active.
📸 Screenshot saved: still_works.png
```

### 🚨 Normal Mode (Production)
```python
scraper = SyncGAScrap(sandbox_mode=False)  # Default

with scraper:
    scraper.goto("https://example.com")
    scraper.click("#non-existent")  # ❌ Raises exception, stops
    scraper.screenshot("never_reached.png")  # Never executed
```

**Output:**
```
❌ Error in click: Page.click: Timeout 30000ms exceeded.
Exception: Page.click: Timeout 30000ms exceeded.
# Script stops here
```

## 🎯 Use Cases

### 🧪 Development & Testing
```python
# Perfect for trying different selectors
scraper = SyncGAScrap(sandbox_mode=True, debug=True)

with scraper:
    scraper.goto("https://example.com")
    
    # Try different selectors until one works
    scraper.click("#button1")      # Might fail
    scraper.click(".button-class") # Might fail  
    scraper.click("button")        # Might work!
    
    # Browser stays open for inspection
```

### 🔍 Debugging & Exploration
```python
# Explore a website without crashes
scraper = SyncGAScrap(sandbox_mode=True)

with scraper:
    scraper.goto("https://complex-site.com")
    
    # Try various interactions
    scraper.click("#menu")
    scraper.click("#submenu")
    scraper.input("#search", "test")
    scraper.click("#search-btn")
    
    # Even if some fail, you can see what works
    scraper.pause("Check the page state...")
```

### 🎓 Learning & Experimentation
```python
# Great for learning web scraping
scraper = SyncGAScrap(sandbox_mode=True)

with scraper:
    scraper.goto("https://practice-site.com")
    
    # Experiment with different approaches
    scraper.click("button")           # Try tag name
    scraper.click(".btn")            # Try class
    scraper.click("#submit")         # Try ID
    scraper.click("[type='submit']") # Try attribute
    
    # See which selectors work without crashes
```

## 🔧 Configuration

### Basic Sandbox Mode
```python
scraper = SyncGAScrap(sandbox_mode=True)
```

### Sandbox Mode with Debug Logging
```python
scraper = SyncGAScrap(
    sandbox_mode=True,
    debug=True,  # Detailed error messages
    headless=False  # Visible browser for inspection
)
```

### Sandbox Mode with Custom Timeout
```python
scraper = SyncGAScrap(
    sandbox_mode=True,
    timeout=5000,  # Shorter timeout for faster feedback
    slow_mo=500    # Slow down for better observation
)
```

## 📊 Error Handling Details

### What Errors Are Handled?
- ❌ **Element not found** - Invalid selectors
- ❌ **Navigation failures** - Invalid URLs, network errors
- ❌ **Timeout errors** - Elements that don't appear
- ❌ **Interaction failures** - Elements that can't be clicked/filled
- ❌ **JavaScript errors** - Script execution failures
- ❌ **Network errors** - Connection issues

### Error Message Format
```
❌ Error in [operation]: [detailed error message]
🏖️ Sandbox mode: Continuing despite error in [operation]
💡 Fix the issue and try again. Browser remains active.
```

### Recovery Behavior
- ✅ Browser stays open and functional
- ✅ Subsequent operations continue normally
- ✅ Error details logged for debugging
- ✅ No data loss or state corruption

## 🎮 Interactive Development

### Live Development Workflow
```python
scraper = SyncGAScrap(sandbox_mode=True, debug=True)

with scraper:
    scraper.goto("https://target-site.com")
    
    # Try operations, fix errors, try again
    while True:
        try:
            operation = input("Enter operation (or 'quit'): ")
            if operation == 'quit':
                break
            
            # Execute operation
            if operation.startswith('click:'):
                selector = operation[6:]
                scraper.click(selector)
            elif operation.startswith('goto:'):
                url = operation[5:]
                scraper.goto(url)
            # ... more operations
            
        except KeyboardInterrupt:
            break
    
    # Browser stays open for final inspection
    scraper.pause("Final inspection...")
```

## 🧪 Testing Integration

### Unit Testing with Sandbox Mode
```python
import unittest
from ga_scrap import SyncGAScrap

class TestWebScraping(unittest.TestCase):
    def setUp(self):
        self.scraper = SyncGAScrap(
            sandbox_mode=True,  # Don't fail tests on errors
            headless=True
        )
        self.scraper.start()
    
    def test_navigation(self):
        # Test won't fail even if navigation fails
        self.scraper.goto("https://test-site.com")
        # Continue with other tests...
    
    def tearDown(self):
        self.scraper.stop()
```

## 🎯 Best Practices

### 1. Use for Development
```python
# Development
scraper = SyncGAScrap(sandbox_mode=True, debug=True)
```

### 2. Disable for Production
```python
# Production
scraper = SyncGAScrap(sandbox_mode=False)  # Default
```

### 3. Combine with Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
scraper = SyncGAScrap(sandbox_mode=True, debug=True)

# All errors will be logged but won't stop execution
```

### 4. Use Shorter Timeouts for Faster Feedback
```python
scraper = SyncGAScrap(
    sandbox_mode=True,
    timeout=5000  # 5 seconds instead of 30
)
```

## 🎉 Benefits

### For Developers
- ✅ **No crashes** during development
- ✅ **Faster iteration** - fix and retry immediately
- ✅ **Better debugging** - browser stays open for inspection
- ✅ **Error visibility** - see exactly what went wrong

### For Testers
- ✅ **Robust testing** - tests don't fail on minor issues
- ✅ **Error collection** - gather all errors in one run
- ✅ **State preservation** - browser state maintained
- ✅ **Recovery testing** - verify error recovery

### For Learners
- ✅ **Forgiving environment** - mistakes don't crash everything
- ✅ **Immediate feedback** - see results of changes instantly
- ✅ **Exploration friendly** - try different approaches safely
- ✅ **Visual debugging** - see what's happening in browser

## 🚀 Get Started

```python
from ga_scrap import SyncGAScrap

# Enable sandbox mode for development
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://your-target-site.com")
    
    # Try operations without fear of crashes
    scraper.click("#button")
    scraper.input("#field", "value")
    scraper.screenshot("debug.png")
    
    # Browser stays active for debugging!
```

**Perfect for development, testing, and learning web scraping!** 🏖️
