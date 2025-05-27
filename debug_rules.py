#!/usr/bin/env python3
"""
Debug the specific parts of the rules endpoint
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def debug_rules_logic():
    """Debug the rules dashboard logic step by step"""
    
    from app.database.database import SessionLocal
    from app.crud.rule import RuleCRUD
    from app.crud.technology import TechnologyCRUD
    from app.database.models import Rule
    
    db = SessionLocal()
    
    try:
        print("Step 1: Testing database connection...")
        rule_count = db.query(Rule).count()
        print(f"Total rules in database: {rule_count}")
        
        print("\nStep 2: Testing TechnologyCRUD...")
        technologies = TechnologyCRUD.get_multi(db)
        print(f"Found {len(technologies)} technologies")
        for tech in technologies:
            print(f"  - {tech.name} (ID: {tech.id})")
        
        print("\nStep 3: Testing RuleCRUD.get_stats...")
        stats = RuleCRUD.get_stats(db)
        print(f"Rule stats: {stats}")
        
        print("\nStep 4: Testing simple rule query...")
        rules = db.query(Rule).filter(Rule.is_active == True).limit(5).all()
        print(f"Found {len(rules)} active rules")
        for rule in rules:
            print(f"  - {rule.title} (Type: {rule.rule_type})")
        
        print("\nStep 5: Testing RuleCRUD.search...")
        search_results = RuleCRUD.search(db, query="test", skip=0, limit=5)
        print(f"Search results: {len(search_results)} rules")
        
        print("\n✅ All basic operations successful!")
        
    except Exception as e:
        print(f"❌ Error in step: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Rules Logic Debug")
    print("=" * 30)
    debug_rules_logic()
