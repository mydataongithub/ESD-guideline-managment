# -*- coding: utf-8 -*-
# Implementation Test Report
# Generated on: 2025-05-26

import sys
import os
import time
import json
import sqlite3
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("ESD & LATCHUP GUIDELINES SYSTEM - IMPLEMENTATION TEST")
print("=" * 60)
print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 60)

# Test results storage
test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "details": []
}

def test_step(name, func):
    """Execute a test step and record results"""
    print(f"\n[TEST] {name}")
    try:
        result = func()
        if result.get("status") == "passed":
            print(f"  [PASS] {result.get('message', 'Test completed successfully')}")
            test_results["passed"] += 1
        elif result.get("status") == "warning":
            print(f"  [WARN] {result.get('message', 'Test completed with warnings')}")
            test_results["warnings"] += 1
        else:
            print(f"  [FAIL] {result.get('message', 'Test failed')}")
            test_results["failed"] += 1
        test_results["details"].append({"test": name, **result})
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        test_results["failed"] += 1
        test_results["details"].append({
            "test": name,
            "status": "failed",
            "message": str(e)
        })

# Test 1: Check Python Version
def test_python_version():
    import sys
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return {"status": "passed", "message": f"Python {version.major}.{version.minor}.{version.micro}"}
    else:
        return {"status": "failed", "message": f"Python {version.major}.{version.minor} (3.8+ required)"}

# Test 2: Check Required Packages
def test_required_packages():
    # First check if uv is available
    import subprocess
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        uv_available = True
    except:
        uv_available = False
    
    missing_packages = []
    packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
        "python-multipart", "jinja2", "markdown2", "pandas",
        "openpyxl", "pdfplumber", "docx", "PIL"
    ]
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if not uv_available:
        return {
            "status": "warning",
            "message": f"UV not installed (use 'pip install uv'). {len(packages) - len(missing_packages)}/{len(packages)} packages installed"
        }
    
    if missing_packages:
        install_cmd = "uv pip install" if uv_available else "pip install"
        return {
            "status": "failed", 
            "message": f"Missing packages: {', '.join(missing_packages)}. Install with: {install_cmd} {' '.join(missing_packages)}"
        }
    return {"status": "passed", "message": f"All {len(packages)} required packages installed (uv available)"}

# Test 3: Check Directory Structure
def test_directory_structure():
    required_dirs = [
        "app", "app/api", "app/core", "app/crud", "app/database",
        "app/models", "app/parsers", "app/static", "app/templates",
        "app/utils", "config", "samples"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        return {
            "status": "failed",
            "message": f"Missing directories: {', '.join(missing_dirs)}"
        }
    return {"status": "passed", "message": "All required directories present"}

# Test 4: Check Database
def test_database():
    db_path = "esd_guidelines.db"
    if not os.path.exists(db_path):
        return {"status": "failed", "message": "Database file not found"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            "technologies", "rules", "rule_images", "imported_documents",
            "validation_queue", "templates"
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            return {
                "status": "failed",
                "message": f"Missing tables: {', '.join(missing_tables)}"
            }
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM technologies")
        tech_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rules")
        rule_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "passed",
            "message": f"Database OK - {len(tables)} tables, {tech_count} technologies, {rule_count} rules"
        }
    except Exception as e:
        return {"status": "failed", "message": f"Database error: {str(e)}"}

# Test 5: Check Templates
def test_templates():
    template_files = [
        "dashboard.html", "document_list.html", "document_upload.html",
        "rule_editor.html", "rule_management.html", "rule_view.html",
        "template_editor.html", "template_editor_new.html", "template_management.html",
        "validation_dashboard.html", "validation_list.html", "validation_review.html"
    ]
    
    missing_templates = []
    for template in template_files:
        if not os.path.exists(f"app/templates/{template}"):
            missing_templates.append(template)
    
    if missing_templates:
        return {
            "status": "warning",
            "message": f"Missing templates: {', '.join(missing_templates[:3])}..."
        }
    return {"status": "passed", "message": f"All {len(template_files)} templates present"}

# Test 6: Check API Endpoints
def test_api_endpoints():
    try:
        from app.main import app
        routes = []
        for route in app.routes:
            if hasattr(route, "path"):
                routes.append(route.path)
        
        required_endpoints = [
            "/api/rules", "/api/templates", "/docs/api/upload",
            "/validation/api", "/rules", "/templates"
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if not any(endpoint in route for route in routes):
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            return {
                "status": "warning",
                "message": f"Missing endpoints: {', '.join(missing_endpoints)}"
            }
        
        return {
            "status": "passed",
            "message": f"API configured with {len(routes)} routes"
        }
    except Exception as e:
        return {"status": "failed", "message": f"Cannot load API: {str(e)}"}

# Test 7: Check Import Functionality
def test_import_functionality():
    parsers_ok = []
    parsers_failed = []
    
    try:
        from app.parsers.excel_parser import ExcelParser
        parsers_ok.append("Excel")
    except:
        parsers_failed.append("Excel")
    
    try:
        from app.parsers.pdf_parser import PDFParser
        parsers_ok.append("PDF")
    except:
        parsers_failed.append("PDF")
    
    try:
        from app.parsers.word_parser import WordParser
        parsers_ok.append("Word")
    except:
        parsers_failed.append("Word")
    
    if parsers_failed:
        return {
            "status": "warning",
            "message": f"Working: {', '.join(parsers_ok)}. Failed: {', '.join(parsers_failed)}"
        }
    return {"status": "passed", "message": f"All document parsers functional"}

# Test 8: Check Server Configuration
def test_server_configuration():
    config_files = ["start_server.bat", "start_server.sh", "requirements.txt"]
    missing_files = []
    
    for file in config_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        return {
            "status": "warning",
            "message": f"Missing config files: {', '.join(missing_files)}"
        }
    return {"status": "passed", "message": "Server configuration files present"}

# Test 9: Test Sample Data
def test_sample_data():
    sample_files = []
    for root, dirs, files in os.walk("samples"):
        for file in files:
            if file.endswith(('.xlsx', '.pdf', '.docx')):
                sample_files.append(file)
    
    if not sample_files:
        return {"status": "warning", "message": "No sample files found"}
    return {"status": "passed", "message": f"Found {len(sample_files)} sample files"}

# Test 10: Check Documentation
def test_documentation():
    doc_files = ["README.md", "QUICKSTART.md", "USER_GUIDE.md", "TASK.md", "UV_BENEFITS.md"]
    missing_docs = []
    
    for doc in doc_files:
        if not os.path.exists(doc):
            missing_docs.append(doc)
    
    if missing_docs:
        # Don't fail if only UV_BENEFITS.md is missing
        if missing_docs == ["UV_BENEFITS.md"]:
            return {"status": "passed", "message": "All core documentation files present"}
        return {
            "status": "warning",
            "message": f"Missing docs: {', '.join(missing_docs)}"
        }
    return {"status": "passed", "message": "All documentation files present"}

# Run all tests
print("\nStarting comprehensive system test...\n")

test_step("Python Version", test_python_version)
test_step("Required Packages", test_required_packages)
test_step("Directory Structure", test_directory_structure)
test_step("Database", test_database)
test_step("Templates", test_templates)
test_step("API Endpoints", test_api_endpoints)
test_step("Import Functionality", test_import_functionality)
test_step("Server Configuration", test_server_configuration)
test_step("Sample Data", test_sample_data)
test_step("Documentation", test_documentation)

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Total Tests: {test_results['passed'] + test_results['failed'] + test_results['warnings']}")
print(f"[PASS] Passed: {test_results['passed']}")
print(f"[WARN] Warnings: {test_results['warnings']}")
print(f"[FAIL] Failed: {test_results['failed']}")
print("-" * 60)

# Overall Status
if test_results["failed"] == 0:
    if test_results["warnings"] == 0:
        print("\n*** ALL TESTS PASSED! System is ready for use.")
    else:
        print("\n*** System is functional with minor warnings.")
else:
    print("\n*** System has critical issues that need to be resolved.")

# Save test report
report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_filename, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": test_results['passed'] + test_results['failed'] + test_results['warnings'],
            "passed": test_results['passed'],
            "warnings": test_results['warnings'],
            "failed": test_results['failed']
        },
        "details": test_results['details']
    }, f, indent=2)

print(f"\nDetailed report saved to: {report_filename}")
print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
