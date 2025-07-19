# 🔧 Architecture

<div align="center">

**Understanding GA-Scrap's Design**  
*How everything works under the hood*

</div>

---

## 🎯 Overview

GA-Scrap is built with a modular architecture that provides multiple interfaces while maintaining a powerful core. The design prioritizes simplicity for users while offering complete flexibility for advanced use cases.

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                     │
├─────────────────────┬───────────────────────────────────┤
│   Synchronous API   │        Asynchronous API          │
│   (SyncGAScrap)     │         (GAScrap)                │
├─────────────────────┼───────────────────────────────────┤
│              Synchronous Translator                    │
│                (translator.py)                         │
├─────────────────────────────────────────────────────────┤
│                   Core Engine                          │
│                   (core.py)                            │
├─────────────────────────────────────────────────────────┤
│                Playwright Engine                       │
│            (Browser Automation)                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Core Components

### 1. Core Engine (`core.py`)
*The heart of GA-Scrap*

```python
class GAScrap:
    """
    Core asynchronous scraping engine
    - Manages Playwright lifecycle
    - Handles browser/context/page operations
    - Implements sandbox mode
    - Provides comprehensive feature set
    """
```

**Responsibilities:**
- 🌐 **Browser Management** - Launch, configure, and control browsers
- 📄 **Page Operations** - Navigation, interaction, data extraction
- 🛡️ **Error Handling** - Sandbox mode and safe execution
- 🎭 **Playwright Integration** - Complete API access
- 📊 **Event Monitoring** - Network, console, and page events

### 2. Synchronous Translator (`translator.py`)
*Makes async code synchronous*

```python
class SyncGAScrap:
    """
    Synchronous wrapper around GAScrap
    - Eliminates async/await complexity
    - Provides method chaining
    - Maintains full feature parity
    """
```

**Key Features:**
- 🔄 **Async-to-Sync Translation** - Automatic async handling
- 🔗 **Method Chaining** - Fluent interface design
- 🧵 **Thread Management** - Background event loop
- 🛡️ **Error Propagation** - Maintains sandbox mode benefits

### 3. Advanced Features (`advanced_features.py`)
*Extended functionality*

```python
class AdvancedFeatures:
    """
    Advanced Playwright features
    - Device emulation
    - Network control
    - Performance monitoring
    - Accessibility testing
    """
```

### 4. CLI Interface (`cli.py`)
*Command-line tools*

```python
class CLI:
    """
    Command-line interface
    - Quick scraping commands
    - Project management
    - Hot reload functionality
    """
```

---

## 🔄 Data Flow

### Synchronous Interface Flow
```
User Code
    ↓
SyncGAScrap Method Call
    ↓
Translator._run_async()
    ↓
Background Event Loop
    ↓
GAScrap Async Method
    ↓
Playwright API
    ↓
Browser Action
    ↓
Result (sync return)
```

### Asynchronous Interface Flow
```
User Code (async)
    ↓
GAScrap Async Method
    ↓
Playwright API
    ↓
Browser Action
    ↓
Result (async return)
```

---

## 🛡️ Sandbox Mode Architecture

### Error Handling Pipeline
```python
def _safe_execute_async(self, operation_name, async_func):
    """
    Safe execution wrapper for sandbox mode
    1. Try to execute operation
    2. If error occurs and sandbox_mode=True:
       - Log detailed error message
       - Continue execution
       - Return None or default value
    3. If error occurs and sandbox_mode=False:
       - Raise exception normally
    """
```

### Error Flow in Sandbox Mode
```
Operation Called
    ↓
Try Execution
    ↓
Error Occurs? ──No──→ Return Result
    ↓ Yes
Sandbox Mode? ──No──→ Raise Exception
    ↓ Yes
Log Error Details
    ↓
Continue Execution
    ↓
Return Safe Default
```

---

## 🧵 Threading Model

### Synchronous Interface Threading
```python
class SyncGAScrap:
    def __init__(self):
        # Create dedicated event loop for async operations
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def _run_async(self, coro):
        # Execute async code in background thread
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
```

**Benefits:**
- 🔄 **No Blocking** - Main thread remains responsive
- 🧵 **Isolated Execution** - Async operations in dedicated thread
- 🛡️ **Error Isolation** - Exceptions properly propagated
- 🔧 **Resource Management** - Clean shutdown and cleanup

---

## 📦 Module Structure

```
ga_scrap/
├── __init__.py              # Public API exports
├── core.py                  # Core GAScrap class
├── translator.py            # Synchronous wrapper
├── advanced_features.py     # Extended functionality
├── comprehensive_features.py # Complete feature set
├── simple.py               # Simplified interface
├── app_manager.py          # Project management
├── hot_reload.py           # Development tools
└── cli.py                  # Command-line interface
```

### Import Structure
```python
# __init__.py
from .core import GAScrap
from .translator import SyncGAScrap
from .simple import SimpleScraper
from .app_manager import AppManager

__all__ = ['GAScrap', 'SyncGAScrap', 'SimpleScraper', 'AppManager']
```

---

## 🎭 Playwright Integration

### Direct Access Architecture
```python
class GAScrap:
    def get_playwright_page(self):
        """Direct access to Playwright Page object"""
        return self.page
    
    def get_playwright_context(self):
        """Direct access to Playwright BrowserContext"""
        return self.context
    
    def execute_playwright_method(self, obj_path, method_name, *args, **kwargs):
        """Safe execution of any Playwright method"""
        # Get object (page, context, browser, playwright)
        # Execute method with sandbox protection
        # Return result or handle error gracefully
```

### Feature Coverage Strategy
```python
# High-level methods for common operations
def click(self, selector): ...
def get_text(self, selector): ...
def screenshot(self, path): ...

# Direct access for advanced operations
page = scraper.get_playwright_page()
await page.evaluate("complex_javascript()")

# Safe execution for any Playwright method
result = scraper.execute_playwright_method('page', 'accessibility.snapshot')
```

---

## 🔧 Configuration System

### Configuration Hierarchy
```
1. Default Values (in code)
    ↓
2. Configuration Files (config.yaml)
    ↓
3. Environment Variables
    ↓
4. Constructor Arguments
    ↓
5. Method Parameters
```

### Configuration Classes
```python
@dataclass
class BrowserConfig:
    headless: bool = False
    browser_type: str = "chromium"
    timeout: int = 30000
    viewport: Dict = field(default_factory=lambda: {"width": 1280, "height": 720})

@dataclass
class ScrapingConfig:
    sandbox_mode: bool = False
    debug: bool = False
    max_retries: int = 3
    delay_between_requests: int = 1000
```

---

## 🚀 Performance Optimizations

### Lazy Loading
```python
class GAScrap:
    def __init__(self):
        # Core components loaded immediately
        self.playwright = None
        self.browser = None
        
        # Advanced features loaded on demand
        self._advanced_features = None
    
    @property
    def advanced_features(self):
        if self._advanced_features is None:
            self._advanced_features = AdvancedFeatures(self)
        return self._advanced_features
```

### Resource Management
```python
async def __aenter__(self):
    """Async context manager - automatic resource management"""
    return await self.start()

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Cleanup resources automatically"""
    await self.stop()
```

### Connection Pooling
```python
class BrowserPool:
    """Reuse browser instances for better performance"""
    def __init__(self, max_browsers=3):
        self.pool = []
        self.max_browsers = max_browsers
    
    async def get_browser(self):
        # Return existing browser or create new one
        pass
```

---

## 🧪 Testing Architecture

### Test Structure
```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_core.py
│   ├── test_translator.py
│   └── test_sandbox.py
├── integration/            # Integration tests
│   ├── test_full_workflow.py
│   └── test_playwright_integration.py
├── e2e/                   # End-to-end tests
│   └── test_real_websites.py
└── fixtures/              # Test data and utilities
    ├── mock_pages.html
    └── test_helpers.py
```

### Test Categories
```python
# Unit Tests - Fast, isolated
def test_sandbox_mode_error_handling():
    # Test sandbox mode logic without browser

# Integration Tests - Medium speed, multiple components
def test_sync_async_parity():
    # Test that sync and async interfaces produce same results

# E2E Tests - Slow, full system
def test_real_website_scraping():
    # Test against real websites
```

---

## 🔮 Extension Points

### Custom Features
```python
class CustomFeatures:
    """Add your own features to GA-Scrap"""
    def __init__(self, scraper):
        self.scraper = scraper
    
    def custom_method(self):
        # Your custom functionality
        pass

# Usage
scraper.add_extension(CustomFeatures)
```

### Plugin System
```python
class PluginManager:
    """Manage GA-Scrap plugins"""
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin_class):
        self.plugins.append(plugin_class)
    
    def apply_plugins(self, scraper):
        for plugin_class in self.plugins:
            plugin = plugin_class(scraper)
            scraper.add_extension(plugin)
```

---

## 🎯 Design Principles

### 1. **Simplicity First**
- Default behavior should be intuitive
- Complex features available but not required
- Clear, readable API design

### 2. **Progressive Disclosure**
- Basic features easily accessible
- Advanced features available when needed
- Multiple levels of abstraction

### 3. **Error Resilience**
- Sandbox mode for development
- Graceful degradation
- Detailed error messages

### 4. **Performance Awareness**
- Lazy loading of heavy components
- Resource pooling where beneficial
- Efficient async/sync translation

### 5. **Extensibility**
- Plugin system for custom features
- Direct Playwright access for power users
- Clear extension points

---

<div align="center">

**🔧 Understanding the Architecture Helps You Use GA-Scrap Better!**

**Next:** [🤝 Contributing](contributing.md) • [🚀 Getting Started](getting-started.md)

</div>
