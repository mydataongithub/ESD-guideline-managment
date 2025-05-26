# app/parsers/pdf_parser.py
import io
from typing import Dict, Any, List, Optional
import PyPDF2
from PIL import Image
import re
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """Parser to extract rule information from PDF documents."""
    
    def __init__(self, file_path: Optional[str] = None, file_content: Optional[bytes] = None):
        super().__init__(file_path, file_content)
        # Open PDF from file path or content
        if file_path:
            self.pdf = PyPDF2.PdfReader(file_path)
        else:
            self.pdf = PyPDF2.PdfReader(io.BytesIO(file_content))
        
    def extract_rules(self) -> List[Dict[str, Any]]:
        """
        Extract rules from PDF content.
        Uses pattern matching to identify rule-like content.
        
        Returns:
            List of dictionaries with rule data
        """
        rules = []
        full_text = self._extract_full_text()
        
        # Look for rule patterns
        # Pattern 1: "Rule X: [Title]" followed by content
        rule_pattern1 = re.compile(r'Rule\s+(\d+):?\s+(.*?)(?:\n|$)(.*?)(?=Rule\s+\d+:|$)', re.DOTALL)
        for match in rule_pattern1.finditer(full_text):
            rule_number, title, content = match.groups()
            content = content.strip()
            if title and content:
                rule = {
                    "title": f"Rule {rule_number}: {title.strip()}",
                    "content": content,
                    "rule_type": self._detect_rule_type(title, content)
                }
                rules.append(rule)
        
        # Pattern 2: "X.Y [Title]" followed by content (common in technical docs)
        rule_pattern2 = re.compile(r'(\d+\.\d+)\s+(.*?)(?:\n|$)(.*?)(?=\d+\.\d+\s+|$)', re.DOTALL)
        if not rules:  # Only try alternative pattern if first didn't find any
            for match in rule_pattern2.finditer(full_text):
                rule_number, title, content = match.groups()
                content = content.strip()
                if title and content:
                    rule = {
                        "title": f"{rule_number} {title.strip()}",
                        "content": content,
                        "rule_type": self._detect_rule_type(title, content)
                    }
                    rules.append(rule)
        
        # Fall back to section headers if no rules found with previous patterns
        if not rules:
            # Look for sections that might be rules
            section_pattern = re.compile(r'(\d+\s+.*?)(?:\n|$)(.*?)(?=\d+\s+|$)', re.DOTALL)
            for match in section_pattern.finditer(full_text):
                title, content = match.groups()
                content = content.strip()
                if len(title) < 100 and content and len(content) > 20:  # Filter out non-rule sections
                    rule = {
                        "title": title.strip(),
                        "content": content,
                        "rule_type": self._detect_rule_type(title, content)
                    }
                    rules.append(rule)
        
        return rules
    
    def _extract_full_text(self) -> str:
        """
        Extract all text from the PDF.
        
        Returns:
            The full text content
        """
        text = ""
        for page in self.pdf.pages:
            try:
                text += page.extract_text() + "\n\n"
            except:
                # Skip pages that cause extraction errors
                pass
        return text
    
    def _detect_rule_type(self, title: str, content: str) -> str:
        """
        Try to detect rule type from title and content.
        
        Args:
            title: Rule title
            content: Rule content
            
        Returns:
            Rule type (esd, latchup, or general)
        """
        combined_text = (title + " " + content).lower()
        
        if "esd" in combined_text:
            return "esd"
        elif any(term in combined_text for term in ["latchup", "latch-up", "latch up"]):
            return "latchup"
        return "general"
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the PDF document.
        
        Returns:
            Dictionary with metadata
        """
        metadata = {}
        
        # Extract document info
        info = self.pdf.metadata
        if info:
            if info.get('/Title'):
                metadata["title"] = info['/Title']
            if info.get('/Subject'):
                metadata["subject"] = info['/Subject']
            if info.get('/Author'):
                metadata["author"] = info['/Author']
            if info.get('/Producer'):
                metadata["producer"] = info['/Producer']
            if info.get('/Creator'):
                metadata["creator"] = info['/Creator']
            if info.get('/CreationDate'):
                # Convert PDF date format to standard date
                try:
                    date_str = info['/CreationDate']
                    if date_str.startswith('D:'):
                        date_str = date_str[2:]
                    metadata["created"] = date_str
                except:
                    pass
        
        # Add page count
        metadata["pages"] = len(self.pdf.pages)
        
        return metadata
    
    def extract_images(self) -> List[Dict[str, Any]]:
        """
        Extract images from the PDF document.
        This is a simplified implementation and might not work for all PDFs.
        
        Returns:
            List of dictionaries with image data
        """
        images = []
        
        # Extracting images from PDFs is complex and unreliable
        # This is a simplified approach that works for some PDFs
        for page_num, page in enumerate(self.pdf.pages):
            count = 0
            for img in page.images:
                try:
                    image_data = {
                        "page": page_num + 1,
                        "filename": f"image_page{page_num+1}_{count}.{img.ext}",
                        "image_data": img.data,
                        "mime_type": f"image/{img.ext}"
                    }
                    images.append(image_data)
                    count += 1
                except (KeyError, AttributeError):
                    # Skip images that can't be processed
                    pass
        
        return images
