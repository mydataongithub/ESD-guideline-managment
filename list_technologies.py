# List all technologies and templates in the database
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import Technology, Template

def list_all_technologies():
    db = SessionLocal()
    try:
        technologies = db.query(Technology).all()
        
        if technologies:
            print(f"Found {len(technologies)} technologies:")
            for tech in technologies:
                print(f"Technology ID={tech.id}, Name={tech.name}, Active={tech.active}")
                
                # Get templates for this technology
                templates = db.query(Template).filter(
                    Template.technology_id == tech.id
                ).all()
                
                if templates:
                    print(f"  Templates for {tech.name}:")
                    for tpl in templates:
                        default_status = "DEFAULT" if tpl.is_default else ""
                        print(f"  - ID={tpl.id}, Name={tpl.name}, Type={tpl.template_type} {default_status}")
                else:
                    print(f"  No templates found for {tech.name}")
        else:
            print("No technologies found in the database")
    finally:
        db.close()

if __name__ == "__main__":
    list_all_technologies()
