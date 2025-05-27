#!/usr/bin/env python3
"""
Fix for template generation issue - the selected template is not being used during generation
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def create_fixed_select_template():
    """Create a fixed version of select_template.html that passes template_id during generation"""
    
    fixed_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Template - {{ technology_name }}</title>
    <link rel="stylesheet" href="{{ url_for('static', path='/styles.css') }}">
    <style>
        .template-selection {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .template-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: white;
        }
        
        .template-card:hover {
            border-color: #007bff;
            box-shadow: 0 4px 12px rgba(0,123,255,0.15);
            transform: translateY(-2px);
        }
        
        .template-card.selected {
            border-color: #007bff;
            background: #f0f7ff;
        }
        
        .template-card.default {
            border-color: #28a745;
        }
        
        .template-name {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .template-description {
            color: #666;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        
        .template-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85em;
            color: #888;
        }
        
        .default-badge {
            background: #28a745;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        
        .action-buttons {
            margin-top: 30px;
            text-align: center;
        }
        
        .btn-preview {
            background: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 0 10px;
            transition: background 0.3s;
        }
        
        .btn-preview:hover {
            background: #0056b3;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 0 10px;
            transition: background 0.3s;
        }
        
        .btn-secondary:hover {
            background: #545b62;
        }
        
        .built-in-template {
            border: 2px dashed #17a2b8;
            background: #e8f4f8;
        }
        
        .template-preview {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.85em;
            color: #555;
            max-height: 100px;
            overflow-y: auto;
        }
        
        .alert-info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 12px 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="back-link">← Back to Home</a>
        </nav>
        <h1>Select Template for {{ technology_name }}</h1>
        <p>Choose a template to generate your guideline document</p>
    </header>
    
    <main class="template-selection">
        <div class="alert-info" id="alertMessage" style="display: none;">
            <span id="alertText"></span>
        </div>
        
        <div class="template-grid">
            <!-- Built-in Template -->
            <div class="template-card built-in-template" data-template-id="builtin">
                <div class="template-name">
                    Default ESD Template
                    <span class="default-badge">BUILT-IN</span>
                </div>
                <div class="template-description">
                    Professional template with comprehensive ESD and Latchup sections, images, and metadata display.
                </div>
                <div class="template-preview">
                    Includes: Header with metadata, ESD rules section, Latchup rules section, visual references, severity indicators
                </div>
                <div class="template-meta">
                    <span>Always Available</span>
                    <span>Last Updated: Today</span>
                </div>
            </div>
            
            <!-- Custom Templates -->
            {% for template in templates %}
            <div class="template-card {% if template.is_default %}default{% endif %}" 
                 data-template-id="{{ template.id }}">
                <div class="template-name">
                    {{ template.name }}
                    {% if template.is_default %}
                    <span class="default-badge">DEFAULT</span>
                    {% endif %}
                </div>
                <div class="template-description">
                    {{ template.description or "Custom template for this technology" }}
                </div>
                {% if template.template_variables %}
                <div class="template-preview">
                    Variables: {{ template.template_variables | join(', ') }}
                </div>
                {% endif %}
                <div class="template-meta">
                    <span>By: {{ template.author or "Unknown" }}</span>
                    <span>v{{ template.version }}</span>
                </div>
            </div>
            {% endfor %}
            
            {% if not templates %}
            <div class="template-card" style="border-style: dashed; background: #f8f9fa;">
                <div class="template-name" style="color: #999;">
                    No Custom Templates
                </div>
                <div class="template-description" style="color: #999;">
                    No custom templates have been created for this technology yet.
                </div>
                <a href="/templates/create?technology={{ technology_id }}" class="btn-secondary" style="margin-top: 10px;">
                    Create Template
                </a>
            </div>
            {% endif %}
        </div>
        
        <div class="action-buttons">
            <button id="previewBtn" class="btn-preview" disabled>
                Preview with Selected Template
            </button>
            <button id="generateBtn" class="btn-secondary" disabled>
                Generating...
            </button>
        </div>
    </main>
    
    <script>
        let selectedTemplateId = null;
        const technologyName = "{{ technology_name }}";
        const technologyId = "{{ technology_id }}";
        
        function showAlert(message, type = 'info') {
            const alertDiv = document.getElementById('alertMessage');
            const alertText = document.getElementById('alertText');
            alertText.textContent = message;
            alertDiv.style.display = 'block';
            
            if (type === 'error') {
                alertDiv.style.backgroundColor = '#f8d7da';
                alertDiv.style.borderColor = '#f5c6cb';
                alertDiv.style.color = '#721c24';
            }
            
            setTimeout(() => {
                alertDiv.style.display = 'none';
            }, 5000);
        }
        
        // Handle template selection
        document.querySelectorAll('.template-card').forEach(card => {
            card.addEventListener('click', function() {
                // Remove previous selection
                document.querySelectorAll('.template-card').forEach(c => c.classList.remove('selected'));
                
                // Add selection to clicked card
                this.classList.add('selected');
                selectedTemplateId = this.dataset.templateId;
                
                // Enable buttons
                document.getElementById('previewBtn').disabled = false;
                document.getElementById('generateBtn').disabled = false;
                document.getElementById('generateBtn').textContent = 'Generate & Save';
            });
        });
        
        // Preview button
        document.getElementById('previewBtn').addEventListener('click', function() {
            if (selectedTemplateId) {
                let url = `/preview/${technologyName}`;
                if (selectedTemplateId !== 'builtin') {
                    url += `?template_id=${selectedTemplateId}`;
                }
                window.open(url, '_blank');
            }
        });
        
        // Generate button - FIXED to generate with template
        document.getElementById('generateBtn').addEventListener('click', async function() {
            if (!selectedTemplateId) {
                showAlert('Please select a template first', 'error');
                return;
            }
            
            // Show loading state
            const originalText = this.textContent;
            this.textContent = 'Generating...';
            this.disabled = true;
            
            try {
                // First, generate the HTML content with the selected template
                let previewUrl = `/preview/${technologyName}`;
                if (selectedTemplateId !== 'builtin') {
                    previewUrl += `?template_id=${selectedTemplateId}`;
                }
                
                showAlert('Generating guideline with selected template...');
                
                // Fetch the rendered HTML
                const previewResponse = await fetch(previewUrl);
                if (!previewResponse.ok) {
                    throw new Error('Failed to generate preview');
                }
                
                const htmlContent = await previewResponse.text();
                
                // Now generate the markdown version and commit
                const generateUrl = `/generate/${technologyName}`;
                const generateResponse = await fetch(generateUrl, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        template_id: selectedTemplateId === 'builtin' ? null : parseInt(selectedTemplateId)
                    })
                });
                
                if (!generateResponse.ok) {
                    const errorData = await generateResponse.json();
                    throw new Error(errorData.detail || 'Failed to generate guideline');
                }
                
                const data = await generateResponse.json();
                console.log('Generation response:', data);
                
                // Success - save HTML version
                showAlert('Guidelines generated successfully! Redirecting...');
                
                // Create a blob and download the HTML
                const blob = new Blob([htmlContent], { type: 'text/html' });
                const downloadUrl = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `${technologyName}_guidelines.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(downloadUrl);
                
                // Redirect to view after short delay
                setTimeout(() => {
                    window.location.href = `/view/${technologyName}/latest`;
                }, 1500);
                
            } catch (error) {
                console.error('Error:', error);
                showAlert('Error generating guideline: ' + error.message, 'error');
                this.textContent = originalText;
                this.disabled = false;
            }
        });
        
        // Auto-select default template
        const defaultCard = document.querySelector('.template-card.default') || 
                          document.querySelector('.template-card.built-in-template');
        if (defaultCard) {
            defaultCard.click();
        }
    </script>
</body>
</html>'''
    
    # Save the fixed template
    template_path = Path("app/templates/select_template_fixed.html")
    template_path.write_text(fixed_template, encoding='utf-8')
    print(f"Created fixed template at: {template_path}")
    
    return template_path

def update_generate_endpoint():
    """Update the generate endpoint to accept template_id parameter"""
    
    endpoint_fix = '''
# Add this to the generate_and_commit_guideline function in app/api/endpoints.py:

from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    template_id: Optional[int] = None

@router.post("/generate/{technology_name}", response_model=schemas.GuidelineResponse)
async def generate_and_commit_guideline(
    technology_name: str = FastAPIPath(..., description="The name of the technology"),
    request: GenerateRequest = None,
    db: Session = Depends(get_db)
):
    """Generates, saves, and commits guidelines for a specific technology."""
    try:
        # Validate technology exists in database
        if not db_generator.validate_technology_in_db(technology_name, db):
            raise HTTPException(
                status_code=400, 
                detail=f"Technology '{technology_name}' not found or has no rules defined"
            )
        
        # Get technology
        from app.crud.technology import TechnologyCRUD
        technology = TechnologyCRUD.get_by_name(db, name=technology_name)
        
        if request and request.template_id:
            # Generate with custom template
            html_content = db_generator.render_guideline_document(
                db, 
                technology.id, 
                custom_template_id=request.template_id
            )
            # Convert HTML to markdown for saving
            from bs4 import BeautifulSoup
            import html2text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            h = html2text.HTML2Text()
            h.ignore_links = False
            markdown_content = h.handle(str(soup))
        else:
            # Generate with default template
            markdown_content = db_generator.generate_guideline_from_db(technology_name, db)
        
        # Save to file system
        saved_file_path = db_generator.save_guideline(technology_name, markdown_content)
        
        # Also save HTML version if custom template was used
        if request and request.template_id:
            html_path = saved_file_path.with_suffix('.html')
            html_path.write_text(html_content, encoding='utf-8')
        
        # Commit to Git
        commit_success = git_utils.commit_guideline(saved_file_path, technology_name)
        
        return schemas.GuidelineResponse(
            technology=technology_name,
            message=f"Guidelines {'generated and committed' if commit_success else 'generated (no changes to commit)'} for {technology_name}.",
            file_path=str(saved_file_path.relative_to(GUIDELINES_REPO_PATH)),
            content=markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
'''
    
    print("\nEndpoint update code:")
    print(endpoint_fix)
    
    # Save the fix instructions
    fix_path = Path("TEMPLATE_GENERATION_FIX.md")
    fix_content = f"""# Template Generation Fix

## Issue
The template selection page allows users to select templates, but the selected template is not used during generation.

## Solution

### 1. Update select_template.html
Replace the current template with the fixed version that:
- Passes template_id to the generate endpoint
- Shows proper loading/success messages
- Downloads the HTML version with images

Run this to apply the fix:
```bash
python fix_template_generation.py
cp app/templates/select_template_fixed.html app/templates/select_template.html
```

### 2. Update the generate endpoint
{endpoint_fix}

### 3. Install required dependencies
```bash
pip install beautifulsoup4 html2text
```

## How it works
1. User selects a template (built-in or custom)
2. When generating:
   - The HTML is rendered with the selected template
   - HTML is converted to markdown for Git storage
   - Both HTML and markdown versions are saved
   - HTML version is downloaded to user's computer
3. User is redirected to view the generated guideline

## Testing
1. Go to http://localhost:8000/select-template/tsmc_28nm
2. Select the "Default ESD Template" 
3. Click "Generate & Save"
4. Verify that:
   - HTML file downloads with images
   - Markdown file is saved to repository
   - Preview shows the guideline with images
"""
    
    fix_path.write_text(fix_content, encoding='utf-8')
    print(f"\nFix instructions saved to: {fix_path}")

def main():
    print("Template Generation Fix")
    print("=" * 50)
    
    print("\n1. Creating fixed select_template.html...")
    template_path = create_fixed_select_template()
    
    print("\n2. Generate endpoint update instructions...")
    update_generate_endpoint()
    
    print("\n3. To apply the fix:")
    print(f"   cp {template_path} app/templates/select_template.html")
    print("   Then update the generate endpoint as shown above")
    
    print("\nDone! The fix addresses:")
    print("- Template selection not being used during generation")
    print("- Images not appearing in generated guidelines")
    print("- Better user feedback during generation")

if __name__ == "__main__":
    main()
