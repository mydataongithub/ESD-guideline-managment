# app/utils/template_utils.py
"""
Utility functions for handling technology-specific templates.
This supports the enhanced template capabilities added in task #5.
"""

import os
import re
import logging
import json
from typing import Dict, Any, List, Optional, Union
from jinja2 import Environment, BaseLoader, Template
from markdown import markdown

# Configure logging
logger = logging.getLogger(__name__)

class TemplateRenderer:
    """Helper class for rendering templates with various formats and options"""
    
    def __init__(self, template_content: str, variables: Optional[Dict[str, Any]] = None):
        """
        Initialize the template renderer
        
        Args:
            template_content: Raw template content
            variables: Dictionary of variables to use in rendering
        """
        self.template_content = template_content
        self.variables = variables or {}
        self.jinja_env = Environment(loader=BaseLoader())
        
    def render(self) -> str:
        """
        Render the template with the provided variables
        
        Returns:
            Rendered template content
        """
        try:
            template = self.jinja_env.from_string(self.template_content)
            rendered = template.render(**self.variables)
            return rendered
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            return f"Error rendering template: {str(e)}"
    
    def render_to_html(self) -> str:
        """
        Render the template and convert markdown to HTML
        
        Returns:
            HTML content
        """
        rendered = self.render()
        try:
            html = markdown(rendered, extensions=['extra', 'codehilite', 'tables'])
            return html
        except Exception as e:
            logger.error(f"Markdown conversion error: {str(e)}")
            return f"<p>Error converting to HTML: {str(e)}</p>"

    def render_with_css(self, css_content: Optional[str] = None) -> str:
        """
        Render the template to HTML and include CSS
        
        Args:
            css_content: Optional CSS content to include
            
        Returns:
            HTML content with embedded CSS
        """
        html = self.render_to_html()
        
        if css_content:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                {css_content}
                </style>
            </head>
            <body>
            {html}
            </body>
            </html>
            """
        else:
            return html

def extract_variables_from_template(template_content: str) -> List[str]:
    """
    Extract variable names from a Jinja2 template
    
    Args:
        template_content: Template content to parse
        
    Returns:
        List of variable names found in the template
    """
    # This is a simple regex-based approach - not 100% accurate but works for basic templates
    variable_pattern = r'{{\s*(\w+)\s*}}'
    matches = re.findall(variable_pattern, template_content)
    return list(set(matches))  # Remove duplicates

def validate_template(
    template_content: str, 
    test_variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate a template by trying to render it with test variables
    
    Args:
        template_content: Template content to validate
        test_variables: Test variables to use (defaults to dummy data)
        
    Returns:
        Dict with validation results
    """
    required_vars = extract_variables_from_template(template_content)
    
    # Create dummy variables if not provided
    if not test_variables:
        test_variables = {var: f"TEST_{var.upper()}" for var in required_vars}
    
    # Check for missing variables
    missing_vars = [var for var in required_vars if var not in test_variables]
    
    result = {
        "valid": len(missing_vars) == 0,
        "required_variables": required_vars,
        "missing_variables": missing_vars,
    }
    
    # Try rendering
    try:
        renderer = TemplateRenderer(template_content, test_variables)
        renderer.render()
        result["renders_correctly"] = True
    except Exception as e:
        result["renders_correctly"] = False
        result["render_error"] = str(e)
        
    return result

def create_default_template(template_type: str, technology_name: str = "Generic") -> Dict[str, Any]:
    """
    Create a default template based on the specified type
    
    Args:
        template_type: Type of template (guideline, rule, email, report)
        technology_name: Name of the technology
        
    Returns:
        Dict with template content and variables
    """
    if template_type == "guideline":
        content = """# {{ technology_name }} ESD & Latchup Guidelines

## Introduction
This document presents the ESD and latchup design guidelines for {{ technology_name }} technology.

## ESD Protection Guidelines
{{ esd_guidelines }}

## Latchup Prevention Guidelines
{{ latchup_guidelines }}

## Rules Summary
{{ rules_summary }}
"""
        variables = {
            "technology_name": technology_name,
            "esd_guidelines": "Place ESD guidelines here",
            "latchup_guidelines": "Place latchup guidelines here",
            "rules_summary": "Summary of rules goes here"
        }
        
    elif template_type == "rule":
        content = """## {{ rule_title }}

**Type:** {{ rule_type }}  
**Severity:** {{ severity }}  
**Category:** {{ category }}

### Description
{{ content }}

### Explanation
{{ explanation }}

{% if implementation_notes %}
### Implementation Notes
{{ implementation_notes }}
{% endif %}

{% if examples %}
### Examples
{{ examples }}
{% endif %}
"""
        variables = {
            "rule_title": "Rule Title",
            "rule_type": "ESD",
            "severity": "Critical",
            "category": "IO Protection",
            "content": "Rule content goes here",
            "explanation": "Rule explanation goes here",
            "implementation_notes": "Implementation notes go here",
            "examples": "Examples go here"
        }
        
    elif template_type == "email":
        content = """Subject: {{ technology_name }} - {{ subject }}

Dear {{ recipient_name }},

{{ email_body }}

Best regards,
{{ sender_name }}
{{ organization }}
"""
        variables = {
            "technology_name": technology_name,
            "subject": "ESD & Latchup Guidelines Update",
            "recipient_name": "Recipient Name",
            "email_body": "Email body goes here",
            "sender_name": "Sender Name",
            "organization": "Organization Name"
        }
        
    elif template_type == "report":
        content = """# {{ report_title }}
## {{ technology_name }} Technology
**Generated on:** {{ generation_date }}

## Summary
{{ summary }}

## Details
{{ details }}

## Statistics
- Total Rules: {{ total_rules }}
- ESD Rules: {{ esd_rules }}
- Latchup Rules: {{ latchup_rules }}
- General Rules: {{ general_rules }}
"""
        variables = {
            "report_title": "ESD & Latchup Rules Report",
            "technology_name": technology_name,
            "generation_date": "YYYY-MM-DD",
            "summary": "Report summary goes here",
            "details": "Report details go here",
            "total_rules": 0,
            "esd_rules": 0,
            "latchup_rules": 0,
            "general_rules": 0
        }
        
    else:
        content = "# {{ title }}\n\n{{ content }}"
        variables = {"title": "Template Title", "content": "Template content goes here"}
    
    return {
        "content": content,
        "variables": variables,
        "css_styles": "body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }"
    }
