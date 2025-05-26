# ESD & Latchup Guidelines Generator - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Getting Started](#getting-started)
4. [Dashboard](#dashboard)
5. [Document Import System](#document-import-system)
6. [Validation Queue](#validation-queue)
7. [Template Management](#template-management)
8. [Rule Management](#rule-management)
9. [MCP Server Integration](#mcp-server-integration)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

The ESD & Latchup Guidelines Generator is a comprehensive system for managing Electrostatic Discharge (ESD) and Latchup rules for semiconductor design. It provides tools for:

- Importing rules from various document formats
- Expert validation of extracted rules
- Template-based document generation
- Comprehensive rule management
- Integration with AI-powered analysis tools

### Key Features

- **Multi-format Document Import**: Support for Excel, PDF, and Word documents
- **AI-Powered Extraction**: Automatic rule extraction using MCP server integration
- **Expert Validation**: Human-in-the-loop validation system
- **Template Engine**: Customizable templates for document generation
- **Rule Database**: Organized storage with categorization and search
- **RESTful API**: Programmatic access to all features

---

## 2. System Architecture

### Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│  FastAPI Backend │────▶│  SQLite Database │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   MCP Server    │
                        └─────────────────┘
```

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, JavaScript
- **Document Processing**: 
  - PDFPlumber (PDF extraction)
  - python-docx (Word documents)
  - openpyxl (Excel files)
- **AI Integration**: MCP Server for advanced analysis

---

## 3. Getting Started

### System Requirements

- Python 3.8+
- 4GB RAM minimum
- 1GB free disk space
- Modern web browser

### Installation

1. **Set up Python environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**
   ```bash
   # Install uv if not already installed
   pip install uv
   
   # Install project dependencies
   uv pip install -r requirements.txt
   ```

3. **Initialize database**
   ```bash
   python init_database.py
   ```

4. **Start the server**
   ```bash
   # Windows
   start_server.bat
   
   # Linux/Mac
   ./start_server.sh
   ```

5. **Access the application**
   Navigate to `http://localhost:8000` in your browser

### System Management Commands

The `manage.py` script provides utilities for system administration:

#### Available Commands:

**1. List Technologies**
```bash
python manage.py list
```
Shows all configured technologies with their process type and HBM levels.

**2. Check System Status**
```bash
python manage.py status
```
Displays:
- Number of configured technologies
- Generated guidelines count  
- Git repository status
- Configuration files status

**3. Generate Guidelines**
```bash
python manage.py generate
```
Automatically generates ESD/Latchup guideline documents for all configured technologies.

**4. Validate Configurations**
```bash
python manage.py validate
```
Checks all JSON configuration files for:
- Required fields (esd_levels, latch_up_rules, approved_clamps)
- Proper structure
- Valid JSON syntax

**5. Create System Backup**
```bash
python manage.py backup
```
Creates a complete backup of the entire system (excluding cache and virtual environment).

**6. Clean Temporary Files**
```bash
python manage.py clean
```
Removes:
- Generated guideline files
- Python cache directories (`__pycache__`)
- Empty directories

#### Example Usage:

To check the system status after installation:
```bash
python manage.py status
```

To validate your technology configurations:
```bash
python manage.py validate
```

---

## 4. Dashboard

The dashboard provides an overview of your ESD & Latchup guidelines system.

### Features

- **Statistics Overview**
  - Total rules count
  - ESD rules count
  - Latchup rules count
  - Technologies overview

- **Quick Actions**
  - Import new documents
  - View validation queue
  - Manage templates
  - Browse rules

### Navigation

From the dashboard, you can access all major features:
- Click statistics cards for filtered views
- Use the navigation bar for direct access
- View recent activity and updates

---

## 5. Document Import System

### Supported Formats

1. **Excel Files (.xlsx, .xls)**
   - Structured rule tables
   - Multiple sheets support
   - Automatic column detection

2. **PDF Files (.pdf)**
   - Text extraction
   - Table recognition
   - Image extraction

3. **Word Documents (.docx, .doc)**
   - Formatted text parsing
   - Table extraction
   - Embedded images

### Import Process

1. **Navigate to Import**
   - Click "Import Documents" in navigation
   - Or go to `/docs/import`

2. **Upload Document**
   - Drag and drop files
   - Or click to browse
   - Multiple file selection supported

3. **Processing**
   - Automatic format detection
   - Content extraction
   - Rule identification

4. **Review Results**
   - Preview extracted content
   - Check identified rules
   - Submit for validation

### Best Practices

- **Excel Format**
  ```
  | Rule ID | Type    | Title          | Description    | Severity |
  |---------|---------|----------------|----------------|----------|
  | ESD-001 | ESD     | Input Protection| Use ESD diodes | High     |
  | LU-001  | Latchup | Guard Rings    | Add guard rings| Medium   |
  ```

- **Document Structure**
  - Clear headings
  - Consistent formatting
  - Tabular data when possible

---

## 6. Validation Queue

The validation queue allows ESD experts to review and approve extracted rules.

### Workflow

1. **Access Queue**
   - Navigate to "Validation Queue"
   - View pending items count

2. **Review Item**
   - Click on item to expand
   - View extracted content
   - Check rule categorization

3. **Validation Actions**
   - **Approve**: Accept the rule as-is
   - **Edit**: Modify before approval
   - **Reject**: Remove from queue
   - **Request Changes**: Send back for modification

### Validation Interface

```
┌──────────────────────────────────────┐
│ Rule Title: [Extracted Title]        │
│ Type: [ESD/Latchup]                  │
│ Content: [Extracted content...]      │
│ Images: [Thumbnails if any]          │
│                                      │
│ [Approve] [Edit] [Reject]           │
└──────────────────────────────────────┘
```

### Expert Review Guidelines

1. **Verify Accuracy**
   - Technical correctness
   - Appropriate categorization
   - Complete information

2. **Check Formatting**
   - Clear title
   - Structured content
   - Proper severity level

3. **Validate Images**
   - Relevant diagrams
   - Clear quality
   - Appropriate captions

---

## 7. Template Management

Templates allow consistent document generation for guidelines.

### Template Types

1. **Guideline Templates**
   - Full document structure
   - Technology-specific
   - Version controlled

2. **Rule Templates**
   - Individual rule format
   - Categorized by type
   - Reusable components

3. **Report Templates**
   - Summary documents
   - Statistics reports
   - Export formats

### Creating Templates

1. **Access Template Manager**
   - Click "Templates" in navigation
   - Click "Create New Template"

2. **Template Editor Features**
   - **Live Preview**: See changes in real-time
   - **Variable System**: Use `{{ variable_name }}`
   - **CSS Styling**: Custom styles support
   - **Markdown Support**: Rich text formatting

3. **Template Variables**
   ```markdown
   # {{ technology_name }} ESD Guidelines
   
   Generated on: {{ generated_date }}
   Total Rules: {{ total_rules }}
   
   ## ESD Rules
   {{ esd_rules_list }}
   ```

4. **Save and Test**
   - Validate template syntax
   - Preview with sample data
   - Set as default if needed

### Template Best Practices

- Use meaningful variable names
- Include conditional sections
- Test with various data sets
- Version your templates

---

## 8. Rule Management

Comprehensive interface for managing all ESD and Latchup rules.

### Features

1. **Rule Browser**
   - Grid/List view
   - Pagination
   - Quick actions

2. **Filtering Options**
   - By Technology
   - By Type (ESD/Latchup/General)
   - By Severity
   - Text search

3. **Rule Operations**
   - Create new rules
   - Edit existing rules
   - Delete (soft delete)
   - Reorder rules
   - Bulk operations

### Creating a Rule

1. **Navigate to Rules**
   - Click "Rules" → "Create New Rule"

2. **Fill Rule Information**
   ```
   Title: [Descriptive title]
   Type: [ESD/Latchup/General]
   Technology: [Select from list]
   Severity: [High/Medium/Low]
   Content: [Rule description]
   Explanation: [Detailed explanation]
   ```

3. **Add Images**
   - Drag and drop images
   - Add captions
   - Reorder if needed

4. **Save Rule**
   - Validate required fields
   - Preview before saving
   - Publish or save as draft

### Rule Organization

- **Order Management**: Drag to reorder
- **Categories**: Organize by type
- **Tags**: Add searchable tags
- **Versioning**: Track changes

---

## 9. MCP Server Integration

The Model Context Protocol (MCP) server provides AI-powered analysis.

### Features

1. **Document Analysis**
   - Intelligent extraction
   - Context understanding
   - Multi-format support

2. **Rule Extraction**
   - Pattern recognition
   - Classification
   - Validation suggestions

### Configuration

1. **VS Code Integration**
   ```json
   {
     "mcp.servers": {
       "esd-analyzer": {
         "command": "python",
         "args": ["mcp_server.py"]
       }
     }
   }
   ```

2. **GitHub Copilot Integration**
   - Automatic suggestions
   - Rule completion
   - Template generation

### Usage

1. **Manual Analysis**
   - Upload document
   - Select "Analyze with MCP"
   - Review results

2. **Automatic Processing**
   - Enable in settings
   - Configure thresholds
   - Monitor results

---

## 10. API Reference

### Authentication

Currently, the API is open. Authentication will be added in future versions.

### Endpoints

#### Rules API

**Get All Rules**
```http
GET /api/rules?technology_id=1&rule_type=esd&search=protection
```

**Create Rule**
```http
POST /api/rules
Content-Type: application/json

{
  "title": "Input Protection Rule",
  "rule_type": "esd",
  "technology_id": 1,
  "content": "All inputs must have ESD protection",
  "severity": "high"
}
```

**Update Rule**
```http
PUT /api/rules/{rule_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content"
}
```

#### Templates API

**Get Templates**
```http
GET /api/templates?technology_id=1
```

**Create Template**
```http
POST /api/templates
Content-Type: application/json

{
  "name": "ESD Guideline Template",
  "template_type": "guideline",
  "template_content": "# {{ title }}",
  "technology_id": 1
}
```

#### Document Import API

**Upload Document**
```http
POST /docs/api/upload
Content-Type: multipart/form-data

file: [binary data]
```

**Get Processing Status**
```http
GET /docs/api/status/{document_id}
```

### Response Formats

**Success Response**
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed"
}
```

**Error Response**
```json
{
  "status": "error",
  "detail": "Error description",
  "code": "ERROR_CODE"
}
```

---

## 11. Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Problem**: Port already in use
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution**:
- Use alternative port: `start_server_8080.bat`
- Kill existing process
- Check for other applications using port 8000

#### 2. Database Errors

**Problem**: Database locked or corrupted
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked
```

**Solution**:
1. Stop the server
2. Backup existing database: `copy esd_guidelines.db esd_guidelines_backup.db`
3. Reinitialize: `python manage.py`

#### 3. Import Failures

**Problem**: Document import fails
```
Error: Unable to extract content from document
```

**Solutions**:
- Check file format (must be .xlsx, .pdf, or .docx)
- Ensure file is not corrupted
- Try converting to different format
- Check file permissions

#### 4. Template Rendering Errors

**Problem**: Template preview shows errors
```
Template Error: Variable 'technology_name' not found
```

**Solution**:
- Check variable names match exactly
- Ensure all variables have default values
- Validate template syntax

### Performance Optimization

1. **Large Document Processing**
   - Split into smaller files
   - Process in batches
   - Use background tasks

2. **Database Performance**
   - Regular cleanup of soft-deleted items
   - Index optimization
   - Consider PostgreSQL for production

3. **Browser Performance**
   - Clear cache regularly
   - Limit items per page
   - Use pagination effectively

### Getting Help

1. **Check Logs**
   - Server logs in console
   - Browser console (F12)
   - Database query logs

2. **Debug Mode**
   ```bash
   uvicorn app.main:app --reload --log-level debug
   ```

3. **Contact Support**
   - Create issue in project repository
   - Include error messages
   - Provide steps to reproduce

---

## Appendix

### Keyboard Shortcuts

- `Ctrl+N` - New rule (when in Rules section)
- `Ctrl+S` - Save (in editors)
- `Ctrl+/` - Search
- `Esc` - Close modals

### Data Backup

1. **Manual Backup**
   ```bash
   copy esd_guidelines.db backups\esd_guidelines_%date%.db
   ```

2. **Scheduled Backup**
   - Use Windows Task Scheduler
   - Or cron job on Linux

### Future Features

- User authentication
- Role-based access control
- Advanced analytics
- API rate limiting
- Multi-language support
- Cloud deployment options

---

*Last Updated: May 2025*
*Version: 1.0.0*
