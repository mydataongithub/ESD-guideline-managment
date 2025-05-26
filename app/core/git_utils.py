# app/core/git_utils.py
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import os

# Try to import git, but handle gracefully if not available
try:
    import git
    # Try to configure Git executable path for Windows
    try:
        # Test if git command works
        git.Repo.init('test_temp_repo', bare=True)
        import shutil
        shutil.rmtree('test_temp_repo')
        GIT_AVAILABLE = True
        print("Git successfully detected and configured")
    except Exception as git_error:
        # Try to find git executable manually
        import subprocess
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, check=True)
            if 'git version' in result.stdout:
                # Git command works, configure GitPython
                git.refresh()
                GIT_AVAILABLE = True
                print(f"Git detected: {result.stdout.strip()}")
            else:
                raise Exception("Git command not working")
        except Exception:
            try:
                # Try common Git installation paths on Windows
                import os
                possible_paths = [
                    r'C:\Program Files\Git\bin\git.exe',
                    r'C:\Program Files (x86)\Git\bin\git.exe',
                    r'C:\Git\bin\git.exe'
                ]
                
                git_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        git_path = path
                        break
                
                if git_path:
                    os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = git_path
                    git.refresh(git_path)
                    GIT_AVAILABLE = True
                    print(f"Git configured at: {git_path}")
                else:
                    raise Exception("Git executable not found")
            except Exception as final_error:
                GIT_AVAILABLE = False
                print(f"Warning: Git not available ({final_error}). Version control features will be disabled.")
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: GitPython not available. Version control features will be disabled.")

GUIDELINES_REPO_PATH = Path(__file__).parent.parent.parent / "guidelines_repo"

def get_repo():
    """Get or initialize Git repository."""
    if not GIT_AVAILABLE:
        return None
    
    try:
        if not (GUIDELINES_REPO_PATH / ".git").exists():
            GUIDELINES_REPO_PATH.mkdir(parents=True, exist_ok=True)
            repo = git.Repo.init(GUIDELINES_REPO_PATH)
            print(f"Initialized Git repository at {GUIDELINES_REPO_PATH}")
            
            # Create an initial commit if the repo is brand new and empty
            readme_path = GUIDELINES_REPO_PATH / "README.md"
            if not readme_path.exists():
                with open(readme_path, "w", encoding='utf-8') as f:
                    f.write("# ESD and Latch-up Guidelines\n\nThis repository stores automatically generated guidelines.")
                repo.index.add([str(readme_path)])
                repo.index.commit("Initial commit: Add README for guidelines repository")
            return repo
        return git.Repo(GUIDELINES_REPO_PATH)
    except Exception as e:
        print(f"Warning: Could not initialize Git repository: {e}")
        return None

def commit_guideline(file_path: Path, technology_name: str, message: str = "") -> bool:
    """Commit guideline changes to Git repository."""
    if not GIT_AVAILABLE:
        print("Git not available - skipping version control")
        return False
    
    try:
        repo = get_repo()
        repo_file_path = file_path.relative_to(GUIDELINES_REPO_PATH)
        
        if not message:
            message = f"Update guidelines for {technology_name}"
        
        # Add file to staging
        repo.index.add([str(repo_file_path)])
        
        # Check if there are changes to commit
        if repo.is_dirty(path=str(repo_file_path)) or str(repo_file_path) in repo.untracked_files:
            repo.index.commit(message)
            print(f"Committed: {repo_file_path} with message: '{message}'")
            return True
        else:
            print(f"No changes to commit for {repo_file_path}")
            return False
            
    except Exception as e:
        print(f"Error during git operation: {e}")
        if "nothing to commit" in str(e).lower():
            print("No textual changes to commit.")
            return False
        else:
            raise

def get_guideline_versions(technology_name: str, max_count: int = 10) -> List[Dict[str, Any]]:
    """Get commit history for a specific guideline."""
    if not GIT_AVAILABLE:
        return []
    
    try:
        repo = get_repo()
        file_path_in_repo = f"{technology_name}/esd_latchup_guidelines.md"
        commits = list(repo.iter_commits(paths=file_path_in_repo, max_count=max_count))
        
        return [
            {
                "sha": c.hexsha,
                "message": c.message.strip(),
                "date": datetime.fromtimestamp(c.committed_date),
                "author": c.author.name
            }
            for c in commits
        ]
    except Exception:
        return []

def get_guideline_content_by_commit(technology_name: str, commit_sha: str) -> str:
    """Get guideline content from a specific commit."""
    if not GIT_AVAILABLE:
        raise ValueError("Git not available - cannot retrieve historical versions")
    
    repo = get_repo()
    if repo is None:
        raise ValueError("Git repository not available")
    file_path_in_repo = f"{technology_name}/esd_latchup_guidelines.md"
    
    try:
        commit = repo.commit(commit_sha)
        blob = commit.tree / file_path_in_repo
        return blob.data_stream.read().decode('utf-8')
    except Exception as e:
        raise ValueError(f"Could not retrieve content for commit {commit_sha}: {str(e)}")

def get_repository_status() -> Dict[str, Any]:
    """Get current repository status."""
    if not GIT_AVAILABLE:
        return {
            "git_available": False,
            "message": "Git is not installed or not available",
            "is_dirty": False,
            "untracked_files": [],
            "active_branch": "N/A"
        }
    
    try:
        repo = get_repo()
        if repo is None:
            return {
                "git_available": False,
                "message": "Git repository could not be initialized",
                "is_dirty": False,
                "untracked_files": [],
                "active_branch": "N/A"
            }
        
        return {
            "git_available": True,
            "is_dirty": repo.is_dirty(),
            "untracked_files": repo.untracked_files,
            "active_branch": repo.active_branch.name,
            "latest_commit": {
                "sha": repo.head.commit.hexsha[:7],
                "message": repo.head.commit.message.strip(),
                "date": datetime.fromtimestamp(repo.head.commit.committed_date)
            }
        }
    except Exception as e:
        return {
            "git_available": False,
            "error": str(e),
            "is_dirty": False,
            "untracked_files": [],
            "active_branch": "N/A"
        }
