#!/usr/bin/env python3
"""
Fix the enum value case mismatch using raw SQL
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def fix_enum_values_raw_sql():
    """Fix lowercase enum values using raw SQL"""
    
    print("Fixing Enum Value Case Mismatch (Raw SQL)")
    print("=" * 50)
    
    from app.database.database import SessionLocal
    from sqlalchemy import text
    
    db = SessionLocal()
    
    try:
        # First, check current values
        print("\n1. Checking current enum values in database...")
        
        result = db.execute(text("SELECT DISTINCT rule_type FROM rule"))
        values = [row[0] for row in result]
        print(f"   Found distinct values: {values}")
        
        # Count lowercase values
        for val in ['esd', 'latchup', 'general']:
            result = db.execute(text(f"SELECT COUNT(*) FROM rule WHERE rule_type = :val"), {"val": val})
            count = result.scalar()
            if count > 0:
                print(f"   - '{val}': {count} rules")
        
        print("\n2. Updating enum values to uppercase...")
        
        # Update the values
        updates = [
            ("UPDATE rule SET rule_type = 'ESD' WHERE rule_type = 'esd'", 'esd', 'ESD'),
            ("UPDATE rule SET rule_type = 'LATCHUP' WHERE rule_type = 'latchup'", 'latchup', 'LATCHUP'),
            ("UPDATE rule SET rule_type = 'GENERAL' WHERE rule_type = 'general'", 'general', 'GENERAL')
        ]
        
        total_updated = 0
        for query, old_val, new_val in updates:
            result = db.execute(text(query))
            count = result.rowcount
            total_updated += count
            if count > 0:
                print(f"   Updated {count} rules from '{old_val}' to '{new_val}'")
        
        db.commit()
        print(f"\n3. Total {total_updated} rules updated and committed!")
        
        # Verify the fix
        print("\n4. Verifying the fix...")
        result = db.execute(text("SELECT DISTINCT rule_type FROM rule"))
        values = [row[0] for row in result]
        print(f"   New distinct values: {values}")
        
        # Test the CRUD method
        print("\n5. Testing TechnologyCRUD.get_all_with_stats...")
        from app.crud.technology import TechnologyCRUD
        
        try:
            result = TechnologyCRUD.get_all_with_stats(db)
            print(f"   [OK] Method now returns {len(result)} technologies")
            
            if result:
                print("\n   Sample technology stats:")
                for tech in result[:3]:  # Show first 3
                    print(f"   - {tech['name']}: {tech['total_rules']} rules " +
                          f"({tech['esd_rules']} ESD, {tech['latchup_rules']} Latchup)")
        except Exception as e:
            print(f"   [ERROR] Still failing: {e}")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to fix enum values: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def fix_crud_method():
    """Also fix the TechnologyCRUD method to be more robust"""
    print("\n6. Updating TechnologyCRUD to handle missing fields...")
    
    crud_path = Path("app/crud/technology.py")
    content = crud_path.read_text(encoding='utf-8')
    
    # Check if we need to add node_size and foundry
    if '"node_size":' not in content:
        print("   Adding node_size and foundry fields to response...")
        
        # Find where to insert the new fields
        old_code = '''            result.append({
                "id": tech.id,
                "name": tech.name,
                "description": tech.description,
                "total_rules": esd_count + latchup_count + general_count,
                "esd_rules": esd_count,
                "latchup_rules": latchup_count,
                "general_rules": general_count,
                "created_at": tech.created_at,
                "updated_at": tech.updated_at
            })'''
        
        new_code = '''            result.append({
                "id": tech.id,
                "name": tech.name,
                "description": tech.description,
                "node_size": getattr(tech, 'node_size', None),
                "foundry": getattr(tech, 'foundry', None),
                "total_rules": esd_count + latchup_count + general_count,
                "esd_rules": esd_count,
                "latchup_rules": latchup_count,
                "general_rules": general_count,
                "created_at": tech.created_at,
                "updated_at": tech.updated_at
            })'''
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            crud_path.write_text(content, encoding='utf-8')
            print("   [OK] Updated TechnologyCRUD to include node_size and foundry")
        else:
            print("   [WARNING] Could not find the exact code to update")

def test_endpoint():
    """Test if the endpoint works after fix"""
    print("\n7. Testing the endpoint...")
    try:
        import requests
        response = requests.get("http://localhost:8000/technologies/stats")
        print(f"   Status Code: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"   [OK] Endpoint returns {len(data)} technologies")
        else:
            print(f"   [ERROR] Endpoint error: {response.text}")
    except Exception as e:
        print(f"   [ERROR] HTTP request failed: {e}")

def main():
    fix_enum_values_raw_sql()
    fix_crud_method()
    test_endpoint()
    
    print("\n" + "=" * 50)
    print("[DONE] The fixes have been applied!")
    print("\n1. Database enum values updated from lowercase to uppercase")
    print("2. TechnologyCRUD updated to include node_size and foundry fields")
    print("\nThe dashboard Technology Overview should now work.")
    print("Refresh your browser to see the changes!")

if __name__ == "__main__":
    main()
