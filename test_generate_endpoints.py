# test_generate_endpoints.py
"""Test the fixed generate endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing Generate Endpoints Fix")
    print("=" * 50)
    
    # Test 1: GET /technologies (should now use database)
    print("\n1. Testing GET /technologies")
    try:
        response = requests.get(f"{BASE_URL}/technologies")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            technologies = response.json()
            print(f"Technologies from database: {technologies}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: GET /generate/tsmc_28nm (should show generation page)
    print("\n2. Testing GET /generate/tsmc_28nm")
    try:
        response = requests.get(f"{BASE_URL}/generate/tsmc_28nm")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Generation page loaded successfully")
            print(f"Content includes 'Generate Guidelines': {'Generate Guidelines' in response.text}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: POST /generate/tsmc_28nm (should generate from database)
    print("\n3. Testing POST /generate/tsmc_28nm")
    try:
        response = requests.post(
            f"{BASE_URL}/generate/tsmc_28nm",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['message']}")
            print(f"File path: {result.get('file_path', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: GET /view/tsmc_28nm/latest (should show generated content)
    print("\n4. Testing GET /view/tsmc_28nm/latest")
    try:
        response = requests.get(f"{BASE_URL}/view/tsmc_28nm/latest")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("View page loaded successfully")
            print(f"Content includes 'ESD': {'ESD' in response.text}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo manually test:")
    print("1. Open browser to: http://localhost:8000/dashboard")
    print("2. Select a technology from the dropdown")
    print("3. Click 'Generate Guidelines'")
    print("4. You should see the generation page (not 405 error)")

if __name__ == "__main__":
    test_endpoints()
