#!/usr/bin/env python3
"""
Test GA-Scrap Installation
Quick test to verify GA-Scrap is properly installed and configured
"""

import sys
import subprocess
from pathlib import Path

def test_installation():
    """Test GA-Scrap installation"""
    print("🧪 Testing GA-Scrap Installation...")
    
    # Test 1: Check if ga-scrap command is available
    try:
        result = subprocess.run(['ga-scrap', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ga-scrap command is available")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ ga-scrap command not found")
            return False
    except FileNotFoundError:
        print("❌ ga-scrap command not found in PATH")
        return False
    
    # Test 2: Check doctor command
    try:
        result = subprocess.run(['ga-scrap', 'doctor'], capture_output=True, text=True)
        print("✅ Doctor command executed")
        if "❌" in result.stdout:
            print("⚠️  Some issues found in doctor check")
        else:
            print("✅ All doctor checks passed")
    except Exception as e:
        print(f"❌ Doctor command failed: {e}")
    
    # Test 3: Test quick scraping
    try:
        print("🚀 Testing quick scraping...")
        result = subprocess.run([
            'ga-scrap', 'quick', 
            'https://httpbin.org/html', 
            'h1'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Quick scraping works")
            print(f"   Result: {result.stdout.strip()}")
        else:
            print("⚠️  Quick scraping had issues")
            if result.stderr:
                print(f"   Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  Quick scraping timed out")
    except Exception as e:
        print(f"⚠️  Quick scraping failed: {e}")
    
    # Test 4: Check workspace
    workspace = Path.home() / "ga_scrap_apps"
    if workspace.exists():
        print(f"✅ Workspace exists: {workspace}")
    else:
        print(f"⚠️  Workspace not found: {workspace}")
    
    # Test 5: Check config
    config_file = Path.home() / ".ga_scrap" / "config.yaml"
    if config_file.exists():
        print(f"✅ Config exists: {config_file}")
    else:
        print(f"⚠️  Config not found: {config_file}")
    
    print("\n🎉 Installation test complete!")
    print("💡 If you see any issues, try: ga-scrap setup --force")
    
    return True

if __name__ == "__main__":
    try:
        test_installation()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
