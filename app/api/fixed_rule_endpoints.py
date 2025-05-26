# app/api/fixed_rule_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
import logging

from app.database.database import get_db
from app.database.models import Rule
from app.crud.rule import RuleCRUD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a separate router for the fixed endpoints
fixed_api_router = APIRouter(prefix="/api/rules-fixed", tags=["rules-fixed"])

@fixed_api_router.post("/")
async def create_rule_fixed(
    rule_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new rule using a simplified approach to avoid Pydantic issues."""
    logger.info(f"Received rule data: {rule_data}")
    
    # Validate required fields
    required_fields = ["technology_id", "rule_type", "title", "content"]
    for field in required_fields:
        if field not in rule_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Get the highest order_index for the technology
    max_order = db.query(func.max(Rule.order_index)).filter(
        Rule.technology_id == rule_data["technology_id"]
    ).scalar() or 0
    
    # Add order_index to the data
    rule_data["order_index"] = max_order + 1
    
    # Create the rule directly from dict data
    try:
        db_rule = Rule(**rule_data)
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        
        # Convert db_rule to a dictionary for response
        result = {c.name: getattr(db_rule, c.name) for c in db_rule.__table__.columns}
        return result
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")
