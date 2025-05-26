# populate_test_data.py
"""Populate the database with test data including ESD circuits and layout rules"""

import os
import sys
import json
import base64
import requests
from datetime import datetime
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal, engine
from app.database.models import Technology, Rule, RuleImage, Template, RuleType, TemplateType
from app.crud.technology import TechnologyCRUD
from app.crud.rule import RuleCRUD

# Local ESD circuit image mappings
ESD_IMAGES = {
    "esd_clamp_circuit": "rc_trigger_clamp.svg",
    "ggNMOS_clamp": "ggnmos_clamp.svg",
    "diode_clamp": "diode_protection.svg",
    "layout_spacing": "ic_layout_example.svg",
    "guard_ring": "guard_ring_layout.svg",
    "cross_domain": "cross_domain_protection.svg",
    "latchup_structure": "latchup_structure.svg",
    "cdm_stitching": "cdm_corner_stitching.svg"
}

def load_local_image(filename):
    """Load image from local static directory"""
    try:
        image_path = Path("app/static/images/esd_circuits") / filename
        if image_path.exists():
            with open(image_path, 'rb') as f:
                return f.read()
        else:
            print(f"Warning: Image not found: {image_path}")
            return None
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        return None

def create_test_technologies(db):
    """Create test technologies"""
    technologies = [
        {
            "name": "tsmc_28nm",
            "description": "TSMC 28nm HPC+ Technology | Foundry: TSMC, Node: 28nm, FinFET, HV Support",
            "version": "1.5",
            "node_size": "28nm",
            "process_type": "CMOS",
            "foundry": "TSMC",
            "active": True,
            "tech_metadata": {
                "vdd_core": "0.9V",
                "vdd_io": "1.8V/3.3V",
                "metal_layers": 9,
                "poly_pitch": "90nm"
            },
            "esd_strategy": {
                "primary_clamp": "ggNMOS",
                "secondary_clamp": "Diode String",
                "cdm_target": "250V",
                "hbm_target": "2kV"
            },
            "latchup_strategy": {
                "guard_ring_width": "2um",
                "well_tap_spacing": "20um",
                "isolation_method": "Deep N-well"
            }
        },
        {
            "name": "gf_14nm_finfet",
            "description": "GlobalFoundries 14nm FinFET Technology | Foundry: GF, Node: 14nm, FinFET, RF Support",
            "version": "2.0",
            "node_size": "14nm",
            "process_type": "FinFET",
            "foundry": "GlobalFoundries",
            "active": True,
            "tech_metadata": {
                "vdd_core": "0.8V",
                "vdd_io": "1.8V",
                "metal_layers": 11,
                "fin_pitch": "42nm"
            },
            "esd_strategy": {
                "primary_clamp": "RC-triggered ggNMOS",
                "secondary_clamp": "SCR",
                "cdm_target": "500V",
                "hbm_target": "2kV"
            },
            "latchup_strategy": {
                "guard_ring_width": "1.5um",
                "well_tap_spacing": "15um",
                "isolation_method": "Triple Well"
            }
        },
        {
            "name": "intel_7nm",
            "description": "Intel 7nm Advanced Technology | Foundry: Intel, Node: 7nm, EUV, HV Support, RF Support",
            "version": "1.0",
            "node_size": "7nm",
            "process_type": "EUV FinFET",
            "foundry": "Intel",
            "active": True,
            "tech_metadata": {
                "vdd_core": "0.7V",
                "vdd_io": "1.5V",
                "metal_layers": 13,
                "euv_layers": 5
            },
            "esd_strategy": {
                "primary_clamp": "Advanced SCR",
                "secondary_clamp": "Cascoded ggNMOS",
                "cdm_target": "750V",
                "hbm_target": "3kV"
            },
            "latchup_strategy": {
                "guard_ring_width": "1um",
                "well_tap_spacing": "10um",
                "isolation_method": "SOI + Deep Trench"
            }
        }
    ]
    
    created_techs = []
    for tech_data in technologies:
        # Check if technology already exists
        existing = db.query(Technology).filter(Technology.name == tech_data["name"]).first()
        if not existing:
            tech = Technology(**tech_data)
            db.add(tech)
            db.commit()
            db.refresh(tech)
            created_techs.append(tech)
            print(f"Created technology: {tech.name}")
        else:
            created_techs.append(existing)
            print(f"Technology already exists: {existing.name}")
    
    return created_techs

def create_esd_rules(db, technology):
    """Create ESD-specific rules for a technology"""
    esd_rules = [
        {
            "rule_type": RuleType.ESD,
            "title": "Primary ESD Clamp Sizing",
            "content": f"For {technology.name}, the primary ESD clamp must have a minimum width of 500um for HBM 2kV protection.",
            "explanation": "The clamp width is critical for handling the peak current during an ESD event. Undersized clamps can fail catastrophically.",
            "detailed_description": """The primary ESD clamp must be sized to handle the peak ESD current without excessive voltage drop or self-heating. 
            Key considerations:
            - Width scales with HBM target (250um per 1kV)
            - Length affects trigger voltage and holding voltage
            - Multiple fingers improve current distribution
            - Layout must minimize parasitic resistance""",
            "implementation_notes": "Use multi-finger layout with 50um finger width. Include metal strapping on all fingers.",
            "references": "ESD Design Guide Rev 2.1, Section 4.3",
            "severity": "high",
            "category": "ESD Protection",
            "subcategory": "Primary Clamp",
            "order_index": 1
        },
        {
            "rule_type": RuleType.ESD,
            "title": "I/O Pad ESD Diode Placement",
            "content": f"Place ESD protection diodes within 50um of I/O pad edge in {technology.name}.",
            "explanation": "Minimizing the distance reduces parasitic resistance and improves ESD current shunting efficiency.",
            "detailed_description": """ESD protection diodes must be placed as close as possible to the I/O pad to minimize the resistance path.
            Layout guidelines:
            - Maximum 50um from pad edge to diode
            - Use top metal layers for connection
            - Avoid routing through lower metal layers
            - Include redundant vias for reliability""",
            "severity": "high",
            "category": "ESD Protection",
            "subcategory": "I/O Protection",
            "order_index": 2
        },
        {
            "rule_type": RuleType.ESD,
            "title": "Power Clamp RC Trigger Design",
            "content": "RC trigger time constant must be between 0.5us and 2us for reliable ESD detection.",
            "explanation": "The RC network distinguishes between ESD events and normal power-up. Too fast triggers on power-up, too slow misses ESD.",
            "detailed_description": """The RC trigger network is critical for proper power clamp operation:
            - R typically 10-50 kOhm (poly resistor)
            - C typically 10-50 pF (MOS capacitor)
            - Time constant τ = RC = 0.5-2 μs
            - Include ESD protection for RC network itself""",
            "severity": "medium",
            "category": "ESD Protection",
            "subcategory": "Power Clamp",
            "order_index": 3
        },
        {
            "rule_type": RuleType.ESD,
            "title": "CDM Corner Stitching",
            "content": "All power and ground buses must have corner stitching with maximum 100um spacing.",
            "explanation": "CDM events cause rapid current flow. Corner stitching prevents voltage buildup at bus discontinuities.",
            "implementation_notes": "Use at least 4 vias at each corner. Overlap metals by minimum 2um.",
            "severity": "high",
            "category": "ESD Protection",
            "subcategory": "CDM Protection",
            "order_index": 4
        },
        {
            "rule_type": RuleType.ESD,
            "title": "Cross-Domain ESD Protection",
            "content": "Signals crossing power domains require back-to-back diode protection or dedicated cross-domain clamps.",
            "explanation": "Different domains may have different potentials during ESD. Protection prevents current flow between domains.",
            "detailed_description": """Cross-domain protection strategies:
            1. Back-to-back diodes between signal and both supplies
            2. Dedicated cross-domain clamp cells
            3. Series resistance (>100 ohm) for current limiting
            4. Avoid direct connections between domains""",
            "severity": "high",
            "category": "ESD Protection",
            "subcategory": "Domain Crossing",
            "order_index": 5
        }
    ]
    
    created_rules = []
    for rule_data in esd_rules:
        rule_data["technology_id"] = technology.id
        rule = Rule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        created_rules.append(rule)
        print(f"  Created ESD rule: {rule.title}")
    
    return created_rules

def create_latchup_rules(db, technology):
    """Create Latchup-specific rules for a technology"""
    latchup_rules = [
        {
            "rule_type": RuleType.LATCHUP,
            "title": "Guard Ring Minimum Width",
            "content": f"Guard rings in {technology.name} must be minimum {technology.latchup_strategy.get('guard_ring_width', '2um')} wide.",
            "explanation": "Guard rings collect minority carriers and prevent latchup triggering. Width affects collection efficiency.",
            "detailed_description": """Guard ring design rules:
            - Minimum width set by technology DRC
            - Use maximum number of contacts allowed
            - Connect to appropriate supply (N+ to VDD, P+ to VSS)
            - Continuous ring preferred over segmented""",
            "severity": "high",
            "category": "Latchup Prevention",
            "subcategory": "Guard Rings",
            "order_index": 1
        },
        {
            "rule_type": RuleType.LATCHUP,
            "title": "Well Tap Spacing Requirements",
            "content": f"Maximum spacing between well taps: {technology.latchup_strategy.get('well_tap_spacing', '20um')}.",
            "explanation": "Well taps provide low-resistance paths to power/ground, preventing voltage buildup that triggers latchup.",
            "implementation_notes": "Place taps in regular grid pattern. Increase density near I/O and power switches.",
            "severity": "high",
            "category": "Latchup Prevention",
            "subcategory": "Well Taps",
            "order_index": 2
        },
        {
            "rule_type": RuleType.LATCHUP,
            "title": "I/O to Core Spacing",
            "content": "Maintain minimum 15um spacing between I/O circuits and core logic.",
            "explanation": "I/O circuits see higher voltages and currents. Spacing prevents latchup triggering in core.",
            "detailed_description": """Isolation techniques:
            - Physical spacing (preferred)
            - Deep N-well isolation
            - Triple-well isolation
            - Guard ring between regions""",
            "severity": "high",
            "category": "Latchup Prevention",
            "subcategory": "Layout Spacing",
            "order_index": 3
        },
        {
            "rule_type": RuleType.LATCHUP,
            "title": "Butting Junction Prohibition",
            "content": "N+ to P+ spacing must be minimum 0.5um. Direct butting is prohibited.",
            "explanation": "Butting junctions create efficient BJTs that easily trigger latchup.",
            "severity": "high",
            "category": "Latchup Prevention",
            "subcategory": "Junction Rules",
            "order_index": 4
        },
        {
            "rule_type": RuleType.LATCHUP,
            "title": "Power Switch Latchup Protection",
            "content": "Power switches require double guard rings and 2X well tap density.",
            "explanation": "Power switches see large transient currents that can trigger latchup in nearby circuits.",
            "implementation_notes": "Inner ring connected to switched power, outer ring to always-on supply.",
            "severity": "medium",
            "category": "Latchup Prevention",
            "subcategory": "Power Management",
            "order_index": 5
        }
    ]
    
    created_rules = []
    for rule_data in latchup_rules:
        rule_data["technology_id"] = technology.id
        rule = Rule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        created_rules.append(rule)
        print(f"  Created Latchup rule: {rule.title}")
    
    return created_rules

def create_general_rules(db, technology):
    """Create general design rules for a technology"""
    general_rules = [
        {
            "rule_type": RuleType.GENERAL,
            "title": "Antenna Rule Compliance",
            "content": "Maximum antenna ratio: 400:1 for gates, 1000:1 for diffusions.",
            "explanation": "Antenna rules prevent gate oxide damage during plasma etching in fabrication.",
            "severity": "medium",
            "category": "DFM Rules",
            "subcategory": "Antenna",
            "order_index": 1
        },
        {
            "rule_type": RuleType.GENERAL,
            "title": "Metal Fill Requirements",
            "content": f"Maintain metal density between 30% and 70% for all layers in {technology.name}.",
            "explanation": "Uniform metal density ensures consistent etching and prevents dishing during CMP.",
            "severity": "low",
            "category": "DFM Rules",
            "subcategory": "Density",
            "order_index": 2
        }
    ]
    
    created_rules = []
    for rule_data in general_rules:
        rule_data["technology_id"] = technology.id
        rule = Rule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        created_rules.append(rule)
        print(f"  Created General rule: {rule.title}")
    
    return created_rules

def add_images_to_rules(db, rules):
    """Add images to specific rules"""
    image_mappings = [
        ("Primary ESD Clamp Sizing", "ggNMOS_clamp", "ggNMOS clamp circuit diagram"),
        ("I/O Pad ESD Diode Placement", "diode_clamp", "ESD diode protection scheme"),
        ("Power Clamp RC Trigger Design", "esd_clamp_circuit", "RC-triggered power clamp circuit"),
        ("Guard Ring Minimum Width", "guard_ring", "Guard ring layout example"),
        ("Well Tap Spacing Requirements", "layout_spacing", "Well tap spacing illustration"),
        ("Cross-Domain ESD Protection", "cross_domain", "Cross-domain protection circuit"),
        ("CDM Corner Stitching", "cdm_stitching", "CDM corner stitching example"),
        ("Butting Junction Prohibition", "latchup_structure", "Latchup parasitic structure")
    ]
    
    for rule_title, image_key, caption in image_mappings:
        # Find the rule
        rule = next((r for r in rules if r.title == rule_title), None)
        if rule and image_key in ESD_IMAGES:
            # Load local image
            print(f"  Loading image for rule: {rule_title}")
            image_filename = ESD_IMAGES[image_key]
            image_data = load_local_image(image_filename)
            if image_data:
                # Create RuleImage entry
                rule_image = RuleImage(
                    rule_id=rule.id,
                    filename=image_filename,
                    mime_type="image/svg+xml" if image_filename.endswith('.svg') else "image/png",
                    caption=caption,
                    description=f"Illustration for {rule_title}",
                    source=f"/static/images/esd_circuits/{image_filename}",
                    order_index=0,
                    image_data=image_data,
                    created_by="system"
                )
                db.add(rule_image)
                db.commit()
                print(f"    Added image: {caption}")

def create_templates(db, technologies):
    """Create default templates for each technology"""
    template_types = [
        {
            "template_type": TemplateType.GUIDELINE,
            "name": "ESD/Latchup Design Guidelines",
            "description": "Comprehensive design guidelines for ESD and Latchup protection",
            "template_content": """# {{ technology_name }} ESD & Latchup Design Guidelines

## Document Information
- **Technology**: {{ technology_name }}
- **Version**: {{ version }}
- **Generated Date**: {{ generated_date }}
- **Foundry**: {{ foundry }}

## 1. Overview
This document provides comprehensive ESD and Latchup design guidelines for {{ technology_name }} technology.

### 1.1 ESD Protection Strategy
{{ esd_strategy_description }}

### 1.2 Latchup Prevention Strategy
{{ latchup_strategy_description }}

## 2. ESD Design Rules
{{ esd_rules }}

## 3. Latchup Prevention Rules
{{ latchup_rules }}

## 4. Layout Guidelines
{{ layout_guidelines }}

## 5. Verification Checklist
{{ verification_checklist }}

---
*This document is auto-generated. For questions, contact the Design Team.*""",
            "is_default": True
        },
        {
            "template_type": TemplateType.RULE,
            "name": "Individual Rule Template",
            "description": "Template for displaying individual rules",
            "template_content": """## Rule: {{ rule_title }}

**Type**: {{ rule_type }}  
**Severity**: {{ severity }}  
**Category**: {{ category }}

### Description
{{ rule_content }}

### Explanation
{{ explanation }}

### Implementation Notes
{{ implementation_notes }}

### References
{{ references }}""",
            "is_default": True
        }
    ]
    
    for tech in technologies:
        print(f"\nCreating templates for {tech.name}")
        for template_data in template_types:
            # Check if template exists
            existing = db.query(Template).filter(
                Template.technology_id == tech.id,
                Template.name == template_data["name"]
            ).first()
            
            if not existing:
                template = Template(
                    technology_id=tech.id,
                    **template_data,
                    version="1.0.0",
                    author="System"
                )
                db.add(template)
                db.commit()
                print(f"  Created template: {template_data['name']}")
            else:
                print(f"  Template already exists: {template_data['name']}")

def main():
    """Main function to populate test data"""
    print("Starting test data population...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create technologies
        print("\n1. Creating test technologies...")
        technologies = create_test_technologies(db)
        
        # Create rules for each technology
        print("\n2. Creating design rules...")
        all_rules = []
        for tech in technologies:
            print(f"\nCreating rules for {tech.name}:")
            esd_rules = create_esd_rules(db, tech)
            latchup_rules = create_latchup_rules(db, tech)
            general_rules = create_general_rules(db, tech)
            all_rules.extend(esd_rules + latchup_rules + general_rules)
        
        # Add images to rules
        print("\n3. Adding images to rules...")
        add_images_to_rules(db, all_rules)
        
        # Create templates
        print("\n4. Creating templates...")
        create_templates(db, technologies)
        
        print("\n✅ Test data population completed successfully!")
        
        # Print summary
        print("\nSummary:")
        print(f"- Technologies created: {len(technologies)}")
        print(f"- Total rules created: {len(all_rules)}")
        print(f"  - ESD rules: {len([r for r in all_rules if r.rule_type == RuleType.ESD])}")
        print(f"  - Latchup rules: {len([r for r in all_rules if r.rule_type == RuleType.LATCHUP])}")
        print(f"  - General rules: {len([r for r in all_rules if r.rule_type == RuleType.GENERAL])}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
