#!/usr/bin/env python3
"""
Debug the /technologies/stats endpoint issue
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def debug_technologies_stats():
    """Debug what's causing the technologies stats to not load"""
    
    print("Debugging /technologies/stats Endpoint")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports...")
    try:
        from app.database.database import SessionLocal
        from app.database.models import Technology
        from app.crud.technology import TechnologyCRUD
        print("   [OK] All imports successful")
    except Exception as e:
        print(f"   [ERROR] Import failed: {e}")
        return
    
    # Test database connection and query
    print("\n2. Testing database and TechnologyCRUD.get_all_with_stats...")
    db = SessionLocal()
    
    try:
        # Test the method directly
        result = TechnologyCRUD.get_all_with_stats(db)
        print(f"   [OK] Method returned {len(result)} technologies")
        
        if result:
            print("\n   Sample technology data:")
            tech = result[0]
            for key, value in tech.items():
                print(f"   - {key}: {value}")
        else:
            print("   [WARNING] No technologies found in database")
        
        # Check Technology model attributes
        print("\n3. Checking Technology model attributes...")
        tech_obj = db.query(Technology).first()
        if tech_obj:
            print("   Available attributes:")
            for attr in ['name', 'description', 'node_size', 'foundry', 'created_at', 'updated_at']:
                try:
                    value = getattr(tech_obj, attr)
                    print(f"   - {attr}: {value}")
                except AttributeError:
                    print(f"   - {attr}: [MISSING]")
        
    except Exception as e:
        print(f"   [ERROR] Query failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    # Test the endpoint via HTTP
    print("\n4. Testing the endpoint via HTTP...")
    try:
        import requests
        response = requests.get("http://localhost:8000/technologies/stats")
        print(f"   Status Code: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"   [OK] Endpoint returned {len(data)} technologies")
        else:
            print(f"   [ERROR] Endpoint returned error: {response.text}")
    except Exception as e:
        print(f"   [ERROR] HTTP request failed: {e}")

if __name__ == "__main__":
    debug_technologies_stats()
