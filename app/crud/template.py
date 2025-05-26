# app/crud/template.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.database.models import Template
from app.models.schemas import TemplateCreate, TemplateUpdate

class CRUDTemplate(CRUDBase[Template, TemplateCreate, TemplateUpdate]):
    def get_by_technology(
        self, 
        db: Session, 
        *, 
        technology_id: int
    ) -> List[Template]:
        return db.query(Template).filter(
            Template.technology_id == technology_id
        ).all()
    
    def get_default(
        self,
        db: Session,
        *,
        technology_id: int
    ) -> Optional[Template]:
        return db.query(Template).filter(
            Template.technology_id == technology_id,
            Template.is_default == True
        ).first()
    
    def set_default(
        self,
        db: Session,
        *,
        template_id: int,
        technology_id: int
    ) -> Template:
        # First, unset all defaults for this technology
        db.query(Template).filter(
            Template.technology_id == technology_id
        ).update({"is_default": False})
        
        # Then set the new default
        template = db.query(Template).filter(
            Template.id == template_id,
            Template.technology_id == technology_id
        ).first()
        
        if template:
            template.is_default = True
            db.commit()
            db.refresh(template)
        
        return template

TemplateCRUD = CRUDTemplate(Template)