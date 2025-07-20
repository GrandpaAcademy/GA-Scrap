"""
Multi-Tab Workflow Template
Demonstrates complex multi-tab workflows and parallel processing
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class MultiTabWorkflow:
    """Template for managing complex multi-tab workflows"""
    
    def __init__(self, max_tabs: int = 5):
        """
        Initialize multi-tab workflow manager
        
        Args:
            max_tabs: Maximum number of tabs to open simultaneously
        """
        self.max_tabs = max_tabs
        self.results = []
        self.active_tabs = {}
        
    def parallel_data_collection(self, urls: List[str], selectors: Dict[str, str],
                                tab_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Collect data from multiple URLs using parallel tabs
        
        Args:
            urls: List of URLs to scrape
            selectors: Selectors for data extraction
            tab_config: Configuration for tab management
            
        Returns:
            List of scraped data from all tabs
        """
        tab_config = tab_config or {}
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🔄 Starting parallel data collection from {len(urls)} URLs", "info")
            
            # Process URLs in batches to respect max_tabs limit
            batch_size = min(self.max_tabs, len(urls))
            
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                scraper.log(f"📄 Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs", "info")
                
                # Open tabs for current batch
                tabs = []
                for j, url in enumerate(batch_urls):
                    try:
                        if j == 0:
                            # Use main page for first URL
                            tab = scraper.page
                        else:
                            # Create new tab for additional URLs
                            tab = scraper.new_page()
                        
                        tabs.append({"page": tab, "url": url, "index": i + j})
                        
                    except Exception as e:
                        scraper.log(f"❌ Error creating tab for {url}: {e}", "error")
                
                # Navigate all tabs
                for tab_info in tabs:
                    try:
                        tab_info["page"].goto(tab_info["url"])
                        scraper.log(f"🌐 Navigated tab to {tab_info['url']}", "debug")
                    except Exception as e:
                        scraper.log(f"❌ Navigation error for {tab_info['url']}: {e}", "error")
                
                # Wait for all tabs to load
                load_timeout = tab_config.get("load_timeout", 10)
                time.sleep(load_timeout)
                
                # Extract data from all tabs
                for tab_info in tabs:
                    try:
                        data = self._extract_data_from_tab(scraper, tab_info, selectors)
                        if data:
                            self.results.append(data)
                            scraper.log(f"✅ Extracted data from {tab_info['url']}", "success")
                        else:
                            scraper.log(f"⚠️ No data extracted from {tab_info['url']}", "warning")
                            
                    except Exception as e:
                        scraper.log(f"❌ Data extraction error for {tab_info['url']}: {e}", "error")
                
                # Close additional tabs (keep main page)
                for tab_info in tabs[1:]:
                    try:
                        tab_info["page"].close()
                    except:
                        pass
                
                # Brief pause between batches
                if i + batch_size < len(urls):
                    time.sleep(1)
            
            scraper.log(f"🎉 Parallel collection complete! Processed {len(self.results)} URLs", "success")
            return self.results
    
    def _extract_data_from_tab(self, scraper: SyncGAScrap, tab_info: Dict[str, Any],
                              selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data from a specific tab"""
        page = tab_info["page"]
        url = tab_info["url"]
        
        # Switch context to this tab's page
        original_page = scraper.page
        scraper.page = page
        
        try:
            data = {
                "url": url,
                "tab_index": tab_info["index"],
                "scraped_at": datetime.now().isoformat(),
                "page_title": scraper.get_text("title") or ""
            }
            
            # Extract each field
            for field_name, selector in selectors.items():
                try:
                    if selector.endswith("[]"):
                        selector = selector[:-2]
                        values = scraper.get_all_text(selector)
                        data[field_name] = values
                    elif selector.startswith("@"):
                        attr_selector, attr_name = selector[1:].split("@")
                        value = scraper.get_attribute(attr_selector, attr_name)
                        data[field_name] = value
                    else:
                        value = scraper.get_text(selector)
                        data[field_name] = value
                        
                except Exception as e:
                    scraper.log(f"⚠️ Could not extract {field_name} from {url}: {e}", "debug")
                    data[field_name] = None
            
            return data
            
        finally:
            # Restore original page context
            scraper.page = original_page
    
    def cross_tab_data_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow that requires data sharing between tabs
        
        Args:
            workflow_config: Configuration for the cross-tab workflow
            
        Returns:
            Workflow results
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🔄 Starting cross-tab workflow...", "info")
            
            workflow_results = {
                "steps_completed": [],
                "data_collected": {},
                "errors": [],
                "start_time": datetime.now().isoformat()
            }
            
            try:
                steps = workflow_config.get("steps", [])
                tabs = {}  # Store tab references
                
                for i, step in enumerate(steps):
                    scraper.log(f"📋 Executing step {i+1}: {step.get('name', 'Unnamed')}", "info")
                    
                    step_result = self._execute_workflow_step(scraper, step, tabs, workflow_results)
                    
                    if step_result["success"]:
                        workflow_results["steps_completed"].append(step.get("name", f"Step {i+1}"))
                        scraper.log(f"✅ Step {i+1} completed", "success")
                    else:
                        error_msg = f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}"
                        workflow_results["errors"].append(error_msg)
                        scraper.log(f"❌ {error_msg}", "error")
                        
                        if step.get("required", True):
                            scraper.log("🛑 Required step failed, stopping workflow", "error")
                            break
                
                # Close all additional tabs
                for tab_name, tab_page in tabs.items():
                    if tab_page != scraper.page:
                        try:
                            tab_page.close()
                        except:
                            pass
                
                workflow_results["end_time"] = datetime.now().isoformat()
                workflow_results["success"] = len(workflow_results["errors"]) == 0
                
                return workflow_results
                
            except Exception as e:
                workflow_results["errors"].append(f"Workflow error: {str(e)}")
                workflow_results["success"] = False
                return workflow_results
    
    def _execute_workflow_step(self, scraper: SyncGAScrap, step: Dict[str, Any],
                              tabs: Dict[str, Any], workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step_type = step.get("type")
        
        try:
            if step_type == "open_tab":
                return self._step_open_tab(scraper, step, tabs)
            elif step_type == "navigate":
                return self._step_navigate(scraper, step, tabs)
            elif step_type == "extract_data":
                return self._step_extract_data(scraper, step, tabs, workflow_results)
            elif step_type == "fill_form":
                return self._step_fill_form(scraper, step, tabs, workflow_results)
            elif step_type == "wait":
                return self._step_wait(scraper, step)
            elif step_type == "switch_tab":
                return self._step_switch_tab(scraper, step, tabs)
            else:
                return {"success": False, "error": f"Unknown step type: {step_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _step_open_tab(self, scraper: SyncGAScrap, step: Dict[str, Any], tabs: Dict[str, Any]) -> Dict[str, Any]:
        """Open a new tab"""
        tab_name = step.get("tab_name", f"tab_{len(tabs)}")
        
        if tab_name in tabs:
            return {"success": False, "error": f"Tab {tab_name} already exists"}
        
        if len(tabs) == 0:
            # Use main page as first tab
            tabs[tab_name] = scraper.page
        else:
            # Create new tab
            new_page = scraper.new_page()
            tabs[tab_name] = new_page
        
        return {"success": True, "tab_name": tab_name}
    
    def _step_navigate(self, scraper: SyncGAScrap, step: Dict[str, Any], tabs: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate a tab to a URL"""
        tab_name = step.get("tab_name", "main")
        url = step.get("url")
        
        if not url:
            return {"success": False, "error": "No URL specified"}
        
        if tab_name not in tabs:
            return {"success": False, "error": f"Tab {tab_name} not found"}
        
        # Switch to target tab
        original_page = scraper.page
        scraper.page = tabs[tab_name]
        
        try:
            scraper.goto(url)
            return {"success": True, "url": url}
        finally:
            scraper.page = original_page
    
    def _step_extract_data(self, scraper: SyncGAScrap, step: Dict[str, Any],
                          tabs: Dict[str, Any], workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from a tab"""
        tab_name = step.get("tab_name", "main")
        selectors = step.get("selectors", {})
        data_key = step.get("data_key", "extracted_data")
        
        if tab_name not in tabs:
            return {"success": False, "error": f"Tab {tab_name} not found"}
        
        # Switch to target tab
        original_page = scraper.page
        scraper.page = tabs[tab_name]
        
        try:
            extracted_data = {}
            for field_name, selector in selectors.items():
                try:
                    if selector.endswith("[]"):
                        selector = selector[:-2]
                        values = scraper.get_all_text(selector)
                        extracted_data[field_name] = values
                    else:
                        value = scraper.get_text(selector)
                        extracted_data[field_name] = value
                except:
                    extracted_data[field_name] = None
            
            workflow_results["data_collected"][data_key] = extracted_data
            return {"success": True, "data": extracted_data}
            
        finally:
            scraper.page = original_page
    
    def _step_fill_form(self, scraper: SyncGAScrap, step: Dict[str, Any],
                       tabs: Dict[str, Any], workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Fill a form in a tab"""
        tab_name = step.get("tab_name", "main")
        form_data = step.get("form_data", {})
        
        if tab_name not in tabs:
            return {"success": False, "error": f"Tab {tab_name} not found"}
        
        # Switch to target tab
        original_page = scraper.page
        scraper.page = tabs[tab_name]
        
        try:
            for selector, value in form_data.items():
                # Support dynamic values from previous steps
                if isinstance(value, str) and value.startswith("${"):
                    # Extract value from workflow results
                    data_path = value[2:-1]  # Remove ${ and }
                    value = self._get_nested_value(workflow_results["data_collected"], data_path)
                
                if value is not None:
                    scraper.input(selector, str(value))
            
            # Submit form if specified
            if "submit_selector" in step:
                scraper.click(step["submit_selector"])
            
            return {"success": True}
            
        finally:
            scraper.page = original_page
    
    def _step_wait(self, scraper: SyncGAScrap, step: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for a specified duration"""
        duration = step.get("duration", 1)
        time.sleep(duration)
        return {"success": True, "waited": duration}
    
    def _step_switch_tab(self, scraper: SyncGAScrap, step: Dict[str, Any], tabs: Dict[str, Any]) -> Dict[str, Any]:
        """Switch active tab"""
        tab_name = step.get("tab_name")
        
        if tab_name not in tabs:
            return {"success": False, "error": f"Tab {tab_name} not found"}
        
        scraper.page = tabs[tab_name]
        return {"success": True, "active_tab": tab_name}
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value

# Example usage functions
def example_parallel_product_comparison():
    """Example: Compare products across multiple e-commerce sites"""
    print("🛒 Parallel Product Comparison")
    print("=" * 50)
    
    workflow = MultiTabWorkflow(max_tabs=3)
    
    # URLs of different e-commerce sites
    urls = [
        "https://example-store1.com/product/laptop",
        "https://example-store2.com/product/laptop",
        "https://example-store3.com/product/laptop"
    ]
    
    # Common selectors for product data
    selectors = {
        "product_name": "h1, .product-title",
        "price": ".price, .product-price",
        "rating": ".rating, .stars",
        "availability": ".stock-status, .availability"
    }
    
    # Collect data from all sites in parallel
    results = workflow.parallel_data_collection(urls, selectors)
    
    print(f"\n📊 Comparison Results:")
    for result in results:
        print(f"Site: {result['url']}")
        print(f"Product: {result.get('product_name', 'N/A')}")
        print(f"Price: {result.get('price', 'N/A')}")
        print(f"Rating: {result.get('rating', 'N/A')}")
        print("-" * 30)

def example_cross_tab_workflow():
    """Example: Multi-step workflow across tabs"""
    print("🔄 Cross-Tab Workflow Example")
    print("=" * 50)
    
    workflow = MultiTabWorkflow()
    
    # Define a complex workflow
    workflow_config = {
        "steps": [
            {
                "type": "open_tab",
                "tab_name": "search",
                "name": "Open search tab"
            },
            {
                "type": "navigate",
                "tab_name": "search",
                "url": "https://httpbin.org/forms/post",
                "name": "Navigate to search page"
            },
            {
                "type": "fill_form",
                "tab_name": "search",
                "form_data": {
                    "input[name='custname']": "John Doe",
                    "input[name='custtel']": "123-456-7890"
                },
                "submit_selector": "input[type='submit']",
                "name": "Fill search form"
            },
            {
                "type": "wait",
                "duration": 2,
                "name": "Wait for results"
            },
            {
                "type": "extract_data",
                "tab_name": "search",
                "selectors": {
                    "page_title": "title",
                    "form_data": "body"
                },
                "data_key": "search_results",
                "name": "Extract search results"
            }
        ]
    }
    
    # Execute workflow
    results = workflow.cross_tab_data_workflow(workflow_config)
    
    print(f"\n📊 Workflow Results:")
    print(f"Success: {results['success']}")
    print(f"Steps completed: {len(results['steps_completed'])}")
    print(f"Data collected: {len(results['data_collected'])}")
    
    if results['errors']:
        print(f"Errors: {results['errors']}")

def main():
    """Main function to demonstrate multi-tab workflows"""
    print("🔄 GA-Scrap Multi-Tab Workflow Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Parallel product comparison")
    print("2. Cross-tab workflow")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_parallel_product_comparison()
    elif choice == "2":
        example_cross_tab_workflow()
    else:
        print("Invalid choice. Running parallel comparison example...")
        example_parallel_product_comparison()

if __name__ == "__main__":
    main()
