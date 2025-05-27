#!/usr/bin/env python3
"""
Add Save Preview button to preview endpoints to save exactly what's shown with images
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def create_preview_save_endpoint():
    """Create endpoint to save preview content"""
    
    endpoint_code = '''# Add to app/api/endpoints.py

@router.post("/save-preview/{technology_name}")
async def save_preview_as_guideline(
    technology_name: str,
    template_id: int = None,
    db: Session = Depends(get_db)
):
    """Save the preview content as the official guideline"""
    try:
        # Get technology
        from app.crud.technology import TechnologyCRUD
        from app.database.models import Technology
        
        technology = db.query(Technology).filter(
            Technology.name.ilike(technology_name)
        ).first()
        
        if not technology:
            raise HTTPException(status_code=404, detail=f"Technology '{technology_name}' not found")
        
        # Generate the preview HTML with images
        html_content = db_generator.render_guideline_document(
            db, 
            technology.id, 
            "guideline.html",
            custom_template_id=template_id
        )
        
        # Save HTML version with images
        tech_dir = GUIDELINES_REPO_PATH / technology_name
        tech_dir.mkdir(parents=True, exist_ok=True)
        
        html_file_path = tech_dir / "esd_latchup_guidelines.html"
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Convert to Markdown while preserving image references
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content and structure
        markdown_lines = []
        
        # Title
        title = soup.find('h1')
        if title:
            markdown_lines.append(f"# {title.get_text().strip()}")
            markdown_lines.append("")
        
        # Process all sections
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'img', 'div']):
            if element.name == 'h1':
                markdown_lines.append(f"# {element.get_text().strip()}")
            elif element.name == 'h2':
                markdown_lines.append(f"## {element.get_text().strip()}")
            elif element.name == 'h3':
                markdown_lines.append(f"### {element.get_text().strip()}")
            elif element.name == 'h4':
                markdown_lines.append(f"#### {element.get_text().strip()}")
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    markdown_lines.append(text)
            elif element.name == 'img':
                # Save image data
                src = element.get('src', '')
                alt = element.get('alt', 'Image')
                if src.startswith('data:'):
                    # Extract base64 image
                    import base64
                    match = re.match(r'data:([^;]+);base64,(.+)', src)
                    if match:
                        mime_type, image_data = match.groups()
                        # Save image file
                        ext = mime_type.split('/')[-1]
                        img_filename = f"image_{len(markdown_lines)}.{ext}"
                        img_path = tech_dir / img_filename
                        img_bytes = base64.b64decode(image_data)
                        with open(img_path, 'wb') as f:
                            f.write(img_bytes)
                        markdown_lines.append(f"![{alt}]({img_filename})")
                else:
                    markdown_lines.append(f"![{alt}]({src})")
            elif element.name == 'ul':
                for li in element.find_all('li'):
                    markdown_lines.append(f"- {li.get_text().strip()}")
            elif element.name == 'ol':
                for i, li in enumerate(element.find_all('li'), 1):
                    markdown_lines.append(f"{i}. {li.get_text().strip()}")
            
            # Add spacing
            if element.name in ['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'img']:
                markdown_lines.append("")
        
        # Save markdown version
        markdown_content = "\\n".join(markdown_lines)
        md_file_path = tech_dir / "esd_latchup_guidelines.md"
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Commit to Git
        commit_success = git_utils.commit_guideline(md_file_path, technology_name)
        
        return {
            "success": True,
            "message": f"Preview saved as guideline for {technology_name}",
            "html_path": str(html_file_path.relative_to(GUIDELINES_REPO_PATH)),
            "markdown_path": str(md_file_path.relative_to(GUIDELINES_REPO_PATH)),
            "committed": commit_success
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving preview: {str(e)}")
'''
    
    print("Save Preview Endpoint Code:")
    print("=" * 50)
    print(endpoint_code)
    
    # Save to file
    endpoint_file = Path("save_preview_endpoint.py")
    endpoint_file.write_text(endpoint_code, encoding='utf-8')
    print(f"\nEndpoint code saved to: {endpoint_file}")
    
    return endpoint_code

def update_guideline_template():
    """Update guideline.html template to include Save Preview button"""
    
    template_update = '''<!-- Add this to app/templates/guideline.html after the <h1> title -->

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
</style>

<button id="savePreviewBtn" class="save-preview-btn">Save Preview as Guideline</button>
<div id="saveStatus" class="save-status"></div>

<script>
document.getElementById('savePreviewBtn').addEventListener('click', async function() {
    const btn = this;
    const statusDiv = document.getElementById('saveStatus');
    
    // Get technology name from URL
    const pathParts = window.location.pathname.split('/');
    let technologyName = '';
    
    if (pathParts.includes('preview')) {
        const previewIndex = pathParts.indexOf('preview');
        technologyName = pathParts[previewIndex + 1];
    } else if (pathParts.includes('guidelines')) {
        // For /guidelines/{id}/preview format, we need to get the technology name differently
        technologyName = document.querySelector('h1').textContent.match(/(.+?)\\s+ESD/)[1].toLowerCase().replace(/\\s+/g, '_');
    }
    
    if (!technologyName) {
        showStatus('Error: Could not determine technology name', 'error');
        return;
    }
    
    // Get template_id from URL params if present
    const urlParams = new URLSearchParams(window.location.search);
    const templateId = urlParams.get('template_id');
    
    // Disable button and show loading
    btn.disabled = true;
    btn.textContent = 'Saving...';
    
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
        showStatus('Preview saved successfully! Files saved: ' + result.markdown_path, 'success');
        btn.textContent = 'Saved ✓';
        
        // Download HTML version
        const htmlBlob = new Blob([document.documentElement.outerHTML], { type: 'text/html' });
        const downloadUrl = URL.createObjectURL(htmlBlob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${technologyName}_guidelines.html`;
        link.click();
        URL.revokeObjectURL(downloadUrl);
        
        // Reset button after delay
        setTimeout(() => {
            btn.textContent = 'Save Preview as Guideline';
            btn.disabled = false;
        }, 3000);
        
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
        btn.textContent = 'Save Preview as Guideline';
        btn.disabled = false;
    }
    
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `save-status ${type}`;
        statusDiv.style.display = 'block';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
});
</script>'''
    
    print("\n\nGuideline Template Update:")
    print("=" * 50)
    print(template_update)
    
    # Read current guideline.html
    guideline_path = Path("app/templates/guideline.html")
    if guideline_path.exists():
        current_content = guideline_path.read_text(encoding='utf-8')
        
        # Find where to insert (after the first h1)
        h1_end = current_content.find('</h1>')
        if h1_end != -1:
            # Insert after the h1
            new_content = (
                current_content[:h1_end + 5] + 
                "\n\n" + template_update + "\n" +
                current_content[h1_end + 5:]
            )
            
            # Save backup
            backup_path = guideline_path.with_suffix('.html.bak2')
            backup_path.write_text(current_content, encoding='utf-8')
            
            # Save updated version
            guideline_path.write_text(new_content, encoding='utf-8')
            print(f"\nUpdated: {guideline_path}")
            print(f"Backup saved: {backup_path}")
        else:
            print("\nCould not find insertion point in guideline.html")
    else:
        print(f"\nGuideline template not found at: {guideline_path}")
    
    return template_update

def update_select_template_to_use_preview():
    """Update select_template.html to use the save-preview endpoint"""
    
    js_update = '''// Replace the existing generate button handler with this:

document.getElementById('generateBtn').addEventListener('click', async function() {
    if (!selectedTemplateId) {
        alert('Please select a template first');
        return;
    }
    
    // First, open the preview
    let previewUrl = `/preview/${technologyName}`;
    if (selectedTemplateId !== 'builtin') {
        previewUrl += `?template_id=${selectedTemplateId}`;
    }
    
    // Open preview in new window
    const previewWindow = window.open(previewUrl, '_blank');
    
    // Show instructions
    alert(`Preview opened in new window!\\n\\nTo save the guideline:\\n1. Click the "Save Preview as Guideline" button in the preview window\\n2. The exact preview content will be saved with images\\n3. An HTML file will also be downloaded`);
    
    // Optionally redirect to dashboard after delay
    setTimeout(() => {
        if (confirm('Go back to dashboard?')) {
            window.location.href = '/dashboard';
        }
    }, 2000);
});'''
    
    print("\n\nSelect Template JS Update:")
    print("=" * 50)
    print(js_update)
    
    return js_update

def main():
    print("Save Preview Implementation")
    print("=" * 50)
    
    print("\nThis solution adds a 'Save Preview as Guideline' button that:")
    print("1. Saves exactly what you see in the preview")
    print("2. Preserves all images by extracting them from base64")
    print("3. Creates both HTML and Markdown versions")
    print("4. Commits to Git repository")
    
    print("\n1. Creating save-preview endpoint...")
    create_preview_save_endpoint()
    
    print("\n2. Updating guideline.html template...")
    update_guideline_template()
    
    print("\n3. Updating select_template.html behavior...")
    update_select_template_to_use_preview()
    
    print("\n\nImplementation Steps:")
    print("1. Add the save-preview endpoint to app/api/endpoints.py")
    print("2. The guideline.html template has been updated (if it exists)")
    print("3. Update select_template.html with the new JS handler")
    print("4. Install required dependencies: pip install beautifulsoup4")
    print("5. Restart your server")
    
    print("\n\nHow to use:")
    print("1. Go to template selection page")
    print("2. Select your template and click 'Generate & Save'")
    print("3. In the preview window, click 'Save Preview as Guideline'")
    print("4. The exact preview content will be saved with images!")

if __name__ == "__main__":
    main()
