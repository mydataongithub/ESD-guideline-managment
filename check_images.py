#!/usr/bin/env python3
"""
Check which sample documents contain images
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def check_documents_for_images():
    """Check all documents for images"""
    
    from app.database.database import SessionLocal
    from app.database.models import ImportedDocument
    from app.parsers import ExcelParser, PDFParser, WordParser
    import tempfile
    import os
    
    db = SessionLocal()
    
    try:
        # Get all documents from the database
        documents = db.query(ImportedDocument).all()
        
        print(f"Checking {len(documents)} documents for images...")
        print("=" * 50)
        
        for doc in documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"Filename: {doc.filename}")
            print(f"Type: {doc.document_type.value}")
            print(f"File size: {len(doc.file_data) if doc.file_data else 0} bytes")
            
            if not doc.file_data:
                print("  [SKIP] No file data")
                continue
                
            try:
                # Create temporary file with proper extension
                file_extension = os.path.splitext(doc.filename)[1].lower()
                if not file_extension:
                    if doc.document_type.value == "EXCEL":
                        file_extension = '.xlsx'
                    elif doc.document_type.value == "PDF":
                        file_extension = '.pdf'
                    elif doc.document_type.value == "WORD":
                        file_extension = '.docx'
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                    temp_file.write(doc.file_data)
                    temp_path = temp_file.name
                
                # Parse with appropriate parser
                images = []
                if doc.document_type.value == "EXCEL":
                    parser = ExcelParser(file_path=temp_path)
                    result = parser.process()
                    images = result.get('images', [])
                elif doc.document_type.value == "PDF":
                    parser = PDFParser(file_path=temp_path)
                    result = parser.process()
                    images = result.get('images', [])
                elif doc.document_type.value == "WORD":
                    parser = WordParser(file_path=temp_path)
                    result = parser.process()
                    images = result.get('images', [])
                
                # Clean up temp file
                os.unlink(temp_path)
                
                # Report results
                if images:
                    print(f"  [FOUND] {len(images)} images!")
                    for i, img in enumerate(images):
                        print(f"    Image {i+1}: {img.get('filename', 'unnamed')}")
                        if 'sheet' in img:
                            print(f"      Sheet: {img['sheet']}")
                        if 'mime_type' in img:
                            print(f"      Type: {img['mime_type']}")
                        if 'image_data' in img:
                            print(f"      Size: {len(img['image_data'])} bytes")
                else:
                    print("  [NONE] No images found")
                    
            except Exception as e:
                print(f"  [ERROR] Failed to process: {str(e)}")
                # Clean up temp file if it exists
                try:
                    if 'temp_path' in locals():
                        os.unlink(temp_path)
                except:
                    pass
        
        print("\n" + "=" * 50)
        print("Image search complete!")
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Document Image Scanner")
    print("=" * 30)
    check_documents_for_images()
