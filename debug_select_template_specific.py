# Debug the select-template endpoint error
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import Technology, Template

def debug_select_template_route(technology_name):
    print(f"Debugging select-template route for technology: {technology_name}")
    
    # Connect to database
    db = SessionLocal()
    try:
        # Get technology (case-insensitive)
        print("Looking for technology in database...")
        technology = db.query(Technology).filter(
            Technology.name.ilike(technology_name)
        ).first()
        
        if not technology:
            print(f"ERROR: Technology '{technology_name}' not found")
            print("This would cause a 404 error in the endpoint")
            
            # List all technologies to help diagnose
            techs = db.query(Technology).all()
            print("\nAvailable technologies:")
            for tech in techs:
                print(f"- {tech.name} (ID: {tech.id}, Active: {tech.active})")
            return False
        
        print(f"Technology found: ID={technology.id}, Name={technology.name}, Active={technology.active}")
        
        # Get templates for this technology
        print("\nLooking for templates for this technology...")
        templates_list = db.query(Template).filter(
            Template.technology_id == technology.id
        ).order_by(Template.is_default.desc(), Template.name).all()
        
        if not templates_list:
            print("WARNING: No templates found for this technology")
            print("The endpoint would continue, but might not display any templates")
        else:
            print(f"Found {len(templates_list)} templates:")
            for tpl in templates_list:
                default_mark = "(DEFAULT)" if tpl.is_default else ""
                print(f"- ID={tpl.id}, Name={tpl.name}, Type={tpl.template_type} {default_mark}")
        
        # Check if template file exists
        print("\nChecking if template HTML file exists...")
        template_path = os.path.join("app", "templates", "select_template.html")
        if not os.path.exists(template_path):
            print(f"ERROR: Template file '{template_path}' not found!")
            print("This would cause a 500 error in the endpoint")
            return False
        
        print(f"Template file found: {template_path}")
        
        # At this point, the endpoint should be working
        print("\nConclusion: All required components exist. The endpoint should work!")
        print("Recommendation: Check for runtime errors in the server logs or try restarting the server.")
        
        return True
    finally:
        db.close()

if __name__ == "__main__":
    technology_name = "tsmc_28nm"
    debug_select_template_route(technology_name)
