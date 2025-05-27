# add_test_images.py
"""Script to add test images to rules in the database"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import Rule, RuleImage, Technology
from app.crud.rule import RuleCRUD
import base64

def create_sample_svg_image(title: str) -> bytes:
    """Create a simple SVG image as test data"""
    svg_content = f"""<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
        <text x="200" y="150" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">
            {title}
        </text>
        <circle cx="100" cy="100" r="40" fill="#007bff" opacity="0.7"/>
        <rect x="250" y="80" width="80" height="80" fill="#28a745" opacity="0.7"/>
        <text x="200" y="250" font-family="Arial" font-size="14" text-anchor="middle" fill="#666">
            Sample ESD Protection Circuit
        </text>
    </svg>"""
    return svg_content.encode('utf-8')

def add_test_images():
    """Add test images to existing rules"""
    db = SessionLocal()
    try:
        # Get all rules without images
        rules = db.query(Rule).filter(Rule.is_active == True).all()
        print(f"Found {len(rules)} active rules")
        
        rules_updated = 0
        
        for rule in rules:
            # Check if rule already has images
            existing_images = db.query(RuleImage).filter(RuleImage.rule_id == rule.id).count()
            
            if existing_images == 0:
                # Create a test image for this rule
                image_data = create_sample_svg_image(f"Diagram for {rule.title[:30]}...")
                
                # Add image to database
                rule_image = RuleImage(
                    rule_id=rule.id,
                    filename=f"test_image_rule_{rule.id}.svg",
                    image_data=image_data,
                    mime_type="image/svg+xml",
                    caption=f"Test diagram for {rule.title}",
                    description=f"This is a sample diagram illustrating the concept of {rule.title}. "
                               f"In a real implementation, this would show the actual circuit or layout design.",
                    width=400,
                    height=300,
                    file_size=len(image_data),
                    created_by="test_script"
                )
                
                db.add(rule_image)
                rules_updated += 1
                print(f"Added image to rule: {rule.title[:50]}...")
                
                # Add a second image for some rules (every 3rd rule)
                if rule.id % 3 == 0:
                    image_data2 = create_sample_svg_image(f"Layout for {rule.title[:30]}...")
                    rule_image2 = RuleImage(
                        rule_id=rule.id,
                        filename=f"test_layout_rule_{rule.id}.svg",
                        image_data=image_data2,
                        mime_type="image/svg+xml",
                        caption=f"Layout example for {rule.title}",
                        description=f"Sample layout showing the physical implementation of {rule.title}.",
                        width=400,
                        height=300,
                        file_size=len(image_data2),
                        order_index=1,
                        created_by="test_script"
                    )
                    db.add(rule_image2)
                    print(f"  Added second image to rule: {rule.title[:50]}...")
        
        db.commit()
        print(f"\nSuccessfully added images to {rules_updated} rules")
        
        # Verify the images were added
        total_images = db.query(RuleImage).count()
        print(f"Total images in database: {total_images}")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding images: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clear_all_images():
    """Clear all images from the database (use with caution!)"""
    db = SessionLocal()
    try:
        count = db.query(RuleImage).count()
        if count > 0:
            response = input(f"This will delete {count} images. Are you sure? (yes/no): ")
            if response.lower() == 'yes':
                db.query(RuleImage).delete()
                db.commit()
                print(f"Deleted {count} images")
            else:
                print("Cancelled")
        else:
            print("No images to delete")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_all_images()
    else:
        print("Adding test images to rules...")
        add_test_images()
        print("\nTo clear all images, run: python add_test_images.py --clear")