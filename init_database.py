#!/usr/bin/env python3
"""
Initialize or reset the ESD Guidelines database
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from app.database.database import Base, engine, SessionLocal
from app.database.models import Technology, Rule, RuleImage, Template, ImportedDocument, ValidationQueue, RuleType, TemplateType

def init_database():
    """Initialize the database with all tables"""
    print("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[OK] All tables created successfully")
    
    # Create default data
    db = SessionLocal()
    try:
        # Check if we already have data
        tech_count = db.query(Technology).count()
        if tech_count == 0:
            print("\nAdding default technologies...")
            
            # Add some default technologies
            default_techs = [
                {"name": "180nm CMOS", "description": "180nm CMOS Process", "node_size": "180nm", "process_type": "CMOS"},
                {"name": "65nm CMOS", "description": "65nm CMOS Process", "node_size": "65nm", "process_type": "CMOS"},
                {"name": "28nm CMOS", "description": "28nm CMOS Process", "node_size": "28nm", "process_type": "CMOS"},
            ]
            
            for tech_data in default_techs:
                tech = Technology(**tech_data)
                db.add(tech)
            
            db.commit()
            print(f"[OK] Added {len(default_techs)} default technologies")
            
            # Add a sample rule
            sample_rule = Rule(
                technology_id=1,
                rule_type=RuleType.ESD,
                title="Input Protection Required",
                content="All input pins must have ESD protection diodes connected to VDD and VSS rails.",
                explanation="ESD events can damage input transistors. Protection diodes provide a discharge path.",
                severity="high",
                category="IO",
                is_active=True
            )
            db.add(sample_rule)
            
            # Add a sample template
            sample_template = Template(
                technology_id=1,
                name="Default ESD Guidelines Template",
                description="Default template for ESD guidelines",
                template_type=TemplateType.GUIDELINE,
                template_content="# {{ technology_name }} ESD Guidelines\n\nGenerated on: {{ date }}\n\n## Rules\n\n{{ rules_content }}",
                template_variables={"technology_name": "Technology", "date": "2025-05-26", "rules_content": "Rules go here"},
                is_default=True
            )
            db.add(sample_template)
            
            db.commit()
            print("[OK] Added sample data")
        else:
            print(f"[OK] Database already contains {tech_count} technologies")
        
        # Show table statistics
        print("\nDatabase Statistics:")
        print(f"  Technologies: {db.query(Technology).count()}")
        print(f"  Rules: {db.query(Rule).count()}")
        print(f"  Templates: {db.query(Template).count()}")
        print(f"  Imported Documents: {db.query(ImportedDocument).count()}")
        print(f"  Validation Queue: {db.query(ValidationQueue).count()}")
        
    finally:
        db.close()
    
    print("\n[DONE] Database initialization complete!")

if __name__ == "__main__":
    init_database()
