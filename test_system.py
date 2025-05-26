#!/usr/bin/env python3
"""
Test script to verify the ESD & Latch-up Guideline Generator installation and functionality.
Windows-compatible version without Unicode emojis.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core import generator, git_utils
    from app.models.schemas import GuidelineResponse
    print("[OK] Successfully imported application modules")
except ImportError as e:
    print(f"[ERROR] Failed to import application modules: {e}")
    sys.exit(1)

def test_configuration_loading():
    """Test loading of technology configurations."""
    print("\n[TEST] Testing configuration loading...")
    
    try:
        technologies = generator.get_available_technologies()
        print(f"[OK] Found {len(technologies)} technologies: {', '.join(technologies)}")
        
        if not technologies:
            print("[WARNING] No technologies found. Please add configuration files.")
            return False
        
        # Test loading each technology
        for tech in technologies:
            try:
                params = generator.load_tech_params(tech)
                print(f"[OK] Successfully loaded configuration for {tech}")
                
                # Validate required fields
                required_fields = ['esd_levels', 'latch_up_rules', 'approved_clamps']
                for field in required_fields:
                    if field not in params:
                        print(f"[WARNING] Missing required field '{field}' in {tech}")
                        return False
                
            except Exception as e:
                print(f"[ERROR] Failed to load configuration for {tech}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuration loading test failed: {e}")
        return False

def test_template_processing():
    """Test Markdown template processing."""
    print("\n[TEST] Testing template processing...")
    
    try:
        technologies = generator.get_available_technologies()
        if not technologies:
            print("[ERROR] No technologies available for testing")
            return False
        
        test_tech = technologies[0]
        print(f"Testing with technology: {test_tech}")
        
        # Generate guideline content
        markdown_content = generator.generate_guideline_markdown(test_tech)
        
        if len(markdown_content) < 100:
            print("[ERROR] Generated content appears too short")
            return False
        
        # Check for basic template elements
        required_elements = [
            f"# ESD and Latch-up Guidelines for {test_tech.upper()}",
            "## 1. Introduction",
            "## 2. General ESD Requirements",
            "## 3. Latch-up Prevention Rules",
            "## 4. Approved ESD Protection Devices"
        ]
        
        for element in required_elements:
            if element not in markdown_content:
                print(f"[ERROR] Missing required element: {element}")
                return False
        
        print(f"[OK] Successfully generated {len(markdown_content)} characters of content")
        print(f"[OK] All required template elements present")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Template processing test failed: {e}")
        return False

def test_file_operations():
    """Test file saving operations."""
    print("\n[TEST] Testing file operations...")
    
    try:
        technologies = generator.get_available_technologies()
        if not technologies:
            print("[ERROR] No technologies available for testing")
            return False
        
        test_tech = technologies[0]
        
        # Generate and save guideline
        markdown_content = generator.generate_guideline_markdown(test_tech)
        saved_path = generator.save_guideline(test_tech, markdown_content)
        
        if not saved_path.exists():
            print(f"[ERROR] File was not saved to {saved_path}")
            return False
        
        # Verify file content
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        if saved_content != markdown_content:
            print("[ERROR] Saved content doesn't match generated content")
            return False
        
        print(f"[OK] Successfully saved guideline to {saved_path}")
        print(f"[OK] File content verified")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] File operations test failed: {e}")
        return False

def test_git_operations():
    """Test Git repository operations."""
    print("\n[TEST] Testing Git operations...")
    
    try:
        # Test repository initialization
        repo = git_utils.get_repo()
        if repo is None:
            print("[INFO] Git not available - this is OK, version control features will be disabled")
            print("  To enable Git features:")
            print("  1. Install Git: https://git-scm.com/downloads")
            print("  2. Restart the application")
            return True
        
        print("[OK] Git repository initialized/accessed")
        
        # Test repository status
        status = git_utils.get_repository_status()
        if not status.get('git_available', True):
            print(f"[INFO] Git repository status: {status.get('message', 'Not available')}")
            print("This is normal if Git is not installed or configured")
            return True  # Don't fail the test for Git issues
        
        print("[OK] Git repository status retrieved")
        
        # Test with actual file if available
        technologies = generator.get_available_technologies()
        if technologies:
            test_tech = technologies[0]
            
            # Generate and save a test file
            markdown_content = generator.generate_guideline_markdown(test_tech)
            saved_path = generator.save_guideline(test_tech, markdown_content)
            
            # Try to commit (may fail if Git not configured, which is OK)
            try:
                commit_success = git_utils.commit_guideline(saved_path, test_tech, "Test commit")
                if commit_success:
                    print("[OK] Successfully committed test file")
                else:
                    print("[INFO] No changes to commit (file already exists) or Git not available")
            except Exception as git_error:
                print(f"[INFO] Git commit skipped: {git_error}")
        
        return True
        
    except Exception as e:
        print(f"[INFO] Git operations test encountered issues: {e}")
        print("This is normal if Git is not installed or configured")
        return True  # Don't fail for Git issues

def test_api_models():
    """Test Pydantic model validation."""
    print("\n[TEST] Testing API models...")
    
    try:
        # Test GuidelineResponse model
        test_response = GuidelineResponse(
            technology="test_tech",
            message="Test message",
            file_path="test/path.md",
            content="Test content"
        )
        
        print("[OK] GuidelineResponse model validation successful")
        
        # Test model serialization
        json_data = test_response.model_dump()
        if not isinstance(json_data, dict):
            print("[ERROR] Model serialization failed")
            return False
        
        print("[OK] Model serialization successful")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API models test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\n[TEST] Testing dependencies...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'markdown2',
        'pydantic'
    ]
    
    optional_modules = [
        'git'  # Git is optional - system works without it
    ]
    
    missing_modules = []
    missing_optional = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"[OK] {module} is available")
        except ImportError:
            print(f"[ERROR] {module} is NOT available")
            missing_modules.append(module)
    
    for module in optional_modules:
        try:
            if module == 'git':
                import git
                # Test if git executable is available
                try:
                    git.Repo.init('test_temp_repo', bare=True)
                    import shutil
                    shutil.rmtree('test_temp_repo')
                    print(f"[OK] {module} is available and working")
                except Exception:
                    print(f"[INFO] {module} library available but Git executable not found")
                    missing_optional.append(module)
            else:
                __import__(module)
                print(f"[OK] {module} is available")
        except ImportError:
            print(f"[INFO] {module} is not available (optional)")
            missing_optional.append(module)
    
    if missing_modules:
        print(f"\n[ERROR] Missing required modules: {', '.join(missing_modules)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n[INFO] Missing optional modules: {', '.join(missing_optional)}")
        if 'git' in missing_optional:
            print("  To enable version control features:")
            print("  1. Install Git: https://git-scm.com/downloads")
            print("  2. Ensure Git is in your system PATH")
            print("  3. Restart the application")
        print("  System will work without these optional features.")
    
    return True

def main():
    """Run all tests."""
    print("ESD & Latch-up Guideline Generator - System Test")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Configuration Loading", test_configuration_loading),
        ("Template Processing", test_template_processing),
        ("File Operations", test_file_operations),
        ("Git Operations", test_git_operations),
        ("API Models", test_api_models),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"[OK] {test_name}: PASSED")
            else:
                print(f"[ERROR] {test_name}: FAILED")
        except Exception as e:
            print(f"[ERROR] {test_name}: ERROR - {e}")
    
    print("\n" + "="*60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! System is ready to use.")
        print("\nTo start the server, run:")
        print("  uvicorn app.main:app --reload")
        print("  or")
        print("  python -m uvicorn app.main:app --reload")
        print("  or")
        print("  start_server.bat")
        sys.exit(0)
    else:
        print("[WARNING] Some tests failed. Please check the output above.")
        print("The system may still work with limited functionality.")
        sys.exit(1)

if __name__ == "__main__":
    main()
