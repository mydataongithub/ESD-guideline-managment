#!/usr/bin/env python3
"""
Debug the /rules endpoint internal server error
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def debug_rules_endpoint():
    """Debug what's causing the internal server error on /rules"""
    
    print("Debugging /rules Endpoint Error")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports...")
    try:
        from app.database.database import SessionLocal
        print("   [OK] Database import successful")
    except Exception as e:
        print(f"   [ERROR] Database import failed: {e}")
        return
    
    try:
        from app.database.models import Rule, RuleType, Technology
        print("   [OK] Models import successful")
    except Exception as e:
        print(f"   [ERROR] Models import failed: {e}")
        return
    
    try:
        from app.crud.rule import RuleCRUD
        print("   [OK] RuleCRUD import successful")
    except Exception as e:
        print(f"   [ERROR] RuleCRUD import failed: {e}")
        return
    
    # Test database connection
    print("\n2. Testing database connection...")
    db = SessionLocal()
    try:
        # Test basic query
        rule_count = db.query(Rule).count()
        print(f"   [OK] Database connected. Found {rule_count} rules")
    except Exception as e:
        print(f"   [ERROR] Database query failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test get_stats method
    print("\n3. Testing RuleCRUD.get_stats...")
    try:
        stats = RuleCRUD.get_stats(db)
        print(f"   [OK] Stats retrieved: {stats}")
    except Exception as e:
        print(f"   [ERROR] get_stats failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test template rendering
    print("\n4. Testing template existence...")
    template_path = Path("app/templates/rule_management.html")
    if template_path.exists():
        print(f"   [OK] Template exists at {template_path}")
    else:
        print(f"   [ERROR] Template not found at {template_path}")
    
    # Test pagination logic
    print("\n5. Testing pagination logic...")
    try:
        page = 1
        page_size = 20
        skip = (page - 1) * page_size
        
        rules = db.query(Rule).filter(Rule.is_active == True).offset(skip).limit(page_size).all()
        total_count = db.query(Rule).filter(Rule.is_active == True).count()
        total_pages = (total_count + page_size - 1) // page_size
        
        print(f"   [OK] Pagination works. Total: {total_count}, Pages: {total_pages}")
    except Exception as e:
        print(f"   [ERROR] Pagination failed: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()
    
    # Check for RuleType enum issue
    print("\n6. Checking RuleType enum compatibility...")
    try:
        from app.database.models import RuleType as DBRuleType
        from app.models.schemas import RuleType as SchemaRuleType
        
        print(f"   DB RuleType values: {[e.value for e in DBRuleType]}")
        print(f"   Schema RuleType values: {[e.value for e in SchemaRuleType]}")
        
        # Check if they match
        db_values = set(e.value for e in DBRuleType)
        schema_values = set(e.value for e in SchemaRuleType)
        
        if db_values == schema_values:
            print("   [OK] RuleType enums match")
        else:
            print("   [WARNING] RuleType enums don't match!")
            print(f"   DB only: {db_values - schema_values}")
            print(f"   Schema only: {schema_values - db_values}")
    except Exception as e:
        print(f"   [ERROR] RuleType check failed: {e}")

if __name__ == "__main__":
    debug_rules_endpoint()
