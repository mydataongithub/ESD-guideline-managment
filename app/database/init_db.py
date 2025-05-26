# app/database/init_db.py
from sqlalchemy import create_engine
from .database import Base, engine
from .models import Technology, Rule, Template, ImportedDocument, ValidationQueue, RuleImage

def init_database():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()