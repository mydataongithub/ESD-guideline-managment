#!/usr/bin/env python3
"""
Test the API endpoint directly to get the real error
"""

import requests
import json

def test_api_endpoint():
    """Test the document processing API endpoint directly"""
    
    # Test with document ID 1 (we know it exists from our previous test)
    document_id = 1
    url = f"http://localhost:8000/documents/{document_id}/process"
    
    print(f"Testing API endpoint: {url}")
    
    try:
        response = requests.post(url, timeout=30)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("Success!")
            try:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
            except:
                print(f"Response text: {response.text}")
        else:
            print("Error response:")
            print(f"Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
def test_document_list():
    """Test getting the document list"""
    url = "http://localhost:8000/documents/"
    
    print(f"\nTesting document list endpoint: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            docs = response.json()
            print(f"Found {len(docs)} documents")
            for doc in docs[:3]:  # Show first 3
                print(f"  ID: {doc['id']}, File: {doc['filename']}, Processed: {doc['processed']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("API Endpoint Test")
    print("=" * 20)
    
    test_document_list()
    test_api_endpoint()
