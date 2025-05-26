# app/database/migrations.py
"""
Database migration script for implementing the database enhancements
defined in task #5 of TASK.md.

This script will:
1. Add new columns to existing tables
2. Convert existing data if needed
3. Update indexes

Run this script after updating the models.py file with the new schema changes.
"""

from sqlalchemy import create_engine, text, MetaData, Table, Column, inspect
from sqlalchemy.types import Integer, String, Text, Boolean, JSON, DateTime
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get database URL from environment or use default
db_url = os.getenv("DATABASE_URL", "sqlite:///./esd_guidelines.db")

def run_migration():
    """
    Execute the database migration to implement the schema enhancements
    """
    logger.info(f"Starting database migration using {db_url}")

    # Create SQLAlchemy engine with echo mode for logging SQL
    engine = create_engine(db_url, echo=True)
    metadata = MetaData()
    inspector = inspect(engine)
    
    try:
        conn = engine.connect()
        
        # Start transaction
        trans = conn.begin()
        
        # 1. Migrate the Rule table
        logger.info("Migrating Rule table...")
        add_columns_if_not_exist(conn, 'rules', [
            {'name': 'detailed_description', 'type': 'TEXT'},
            {'name': 'implementation_notes', 'type': 'TEXT'},
            {'name': 'references', 'type': 'TEXT'},
            {'name': 'examples', 'type': 'TEXT'},
            {'name': 'subcategory', 'type': 'VARCHAR(100)'},
            {'name': 'applicable_technologies', 'type': 'JSON'},
            {'name': 'reviewed_at', 'type': 'TIMESTAMP'},
            {'name': 'reviewed_by', 'type': 'VARCHAR(100)'}
        ])
        
        # Add indexes to rule table
        add_index_if_not_exists(conn, 'rules', 'idx_rules_category', 'category')
        add_index_if_not_exists(conn, 'rules', 'idx_rules_severity', 'severity')
        
        # 2. Migrate the RuleImage table
        logger.info("Migrating RuleImage table...")
        add_columns_if_not_exist(conn, 'rule_images', [
            {'name': 'description', 'type': 'TEXT'},
            {'name': 'source', 'type': 'VARCHAR(255)'},
            {'name': 'width', 'type': 'INTEGER'},
            {'name': 'height', 'type': 'INTEGER'},
            {'name': 'file_size', 'type': 'INTEGER'},
            {'name': 'created_by', 'type': 'VARCHAR(100)'}
        ])
        
        # 3. Migrate the Template table
        logger.info("Migrating Template table...")
        # First, create the template_type enum if it doesn't exist
        create_enum_type_if_not_exists(conn, 'template_type', 
                                     ["guideline", "rule", "email", "report"])
        
        # Now add the columns
        add_columns_if_not_exist(conn, 'templates', [
            {'name': 'template_type', 'type': 'template_type', 'default': "'guideline'::template_type"},
            {'name': 'css_styles', 'type': 'TEXT'},
            {'name': 'script_content', 'type': 'TEXT'},
            {'name': 'version', 'type': 'VARCHAR(50)', 'default': "'1.0.0'"},
            {'name': 'author', 'type': 'VARCHAR(100)'},
            {'name': 'last_used_at', 'type': 'TIMESTAMP'}
        ])
        
        # Add index to template table
        add_index_if_not_exists(conn, 'templates', 'idx_templates_type', 'template_type')
        
        # 4. Migrate the Technology table
        logger.info("Migrating Technology table...")
        add_columns_if_not_exist(conn, 'technologies', [
            {'name': 'version', 'type': 'VARCHAR(50)'},
            {'name': 'node_size', 'type': 'VARCHAR(50)'},            {'name': 'process_type', 'type': 'VARCHAR(100)'},
            {'name': 'foundry', 'type': 'VARCHAR(100)'},
            {'name': 'active', 'type': 'BOOLEAN', 'default': 'TRUE'},
            {'name': 'tech_metadata', 'type': 'JSON'},
            {'name': 'esd_strategy', 'type': 'JSON'},
            {'name': 'latchup_strategy', 'type': 'JSON'}
        ])
        
        # Commit the transaction
        trans.commit()
        logger.info("Migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        trans.rollback()
        raise
    finally:
        conn.close()
        
def add_columns_if_not_exist(conn, table_name, columns):
    """
    Add columns to a table if they don't already exist
    
    Args:
        conn: SQLAlchemy connection
        table_name: Name of the table to modify
        columns: List of column definitions (dict with name, type, and optional default)
    """
    # Get existing columns in the table
    existing_columns = []
    
    if 'sqlite' in conn.engine.url.drivername:
        # For SQLite, use PRAGMA table_info
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        existing_columns = [row[1] for row in result]  # Column name is at index 1
    else:
        # For PostgreSQL and others
        result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"))
        existing_columns = [row[0] for row in result]
    
    for column in columns:
        if column['name'].lower() not in [col.lower() for col in existing_columns]:
            # Map generic types to SQLite types
            col_type = column['type']
            if 'sqlite' in conn.engine.url.drivername:
                type_mapping = {
                    'VARCHAR': 'TEXT',
                    'BOOLEAN': 'INTEGER',
                    'TIMESTAMP': 'TEXT',
                    'JSON': 'TEXT',
                    'template_type': 'TEXT'
                }
                for pattern, replacement in type_mapping.items():
                    if pattern in col_type:
                        col_type = col_type.replace(pattern, replacement)
                
                # SQLite doesn't support adding columns with defaults directly
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN \"{column['name']}\" {col_type}"))
                if 'default' in column:
                    # Clean up the default value for SQLite
                    default_val = column['default']
                    if "::template_type" in default_val:
                        default_val = "'guideline'"
                    conn.execute(text(f"UPDATE {table_name} SET \"{column['name']}\" = {default_val}"))
            else:
                # For PostgreSQL and others
                default_clause = f" DEFAULT {column['default']}" if 'default' in column else ""
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column['name']} {column['type']}{default_clause}"))
                
            logger.info(f"Added column '{column['name']}' to table '{table_name}'")
        else:
            logger.info(f"Column '{column['name']}' already exists in table '{table_name}'")
            
def add_index_if_not_exists(conn, table_name, index_name, column_name):
    """
    Add an index to a table if it doesn't already exist
    
    Args:
        conn: SQLAlchemy connection
        table_name: Name of the table
        index_name: Name of the index to create
        column_name: Column to index
    """
    # For SQLite
    if 'sqlite' in conn.engine.url.drivername:
        # Check if index exists
        result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'"))
        if not result.fetchone():
            conn.execute(text(f"CREATE INDEX {index_name} ON {table_name}({column_name})"))
            logger.info(f"Created index '{index_name}' on table '{table_name}'")
        else:
            logger.info(f"Index '{index_name}' already exists on table '{table_name}'")
    else:
        # For PostgreSQL and others
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"))
        logger.info(f"Ensured index '{index_name}' exists on table '{table_name}'")
        
def create_enum_type_if_not_exists(conn, enum_name, values):
    """
    Create an enum type if it doesn't already exist
    
    Args:
        conn: SQLAlchemy connection
        enum_name: Name of the enum type
        values: List of valid enum values
    """
    # For SQLite, enums are not supported
    if 'sqlite' in conn.engine.url.drivername:
        logger.info(f"SQLite does not support enum types, skipping creation of '{enum_name}'")
        return
    
    # For PostgreSQL
    result = conn.execute(text(f"SELECT 1 FROM pg_type WHERE typname = '{enum_name}'"))
    if not result.fetchone():
        value_list = "'" + "', '".join(values) + "'"
        conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ({value_list})"))
        logger.info(f"Created enum type '{enum_name}'")
    else:
        logger.info(f"Enum type '{enum_name}' already exists")

if __name__ == "__main__":
    run_migration()
