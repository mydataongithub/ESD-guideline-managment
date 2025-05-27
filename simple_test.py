#!/usr/bin/env python3
"""
Simple test to check if ExcelParser dependencies are working
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required imports work"""
    print("Testing imports...")
    
    try:
        import openpyxl
        print("[OK] openpyxl imported successfully")
    except ImportError as e:
        print(f"[ERROR] openpyxl import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("[OK] pandas imported successfully")
    except ImportError as e:
        print(f"[ERROR] pandas import failed: {e}")
        return False
        
    try:
        from app.parsers.excel_parser import ExcelParser
        print("[OK] ExcelParser imported successfully")
    except ImportError as e:
        print(f"[ERROR] ExcelParser import failed: {e}")
        return False
        
    try:
        from app.database.database import SessionLocal
        print("[OK] Database session imported successfully")
    except ImportError as e:
        print(f"[ERROR] Database session import failed: {e}")
        return False
        
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from app.database.database import SessionLocal
        from app.database.models import ImportedDocument
        
        db = SessionLocal()
        count = db.query(ImportedDocument).count()
        print(f"[OK] Database connection successful. Found {count} documents.")
        db.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Simple Dependency Test")
    print("=" * 30)
    
    imports_ok = test_imports()
    db_ok = test_database_connection()
    
    if imports_ok and db_ok:
        print("\n[OK] All basic tests passed!")
    else:
        print("\n[ERROR] Some tests failed. Check the errors above.")
