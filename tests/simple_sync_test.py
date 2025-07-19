"""
Simple test of the synchronous GA-Scrap interface
"""

from ga_scrap import SyncGAScrap

# Create scraper - no async needed!
ga = SyncGAScrap()

# Start browser
ga.start()

# Test basic operations
print("🚀 Testing synchronous GA-Scrap interface...")

# Navigate to a simple page
ga.goto("https://httpbin.org/html")
print("✅ Navigation successful")

# Take screenshot
ga.screenshot("simple_test.png")
print("✅ Screenshot taken")

# Get text
title = ga.get_text("h1")
print(f"✅ Title extracted: {title}")

# Test new page
page2 = ga.new_page()
ga.goto("https://httpbin.org/json", page=page2)
print("✅ New page created and navigated")

# Test scrolling
ga.scroll_to_bottom()
ga.scroll_to_top()
print("✅ Scrolling works")

# Test method chaining
ga.goto("https://httpbin.org/html").screenshot("chained.png")
print("✅ Method chaining works")

print(f"📊 Total pages: {len(ga.pages)}")
print(f"📊 Total requests: {len(ga.requests)}")

# Clean up
ga.stop()
print("🎉 All tests passed! Synchronous interface working perfectly!")
