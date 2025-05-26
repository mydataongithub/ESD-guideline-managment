# app/api/validation_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.database.database import get_db
from app.database.models import ValidationQueue, ValidationStatus
from app.models.schemas import ValidationQueue as ValidationQueueSchema
from app.models.schemas import ValidationQueueUpdate, ValidationQueueCreate
from app.crud.validation import (
    get_validation_item, get_validation_items, update_validation_status,
    get_pending_validation_count
)
from app.crud.rule import RuleCRUD
from app.core.notification import notification_manager

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validation", tags=["validation"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_model=List[ValidationQueueSchema])
def get_validation_list(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    document_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of validation queue items with optional filtering."""
    validation_status = None
    if status:
        try:
            validation_status = ValidationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid values: {[s.value for s in ValidationStatus]}"
            )
            
    return get_validation_items(db, skip, limit, document_id, validation_status)


@router.get("/{validation_id}", response_model=ValidationQueueSchema)
def get_validation_by_id(validation_id: int, db: Session = Depends(get_db)):
    """Get a specific validation queue item by ID."""
    validation = get_validation_item(db, validation_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item with ID {validation_id} not found"
        )
    return validation


@router.put("/{validation_id}", response_model=ValidationQueueSchema)
def update_validation_item(
    validation_id: int, 
    update_data: ValidationQueueUpdate,
    db: Session = Depends(get_db)
):
    """Update the status of a validation queue item."""
    # Check if this is an approval that should create a rule
    create_rule = False
    if update_data.validation_status == ValidationStatus.APPROVED:
        create_rule = True
    
    # Get current time for validation timestamp
    if update_data.validation_status in [ValidationStatus.APPROVED, ValidationStatus.REJECTED]:
        update_data.validated_at = datetime.now()
    
    # Update validation status
    updated_validation = update_validation_status(db, validation_id, update_data)
    
    if not updated_validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item with ID {validation_id} not found"
        )
    
    # Create a rule if approved
    if create_rule:
        try:
            rule = RuleCRUD.create_rule_from_validation(db, updated_validation)
            return updated_validation
        except Exception as e:
            logger.error(f"Error creating rule from validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating rule from validation: {str(e)}"
            )
    
    return updated_validation


@router.get("/count/pending")
def get_pending_count(db: Session = Depends(get_db)):
    """Get the number of pending validation items."""
    count = get_pending_validation_count(db)
    return {"count": count}


@router.post("/review/{validation_id}/approve")
def approve_validation_item(
    validation_id: int, 
    validator_notes: Optional[str] = None,
    validator: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Approve a validation item and create a rule from it."""
    update_data = ValidationQueueUpdate(
        validation_status=ValidationStatus.APPROVED,
        validator_notes=validator_notes,
        validated_by=validator,
        validated_at=datetime.now()
    )
    
    updated_validation = update_validation_status(db, validation_id, update_data)
    
    if not updated_validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item with ID {validation_id} not found"
        )
    
    # Create a rule from the validated content
    try:
        rule = RuleCRUD.create_rule_from_validation(db, updated_validation)
        
        # Send notification
        if background_tasks:
            notification_data = {
                "title": updated_validation.extracted_content.get("title", "Untitled Rule"),
                "rule_type": updated_validation.extracted_content.get("rule_type", "general"),
                "validator": validator or "System",
                "notes": validator_notes,
                "url": f"/validation/ui/review/{validation_id}"
            }
            background_tasks.add_task(
                notification_manager.send_validation_approval_notification,
                validation_data=notification_data,
                recipients=["esd-team@example.com"]  # Would be configured in production
            )
        
        # Log the notification
        notification_manager.log_notification(
            notification_type="approval",
            validation_id=validation_id,
            user=validator or "Unknown",
            message=f"Rule '{updated_validation.extracted_content.get('title', 'Untitled')}' approved and created"
        )
            
        return {
            "message": "Validation approved and rule created",
            "validation_id": validation_id,
            "rule_id": rule.id
        }
    except Exception as e:
        logger.error(f"Error creating rule from validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving validation: {str(e)}"
        )


@router.post("/review/{validation_id}/reject")
def reject_validation_item(
    validation_id: int, 
    validator_notes: Optional[str] = None,
    validator: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Reject a validation item."""
    if not validator_notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection requires notes explaining the reason"
        )
        
    update_data = ValidationQueueUpdate(
        validation_status=ValidationStatus.REJECTED,
        validator_notes=validator_notes,
        validated_by=validator,
        validated_at=datetime.now()
    )
    
    updated_validation = update_validation_status(db, validation_id, update_data)
    
    if not updated_validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item with ID {validation_id} not found"
        )
    
    # Send notification
    if background_tasks:
        notification_data = {
            "title": updated_validation.extracted_content.get("title", "Untitled Rule"),
            "rule_type": updated_validation.extracted_content.get("rule_type", "general"),
            "validator": validator or "System",
            "notes": validator_notes,
            "url": f"/validation/ui/review/{validation_id}"
        }
        background_tasks.add_task(
            notification_manager.send_validation_rejection_notification,
            validation_data=notification_data,
            recipients=["esd-team@example.com"]  # Would be configured in production
        )
    
    # Log the notification
    notification_manager.log_notification(
        notification_type="rejection",
        validation_id=validation_id,
        user=validator or "Unknown",
        message=f"Rule '{updated_validation.extracted_content.get('title', 'Untitled')}' rejected"
    )
    
    return {
        "message": "Validation rejected",
        "validation_id": validation_id
    }


@router.post("/review/{validation_id}/needs-review")
def mark_validation_for_review(
    validation_id: int, 
    validator_notes: Optional[str] = None,
    validator: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Mark a validation item as needing further review."""
    update_data = ValidationQueueUpdate(
        validation_status=ValidationStatus.NEEDS_REVIEW,
        validator_notes=validator_notes,
        validated_by=validator
    )
    
    updated_validation = update_validation_status(db, validation_id, update_data)
    
    if not updated_validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item with ID {validation_id} not found"
        )
    
    # Send notification
    if background_tasks:
        notification_data = {
            "title": updated_validation.extracted_content.get("title", "Untitled Rule"),
            "rule_type": updated_validation.extracted_content.get("rule_type", "general"),
            "validator": validator or "System",
            "notes": validator_notes,
            "url": f"/validation/ui/review/{validation_id}"
        }
        background_tasks.add_task(
            notification_manager.send_needs_review_notification,
            validation_data=notification_data,
            recipients=["esd-experts@example.com"]  # Would be configured in production
        )
    
    # Log the notification
    notification_manager.log_notification(
        notification_type="needs_review",
        validation_id=validation_id,
        user=validator or "Unknown",
        message=f"Rule '{updated_validation.extracted_content.get('title', 'Untitled')}' marked for expert review"
    )
    
    return {
        "message": "Validation marked for review",
        "validation_id": validation_id
    }


@router.get("/ui/list", include_in_schema=False)
async def validation_list_page(
    request: Request, 
    status: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """Validation queue UI page."""
    validation_status = None
    if status:
        try:
            validation_status = ValidationStatus(status)
        except ValueError:
            pass

    validation_items = get_validation_items(db, limit=100, validation_status=validation_status)
    
    return templates.TemplateResponse(
        "validation_list.html", 
        {
            "request": request, 
            "title": "Validation Queue", 
            "validation_items": validation_items,
            "current_status": status or "all"
        }
    )


@router.get("/ui/review/{validation_id}", include_in_schema=False)
async def validation_review_page(
    request: Request, 
    validation_id: int,
    db: Session = Depends(get_db)
):
    """Validation review UI page for a specific item."""
    validation = get_validation_item(db, validation_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation item with ID {validation_id} not found"
        )
        
    return templates.TemplateResponse(
        "validation_review.html", 
        {
            "request": request, 
            "title": "Review Rule", 
            "validation": validation
        }
    )


@router.get("/ui/dashboard", include_in_schema=False)
async def validation_dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Validation dashboard UI page."""
    # Get counts per status
    pending_count = db.query(ValidationQueue).filter(
        ValidationQueue.validation_status == ValidationStatus.PENDING
    ).count()
    
    approved_count = db.query(ValidationQueue).filter(
        ValidationQueue.validation_status == ValidationStatus.APPROVED
    ).count()
    
    rejected_count = db.query(ValidationQueue).filter(
        ValidationQueue.validation_status == ValidationStatus.REJECTED
    ).count()
    
    needs_review_count = db.query(ValidationQueue).filter(
        ValidationQueue.validation_status == ValidationStatus.NEEDS_REVIEW
    ).count()
    
    return templates.TemplateResponse(
        "validation_dashboard.html", 
        {
            "request": request, 
            "title": "Validation Dashboard",
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "needs_review_count": needs_review_count,
            "total_count": pending_count + approved_count + rejected_count + needs_review_count
        }
    )
