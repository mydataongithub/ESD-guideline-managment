# Complete Solution: Save Preview with Images

## What Has Been Implemented

I've successfully implemented a comprehensive solution that saves exactly what you see in the preview, including all images. Here's what's now available:

### 1. **"Save as Guideline" Button**
- Added to all preview pages (top-right corner)
- Saves the EXACT content as shown in preview
- Preserves all images and formatting

### 2. **What Gets Saved**
When you click "Save as Guideline":
- **HTML File**: Complete preview with embedded base64 images (`esd_latchup_guidelines.html`)
- **Markdown File**: Structured markdown version (`esd_latchup_guidelines.md`)
- **Image Files**: All images extracted and saved separately (`.png`, `.svg` files)
- **Git Commit**: Everything automatically committed to repository

### 3. **How It Works**
The save process:
1. Captures the exact HTML content from the preview
2. Saves it with all base64 images embedded
3. Extracts images and saves them as separate files
4. Creates a markdown version with image references
5. Downloads the HTML to your computer
6. Commits everything to Git

## Installation Steps

### 1. Install Dependencies
```bash
pip install beautifulsoup4
```

### 2. Files Modified
- ✅ `app/api/endpoints.py` - Added `/save-preview/{technology_name}` endpoint
- ✅ `app/templates/guideline.html` - Added save button with JavaScript
- 📄 Backups created: `.bak` and `.bak3` files

### 3. Restart Server
```bash
# Stop current server (Ctrl+C)
python start_server.bat
```

## How to Use

### Method 1: Direct Preview → Save
1. Go to preview: http://localhost:8000/preview/tsmc_28nm
2. Click "Save as Guideline" button (top-right)
3. Wait for success message
4. HTML downloads automatically
5. Check `guidelines_repo/tsmc_28nm/` for all files

### Method 2: Template Selection → Preview → Save
1. Go to: http://localhost:8000/select-template/tsmc_28nm
2. Select template (e.g., "Default ESD Template")
3. Click "Preview with Selected Template"
4. In preview window, click "Save as Guideline"

### Method 3: From Dashboard
1. Go to Dashboard
2. Select technology
3. Click "Generate Guidelines" → Select template
4. Instead of "Generate & Save", click "Preview"
5. In preview, click "Save as Guideline"

## Key Features

✅ **Exact Preview Preservation**: What you see is exactly what gets saved
✅ **Image Handling**: 
   - Base64 images remain embedded in HTML
   - Images also extracted as separate files
   - Both inline and referenced images supported
✅ **Multiple Formats**:
   - HTML with embedded images (for viewing)
   - Markdown with image references (for editing)
   - Individual image files (for reuse)
✅ **Automatic Downloads**: HTML file downloads to your computer
✅ **Git Integration**: All files committed automatically
✅ **Template Support**: Works with any template (built-in or custom)

## File Structure After Saving

```
guidelines_repo/
└── tsmc_28nm/
    ├── esd_latchup_guidelines.html  # Complete HTML with embedded images
    ├── esd_latchup_guidelines.md    # Markdown version
    ├── rule_123_0.png              # Extracted images
    ├── rule_123_1.svg              # (numbered by rule)
    └── ...
```

## Troubleshooting

### Button doesn't appear?
- Clear browser cache (Ctrl+F5)
- Check browser console (F12)
- Verify guideline.html was updated

### Save fails?
- Check beautifulsoup4 is installed
- Verify technology exists in database
- Check server console for errors

### Images missing?
- Ensure rules have images in database
- Run `python add_test_images.py` to add test images
- Check that preview shows images before saving

## Summary

The implementation now provides exactly what you requested:
- **"Generate & Save"** from template selection now properly uses the selected template
- **Preview content** is saved exactly as shown with all images
- **"Save as Guideline"** button on preview pages for direct saving
- Both HTML (with embedded images) and Markdown versions are created
- All images are preserved and also extracted as separate files

This ensures that the Default ESD Template (with images) or any other template you select will be properly saved with all visual content intact.
