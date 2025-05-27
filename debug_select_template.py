#!/usr/bin/env python
# Script to debug the select-template endpoint

import requests
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database.models import Technology, Template

def debug_endpoint_directly():
    """Debug by making a direct HTTP request"""
    technology_name = "tsmc_28nm"
    url = f"http://localhost:8000/select-template/{technology_name}"
    
    print(f"Testing endpoint: {url}")
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Endpoint returned 200 OK")
        elif response.status_code == 404:
            print("Error: Endpoint returned 404 Not Found")
            # Check database content
            debug_database(technology_name)
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

def debug_with_testclient():
    """Debug with FastAPI TestClient"""
    technology_name = "tsmc_28nm"
    print(f"Using TestClient to check endpoint /select-template/{technology_name}")
    
    client = TestClient(app)
    response = client.get(f"/select-template/{technology_name}")
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Success! TestClient returned 200 OK")
    elif response.status_code == 404:
        print("Error: TestClient returned 404 Not Found")
        print(f"Response text: {response.text}")
        debug_database(technology_name)
    else:
        print(f"Unexpected status code: {response.status_code}")
        print(f"Response text: {response.text}")

def debug_database(technology_name):
    """Debug the database content for the technology"""
    db = SessionLocal()
    try:
        print("\n--- Database Debugging ---")
        
        # 1. Check if technology exists
        technology = db.query(Technology).filter(
            Technology.name.ilike(technology_name)
        ).first()
        
        if not technology:
            print(f"Technology '{technology_name}' NOT FOUND in database")
            
            # List available technologies
            techs = db.query(Technology.name, Technology.id, Technology.active).all()
            print("\nAvailable technologies:")
            for t in techs:
                print(f"- {t.name} (ID: {t.id}, Active: {t.active})")
                
            return
        
        print(f"Technology found: ID={technology.id}, Name={technology.name}, Active={technology.active}")
        
        # 2. Check if templates exist for this technology
        templates = db.query(Template).filter(
            Template.technology_id == technology.id
        ).all()
        
        if templates:
            print(f"\nFound {len(templates)} templates for {technology.name}:")
            for tpl in templates:
                default_status = " (DEFAULT)" if tpl.is_default else ""
                print(f"- ID={tpl.id}, Name={tpl.name}, Type={tpl.template_type}{default_status}")
        else:
            print(f"\nNo templates found for {technology.name}")
            print("This might be causing the 404 error - the endpoint expects templates to exist")
        
        # 3. Check for any DB relationship issues
        print("\nChecking technology fields:")
        for column in Technology.__table__.columns:
            value = getattr(technology, column.name)
            print(f"  {column.name}: {value}")
            
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db.close()

def debug_templates_html():
    """Check if template file exists"""
    template_path = Path("app/templates/select_template.html")
    if template_path.exists():
        print(f"\nTemplate file found: {template_path}")
        with open(template_path, 'r') as f:
            first_10_lines = [next(f) for _ in range(10)]
        print("First 10 lines of the template file:")
        print(''.join(first_10_lines))
    else:
        print(f"\nTemplate file NOT FOUND: {template_path}")

if __name__ == "__main__":
    print("===== Debugging Select-Template Endpoint =====")
    debug_database("tsmc_28nm")
    debug_templates_html()
    print("\n===== Attempting Direct HTTP Request =====")
    debug_endpoint_directly()
    print("\n===== Using TestClient =====")
    debug_with_testclient()
