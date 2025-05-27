# add_test_technology.py
"""Add test technology to the database"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import Technology, Rule, RuleType, Template, TemplateType
from datetime import datetime

def add_test_technology():
    """Add TSMC 28nm technology with sample rules"""
    db = SessionLocal()
    try:
        # Check if tsmc_28nm already exists
        existing = db.query(Technology).filter(
            Technology.name.ilike("tsmc_28nm")
        ).first()
        
        if existing:
            print(f"Technology 'tsmc_28nm' already exists with ID {existing.id}")
            return existing
        
        # Create new technology
        tech = Technology(
            name="tsmc_28nm",
            description="TSMC 28nm High Performance Mobile Computing Plus (HPC+) Process",
            version="1.0",
            node_size="28nm",
            process_type="CMOS",
            foundry="TSMC",
            active=True,
            tech_metadata={
                "vdd_core": "0.9V",
                "vdd_io": "1.8V/2.5V",
                "metal_layers": "9-11",
                "poly_pitch": "120nm"
            },
            esd_strategy={
                "primary_clamp": "GGNMOS",
                "secondary_clamp": "Diode String",
                "hbm_target": "2kV",
                "cdm_target": "500V"
            },
            latchup_strategy={
                "guard_ring_width": "2.4um",
                "well_tap_spacing": "25um",
                "isolation_method": "Triple Well"
            }
        )
        db.add(tech)
        db.flush()
        
        print(f"Created technology: {tech.name} (ID: {tech.id})")
        
        # Add sample ESD rules
        esd_rules = [
            {
                "title": "I/O ESD Protection Requirements",
                "content": "All I/O pads must have dual-diode ESD protection with GGNMOS clamp. Primary clamp size: W=200um, L=0.5um minimum.",
                "explanation": "Dual protection ensures robust ESD performance for both positive and negative stress conditions.",
                "category": "I/O Protection",
                "severity": "high"
            },
            {
                "title": "Power Clamp Placement",
                "content": "Place distributed power clamps every 200um along the power rail. Each clamp should be sized at W=100um minimum.",
                "explanation": "Distributed clamping reduces CDM voltage peaks and ensures uniform current distribution.",
                "category": "Power Protection",
                "severity": "high"
            },
            {
                "title": "Cross-Domain Protection",
                "content": "Signals crossing between different power domains require back-to-back diodes at domain boundaries.",
                "explanation": "Prevents ESD current from flowing between domains during stress events.",
                "category": "Domain Isolation",
                "severity": "medium"
            }
        ]
        
        for idx, rule_data in enumerate(esd_rules):
            rule = Rule(
                technology_id=tech.id,
                rule_type=RuleType.ESD,
                title=rule_data["title"],
                content=rule_data["content"],
                explanation=rule_data["explanation"],
                category=rule_data["category"],
                severity=rule_data["severity"],
                order_index=idx,
                is_active=True,
                created_by="test_script"
            )
            db.add(rule)
        
        # Add sample Latchup rules
        latchup_rules = [
            {
                "title": "Guard Ring Requirements",
                "content": "All N-wells must be surrounded by P+ guard rings with minimum width of 2.4um. Contact spacing maximum 1um.",
                "explanation": "Guard rings collect minority carriers and prevent latchup triggering.",
                "category": "Well Isolation",
                "severity": "high"
            },
            {
                "title": "I/O to Core Spacing",
                "content": "Maintain minimum 15um spacing between I/O circuits and core logic. Use double guard ring in this region.",
                "explanation": "I/O circuits can inject high currents that trigger latchup in nearby core circuits.",
                "category": "Layout Spacing",
                "severity": "high"
            }
        ]
        
        for idx, rule_data in enumerate(latchup_rules):
            rule = Rule(
                technology_id=tech.id,
                rule_type=RuleType.LATCHUP,
                title=rule_data["title"],
                content=rule_data["content"],
                explanation=rule_data["explanation"],
                category=rule_data["category"],
                severity=rule_data["severity"],
                order_index=idx,
                is_active=True,
                created_by="test_script"
            )
            db.add(rule)
        
        # Add a sample template
        template = Template(
            technology_id=tech.id,
            name="Compact ESD Template",
            description="A more compact template focusing on critical ESD rules only",
            template_type=TemplateType.GUIDELINE,
            template_content="""<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .rule { margin: 20px 0; padding: 15px; background: #f5f5f5; border-left: 4px solid #007bff; }
        .severity-high { border-left-color: #dc3545; }
        .severity-medium { border-left-color: #ffc107; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 30px; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p><strong>Technology:</strong> {{ technology_name }} | <strong>Version:</strong> {{ version }}</p>
    
    <h2>Critical ESD Rules</h2>
    {% for rule in esd_rules %}
    {% if rule.severity == "high" %}
    <div class="rule severity-{{ rule.severity }}">
        <h3>{{ rule.title }}</h3>
        <p>{{ rule.content }}</p>
        {% if rule.images %}
        <div style="margin-top: 10px;">
            {% for image in rule.images %}
            <img src="{{ image.url }}" alt="{{ image.alt_text }}" style="max-width: 100%; margin: 5px 0;">
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endif %}
    {% endfor %}
    
    <h2>Critical Latchup Rules</h2>
    {% for rule in latchup_rules %}
    {% if rule.severity == "high" %}
    <div class="rule severity-{{ rule.severity }}">
        <h3>{{ rule.title }}</h3>
        <p>{{ rule.content }}</p>
    </div>
    {% endif %}
    {% endfor %}
</body>
</html>""",
            is_default=False,
            author="Test Script",
            version="1.0.0"
        )
        db.add(template)
        
        db.commit()
        print(f"Successfully created technology '{tech.name}' with {len(esd_rules)} ESD rules and {len(latchup_rules)} Latchup rules")
        print(f"Also created 1 custom template")
        
        return tech
        
    except Exception as e:
        db.rollback()
        print(f"Error creating technology: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding TSMC 28nm test technology...")
    add_test_technology()
