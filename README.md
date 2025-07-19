# 🕷️ GA-Scrap

<div align="center">

**The Ultimate Web Scraping Library**  
*Playwright-powered • Developer-friendly • Production-ready*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green.svg)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

</div>

---

## ✨ What Makes GA-Scrap Special?

<table>
<tr>
<td width="50%">

### 🎯 **Simple & Powerful**
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    scraper.screenshot("page.png")
```

</td>
<td width="50%">

### 🏖️ **Error-Resilient Development**
```python
# Sandbox mode - errors don't crash!
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.click("#might-not-exist")  # Logs error, continues
    scraper.screenshot("still_works.png")  # Still works!
```

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap
pip install -r requirements.txt
playwright install
```

### Your First Scraper
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://quotes.toscrape.com")
    quotes = scraper.get_all_text(".quote .text")
    print(f"Found {len(quotes)} quotes!")
```

**That's it!** No `async`/`await`, no complex setup - just simple Python code.

### 📚 Learn More
**Comprehensive documentation and examples:**

<div align="center">

**[📖 Full Documentation](docs/web/index.html)** • **[🚀 Real-World Examples](docs/web/examples.html)** • **[🔧 API Reference](docs/web/api-reference.html)**

</div>

---

## 🎯 Core Features

<div align="center">

| Feature | Description | Status |
|---------|-------------|--------|
| 🔄 **Dual Interface** | Both sync and async APIs | ✅ |
| 🏖️ **Sandbox Mode** | Error-resilient development | ✅ |
| 🎭 **Full Playwright** | Complete A-Z feature access | ✅ |
| 📱 **Device Emulation** | Mobile, tablet, desktop | ✅ |
| 🌐 **Network Control** | Request/response interception | ✅ |
| 📸 **Media Capture** | Screenshots, PDFs, videos | ✅ |
| 🔧 **Developer Tools** | Hot reload, debugging | ✅ |
| 🎨 **Beautiful CLI** | Colorful command interface | ✅ |

</div>

---

## 📚 Complete Web Documentation

<div align="center">

🌐 **[Visit Our Interactive Documentation Site](docs/web/index.html)** 🌐

*Beautiful • Interactive • Complete*

[![Documentation](https://img.shields.io/badge/Docs-Interactive-brightgreen.svg)](docs/web/index.html)
[![Examples](https://img.shields.io/badge/Examples-Real%20World-orange.svg)](docs/web/examples.html)
[![API Reference](https://img.shields.io/badge/API-Complete-blue.svg)](docs/web/api-reference.html)

</div>

### 🎯 **Choose Your Learning Path**

<table>
<tr>
<td width="33%" align="center">

### 👶 **Beginner**
**New to web scraping?**

📖 [**Getting Started**](docs/web/getting-started.html)
🎯 [**Basic Examples**](docs/web/examples.html)
🔧 [**Installation Guide**](docs/web/installation.html)

</td>
<td width="33%" align="center">

### 🧪 **Developer**
**Building scrapers?**

🏖️ [**Sandbox Mode**](docs/web/sandbox-mode.html)
🔄 [**Sync Interface**](docs/web/sync-interface.html)
⚡ [**Hot Reload**](docs/web/hot-reload.html)

</td>
<td width="33%" align="center">

### 🚀 **Advanced**
**Need full control?**

🎭 [**Playwright API**](docs/web/playwright-api.html)
🔧 [**Architecture**](docs/web/architecture.html)
🤝 [**Contributing**](docs/web/contributing.html)

</td>
</tr>
</table>

---

## 🎨 Interface Options

### 🔄 Synchronous (Recommended)
*Perfect for beginners and most use cases*

```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    data = scraper.get_text(".content")
    scraper.screenshot("result.png")
```

### ⚡ Asynchronous
*For advanced users and high-performance scenarios*

```python
import asyncio
from ga_scrap import GAScrap

async def scrape():
    async with GAScrap() as scraper:
        await scraper.goto("https://example.com")
        data = await scraper.get_text(".content")
        await scraper.screenshot("result.png")

asyncio.run(scrape())
```

---

## 🏖️ Sandbox Mode

**The game-changer for development!**

```python
# Traditional scraping - one error stops everything
scraper.click("#button")  # ❌ Element not found → CRASH!

# GA-Scrap sandbox mode - errors are handled gracefully
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.click("#button")  # ❌ Error logged, execution continues
    scraper.screenshot("debug.png")  # ✅ Still works perfectly!
```

**Benefits:**
- 🛡️ **Never crashes** - Browser stays active during errors
- 📝 **Detailed logging** - Know exactly what went wrong
- 🔄 **Instant recovery** - Fix and continue immediately
- 🧪 **Perfect for testing** - Try different approaches safely

---

## 🎭 Complete Playwright Access

**Every Playwright feature from A-Z is available:**

```python
# High-level GA-Scrap methods
scraper.goto("https://example.com")
scraper.screenshot("page.png")

# Direct Playwright access when needed
page = scraper.get_playwright_page()
await page.evaluate("document.body.style.background = 'red'")

# Safe method execution with sandbox protection
result = scraper.execute_playwright_method('page', 'title')
```

<details>
<summary><strong>🔤 View A-Z Feature List</strong></summary>

- **A**ccessibility testing
- **B**rowser management  
- **C**ookies & context
- **D**ownloads handling
- **E**valuate JavaScript
- **F**orm interactions
- **G**eolocation control
- **H**over & interactions
- **I**njection (CSS/JS)
- **J**avaScript execution
- **K**eyboard simulation
- **L**ocators & selectors
- **M**ouse operations
- **N**etwork monitoring
- **O**ffline mode
- **P**DF generation
- **Q**uery selectors
- **R**ecording (video/HAR)
- **S**creenshots
- **T**ouch simulation
- **U**pload files
- **V**iewport control
- **W**aiting strategies
- **X**Path selectors
- **Y**ielding control
- **Z**one/timezone settings

</details>

---

## 🛠️ CLI Tools

```bash
# Quick scraping
ga-scrap quick "https://example.com" "h1"

# Create new project
ga-scrap new my-scraper

# Development with hot reload
ga-scrap dev

# Run with auto-restart
ga-scrap run script.py
```

---

## 🎯 Examples

<details>
<summary><strong>📰 News Scraper</strong></summary>

```python
with SyncGAScrap() as scraper:
    scraper.goto("https://news.ycombinator.com")
    
    titles = scraper.get_all_text(".titleline > a")
    scores = scraper.get_all_text(".score")
    
    for title, score in zip(titles, scores):
        print(f"{score}: {title}")
```

</details>

<details>
<summary><strong>🛒 E-commerce Scraper</strong></summary>

```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example-shop.com")
    
    # Handle potential popups gracefully
    scraper.click(".popup-close")  # Won't crash if not found
    
    products = scraper.get_all_text(".product-name")
    prices = scraper.get_all_text(".product-price")
    
    for product, price in zip(products, prices):
        print(f"{product}: {price}")
```

</details>

<details>
<summary><strong>📱 Mobile Scraping</strong></summary>

```python
with SyncGAScrap(device="iPhone 12") as scraper:
    scraper.goto("https://mobile-site.com")
    scraper.simulate_touch(100, 200)
    scraper.screenshot("mobile-view.png")
```

</details>

---

## 🤝 Contributing

We love contributions! Check out our [Contributing Guide](docs/web/contributing.html) to get started.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ by [Grandpa Academy](https://github.com/GrandpaAcademy)**

[⭐ Star us on GitHub](https://github.com/GrandpaAcademy/GA-Scrap) • [📖 Read the Docs](docs/web/index.html) • [🚀 See Examples](docs/web/examples.html) • [🐛 Report Issues](https://github.com/GrandpaAcademy/GA-Scrap/issues)

</div>
