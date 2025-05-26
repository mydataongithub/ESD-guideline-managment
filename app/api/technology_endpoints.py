# app/api/technology_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.crud import TechnologyCRUD
from app.models.schemas import Technology, TechnologyCreate, TechnologyUpdate
from app.api.rule_endpoints import get_db

router = APIRouter(prefix="/technologies", tags=["technologies"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_model=List[Technology])
async def list_technologies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all technologies."""
    return TechnologyCRUD.get_multi(db, skip=skip, limit=limit)

# UI Routes - Define these BEFORE dynamic routes to avoid conflicts
@router.get("/manage", response_class=HTMLResponse, include_in_schema=False)
async def technology_management_page(request: Request):
    """Render the technology management page."""
    return templates.TemplateResponse("technology_management.html", {
        "request": request
    })

@router.get("/stats")
async def get_technologies_with_stats(db: Session = Depends(get_db)):
    """Get all technologies with rule statistics."""
    return TechnologyCRUD.get_all_with_stats(db)

@router.post("", response_model=Technology)
async def create_technology(
    technology: TechnologyCreate,
    db: Session = Depends(get_db)
):
    """Create a new technology."""
    # Check if technology with same name exists
    existing = TechnologyCRUD.get_by_name(db, name=technology.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Technology '{technology.name}' already exists"
        )
    
    return TechnologyCRUD.create(db, obj_in=technology)

@router.get("/{technology_id}", response_model=Technology)
async def get_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific technology by ID."""
    technology = TechnologyCRUD.get(db, id=technology_id)
    if not technology:
        raise HTTPException(status_code=404, detail="Technology not found")
    return technology

@router.put("/{technology_id}", response_model=Technology)
async def update_technology(
    technology_id: int,
    technology_update: TechnologyUpdate,
    db: Session = Depends(get_db)
):
    """Update a technology."""
    technology = TechnologyCRUD.get(db, id=technology_id)
    if not technology:
        raise HTTPException(status_code=404, detail="Technology not found")
    
    # Check if new name conflicts with existing technology
    if technology_update.name and technology_update.name != technology.name:
        existing = TechnologyCRUD.get_by_name(db, name=technology_update.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Technology '{technology_update.name}' already exists"
            )
    
    return TechnologyCRUD.update(db, db_obj=technology, obj_in=technology_update)

@router.delete("/{technology_id}")
async def delete_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    """Delete a technology."""
    technology = TechnologyCRUD.get(db, id=technology_id)
    if not technology:
        raise HTTPException(status_code=404, detail="Technology not found")
    
    # Check if technology has associated rules
    if technology.rules:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete technology with {len(technology.rules)} associated rules"
        )
    
    TechnologyCRUD.remove(db, id=technology_id)
    return {"message": "Technology deleted successfully"}

@router.get("/edit/{technology_id}", response_class=HTMLResponse)
async def technology_editor_page(
    request: Request,
    technology_id: int,
    db: Session = Depends(get_db)
):
    """Render the technology editor page."""
    technology = TechnologyCRUD.get(db, id=technology_id)
    if not technology:
        raise HTTPException(status_code=404, detail="Technology not found")
    
    return templates.TemplateResponse("technology_editor.html", {
        "request": request,
        "technology": technology
    })
