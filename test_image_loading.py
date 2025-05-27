# test_image_loading.py
"""Test script to verify images are being loaded with rules"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.core.db_generator import generate_guideline_from_database
from app.database.models import Technology, Rule, RuleImage
from sqlalchemy.orm import selectinload

def test_image_loading():
    """Test that images are properly loaded with rules"""
    db = SessionLocal()
    try:
        # First, let's check if we have any technologies
        technologies = db.query(Technology).all()
        print(f"Found {len(technologies)} technologies in database")
        
        if not technologies:
            print("No technologies found. Please add some test data first.")
            return
        
        # Get the first technology
        tech = technologies[0]
        print(f"\nTesting with technology: {tech.name} (ID: {tech.id})")
        
        # Get rules with eager loading of images
        rules_with_images = db.query(Rule).options(
            selectinload(Rule.images)
        ).filter(
            Rule.technology_id == tech.id,
            Rule.is_active == True
        ).all()
        
        print(f"Found {len(rules_with_images)} active rules for {tech.name}")
        
        # Check each rule for images
        rules_with_actual_images = 0
        total_images = 0
        
        for rule in rules_with_images:
            if rule.images:
                rules_with_actual_images += 1
                total_images += len(rule.images)
                print(f"\nRule '{rule.title}' has {len(rule.images)} images:")
                for img in rule.images:
                    print(f"  - {img.filename} (ID: {img.id}, Size: {len(img.image_data) if img.image_data else 0} bytes)")
        
        print(f"\nSummary:")
        print(f"- Total rules: {len(rules_with_images)}")
        print(f"- Rules with images: {rules_with_actual_images}")
        print(f"- Total images: {total_images}")
        
        # Test the generate_guideline_from_database function
        print(f"\nTesting generate_guideline_from_database for technology ID {tech.id}...")
        try:
            doc_data = generate_guideline_from_database(db, tech.id)
            print(f"Successfully generated document data:")
            print(f"- Title: {doc_data['title']}")
            print(f"- Number of rules: {len(doc_data['rules'])}")
            
            # Count images in generated data
            total_doc_images = sum(len(rule['images']) for rule in doc_data['rules'])
            print(f"- Total images in document: {total_doc_images}")
            
            # Show sample of rules with images
            for rule in doc_data['rules'][:3]:  # Show first 3 rules
                if rule['images']:
                    print(f"\n  Rule '{rule['title']}' has {len(rule['images'])} images")
                    for img in rule['images']:
                        print(f"    - {img['filename']} (Data URL length: {len(img['url'])} chars)")
            
        except Exception as e:
            print(f"Error generating document: {str(e)}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

def check_rule_images_table():
    """Check if RuleImage table has any data"""
    db = SessionLocal()
    try:
        image_count = db.query(RuleImage).count()
        print(f"\nTotal images in rule_images table: {image_count}")
        
        if image_count > 0:
            # Show first few images
            images = db.query(RuleImage).limit(5).all()
            print("\nSample images:")
            for img in images:
                print(f"- ID: {img.id}, Rule ID: {img.rule_id}, Filename: {img.filename}, "
                      f"Size: {len(img.image_data) if img.image_data else 0} bytes")
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing image loading functionality...")
    print("=" * 50)
    check_rule_images_table()
    print("\n" + "=" * 50)
    test_image_loading()