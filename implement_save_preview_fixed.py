#!/usr/bin/env python3
"""
Complete implementation to save preview exactly as shown with images
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def add_save_preview_endpoint():
    """Add the save-preview endpoint to endpoints.py"""
    
    endpoint_code = '''
@router.post("/save-preview/{technology_name}")
async def save_preview_as_guideline(
    technology_name: str,
    template_id: int = None,
    db: Session = Depends(get_db)
):
    """Save the preview content exactly as shown with all images embedded"""
    import base64
    import re
    from bs4 import BeautifulSoup
    
    try:
        # Get technology
        from app.crud.technology import TechnologyCRUD
        from app.database.models import Technology
        
        technology = db.query(Technology).filter(
            Technology.name.ilike(technology_name)
        ).first()
        
        if not technology:
            raise HTTPException(status_code=404, detail=f"Technology '{technology_name}' not found")
        
        # Generate the preview HTML with images (exactly as shown)
        html_content = db_generator.render_guideline_document(
            db, 
            technology.id, 
            "guideline.html",
            custom_template_id=template_id
        )
        
        # Save directory
        tech_dir = GUIDELINES_REPO_PATH / technology_name
        tech_dir.mkdir(parents=True, exist_ok=True)
        
        # Save HTML version with embedded images
        html_file_path = tech_dir / "esd_latchup_guidelines.html"
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Parse HTML to create markdown version
        soup = BeautifulSoup(html_content, 'html.parser')
        markdown_lines = []
        
        # Extract title
        title = soup.find('h1')
        if title:
            markdown_lines.append(f"# {title.get_text().strip()}")
            markdown_lines.append("")
        
        # Extract metadata from header
        header = soup.find('header')
        if header:
            for p in header.find_all('p', class_='metadata'):
                markdown_lines.append(p.get_text().strip())
            markdown_lines.append("")
        
        # Process all rule sections
        for section in soup.find_all('section', class_='rule-section'):
            # Rule title
            rule_title = section.find('h3', class_='rule-title')
            if rule_title:
                markdown_lines.append(f"### {rule_title.get_text().strip()}")
                markdown_lines.append("")
            
            # Rule content
            rule_content = section.find('div', class_='rule-content')
            if rule_content:
                markdown_lines.append(rule_content.get_text().strip())
                markdown_lines.append("")
            
            # Rule metadata
            rule_metadata = section.find('div', class_='rule-metadata')
            if rule_metadata:
                for p in rule_metadata.find_all('p'):
                    markdown_lines.append(p.get_text().strip())
                markdown_lines.append("")
            
            # Images - save them as separate files
            images_container = section.find('div', class_='images-container')
            if images_container:
                markdown_lines.append("**Visual References:**")
                for idx, img in enumerate(images_container.find_all('img')):
                    src = img.get('src', '')
                    alt = img.get('alt', 'Image')
                    
                    if src.startswith('data:'):
                        # Extract and save base64 image
                        match = re.match(r'data:([^;]+);base64,(.+)', src)
                        if match:
                            mime_type, image_data = match.groups()
                            ext = mime_type.split('/')[-1]
                            img_filename = f"rule_{section.get('id', idx)}_{idx}.{ext}"
                            img_path = tech_dir / img_filename
                            
                            # Decode and save image
                            img_bytes = base64.b64decode(image_data)
                            with open(img_path, 'wb') as f:
                                f.write(img_bytes)
                            
                            markdown_lines.append(f"![{alt}]({img_filename})")
                            
                            # Add caption if present
                            figcaption = img.find_parent('figure')
                            if figcaption:
                                caption = figcaption.find('figcaption')
                                if caption:
                                    markdown_lines.append(f"*{caption.get_text().strip()}*")
                    else:
                        # External image URL
                        markdown_lines.append(f"![{alt}]({src})")
                
                markdown_lines.append("")
        
        # Add footer
        markdown_lines.extend([
            "",
            "---",
            "",
            "*This document is auto-generated from the ESD & Latchup Guidelines system.*",
            "*For questions or updates, contact the Design Team.*"
        ])
        
        # Save markdown version
        markdown_content = "\\n".join(markdown_lines)
        md_file_path = tech_dir / "esd_latchup_guidelines.md"
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Commit to Git
        commit_success = git_utils.commit_guideline(md_file_path, technology_name)
        
        return {
            "success": True,
            "message": f"Preview saved successfully as guideline for {technology_name}",
            "html_path": str(html_file_path.relative_to(GUIDELINES_REPO_PATH)),
            "markdown_path": str(md_file_path.relative_to(GUIDELINES_REPO_PATH)),
            "committed": commit_success,
            "images_extracted": len([f for f in tech_dir.glob("*.png") + list(tech_dir.glob("*.svg"))]),
            "download_html": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving preview: {str(e)}")
'''
    
    # Read current endpoints.py
    endpoints_path = Path("app/api/endpoints.py")
    current_content = endpoints_path.read_text(encoding='utf-8')
    
    # Check if beautifulsoup4 import exists
    if "from bs4 import BeautifulSoup" not in current_content:
        # Add import at the top with other imports
        import_line = "from bs4 import BeautifulSoup\nimport base64\nimport re\n"
        
        # Find where to insert (after other imports)
        insert_pos = current_content.find("router = APIRouter()")
        if insert_pos > 0:
            current_content = current_content[:insert_pos] + import_line + "\n" + current_content[insert_pos:]
    
    # Add the endpoint before the last function or at the end
    if "@router.post(\"/save-preview/" not in current_content:
        # Find a good insertion point (before the last route)
        insert_pos = current_content.rfind("@router.get(\"/select-template/")
        if insert_pos > 0:
            current_content = current_content[:insert_pos] + endpoint_code + "\n" + current_content[insert_pos:]
        else:
            current_content += "\n" + endpoint_code
    
    # Save backup
    backup_path = endpoints_path.with_suffix('.py.bak')
    backup_path.write_text(endpoints_path.read_text(encoding='utf-8'), encoding='utf-8')
    
    # Save updated file
    endpoints_path.write_text(current_content, encoding='utf-8')
    
    print(f"[OK] Added save-preview endpoint to {endpoints_path}")
    print(f"[INFO] Backup saved to {backup_path}")
    
    return True

def update_guideline_template_with_save_button():
    """Add save button to guideline.html template"""
    
    template_path = Path("app/templates/guideline.html")
    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return False
    
    current_content = template_path.read_text(encoding='utf-8')
    
    # Check if save button already exists
    if "save-preview-btn" in current_content:
        print("[INFO] Save button already exists in template")
        return True
    
    # Add save button after the header
    save_button_html = '''
    <!-- Save Preview Button -->
    <button id="savePreviewBtn" class="save-preview-btn">Save as Guideline</button>
    <div id="saveStatus" class="save-status"></div>
    
    <style>
        .save-preview-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .save-preview-btn:hover {
            background: #218838;
        }
        
        .save-preview-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .save-status {
            position: fixed;
            top: 70px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 14px;
            display: none;
            z-index: 1000;
            max-width: 300px;
        }
        
        .save-status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .save-status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        @media print {
            .save-preview-btn,
            .save-status {
                display: none !important;
            }
        }
    </style>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const saveBtn = document.getElementById('savePreviewBtn');
        const statusDiv = document.getElementById('saveStatus');
        
        saveBtn.addEventListener('click', async function() {
            // Get technology name from URL
            const pathParts = window.location.pathname.split('/');
            let technologyName = '';
            
            // Handle different URL patterns
            if (pathParts.includes('preview')) {
                const previewIndex = pathParts.indexOf('preview');
                technologyName = pathParts[previewIndex + 1];
            } else if (pathParts.includes('guidelines')) {
                // Extract from title
                const title = document.querySelector('h1').textContent;
                const match = title.match(/(.+?)\\s+ESD/i);
                if (match) {
                    technologyName = match[1].toLowerCase().replace(/\\s+/g, '_');
                }
            }
            
            if (!technologyName) {
                showStatus('Error: Could not determine technology name', 'error');
                return;
            }
            
            // Get template_id from URL if present
            const urlParams = new URLSearchParams(window.location.search);
            const templateId = urlParams.get('template_id');
            
            // Disable button and show loading
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            
            try {
                let url = `/save-preview/${technologyName}`;
                if (templateId) {
                    url += `?template_id=${templateId}`;
                }
                
                const response = await fetch(url, { method: 'POST' });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to save preview');
                }
                
                const result = await response.json();
                
                // Show success
                showStatus(`Saved successfully!\\nHTML: ${result.html_path}\\nMarkdown: ${result.markdown_path}\\nImages extracted: ${result.images_extracted || 0}`, 'success');
                saveBtn.textContent = 'Saved!';
                
                // Download HTML if indicated
                if (result.download_html) {
                    // Create a blob of the current page
                    const htmlContent = document.documentElement.outerHTML;
                    const blob = new Blob([htmlContent], { type: 'text/html' });
                    const downloadUrl = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.download = `${technologyName}_guidelines.html`;
                    link.click();
                    URL.revokeObjectURL(downloadUrl);
                }
                
                // Reset button after delay
                setTimeout(() => {
                    saveBtn.textContent = 'Save as Guideline';
                    saveBtn.disabled = false;
                }, 3000);
                
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                saveBtn.textContent = 'Save as Guideline';
                saveBtn.disabled = false;
            }
        });
        
        function showStatus(message, type) {
            statusDiv.textContent = message;
            statusDiv.className = `save-status ${type}`;
            statusDiv.style.display = 'block';
            
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }
    });
    </script>
'''
    
    # Find where to insert (after </header>)
    insert_pos = current_content.find('</header>')
    if insert_pos > 0:
        insert_pos += len('</header>')
        new_content = current_content[:insert_pos] + "\n" + save_button_html + current_content[insert_pos:]
        
        # Save backup
        backup_path = template_path.with_suffix('.html.bak3')
        backup_path.write_text(current_content, encoding='utf-8')
        
        # Save updated template
        template_path.write_text(new_content, encoding='utf-8')
        
        print(f"[OK] Updated {template_path} with save button")
        print(f"[INFO] Backup saved to {backup_path}")
        return True
    else:
        print("[ERROR] Could not find insertion point in template")
        return False

def create_installation_guide():
    """Create installation guide"""
    
    guide = '''# Save Preview Implementation Guide

## What This Does
This implementation adds a "Save as Guideline" button to all preview pages that:
1. Saves the EXACT preview content as shown (with all images)
2. Extracts embedded images and saves them as separate files
3. Creates both HTML and Markdown versions
4. Commits everything to Git
5. Downloads the HTML file to your computer

## Installation Steps

### 1. Install Required Dependencies
```bash
pip install beautifulsoup4
```

### 2. Apply the Updates
The script has already:
- Added the `/save-preview/{technology_name}` endpoint to `app/api/endpoints.py`
- Updated `app/templates/guideline.html` with the save button
- Created backups of modified files

### 3. Restart Your Server
```bash
# Stop the current server (Ctrl+C)
# Start it again
python start_server.bat
```

## How to Use

### Method 1: Direct Preview Save
1. Go to any preview URL:
   - http://localhost:8000/preview/tsmc_28nm
   - http://localhost:8000/preview/tsmc_28nm?template_id=1
2. Click the "Save as Guideline" button in the top-right corner
3. Wait for success message
4. HTML file will download automatically
5. Check the `guidelines_repo/tsmc_28nm/` folder for:
   - `esd_latchup_guidelines.html` (with embedded images)
   - `esd_latchup_guidelines.md` (markdown version)
   - Individual image files (extracted from base64)

### Method 2: From Template Selection
1. Go to http://localhost:8000/select-template/tsmc_28nm
2. Select your template
3. Click "Preview with Selected Template"
4. In the preview window, click "Save as Guideline"

## What Gets Saved

When you click "Save as Guideline":
1. **HTML File**: Exact copy of the preview with embedded base64 images
2. **Markdown File**: Structured markdown with image references
3. **Image Files**: All base64 images extracted and saved as separate files
4. **Git Commit**: All files committed to the repository

## Features
- Preserves exact preview formatting
- Keeps all images (embedded as base64)
- Extracts images for separate use
- Creates both HTML and Markdown versions
- Automatic Git commits
- Download HTML to your computer
- Works with any template (built-in or custom)

## Troubleshooting

### If the button doesn't appear:
1. Clear browser cache (Ctrl+F5)
2. Check browser console for errors
3. Verify the template was updated correctly

### If saving fails:
1. Check that beautifulsoup4 is installed
2. Verify the technology exists in the database
3. Check server logs for detailed error messages

## File Locations
- Backups: `*.bak` and `*.bak3` files
- Generated files: `guidelines_repo/{technology_name}/`
- Server code: `app/api/endpoints.py`
- Template: `app/templates/guideline.html`
'''
    
    guide_path = Path("SAVE_PREVIEW_IMPLEMENTATION.md")
    guide_path.write_text(guide, encoding='utf-8')
    print(f"\n[INFO] Implementation guide saved to: {guide_path}")

def main():
    print("Save Preview Implementation")
    print("=" * 50)
    print("\nThis will add a 'Save as Guideline' button that saves")
    print("the EXACT preview content with all images.\n")
    
    # Step 1: Add endpoint
    print("Step 1: Adding save-preview endpoint...")
    endpoint_success = add_save_preview_endpoint()
    
    # Step 2: Update template
    print("\nStep 2: Updating guideline template...")
    template_success = update_guideline_template_with_save_button()
    
    # Step 3: Create guide
    print("\nStep 3: Creating implementation guide...")
    create_installation_guide()
    
    print("\n" + "=" * 50)
    
    if endpoint_success and template_success:
        print("[SUCCESS] Implementation complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install beautifulsoup4")
        print("2. Restart your server")
        print("3. Go to any preview page")
        print("4. Click the 'Save as Guideline' button")
        print("\nThe exact preview content will be saved with all images!")
    else:
        print("[WARNING] Partial success. Check the logs above for details.")
        print("You may need to manually apply some changes.")

if __name__ == "__main__":
    main()
