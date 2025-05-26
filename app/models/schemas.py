# app/models/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class RuleType(str, Enum):
    ESD = "esd"
    LATCHUP = "latchup"
    GENERAL = "general"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

class DocumentType(str, Enum):
    EXCEL = "EXCEL"
    PDF = "PDF"
    WORD = "WORD"
    MARKDOWN = "MARKDOWN"

# Base schemas
class TechnologyBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    node_size: Optional[str] = None
    process_type: Optional[str] = None
    foundry: Optional[str] = None
    active: bool = True
    tech_metadata: Optional[Dict[str, Any]] = None
    config_data: Optional[Dict[str, Any]] = None
    esd_strategy: Optional[Dict[str, Any]] = None
    latchup_strategy: Optional[Dict[str, Any]] = None

class TechnologyCreate(TechnologyBase):
    pass

class TechnologyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    node_size: Optional[str] = None
    process_type: Optional[str] = None
    foundry: Optional[str] = None
    active: Optional[bool] = None
    tech_metadata: Optional[Dict[str, Any]] = None
    config_data: Optional[Dict[str, Any]] = None
    esd_strategy: Optional[Dict[str, Any]] = None
    latchup_strategy: Optional[Dict[str, Any]] = None

class Technology(TechnologyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Rule schemas
class RuleBase(BaseModel):
    technology_id: int
    rule_type: RuleType
    title: str
    content: str
    explanation: Optional[str] = None
    detailed_description: Optional[str] = None
    implementation_notes: Optional[str] = None
    references: Optional[str] = None
    examples: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    applicable_technologies: Optional[List[int]] = None
    order_index: int = 0
    is_active: bool = True

class RuleCreate(RuleBase):
    created_by: Optional[str] = None
    reviewed_by: Optional[str] = None

class RuleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    explanation: Optional[str] = None
    detailed_description: Optional[str] = None
    implementation_notes: Optional[str] = None
    references: Optional[str] = None
    examples: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    applicable_technologies: Optional[List[int]] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

class Rule(RuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Rule Image schemas
class RuleImageBase(BaseModel):
    rule_id: int
    filename: str
    mime_type: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    order_index: int = 0

class RuleImageCreate(RuleImageBase):
    image_data: bytes
    created_by: Optional[str] = None

class RuleImage(RuleImageBase):
    id: int
    created_at: datetime
    created_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Template Type enum
class TemplateType(str, Enum):
    GUIDELINE = "guideline"
    RULE = "rule"
    EMAIL = "email"
    REPORT = "report"

# Template schemas
class TemplateBase(BaseModel):
    technology_id: int
    name: str
    description: Optional[str] = None
    template_type: TemplateType = TemplateType.GUIDELINE
    template_content: str
    template_variables: Optional[Dict[str, Any]] = None
    css_styles: Optional[str] = None
    script_content: Optional[str] = None
    version: str = "1.0.0"
    is_default: bool = False
    author: Optional[str] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[TemplateType] = None
    template_content: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    css_styles: Optional[str] = None
    script_content: Optional[str] = None
    version: Optional[str] = None
    is_default: Optional[bool] = None
    author: Optional[str] = None

class Template(TemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Import Document schemas
class ImportedDocumentBase(BaseModel):
    filename: str
    document_type: DocumentType
    processing_notes: Optional[str] = None
    uploaded_by: Optional[str] = None

class ImportedDocumentCreate(ImportedDocumentBase):
    file_data: Optional[bytes] = None

class ImportedDocument(ImportedDocumentBase):
    id: int
    processed: bool
    processing_status: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Validation Queue schemas
class ValidationQueueBase(BaseModel):
    document_id: Optional[int] = None
    rule_id: Optional[int] = None
    extracted_content: Dict[str, Any]
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validator_notes: Optional[str] = None

class ValidationQueueCreate(ValidationQueueBase):
    pass

class ValidationQueueUpdate(BaseModel):
    validation_status: Optional[ValidationStatus] = None
    validator_notes: Optional[str] = None
    validated_by: Optional[str] = None

class ValidationQueue(ValidationQueueBase):
    id: int
    created_at: datetime
    validated_at: Optional[datetime] = None
    validated_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Dashboard schemas
class DashboardStats(BaseModel):
    total_rules: int
    esd_rules: int
    latchup_rules: int
    general_rules: int
    total_technologies: int
    pending_validations: int
    total_documents: int
    processed_documents: int

class RuleStats(BaseModel):
    technology: str
    total: int
    esd: int
    latchup: int
    general: int

# Legacy schemas (keeping for backward compatibility)
class GuidelineResponse(BaseModel):
    technology: str
    message: str
    file_path: str
    content: Optional[str] = None

class GitCommitInfo(BaseModel):
    sha: str
    message: str
    date: datetime

class TechnologyConfig(BaseModel):
    esd_levels: dict
    latch_up_rules: dict
    approved_clamps: List[dict]
    advanced_protection_scheme: Optional[bool] = False
    advanced_protection_scheme_details: Optional[str] = None