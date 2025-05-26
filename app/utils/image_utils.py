# app/utils/image_utils.py
"""
Utility functions for handling images in the application.
This supports the enhanced image storage capabilities added in task #5.
"""

import os
import base64
from typing import Optional, Tuple, Dict, Any
from io import BytesIO
import logging
from PIL import Image, UnidentifiedImageError

# Configure logging
logger = logging.getLogger(__name__)

def get_image_dimensions(image_data: bytes) -> Tuple[int, int]:
    """
    Get the dimensions (width, height) of an image from its binary data.
    
    Args:
        image_data: Raw binary image data
        
    Returns:
        Tuple of (width, height) in pixels
        
    Raises:
        ValueError: If the image data is invalid
    """
    try:
        with BytesIO(image_data) as img_io:
            with Image.open(img_io) as img:
                return img.size  # (width, height)
    except UnidentifiedImageError:
        logger.error("Could not identify image format")
        raise ValueError("Invalid image format")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}")

def get_image_metadata(image_data: bytes) -> Dict[str, Any]:
    """
    Extract metadata from an image.
    
    Args:
        image_data: Raw binary image data
        
    Returns:
        Dictionary containing image metadata
    """
    metadata = {}
    
    try:
        with BytesIO(image_data) as img_io:
            with Image.open(img_io) as img:
                metadata['width'], metadata['height'] = img.size
                metadata['format'] = img.format.lower() if img.format else "unknown"
                metadata['mode'] = img.mode
                
                if hasattr(img, 'info'):
                    # Extract EXIF data if available
                    if 'exif' in img.info:
                        metadata['exif'] = True
                        
                    # Get DPI information if available
                    if 'dpi' in img.info:
                        metadata['dpi'] = img.info['dpi']
    
    except Exception as e:
        logger.error(f"Error extracting image metadata: {str(e)}")
        metadata['error'] = str(e)
        
    return metadata

def optimize_image(image_data: bytes, quality: int = 85, max_size: Optional[Tuple[int, int]] = None) -> bytes:
    """
    Optimize an image by reducing its quality and/or resizing it.
    
    Args:
        image_data: Raw binary image data
        quality: JPEG quality (1-100)
        max_size: Maximum dimensions as (width, height)
        
    Returns:
        Optimized image data as bytes
    """
    try:
        with BytesIO(image_data) as img_io:
            with Image.open(img_io) as img:
                # Resize if max_size is specified and the image is larger
                if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                    img.thumbnail(max_size, Image.LANCZOS)
                
                # Convert to RGB if image has alpha channel (to avoid RGBA to JPEG error)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Save optimized image to bytes
                output = BytesIO()
                img.save(output, format=img.format or 'JPEG', quality=quality, optimize=True)
                return output.getvalue()
                
    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}")
        return image_data  # Return original if optimization fails

def image_to_base64(image_data: bytes, mime_type: Optional[str] = None) -> str:
    """
    Convert image data to base64 string for embedding in HTML.
    
    Args:
        image_data: Raw binary image data
        mime_type: MIME type of the image (e.g., 'image/jpeg')
        
    Returns:
        Base64-encoded string representing the image
    """
    encoded = base64.b64encode(image_data).decode('utf-8')
    
    # Try to determine MIME type if not provided
    if not mime_type:
        try:
            with BytesIO(image_data) as img_io:
                with Image.open(img_io) as img:
                    format_map = {
                        'JPEG': 'image/jpeg',
                        'JPG': 'image/jpeg',
                        'PNG': 'image/png',
                        'GIF': 'image/gif',
                        'BMP': 'image/bmp',
                        'WEBP': 'image/webp'
                    }
                    mime_type = format_map.get(img.format, 'image/jpeg')
        except:
            mime_type = 'image/jpeg'  # Default to JPEG
    
    return encoded
