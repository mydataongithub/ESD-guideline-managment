# app/core/db_generator.py
"""Database-driven guideline generator"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session, selectinload
from jinja2 import Template, Environment, FileSystemLoader
import os
import base64

from app.database.models import Technology, Rule, RuleType, Template as DBTemplate, RuleImage
from app.crud.technology import TechnologyCRUD
from app.crud.rule import RuleCRUD

GUIDELINES_REPO_PATH = Path(__file__).parent.parent.parent / "guidelines_repo"

def generate_guideline_from_database(db: Session, guideline_id: int) -> Dict[str, Any]:
    """Generate guideline document data with all associated rules and images"""
    
    # For now, we'll use technology_id as guideline_id since we don't have a separate Guideline model
    # Fetch technology with eager loading of rules and images
    technology = db.query(Technology).options(
        selectinload(Technology.rules).selectinload(Rule.images)
    ).filter(Technology.id == guideline_id).first()
    
    if not technology:
        raise ValueError(f"Technology with ID {guideline_id} not found")
    
    # Prepare document data structure
    document_data = {
        "title": f"{technology.name.replace('_', ' ').title()} ESD & Latchup Design Guidelines",
        "description": technology.description or "Comprehensive ESD and Latchup design guidelines",
        "version": technology.version or "1.0",
        "technology_name": technology.name.replace('_', ' ').title(),
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "foundry": technology.foundry or "N/A",
        "node_size": technology.node_size or "N/A",
        "process_type": technology.process_type or "N/A",
        "rules": []
    }
    
    # Process each rule with its images
    for rule in technology.rules:
        if not rule.is_active:
            continue
            
        rule_data = {
            "id": rule.id,
            "title": rule.title,
            "content": rule.content,
            "order": rule.order_index,
            "type": rule.rule_type.value,
            "severity": rule.severity,
            "category": rule.category,
            "explanation": rule.explanation,
            "implementation_notes": rule.implementation_notes,
            "references": rule.references,
            "images": []
        }
        
        # Process associated images
        for image in rule.images:
            # Convert binary image data to base64 for embedding
            image_base64 = base64.b64encode(image.image_data).decode('utf-8')
            image_data = {
                "id": image.id,
                "filename": image.filename,
                "url": f"data:{image.mime_type or 'image/png'};base64,{image_base64}",
                "description": image.description or image.caption or f"Image for {rule.title}",
                "alt_text": f"{rule.title} - {image.description or image.caption or 'Illustration'}",
                "mime_type": image.mime_type or "image/png"
            }
            rule_data["images"].append(image_data)
        
        document_data["rules"].append(rule_data)
    
    # Sort rules by type and order
    document_data["rules"].sort(key=lambda x: (x["type"], x["order"]))
    
    return document_data

def render_guideline_document(db: Session, guideline_id: int, template_path: str = "guideline.html", custom_template_id: int = None):
    """Render guideline document using Jinja2 template"""
    
    # Get document data with images
    doc_data = generate_guideline_from_database(db, guideline_id)
    
    # Setup Jinja2
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Check if custom template is requested
    if custom_template_id:
        from app.database.models import Template as DBTemplate
        custom_template = db.query(DBTemplate).filter(
            DBTemplate.id == custom_template_id
        ).first()
        
        if custom_template and custom_template.template_content:
            # Render using custom template content
            template = Environment().from_string(custom_template.template_content)
        else:
            # Fall back to default template
            if not (template_dir / template_path).exists():
                template_path = "view_guideline.html"
            template = env.get_template(template_path)
    else:
        # Check if guideline.html exists, if not use view_guideline.html
        if not (template_dir / template_path).exists():
            template_path = "view_guideline.html"
        template = env.get_template(template_path)
    
    # Group rules by type for better organization
    esd_rules = [r for r in doc_data["rules"] if r["type"] == "esd"]
    latchup_rules = [r for r in doc_data["rules"] if r["type"] == "latchup"]
    general_rules = [r for r in doc_data["rules"] if r["type"] == "general"]
    
    doc_data["esd_rules"] = esd_rules
    doc_data["latchup_rules"] = latchup_rules
    doc_data["general_rules"] = general_rules
    
    # Render template with data
    rendered_html = template.render(**doc_data)
    
    return rendered_html

def generate_guideline_from_db(technology_name: str, db: Session) -> str:
    """Generate guideline markdown content from database rules."""
    
    # Get technology
    technology = TechnologyCRUD.get_by_name(db, name=technology_name)
    if not technology:
        raise ValueError(f"Technology '{technology_name}' not found in database.")
    
    # Get all active rules for this technology with eager loading of images
    rules = db.query(Rule).options(
        selectinload(Rule.images)
    ).filter(
        Rule.technology_id == technology.id,
        Rule.is_active == True
    ).order_by(Rule.rule_type, Rule.order_index).all()
    
    # Group rules by type
    esd_rules = [r for r in rules if r.rule_type == RuleType.ESD]
    latchup_rules = [r for r in rules if r.rule_type == RuleType.LATCHUP]
    general_rules = [r for r in rules if r.rule_type == RuleType.GENERAL]
    
    # Get template for this technology (if exists)
    template = db.query(DBTemplate).filter(
        DBTemplate.technology_id == technology.id,
        DBTemplate.is_default == True,
        DBTemplate.template_type == "guideline"
    ).first()
    
    if template and template.template_content:
        # Use custom template
        return render_template_with_rules(
            template.template_content,
            technology,
            esd_rules,
            latchup_rules,
            general_rules
        )
    else:
        # Use default template
        return generate_default_guideline(
            technology,
            esd_rules,
            latchup_rules,
            general_rules
        )

def render_template_with_rules(
    template_content: str,
    technology: Technology,
    esd_rules: list,
    latchup_rules: list,
    general_rules: list
) -> str:
    """Render a Jinja2 template with rule data."""
    
    # Prepare context
    context = {
        "technology_name": technology.name.replace("_", " ").title(),
        "version": technology.version or "1.0",
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "foundry": technology.foundry or "N/A",
        "node_size": technology.node_size or "N/A",
        "process_type": technology.process_type or "N/A",
        "esd_strategy_description": format_esd_strategy(technology.esd_strategy),
        "latchup_strategy_description": format_latchup_strategy(technology.latchup_strategy),
        "esd_rules": format_rules_section(esd_rules),
        "latchup_rules": format_rules_section(latchup_rules),
        "general_rules": format_rules_section(general_rules) if general_rules else "",
        "layout_guidelines": generate_layout_guidelines(technology),
        "verification_checklist": generate_verification_checklist(esd_rules, latchup_rules)
    }
    
    # Render template
    template = Template(template_content)
    return template.render(**context)

def generate_default_guideline(
    technology: Technology,
    esd_rules: list,
    latchup_rules: list,
    general_rules: list
) -> str:
    """Generate default guideline content when no template exists."""
    
    tech_name = technology.name.replace("_", " ").title()
    
    content = f"""# {tech_name} ESD & Latchup Design Guidelines

## Document Information
- **Technology**: {tech_name}
- **Version**: {technology.version or "1.0"}
- **Generated Date**: {datetime.now().strftime("%Y-%m-%d")}
- **Foundry**: {technology.foundry or "N/A"}
- **Node Size**: {technology.node_size or "N/A"}
- **Process Type**: {technology.process_type or "N/A"}

## 1. Overview
This document provides comprehensive ESD and Latchup design guidelines for {tech_name} technology.

### 1.1 Technology Specifications
{format_technology_specs(technology)}

### 1.2 ESD Protection Strategy
{format_esd_strategy(technology.esd_strategy)}

### 1.3 Latchup Prevention Strategy
{format_latchup_strategy(technology.latchup_strategy)}

## 2. ESD Design Rules
{format_rules_section(esd_rules)}

## 3. Latchup Prevention Rules
{format_rules_section(latchup_rules)}

{f"## 4. General Design Rules{chr(10)}{format_rules_section(general_rules)}" if general_rules else ""}

## 5. Layout Guidelines
{generate_layout_guidelines(technology)}

## 6. Verification Checklist
{generate_verification_checklist(esd_rules, latchup_rules)}

## 7. References
- Technology Design Manual
- ESD/Latchup Design Guidelines
- Foundry Process Specification

---
*This document is auto-generated from the ESD & Latchup Guidelines system.*
*For questions or updates, contact the Design Team.*
"""
    
    return content

def format_technology_specs(technology: Technology) -> str:
    """Format technology specifications."""
    specs = []
    
    if technology.tech_metadata:
        meta = technology.tech_metadata
        if "vdd_core" in meta:
            specs.append(f"- Core Voltage: {meta['vdd_core']}")
        if "vdd_io" in meta:
            specs.append(f"- I/O Voltage: {meta['vdd_io']}")
        if "metal_layers" in meta:
            specs.append(f"- Metal Layers: {meta['metal_layers']}")
        if "poly_pitch" in meta:
            specs.append(f"- Poly Pitch: {meta['poly_pitch']}")
        if "fin_pitch" in meta:
            specs.append(f"- Fin Pitch: {meta['fin_pitch']}")
    
    return "\n".join(specs) if specs else "No specifications available."

def format_esd_strategy(esd_strategy: Optional[Dict[str, Any]]) -> str:
    """Format ESD strategy information."""
    if not esd_strategy:
        return "No ESD strategy defined."
    
    lines = []
    if "primary_clamp" in esd_strategy:
        lines.append(f"**Primary Clamp**: {esd_strategy['primary_clamp']}")
    if "secondary_clamp" in esd_strategy:
        lines.append(f"**Secondary Clamp**: {esd_strategy['secondary_clamp']}")
    if "hbm_target" in esd_strategy:
        lines.append(f"**HBM Target**: {esd_strategy['hbm_target']}")
    if "cdm_target" in esd_strategy:
        lines.append(f"**CDM Target**: {esd_strategy['cdm_target']}")
    
    return "\n\n".join(lines) if lines else "No ESD strategy defined."

def format_latchup_strategy(latchup_strategy: Optional[Dict[str, Any]]) -> str:
    """Format latchup strategy information."""
    if not latchup_strategy:
        return "No latchup strategy defined."
    
    lines = []
    if "guard_ring_width" in latchup_strategy:
        lines.append(f"**Guard Ring Width**: {latchup_strategy['guard_ring_width']}")
    if "well_tap_spacing" in latchup_strategy:
        lines.append(f"**Well Tap Spacing**: {latchup_strategy['well_tap_spacing']}")
    if "isolation_method" in latchup_strategy:
        lines.append(f"**Isolation Method**: {latchup_strategy['isolation_method']}")
    
    return "\n\n".join(lines) if lines else "No latchup strategy defined."

def format_rules_section(rules: list) -> str:
    """Format a section of rules with image support."""
    if not rules:
        return "No rules defined for this category."
    
    content = []
    current_category = None
    
    for rule in rules:
        # Add category header if changed
        if rule.category != current_category:
            current_category = rule.category
            content.append(f"\n### {current_category}\n")
        
        # Add rule
        content.append(f"#### {rule.title}")
        content.append(f"\n{rule.content}\n")
        
        if rule.explanation:
            content.append(f"**Explanation**: {rule.explanation}\n")
        
        if rule.implementation_notes:
            content.append(f"**Implementation Notes**: {rule.implementation_notes}\n")
        
        if rule.severity:
            severity_emoji = {
                "high": "🔴",
                "medium": "🟡", 
                "low": "🟢"
            }.get(rule.severity, "⚪")
            content.append(f"**Severity**: {severity_emoji} {rule.severity.title()}\n")
        
        if rule.references:
            content.append(f"**References**: {rule.references}\n")
        
        # Add images if available
        if hasattr(rule, 'images') and rule.images:
            content.append("\n**Visual References:**\n")
            for idx, image in enumerate(rule.images):
                # Since we're generating markdown, we can't embed binary data directly
                # We'll reference the image by its ID for later processing
                content.append(f"![{image.caption or image.description or f'Figure {idx+1}'}](image://{image.id})\n")
                if image.description:
                    content.append(f"*{image.description}*\n")
        
        content.append("")  # Empty line between rules
    
    return "\n".join(content)

def generate_layout_guidelines(technology: Technology) -> str:
    """Generate layout guidelines based on technology parameters."""
    guidelines = [
        "### General Layout Guidelines",
        "",
        "1. **Well and Substrate Taps**",
        f"   - Maximum tap spacing: {technology.latchup_strategy.get('well_tap_spacing', '20um') if technology.latchup_strategy else '20um'}",
        "   - Place taps in regular grid pattern",
        "   - Increase density near I/O and power domains",
        "",
        "2. **Guard Rings**",
        f"   - Minimum width: {technology.latchup_strategy.get('guard_ring_width', '2um') if technology.latchup_strategy else '2um'}",
        "   - Use continuous rings (not segmented)",
        "   - Connect N+ rings to VDD, P+ rings to VSS",
        "",
        "3. **ESD Protection Devices**",
        "   - Place within 50um of I/O pads",
        "   - Use top metal layers for connections",
        "   - Include redundant vias",
        "",
        "4. **Power Grid**",
        "   - Implement corner stitching for CDM protection",
        "   - Maximum via spacing at corners: 100um",
        "   - Use multiple parallel paths"
    ]
    
    return "\n".join(guidelines)

def generate_verification_checklist(esd_rules: list, latchup_rules: list) -> str:
    """Generate verification checklist."""
    checklist = [
        "### Pre-Tapeout Verification Checklist",
        "",
        "#### ESD Verification",
        "- [ ] All I/O pads have primary ESD protection",
        "- [ ] Power clamps placed and sized correctly",
        "- [ ] Cross-domain signals have proper protection",
        "- [ ] CDM corner stitching implemented",
        "- [ ] All ESD current paths verified",
        "",
        "#### Latchup Verification",
        "- [ ] Guard rings placed around sensitive circuits",
        "- [ ] Well tap density meets requirements",
        "- [ ] No butting junctions present",
        "- [ ] I/O to core spacing verified",
        "- [ ] Power domain isolation implemented",
        "",
        "#### Sign-off Requirements",
        "- [ ] DRC clean for all ESD/Latchup rules",
        "- [ ] LVS includes ESD/Latchup devices",
        "- [ ] ESD simulation completed",
        "- [ ] Design review with ESD/Latchup expert"
    ]
    
    return "\n".join(checklist)

def save_guideline(technology_name: str, markdown_content: str) -> Path:
    """Save generated guideline to file system."""
    tech_dir = GUIDELINES_REPO_PATH / technology_name
    tech_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = tech_dir / "esd_latchup_guidelines.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return file_path

def get_available_technologies_from_db(db: Session) -> list[str]:
    """Get list of available technologies from database."""
    technologies = db.query(Technology.name).filter(Technology.active == True).all()
    return [tech.name for tech in technologies]

def validate_technology_in_db(technology_name: str, db: Session) -> bool:
    """Validate that technology exists in database with rules."""
    technology = TechnologyCRUD.get_by_name(db, name=technology_name)
    if not technology:
        return False
    
    # Check if technology has any rules
    rule_count = db.query(Rule).filter(
        Rule.technology_id == technology.id,
        Rule.is_active == True
    ).count()
    
    return rule_count > 0
