# app/parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseParser(ABC):
    """Abstract base class for document parsers."""
    
    def __init__(self, file_path: Optional[str] = None, file_content: Optional[bytes] = None):
        """
        Initialize parser with either file path or content.
        
        Args:
            file_path: Path to the document file
            file_content: Raw bytes of the document
        """
        if not file_path and not file_content:
            raise ValueError("Either file_path or file_content must be provided")
            
        self.file_path = file_path
        self.file_content = file_content
    
    @abstractmethod
    def extract_rules(self) -> List[Dict[str, Any]]:
        """
        Extract rules from the document.
        
        Returns:
            A list of dictionaries with extracted rule data
        """
        pass
    
    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract document metadata.
        
        Returns:
            A dictionary with metadata (author, creation date, etc.)
        """
        pass
    
    @abstractmethod
    def extract_images(self) -> List[Dict[str, Any]]:
        """
        Extract images from the document.
        
        Returns:
            A list of dictionaries with image data and metadata
        """
        pass
    
    def process(self) -> Dict[str, Any]:
        """
        Process the document and extract all available information.
        
        Returns:
            A dictionary with rules, metadata, and images
        """
        return {
            "rules": self.extract_rules(),
            "metadata": self.extract_metadata(),
            "images": self.extract_images()
        }
