#!/usr/bin/env python3
"""
Fix image extension issue in save-preview endpoint
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def fix_image_extension_issue():
    """Fix the MIME type to file extension conversion"""
    
    print("Fixing Image Extension Issue")
    print("=" * 50)
    
    # Read current endpoints.py
    endpoints_path = Path("app/api/endpoints.py")
    if not endpoints_path.exists():
        print(f"[ERROR] {endpoints_path} not found!")
        return False
    
    content = endpoints_path.read_text(encoding='utf-8')
    
    # Find the problematic line
    old_code = """                            mime_type, image_data = match.groups()
                            ext = mime_type.split('/')[-1]
                            img_filename = f"rule_{section.get('id', idx)}_{idx}.{ext}\""""
    
    # Fix: Handle SVG special case
    new_code = """                            mime_type, image_data = match.groups()
                            # Handle special cases for MIME types
                            if mime_type == 'image/svg+xml':
                                ext = 'svg'
                            elif mime_type == 'image/jpeg':
                                ext = 'jpg'
                            else:
                                ext = mime_type.split('/')[-1]
                            img_filename = f"rule_{section.get('id', idx)}_{idx}.{ext}\""""
    
    if old_code in content:
        print("[FOUND] Found problematic code")
        
        # Replace the code
        content = content.replace(old_code, new_code)
        
        # Save backup
        backup_path = endpoints_path.with_suffix('.py.bak_ext')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(endpoints_path.read_text(encoding='utf-8'))
        print(f"[INFO] Backup saved to {backup_path}")
        
        # Save fixed file
        with open(endpoints_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Fixed the extension handling in {endpoints_path}")
        
        return True
    else:
        print("[ERROR] Could not find the exact code block")
        print("\n[MANUAL FIX] In the save-preview endpoint, find this line:")
        print("  ext = mime_type.split('/')[-1]")
        print("\nReplace it with:")
        print("  # Handle special cases for MIME types")
        print("  if mime_type == 'image/svg+xml':")
        print("      ext = 'svg'")
        print("  elif mime_type == 'image/jpeg':")
        print("      ext = 'jpg'")
        print("  else:")
        print("      ext = mime_type.split('/')[-1]")
        
        return False

def rename_existing_files():
    """Rename existing incorrectly named files"""
    
    print("\n" + "=" * 50)
    print("Renaming existing files with wrong extensions...")
    
    repo_path = Path("guidelines_repo")
    if not repo_path.exists():
        print("[ERROR] guidelines_repo not found")
        return
    
    count = 0
    for tech_dir in repo_path.iterdir():
        if tech_dir.is_dir() and not tech_dir.name.startswith('.'):
            # Look for files with wrong extensions
            for wrong_file in tech_dir.glob("*.svg+xml"):
                correct_name = str(wrong_file).replace('.svg+xml', '.svg')
                correct_path = Path(correct_name)
                
                print(f"[RENAME] {wrong_file.name} -> {correct_path.name}")
                wrong_file.rename(correct_path)
                count += 1
    
    if count > 0:
        print(f"\n[OK] Renamed {count} files")
        
        # Also fix the markdown files
        print("\nUpdating markdown files to use correct extensions...")
        for tech_dir in repo_path.iterdir():
            if tech_dir.is_dir() and not tech_dir.name.startswith('.'):
                md_file = tech_dir / "esd_latchup_guidelines.md"
                if md_file.exists():
                    content = md_file.read_text(encoding='utf-8')
                    if '.svg+xml' in content:
                        content = content.replace('.svg+xml)', '.svg)')
                        md_file.write_text(content, encoding='utf-8')
                        print(f"[OK] Updated {md_file}")
    else:
        print("[INFO] No files need renaming")

def main():
    # Apply the fix
    success = fix_image_extension_issue()
    
    if success:
        print("\n[SUCCESS] Extension handling fixed!")
        print("\nThe code now properly handles:")
        print("- SVG files: image/svg+xml -> .svg")
        print("- JPEG files: image/jpeg -> .jpg")
        print("- Other files: use standard extension")
    
    # Rename existing files
    rename_existing_files()
    
    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. The server should reload automatically")
    print("2. Try 'Save as Guideline' again for fresh generation")
    print("3. Images should now have correct extensions and display properly")

if __name__ == "__main__":
    main()
