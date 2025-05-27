#!/usr/bin/env python3
"""
Comprehensive endpoint testing for the ESD Guideline Generator
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, method="GET", description="", expect_status=200):
    """Test a single endpoint and return results"""
    result = {
        "url": url,
        "method": method,
        "description": description,
        "status": "UNKNOWN",
        "status_code": None,
        "error": None,
        "response_size": 0
    }
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=10)
        else:
            result["error"] = f"Unsupported method: {method}"
            result["status"] = "ERROR"
            return result
            
        result["status_code"] = response.status_code
        result["response_size"] = len(response.text)
        
        if response.status_code == expect_status:
            result["status"] = "SUCCESS"
        elif response.status_code == 404:
            result["status"] = "NOT_FOUND"
        elif response.status_code == 500:
            result["status"] = "SERVER_ERROR"
            result["error"] = "Internal Server Error"
        else:
            result["status"] = "UNEXPECTED"
            result["error"] = f"Expected {expect_status}, got {response.status_code}"
            
    except requests.exceptions.Timeout:
        result["status"] = "TIMEOUT"
        result["error"] = "Request timed out"
    except requests.exceptions.ConnectionError:
        result["status"] = "CONNECTION_ERROR"
        result["error"] = "Could not connect to server"
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result

def test_all_endpoints():
    """Test all application endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Define all endpoints to test
    endpoints = [
        # Main routes
        (f"{base_url}/", "GET", "Home page", 200),
        (f"{base_url}/dashboard", "GET", "Dashboard", 200),
        
        # Document management
        (f"{base_url}/documents/", "GET", "Document list API", 200),
        (f"{base_url}/documents/ui/list", "GET", "Document list UI", 200),
        (f"{base_url}/documents/ui/upload", "GET", "Document upload UI", 200),
        (f"{base_url}/documents/mcp-status", "GET", "MCP status check", 200),
        
        # Rules management  
        (f"{base_url}/rules/", "GET", "Rules dashboard", 200),
        (f"{base_url}/rules/create", "GET", "Rule creation form", 200),
        (f"{base_url}/api/rules/", "GET", "Rules API", 200),
        (f"{base_url}/api/rules/stats/summary", "GET", "Rule statistics", 200),
        (f"{base_url}/api/rules/export", "GET", "Rules export", 200),
        
        # Technology management
        (f"{base_url}/technologies/", "GET", "Technology list", 200),
        (f"{base_url}/api/technologies/", "GET", "Technology API", 200),
        
        # Template management
        (f"{base_url}/templates/", "GET", "Template list", 200),
        (f"{base_url}/api/templates/", "GET", "Template API", 200),
        
        # Validation system
        (f"{base_url}/validation", "GET", "Validation dashboard", 200),
        (f"{base_url}/validation/", "GET", "Validation list", 200),
        (f"{base_url}/api/validation/", "GET", "Validation API", 200),
        
        # Generation endpoints
        (f"{base_url}/generate/technology_A", "POST", "Generate for Technology A", 200),
        (f"{base_url}/status", "GET", "System status", 200),
        (f"{base_url}/technologies", "GET", "Available technologies", 200),
        
        # Legacy/compatibility routes
        (f"{base_url}/docs/import", "GET", "Document import redirect", 200),
    ]
    
    print("=" * 80)
    print("COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 80)
    print(f"Testing {len(endpoints)} endpoints at {datetime.now()}")
    print()
    
    results = []
    success_count = 0
    error_count = 0
    
    for url, method, description, expected_status in endpoints:
        print(f"Testing: {description}")
        print(f"  URL: {url}")
        
        result = test_endpoint(url, method, description, expected_status)
        results.append(result)
        
        # Print result
        status_icon = {
            "SUCCESS": "[OK]",
            "NOT_FOUND": "[404]", 
            "SERVER_ERROR": "[ERROR]",
            "TIMEOUT": "[TIMEOUT]",
            "CONNECTION_ERROR": "[CONN_ERR]",
            "ERROR": "[FAIL]",
            "UNEXPECTED": "[UNEXPECTED]"
        }.get(result["status"], "[UNKNOWN]")
        
        print(f"  Result: {status_icon} {result['status']} ({result['status_code']})")
        
        if result["error"]:
            print(f"  Error: {result['error']}")
        if result["response_size"] > 0:
            print(f"  Size: {result['response_size']:,} bytes")
            
        if result["status"] == "SUCCESS":
            success_count += 1
        else:
            error_count += 1
            
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Endpoints: {len(endpoints)}")
    print(f"[OK] Successful: {success_count}")
    print(f"[ERROR] Failed: {error_count}")
    print(f"Success Rate: {(success_count/len(endpoints)*100):.1f}%")
    print()
    
    # Detailed results for failed endpoints
    failed_endpoints = [r for r in results if r["status"] != "SUCCESS"]
    if failed_endpoints:
        print("FAILED ENDPOINTS DETAILS:")
        print("-" * 50)
        for result in failed_endpoints:
            print(f"[ERROR] {result['description']}")
            print(f"   URL: {result['url']}")
            print(f"   Status: {result['status']} ({result['status_code']})")
            if result['error']:
                print(f"   Error: {result['error']}")
            print()
    else:
        print("ALL ENDPOINTS WORKING CORRECTLY!")
    
    return results

if __name__ == "__main__":
    print("ESD Guideline Generator - Endpoint Health Check")
    results = test_all_endpoints()
