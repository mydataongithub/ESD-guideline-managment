# ESD & Latchup Guidelines Generator - Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- uv (Python package installer) - Install with: `pip install uv`
- Git (optional, for version control)
- Web browser (Chrome, Firefox, Edge, or Safari)

## Installation

1. **Clone or Download the Project**
   ```bash
   cd C:\Users\weidner\Desktop\workflow3
   ```

2. **Create Virtual Environment (if not already created)**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   # If uv is not installed yet:
   pip install uv
   
   # Install project dependencies:
   uv pip install -r requirements.txt
   ```

5. **Initialize Database**
   ```bash
   python manage.py
   ```

## Starting the Application

### Windows Users
Double-click `start_server.bat` or run:
```bash
start_server.bat
```

### Linux/Mac Users
```bash
chmod +x start_server.sh
./start_server.sh
```

### Manual Start
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## First Steps

1. **Access the Application**
   Open your browser and navigate to: `http://localhost:8000`

2. **Navigate to Dashboard**
   Click on "Dashboard" or go to: `http://localhost:8000/dashboard`

3. **Key Features to Explore:**

   ### a) Import Documents
   - Click "Import Documents" in the navigation
   - Upload Excel, PDF, or Word documents containing ESD/Latchup rules
   - The system will automatically extract rules and queue them for validation

   ### b) Validate Rules
   - Go to "Validation Queue" to review extracted rules
   - Approve or reject rules with expert feedback
   - Approved rules are automatically added to the database

   ### c) Manage Templates
   - Click "Templates" to create document templates
   - Use templates for generating consistent guideline documents
   - Preview templates with live data

   ### d) Browse Rules
   - Click "Rules" to view all ESD and Latchup rules
   - Filter by technology, type, or search by keywords
   - Create, edit, or delete rules as needed

## Common Workflows

### 1. Import and Validate New Rules
```
Import Documents → Upload File → View in Validation Queue → Review & Approve → Rules Added
```

### 2. Create a New Rule Manually
```
Rules → Create New Rule → Fill Form → Add Images → Save
```

### 3. Generate Guidelines Document
```
Templates → Select Template → Preview with Data → Export
```

## Troubleshooting

- **Port Already in Use**: Change port in start_server.bat to 8080 or another available port
- **Database Errors**: Run `python manage.py` to reinitialize the database
- **Import Errors**: Ensure documents are in supported formats (Excel, PDF, Word)

## Need Help?

- Check the detailed user documentation: [USER_GUIDE.md](USER_GUIDE.md)
- Review implementation details: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- Check task status: [TASK.md](TASK.md)
