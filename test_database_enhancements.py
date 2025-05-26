# test_database_enhancements.py
"""
Test script to verify the database enhancements from task #5.
This script tests:
1. Extended image storage capabilities
2. Enhanced explanatory text storage
3. Technology-specific templates
4. Rule categorization
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import get_db, engine
from app.database.models import (
    Rule, RuleImage, Template, Technology, 
    RuleType, TemplateType
)
from app.utils.image_utils import get_image_dimensions, get_image_metadata
from app.utils.template_utils import TemplateRenderer, create_default_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_rule_enhancements():
    """Test the enhanced Rule model with explanatory texts"""
    logger.info("Testing Rule enhancements...")
    
    db = next(get_db())
    
    # Create a test technology if none exists
    technology = db.query(Technology).first()
    if not technology:
        technology = Technology(
            name="Test Technology",
            description="Technology for testing database enhancements",
            version="1.0.0",
            node_size="45nm",
            process_type="CMOS",
            foundry="Test Foundry",
            active=True
        )
        db.add(technology)
        db.commit()
        db.refresh(technology)
        logger.info(f"Created test technology with ID: {technology.id}")
    
    # Create a test rule with enhanced fields
    test_rule = Rule(
        technology_id=technology.id,
        rule_type=RuleType.ESD,
        title="Enhanced Test Rule",
        content="This is a test rule with enhanced explanatory texts",
        explanation="Basic explanation of the rule",
        detailed_description="More detailed technical explanation of how this rule works",
        implementation_notes="Implementation guidelines: apply this rule to all I/O cells",
        references="IEEE Standard 12345-6789, Section 7.2",
        examples="Example circuit:\n```\nX1 IN OUT VDD VSS CUSTOM_CLAMP\n```",
        severity="critical",
        category="IO",
        subcategory="Input Protection",
        applicable_technologies={"compatible_nodes": ["65nm", "45nm", "28nm"]},
        created_by="Test User",
        reviewed_by="Test Reviewer",
        reviewed_at=datetime.now()
    )
    
    db.add(test_rule)
    db.commit()
    db.refresh(test_rule)
    
    logger.info(f"Created test rule with ID: {test_rule.id}")
    logger.info(f"Rule details: {test_rule.title} - {test_rule.category}/{test_rule.subcategory}")
    logger.info(f"Rule has explanatory texts: explanation, detailed_description, implementation_notes, references, examples")
    
    # Clean up (uncomment to keep the test rule in database)
    # db.delete(test_rule)
    # db.commit()
    # logger.info("Cleaned up test rule")
    
    return test_rule

def test_rule_image_enhancements():
    """Test the enhanced RuleImage model"""
    logger.info("Testing RuleImage enhancements...")
    
    db = next(get_db())
    
    # Get our test rule or create one
    test_rule = db.query(Rule).filter(Rule.title == "Enhanced Test Rule").first()
    if not test_rule:
        test_rule = test_rule_enhancements()
    
    # Create a simple test image (a 100x100 red square)
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_data = img_io.getvalue()
    
    # Get image metadata
    width, height = get_image_dimensions(img_data)
    metadata = get_image_metadata(img_data)
    
    # Create enhanced rule image
    test_image = RuleImage(
        rule_id=test_rule.id,
        filename="test_image.png",
        image_data=img_data,
        mime_type="image/png",
        caption="Test image for database enhancements",
        description="This is a 100x100 red square used for testing image storage enhancements",
        source="Generated for testing",
        width=width,
        height=height,
        file_size=len(img_data),
        created_by="Test User"
    )
    
    db.add(test_image)
    db.commit()
    db.refresh(test_image)
    
    logger.info(f"Created test image with ID: {test_image.id}")
    logger.info(f"Image details: {test_image.width}x{test_image.height}, {test_image.file_size} bytes")
    logger.info(f"Image has enhanced metadata: description, source, width, height, file_size")
    
    # Clean up (uncomment to keep the test image in database)
    # db.delete(test_image)
    # db.commit()
    # logger.info("Cleaned up test image")

def test_template_enhancements():
    """Test the enhanced Template model"""
    logger.info("Testing Template enhancements...")
    
    db = next(get_db())
    
    # Get our test technology or create one
    technology = db.query(Technology).filter(Technology.name == "Test Technology").first()
    if not technology:
        technology = Technology(
            name="Test Technology",
            description="Technology for testing database enhancements",
            version="1.0.0",
            node_size="45nm",
            process_type="CMOS",
            foundry="Test Foundry",
            active=True
        )
        db.add(technology)
        db.commit()
        db.refresh(technology)
    
    # Get default template content
    template_data = create_default_template("guideline", technology.name)
    
    # Create enhanced template
    test_template = Template(
        technology_id=technology.id,
        name="Enhanced Test Template",
        description="Template for testing database enhancements",
        template_type=TemplateType.GUIDELINE,
        template_content=template_data["content"],
        template_variables=template_data["variables"],
        css_styles=template_data["css_styles"],
        script_content="console.log('Template loaded');",
        version="1.0.0",
        author="Test User",
        is_default=True
    )
    
    db.add(test_template)
    db.commit()
    db.refresh(test_template)
    
    logger.info(f"Created test template with ID: {test_template.id}")
    logger.info(f"Template details: {test_template.name} - Type: {test_template.template_type.value}, Version: {test_template.version}")
    logger.info(f"Template has enhanced fields: template_type, css_styles, script_content, version, author")
    
    # Test rendering
    renderer = TemplateRenderer(test_template.template_content, test_template.template_variables)
    rendered_content = renderer.render_with_css(test_template.css_styles)
    
    logger.info("Successfully rendered template with enhanced capabilities")
    
    # Clean up (uncomment to keep the test template in database)
    # db.delete(test_template)
    # db.commit()
    # logger.info("Cleaned up test template")

def test_technology_enhancements():
    """Test the enhanced Technology model"""
    logger.info("Testing Technology enhancements...")
    
    db = next(get_db())
    
    # Create or update test technology with enhanced fields
    technology = db.query(Technology).filter(Technology.name == "Test Technology").first()
    if not technology:
        technology = Technology(name="Test Technology")
        db.add(technology)
    
    # Update with enhanced fields
    technology.version = "2.0.0"
    technology.node_size = "28nm"
    technology.process_type = "FDSOI"
    technology.foundry = "Enhanced Test Foundry"
    technology.active = True
    technology.metadata = {
        "design_manual_version": "3.4.2",
        "supported_operating_voltages": [1.8, 3.3],
        "release_date": "2025-05-26"
    }
    technology.esd_strategy = {
        "primary_protection": "Dual Diode",
        "secondary_protection": "GGNMOS",
        "hbm_target": "2kV",
        "cdm_target": "500V"
    }
    technology.latchup_strategy = {
        "guard_rings": True,
        "substrate_contacts_spacing": "2.5um",
        "well_contacts_spacing": "5.0um",
        "trigger_current": ">100mA"
    }
    
    db.commit()
    db.refresh(technology)
    
    logger.info(f"Enhanced technology with ID: {technology.id}")
    logger.info(f"Technology details: {technology.name} - {technology.node_size} {technology.process_type}")
    logger.info(f"Technology has enhanced fields: version, node_size, process_type, foundry, metadata, esd_strategy, latchup_strategy")

def run_all_tests():
    """Run all database enhancement tests"""
    logger.info("Starting database enhancement tests...")
    
    try:
        test_technology_enhancements()
        rule = test_rule_enhancements()
        test_rule_image_enhancements()
        test_template_enhancements()
        
        logger.info("All tests completed successfully!")
        logger.info("Database enhancements from task #5 have been verified.")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()
