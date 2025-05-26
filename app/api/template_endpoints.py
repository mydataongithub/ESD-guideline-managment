# app/api/template_endpoints.py
from fastapi import APIRouter, HTTPException, Depends, Request, Path as FastAPIPath
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from app.database.database import get_db
from app.database.models import Template, Technology, TemplateType
from app.models import schemas
from app.crud.template import TemplateCRUD
from app.crud.technology import TechnologyCRUD
from app.utils.template_utils import (
    TemplateRenderer,
    extract_variables_from_template,
    validate_template,
    create_default_template
)

router = APIRouter(prefix="/templates", tags=["templates"])
templates = Jinja2Templates(directory="app/templates")

# Also create a separate router for API endpoints
api_router = APIRouter(prefix="/api/templates", tags=["templates-api"])

@router.get("/", response_class=HTMLResponse)
async def template_management_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Template management dashboard."""
    # Get all technologies
    technologies = TechnologyCRUD.get_multi(db)
    
    # Get template statistics
    total_templates = db.query(Template).count()
    templates_by_type = db.query(
        Template.template_type,
        func.count(Template.id)
    ).group_by(Template.template_type).all()
    
    stats = {
        "total_templates": total_templates,
        "templates_by_type": {t[0]: t[1] for t in templates_by_type}
    }
    
    return templates.TemplateResponse("template_management.html", {
        "request": request,
        "technologies": technologies,
        "stats": stats
    })

@router.get("/technology/{technology_id}", response_model=List[schemas.Template])
async def get_templates_by_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    """Get all templates for a specific technology."""
    return TemplateCRUD.get_by_technology(db, technology_id=technology_id)

@router.get("/{template_id}", response_model=schemas.Template)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific template by ID."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/", response_model=schemas.Template)
async def create_template(
    template: schemas.TemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new template."""
    # Validate the template
    validation_result = validate_template(template.template_content, template.template_variables)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Template validation failed: Missing variables {validation_result['missing_variables']}"
        )
    
    # Extract variables if not provided
    if not template.template_variables:
        variables = extract_variables_from_template(template.template_content)
        template.template_variables = {var: f"Default value for {var}" for var in variables}
    
    return TemplateCRUD.create(db, obj_in=template)

@router.put("/{template_id}", response_model=schemas.Template)
async def update_template(
    template_id: int,
    template_update: schemas.TemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing template."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # If template content is being updated, validate it
    if template_update.template_content:
        variables = template_update.template_variables or template.template_variables
        validation_result = validate_template(template_update.template_content, variables)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Template validation failed: {validation_result}"
            )
    
    # Update last_used_at if we're using the template
    if hasattr(template, 'last_used_at'):
        template.last_used_at = datetime.utcnow()
    
    return TemplateCRUD.update(db, db_obj=template, obj_in=template_update)

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete a template."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Don't delete default templates
    if template.is_default:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete default template. Set another template as default first."
        )
    
    TemplateCRUD.remove(db, id=template_id)
    return {"status": "success", "message": "Template deleted successfully"}

@router.post("/{template_id}/set-default")
async def set_default_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Set a template as the default for its technology."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    TemplateCRUD.set_default(
        db,
        template_id=template_id,
        technology_id=template.technology_id
    )
    
    return {"status": "success", "message": "Template set as default"}

@router.get("/{template_id}/preview", response_class=HTMLResponse)
async def preview_template(
    template_id: int,
    request: Request,
    db: Session = Depends(get_db),
    test_data: Optional[Dict[str, Any]] = None
):
    """Preview a template with test data."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Use provided test data or template's default variables
    variables = test_data or template.template_variables or {}
    
    # Add some default values if empty
    if not variables:
        variables = {
            "technology_name": "Test Technology",
            "generated_date": datetime.utcnow().strftime("%Y-%m-%d"),
        }
    
    # Render the template
    renderer = TemplateRenderer(template.template_content, variables)
    rendered_html = renderer.render_with_css(template.css_styles)
    
    return rendered_html

@router.post("/{template_id}/preview-data")
async def preview_template_with_data(
    template_id: int,
    preview_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Preview a template with specific data (JSON response)."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Render the template
    renderer = TemplateRenderer(template.template_content, preview_data)
    rendered_content = renderer.render()
    rendered_html = renderer.render_to_html()
    
    return {
        "rendered_content": rendered_content,
        "rendered_html": rendered_html,
        "variables_used": list(preview_data.keys())
    }

@router.get("/{template_id}/editor", response_class=HTMLResponse)
async def template_editor(
    template_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Template editor interface."""
    template = TemplateCRUD.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    technology = TechnologyCRUD.get(db, id=template.technology_id)
    
    return templates.TemplateResponse("template_editor.html", {
        "request": request,
        "template": template,
        "technology": technology,
        "template_types": [t.value for t in TemplateType]
    })

@router.get("/create/new", response_class=HTMLResponse)
async def new_template_editor(
    request: Request,
    technology_id: Optional[int] = None,
    template_type: Optional[str] = "guideline",
    db: Session = Depends(get_db)
):
    """New template creation interface."""
    technologies = TechnologyCRUD.get_multi(db)
    
    # Get default template content
    default_content = create_default_template(
        template_type,
        "Technology Name"
    )
    
    return templates.TemplateResponse("template_editor_new.html", {
        "request": request,
        "technologies": technologies,
        "selected_technology_id": technology_id,
        "template_types": [t.value for t in TemplateType],
        "default_content": default_content,
        "selected_type": template_type
    })

@router.post("/validate")
async def validate_template_content(
    validation_request: Dict[str, Any]
):
    """Validate template content and variables."""
    template_content = validation_request.get("template_content", "")
    variables = validation_request.get("variables", {})
    
    validation_result = validate_template(template_content, variables)
    
    return validation_result

@router.get("/types/defaults")
async def get_default_templates():
    """Get default template content for each template type."""
    defaults = {}
    for template_type in TemplateType:
        defaults[template_type.value] = create_default_template(
            template_type.value,
            "Technology Name"
        )
    return defaults

# API endpoints for JSON responses
@api_router.get("/", response_model=List[schemas.Template])
async def get_all_templates(
    db: Session = Depends(get_db),
    technology_id: Optional[int] = None,
    template_type: Optional[str] = None
):
    """Get all templates with optional filtering."""
    query = db.query(Template)
    
    if technology_id:
        query = query.filter(Template.technology_id == technology_id)
    
    if template_type:
        query = query.filter(Template.template_type == template_type)
    
    return query.all()
