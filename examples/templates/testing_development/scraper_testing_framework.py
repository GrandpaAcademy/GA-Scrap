"""
Scraper Testing Framework Template
Comprehensive testing framework for GA-Scrap scrapers with hot reload and debugging
"""

import sys
import os
import json
import time
import unittest
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

@dataclass
class TestResult:
    """Data class for test results"""
    test_name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None

class ScraperTestFramework:
    """Comprehensive testing framework for scrapers"""
    
    def __init__(self, test_config_file: str = "scraper_tests.json"):
        """
        Initialize testing framework
        
        Args:
            test_config_file: Path to test configuration file
        """
        self.test_config_file = test_config_file
        self.test_config = self._load_test_config()
        self.test_results = []
        self.test_data_dir = "test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)
        
    def _load_test_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        try:
            with open(self.test_config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_test_config()
    
    def _create_default_test_config(self) -> Dict[str, Any]:
        """Create default test configuration"""
        default_config = {
            "test_sites": {
                "httpbin": {
                    "base_url": "https://httpbin.org",
                    "tests": [
                        {
                            "name": "basic_html_test",
                            "url": "/html",
                            "selectors": {
                                "title": "title",
                                "heading": "h1",
                                "paragraphs": "p[]"
                            },
                            "expected_results": {
                                "title": "Herman Melville - Moby-Dick",
                                "heading_contains": "Herman Melville"
                            }
                        },
                        {
                            "name": "json_response_test",
                            "url": "/json",
                            "selectors": {
                                "content": "body"
                            },
                            "expected_results": {
                                "content_contains": "slideshow"
                            }
                        }
                    ]
                }
            },
            "test_settings": {
                "timeout": 30000,
                "take_screenshots": True,
                "save_html": True,
                "retry_failed_tests": True,
                "max_retries": 2
            }
        }
        
        with open(self.test_config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all configured tests"""
        print("🧪 Starting scraper test suite...")
        start_time = time.time()
        
        total_tests = 0
        passed_tests = 0
        
        for site_name, site_config in self.test_config["test_sites"].items():
            print(f"\n🌐 Testing site: {site_name}")
            
            for test_case in site_config["tests"]:
                total_tests += 1
                result = self._run_single_test(site_name, site_config, test_case)
                self.test_results.append(result)
                
                if result.success:
                    passed_tests += 1
                    print(f"✅ {result.test_name} - PASSED ({result.duration:.2f}s)")
                else:
                    print(f"❌ {result.test_name} - FAILED ({result.duration:.2f}s)")
                    if result.error_message:
                        print(f"   Error: {result.error_message}")
        
        total_duration = time.time() - start_time
        
        # Generate test report
        test_summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "error_message": r.error_message
                }
                for r in self.test_results
            ]
        }
        
        # Save test report
        self._save_test_report(test_summary)
        
        print(f"\n📊 Test Summary:")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {test_summary['success_rate']:.1f}%")
        print(f"Total duration: {total_duration:.2f}s")
        
        return test_summary
    
    def _run_single_test(self, site_name: str, site_config: Dict[str, Any], test_case: Dict[str, Any]) -> TestResult:
        """Run a single test case"""
        test_name = f"{site_name}_{test_case['name']}"
        start_time = time.time()
        
        try:
            with SyncGAScrap(
                sandbox_mode=True,
                debug=True,
                timeout=self.test_config["test_settings"]["timeout"]
            ) as scraper:
                
                # Navigate to test URL
                full_url = site_config["base_url"] + test_case["url"]
                scraper.goto(full_url)
                
                # Extract data using selectors
                extracted_data = {}
                for field_name, selector in test_case["selectors"].items():
                    try:
                        if selector.endswith("[]"):
                            # Multiple elements
                            selector = selector[:-2]
                            values = scraper.get_all_text(selector)
                            extracted_data[field_name] = values
                        else:
                            # Single element
                            value = scraper.get_text(selector)
                            extracted_data[field_name] = value
                    except Exception as e:
                        extracted_data[field_name] = f"ERROR: {str(e)}"
                
                # Validate results
                validation_result = self._validate_test_results(extracted_data, test_case.get("expected_results", {}))
                
                # Take screenshot if enabled
                screenshot_path = None
                if self.test_config["test_settings"]["take_screenshots"]:
                    screenshot_path = self._take_test_screenshot(scraper, test_name)
                
                # Save HTML if enabled
                if self.test_config["test_settings"]["save_html"]:
                    self._save_test_html(scraper, test_name)
                
                duration = time.time() - start_time
                
                return TestResult(
                    test_name=test_name,
                    success=validation_result["success"],
                    duration=duration,
                    error_message=validation_result.get("error"),
                    extracted_data=extracted_data,
                    screenshot_path=screenshot_path
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                error_message=str(e)
            )
    
    def _validate_test_results(self, extracted_data: Dict[str, Any], expected_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against expected results"""
        validation_errors = []
        
        for expected_field, expected_value in expected_results.items():
            if expected_field.endswith("_contains"):
                # Check if field contains expected text
                field_name = expected_field.replace("_contains", "")
                actual_value = extracted_data.get(field_name, "")
                
                if expected_value not in str(actual_value):
                    validation_errors.append(f"{field_name} should contain '{expected_value}', got '{actual_value}'")
            
            elif expected_field.endswith("_not_empty"):
                # Check if field is not empty
                field_name = expected_field.replace("_not_empty", "")
                actual_value = extracted_data.get(field_name, "")
                
                if not actual_value or actual_value.strip() == "":
                    validation_errors.append(f"{field_name} should not be empty")
            
            elif expected_field.endswith("_count"):
                # Check count of items
                field_name = expected_field.replace("_count", "")
                actual_value = extracted_data.get(field_name, [])
                
                if isinstance(actual_value, list) and len(actual_value) != expected_value:
                    validation_errors.append(f"{field_name} should have {expected_value} items, got {len(actual_value)}")
            
            else:
                # Exact match
                actual_value = extracted_data.get(expected_field, "")
                if actual_value != expected_value:
                    validation_errors.append(f"{expected_field} should be '{expected_value}', got '{actual_value}'")
        
        if validation_errors:
            return {
                "success": False,
                "error": "; ".join(validation_errors)
            }
        
        return {"success": True}
    
    def _take_test_screenshot(self, scraper: SyncGAScrap, test_name: str) -> str:
        """Take screenshot for test documentation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.test_data_dir, f"{test_name}_{timestamp}.png")
        
        try:
            scraper.screenshot(screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"⚠️ Could not take screenshot: {e}")
            return None
    
    def _save_test_html(self, scraper: SyncGAScrap, test_name: str):
        """Save HTML content for test analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(self.test_data_dir, f"{test_name}_{timestamp}.html")
        
        try:
            html_content = scraper.page.content()
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            print(f"⚠️ Could not save HTML: {e}")
    
    def _save_test_report(self, test_summary: Dict[str, Any]):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.test_data_dir, f"test_report_{timestamp}.json")
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(test_summary, f, indent=2)
        
        print(f"📄 Test report saved to: {report_path}")
    
    def test_selector_performance(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Test performance of different selectors"""
        print(f"⚡ Testing selector performance on {url}")
        
        performance_results = {}
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.goto(url)
            
            for selector_name, selector in selectors.items():
                start_time = time.time()
                
                try:
                    if selector.endswith("[]"):
                        selector = selector[:-2]
                        result = scraper.get_all_text(selector)
                        result_count = len(result)
                    else:
                        result = scraper.get_text(selector)
                        result_count = 1 if result else 0
                    
                    duration = time.time() - start_time
                    
                    performance_results[selector_name] = {
                        "selector": selector,
                        "duration": duration,
                        "success": True,
                        "result_count": result_count
                    }
                    
                    print(f"✅ {selector_name}: {duration:.3f}s ({result_count} results)")
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    performance_results[selector_name] = {
                        "selector": selector,
                        "duration": duration,
                        "success": False,
                        "error": str(e)
                    }
                    
                    print(f"❌ {selector_name}: {duration:.3f}s (ERROR: {str(e)})")
        
        return performance_results
    
    def debug_scraper_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Debug a scraper workflow step by step"""
        print("🐛 Starting scraper workflow debugging...")
        
        debug_results = {
            "steps": [],
            "final_state": {},
            "errors": []
        }
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            try:
                for i, step in enumerate(workflow_config.get("steps", [])):
                    step_name = step.get("name", f"Step {i+1}")
                    print(f"\n🔍 Debugging step: {step_name}")
                    
                    step_result = self._debug_single_step(scraper, step)
                    debug_results["steps"].append(step_result)
                    
                    if not step_result["success"]:
                        print(f"❌ Step failed: {step_result['error']}")
                        if step.get("required", True):
                            break
                    else:
                        print(f"✅ Step completed successfully")
                
                # Capture final page state
                debug_results["final_state"] = {
                    "url": scraper.page.url,
                    "title": scraper.get_text("title"),
                    "page_load_time": scraper.page.evaluate("performance.timing.loadEventEnd - performance.timing.navigationStart")
                }
                
            except Exception as e:
                debug_results["errors"].append(f"Workflow error: {str(e)}")
        
        return debug_results
    
    def _debug_single_step(self, scraper: SyncGAScrap, step: Dict[str, Any]) -> Dict[str, Any]:
        """Debug a single workflow step"""
        step_type = step.get("type")
        start_time = time.time()
        
        try:
            if step_type == "navigate":
                scraper.goto(step["url"])
                result_data = {"url": step["url"]}
                
            elif step_type == "click":
                element = scraper.get_element(step["selector"])
                if element:
                    scraper.click(step["selector"])
                    result_data = {"clicked": step["selector"]}
                else:
                    raise Exception(f"Element not found: {step['selector']}")
                
            elif step_type == "input":
                scraper.input(step["selector"], step["value"])
                result_data = {"input": step["selector"], "value": step["value"]}
                
            elif step_type == "extract":
                extracted = {}
                for field, selector in step["selectors"].items():
                    try:
                        value = scraper.get_text(selector)
                        extracted[field] = value
                    except:
                        extracted[field] = None
                result_data = {"extracted": extracted}
                
            elif step_type == "wait":
                duration = step.get("duration", 1)
                time.sleep(duration)
                result_data = {"waited": duration}
                
            else:
                raise Exception(f"Unknown step type: {step_type}")
            
            duration = time.time() - start_time
            
            return {
                "step_name": step.get("name", "Unnamed"),
                "step_type": step_type,
                "success": True,
                "duration": duration,
                "result_data": result_data
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            return {
                "step_name": step.get("name", "Unnamed"),
                "step_type": step_type,
                "success": False,
                "duration": duration,
                "error": str(e)
            }

# Example usage and test cases
def example_basic_testing():
    """Example: Basic scraper testing"""
    print("🧪 Basic Scraper Testing Example")
    print("=" * 50)
    
    framework = ScraperTestFramework()
    
    # Run all configured tests
    test_results = framework.run_all_tests()
    
    # Test selector performance
    performance_results = framework.test_selector_performance(
        url="https://httpbin.org/html",
        selectors={
            "title_by_tag": "title",
            "title_by_xpath": "//title",
            "all_paragraphs": "p[]",
            "first_paragraph": "p:first-child",
            "heading": "h1"
        }
    )
    
    print(f"\n⚡ Selector Performance Results:")
    for selector_name, result in performance_results.items():
        if result["success"]:
            print(f"{selector_name}: {result['duration']:.3f}s")

def example_workflow_debugging():
    """Example: Debug a complex workflow"""
    print("🐛 Workflow Debugging Example")
    print("=" * 50)
    
    framework = ScraperTestFramework()
    
    # Define a workflow to debug
    workflow_config = {
        "steps": [
            {
                "type": "navigate",
                "url": "https://httpbin.org/forms/post",
                "name": "Navigate to form"
            },
            {
                "type": "input",
                "selector": "input[name='custname']",
                "value": "Test User",
                "name": "Fill customer name"
            },
            {
                "type": "input",
                "selector": "input[name='custtel']",
                "value": "123-456-7890",
                "name": "Fill phone number"
            },
            {
                "type": "extract",
                "selectors": {
                    "form_title": "h1",
                    "input_count": "input[]"
                },
                "name": "Extract form data"
            }
        ]
    }
    
    # Debug the workflow
    debug_results = framework.debug_scraper_workflow(workflow_config)
    
    print(f"\n🐛 Debug Results:")
    for step in debug_results["steps"]:
        status = "✅" if step["success"] else "❌"
        print(f"{status} {step['step_name']}: {step['duration']:.3f}s")

def main():
    """Main function to demonstrate testing framework"""
    print("🧪 GA-Scrap Testing Framework Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Basic scraper testing")
    print("2. Workflow debugging")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_basic_testing()
    elif choice == "2":
        example_workflow_debugging()
    else:
        print("Invalid choice. Running basic testing example...")
        example_basic_testing()

if __name__ == "__main__":
    main()
