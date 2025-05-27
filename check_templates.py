# Check templates for tsmc_28nm technology
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.database import SessionLocal
from app.database.models import Technology, Template
from app.crud.template import TemplateCRUD
from app.crud.technology import TechnologyCRUD

def check_templates_for_technology(tech_name: str):
    db = SessionLocal()
    try:
        print(f"Looking for technology: {tech_name}")
        
        # Try to get technology using the CRUD function
        technology = TechnologyCRUD.get_by_name(db, name=tech_name)
        
        # If not found with exact match, try case-insensitive
        if not technology:
            technology = db.query(Technology).filter(
                Technology.name.ilike(tech_name)
            ).first()
        
        if not technology:
            print(f"Technology '{tech_name}' not found!")
            return
            
        print(f"Found technology: ID={technology.id}, Name={technology.name}")
        
        # Get templates using CRUD function
        templates = TemplateCRUD.get_by_technology(db, technology_id=technology.id)
        
        if templates:
            print(f"Found {len(templates)} templates:")
            for template in templates:
                default_status = "DEFAULT" if template.is_default else ""
                print(f"- ID={template.id}, Name={template.name}, Type={template.template_type} {default_status}")
        else:
            print(f"No templates found for {tech_name}")
            
        # Try direct database query as well
        db_templates = db.query(Template).filter(
            Template.technology_id == technology.id
        ).all()
        
        if db_templates:
            print(f"\nFound {len(db_templates)} templates via direct query:")
            for template in db_templates:
                default_status = "DEFAULT" if template.is_default else ""
                print(f"- ID={template.id}, Name={template.name}, Type={template.template_type} {default_status}")
        else:
            print(f"\nNo templates found for {tech_name} via direct query")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_templates_for_technology("tsmc_28nm")
