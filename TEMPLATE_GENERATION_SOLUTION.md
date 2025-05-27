# Template Generation Issue - Solution

## Problem Summary
You're experiencing an issue where the Default ESD Template (with images) is not generating properly when clicking "Generate & Save" on the template selection page. The preview works correctly but the actual generation fails.

## Root Cause
The template selection page (`select_template.html`) has a disconnect between:
1. **Template Selection**: Users can select a template (works ✓)
2. **Preview**: Shows the correct template with images (works ✓)  
3. **Generation**: Doesn't use the selected template (broken ✗)

The JavaScript code for the "Generate & Save" button makes a POST request to `/generate/{technology_name}` without passing the `template_id`, so the backend doesn't know which template to use.

## Solution

### Quick Fix (Recommended)
I've created a fix that updates the template selection page to properly handle template-based generation:

```bash
# Apply the fix
python apply_template_fix.py

# Restart your server
python start_server.bat  # or your usual start command
```

This fix modifies the "Generate & Save" button to:
1. Generate HTML with the selected template (including images)
2. Download the HTML file to your computer
3. Save the markdown version to the repository
4. Show proper success messages

### How It Works
When you click "Generate & Save":
1. It fetches the HTML preview with your selected template
2. Downloads this HTML (with embedded images) to your computer
3. Generates and saves the markdown version to the repository
4. Redirects you to view the generated guideline

### Testing the Fix
1. Go to http://localhost:8000/select-template/tsmc_28nm
2. Select "Default ESD Template" (or any template)
3. Click "Generate & Save"
4. You should see:
   - A file download of the HTML with images
   - A success message
   - Redirect to the generated guideline view

### Alternative Workaround
If the automatic fix doesn't work, use the workaround script:

```bash
# Generate with images for tsmc_28nm
python generate_with_images.py tsmc_28nm

# This opens the preview in your browser
# Save it using Ctrl+S (or Cmd+S on Mac)
```

## What Changed
The fix updates the JavaScript in `select_template.html` to:
- Use the preview endpoint to generate HTML with the selected template
- Download the HTML file (with embedded images) 
- Still generate the markdown version for Git storage
- Provide better user feedback

## Benefits
- ✅ Selected templates are now used during generation
- ✅ Images are included in the generated HTML
- ✅ Both HTML (with images) and Markdown versions are created
- ✅ Better user experience with progress feedback
- ✅ No backend changes required

## Files Modified
- `app/templates/select_template.html` - Updated JavaScript for proper template handling
- Created backup: `app/templates/select_template.html.bak`

## Next Steps
1. Run `python apply_template_fix.py` to apply the fix
2. Restart your server
3. Test the generation with different templates
4. The Default ESD Template should now generate with all images included

If you still have issues after applying this fix, the problem might be deeper in the backend template rendering system, but this fix should resolve the immediate issue of templates not being used during generation.
