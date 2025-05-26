# ESD & Latch-up Guideline Generator

A comprehensive automated system for generating, managing, and version-controlling ESD (Electrostatic Discharge) and latch-up guidelines for semiconductor technologies.

## Features

- **Automated Guideline Generation**: Template-based Markdown document generation
- **Version Control**: Git-based versioning of all generated documents
- **Web Interface**: User-friendly web application for management and viewing
- **Multi-Technology Support**: Configure multiple technology nodes
- **Document History**: View and compare different versions of guidelines
- **RESTful API**: Programmatic access to all functionality

## Architecture

```
workflow3/
├── app/                    # Main application code
│   ├── api/               # FastAPI endpoints
│   ├── core/              # Core business logic
│   ├── models/            # Pydantic data models
│   ├── static/            # CSS, JavaScript files
│   ├── templates/         # HTML templates
│   └── main.py            # FastAPI application entry point
├── config/                # Configuration files
│   ├── master_template.md # Jinja2 template for guidelines
│   ├── technology_A.json  # Technology-specific parameters
│   └── technology_B.json  # Additional technology config
├── guidelines_repo/       # Git repository for generated documents
└── requirements.txt       # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (optional - for version control functionality)

**Note:** Git is optional! The system works perfectly without it, but you'll miss version control features like document history and change tracking.

### Setup

1. **Clone or download the project to your desired location**

2. **Create a virtual environment (recommended):**
   ```bash
   cd workflow3
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies using uv (recommended for faster installation):**
   ```bash
   # Install uv package manager
   pip install uv
   
   # Install project dependencies
   uv pip install -r requirements.txt
   ```
   
   **Alternative (using standard pip):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the guidelines repository (optional, only if Git is installed):**
   ```bash
   cd guidelines_repo
   git init
   echo "# ESD and Latch-up Guidelines Repository" > README.md
   git add README.md
   git commit -m "Initial commit"
   cd ..
   ```

   **If Git is not installed:** Skip this step. The system will work normally without version control.

## Usage

### Starting the Application

1. **Run the FastAPI server:**
   ```bash
   # From the workflow3 directory
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the web interface:**
   Open your browser and navigate to: `http://localhost:8000`

### Web Interface

The web interface provides:

- **Technology Selection**: Choose from configured technologies
- **Guideline Generation**: Generate or update guidelines with one click
- **Document Viewing**: View rendered guidelines with full formatting
- **Version History**: Browse through all document versions
- **Download Options**: Download guidelines as Markdown files

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/technologies` | GET | List available technologies |
| `/generate/{technology_name}` | POST | Generate guidelines for a technology |
| `/view/{technology_name}/latest` | GET | View latest guideline (HTML) |
| `/view/{technology_name}/history` | GET | View version history (HTML) |
| `/view/{technology_name}/version/{commit_sha}` | GET | View specific version (HTML) |
| `/download/{technology_name}/latest` | GET | Download latest guideline (Markdown) |
| `/status` | GET | Get system status |

### Configuration

#### Adding New Technologies

1. **Create a JSON configuration file** in the `config/` directory:
   ```json
   {
     "process_type": "Your Process Node",
     "esd_levels": {
       "hbm": "2kV",
       "cdm": "500V"
     },
     "latch_up_rules": {
       "rule1": "Your specific rule",
       "nwell_psub_spacing_io": "5μm"
     },
     "approved_clamps": [
       {
         "name": "Clamp_Name",
         "type": "Primary",
         "rating": "2kV HBM",
         "application": "Standard I/O"
       }
     ]
   }
   ```

2. **Save the file** as `config/your_technology_name.json`

3. **Restart the server** to load the new configuration

#### Customizing the Template

Edit `config/master_template.md` to modify the generated document structure. The template uses Jinja2 syntax:

- `{{ variable_name }}` - Insert variable value
- `{% if condition %}...{% endif %}` - Conditional content
- `{% for item in list %}...{% endfor %}` - Loop through lists

## Configuration Examples

### Sample Technology Configuration

```json
{
  "process_type": "28nm CMOS",
  "esd_levels": {
    "hbm": "2kV",
    "cdm": "500V",
    "mm": "200V"
  },
  "latch_up_rules": {
    "rule1": "All I/O cells must use guard rings.",
    "nwell_psub_spacing_io": "8μm",
    "guard_ring_width": "5.0μm"
  },
  "approved_clamps": [
    {
      "name": "Standard_IO_Clamp",
      "type": "Primary",
      "rating": "2kV HBM",
      "application": "Digital I/O"
    }
  ],
  "advanced_protection_scheme": true,
  "advanced_protection_scheme_details": "Multi-stage protection with RC triggers"
}
```

## Development

### Project Structure

- **`app/main.py`**: FastAPI application initialization
- **`app/core/generator.py`**: Template processing and document generation
- **`app/core/git_utils.py`**: Git operations for version control
- **`app/api/endpoints.py`**: HTTP API endpoint definitions
- **`app/models/schemas.py`**: Pydantic models for data validation
- **`app/templates/`**: HTML templates for web interface
- **`app/static/`**: CSS and JavaScript for frontend

### Adding New Features

1. **Backend Logic**: Add new functions to appropriate modules in `app/core/`
2. **API Endpoints**: Add new routes in `app/api/endpoints.py`
3. **Data Models**: Define new Pydantic models in `app/models/schemas.py`
4. **Frontend**: Update HTML templates and JavaScript as needed

### Testing

Run tests using pytest:
```bash
pytest
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Use a different port
   uvicorn app.main:app --port 8001
   ```

2. **Git Not Available Error**:
   - **Symptom**: "Bad git executable" or "Git not found" errors
   - **Solution**: Install Git from https://git-scm.com/downloads
   - **Alternative**: System works without Git (version control disabled)
   - **Helper**: Run `install_git.bat` for automatic download

3. **Git Repository Issues**:
   ```bash
   # Reinitialize the guidelines repository (if Git is installed)
   cd guidelines_repo
   rm -rf .git
   git init
   ```

4. **Template Errors**:
   - Check JSON syntax in configuration files
   - Verify all required variables are defined
   - Check Jinja2 template syntax in `master_template.md`

5. **Dependency Issues**:
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r requirements.txt
   ```

### Debug Mode

Enable debug mode for detailed error messages:
```bash
uvicorn app.main:app --reload --log-level debug
```

## Integration Points

### MCP Integration

The system is designed to integrate with external systems through:

1. **API Endpoints**: RESTful APIs for external system integration
2. **Git Hooks**: Post-commit hooks for downstream system notifications
3. **Configuration Sources**: External configuration management systems
4. **Document Export**: Multiple export formats for downstream consumption

### Webhook Support

Add webhook notifications by extending `app/core/git_utils.py`:

```python
def commit_guideline(file_path, technology_name, message=""):
    # ... existing commit logic ...
    
    # Add webhook notification
    notify_external_system(technology_name, commit_sha)
```

## License

This project is proprietary software. Please refer to your organization's licensing terms.

## Support

For questions, issues, or feature requests:

1. Check the troubleshooting section above
2. Review the generated log files
3. Consult your system administrator
4. Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Web interface for guideline generation
- Git-based version control
- Multi-technology support
- RESTful API
- Comprehensive template system

---

**Generated on**: $(date)  
**System Version**: 1.0.0  
**Python Version**: $(python --version)