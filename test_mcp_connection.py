"""
Test MCP server connection and functionality.

This script checks if the MCP server is available and tests basic functionality
by analyzing a sample document.

Usage:
    python test_mcp_connection.py
"""
import asyncio
import os
from datetime import datetime
import argparse

from app.core.mcp_client import MCPClient
from app.core.mcp_config import load_mcp_config


async def test_connection(server_url=None, api_key=None):
    """Test connection to the MCP server."""
    # Load config or use provided values
    config = load_mcp_config()
    server_url = server_url or config["server_url"]
    api_key = api_key or config["api_key"]
    
    print(f"Testing connection to MCP server at: {server_url}")
    
    # Initialize client
    client = MCPClient(server_url=server_url, api_key=api_key)
    
    try:
        # Test ping
        print("Pinging server...")
        is_available = await client.ping()
        
        if is_available:
            print("✅ Connection successful!")
        else:
            print("❌ Server is not responding.")
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
    finally:
        await client.close()


async def test_document_analysis(file_path=None, server_url=None, api_key=None):
    """Test document analysis with a sample document."""
    if not file_path:
        print("No test file specified. Please provide a file path.")
        return
        
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Load config or use provided values
    config = load_mcp_config()
    server_url = server_url or config["server_url"]
    api_key = api_key or config["api_key"]
    
    # Get file info
    file_name = os.path.basename(file_path)
    _, file_ext = os.path.splitext(file_name)
    
    # Determine document type
    if file_ext.lower() in ['.xlsx', '.xls']:
        doc_type = 'excel'
    elif file_ext.lower() == '.pdf':
        doc_type = 'pdf'
    elif file_ext.lower() in ['.doc', '.docx']:
        doc_type = 'word'
    else:
        print(f"Unsupported file type: {file_ext}")
        return
    
    print(f"Testing document analysis with file: {file_name} (type: {doc_type})")
    
    # Initialize client
    client = MCPClient(server_url=server_url, api_key=api_key)
    
    try:
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Start time
        start_time = datetime.now()
        print(f"Sending document to MCP server at {start_time.strftime('%H:%M:%S')}...")
        
        # Analyze document
        result = await client.extract_rules_with_ai(
            file_content=file_content,
            file_name=file_name,
            document_type=doc_type
        )
        
        # End time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Check for errors
        if "error" in result:
            print(f"❌ Analysis error: {result['error']}")
            return
        
        # Print results
        print(f"✅ Analysis completed in {duration:.2f} seconds!")
        print(f"Extracted {len(result['rules'])} rules")
        print(f"Extracted {len(result['images'])} images")
        print("\nSample rules:")
        
        # Print up to 3 sample rules
        for i, rule in enumerate(result['rules'][:3]):
            print(f"\n--- Rule {i+1} ---")
            print(f"Title: {rule.get('title', 'No title')}")
            print(f"Type: {rule.get('rule_type', 'general')}")
            if 'confidence' in rule:
                print(f"Confidence: {rule['confidence']:.2f}")
            print("Content excerpt: " + rule.get('content', 'No content')[:100] + "...")
            
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
    finally:
        await client.close()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test MCP server connection and functionality.')
    parser.add_argument('--url', help='MCP server URL')
    parser.add_argument('--key', help='MCP server API key')
    parser.add_argument('--file', help='Path to a test document file')
    args = parser.parse_args()
    
    # Test connection
    await test_connection(server_url=args.url, api_key=args.key)
    
    # Test document analysis if file provided
    if args.file:
        print("\n" + "="*50 + "\n")
        await test_document_analysis(
            file_path=args.file,
            server_url=args.url,
            api_key=args.key
        )


if __name__ == "__main__":
    asyncio.run(main())
