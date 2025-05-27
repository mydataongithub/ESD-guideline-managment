#!/usr/bin/env python3
"""
Check database structure and fix Technology Overview
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def check_database_structure():
    """Check the actual database structure"""
    
    print("Checking Database Structure")
    print("=" * 50)
    
    from app.database.database import SessionLocal
    from sqlalchemy import text, inspect
    
    db = SessionLocal()
    
    try:
        # Get database inspector
        inspector = inspect(db.bind)
        
        print("\n1. Available tables:")
        tables = inspector.get_table_names()
        for table in tables:
            print(f"   - {table}")
        
        # Look for rule-related tables
        rule_tables = [t for t in tables if 'rule' in t.lower()]
        print(f"\n2. Rule-related tables: {rule_tables}")
        
        # Check if it's 'rules' instead of 'rule'
        if 'rules' in tables:
            print("\n3. Checking 'rules' table structure...")
            columns = inspector.get_columns('rules')
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
            
            # Check distinct values
            result = db.execute(text("SELECT DISTINCT rule_type FROM rules"))
            values = [row[0] for row in result]
            print(f"\n4. Distinct rule_type values in 'rules' table: {values}")
            
            # Fix enum values
            print("\n5. Fixing enum values...")
            for old_val, new_val in [('esd', 'ESD'), ('latchup', 'LATCHUP'), ('general', 'GENERAL')]:
                result = db.execute(text(f"UPDATE rules SET rule_type = :new WHERE rule_type = :old"), 
                                  {"new": new_val, "old": old_val})
                if result.rowcount > 0:
                    print(f"   Updated {result.rowcount} rules from '{old_val}' to '{new_val}'")
            
            db.commit()
            print("   [OK] Changes committed")
            
            # Verify
            result = db.execute(text("SELECT DISTINCT rule_type FROM rules"))
            values = [row[0] for row in result]
            print(f"\n6. New distinct values: {values}")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def fix_technology_crud():
    """Fix the TechnologyCRUD to include missing fields"""
    print("\n\nFixing TechnologyCRUD")
    print("=" * 50)
    
    crud_path = Path("app/crud/technology.py")
    content = crud_path.read_text(encoding='utf-8')
    
    # Create backup
    backup_path = crud_path.with_suffix('.py.bak_tech')
    backup_path.write_text(content, encoding='utf-8')
    print(f"1. Created backup: {backup_path}")
    
    # Fix the get_all_with_stats method
    old_result = '''            result.append({
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
    
    new_result = '''            result.append({
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
    
    if old_result in content:
        content = content.replace(old_result, new_result)
        crud_path.write_text(content, encoding='utf-8')
        print("2. [OK] Updated get_all_with_stats to include node_size and foundry")
    else:
        print("2. [WARNING] Could not find exact code to replace")

def test_fixed_endpoint():
    """Test the endpoint after fixes"""
    print("\n\nTesting Fixed Endpoint")
    print("=" * 50)
    
    from app.database.database import SessionLocal
    from app.crud.technology import TechnologyCRUD
    
    db = SessionLocal()
    
    try:
        # Test the method directly
        print("1. Testing TechnologyCRUD.get_all_with_stats...")
        result = TechnologyCRUD.get_all_with_stats(db)
        print(f"   [OK] Returns {len(result)} technologies")
        
        if result:
            print("\n   Sample data:")
            tech = result[0]
            for key in ['name', 'node_size', 'foundry', 'total_rules', 'esd_rules', 'latchup_rules']:
                print(f"   - {key}: {tech.get(key, 'N/A')}")
        
        # Test HTTP endpoint
        print("\n2. Testing HTTP endpoint...")
        import requests
        response = requests.get("http://localhost:8000/technologies/stats")
        print(f"   Status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"   [OK] Returns {len(data)} technologies")
        else:
            print(f"   [ERROR] {response.text}")
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    check_database_structure()
    fix_technology_crud()
    test_fixed_endpoint()
    
    print("\n" + "=" * 50)
    print("[COMPLETE] Dashboard Technology Overview should now work!")
    print("\nRefresh your browser dashboard to see the technology list.")

if __name__ == "__main__":
    main()
