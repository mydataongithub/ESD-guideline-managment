# app/crud/__init__.py
from .technology import TechnologyCRUD
from .rule import RuleCRUD
from .template import TemplateCRUD
# Import document CRUD functions separately
import app.crud.document 

__all__ = [
    "TechnologyCRUD",
    "RuleCRUD",
    "TemplateCRUD"
]