# app/crud/rule.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func
from app.crud.base import CRUDBase
from app.database.models import Rule, RuleImage, RuleType as DBRuleType
from app.models.schemas import RuleCreate, RuleUpdate, RuleType

class CRUDRule(CRUDBase[Rule, RuleCreate, RuleUpdate]):
    def get_with_images(self, db: Session, rule_id: int) -> Optional[Rule]:
        """Fetch a single rule with all associated images"""
        return db.query(Rule).options(
            selectinload(Rule.images)
        ).filter(Rule.id == rule_id).first()
    
    def get_all_rules_for_technology(self, db: Session, technology_id: int) -> List[Rule]:
        """Fetch all rules for a technology with their images"""
        return db.query(Rule).options(
            selectinload(Rule.images)
        ).filter(
            Rule.technology_id == technology_id,
            Rule.is_active == True
        ).order_by(Rule.order_index).all()
    
    def create_rule_with_image(self, db: Session, rule_data: dict, image_data: dict) -> Rule:
        """Create a rule with an associated image"""
        # Create rule
        rule = Rule(**rule_data)
        db.add(rule)
        db.flush()  # Get rule.id
        
        # Create associated image
        if image_data:
            image = RuleImage(
                rule_id=rule.id,
                filename=image_data['filename'],
                image_data=image_data.get('image_data'),
                mime_type=image_data.get('mime_type', 'image/png'),
                description=image_data.get('description'),
                caption=image_data.get('caption')
            )
            db.add(image)
        
        db.commit()
        
        # Return with images loaded
        return self.get_with_images(db, rule.id)
    
    def get_by_technology(
        self, 
        db: Session, 
        *, 
        technology_id: int,
        rule_type: Optional[RuleType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Rule]:
        query = db.query(Rule).filter(Rule.technology_id == technology_id)
        
        if rule_type:
            query = query.filter(Rule.rule_type == rule_type)
        
        return query.filter(Rule.is_active == True).order_by(Rule.order_index).offset(skip).limit(limit).all()
    
    def search(
        self,
        db: Session,
        *,
        query: str,
        technology_id: Optional[int] = None,
        rule_type: Optional[RuleType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Rule]:
        search_filter = or_(
            Rule.title.ilike(f"%{query}%"),
            Rule.content.ilike(f"%{query}%"),
            Rule.explanation.ilike(f"%{query}%")
        )
        
        db_query = db.query(Rule).filter(search_filter)
        
        if technology_id:
            db_query = db_query.filter(Rule.technology_id == technology_id)
        
        if rule_type:
            db_query = db_query.filter(Rule.rule_type == rule_type)
        
        return db_query.filter(Rule.is_active == True).offset(skip).limit(limit).all()
    
    def get_stats(self, db: Session) -> Dict[str, Any]:
        """Get overall rule statistics."""
        total = db.query(func.count(Rule.id)).filter(Rule.is_active == True).scalar()
        esd = db.query(func.count(Rule.id)).filter(
            and_(Rule.rule_type == DBRuleType.ESD, Rule.is_active == True)
        ).scalar()
        latchup = db.query(func.count(Rule.id)).filter(
            and_(Rule.rule_type == DBRuleType.LATCHUP, Rule.is_active == True)
        ).scalar()
        general = db.query(func.count(Rule.id)).filter(
            and_(Rule.rule_type == DBRuleType.GENERAL, Rule.is_active == True)
        ).scalar()
        
        return {
            "total": total,
            "esd": esd,
            "latchup": latchup,
            "general": general
        }
    
    def add_image(
        self,
        db: Session,
        *,
        rule_id: int,
        filename: str,
        image_data: bytes,
        mime_type: Optional[str] = None,
        caption: Optional[str] = None,
        order_index: int = 0
    ) -> RuleImage:
        db_image = RuleImage(
            rule_id=rule_id,
            filename=filename,
            image_data=image_data,
            mime_type=mime_type,
            caption=caption,
            order_index=order_index
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image
    
    def get_images(self, db: Session, *, rule_id: int) -> List[RuleImage]:
        return db.query(RuleImage).filter(
            RuleImage.rule_id == rule_id
        ).order_by(RuleImage.order_index).all()
    
    def delete_image(self, db: Session, *, image_id: int) -> bool:
        image = db.query(RuleImage).filter(RuleImage.id == image_id).first()
        if image:
            db.delete(image)
            db.commit()
            return True
        return False
    
    def create_rule_from_validation(self, db: Session, validation_item) -> Rule:
        """
        Create a new rule from a validated queue item.
        
        Args:
            db: Database session
            validation_item: Validated queue item from which to create a rule
            
        Returns:
            Created Rule database model
        """
        # Extract content from the validated item
        extracted_content = validation_item.extracted_content
        
        # Determine rule type 
        rule_type_str = extracted_content.get("rule_type", "general").lower()
        if rule_type_str == "esd":
            rule_type = DBRuleType.ESD
        elif rule_type_str == "latchup":
            rule_type = DBRuleType.LATCHUP
        else:
            rule_type = DBRuleType.GENERAL
            
        # Use technology_id if available, or a default
        technology_id = extracted_content.get("technology_id", 1)
        
        # Create the rule
        db_rule = Rule(
            technology_id=technology_id,
            rule_type=rule_type,
            title=extracted_content.get("title", "Untitled Rule"),
            content=extracted_content.get("content", ""),
            explanation=extracted_content.get("explanation", ""),
            severity=extracted_content.get("severity", "medium"),
            is_active=True,
            order_index=0  # Will be updated later if needed
        )
        
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        
        # Link the validation item to the rule
        validation_item.rule_id = db_rule.id
        db.commit()
        
        # If there are images, create them too
        if "images" in extracted_content and isinstance(extracted_content["images"], list):
            for img_data in extracted_content["images"]:
                # Create rule image
                rule_image = RuleImage(
                    rule_id=db_rule.id,
                    image_data=img_data.get("image_data"),
                    mime_type=img_data.get("mime_type", "image/png"),
                    caption=img_data.get("description", "")
                )
                db.add(rule_image)
        
        db.commit()
        return db_rule

RuleCRUD = CRUDRule(Rule)