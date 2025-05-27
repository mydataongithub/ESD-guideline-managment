#!/usr/bin/env python3
"""
Simple workaround to generate guidelines with images
"""

import sys
import webbrowser
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def generate_with_template(technology_name="tsmc_28nm"):
    """Generate guidelines with the Default ESD Template (includes images)"""
    
    print(f"Generating guidelines for {technology_name} with images...")
    
    # Open the preview in browser (this will have images)
    preview_url = f"http://localhost:8000/preview/{technology_name}"
    print(f"Opening preview: {preview_url}")
    webbrowser.open(preview_url)
    
    print("\nTo save the guideline with images:")
    print("1. In your browser, press Ctrl+S (or Cmd+S on Mac)")
    print("2. Save as 'Web Page, Complete' to include images")
    print("3. Or save as 'Web Page, HTML only' for a single file")
    
    print("\nTo generate the markdown version:")
    print(f"1. Go to http://localhost:8000/generate/{technology_name}")
    print("2. Or run: curl -X POST http://localhost:8000/generate/{technology_name}")

if __name__ == "__main__":
    import sys
    tech = sys.argv[1] if len(sys.argv) > 1 else "tsmc_28nm"
    generate_with_template(tech)
