# test_technology_management.py
"""Test script for Technology Management endpoints"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_technology_endpoints():
    """Test all technology management endpoints"""
    print("Testing Technology Management Endpoints...")
    print("=" * 50)
    
    # Test 1: List technologies
    print("\n1. Testing GET /technologies")
    try:
        response = requests.get(f"{BASE_URL}/technologies")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            techs = response.json()
            print(f"Found {len(techs)} technologies")
            for tech in techs[:3]:  # Show first 3
                print(f"  - {tech.get('name', 'Unknown')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get technologies with stats
    print("\n2. Testing GET /technologies/stats")
    try:
        response = requests.get(f"{BASE_URL}/technologies/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"Technologies with statistics:")
            for tech in stats[:3]:  # Show first 3
                print(f"  - {tech['name']}: {tech['total_rules']} rules "
                      f"(ESD: {tech['esd_rules']}, Latchup: {tech['latchup_rules']})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Create a test technology
    print("\n3. Testing POST /technologies")
    test_tech = {
        "name": "test_28nm_finfet",
        "description": "Test 28nm FinFET Technology | Foundry: Test, Node: 28nm, FinFET, HV Support"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/technologies",
            json=test_tech,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            created = response.json()
            print(f"Created technology: {created['name']} (ID: {created['id']})")
            return created['id']
        else:
            print(f"Error: {response.text}")
            # Try to get existing technology
            response = requests.get(f"{BASE_URL}/technologies")
            if response.status_code == 200:
                techs = response.json()
                for tech in techs:
                    if tech['name'] == test_tech['name']:
                        print(f"Technology already exists with ID: {tech['id']}")
                        return tech['id']
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_ui_endpoints():
    """Test UI endpoints"""
    print("\n\nTesting UI Endpoints...")
    print("=" * 50)
    
    # Test technology management page
    print("\n1. Testing GET /technologies/manage")
    try:
        response = requests.get(f"{BASE_URL}/technologies/manage")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Technology management page loaded successfully")
            print(f"Content length: {len(response.content)} bytes")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests"""
    print("Technology Management Test Suite")
    print("================================\n")
    
    # Test API endpoints
    tech_id = test_technology_endpoints()
    
    # Test UI endpoints
    test_ui_endpoints()
    
    # Cleanup - delete test technology if created
    if tech_id:
        print(f"\n\nCleaning up - deleting test technology (ID: {tech_id})")
        try:
            response = requests.delete(f"{BASE_URL}/technologies/{tech_id}")
            print(f"Delete status: {response.status_code}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    print("\n\nTest suite completed!")
    print("=" * 50)
    print("\nTo access the Technology Management interface:")
    print(f"1. Open browser to: {BASE_URL}/dashboard")
    print("2. Click on 'Manage Technologies' in the Technology Management section")
    print(f"3. Or go directly to: {BASE_URL}/technologies/manage")

if __name__ == "__main__":
    main()
