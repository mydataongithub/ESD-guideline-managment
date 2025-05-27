# Check if a specific technology exists in the database
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, get_db
from app.database.models import Technology

def check_technology_exists(technology_name: str):
    db = SessionLocal()
    try:
        # Try exact match first
        technology = db.query(Technology).filter(Technology.name == technology_name).first()
        
        # If not found, try case-insensitive search
        if not technology:
            technology = db.query(Technology).filter(
                Technology.name.ilike(technology_name)
            ).first()
        
        if technology:
            print(f"Technology found: ID={technology.id}, Name={technology.name}, Active={technology.active}")
            
            # List templates for this technology
            from app.database.models import Template
            templates = db.query(Template).filter(
                Template.technology_id == technology.id
            ).all()
            
            print(f"Templates for {technology.name}:")
            for template in templates:
                default_status = "DEFAULT" if template.is_default else ""
                print(f"  - ID={template.id}, Name={template.name}, Type={template.template_type} {default_status}")
            
            return True
        else:
            print(f"Technology '{technology_name}' not found in database")
            
            # List all technologies
            all_technologies = db.query(Technology).all()
            print("\nAvailable technologies:")
            for tech in all_technologies:
                print(f"  - ID={tech.id}, Name={tech.name}, Active={tech.active}")
            
            return False
    finally:
        db.close()

if __name__ == "__main__":
    technology_name = "tsmc_28nm"
    check_technology_exists(technology_name)
