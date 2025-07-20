"""
File Operations Template
Demonstrates file uploads, downloads, and file handling in web scraping
"""

import asyncio
import sys
import os
import json
import time
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class FileOperationsScraper:
    """Template for handling file uploads, downloads, and file-based interactions"""
    
    def __init__(self, downloads_dir: str = "downloads", uploads_dir: str = "uploads"):
        """
        Initialize file operations scraper
        
        Args:
            downloads_dir: Directory for downloaded files
            uploads_dir: Directory containing files to upload
        """
        self.downloads_dir = Path(downloads_dir)
        self.uploads_dir = Path(uploads_dir)
        
        # Create directories if they don't exist
        self.downloads_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
        
        self.downloaded_files = []
        self.uploaded_files = []
    
    def download_files_from_page(self, url: str, download_selectors: List[str],
                                file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Download files from a webpage
        
        Args:
            url: URL of the page containing download links
            download_selectors: CSS selectors for download links
            file_types: Optional list of file extensions to filter (e.g., ['.pdf', '.xlsx'])
            
        Returns:
            List of download results
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("📥 Starting file downloads...", "info")
            
            # Navigate to page
            scraper.goto(url)
            
            # Handle popups
            self._handle_popups(scraper)
            
            # Collect download links
            download_links = []
            for selector in download_selectors:
                try:
                    links = scraper.get_all_attributes(selector, "href")
                    download_links.extend(links)
                except Exception as e:
                    scraper.log(f"⚠️ Could not get links from {selector}: {e}", "warning")
            
            # Filter by file type if specified
            if file_types:
                filtered_links = []
                for link in download_links:
                    if any(link.lower().endswith(ext.lower()) for ext in file_types):
                        filtered_links.append(link)
                download_links = filtered_links
            
            scraper.log(f"🔗 Found {len(download_links)} download links", "info")
            
            # Download each file
            for i, link in enumerate(download_links):
                try:
                    scraper.log(f"📥 Downloading file {i+1}/{len(download_links)}: {link}", "info")
                    
                    # Make link absolute if needed
                    if link.startswith("/"):
                        base_url = f"{scraper.page.url.split('/')[0]}//{scraper.page.url.split('/')[2]}"
                        link = base_url + link
                    elif not link.startswith("http"):
                        base_url = "/".join(scraper.page.url.split("/")[:-1])
                        link = f"{base_url}/{link}"
                    
                    # Download file
                    download_result = self._download_file(scraper, link)
                    self.downloaded_files.append(download_result)
                    
                    if download_result["success"]:
                        scraper.log(f"✅ Downloaded: {download_result['filename']}", "success")
                    else:
                        scraper.log(f"❌ Failed to download: {link}", "error")
                    
                except Exception as e:
                    scraper.log(f"❌ Error downloading {link}: {e}", "error")
                    self.downloaded_files.append({
                        "url": link,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            scraper.log(f"📥 Download complete! {len([f for f in self.downloaded_files if f['success']])} files downloaded", "success")
            return self.downloaded_files
    
    def _download_file(self, scraper: SyncGAScrap, url: str) -> Dict[str, Any]:
        """Download a single file"""
        try:
            # Start download
            with scraper.page.expect_download() as download_info:
                scraper.page.goto(url)
            
            download = download_info.value
            
            # Generate filename
            suggested_filename = download.suggested_filename
            if not suggested_filename:
                # Extract filename from URL
                suggested_filename = url.split("/")[-1].split("?")[0]
                if not suggested_filename or "." not in suggested_filename:
                    suggested_filename = f"download_{int(time.time())}.bin"
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{suggested_filename}"
            filepath = self.downloads_dir / filename
            
            download.save_as(str(filepath))
            
            # Get file info
            file_size = filepath.stat().st_size if filepath.exists() else 0
            
            return {
                "url": url,
                "filename": filename,
                "filepath": str(filepath),
                "file_size": file_size,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def upload_files_to_form(self, url: str, upload_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload files to a web form
        
        Args:
            url: URL of the page with upload form
            upload_config: Configuration for upload process
            
        Returns:
            Upload result summary
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("📤 Starting file upload...", "info")
            
            # Navigate to upload page
            scraper.goto(url)
            self._handle_popups(scraper)
            
            # Wait for upload form
            upload_selector = upload_config.get("upload_selector", "input[type='file']")
            scraper.wait_for_selector(upload_selector, timeout=10000)
            
            # Prepare files to upload
            files_to_upload = self._prepare_upload_files(upload_config.get("files", []))
            
            if not files_to_upload:
                return {
                    "success": False,
                    "error": "No files to upload",
                    "timestamp": datetime.now().isoformat()
                }
            
            try:
                # Upload files
                scraper.log(f"📤 Uploading {len(files_to_upload)} files...", "info")
                
                # Handle single vs multiple file upload
                if upload_config.get("multiple", False):
                    # Multiple file upload
                    scraper.upload_files(upload_selector, files_to_upload)
                else:
                    # Single file upload
                    scraper.upload_files(upload_selector, [files_to_upload[0]])
                
                # Fill additional form fields
                if "form_fields" in upload_config:
                    for field_selector, field_value in upload_config["form_fields"].items():
                        scraper.input(field_selector, field_value)
                
                # Submit form
                submit_selector = upload_config.get("submit_selector", "button[type='submit'], .upload-submit")
                scraper.click(submit_selector)
                
                # Wait for upload completion
                self._wait_for_upload_completion(scraper, upload_config)
                
                # Verify upload success
                success = self._verify_upload_success(scraper, upload_config)
                
                result = {
                    "success": success,
                    "uploaded_files": [os.path.basename(f) for f in files_to_upload],
                    "upload_count": len(files_to_upload),
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    scraper.log("✅ Upload completed successfully", "success")
                else:
                    scraper.log("⚠️ Upload may have failed", "warning")
                
                return result
                
            except Exception as e:
                scraper.log(f"❌ Upload error: {e}", "error")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    def _prepare_upload_files(self, file_specs: List[Any]) -> List[str]:
        """Prepare files for upload"""
        files_to_upload = []
        
        for file_spec in file_specs:
            if isinstance(file_spec, str):
                # Direct file path
                file_path = self.uploads_dir / file_spec
                if file_path.exists():
                    files_to_upload.append(str(file_path))
            elif isinstance(file_spec, dict):
                # File specification with options
                filename = file_spec.get("filename")
                if filename:
                    file_path = self.uploads_dir / filename
                    if file_path.exists():
                        files_to_upload.append(str(file_path))
                    elif file_spec.get("create_if_missing", False):
                        # Create dummy file
                        content = file_spec.get("content", "Test file content")
                        file_path.write_text(content)
                        files_to_upload.append(str(file_path))
        
        return files_to_upload
    
    def _wait_for_upload_completion(self, scraper: SyncGAScrap, upload_config: Dict[str, Any]):
        """Wait for upload to complete"""
        # Wait for upload progress indicators
        progress_selectors = upload_config.get("progress_selectors", [".upload-progress", ".uploading"])
        
        for selector in progress_selectors:
            try:
                # Wait for progress indicator to appear
                scraper.wait_for_selector(selector, timeout=5000)
                # Wait for it to disappear (upload complete)
                scraper.wait_for_selector(selector, state="hidden", timeout=30000)
            except:
                # Progress indicator might not appear
                continue
        
        # Additional wait time
        upload_timeout = upload_config.get("upload_timeout", 10)
        time.sleep(upload_timeout)
    
    def _verify_upload_success(self, scraper: SyncGAScrap, upload_config: Dict[str, Any]) -> bool:
        """Verify that upload was successful"""
        # Check for success indicators
        success_selectors = upload_config.get("success_selectors", [".upload-success", ".file-uploaded"])
        for selector in success_selectors:
            if scraper.get_element(selector):
                return True
        
        # Check for error indicators
        error_selectors = upload_config.get("error_selectors", [".upload-error", ".error"])
        for selector in error_selectors:
            if scraper.get_element(selector):
                return False
        
        # If no specific indicators, assume success if no errors
        return True
    
    def process_csv_upload_workflow(self, url: str, csv_file: str,
                                   workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete workflow for CSV file upload and processing
        
        Args:
            url: URL of the CSV upload page
            csv_file: Path to CSV file to upload
            workflow_config: Configuration for the workflow
            
        Returns:
            Workflow result
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("📊 Starting CSV upload workflow...", "info")
            
            try:
                # Navigate to upload page
                scraper.goto(url)
                self._handle_popups(scraper)
                
                # Step 1: Upload CSV file
                csv_path = self.uploads_dir / csv_file
                if not csv_path.exists():
                    return {
                        "success": False,
                        "error": f"CSV file not found: {csv_file}",
                        "timestamp": datetime.now().isoformat()
                    }
                
                upload_selector = workflow_config.get("upload_selector", "input[type='file']")
                scraper.upload_files(upload_selector, [str(csv_path)])
                
                # Step 2: Configure import settings
                if "import_settings" in workflow_config:
                    for setting_selector, setting_value in workflow_config["import_settings"].items():
                        if isinstance(setting_value, bool):
                            if setting_value:
                                scraper.check(setting_selector)
                        else:
                            scraper.input(setting_selector, setting_value)
                
                # Step 3: Start import process
                import_button = workflow_config.get("import_button", ".start-import, .process-csv")
                scraper.click(import_button)
                
                # Step 4: Wait for processing
                self._wait_for_csv_processing(scraper, workflow_config)
                
                # Step 5: Get results
                results = self._get_csv_processing_results(scraper, workflow_config)
                
                scraper.log("✅ CSV workflow completed", "success")
                return {
                    "success": True,
                    "csv_file": csv_file,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                scraper.log(f"❌ CSV workflow error: {e}", "error")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    def _wait_for_csv_processing(self, scraper: SyncGAScrap, workflow_config: Dict[str, Any]):
        """Wait for CSV processing to complete"""
        # Wait for processing indicators
        processing_selectors = workflow_config.get("processing_selectors", [".processing", ".importing"])
        
        for selector in processing_selectors:
            try:
                scraper.wait_for_selector(selector, timeout=5000)
                scraper.wait_for_selector(selector, state="hidden", timeout=60000)  # 1 minute timeout
            except:
                continue
        
        # Wait for completion indicators
        completion_selectors = workflow_config.get("completion_selectors", [".import-complete", ".processing-done"])
        
        for selector in completion_selectors:
            try:
                scraper.wait_for_selector(selector, timeout=30000)
                break
            except:
                continue
    
    def _get_csv_processing_results(self, scraper: SyncGAScrap, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract CSV processing results"""
        results = {}
        
        # Extract result metrics
        result_selectors = workflow_config.get("result_selectors", {})
        for metric_name, selector in result_selectors.items():
            try:
                value = scraper.get_text(selector)
                results[metric_name] = value
            except:
                results[metric_name] = None
        
        # Extract any error messages
        error_selectors = workflow_config.get("error_selectors", [".import-errors", ".processing-errors"])
        errors = []
        for selector in error_selectors:
            try:
                error_messages = scraper.get_all_text(selector)
                errors.extend(error_messages)
            except:
                continue
        
        if errors:
            results["errors"] = errors
        
        return results
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common popups"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def create_sample_files(self):
        """Create sample files for testing uploads"""
        # Create sample text file
        text_file = self.uploads_dir / "sample.txt"
        text_file.write_text("This is a sample text file for testing uploads.")
        
        # Create sample CSV file
        csv_file = self.uploads_dir / "sample.csv"
        csv_content = """Name,Email,Age
John Doe,john@example.com,30
Jane Smith,jane@example.com,25
Bob Johnson,bob@example.com,35"""
        csv_file.write_text(csv_content)
        
        # Create sample JSON file
        json_file = self.uploads_dir / "sample.json"
        json_data = {
            "users": [
                {"name": "Alice", "role": "admin"},
                {"name": "Bob", "role": "user"}
            ]
        }
        json_file.write_text(json.dumps(json_data, indent=2))
        
        print(f"✅ Created sample files in {self.uploads_dir}")

# Example usage functions
def example_document_downloads():
    """Example: Download documents from a website"""
    print("📥 Document Download Example")
    print("=" * 50)
    
    scraper = FileOperationsScraper()
    
    # Example: Download PDFs from a documentation site
    url = "https://httpbin.org/links/10/0"  # Example page with links
    
    download_selectors = [
        "a[href$='.pdf']",
        "a[href$='.doc']",
        "a[href$='.xlsx']",
        "a[download]"  # Any link with download attribute
    ]
    
    file_types = [".pdf", ".doc", ".docx", ".xlsx", ".txt"]
    
    # Download files
    results = scraper.download_files_from_page(url, download_selectors, file_types)
    
    print(f"\n📊 Download Results:")
    successful = [r for r in results if r["success"]]
    print(f"Successfully downloaded: {len(successful)} files")
    
    for result in successful:
        print(f"  📄 {result['filename']} ({result['file_size']} bytes)")

def example_file_upload():
    """Example: Upload files to a web form"""
    print("📤 File Upload Example")
    print("=" * 50)
    
    scraper = FileOperationsScraper()
    
    # Create sample files for testing
    scraper.create_sample_files()
    
    # Example upload configuration
    upload_config = {
        "upload_selector": "input[type='file']",
        "files": [
            "sample.txt",
            "sample.csv"
        ],
        "multiple": True,
        "form_fields": {
            "input[name='description']": "Test file upload",
            "select[name='category']": "documents"
        },
        "submit_selector": "button[type='submit']",
        "success_selectors": [".upload-success", ".files-uploaded"],
        "upload_timeout": 5
    }
    
    # Example upload URL (replace with actual upload form)
    url = "https://httpbin.org/forms/post"
    
    # Perform upload
    result = scraper.upload_files_to_form(url, upload_config)
    
    print(f"\n📊 Upload Results:")
    print(f"Success: {result['success']}")
    if result["success"]:
        print(f"Uploaded files: {result.get('uploaded_files', [])}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

def example_csv_workflow():
    """Example: Complete CSV upload and processing workflow"""
    print("📊 CSV Processing Workflow Example")
    print("=" * 50)
    
    scraper = FileOperationsScraper()
    
    # Create sample CSV
    scraper.create_sample_files()
    
    # CSV workflow configuration
    workflow_config = {
        "upload_selector": "input[type='file']",
        "import_settings": {
            "input[name='has_header']": True,
            "select[name='delimiter']": ",",
            "input[name='skip_errors']": True
        },
        "import_button": ".start-import",
        "processing_selectors": [".processing-csv"],
        "completion_selectors": [".import-complete"],
        "result_selectors": {
            "total_rows": ".total-rows",
            "successful_rows": ".successful-rows",
            "error_rows": ".error-rows"
        },
        "error_selectors": [".import-errors"]
    }
    
    # Example CSV processing URL
    url = "https://example-app.com/csv-import"
    
    # Run workflow
    result = scraper.process_csv_upload_workflow(url, "sample.csv", workflow_config)
    
    print(f"\n📊 CSV Workflow Results:")
    print(f"Success: {result['success']}")
    if result["success"]:
        results = result.get("results", {})
        print(f"Processing results: {results}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

def main():
    """Main function to demonstrate file operations"""
    print("📁 GA-Scrap File Operations Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Document downloads")
    print("2. File upload form")
    print("3. CSV processing workflow")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        example_document_downloads()
    elif choice == "2":
        example_file_upload()
    elif choice == "3":
        example_csv_workflow()
    else:
        print("Invalid choice. Running document download example...")
        example_document_downloads()

if __name__ == "__main__":
    main()
