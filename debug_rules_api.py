#!/usr/bin/env python3
"""
Debug the Rules API endpoint specifically
"""

import requests
import json

def test_rules_api():
    """Test the Rules API endpoint and get detailed error info"""
    
    url = "http://localhost:8000/api/rules/"
    
    print(f"Testing Rules API: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"JSON Data: {json.dumps(data, indent=2)}")
            except:
                pass
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rules_api()
