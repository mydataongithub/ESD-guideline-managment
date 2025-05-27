# Complete Solution: Fixing Missing Images in ESD Guideline Generator

## Executive Summary

The images associated with rules are not appearing in generated guideline documents because SQLAlchemy's default lazy loading behavior prevents the RuleImage data from being fetched when rules are queried. The solution requires modifying the database queries to use eager loading and updating the templates to properly render the images.

## Root Cause Analysis

### The Core Problem
When `app/core/db_generator.py` fetches rules from the database, it uses standard SQLAlchemy queries that don't explicitly load the related `RuleImage` records. By default, SQLAlchemy uses "lazy loading" for relationships, meaning:
- The `rule.images` relationship is not populated when rules are initially fetched
- Attempting to access `rule.images` after the database session closes results in empty data
- The template receives rules without their associated images

### Database Structure
Your application likely has this relationship structure:
```python
class Rule(Base):
    images = relationship("RuleImage", back_populates="rule")  # Lazy-loaded by default

class RuleImage(Base):
    rule_id = Column(Integer, ForeignKey("rules.id"))
    rule = relationship("Rule", back_populates="images")
```

## Implementation Guide

### Step 1: Update Database Queries in db_generator.py

```python
# app/core/db_generator.py
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
import os

def generate_guideline_from_database(db: Session, guideline_id: int) -> Dict[str, Any]:
    """Generate guideline document data with all associated rules and images"""
    
    # Fetch guideline with eager loading of rules and images
    guideline = db.query(Guideline).options(
        selectinload(Guideline.rules).selectinload(Rule.images)
    ).filter(Guideline.id == guideline_id).first()
    
    if not guideline:
        raise ValueError(f"Guideline with ID {guideline_id} not found")
    
    # Prepare document data structure
    document_data = {
        "title": guideline.title,
        "description": guideline.description,
        "version": guideline.version,
        "rules": []
    }
    
    # Process each rule with its images
    for rule in guideline.rules:
        rule_data = {
            "id": rule.id,
            "title": rule.title,
            "content": rule.content,
            "order": rule.order,
            "images": []
        }
        
        # Process associated images
        for image in rule.images:
            image_data = {
                "filename": image.filename,
                "url": f"/static/images/{image.file_path}",
                "description": image.description or f"Image for {rule.title}",
                "alt_text": f"{rule.title} - {image.description or 'Illustration'}"
            }
            rule_data["images"].append(image_data)
        
        document_data["rules"].append(rule_data)
    
    return document_data

def render_guideline_document(db: Session, guideline_id: int, template_path: str = "guideline.html"):
    """Render guideline document using Jinja2 template"""
    from jinja2 import Environment, FileSystemLoader
    
    # Get document data with images
    doc_data = generate_guideline_from_database(db, guideline_id)
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_path)
    
    # Render template with data
    rendered_html = template.render(**doc_data)
    
    return rendered_html
```

### Step 2: Update CRUD Operations in rule.py

```python
# app/crud/rule.py
from sqlalchemy.orm import selectinload
from typing import List, Optional

def get_rule_with_images(db: Session, rule_id: int) -> Optional[Rule]:
    """Fetch a single rule with all associated images"""
    return db.query(Rule).options(
        selectinload(Rule.images)
    ).filter(Rule.id == rule_id).first()

def get_all_rules_for_guideline(db: Session, guideline_id: int) -> List[Rule]:
    """Fetch all rules for a guideline with their images"""
    return db.query(Rule).options(
        selectinload(Rule.images)
    ).filter(
        Rule.guideline_id == guideline_id
    ).order_by(Rule.order).all()

def create_rule_with_image(db: Session, rule_data: dict, image_data: dict) -> Rule:
    """Create a rule with an associated image"""
    # Create rule
    rule = Rule(**rule_data)
    db.add(rule)
    db.flush()  # Get rule.id
    
    # Create associated image
    if image_data:
        image = RuleImage(
            rule_id=rule.id,
            filename=image_data['filename'],
            file_path=image_data['file_path'],
            description=image_data.get('description')
        )
        db.add(image)
    
    db.commit()
    
    # Return with images loaded
    return get_rule_with_images(db, rule.id)
```

### Step 3: Update or Create Jinja2 Template

```html
<!-- templates/guideline.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - ESD Guidelines</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .rule-section {
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        
        .rule-title {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .rule-content {
            margin-bottom: 20px;
            white-space: pre-wrap;
        }
        
        .images-container {
            margin-top: 25px;
        }
        
        figure {
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .rule-image {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            cursor: zoom-in;
        }
        
        figcaption {
            margin-top: 12px;
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .image-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>{{ title }}</h1>
        {% if description %}
        <p class="description">{{ description }}</p>
        {% endif %}
        <p class="metadata">Version: {{ version }} | Generated: {{ current_date }}</p>
    </header>

    <main>
        {% for rule in rules %}
        <section class="rule-section" id="rule-{{ rule.id }}">
            <h2 class="rule-title">{{ loop.index }}. {{ rule.title }}</h2>
            <div class="rule-content">{{ rule.content }}</div>
            
            {% if rule.images %}
            <div class="images-container">
                <h3>Visual References</h3>
                {% if rule.images|length == 1 %}
                    <!-- Single image -->
                    <figure>
                        <img src="{{ rule.images[0].url }}" 
                             alt="{{ rule.images[0].alt_text }}" 
                             class="rule-image"
                             onclick="window.open(this.src, '_blank')">
                        <figcaption>{{ rule.images[0].description }}</figcaption>
                    </figure>
                {% else %}
                    <!-- Multiple images in grid -->
                    <div class="image-grid">
                        {% for image in rule.images %}
                        <figure>
                            <img src="{{ image.url }}" 
                                 alt="{{ image.alt_text }}" 
                                 class="rule-image"
                                 onclick="window.open(this.src, '_blank')">
                            <figcaption>{{ image.description }}</figcaption>
                        </figure>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            {% endif %}
        </section>
        {% endfor %}
    </main>
</body>
</html>
```

### Step 4: Ensure Static Files Are Properly Configured

```python
# app/main.py (or wherever your FastAPI app is initialized)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="ESD Guideline Generator")

# Create static directory if it doesn't exist
os.makedirs("static/images", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Step 5: Update Models if Needed

```python
# app/database/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    guideline_id = Column(Integer, ForeignKey("guidelines.id"))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    # Explicitly set loading strategy if needed
    images = relationship("RuleImage", back_populates="rule", cascade="all, delete-orphan")
    guideline = relationship("Guideline", back_populates="rules")

class RuleImage(Base):
    __tablename__ = "rule_images"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id", ondelete="CASCADE"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    rule = relationship("Rule", back_populates="images")
```

### Step 6: Create a Test Endpoint

```python
# app/api/endpoints/guidelines.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.db_generator import render_guideline_document

router = APIRouter()

@router.get("/guidelines/{guideline_id}/preview")
def preview_guideline(guideline_id: int, db: Session = Depends(get_db)):
    """Preview generated guideline with images"""
    try:
        html_content = render_guideline_document(db, guideline_id)
        return HTMLResponse(content=html_content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Alternative: PDF Generation with Images

If you need to generate PDFs with embedded images:

```python
# app/core/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

def generate_pdf_with_images(document_data: dict, output_path: str):
    """Generate PDF document with embedded images"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    story.append(Paragraph(document_data['title'], styles['Title']))
    story.append(Spacer(1, 12))
    
    # Add rules with images
    for rule in document_data['rules']:
        story.append(Paragraph(rule['title'], styles['Heading2']))
        story.append(Paragraph(rule['content'], styles['BodyText']))
        
        # Add images
        for image in rule['images']:
            img_path = f"static/images/{image['file_path']}"
            if os.path.exists(img_path):
                img = Image(img_path, width=400, height=300)
                story.append(img)
                story.append(Paragraph(image['description'], styles['Caption']))
        
        story.append(Spacer(1, 12))
    
    doc.build(story)
```

## Verification Steps

1. **Check Database Queries**: Add logging to verify images are being loaded
```python
import logging
logger = logging.getLogger(__name__)

def generate_guideline_from_database(db: Session, guideline_id: int):
    # ... existing code ...
    for rule in guideline.rules:
        logger.info(f"Rule '{rule.title}' has {len(rule.images)} images")
```

2. **Test Image Loading**: Create a simple test script
```python
from app.database.session import SessionLocal
from app.core.db_generator import generate_guideline_from_database

db = SessionLocal()
try:
    data = generate_guideline_from_database(db, 1)
    for rule in data['rules']:
        print(f"Rule: {rule['title']}")
        print(f"Images: {len(rule['images'])}")
        for img in rule['images']:
            print(f"  - {img['filename']}: {img['url']}")
finally:
    db.close()
```

## Summary

The key fix is adding `.options(selectinload(Rule.images))` to your database queries in `db_generator.py`. This ensures images are fetched along with rules, making them available for template rendering. The provided code modifications will:

1. Fetch images with rules using eager loading
2. Structure the data properly for template consumption
3. Render images with proper HTML markup and styling
4. Handle both single and multiple images per rule
5. Provide fallbacks for missing images

Implement these changes in order, starting with the database query modifications, and your generated guideline documents will properly display all associated images.