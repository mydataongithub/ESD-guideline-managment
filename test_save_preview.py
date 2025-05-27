#!/usr/bin/env python3
"""
Test the save preview functionality
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_save_preview():
    """Test that save preview functionality is properly installed"""
    
    print("Testing Save Preview Implementation")
    print("=" * 50)
    
    # Check if endpoint was added
    print("\n1. Checking if save-preview endpoint exists...")
    endpoints_path = Path("app/api/endpoints.py")
    if endpoints_path.exists():
        content = endpoints_path.read_text(encoding='utf-8')
        if "@router.post(\"/save-preview/" in content:
            print("   [OK] Save-preview endpoint found in endpoints.py")
        else:
            print("   [ERROR] Save-preview endpoint NOT found in endpoints.py")
    else:
        print("   [ERROR] endpoints.py not found")
    
    # Check if template was updated
    print("\n2. Checking if save button exists in template...")
    template_path = Path("app/templates/guideline.html")
    if template_path.exists():
        content = template_path.read_text(encoding='utf-8')
        if "savePreviewBtn" in content:
            print("   [OK] Save button found in guideline.html")
        else:
            print("   [ERROR] Save button NOT found in guideline.html")
    else:
        print("   [ERROR] guideline.html not found")
    
    # Check if beautifulsoup4 is installed
    print("\n3. Checking dependencies...")
    try:
        import bs4
        print("   [OK] beautifulsoup4 is installed")
    except ImportError:
        print("   [ERROR] beautifulsoup4 NOT installed")
        print("   Run: pip install beautifulsoup4")
    
    # Check guidelines repo exists
    print("\n4. Checking guidelines repository...")
    repo_path = Path("guidelines_repo")
    if repo_path.exists() and repo_path.is_dir():
        print(f"   [OK] Guidelines repository exists at: {repo_path.absolute()}")
    else:
        print("   [WARNING] Guidelines repository not found, will be created on first save")
    
    print("\n" + "=" * 50)
    print("\nTest URLs to try:")
    print("1. Preview with save button:")
    print("   http://localhost:8000/preview/tsmc_28nm")
    print("\n2. Template selection:")
    print("   http://localhost:8000/select-template/tsmc_28nm")
    print("\n3. After clicking 'Save as Guideline', check:")
    print("   - guidelines_repo/tsmc_28nm/ folder")
    print("   - Your Downloads folder for HTML file")
    
    print("\nRemember to restart your server for changes to take effect!")

if __name__ == "__main__":
    test_save_preview()
