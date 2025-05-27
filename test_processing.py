#!/usr/bin/env python3
"""
Test the document processing endpoint directly
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_document_processing():
    """Test document processing with a specific document"""
    
    from app.database.database import SessionLocal
    from app.database.models import ImportedDocument, DocumentType
    from app.crud.document import get_document
    from app.parsers import ExcelParser
    import tempfile
    import os
    
    db = SessionLocal()
    
    try:
        # Get the first unprocessed document
        doc = db.query(ImportedDocument).filter(ImportedDocument.processed == False).first()
        
        if not doc:
            print("No unprocessed documents found")
            return
            
        print(f"Testing with document ID: {doc.id}")
        print(f"Filename: {doc.filename}")
        print(f"Type: {doc.document_type}")
        print(f"File data size: {len(doc.file_data) if doc.file_data else 0} bytes")
        
        # Check document type enum
        print(f"Document type value: {doc.document_type.value}")
        print(f"Document type comparison: {doc.document_type == DocumentType.EXCEL}")
        
        # Try the processing logic step by step
        print("\nStep 1: Creating temporary file...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(doc.file_data)
            temp_path = temp_file.name
        
        print(f"Temp file created: {temp_path}")
        print(f"Temp file exists: {os.path.exists(temp_path)}")
        print(f"Temp file size: {os.path.getsize(temp_path)}")
        
        print("\nStep 2: Creating parser...")
        if doc.document_type == DocumentType.EXCEL:
            print("Using ExcelParser...")
            parser = ExcelParser(file_path=temp_path)
            
            print("\nStep 3: Running parser.process()...")
            processing_result = parser.process()
            
            print(f"Processing completed successfully!")
            print(f"Rules: {len(processing_result['rules'])}")
            print(f"Images: {len(processing_result['images'])}")
            print(f"Metadata: {processing_result['metadata']}")
            
            # Show some details
            if processing_result['rules']:
                print(f"\nFirst rule: {processing_result['rules'][0]}")
        else:
            print(f"Document type {doc.document_type} not supported in this test")
        
        # Clean up
        os.unlink(temp_path)
        print("\nTemp file cleaned up")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Document Processing Test")
    print("=" * 30)
    test_document_processing()
