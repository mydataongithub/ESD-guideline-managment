# check_technologies.py
"""Check what technologies exist in the database"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import Technology, Rule, Template

def check_technologies():
    """List all technologies in the database"""
    db = SessionLocal()
    try:
        # Get all technologies
        technologies = db.query(Technology).all()
        
        print(f"Found {len(technologies)} technologies in database:\n")
        
        for tech in technologies:
            rule_count = db.query(Rule).filter(
                Rule.technology_id == tech.id,
                Rule.is_active == True
            ).count()
            
            template_count = db.query(Template).filter(
                Template.technology_id == tech.id
            ).count()
            
            print(f"ID: {tech.id}")
            print(f"Name: {tech.name}")
            print(f"Active: {tech.active}")
            print(f"Description: {tech.description}")
            print(f"Node Size: {tech.node_size}")
            print(f"Foundry: {tech.foundry}")
            print(f"Active Rules: {rule_count}")
            print(f"Templates: {template_count}")
            print("-" * 50)
            
        # Also check for case-sensitive issues
        print("\nSearching for 'tsmc_28nm' variations:")
        variations = ['tsmc_28nm', 'TSMC_28nm', 'tsmc28nm', 'TSMC28nm', 'tsmc_28']
        
        for var in variations:
            tech = db.query(Technology).filter(
                Technology.name.ilike(f"%{var}%")
            ).first()
            if tech:
                print(f"Found match: {tech.name} (ID: {tech.id})")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_technologies()
