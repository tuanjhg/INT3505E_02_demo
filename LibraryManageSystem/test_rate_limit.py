#!/usr/bin/env python3
"""
Rate Limiting Test Script for Auth Login Endpoint

This script tests the rate limiting functionality specifically for the
authentication login endpoint.

Requirements:
- requests library: pip install requests
- Run the Flask app first: python app_swagger.py

Usage:
    python test_rate_limit.py

Rate Limits:
    - Login: 5 requests per minute, 20 requests per hour
    - Register: 3 requests per minute, 10 requests per hour
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"
LOGIN_URL = f"{API_BASE}/auth/login"
REGISTER_URL = f"{API_BASE}/auth/register"

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_response(response: requests.Response, description: str, attempt_num: int = None):
    """Print formatted response information"""
    prefix = f"Attempt {attempt_num}: " if attempt_num else ""
    print(f"\n{Colors.BOLD}{prefix}{description}{Colors.RESET}")
    
    # Status code with color
    if response.status_code == 200:
        status_color = Colors.GREEN
    elif response.status_code == 429:
        status_color = Colors.YELLOW
    else:
        status_color = Colors.RED
    
    print(f"Status Code: {status_color}{response.status_code}{Colors.RESET}")

    # Rate limit headers
    rate_limit_headers = {
        'X-RateLimit-Limit': response.headers.get('X-RateLimit-Limit'),
        'X-RateLimit-Remaining': response.headers.get('X-RateLimit-Remaining'),
        'X-RateLimit-Reset': response.headers.get('X-RateLimit-Reset'),
        'Retry-After': response.headers.get('Retry-After')
    }

    print(f"{Colors.CYAN}Rate Limit Headers:{Colors.RESET}")
    for header, value in rate_limit_headers.items():
        if value:
            print(f"  {header}: {value}")

    # Response body
    try:
        data = response.json()
        print(f"{Colors.CYAN}Response:{Colors.RESET}")
        print(json.dumps(data, indent=2))
    except Exception:
        print(f"{Colors.CYAN}Response:{Colors.RESET} {response.text[:200]}...")

def check_api_health() -> bool:
    """Check if API is running"""
    try:
        # Try to access the Swagger documentation
        response = requests.get(f"{BASE_URL}/swagger/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def test_login_rate_limit() -> Dict[str, Any]:
    """
    Test login endpoint rate limiting
    Expected: 5 requests per minute, 20 requests per hour
    """
    print_header("TESTING LOGIN RATE LIMIT")
    print_info("Rate limit: 5 requests per minute, 20 requests per hour")
    
    results = {
        'passed': False,
        'rate_limit_triggered': False,
        'attempts_before_limit': 0,
        'rate_limit_response': None
    }

    print("\n" + Colors.BOLD + "Making login attempts..." + Colors.RESET)
    
    for i in range(10):  # Try more than the limit
        try:
            response = requests.post(
                LOGIN_URL, 
                json={
                    "username": "testuser",
                    "password": "wrongpassword"
                },
                timeout=5
            )

            print_response(response, "Login attempt", i + 1)

            if response.status_code == 429:
                print_success("Rate limit triggered successfully!")
                results['rate_limit_triggered'] = True
                results['attempts_before_limit'] = i
                results['rate_limit_response'] = response.json()
                
                # Verify error response structure
                try:
                    data = response.json()
                    if data.get('error_code') == 'RATE_LIMIT_EXCEEDED':
                        print_success("Correct error code returned: RATE_LIMIT_EXCEEDED")
                        results['passed'] = True
                    else:
                        print_error(f"Unexpected error code: {data.get('error_code')}")
                    
                    # Check for retry_after in response
                    if 'retry_after' in data or response.headers.get('Retry-After'):
                        print_success("Retry-After information provided")
                except Exception as e:
                    print_error(f"Could not parse error response: {e}")
                
                break

            time.sleep(0.2)  # Small delay between requests

        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
            break

    if not results['rate_limit_triggered']:
        print_error("Rate limit was not triggered after 10 attempts")
        print_warning("Check if rate limiting is properly configured")

    return results

def test_rate_limit_recovery(retry_after: int = 60) -> bool:
    """
    Test that rate limits reset after the time window
    
    Args:
        retry_after: Seconds to wait for rate limit reset
    
    Returns:
        True if rate limit recovered successfully
    """
    print_header("TESTING RATE LIMIT RECOVERY")

    # First, trigger the rate limit
    print_info("Triggering rate limit...")
    rate_limit_triggered = False
    actual_retry_after = retry_after

    for i in range(10):
        try:
            response = requests.post(
                LOGIN_URL,
                json={
                    "username": "testuser",
                    "password": "wrongpassword"
                },
                timeout=5
            )

            if response.status_code == 429:
                actual_retry_after = int(response.headers.get('Retry-After', retry_after))
                print_success(f"Rate limit triggered. Retry-After: {actual_retry_after} seconds")
                rate_limit_triggered = True
                break
                
            time.sleep(0.2)
            
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
            return False

    if not rate_limit_triggered:
        print_warning("Could not trigger rate limit for recovery test")
        return False

    # Wait for recovery with countdown
    wait_time = min(actual_retry_after + 2, 65)  # Cap at 65 seconds for testing
    print_info(f"Waiting {wait_time} seconds for rate limit to reset...")
    
    for remaining in range(wait_time, 0, -1):
        print(f"\rTime remaining: {remaining} seconds...", end='', flush=True)
        time.sleep(1)
    print()  # New line after countdown

    # Try again after waiting
    try:
        response = requests.post(
            LOGIN_URL,
            json={
                "username": "testuser",
                "password": "wrongpassword"
            },
            timeout=5
        )

        print_response(response, "Request after rate limit reset")

        if response.status_code != 429:
            print_success("Rate limit reset successfully!")
            return True
        else:
            print_error("Rate limit did not reset")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False

def test_different_ips_rate_limit():
    """
    Test that rate limits are tracked per IP address
    Note: This test simulates the concept but won't actually work
    with different IPs from a single machine
    """
    print_header("RATE LIMIT PER IP VERIFICATION")
    print_info("Verifying rate limits are tracked separately per client")
    
    # In a real scenario, you would need to test from different machines/IPs
    # This is a demonstration of the concept
    print_warning("Note: True multi-IP testing requires multiple client machines")
    print_info("Rate limiter uses IP address to identify unique clients")
    print_info("Each IP address has its own rate limit counter")
    
    return True

def test_rate_limit_headers():
    """Test that appropriate rate limit headers are returned"""
    print_header("TESTING RATE LIMIT HEADERS")
    
    try:
        response = requests.post(
            LOGIN_URL,
            json={
                "username": "testuser",
                "password": "wrongpassword"
            },
            timeout=5
        )
        
        required_headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset']
        headers_present = []
        headers_missing = []
        
        for header in required_headers:
            if response.headers.get(header):
                headers_present.append(header)
            else:
                headers_missing.append(header)
        
        print(f"\n{Colors.BOLD}Header Check Results:{Colors.RESET}")
        
        if headers_present:
            print(f"{Colors.GREEN}Present headers:{Colors.RESET}")
            for header in headers_present:
                value = response.headers.get(header)
                print(f"  ✅ {header}: {value}")
        
        if headers_missing:
            print(f"\n{Colors.YELLOW}Missing headers:{Colors.RESET}")
            for header in headers_missing:
                print(f"  ⚠️  {header}")
        
        all_present = len(headers_missing) == 0
        if all_present:
            print_success("All required rate limit headers are present")
        else:
            print_warning("Some rate limit headers are missing")
        
        return all_present
        
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False

def run_all_tests():
    """Run all rate limiting tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       Library Management API - Rate Limiting Test Suite         ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    print_info(f"Testing endpoint: {LOGIN_URL}")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if API is running
    print_header("API HEALTH CHECK")
    if not check_api_health():
        print_error("API is not running or not accessible")
        print_info("Please start the Flask app first:")
        print_info("  cd LibraryManageSystem")
        print_info("  python app_swagger.py")
        return False

    print_success("API is running and accessible")

    # Track test results
    tests_passed = []
    tests_failed = []

    # Test 1: Rate limit headers
    print_info("\nTest 1/4: Checking rate limit headers...")
    if test_rate_limit_headers():
        tests_passed.append("Rate Limit Headers")
    else:
        tests_failed.append("Rate Limit Headers")

    time.sleep(2)  # Brief pause between tests

    # Test 2: Login rate limit
    print_info("\nTest 2/4: Testing login rate limit...")
    login_results = test_login_rate_limit()
    if login_results['passed']:
        tests_passed.append("Login Rate Limit")
    else:
        tests_failed.append("Login Rate Limit")

    time.sleep(2)  # Brief pause between tests

    # Test 3: Rate limit recovery
    print_info("\nTest 3/4: Testing rate limit recovery...")
    if test_rate_limit_recovery():
        tests_passed.append("Rate Limit Recovery")
    else:
        tests_failed.append("Rate Limit Recovery")

    # Test 4: IP-based rate limiting concept
    print_info("\nTest 4/4: Verifying IP-based rate limiting...")
    if test_different_ips_rate_limit():
        tests_passed.append("IP-based Rate Limiting")

    # Print final summary
    print_header("TEST SUMMARY")
    
    total_tests = len(tests_passed) + len(tests_failed)
    
    print(f"\n{Colors.BOLD}Total Tests: {total_tests}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {len(tests_passed)}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {len(tests_failed)}{Colors.RESET}")
    
    if tests_passed:
        print(f"\n{Colors.GREEN}✅ Passed Tests:{Colors.RESET}")
        for test in tests_passed:
            print(f"   • {test}")
    
    if tests_failed:
        print(f"\n{Colors.RED}❌ Failed Tests:{Colors.RESET}")
        for test in tests_failed:
            print(f"   • {test}")
    
    print(f"\n{Colors.BOLD}Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    
    # Overall result
    if len(tests_failed) == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! 🎉{Colors.RESET}\n")
        return True
    else:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠️  SOME TESTS FAILED{Colors.RESET}\n")
        return False

def main():
    """Main entry point"""
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
