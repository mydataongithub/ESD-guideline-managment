# app/api/rule_endpoints.py
from fastapi import APIRouter, HTTPException, Depends, Request, Query, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import io
import base64
from datetime import datetime

from app.database.database import get_db
from app.database.models import Rule, RuleImage, Technology, RuleType as DBRuleType
from app.models import schemas
from app.crud.rule import RuleCRUD
from app.crud.technology import TechnologyCRUD

router = APIRouter(prefix="/rules", tags=["rules"])
api_router = APIRouter(prefix="/api/rules", tags=["rules-api"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def rule_management_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    technology_id: Optional[int] = Query(None),
    rule_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1)
):
    """Rule management dashboard."""
    # Pagination settings
    page_size = 20
    skip = (page - 1) * page_size
    
    # Get all technologies for filter dropdown
    technologies = TechnologyCRUD.get_multi(db)
    
    # Get rule statistics
    stats = RuleCRUD.get_stats(db)
    
    # Query rules based on filters
    if search:
        rules = RuleCRUD.search(
            db, 
            query=search,
            technology_id=technology_id,
            rule_type=rule_type,
            skip=skip,
            limit=page_size
        )
        total_count = len(RuleCRUD.search(
            db, 
            query=search,
            technology_id=technology_id,
            rule_type=rule_type
        ))
    else:
        query = db.query(Rule).filter(Rule.is_active == True)
        
        if technology_id:
            query = query.filter(Rule.technology_id == technology_id)
        
        if rule_type:
            query = query.filter(Rule.rule_type == rule_type)
        
        total_count = query.count()
        rules = query.order_by(Rule.order_index).offset(skip).limit(page_size).all()
    
    # Calculate pagination info
    total_pages = (total_count + page_size - 1) // page_size
    
    return templates.TemplateResponse("rule_management.html", {
        "request": request,
        "rules": rules,
        "technologies": technologies,
        "stats": stats,
        "filters": {
            "technology_id": technology_id,
            "rule_type": rule_type,
            "search": search
        },
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    })

@router.get("/create", response_class=HTMLResponse)
async def create_rule_form(
    request: Request,
    db: Session = Depends(get_db),
    technology_id: Optional[int] = Query(None)
):
    """Display rule creation form."""
    technologies = TechnologyCRUD.get_multi(db)
    
    return templates.TemplateResponse("rule_editor.html", {
        "request": request,
        "rule": None,  # New rule
        "technologies": technologies,
        "selected_technology_id": technology_id,
        "mode": "create"
    })

@router.get("/{rule_id}", response_class=HTMLResponse)
async def view_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """View a specific rule."""
    rule = RuleCRUD.get(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get associated images
    images = RuleCRUD.get_images(db, rule_id=rule_id)
    
    # Get technology info
    technology = TechnologyCRUD.get(db, id=rule.technology_id)
    
    return templates.TemplateResponse("rule_view.html", {
        "request": request,
        "rule": rule,
        "technology": technology,
        "images": images
    })

@router.get("/{rule_id}/edit", response_class=HTMLResponse)
async def edit_rule_form(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Display rule edit form."""
    rule = RuleCRUD.get(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    technologies = TechnologyCRUD.get_multi(db)
    images = RuleCRUD.get_images(db, rule_id=rule_id)
    
    return templates.TemplateResponse("rule_editor.html", {
        "request": request,
        "rule": rule,
        "technologies": technologies,
        "images": images,
        "mode": "edit"
    })

# API endpoints for JSON responses
@api_router.get("/", response_model=List[schemas.Rule])
async def get_rules(
    db: Session = Depends(get_db),
    technology_id: Optional[int] = Query(None),
    rule_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """Get rules with optional filtering."""
    if search:
        return RuleCRUD.search(
            db,
            query=search,
            technology_id=technology_id,
            rule_type=rule_type,
            skip=skip,
            limit=limit
        )
    else:
        query = db.query(Rule).filter(Rule.is_active == True)
        
        if technology_id:
            query = query.filter(Rule.technology_id == technology_id)
        
        if rule_type:
            query = query.filter(Rule.rule_type == rule_type)
        
        return query.order_by(Rule.order_index).offset(skip).limit(limit).all()

@api_router.post("/", response_model=schemas.Rule)
async def create_rule(
    rule_create: schemas.RuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new rule."""
    # Get the highest order_index for the technology
    max_order = db.query(func.max(Rule.order_index)).filter(
        Rule.technology_id == rule_create.technology_id
    ).scalar() or 0
    
    # Convert from raw rule_create object to a Pydantic model instance
    from app.models.schemas import RuleCreate as RuleCreateModel
    
    # Extract the data and ensure it has all required fields
    data_dict = rule_create.dict() if hasattr(rule_create, 'dict') else rule_create.__dict__
    rule_model = RuleCreateModel(**data_dict)
    rule_model.order_index = max_order + 1
    
    return RuleCRUD.create(db, obj_in=rule_model)

@api_router.put("/{rule_id}", response_model=schemas.Rule)
async def update_rule(
    rule_id: int,
    rule_update: schemas.RuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing rule."""
    rule = RuleCRUD.get(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return RuleCRUD.update(db, db_obj=rule, obj_in=rule_update)

@api_router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a rule (soft delete by setting is_active=False)."""
    rule = RuleCRUD.get(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Soft delete
    rule.is_active = False
    db.commit()
    
    return {"status": "success", "message": "Rule deleted successfully"}

@api_router.post("/{rule_id}/reorder")
async def reorder_rule(
    rule_id: int,
    new_order: int = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    """Change the order index of a rule."""
    rule = RuleCRUD.get(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get all rules for the same technology
    rules = db.query(Rule).filter(
        Rule.technology_id == rule.technology_id,
        Rule.is_active == True
    ).order_by(Rule.order_index).all()
    
    # Remove the rule from its current position
    rules.remove(rule)
    
    # Insert at new position
    rules.insert(new_order, rule)
    
    # Update order indices
    for idx, r in enumerate(rules):
        r.order_index = idx
    
    db.commit()
    
    return {"status": "success", "message": "Rule order updated"}

# Image management endpoints
@api_router.post("/{rule_id}/images")
async def upload_rule_image(
    rule_id: int,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload an image for a rule."""
    rule = RuleCRUD.get(db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image data
    image_data = await file.read()
    
    # Get the highest order_index for this rule's images
    max_order = db.query(func.max(RuleImage.order_index)).filter(
        RuleImage.rule_id == rule_id
    ).scalar() or 0
    
    # Save image
    image = RuleCRUD.add_image(
        db,
        rule_id=rule_id,
        filename=file.filename,
        image_data=image_data,
        mime_type=file.content_type,
        caption=caption,
        order_index=max_order + 1
    )
    
    return {
        "id": image.id,
        "filename": image.filename,
        "caption": image.caption,
        "order_index": image.order_index
    }

@api_router.get("/{rule_id}/images/{image_id}")
async def get_rule_image(
    rule_id: int,
    image_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific rule image."""
    image = db.query(RuleImage).filter(
        RuleImage.id == image_id,
        RuleImage.rule_id == rule_id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return StreamingResponse(
        io.BytesIO(image.image_data),
        media_type=image.mime_type or "image/png",
        headers={"Content-Disposition": f"inline; filename={image.filename}"}
    )

@api_router.delete("/{rule_id}/images/{image_id}")
async def delete_rule_image(
    rule_id: int,
    image_id: int,
    db: Session = Depends(get_db)
):
    """Delete a rule image."""
    success = RuleCRUD.delete_image(db, image_id=image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"status": "success", "message": "Image deleted successfully"}

@api_router.get("/stats/summary")
async def get_rule_statistics(db: Session = Depends(get_db)):
    """Get summary statistics for rules."""
    return RuleCRUD.get_stats(db)

@api_router.post("/bulk-import")
async def bulk_import_rules(
    rules: List[schemas.RuleCreate],
    db: Session = Depends(get_db)
):
    """Import multiple rules at once."""
    created_rules = []
    for rule_data in rules:
        rule = RuleCRUD.create(db, obj_in=rule_data)
        created_rules.append(rule)
    
    return {
        "status": "success",
        "count": len(created_rules),
        "rules": created_rules
    }

@api_router.get("/export")
async def export_rules(
    db: Session = Depends(get_db),
    format: str = Query("json", enum=["json", "excel", "csv"]),
    technology_id: Optional[int] = Query(None)
):
    """Export rules in various formats."""
    # Get rules based on filters
    query = db.query(Rule).filter(Rule.is_active == True)
    if technology_id:
        query = query.filter(Rule.technology_id == technology_id)
    
    rules = query.all()
    
    if format == "json":
        # Return JSON response
        rules_data = [
            {
                "id": rule.id,
                "title": rule.title,
                "rule_type": rule.rule_type.value,
                "content": rule.content,
                "explanation": rule.explanation,
                "severity": rule.severity,
                "technology_id": rule.technology_id,
                "category": rule.category
            }
            for rule in rules
        ]
        return JSONResponse(content={"rules": rules_data, "count": len(rules_data)})
    
    elif format == "excel":
        # Create Excel file
        import pandas as pd
        from io import BytesIO
        
        rules_data = [
            {
                "Rule ID": f"{rule.rule_type.value.upper()}-{rule.id:03d}",
                "Type": rule.rule_type.value.upper(),
                "Title": rule.title,
                "Content": rule.content,
                "Explanation": rule.explanation or "",
                "Severity": rule.severity,
                "Category": rule.category or "",
                "Technology": rule.technology.name if rule.technology else ""
            }
            for rule in rules
        ]
        
        df = pd.DataFrame(rules_data)
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name="ESD_Latchup_Rules")
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=esd_latchup_rules.xlsx"}
        )
    
    elif format == "csv":
        # Create CSV file
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Rule ID", "Type", "Title", "Content", "Explanation", "Severity", "Category", "Technology"])
        
        # Write data
        for rule in rules:
            writer.writerow([
                f"{rule.rule_type.value.upper()}-{rule.id:03d}",
                rule.rule_type.value.upper(),
                rule.title,
                rule.content,
                rule.explanation or "",
                rule.severity,
                rule.category or "",
                rule.technology.name if rule.technology else ""
            ])
        
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=esd_latchup_rules.csv"}
        )
