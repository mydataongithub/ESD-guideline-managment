# Generate Endpoint Fixes Summary

## Issue
The `/generate/{technology}` endpoints were returning 405 Method Not Allowed errors because:
- The endpoint was defined as POST-only
- The UI was trying to access it with GET requests (via `window.location.href`)

## Solution Implemented

### 1. Added GET Endpoint for Generation Page
Created `/generate/{technology_name}` GET endpoint that shows a generation page with:
- Technology information
- Generate button
- Progress indicator
- Success/error feedback
- Links to view/download generated content

### 2. Created Database-Driven Generator
Since the original generator expected JSON config files, created `app/core/db_generator.py` that:
- Generates guidelines from database rules
- Groups rules by type (ESD, Latchup, General)
- Formats rules with categories and metadata
- Uses custom templates if available
- Falls back to default template format

### 3. Updated All Endpoints
Modified endpoints to use the database instead of config files:
- `/technologies` - Lists from database
- `/generate/{technology}` GET - Shows generation page
- `/generate/{technology}` POST - Generates from database
- `/status` - Uses database for technology list

### 4. Created Generation UI
New template `generate_guideline.html` provides:
- User-friendly generation interface
- Real-time progress feedback
- Success/error handling
- Direct links to view/download results

## Files Modified/Created

**New Files:**
- `/app/core/db_generator.py` - Database-driven guideline generator
- `/app/templates/generate_guideline.html` - Generation UI page
- `/test_generate_endpoints.py` - Test script

**Modified Files:**
- `/app/api/endpoints.py` - Added GET endpoint, switched to database
- `/app/templates/dashboard.html` - Fixed min() Jinja2 error
- `/app/api/template_endpoints.py` - Fixed SQLAlchemy func import
- `/download_esd_images.py` - Fixed Wikipedia download issues

## Testing

Run the test script:
```bash
python test_generate_endpoints.py
```

Or manually test:
1. Go to http://localhost:8000/dashboard
2. Select a technology from dropdown
3. Click "Generate Guidelines"
4. Click "Generate Guidelines" button on the page
5. View the generated content

## Result
- No more 405 errors
- Guidelines generate from database rules
- Proper UI feedback during generation
- All dashboard functions now work correctly
