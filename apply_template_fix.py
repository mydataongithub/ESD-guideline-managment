#!/usr/bin/env python3
"""
Direct fix for the template generation issue - ensure Default ESD Template with images is used
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def apply_template_generation_fix():
    """Apply the fix to ensure templates with images are generated properly"""
    
    print("Applying Template Generation Fix...")
    print("=" * 50)
    
    # Read the current select_template.html
    template_path = Path("app/templates/select_template.html")
    
    if not template_path.exists():
        print(f"ERROR: {template_path} not found!")
        return False
    
    current_content = template_path.read_text(encoding='utf-8')
    
    # Find the generate button click handler
    if "Generate & Save" not in current_content:
        print("ERROR: Generate button not found in template!")
        return False
    
    # Create backup
    backup_path = template_path.with_suffix('.html.bak')
    backup_path.write_text(current_content, encoding='utf-8')
    print(f"Created backup at: {backup_path}")
    
    # Replace the generate button handler to use the preview endpoint for generation
    # This is a simpler fix that leverages the existing preview functionality
    
    new_handler = '''
        // Generate button - FIXED to use template
        document.getElementById('generateBtn').addEventListener('click', async function() {
            if (!selectedTemplateId) {
                alert('Please select a template first');
                return;
            }
            
            // Show loading state
            const originalText = this.textContent;
            this.textContent = 'Generating...';
            this.disabled = true;
            
            try {
                // Step 1: Get the preview HTML with the selected template
                let previewUrl = `/preview/${technologyName}`;
                if (selectedTemplateId !== 'builtin') {
                    previewUrl += `?template_id=${selectedTemplateId}`;
                }
                
                const previewResponse = await fetch(previewUrl);
                if (!previewResponse.ok) {
                    throw new Error('Failed to generate preview');
                }
                
                const htmlContent = await previewResponse.text();
                
                // Step 2: Generate the markdown and commit (standard endpoint)
                const generateUrl = `/generate/${technologyName}`;
                const generateResponse = await fetch(generateUrl, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!generateResponse.ok) {
                    const errorData = await generateResponse.json();
                    throw new Error(errorData.detail || 'Failed to generate guideline');
                }
                
                const data = await generateResponse.json();
                
                // Step 3: Save the HTML version locally
                const blob = new Blob([htmlContent], { type: 'text/html' });
                const downloadUrl = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = `${technologyName}_guidelines_with_images.html`;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(downloadUrl);
                
                // Show success message
                alert(`Guidelines generated successfully!\\n\\nMarkdown version saved to: ${data.file_path}\\nHTML version (with images) downloaded to your computer.`);
                
                // Redirect to view
                setTimeout(() => {
                    window.location.href = `/view/${technologyName}/latest`;
                }, 1000);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating guideline: ' + error.message);
                this.textContent = originalText;
                this.disabled = false;
            }
        });'''
    
    # Find the existing handler and replace it
    start_marker = "// Generate button"
    end_marker = "});"
    
    start_idx = current_content.find(start_marker)
    if start_idx == -1:
        print("ERROR: Could not find generate button handler!")
        return False
    
    # Find the end of the handler
    end_idx = current_content.find(end_marker, start_idx)
    # Find the next occurrence after that (to get the full handler)
    end_idx = current_content.find(end_marker, end_idx + 1)
    
    if end_idx == -1:
        print("ERROR: Could not find end of generate button handler!")
        return False
    
    # Replace the handler
    new_content = current_content[:start_idx] + new_handler + current_content[end_idx + len(end_marker):]
    
    # Write the updated content
    template_path.write_text(new_content, encoding='utf-8')
    print(f"Updated: {template_path}")
    
    return True

def create_simple_workaround():
    """Create a simple workaround script that users can run"""
    
    workaround_content = '''#!/usr/bin/env python3
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
    
    print("\\nTo save the guideline with images:")
    print("1. In your browser, press Ctrl+S (or Cmd+S on Mac)")
    print("2. Save as 'Web Page, Complete' to include images")
    print("3. Or save as 'Web Page, HTML only' for a single file")
    
    print("\\nTo generate the markdown version:")
    print(f"1. Go to http://localhost:8000/generate/{technology_name}")
    print("2. Or run: curl -X POST http://localhost:8000/generate/{technology_name}")

if __name__ == "__main__":
    import sys
    tech = sys.argv[1] if len(sys.argv) > 1 else "tsmc_28nm"
    generate_with_template(tech)
'''
    
    workaround_path = Path("generate_with_images.py")
    workaround_path.write_text(workaround_content, encoding='utf-8')
    workaround_path.chmod(0o755)  # Make executable
    print(f"\nCreated workaround script: {workaround_path}")
    
    return workaround_path

def main():
    print("Template Generation Fix Application")
    print("=" * 50)
    
    # Apply the fix
    success = apply_template_generation_fix()
    
    if success:
        print("\n✅ Fix applied successfully!")
        print("\nThe fix does the following:")
        print("1. When you click 'Generate & Save', it now:")
        print("   - Uses the selected template (Default ESD or custom)")
        print("   - Generates HTML with images included")
        print("   - Downloads the HTML file to your computer")
        print("   - Saves the markdown version to the repository")
        print("   - Redirects to view the generated guideline")
        
        print("\nTo test:")
        print("1. Restart your server")
        print("2. Go to http://localhost:8000/select-template/tsmc_28nm")
        print("3. Select 'Default ESD Template'")
        print("4. Click 'Generate & Save'")
        print("5. Check that the downloaded HTML has images")
    else:
        print("\n❌ Fix could not be applied automatically")
        print("\nCreating workaround script instead...")
        
    # Create workaround script regardless
    workaround_path = create_simple_workaround()
    print(f"\nWorkaround available: python {workaround_path} [technology_name]")

if __name__ == "__main__":
    main()
