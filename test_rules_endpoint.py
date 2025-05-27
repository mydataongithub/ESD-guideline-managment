#!/usr/bin/env python3
"""
Test the rules endpoint directly to see the error
"""

import requests
import json

def test_rules_endpoint():
    """Test the rules endpoint directly"""
    
    url = "http://localhost:8000/rules/"
    
    print(f"Testing rules endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("Success!")
            print(f"Response length: {len(response.text)} characters")
            # Just show first few lines
            print("First few lines of response:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print("Error response:")
            print(f"Status: {response.status_code}")
            print(f"Response text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("Rules Endpoint Test")
    print("=" * 20)
    test_rules_endpoint()
