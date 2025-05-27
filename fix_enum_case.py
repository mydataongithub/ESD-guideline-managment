#!/usr/bin/env python3
"""
Fix the enum value case mismatch in the database
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def fix_enum_values():
    """Fix lowercase enum values in the database"""
    
    print("Fixing Enum Value Case Mismatch")
    print("=" * 50)
    
    from app.database.database import SessionLocal
    from app.database.models import Rule
    
    db = SessionLocal()
    
    try:
        # First, check how many rules have lowercase enum values
        print("\n1. Checking for lowercase enum values...")
        
        # Query all rules
        all_rules = db.query(Rule).all()
        
        lowercase_count = 0
        for rule in all_rules:
            # Access the rule_type column value directly
            rule_type_value = db.execute(
                f"SELECT rule_type FROM rule WHERE id = {rule.id}"
            ).fetchone()
            
            if rule_type_value and rule_type_value[0] in ['esd', 'latchup', 'general']:
                lowercase_count += 1
        
        print(f"   Found {lowercase_count} rules with lowercase enum values")
        
        if lowercase_count > 0:
            print("\n2. Updating enum values to uppercase...")
            
            # Use raw SQL to update the values
            updates = [
                ("UPDATE rule SET rule_type = 'ESD' WHERE rule_type = 'esd'", 'esd', 'ESD'),
                ("UPDATE rule SET rule_type = 'LATCHUP' WHERE rule_type = 'latchup'", 'latchup', 'LATCHUP'),
                ("UPDATE rule SET rule_type = 'GENERAL' WHERE rule_type = 'general'", 'general', 'GENERAL')
            ]
            
            for query, old_val, new_val in updates:
                result = db.execute(query)
                count = result.rowcount
                print(f"   Updated {count} rules from '{old_val}' to '{new_val}'")
            
            db.commit()
            print("\n3. Changes committed successfully!")
            
            # Verify the fix
            print("\n4. Verifying the fix...")
            from app.crud.technology import TechnologyCRUD
            
            try:
                result = TechnologyCRUD.get_all_with_stats(db)
                print(f"   [OK] get_all_with_stats now returns {len(result)} technologies")
            except Exception as e:
                print(f"   [ERROR] Still failing: {e}")
        else:
            print("\n   No lowercase enum values found. The issue might be something else.")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to fix enum values: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def test_dashboard_after_fix():
    """Test if the dashboard loads properly after the fix"""
    print("\n5. Testing the endpoint after fix...")
    try:
        import requests
        response = requests.get("http://localhost:8000/technologies/stats")
        print(f"   Status Code: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"   [OK] Endpoint now returns {len(data)} technologies")
            if data:
                print("\n   Sample technology data:")
                tech = data[0]
                for key in ['name', 'total_rules', 'esd_rules', 'latchup_rules']:
                    print(f"   - {key}: {tech.get(key, 'N/A')}")
        else:
            print(f"   [ERROR] Endpoint still returning error: {response.text}")
    except Exception as e:
        print(f"   [ERROR] HTTP request failed: {e}")

def main():
    fix_enum_values()
    test_dashboard_after_fix()
    
    print("\n" + "=" * 50)
    print("[DONE] The dashboard Technology Overview should now load properly!")
    print("\nRefresh your browser to see the changes.")

if __name__ == "__main__":
    main()
