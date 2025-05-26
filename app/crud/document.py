# app/crud/document.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.models import ImportedDocument, DocumentType
from app.models.schemas import ImportedDocumentCreate, ImportedDocument as ImportedDocumentSchema


def create_document(db: Session, document: ImportedDocumentCreate) -> ImportedDocument:
    """
    Create a new imported document record in the database.
    
    Args:
        db: Database session
        document: Document data to create
        
    Returns:
        Created ImportedDocument database model
    """
    db_document = ImportedDocument(
        filename=document.filename,
        document_type=document.document_type,
        file_data=document.file_data,
        processing_notes=document.processing_notes,
        uploaded_by=document.uploaded_by,
        processed=False,
        processing_status="pending"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> Optional[ImportedDocument]:
    """
    Get a document by ID.
    
    Args:
        db: Database session
        document_id: Document ID to retrieve
        
    Returns:
        ImportedDocument model or None if not found
    """
    return db.query(ImportedDocument).filter(ImportedDocument.id == document_id).first()


def get_documents(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    document_type: Optional[DocumentType] = None,
    processed: Optional[bool] = None
) -> List[ImportedDocument]:
    """
    Get a list of documents with optional filters.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        document_type: Filter by document type
        processed: Filter by processed status
        
    Returns:
        List of ImportedDocument models
    """
    query = db.query(ImportedDocument)
    
    if document_type:
        query = query.filter(ImportedDocument.document_type == document_type)
    
    if processed is not None:
        query = query.filter(ImportedDocument.processed == processed)
    
    return query.order_by(ImportedDocument.uploaded_at.desc()).offset(skip).limit(limit).all()


def update_document_status(
    db: Session, 
    document_id: int, 
    processed: bool,
    processing_status: str,
    processing_notes: Optional[str] = None
) -> Optional[ImportedDocument]:
    """
    Update a document's processing status.
    
    Args:
        db: Database session
        document_id: Document ID to update
        processed: Whether document has been fully processed
        processing_status: Status description (e.g., "success", "failed", "partially_processed")
        processing_notes: Additional notes about processing
        
    Returns:
        Updated ImportedDocument model or None if not found
    """
    db_document = get_document(db, document_id)
    if not db_document:
        return None
    
    db_document.processed = processed
    db_document.processing_status = processing_status
    if processing_notes:
        db_document.processing_notes = processing_notes
    db_document.processed_at = datetime.now()
    
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    """
    Delete a document by ID.
    
    Args:
        db: Database session
        document_id: Document ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_document = get_document(db, document_id)
    if not db_document:
        return False
    
    db.delete(db_document)
    db.commit()
    return True
