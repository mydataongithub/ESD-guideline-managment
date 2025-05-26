# app/utils/__init__.py
"""
Utility functions and helpers for the ESD & Latchup Guidelines application.
These utilities support the database enhancements from task #5.
"""

from .image_utils import (
    get_image_dimensions,
    get_image_metadata,
    optimize_image,
    image_to_base64
)

from .template_utils import (
    TemplateRenderer,
    extract_variables_from_template,
    validate_template,
    create_default_template
)

__all__ = [
    'get_image_dimensions',
    'get_image_metadata',
    'optimize_image',
    'image_to_base64',
    'TemplateRenderer',
    'extract_variables_from_template',
    'validate_template',
    'create_default_template'
]
