# Test Data Setup Guide

## Overview
This guide explains how to populate the ESD & Latchup Guidelines system with comprehensive test data including:
- 3 technology nodes (TSMC 28nm, GF 14nm FinFET, Intel 7nm)
- 30+ design rules (ESD, Latchup, and General)
- 8 custom ESD circuit diagrams
- Template configurations

## Prerequisites
- Python environment with dependencies installed
- Database initialized (run `init_database.py` if not done)
- Server not running (to avoid conflicts)

## Quick Setup

### Windows
```batch
setup_test_data.bat
```

### Linux/Mac
```bash
# Activate virtual environment
source venv/bin/activate

# Download ESD images
python download_esd_images.py

# Populate database
python populate_test_data.py
```

## What Gets Created

### 1. Technologies (3 total)
- **TSMC 28nm**: Standard CMOS with HV support
- **GF 14nm FinFET**: Advanced FinFET with RF support  
- **Intel 7nm**: EUV FinFET with SOI

### 2. Design Rules (30+ total)
#### ESD Rules (per technology):
- Primary ESD Clamp Sizing
- I/O Pad ESD Diode Placement
- Power Clamp RC Trigger Design
- CDM Corner Stitching
- Cross-Domain ESD Protection

#### Latchup Rules (per technology):
- Guard Ring Minimum Width
- Well Tap Spacing Requirements
- I/O to Core Spacing
- Butting Junction Prohibition
- Power Switch Latchup Protection

#### General Rules:
- Antenna Rule Compliance
- Metal Fill Requirements

### 3. ESD Circuit Diagrams (8 images)
Located in `app/static/images/esd_circuits/`:
- `ggnmos_clamp.svg` - Grounded-gate NMOS clamp
- `rc_trigger_clamp.svg` - RC-triggered power clamp
- `diode_protection.svg` - Diode protection scheme
- `cross_domain_protection.svg` - Cross-domain protection
- `latchup_structure.svg` - Latchup parasitic structure
- `cdm_corner_stitching.svg` - CDM corner stitching
- `guard_ring_layout.svg` - Guard ring layout
- `ic_layout_example.svg` - IC layout spacing

### 4. Templates
- ESD/Latchup Design Guidelines (default)
- Individual Rule Template

## Viewing the Data

### Dashboard
1. Start the server: `start_server.bat`
2. Open browser to: http://localhost:8000/dashboard
3. You'll see:
   - Technology statistics
   - Rule counts by type
   - Quick action buttons

### ESD Circuit Images
Open `app/static/images/esd_circuits/index.html` in a browser to see all circuit diagrams in a gallery view.

### Technology Management
1. Click "Manage Technologies" on dashboard
2. View technologies in card or table format
3. Click any technology to see its rules

### Rule Management  
1. Click "Manage Rules" on dashboard
2. Filter by technology or rule type
3. Click any rule to see details and images

## Customization

### Adding More Technologies
Edit `create_test_technologies()` in `populate_test_data.py`:
```python
{
    "name": "your_tech_name",
    "description": "Your description",
    "foundry": "Foundry Name",
    "node_size": "XXnm",
    # ... other fields
}
```

### Adding More Rules
Edit the relevant function in `populate_test_data.py`:
- `create_esd_rules()` for ESD rules
- `create_latchup_rules()` for Latchup rules
- `create_general_rules()` for general rules

### Adding More Images
1. Add SVG content to `PLACEHOLDER_CIRCUITS` in `download_esd_images.py`
2. Update `ESD_IMAGES` mapping in `populate_test_data.py`
3. Add to `image_mappings` in `add_images_to_rules()`

## Troubleshooting

### Images not showing
1. Check if images exist: `dir app\static\images\esd_circuits`
2. Re-run: `python download_esd_images.py`

### Database errors
1. Check if database exists
2. Run: `python init_database.py`
3. Try again

### Missing dependencies
1. Install requests: `pip install requests`
2. Check all requirements: `pip install -r requirements.txt`

## Notes
- Test data is idempotent - running multiple times won't create duplicates
- Images are stored as binary data in the database AND as files
- All test data uses realistic values based on actual technology nodes
