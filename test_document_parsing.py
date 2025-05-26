# test_document_parsing.py
"""
Test script for document parsing functionality.
This script demonstrates how to use the document parsers to extract rules from files.
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.parsers import ExcelParser, PDFParser, WordParser

def test_parser(file_path, parser_class):
    """Test a parser on a specific file."""
    print(f"\nTesting {parser_class.__name__} on {os.path.basename(file_path)}")
    print("-" * 50)
    
    try:
        parser = parser_class(file_path=file_path)
        
        # Process and extract data
        result = parser.process()
        
        # Print metadata
        print("\nDocument Metadata:")
        print(json.dumps(result['metadata'], indent=2))
        
        # Print rules
        print(f"\nExtracted Rules ({len(result['rules'])}):")
        for i, rule in enumerate(result['rules'], 1):
            print(f"\n[Rule {i}]")
            print(f"Title: {rule.get('title', 'No title')}")
            print(f"Type: {rule.get('rule_type', 'general')}")
            content = rule.get('content', 'No content')
            print(f"Content: {content[:100]}..." if len(content) > 100 else f"Content: {content}")
        
        # Print image info
        print(f"\nExtracted Images ({len(result['images'])}):")
        for i, image in enumerate(result['images'], 1):
            print(f"[Image {i}] {image.get('filename', 'Unnamed')} - {image.get('mime_type', 'Unknown type')}")
        
        return True
        
    except Exception as e:
        print(f"Error testing {parser_class.__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to test document parsers."""
    # Check for sample files in a "samples" directory
    samples_dir = Path("samples")
    
    if not samples_dir.exists():
        print(f"Creating samples directory at {samples_dir.absolute()}")
        samples_dir.mkdir(exist_ok=True)
        print("Please place sample documents in this directory and run the script again.")
        print("Required sample files:")
        print("- sample.xlsx (Excel file)")
        print("- sample.pdf (PDF file)")
        print("- sample.docx (Word file)")
        return
    
    # Test Excel parser
    excel_samples = list(samples_dir.glob("*.xlsx")) + list(samples_dir.glob("*.xls"))
    if excel_samples:
        test_parser(str(excel_samples[0]), ExcelParser)
    else:
        print("No Excel samples found in 'samples' directory. Looking for .xlsx or .xls files.")
    
    # Test PDF parser
    pdf_samples = list(samples_dir.glob("*.pdf"))
    if pdf_samples:
        test_parser(str(pdf_samples[0]), PDFParser)
    else:
        print("No PDF samples found in 'samples' directory. Looking for .pdf files.")
    
    # Test Word parser
    word_samples = list(samples_dir.glob("*.docx")) + list(samples_dir.glob("*.doc"))
    if word_samples:
        test_parser(str(word_samples[0]), WordParser)
    else:
        print("No Word samples found in 'samples' directory. Looking for .docx or .doc files.")
    
if __name__ == "__main__":
    main()
