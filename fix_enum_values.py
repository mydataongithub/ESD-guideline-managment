#!/usr/bin/env python3
"""
Fix enum values in the database to match the expected format
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def fix_enum_values():
    """Fix rule_type enum values in the database"""
    
    from app.database.database import SessionLocal
    from app.database.models import Rule
    from sqlalchemy import text
    
    db = SessionLocal()
    
    try:
        print("Fixing rule_type enum values in database...")
        
        # Get rules with lowercase enum values
        print("Checking current enum values...")
        result = db.execute(text("SELECT DISTINCT rule_type FROM rules")).fetchall()
        print(f"Current rule_type values: {[row[0] for row in result]}")
        
        # Update lowercase to uppercase
        updates = [
            ("esd", "ESD"),
            ("latchup", "LATCHUP"), 
            ("general", "GENERAL")
        ]
        
        for old_val, new_val in updates:
            count = db.execute(
                text("UPDATE rules SET rule_type = :new_val WHERE rule_type = :old_val"),
                {"old_val": old_val, "new_val": new_val}
            ).rowcount
            
            if count > 0:
                print(f"Updated {count} rules from '{old_val}' to '{new_val}'")
        
        # Commit the changes
        db.commit()
        
        # Verify the fix
        print("\nVerifying fix...")
        result = db.execute(text("SELECT DISTINCT rule_type FROM rules")).fetchall()
        print(f"Updated rule_type values: {[row[0] for row in result]}")
        
        print("\n✅ Database enum values fixed!")
        
    except Exception as e:
        print(f"❌ Error fixing enum values: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Database Enum Fix")
    print("=" * 30)
    fix_enum_values()
