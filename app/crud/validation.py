# app/crud/validation.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.models import ValidationQueue, ValidationStatus, ImportedDocument
from app.models.schemas import ValidationQueueCreate, ValidationQueueUpdate

def create_validation_item(db: Session, validation_item: ValidationQueueCreate) -> ValidationQueue:
    """
    Create a new validation queue item in the database.
    
    Args:
        db: Database session
        validation_item: Validation item data to create
        
    Returns:
        Created ValidationQueue database model
    """
    db_validation_item = ValidationQueue(
        document_id=validation_item.document_id,
        rule_id=validation_item.rule_id,
        extracted_content=validation_item.extracted_content,
        validation_status=validation_item.validation_status,
        validator_notes=validation_item.validator_notes
    )
    db.add(db_validation_item)
    db.commit()
    db.refresh(db_validation_item)
    return db_validation_item


def get_validation_item(db: Session, validation_id: int) -> Optional[ValidationQueue]:
    """
    Get a validation item by ID.
    
    Args:
        db: Database session
        validation_id: Validation queue item ID to retrieve
        
    Returns:
        ValidationQueue model or None if not found
    """
    return db.query(ValidationQueue).filter(ValidationQueue.id == validation_id).first()


def get_validation_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    document_id: Optional[int] = None,
    validation_status: Optional[ValidationStatus] = None
) -> List[ValidationQueue]:
    """
    Get validation queue items with optional filtering.
    
    Args:
        db: Database session
        skip: Number of items to skip
        limit: Maximum number of items to return
        document_id: Filter by document ID
        validation_status: Filter by validation status
        
    Returns:
        List of ValidationQueue models
    """
    query = db.query(ValidationQueue)
    
    if document_id is not None:
        query = query.filter(ValidationQueue.document_id == document_id)
        
    if validation_status is not None:
        query = query.filter(ValidationQueue.validation_status == validation_status)
    
    return query.order_by(ValidationQueue.created_at.desc()).offset(skip).limit(limit).all()


def update_validation_status(
    db: Session, 
    validation_id: int, 
    status_update: ValidationQueueUpdate
) -> Optional[ValidationQueue]:
    """
    Update the status of a validation queue item.
    
    Args:
        db: Database session
        validation_id: ID of the validation item to update
        status_update: Data for the update
        
    Returns:
        Updated ValidationQueue model or None if not found
    """
    db_validation = get_validation_item(db, validation_id)
    if not db_validation:
        return None
        
    # Update fields from status_update if they have values
    for field, value in status_update.dict(exclude_unset=True).items():
        setattr(db_validation, field, value)
        
    db.commit()
    db.refresh(db_validation)
    return db_validation


def get_pending_validation_count(db: Session) -> int:
    """
    Get the number of pending validation items.
    
    Args:
        db: Database session
        
    Returns:
        Count of pending validation items
    """
    return db.query(ValidationQueue).filter(
        ValidationQueue.validation_status == ValidationStatus.PENDING
    ).count()


def delete_validation_items_for_document(db: Session, document_id: int) -> int:
    """
    Delete all validation items for a document.
    
    Args:
        db: Database session
        document_id: Document ID to delete validations for
        
    Returns:
        Number of deleted items
    """
    deleted = db.query(ValidationQueue).filter(
        ValidationQueue.document_id == document_id
    ).delete()
    
    db.commit()
    return deleted
