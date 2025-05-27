# app/api/document_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import tempfile
import asyncio
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from app.database.database import get_db
from app.database.models import DocumentType, ValidationStatus
from app.models.schemas import ImportedDocumentCreate, ImportedDocument as ImportedDocumentSchema
from app.models.schemas import ValidationQueueCreate
from app.parsers import ExcelParser, PDFParser, WordParser
from app.crud.document import create_document, get_document, get_documents, update_document_status, delete_document
from app.crud.validation import create_validation_item
from app.core.mcp_client import MCPClient
from app.core.mcp_config import load_mcp_config

router = APIRouter(prefix="/documents", tags=["documents"])
templates = Jinja2Templates(directory="app/templates")

# Define supported file types
SUPPORTED_EXTENSIONS = {
    ".xlsx": DocumentType.EXCEL,
    ".xls": DocumentType.EXCEL,
    ".pdf": DocumentType.PDF,
    ".doc": DocumentType.WORD,
    ".docx": DocumentType.WORD
}


@router.post("/upload", response_model=ImportedDocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a document and store it in the database."""
    # Check file extension
    filename = file.filename
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_EXTENSIONS.keys())}"
        )
    
    # Read file content
    file_content = await file.read()
      # Create document record
    document = ImportedDocumentCreate(
        filename=filename,
        document_type=SUPPORTED_EXTENSIONS[file_extension].value.upper(),  # Convert to upper case to match enum
        file_data=file_content,
        processing_notes=description
    )
    
    # Store in database
    try:
        db_document = create_document(db, document)
        return db_document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document: {str(e)}"
        )


@router.get("/", response_model=List[ImportedDocumentSchema])
def get_document_list(
    skip: int = 0, 
    limit: int = 100,
    document_type: Optional[str] = None,
    processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get a list of uploaded documents."""
    # Convert string document_type to enum if provided
    doc_type_enum = None
    if document_type:
        try:
            doc_type_enum = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Valid types: {[t.value for t in DocumentType]}"
            )
    
    return get_documents(db, skip, limit, doc_type_enum, processed)


@router.get("/{document_id}", response_model=ImportedDocumentSchema)
def get_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """Get a document by ID."""
    db_document = get_document(db, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return db_document


@router.post("/{document_id}/process")
def process_document(document_id: int, db: Session = Depends(get_db)):
    """Process a document to extract rules, metadata, and images."""
    # Get document from database
    db_document = get_document(db, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Check if already processed
    if db_document.processed:
        return {"message": "Document already processed", "status": db_document.processing_status}
    
    # Process based on document type
    try:
        # Save file to temporary location for processing
        # Get proper file extension for the temporary file
        file_extension = os.path.splitext(db_document.filename)[1].lower()
        if not file_extension:
            # Default to .xlsx for Excel files
            if db_document.document_type == DocumentType.EXCEL:
                file_extension = '.xlsx'
            elif db_document.document_type == DocumentType.PDF:
                file_extension = '.pdf'
            elif db_document.document_type == DocumentType.WORD:
                file_extension = '.docx'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(db_document.file_data)
            temp_path = temp_file.name
        
        processing_result = {"rules": [], "metadata": {}, "images": []}
        
        # Process with appropriate parser
        if db_document.document_type == DocumentType.EXCEL:
            parser = ExcelParser(file_path=temp_path)
            processing_result = parser.process()
        elif db_document.document_type == DocumentType.PDF:
            parser = PDFParser(file_path=temp_path)
            processing_result = parser.process()
        elif db_document.document_type == DocumentType.WORD:
            parser = WordParser(file_path=temp_path)
            processing_result = parser.process()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Update document status in database
        update_document_status(
            db, 
            document_id, 
            processed=True,
            processing_status="success",
            processing_notes=f"Extracted {len(processing_result['rules'])} rules, {len(processing_result['images'])} images"
        )
        
        return {
            "message": "Document processed successfully",
            "status": "success",
            "rules_extracted": len(processing_result['rules']),
            "images_extracted": len(processing_result['images']),
            "metadata": processing_result['metadata']
        }
        
    except Exception as e:
        # Update document with error status
        update_document_status(
            db, 
            document_id, 
            processed=False,
            processing_status="failed",
            processing_notes=f"Processing error: {str(e)}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.delete("/{document_id}")
def delete_document_by_id(document_id: int, db: Session = Depends(get_db)):
    """Delete a document by ID."""
    success = delete_document(db, document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return {"message": f"Document {document_id} deleted successfully"}


@router.get("/ui/upload", include_in_schema=False)
async def document_upload_page(request: Request):
    """Document upload UI page."""
    return templates.TemplateResponse(
        "document_upload.html", 
        {"request": request, "title": "Upload Documents"}
    )


@router.get("/ui/list", include_in_schema=False)
async def document_list_page(request: Request, db: Session = Depends(get_db)):
    """Document list UI page."""
    documents = get_documents(db)
    return templates.TemplateResponse(
        "document_list.html", 
        {"request": request, "title": "Document Management", "documents": documents}
    )


@router.post("/{document_id}/process-with-mcp")
async def process_document_with_mcp(
    document_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process a document using the MCP server for AI-assisted analysis."""
    # Get document from database
    db_document = get_document(db, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Check if already processed
    if db_document.processed:
        return {"message": "Document already processed", "status": db_document.processing_status}
    
    # Update document status to processing
    update_document_status(
        db, 
        document_id, 
        processed=False,
        processing_status="processing",
        processing_notes="Sending document to MCP server for analysis..."
    )
    
    # Process in background to avoid blocking the API
    background_tasks.add_task(
        process_document_with_mcp_background,
        document_id=document_id
    )
    
    return {
        "message": "Document sent for processing with MCP server",
        "status": "processing",
        "document_id": document_id
    }


async def process_document_with_mcp_background(document_id: int):
    """Background task for processing a document with MCP server."""
    # Get a new db session for this background task
    from app.database.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Get document from database
        db_document = get_document(db, document_id)
        if not db_document:
            logger.error(f"Document with ID {document_id} not found in background task")
            return
            
        # Load MCP configuration
        mcp_config = load_mcp_config()
        
        # Initialize MCP client
        mcp_client = MCPClient(
            server_url=mcp_config["server_url"],
            api_key=mcp_config["api_key"]
        )
        
        try:
            # Send document to MCP for analysis
            result = await mcp_client.extract_rules_with_ai(
                file_content=db_document.file_data,
                file_name=db_document.filename,
                document_type=db_document.document_type.value
            )
            
            # Close the client
            await mcp_client.close()
            
            # Check for errors
            if "error" in result:
                update_document_status(
                    db, 
                    document_id, 
                    processed=False,
                    processing_status="failed",
                    processing_notes=f"MCP processing error: {result['error']}"
                )
                return
                
            # Add extracted rules to validation queue
            rules_added = 0
            for rule in result["rules"]:
                # Only add rules with confidence above threshold
                if rule.get("confidence", 0) >= mcp_config.get("confidence_threshold", 0.7):
                    validation_item = ValidationQueueCreate(
                        document_id=document_id,
                        extracted_content=rule,
                        validation_status=ValidationStatus.PENDING
                    )
                    create_validation_item(db, validation_item)
                    rules_added += 1
            
            # Update document status
            update_document_status(
                db, 
                document_id, 
                processed=True,
                processing_status="success",
                processing_notes=(
                    f"MCP processing completed. "
                    f"Added {rules_added} rules to validation queue. "
                    f"Extracted {len(result['images'])} images."
                )
            )
            
        except Exception as e:
            # Handle any exceptions during MCP processing
            update_document_status(
                db, 
                document_id, 
                processed=False,
                processing_status="failed",
                processing_notes=f"MCP processing error: {str(e)}"
            )
            
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error in MCP background processing: {str(e)}")
        
    finally:
        # Close the database session
        db.close()


@router.get("/mcp-status")
async def check_mcp_status():
    """Check the connection status with the MCP server."""
    try:
        # Load MCP configuration
        mcp_config = load_mcp_config()
        
        # Initialize MCP client
        mcp_client = MCPClient(
            server_url=mcp_config["server_url"],
            api_key=mcp_config["api_key"]
        )
        
        # Check server availability
        server_available = await mcp_client.ping()
        
        # Close the client
        await mcp_client.close()
        
        if server_available:
            return {
                "status": "connected",
                "server_url": mcp_config["server_url"],
                "message": "Successfully connected to MCP server"
            }
        else:
            return {
                "status": "disconnected",
                "server_url": mcp_config["server_url"],
                "message": "Failed to connect to MCP server"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error connecting to MCP server: {str(e)}",
            "error": str(e)
        }


@router.get("/ui/mcp", include_in_schema=False)
async def mcp_document_page(request: Request, db: Session = Depends(get_db)):
    """MCP document processing UI page."""
    documents = get_documents(db)
    return templates.TemplateResponse(
        "mcp_document_processing.html", 
        {"request": request, "title": "AI Document Processing", "documents": documents}
    )