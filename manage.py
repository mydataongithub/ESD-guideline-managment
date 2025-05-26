#!/usr/bin/env python3
"""
Utility script for managing the ESD & Latch-up Guideline Generator system.
"""

import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core import generator, git_utils
except ImportError as e:
    print(f"Error: Could not import application modules: {e}")
    sys.exit(1)

def list_technologies():
    """List all available technologies."""
    print("Available Technologies:")
    print("=" * 40)
    
    technologies = generator.get_available_technologies()
    
    if not technologies:
        print("No technologies found.")
        print("Add configuration files to the config/ directory.")
        return
    
    for tech in technologies:
        try:
            config = generator.load_tech_params(tech)
            process_type = config.get('process_type', 'Unknown')
            esd_hbm = config.get('esd_levels', {}).get('hbm', 'Unknown')
            
            print(f"• {tech}")
            print(f"  Process: {process_type}")
            print(f"  HBM Level: {esd_hbm}")
            print(f"  Config: config/{tech}.json")
            print()
        except Exception as e:
            print(f"• {tech} (Error loading: {e})")
            print()

def generate_all_guidelines():
    """Generate guidelines for all technologies."""
    print("Generating Guidelines for All Technologies")
    print("=" * 50)
    
    technologies = generator.get_available_technologies()
    
    if not technologies:
        print("No technologies found.")
        return
    
    success_count = 0
    error_count = 0
    
    for tech in technologies:
        try:
            print(f"\nGenerating guidelines for {tech}...")
            
            # Generate content
            markdown_content = generator.generate_guideline_markdown(tech)
            
            # Save to file
            saved_path = generator.save_guideline(tech, markdown_content)
            
            # Commit to Git
            try:
                commit_success = git_utils.commit_guideline(
                    saved_path, 
                    tech, 
                    f"Batch update guidelines for {tech}"
                )
                if commit_success:
                    print(f"✅ Generated and committed guidelines for {tech}")
                else:
                    print(f"✅ Generated guidelines for {tech} (no Git changes)")
            except Exception as git_error:
                print(f"✅ Generated guidelines for {tech} (Git error: {git_error})")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to generate guidelines for {tech}: {e}")
            error_count += 1
    
    print(f"\n📊 Summary: {success_count} successful, {error_count} errors")

def validate_configurations():
    """Validate all technology configurations."""
    print("Validating Technology Configurations")
    print("=" * 40)
    
    config_path = Path("config")
    config_files = list(config_path.glob("*.json"))
    
    if not config_files:
        print("No configuration files found.")
        return
    
    valid_count = 0
    error_count = 0
    
    required_fields = ['esd_levels', 'latch_up_rules', 'approved_clamps']
    
    for config_file in config_files:
        tech_name = config_file.stem
        
        if tech_name == "master_template":
            continue
        
        print(f"\nValidating {tech_name}...")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check required fields
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                print(f"❌ Missing required fields: {', '.join(missing_fields)}")
                error_count += 1
                continue
            
            # Validate ESD levels
            esd_levels = config['esd_levels']
            if 'hbm' not in esd_levels or 'cdm' not in esd_levels:
                print("❌ ESD levels missing HBM or CDM specification")
                error_count += 1
                continue
            
            # Validate approved clamps
            clamps = config['approved_clamps']
            if not isinstance(clamps, list) or len(clamps) == 0:
                print("❌ No approved clamps specified")
                error_count += 1
                continue
            
            # Check clamp structure
            for i, clamp in enumerate(clamps):
                required_clamp_fields = ['name', 'type', 'rating']
                missing_clamp_fields = [field for field in required_clamp_fields if field not in clamp]
                if missing_clamp_fields:
                    print(f"❌ Clamp {i}: Missing fields {', '.join(missing_clamp_fields)}")
                    error_count += 1
                    break
            else:
                print(f"✅ Configuration valid ({len(clamps)} clamps defined)")
                valid_count += 1
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON syntax error: {e}")
            error_count += 1
        except Exception as e:
            print(f"❌ Validation error: {e}")
            error_count += 1
    
    print(f"\n📊 Summary: {valid_count} valid, {error_count} errors")

def backup_system():
    """Create a backup of the entire system."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"esd_guidelines_backup_{timestamp}"
    backup_path = Path.cwd().parent / backup_name
    
    print(f"Creating system backup: {backup_path}")
    
    try:
        # Copy entire project directory
        shutil.copytree(Path.cwd(), backup_path, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.git', 'venv', 'env'
        ))
        
        print(f"✅ Backup created successfully at {backup_path}")
        
        # Create backup info file
        info_file = backup_path / "backup_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"ESD Guidelines System Backup\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {Path.cwd()}\n")
            f.write(f"Technologies: {', '.join(generator.get_available_technologies())}\n")
        
        print(f"✅ Backup info written to {info_file}")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def clean_system():
    """Clean generated files and temporary data."""
    print("Cleaning System")
    print("=" * 20)
    
    # Clean generated guidelines
    guidelines_path = Path("guidelines_repo")
    if guidelines_path.exists():
        for tech_dir in guidelines_path.iterdir():
            if tech_dir.is_dir() and tech_dir.name != ".git":
                guideline_file = tech_dir / "esd_latchup_guidelines.md"
                if guideline_file.exists():
                    guideline_file.unlink()
                    print(f"🗑️  Removed {guideline_file}")
                
                # Remove empty directories
                try:
                    tech_dir.rmdir()
                    print(f"🗑️  Removed directory {tech_dir}")
                except OSError:
                    pass  # Directory not empty
    
    # Clean Python cache
    for cache_dir in Path.cwd().rglob("__pycache__"):
        shutil.rmtree(cache_dir)
        print(f"🗑️  Removed {cache_dir}")
    
    print("✅ System cleaned")

def show_status():
    """Show system status and statistics."""
    print("System Status")
    print("=" * 20)
    
    # Technology count
    technologies = generator.get_available_technologies()
    print(f"Technologies configured: {len(technologies)}")
    
    # Generated guidelines count
    guidelines_path = Path("guidelines_repo")
    generated_count = 0
    if guidelines_path.exists():
        for tech_dir in guidelines_path.iterdir():
            if tech_dir.is_dir() and (tech_dir / "esd_latchup_guidelines.md").exists():
                generated_count += 1
    
    print(f"Guidelines generated: {generated_count}")
    
    # Git status
    try:
        git_status = git_utils.get_repository_status()
        if 'error' not in git_status:
            print(f"Git repository: Active")
            print(f"Latest commit: {git_status.get('latest_commit', {}).get('sha', 'Unknown')}")
            print(f"Uncommitted changes: {'Yes' if git_status.get('is_dirty') else 'No'}")
        else:
            print("Git repository: Not available")
    except Exception:
        print("Git repository: Error accessing")
    
    # Configuration status
    config_path = Path("config")
    config_files = len(list(config_path.glob("*.json")))
    print(f"Configuration files: {config_files}")
    
    # Template status
    template_path = config_path / "master_template.md"
    print(f"Master template: {'Available' if template_path.exists() else 'Missing'}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ESD & Latch-up Guideline Generator - System Utilities"
    )
    
    parser.add_argument(
        'command',
        choices=['list', 'generate', 'validate', 'backup', 'clean', 'status'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    commands = {
        'list': list_technologies,
        'generate': generate_all_guidelines,
        'validate': validate_configurations,
        'backup': backup_system,
        'clean': clean_system,
        'status': show_status
    }
    
    print(f"ESD & Latch-up Guideline Generator - {args.command.title()}")
    print("=" * 60)
    
    try:
        commands[args.command]()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
