# Save Preview Implementation Guide

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
