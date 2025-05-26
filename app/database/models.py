# app/database/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, LargeBinary, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class RuleType(enum.Enum):
    ESD = "esd"
    LATCHUP = "latchup"
    GENERAL = "general"

class ValidationStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

class DocumentType(enum.Enum):
    EXCEL = "EXCEL"
    PDF = "PDF"
    WORD = "WORD"
    MARKDOWN = "MARKDOWN"

class Technology(Base):
    __tablename__ = "technologies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    version = Column(String(50))  # Technology version
    node_size = Column(String(50))  # e.g., "180nm", "65nm", "22nm", etc.
    process_type = Column(String(100))  # e.g., "CMOS", "BiCMOS", "SiGe", etc.
    foundry = Column(String(100))  # Manufacturing foundry
    active = Column(Boolean, default=True)  # Is this technology currently active/supported
    tech_metadata = Column(JSON)  # Additional technology metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Technology-specific configuration
    config_data = Column(JSON)  # Store technology-specific configuration
    esd_strategy = Column(JSON)  # ESD protection strategy details
    latchup_strategy = Column(JSON)  # Latchup prevention strategy
    
    # Relationships
    rules = relationship("Rule", back_populates="technology", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="technology", cascade="all, delete-orphan")

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    technology_id = Column(Integer, ForeignKey("technologies.id"), nullable=False)
    rule_type = Column(Enum(RuleType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    explanation = Column(Text)  # Basic explanation
    detailed_description = Column(Text)  # More detailed technical explanation
    implementation_notes = Column(Text)  # Implementation guidelines
    references = Column(Text)  # References to standards, papers, etc.
    examples = Column(Text)  # Code or circuit examples
    severity = Column(String(50), index=True)  # e.g., "critical", "warning", "info"
    category = Column(String(100), index=True)  # e.g., "IO", "Power", "Clamp", etc.
    subcategory = Column(String(100))  # More specific categorization
    applicable_technologies = Column(JSON)  # Lists other technologies where this rule applies
    order_index = Column(Integer, default=0)  # For ordering rules
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))
    reviewed_at = Column(DateTime)  # When the rule was last reviewed
    reviewed_by = Column(String(100))  # Who performed the review
    
    # Relationships
    technology = relationship("Technology", back_populates="rules")
    images = relationship("RuleImage", back_populates="rule", cascade="all, delete-orphan")
    validation_queue = relationship("ValidationQueue", back_populates="rule")

class RuleImage(Base):
    __tablename__ = "rule_images"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    mime_type = Column(String(50))
    caption = Column(Text)
    description = Column(Text)  # Detailed explanation of the image
    source = Column(String(255))  # Source of the image (document, manual upload, etc.)
    width = Column(Integer)  # Image width in pixels
    height = Column(Integer)  # Image height in pixels
    file_size = Column(Integer)  # Size in bytes
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String(100))  # Who added this image
    
    # Relationships
    rule = relationship("Rule", back_populates="images")

class TemplateType(enum.Enum):
    GUIDELINE = "guideline"
    RULE = "rule"
    EMAIL = "email"
    REPORT = "report"

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    technology_id = Column(Integer, ForeignKey("technologies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    template_type = Column(Enum(TemplateType), default=TemplateType.GUIDELINE, index=True)
    template_content = Column(Text, nullable=False)  # Markdown/HTML template
    template_variables = Column(JSON)  # JSON field for template variables
    css_styles = Column(Text)  # Additional CSS styles for this template
    script_content = Column(Text)  # JavaScript for this template
    version = Column(String(50), default="1.0.0")  # Template version
    is_default = Column(Boolean, default=False)
    author = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_used_at = Column(DateTime)  # Track template usage
    
    # Relationships
    technology = relationship("Technology", back_populates="templates")

class ImportedDocument(Base):
    __tablename__ = "imported_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_data = Column(LargeBinary)  # Store original file
    file_path = Column(String(500))  # Alternative: store path
    processed = Column(Boolean, default=False)
    processing_status = Column(String(50))
    processing_notes = Column(Text)
    uploaded_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime)
    uploaded_by = Column(String(100))
    
    # Relationships
    validation_queue = relationship("ValidationQueue", back_populates="document")

class ValidationQueue(Base):
    __tablename__ = "validation_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("imported_documents.id"))
    rule_id = Column(Integer, ForeignKey("rules.id"))
    extracted_content = Column(JSON)  # JSON with extracted data
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    validator_notes = Column(Text)
    validated_by = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    validated_at = Column(DateTime)
    
    # Relationships
    document = relationship("ImportedDocument", back_populates="validation_queue")
    rule = relationship("Rule", back_populates="validation_queue")