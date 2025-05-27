#!/usr/bin/env python3
"""
Debug script to test document processing functionality
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import SessionLocal
from app.crud.document import get_document
from app.parsers import ExcelParser
import tempfile
import traceback

def debug_document_processing():
    """Debug document processing with actual database documents"""
    db = SessionLocal()
    
    try:
        # Get all documents from the database
        from app.database.models import ImportedDocument
        documents = db.query(ImportedDocument).all()
        
        if not documents:
            print("No documents found in database")
            return
            
        print(f"Found {len(documents)} documents in database:")
        
        for doc in documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"Filename: {doc.filename}")
            print(f"Type: {doc.document_type}")
            print(f"Processed: {doc.processed}")
            print(f"Status: {doc.processing_status}")
            
            if not doc.processed and doc.file_data:
                print(f"Attempting to process document {doc.id}...")
                
                try:
                    # Save file to temporary location for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                        temp_file.write(doc.file_data)
                        temp_path = temp_file.name
                    
                    print(f"Saved to temp file: {temp_path}")
                    print(f"File size: {len(doc.file_data)} bytes")
                    
                    # Try to process with appropriate parser
                    if doc.document_type.value == "EXCEL":
                        print("Using ExcelParser...")
                        parser = ExcelParser(file_path=temp_path)
                        processing_result = parser.process()
                        
                        print(f"Processing successful!")
                        print(f"Rules extracted: {len(processing_result['rules'])}")
                        print(f"Images extracted: {len(processing_result['images'])}")
                        print(f"Metadata: {processing_result['metadata']}")
                        
                        # Show first few rules if any
                        if processing_result['rules']:
                            print("\nFirst few rules:")
                            for i, rule in enumerate(processing_result['rules'][:3]):
                                print(f"  Rule {i+1}: {rule}")
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                    
                except Exception as e:
                    print(f"ERROR processing document {doc.id}: {str(e)}")
                    print("Full traceback:")
                    traceback.print_exc()
                    
                    # Clean up temp file if it exists
                    try:
                        if 'temp_path' in locals():
                            os.unlink(temp_path)
                    except:
                        pass
                
                # Only test first unprocessed document for now
                break
                
    except Exception as e:
        print(f"Database error: {str(e)}")
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Debug Document Processing")
    print("=" * 40)
    debug_document_processing()
