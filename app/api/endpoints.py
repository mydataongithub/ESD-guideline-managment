# app/api/endpoints.py
from fastapi import APIRouter, HTTPException, Request, Path as FastAPIPath, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path as PythonPath
from typing import List
from sqlalchemy.orm import Session

from app.core import generator, git_utils, db_generator
from app.database.database import get_db
from app.models import schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

CONFIG_PATH = PythonPath(__file__).parent.parent.parent / "config"
GUIDELINES_REPO_PATH = PythonPath(__file__).parent.parent.parent / "guidelines_repo"

@router.get("/technologies", response_model=List[str])
async def list_technologies(db: Session = Depends(get_db)):
    """Lists available technologies from database."""
    try:
        return db_generator.get_available_technologies_from_db(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading technologies: {str(e)}")

@router.get("/generate/{technology_name}", response_class=HTMLResponse)
async def generate_guideline_page(request: Request, technology_name: str):
    """Show guideline generation page for a technology."""
    return templates.TemplateResponse("generate_guideline.html", {
        "request": request,
        "technology_name": technology_name
    })

@router.post("/generate/{technology_name}", response_model=schemas.GuidelineResponse)
async def generate_and_commit_guideline(
    technology_name: str = FastAPIPath(..., description="The name of the technology"),
    db: Session = Depends(get_db)
):
    """Generates, saves, and commits guidelines for a specific technology."""
    try:
        # Validate technology exists in database
        if not db_generator.validate_technology_in_db(technology_name, db):
            raise HTTPException(
                status_code=400, 
                detail=f"Technology '{technology_name}' not found or has no rules defined"
            )
        
        # Generate guideline content from database
        markdown_content = db_generator.generate_guideline_from_db(technology_name, db)
        
        # Save to file system
        saved_file_path = db_generator.save_guideline(technology_name, markdown_content)
        
        # Commit to Git
        commit_success = git_utils.commit_guideline(saved_file_path, technology_name)
        
        return schemas.GuidelineResponse(
            technology=technology_name,
            message=f"Guidelines {'generated and committed' if commit_success else 'generated (no changes to commit)'} for {technology_name}.",
            file_path=str(saved_file_path.relative_to(GUIDELINES_REPO_PATH)),
            content=markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/view/{technology_name}/latest", response_class=HTMLResponse)
async def view_latest_guideline(request: Request, technology_name: str):
    """Displays the latest version of the guideline for a technology."""
    file_path = GUIDELINES_REPO_PATH / technology_name / "esd_latchup_guidelines.md"
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Guideline not found for this technology. Try generating it first."
        )
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert Markdown to HTML
        try:
            import markdown2
            html_content = markdown2.markdown(
                markdown_content, 
                extras=["tables", "fenced-code-blocks", "header-ids"]
            )
        except ImportError:
            # Fallback to pre-formatted text if markdown2 is not installed
            html_content = f"<pre>{markdown_content}</pre>"

        return templates.TemplateResponse("view_guideline.html", {
            "request": request,
            "technology_name": technology_name,
            "guideline_html": html_content,
            "guideline_markdown": markdown_content,
            "versions": None
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading guideline: {str(e)}")

@router.get("/view/{technology_name}/history", response_class=HTMLResponse)
async def view_guideline_history(request: Request, technology_name: str):
    """Displays the commit history for a specific guideline."""
    try:
        versions = git_utils.get_guideline_versions(technology_name)
        
        # Get current content
        file_path = GUIDELINES_REPO_PATH / technology_name / "esd_latchup_guidelines.md"
        current_content = ""
        current_html = ""
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            try:
                import markdown2
                current_html = markdown2.markdown(
                    current_content, 
                    extras=["tables", "fenced-code-blocks", "header-ids"]
                )
            except ImportError:
                current_html = f"<pre>{current_content}</pre>"

        return templates.TemplateResponse("view_guideline_history.html", {
            "request": request,
            "technology_name": technology_name,
            "versions": versions,
            "current_guideline_html": current_html
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve history: {str(e)}")

@router.get("/view/{technology_name}/version/{commit_sha}", response_class=HTMLResponse)
async def view_specific_version_guideline(request: Request, technology_name: str, commit_sha: str):
    """Displays a specific version of the guideline."""
    try:
        markdown_content = git_utils.get_guideline_content_by_commit(technology_name, commit_sha)
        
        try:
            import markdown2
            html_content = markdown2.markdown(
                markdown_content, 
                extras=["tables", "fenced-code-blocks", "header-ids"]
            )
        except ImportError:
            html_content = f"<pre>{markdown_content}</pre>"

        return templates.TemplateResponse("view_guideline.html", {
            "request": request,
            "technology_name": f"{technology_name} (Version: {commit_sha[:7]})",
            "guideline_html": html_content,
            "guideline_markdown": markdown_content,
            "versions": None
        })
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve version: {str(e)}")

@router.get("/download/{technology_name}/latest", response_class=PlainTextResponse)
async def download_latest_guideline(technology_name: str):
    """Download the latest guideline as Markdown file."""
    file_path = GUIDELINES_REPO_PATH / technology_name / "esd_latchup_guidelines.md"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Guideline not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return PlainTextResponse(
            content=content,
            headers={"Content-Disposition": f"attachment; filename=esd_latchup_guidelines_{technology_name}.md"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@router.get("/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status including Git repository information."""
    try:
        repo_status = git_utils.get_repository_status()
        technologies = db_generator.get_available_technologies_from_db(db)
        
        return {
            "repository": repo_status,
            "available_technologies": technologies,
            "system": "operational"
        }
    except Exception as e:
        return {
            "system": "error",
            "error": str(e)
        }
