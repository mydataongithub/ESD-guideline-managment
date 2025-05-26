"""
Model Context Protocol (MCP) Client for the Guideline Generator Application.

This module provides functionality to connect with an MCP server for advanced document analysis
and rule extraction using AI models.
"""
import httpx
import json
import asyncio
import os
import base64
from typing import Dict, Any, List, Optional, Union, BinaryIO
import logging
from pathlib import Path
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_client")

class MCPClient:
    """Client for interacting with a Model Context Protocol server."""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            server_url: Base URL of the MCP server
            api_key: API key for authentication (optional)
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}" if api_key else "",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=60.0  # Increased timeout for document processing
        )
        
    async def close(self):
        """Close the HTTP client session."""
        await self.client.aclose()
        
    async def ping(self) -> bool:
        """
        Check if the MCP server is available.
        
        Returns:
            True if server is available, False otherwise
        """
        try:
            response = await self.client.get(f"{self.server_url}/ping")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pinging MCP server: {str(e)}")
            return False
            
    async def analyze_document(
        self, 
        file_content: bytes, 
        file_name: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Send a document to the MCP server for analysis.
        
        Args:
            file_content: Binary content of the file
            file_name: Original filename
            document_type: Type of document (excel, pdf, word)
            
        Returns:
            Dictionary containing analysis results
        """
        # Convert file content to base64 for transmission
        encoded_content = base64.b64encode(file_content).decode()
        
        payload = {
            "document": {
                "name": file_name,
                "type": document_type,
                "content": encoded_content
            },
            "analysis_type": "rule_extraction",
            "options": {
                "extract_rules": True,
                "extract_metadata": True,
                "extract_images": True,
                "use_advanced_models": True
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.server_url}/analyze",
                json=payload
            )
            
            if response.status_code == 202:
                # Asynchronous processing - get task ID
                task_id = response.json().get("task_id")
                return await self._poll_task_result(task_id)
            elif response.status_code == 200:
                # Synchronous response
                return response.json()
            else:
                error_msg = f"Error analyzing document: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            logger.error(f"Exception during document analysis: {str(e)}")
            return {"error": str(e)}
    
    async def _poll_task_result(self, task_id: str, max_retries: int = 30, retry_delay: int = 2) -> Dict[str, Any]:
        """
        Poll for the result of an asynchronous task.
        
        Args:
            task_id: ID of the task to poll for
            max_retries: Maximum number of polling attempts
            retry_delay: Delay between polling attempts in seconds
            
        Returns:
            Task result or error information
        """
        retries = 0
        
        while retries < max_retries:
            try:
                response = await self.client.get(f"{self.server_url}/tasks/{task_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "")
                    
                    if status == "completed":
                        return data.get("result", {})
                    elif status == "failed":
                        return {"error": data.get("error", "Task failed")}
                    elif status == "processing":
                        # Still processing, wait and retry
                        await asyncio.sleep(retry_delay)
                        retries += 1
                        continue
                else:
                    return {"error": f"Error checking task status: {response.status_code} - {response.text}"}
                    
            except Exception as e:
                return {"error": f"Exception during task polling: {str(e)}"}
                
        return {"error": "Maximum retries reached while waiting for task completion"}
        
    async def extract_rules_with_ai(self, file_content: bytes, file_name: str, document_type: str) -> Dict[str, Any]:
        """
        Extract rules from a document using AI assistance.
        
        Args:
            file_content: Binary content of the file
            file_name: Original filename
            document_type: Type of document (excel, pdf, word)
            
        Returns:
            Dictionary with extracted rules, metadata and images
        """
        result = await self.analyze_document(file_content, file_name, document_type)
        
        # Handle error cases
        if "error" in result:
            return {"rules": [], "metadata": {}, "images": [], "error": result["error"]}
            
        # Process and format the results
        processed_result = {
            "rules": [],
            "metadata": result.get("metadata", {}),
            "images": []
        }
        
        # Process extracted rules
        if "rules" in result:
            processed_result["rules"] = [
                {
                    "title": rule.get("title", ""),
                    "content": rule.get("content", ""),
                    "rule_type": rule.get("type", "general").lower(),
                    "severity": rule.get("severity", "medium"),
                    "category": rule.get("category", "general"),
                    "confidence": rule.get("confidence", 0.0)
                }
                for rule in result["rules"]
            ]
            
        # Process extracted images
        if "images" in result:
            processed_result["images"] = [
                {
                    "filename": img.get("name", f"image_{i}.png"),
                    "image_data": base64.b64decode(img.get("content", "")),
                    "mime_type": img.get("mime_type", "image/png"),
                    "description": img.get("description", "")
                }
                for i, img in enumerate(result["images"])
            ]
            
        return processed_result
