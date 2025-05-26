# app/crud/technology.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.database.models import Technology
from app.models.schemas import TechnologyCreate, TechnologyUpdate

class CRUDTechnology(CRUDBase[Technology, TechnologyCreate, TechnologyUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Technology]:
        return db.query(Technology).filter(Technology.name == name).first()
    
    def get_all_with_stats(self, db: Session) -> List[dict]:
        """Get all technologies with rule statistics."""
        technologies = db.query(Technology).all()
        result = []
        
        for tech in technologies:
            rules = tech.rules
            esd_count = sum(1 for r in rules if r.rule_type.value == "esd" and r.is_active)
            latchup_count = sum(1 for r in rules if r.rule_type.value == "latchup" and r.is_active)
            general_count = sum(1 for r in rules if r.rule_type.value == "general" and r.is_active)
            
            result.append({
                "id": tech.id,
                "name": tech.name,
                "description": tech.description,
                "total_rules": esd_count + latchup_count + general_count,
                "esd_rules": esd_count,
                "latchup_rules": latchup_count,
                "general_rules": general_count,
                "created_at": tech.created_at,
                "updated_at": tech.updated_at
            })
        
        return result

TechnologyCRUD = CRUDTechnology(Technology)