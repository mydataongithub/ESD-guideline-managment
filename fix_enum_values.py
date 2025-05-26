# Fix database enum values for existing documents
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.database.database import DATABASE_URL

def fix_document_enum_values():
    """Fix enum values in imported_documents table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Begin transaction
        trans = conn.begin()
        try:
            # Update any lowercase enum values to uppercase
            result = conn.execute(text("""
                UPDATE imported_documents 
                SET document_type = UPPER(document_type)
                WHERE document_type IN ('excel', 'pdf', 'word', 'markdown')
            """))
            
            print(f"Updated {result.rowcount} documents with incorrect enum values")
            
            # Commit transaction
            trans.commit()
            print("[OK] Database enum values fixed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"[ERROR] Error fixing enum values: {e}")
            raise

if __name__ == "__main__":
    fix_document_enum_values()
