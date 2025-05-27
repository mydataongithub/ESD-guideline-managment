#!/usr/bin/env python3
"""
Fix the min filter issue in rule_management.html template
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def fix_rule_management_template():
    """Fix the min filter issue in rule_management.html"""
    
    print("Fixing rule_management.html template")
    print("=" * 50)
    
    template_path = Path("app/templates/rule_management.html")
    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return False
    
    content = template_path.read_text(encoding='utf-8')
    
    # Find the problematic line
    old_line = "{{ [pagination.current_page * 20, pagination.total_count]|min }}"
    
    # Replace with a conditional expression
    new_line = "{{ pagination.current_page * 20 if pagination.current_page * 20 < pagination.total_count else pagination.total_count }}"
    
    if old_line in content:
        print("[FOUND] Found problematic min filter usage")
        
        # Replace it
        content = content.replace(old_line, new_line)
        
        # Save backup
        backup_path = template_path.with_suffix('.html.bak_min')
        backup_path.write_text(template_path.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"[INFO] Backup saved to {backup_path}")
        
        # Save fixed file
        template_path.write_text(content, encoding='utf-8')
        print(f"[OK] Fixed the template: {template_path}")
        
        print("\n[FIXED] Changed:")
        print(f"OLD: {old_line}")
        print(f"NEW: {new_line}")
        
        return True
    else:
        print("[ERROR] Could not find the problematic line")
        print("\nSearching for similar patterns...")
        
        # Look for any use of |min filter
        import re
        min_pattern = r'\|min\b'
        matches = re.findall(min_pattern, content)
        
        if matches:
            print(f"[FOUND] Found {len(matches)} uses of |min filter")
            # Find the lines containing |min
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if '|min' in line:
                    print(f"Line {i}: {line.strip()}")
        else:
            print("[INFO] No |min filter found in template")
        
        return False

def main():
    success = fix_rule_management_template()
    
    if success:
        print("\n" + "=" * 50)
        print("[SUCCESS] Template fixed!")
        print("\nThe /rules endpoint should now work properly.")
        print("The server should reload automatically.")
    else:
        print("\n[MANUAL FIX NEEDED]")
        print("Look for any line using |min filter and replace it with:")
        print("{{ value1 if value1 < value2 else value2 }}")

if __name__ == "__main__":
    main()
