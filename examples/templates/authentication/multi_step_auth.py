"""
Multi-Step Authentication Template
Handles complex authentication flows including CAPTCHA, email verification, and multi-factor authentication
"""

import asyncio
import sys
import os
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class MultiStepAuthenticator:
    """Template for handling complex multi-step authentication flows"""
    
    def __init__(self, config_file: str = "auth_config.json"):
        """
        Initialize multi-step authenticator
        
        Args:
            config_file: Configuration file for authentication flows
        """
        self.config_file = config_file
        self.auth_config = self._load_auth_config()
        self.auth_state = {}
        
    def _load_auth_config(self) -> Dict[str, Any]:
        """Load authentication configuration"""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default authentication configuration"""
        default_config = {
            "sites": {
                "example_site": {
                    "login_url": "https://example.com/login",
                    "steps": [
                        {
                            "type": "credentials",
                            "username_selector": "input[name='email']",
                            "password_selector": "input[name='password']",
                            "submit_selector": "button[type='submit']"
                        },
                        {
                            "type": "captcha",
                            "captcha_selector": ".captcha-container",
                            "captcha_input_selector": "input[name='captcha']"
                        },
                        {
                            "type": "two_factor",
                            "code_input_selector": "input[name='verification_code']",
                            "submit_selector": ".verify-button"
                        }
                    ],
                    "success_indicators": [".dashboard", ".user-menu"],
                    "failure_indicators": [".error", ".alert-danger"]
                }
            }
        }
        
        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def authenticate(self, site_name: str, credentials: Dict[str, Any],
                    step_handlers: Dict[str, Callable] = None) -> bool:
        """
        Perform multi-step authentication
        
        Args:
            site_name: Name of the site to authenticate with
            credentials: Dictionary containing authentication credentials
            step_handlers: Custom handlers for specific authentication steps
            
        Returns:
            True if authentication successful
        """
        if site_name not in self.auth_config["sites"]:
            print(f"❌ No configuration found for {site_name}")
            return False
        
        site_config = self.auth_config["sites"][site_name]
        self.auth_state[site_name] = {"current_step": 0, "completed_steps": []}
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🔐 Starting multi-step authentication for {site_name}...", "info")
            
            try:
                # Navigate to login page
                scraper.goto(site_config["login_url"])
                
                # Handle pre-auth popups
                self._handle_popups(scraper)
                
                # Execute authentication steps
                for i, step_config in enumerate(site_config["steps"]):
                    scraper.log(f"🔄 Executing step {i+1}: {step_config['type']}", "info")
                    
                    self.auth_state[site_name]["current_step"] = i
                    
                    # Use custom handler if provided
                    if step_handlers and step_config["type"] in step_handlers:
                        success = step_handlers[step_config["type"]](scraper, step_config, credentials)
                    else:
                        success = self._execute_auth_step(scraper, step_config, credentials, site_name)
                    
                    if not success:
                        scraper.log(f"❌ Step {i+1} failed", "error")
                        return False
                    
                    self.auth_state[site_name]["completed_steps"].append(step_config["type"])
                    scraper.log(f"✅ Step {i+1} completed", "success")
                    
                    # Wait between steps
                    time.sleep(2)
                
                # Verify final authentication success
                if self._verify_authentication_success(scraper, site_config):
                    scraper.log(f"🎉 Authentication successful for {site_name}", "success")
                    return True
                else:
                    scraper.log(f"❌ Authentication failed for {site_name}", "error")
                    return False
                    
            except Exception as e:
                scraper.log(f"❌ Authentication error for {site_name}: {e}", "error")
                return False
    
    def _execute_auth_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                          credentials: Dict[str, Any], site_name: str) -> bool:
        """Execute a single authentication step"""
        step_type = step_config["type"]
        
        if step_type == "credentials":
            return self._handle_credentials_step(scraper, step_config, credentials)
        elif step_type == "captcha":
            return self._handle_captcha_step(scraper, step_config, credentials)
        elif step_type == "two_factor":
            return self._handle_two_factor_step(scraper, step_config, credentials)
        elif step_type == "email_verification":
            return self._handle_email_verification_step(scraper, step_config, credentials)
        elif step_type == "security_questions":
            return self._handle_security_questions_step(scraper, step_config, credentials)
        elif step_type == "device_verification":
            return self._handle_device_verification_step(scraper, step_config, credentials)
        else:
            print(f"⚠️ Unknown authentication step type: {step_type}")
            return False
    
    def _handle_credentials_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                               credentials: Dict[str, Any]) -> bool:
        """Handle username/password credentials step"""
        try:
            # Wait for form elements
            username_selector = step_config["username_selector"]
            password_selector = step_config["password_selector"]
            
            scraper.wait_for_selector(username_selector, timeout=10000)
            
            # Fill credentials
            scraper.input(username_selector, credentials.get("username", ""))
            scraper.input(password_selector, credentials.get("password", ""))
            
            # Handle additional fields
            if "additional_fields" in step_config:
                for field_selector, field_key in step_config["additional_fields"].items():
                    if field_key in credentials:
                        scraper.input(field_selector, credentials[field_key])
            
            # Submit form
            submit_selector = step_config["submit_selector"]
            scraper.click(submit_selector)
            
            # Wait for response
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Credentials step failed: {e}")
            return False
    
    def _handle_captcha_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                           credentials: Dict[str, Any]) -> bool:
        """Handle CAPTCHA verification step"""
        try:
            # Check if CAPTCHA is present
            captcha_selector = step_config.get("captcha_selector", ".captcha")
            if not scraper.get_element(captcha_selector):
                print("ℹ️ No CAPTCHA found, skipping step")
                return True
            
            # Take screenshot of CAPTCHA for manual solving
            captcha_screenshot = f"captcha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            scraper.screenshot(captcha_screenshot)
            print(f"📸 CAPTCHA screenshot saved: {captcha_screenshot}")
            
            # Get CAPTCHA solution
            if "captcha_solution" in credentials:
                captcha_solution = credentials["captcha_solution"]
            else:
                captcha_solution = input("Enter CAPTCHA solution: ").strip()
            
            # Enter CAPTCHA solution
            captcha_input_selector = step_config["captcha_input_selector"]
            scraper.input(captcha_input_selector, captcha_solution)
            
            # Submit if there's a separate submit button
            if "captcha_submit_selector" in step_config:
                scraper.click(step_config["captcha_submit_selector"])
            
            return True
            
        except Exception as e:
            print(f"❌ CAPTCHA step failed: {e}")
            return False
    
    def _handle_two_factor_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                              credentials: Dict[str, Any]) -> bool:
        """Handle two-factor authentication step"""
        try:
            # Wait for 2FA input
            code_input_selector = step_config["code_input_selector"]
            scraper.wait_for_selector(code_input_selector, timeout=15000)
            
            # Get 2FA code
            if "two_factor_code" in credentials:
                tfa_code = credentials["two_factor_code"]
            else:
                tfa_code = input("Enter 2FA code: ").strip()
            
            # Enter 2FA code
            scraper.input(code_input_selector, tfa_code)
            
            # Submit code
            submit_selector = step_config["submit_selector"]
            scraper.click(submit_selector)
            
            # Wait for verification
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Two-factor step failed: {e}")
            return False
    
    def _handle_email_verification_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                                      credentials: Dict[str, Any]) -> bool:
        """Handle email verification step"""
        try:
            # Check if email verification is required
            email_prompt_selector = step_config.get("email_prompt_selector", ".email-verification")
            if not scraper.get_element(email_prompt_selector):
                print("ℹ️ No email verification required, skipping step")
                return True
            
            print("📧 Email verification required")
            
            # If email verification link is provided
            if "verification_link" in credentials:
                verification_link = credentials["verification_link"]
                scraper.goto(verification_link)
                return True
            
            # If verification code is provided
            if "verification_code" in credentials:
                code_input_selector = step_config.get("code_input_selector", "input[name='verification_code']")
                scraper.input(code_input_selector, credentials["verification_code"])
                
                submit_selector = step_config.get("submit_selector", "button[type='submit']")
                scraper.click(submit_selector)
                return True
            
            # Manual verification
            verification_method = input("Enter verification method (link/code): ").strip().lower()
            
            if verification_method == "link":
                verification_link = input("Enter verification link: ").strip()
                scraper.goto(verification_link)
            elif verification_method == "code":
                verification_code = input("Enter verification code: ").strip()
                code_input_selector = step_config.get("code_input_selector", "input[name='verification_code']")
                scraper.input(code_input_selector, verification_code)
                
                submit_selector = step_config.get("submit_selector", "button[type='submit']")
                scraper.click(submit_selector)
            
            return True
            
        except Exception as e:
            print(f"❌ Email verification step failed: {e}")
            return False
    
    def _handle_security_questions_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                                      credentials: Dict[str, Any]) -> bool:
        """Handle security questions step"""
        try:
            # Check if security questions are present
            questions_selector = step_config.get("questions_selector", ".security-question")
            questions = scraper.get_all_text(questions_selector)
            
            if not questions:
                print("ℹ️ No security questions found, skipping step")
                return True
            
            print(f"🔒 Found {len(questions)} security questions")
            
            # Answer each question
            for i, question in enumerate(questions):
                print(f"Question {i+1}: {question}")
                
                # Look for answer in credentials
                answer_key = f"security_answer_{i+1}"
                if answer_key in credentials:
                    answer = credentials[answer_key]
                else:
                    answer = input(f"Answer: ").strip()
                
                # Find and fill answer input
                answer_selector = step_config.get("answer_selector", f".security-answer:nth-child({i+1}) input")
                scraper.input(answer_selector, answer)
            
            # Submit answers
            submit_selector = step_config.get("submit_selector", "button[type='submit']")
            scraper.click(submit_selector)
            
            return True
            
        except Exception as e:
            print(f"❌ Security questions step failed: {e}")
            return False
    
    def _handle_device_verification_step(self, scraper: SyncGAScrap, step_config: Dict[str, Any],
                                       credentials: Dict[str, Any]) -> bool:
        """Handle device verification step"""
        try:
            # Check if device verification is required
            device_prompt_selector = step_config.get("device_prompt_selector", ".device-verification")
            if not scraper.get_element(device_prompt_selector):
                print("ℹ️ No device verification required, skipping step")
                return True
            
            print("📱 Device verification required")
            
            # Look for "Trust this device" option
            trust_device_selector = step_config.get("trust_device_selector", "input[name='trust_device']")
            if scraper.get_element(trust_device_selector):
                trust_device = credentials.get("trust_device", True)
                if trust_device:
                    scraper.check(trust_device_selector)
            
            # Submit device verification
            submit_selector = step_config.get("submit_selector", "button[type='submit']")
            scraper.click(submit_selector)
            
            return True
            
        except Exception as e:
            print(f"❌ Device verification step failed: {e}")
            return False
    
    def _verify_authentication_success(self, scraper: SyncGAScrap, site_config: Dict[str, Any]) -> bool:
        """Verify that authentication was successful"""
        # Check for success indicators
        success_indicators = site_config.get("success_indicators", [])
        for indicator in success_indicators:
            if scraper.get_element(indicator):
                return True
        
        # Check for failure indicators
        failure_indicators = site_config.get("failure_indicators", [])
        for indicator in failure_indicators:
            if scraper.get_element(indicator):
                return False
        
        # If no specific indicators, check URL change
        current_url = scraper.page.url
        login_url = site_config["login_url"]
        
        return current_url != login_url and "login" not in current_url.lower()
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common popups before authentication"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close",
            ".gdpr-accept", ".privacy-accept"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def get_auth_state(self, site_name: str) -> Dict[str, Any]:
        """Get current authentication state for a site"""
        return self.auth_state.get(site_name, {})
    
    def create_custom_auth_flow(self, site_name: str, steps: List[Dict[str, Any]],
                               success_indicators: List[str], failure_indicators: List[str],
                               login_url: str) -> None:
        """Create a custom authentication flow configuration"""
        self.auth_config["sites"][site_name] = {
            "login_url": login_url,
            "steps": steps,
            "success_indicators": success_indicators,
            "failure_indicators": failure_indicators
        }
        
        # Save updated configuration
        with open(self.config_file, "w") as f:
            json.dump(self.auth_config, f, indent=2)
        
        print(f"✅ Custom auth flow created for {site_name}")

# Example usage functions
def example_banking_login():
    """Example: Multi-step banking authentication"""
    print("🏦 Banking Multi-Step Authentication")
    print("=" * 50)
    
    authenticator = MultiStepAuthenticator()
    
    # Create banking auth flow
    banking_steps = [
        {
            "type": "credentials",
            "username_selector": "input[name='user_id']",
            "password_selector": "input[name='password']",
            "submit_selector": ".login-submit"
        },
        {
            "type": "security_questions",
            "questions_selector": ".security-question-text",
            "answer_selector": ".security-answer input",
            "submit_selector": ".verify-submit"
        },
        {
            "type": "two_factor",
            "code_input_selector": "input[name='sms_code']",
            "submit_selector": ".verify-code"
        },
        {
            "type": "device_verification",
            "device_prompt_selector": ".device-trust",
            "trust_device_selector": "input[name='trust_device']",
            "submit_selector": ".continue-button"
        }
    ]
    
    authenticator.create_custom_auth_flow(
        site_name="bank_site",
        steps=banking_steps,
        success_indicators=[".account-dashboard", ".balance-summary"],
        failure_indicators=[".error-message", ".login-failed"],
        login_url="https://bank.example.com/login"
    )
    
    # Perform authentication
    credentials = {
        "username": "user123",
        "password": "password123",
        "security_answer_1": "Answer 1",
        "security_answer_2": "Answer 2",
        "two_factor_code": "123456",
        "trust_device": True
    }
    
    success = authenticator.authenticate("bank_site", credentials)
    print(f"Authentication result: {'Success' if success else 'Failed'}")

def example_enterprise_sso():
    """Example: Enterprise SSO with CAPTCHA"""
    print("🏢 Enterprise SSO Authentication")
    print("=" * 50)
    
    authenticator = MultiStepAuthenticator()
    
    # Enterprise SSO flow
    sso_steps = [
        {
            "type": "credentials",
            "username_selector": "input[name='email']",
            "password_selector": "input[name='password']",
            "submit_selector": ".sso-login"
        },
        {
            "type": "captcha",
            "captcha_selector": ".captcha-image",
            "captcha_input_selector": "input[name='captcha_response']",
            "captcha_submit_selector": ".captcha-verify"
        },
        {
            "type": "email_verification",
            "email_prompt_selector": ".email-verification-prompt",
            "code_input_selector": "input[name='email_code']",
            "submit_selector": ".verify-email"
        }
    ]
    
    authenticator.create_custom_auth_flow(
        site_name="enterprise_sso",
        steps=sso_steps,
        success_indicators=[".dashboard", ".user-profile"],
        failure_indicators=[".auth-error", ".access-denied"],
        login_url="https://sso.company.com/login"
    )
    
    # Custom CAPTCHA handler
    def custom_captcha_handler(scraper, step_config, credentials):
        print("🤖 Custom CAPTCHA handler activated")
        # Implement custom CAPTCHA solving logic here
        # This could integrate with CAPTCHA solving services
        return True
    
    credentials = {
        "username": "employee@company.com",
        "password": "enterprise_password",
        "captcha_solution": "ABCD123",
        "verification_code": "789012"
    }
    
    step_handlers = {
        "captcha": custom_captcha_handler
    }
    
    success = authenticator.authenticate("enterprise_sso", credentials, step_handlers)
    print(f"SSO Authentication result: {'Success' if success else 'Failed'}")

def main():
    """Main function to demonstrate multi-step authentication"""
    print("🔐 GA-Scrap Multi-Step Authentication Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Banking multi-step authentication")
    print("2. Enterprise SSO with CAPTCHA")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_banking_login()
    elif choice == "2":
        example_enterprise_sso()
    else:
        print("Invalid choice. Running banking example...")
        example_banking_login()

if __name__ == "__main__":
    main()
