# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import endpoints, document_endpoints, validation_endpoints, template_endpoints, rule_endpoints, technology_endpoints
from app.api.fixed_rule_endpoints import fixed_api_router

app = FastAPI(title="ESD & Latch-up Guideline Generator")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(endpoints.router)
app.include_router(document_endpoints.router)
app.include_router(validation_endpoints.router)
app.include_router(template_endpoints.router)
app.include_router(template_endpoints.api_router)
app.include_router(rule_endpoints.router)
app.include_router(rule_endpoints.api_router)
app.include_router(fixed_api_router)  # Include our fixed rule endpoints
app.include_router(technology_endpoints.router)

@app.get("/", include_in_schema=False)
async def read_root(request: Request):
    """Redirect to dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard", include_in_schema=False)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Add document import route alias for backward compatibility
@app.get("/docs/import", include_in_schema=False)
async def document_import_redirect(request: Request):
    """Redirect to document upload page."""
    return templates.TemplateResponse(
        "document_upload.html", 
        {"request": request, "title": "Upload Documents"}
    )

# Add validation route
@app.get("/validation", include_in_schema=False)
async def validation_dashboard(request: Request):
    """Validation dashboard page."""
    return templates.TemplateResponse(
        "validation_dashboard.html", 
        {"request": request}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
