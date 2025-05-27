#!/usr/bin/env python3
"""
Test the generate endpoint functionality
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_generate_functionality():
    """Test the generate functionality step by step"""
    
    from app.database.database import SessionLocal
    from app.core import db_generator
    from app.crud.technology import TechnologyCRUD
    
    db = SessionLocal()
    
    try:
        print("Step 1: Check available technologies...")
        technologies = db_generator.get_available_technologies_from_db(db)
        print(f"Available technologies: {technologies}")
        
        print("\nStep 2: Check if 'technology_A' exists...")
        tech_exists = db_generator.validate_technology_in_db("technology_A", db)
        print(f"technology_A exists: {tech_exists}")
        
        # Try with different technology names
        for tech_name in ["technology_A", "180nm CMOS", "Test Technology"]:
            print(f"\nChecking '{tech_name}'...")
            exists = db_generator.validate_technology_in_db(tech_name, db)
            print(f"  Exists: {exists}")
            
            if exists:
                try:
                    print(f"  Attempting to generate guideline...")
                    content = db_generator.generate_guideline_from_db(tech_name, db)
                    print(f"  Generated successfully! Length: {len(content)} characters")
                    print(f"  First 200 chars: {content[:200]}...")
                    break
                except Exception as e:
                    print(f"  Generation failed: {e}")
                    import traceback
                    traceback.print_exc()
        
        print("\nStep 3: Check Technology table directly...")
        all_techs = TechnologyCRUD.get_multi(db)
        print("All technologies in database:")
        for tech in all_techs:
            print(f"  - {tech.name} (ID: {tech.id}, Active: {tech.active})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Generate Functionality Test")
    print("=" * 30)
    test_generate_functionality()
