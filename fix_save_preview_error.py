#!/usr/bin/env python3
"""
Fix the save preview endpoint error
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def fix_save_preview_error():
    """Fix the type error in save-preview endpoint"""
    
    print("Fixing Save Preview Error")
    print("=" * 50)
    
    # Read current endpoints.py
    endpoints_path = Path("app/api/endpoints.py")
    if not endpoints_path.exists():
        print(f"[ERROR] {endpoints_path} not found!")
        return False
    
    content = endpoints_path.read_text(encoding='utf-8')
    
    # Find the problematic line
    old_line = '"images_extracted": len([f for f in tech_dir.glob("*.png") + list(tech_dir.glob("*.svg"))]),'
    
    # Fix: Convert both glob results to lists before concatenating
    new_line = '"images_extracted": len(list(tech_dir.glob("*.png")) + list(tech_dir.glob("*.svg"))),'
    
    if old_line in content:
        print("[FOUND] Found problematic line")
        
        # Replace the line
        content = content.replace(old_line, new_line)
        
        # Save backup
        backup_path = endpoints_path.with_suffix('.py.bak_fix')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(endpoints_path.read_text(encoding='utf-8'))
        print(f"[INFO] Backup saved to {backup_path}")
        
        # Save fixed file
        with open(endpoints_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Fixed the error in {endpoints_path}")
        
        print("\n[FIXED] The problematic line:")
        print(f"OLD: {old_line}")
        print(f"NEW: {new_line}")
        
        return True
    else:
        print("[ERROR] Could not find the problematic line")
        print("Looking for alternative patterns...")
        
        # Try to find the save_preview_as_guideline function
        if "@router.post(\"/save-preview/" in content:
            print("[OK] Found save-preview endpoint")
            
            # Look for the images_extracted line
            import re
            pattern = r'"images_extracted":\s*len\([^)]+\),'
            match = re.search(pattern, content)
            
            if match:
                print(f"[FOUND] Found images_extracted line: {match.group()}")
                print("\nManually fix by changing it to:")
                print('"images_extracted": len(list(tech_dir.glob("*.png")) + list(tech_dir.glob("*.svg"))),')
            else:
                print("[ERROR] Could not find images_extracted line")
        
        return False

def test_fix():
    """Test that the fix works"""
    from pathlib import Path
    
    # Simulate the fix
    tech_dir = Path(".")
    
    try:
        # This would fail with the original code
        # result = len([f for f in tech_dir.glob("*.png") + list(tech_dir.glob("*.svg"))])
        
        # This works with the fix
        result = len(list(tech_dir.glob("*.png")) + list(tech_dir.glob("*.svg")))
        print(f"\n[TEST] Fix works! Found {result} image files")
        return True
    except Exception as e:
        print(f"\n[TEST] Error: {e}")
        return False

def main():
    # Apply the fix
    success = fix_save_preview_error()
    
    if success:
        print("\n" + "=" * 50)
        print("[SUCCESS] Error fixed!")
        print("\nNext steps:")
        print("1. The server should reload automatically")
        print("2. Try clicking 'Save as Guideline' again")
        print("3. It should now work without errors")
        
        # Test the fix
        test_fix()
    else:
        print("\n[MANUAL FIX NEEDED]")
        print("Open app/api/endpoints.py and find this line:")
        print('  "images_extracted": len([f for f in tech_dir.glob("*.png") + list(tech_dir.glob("*.svg"))])')
        print("\nChange it to:")
        print('  "images_extracted": len(list(tech_dir.glob("*.png")) + list(tech_dir.glob("*.svg")))')

if __name__ == "__main__":
    main()
