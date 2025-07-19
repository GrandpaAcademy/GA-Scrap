# 🚀 Getting Started with GA-Scrap

<div align="center">

**Your journey to effortless web scraping starts here!**

</div>

---

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Basic Python knowledge** (variables, functions, loops)

---

## ⚡ Quick Installation

### 1. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

### 2. Verify Installation
```bash
# Test the installation
python -c "from ga_scrap import SyncGAScrap; print('✅ GA-Scrap installed successfully!')"
```

---

## 🎯 Your First Scraper

Let's create your first web scraper in just a few lines of code!

### Example 1: Extract Page Title
```python
from ga_scrap import SyncGAScrap

# Create and use scraper
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    print(f"Page title: {title}")
```

**Run it:**
```bash
python your_first_scraper.py
```

### Example 2: Extract Multiple Elements
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://quotes.toscrape.com")
    
    # Get all quotes
    quotes = scraper.get_all_text(".quote .text")
    authors = scraper.get_all_text(".quote .author")
    
    # Display results
    for quote, author in zip(quotes, authors):
        print(f'"{quote}" - {author}')
```

### Example 3: Take Screenshots
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    scraper.screenshot("my_first_screenshot.png")
    print("📸 Screenshot saved!")
```

---

## 🏖️ Enable Sandbox Mode (Recommended for Learning)

Sandbox mode prevents crashes during development - perfect for beginners!

```python
from ga_scrap import SyncGAScrap

# Enable sandbox mode - errors won't stop your scraper
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example.com")
    
    # These might fail, but scraper continues
    scraper.click("#might-not-exist")  # ❌ Error logged, continues
    scraper.input("#fake-input", "test")  # ❌ Error logged, continues
    
    # This will still work!
    scraper.screenshot("still_working.png")  # ✅ Works perfectly!
    print("✅ Scraper completed despite errors!")
```

---

## 🎨 Common Patterns

### Pattern 1: Navigation & Data Extraction
```python
with SyncGAScrap() as scraper:
    # Navigate to page
    scraper.goto("https://example.com")
    
    # Extract data
    title = scraper.get_text("h1")
    links = scraper.get_all_text("a")
    
    # Save results
    scraper.screenshot("page.png")
    print(f"Found {len(links)} links")
```

### Pattern 2: Form Interaction
```python
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com/search")
    
    # Fill form
    scraper.input("input[name='q']", "search term")
    scraper.click("button[type='submit']")
    
    # Wait and extract results
    scraper.wait_for_selector(".results")
    results = scraper.get_all_text(".result-title")
    print(f"Found {len(results)} results")
```

### Pattern 3: Multiple Pages
```python
with SyncGAScrap() as scraper:
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    
    all_data = []
    for url in urls:
        scraper.goto(url)
        data = scraper.get_text(".content")
        all_data.append(data)
        
    print(f"Scraped {len(all_data)} pages")
```

---

## 🛠️ Configuration Options

### Basic Configuration
```python
scraper = SyncGAScrap(
    headless=False,        # Show browser (great for learning)
    sandbox_mode=True,     # Error-resilient mode
    timeout=30000,         # 30 second timeout
    debug=True            # Detailed logging
)
```

### Mobile Device Emulation
```python
scraper = SyncGAScrap(
    device="iPhone 12",    # Emulate mobile device
    sandbox_mode=True
)
```

### Custom Browser Settings
```python
scraper = SyncGAScrap(
    browser_type="firefox",  # Use Firefox instead of Chrome
    viewport={"width": 1920, "height": 1080},
    user_agent="Custom User Agent"
)
```

---

## 🎯 Next Steps

### 📚 Learn More
- **[Basic Examples](examples.md)** - More practical examples
- **[Sandbox Mode](sandbox-mode.md)** - Master error-resilient development
- **[Sync Interface](sync-interface.md)** - Complete API reference

### 🧪 Try Advanced Features
- **[Playwright API](playwright-api.md)** - Access full Playwright power
- **[Hot Reload](hot-reload.md)** - Faster development workflow

### 🛠️ Build Projects
- **[Architecture](architecture.md)** - Understand how GA-Scrap works
- **[Contributing](contributing.md)** - Help improve GA-Scrap

---

## 🆘 Getting Help

### Common Issues

**❓ Browser doesn't open?**
```bash
# Reinstall Playwright browsers
playwright install
```

**❓ Import errors?**
```bash
# Check installation
pip list | grep playwright
python -c "import playwright; print('✅ Playwright OK')"
```

**❓ Permission errors?**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Resources
- 📖 **[Examples Directory](../examples/)** - Working code samples
- 🧪 **[Tests Directory](../tests/)** - Test examples
- 🐛 **[GitHub Issues](https://github.com/GrandpaAcademy/GA-Scrap/issues)** - Report problems
- 💬 **[Discussions](https://github.com/GrandpaAcademy/GA-Scrap/discussions)** - Ask questions

---

<div align="center">

**🎉 Congratulations! You're ready to start scraping!**

**Next:** [📖 Basic Examples](examples.md) • [🏖️ Sandbox Mode](sandbox-mode.md)

</div>
