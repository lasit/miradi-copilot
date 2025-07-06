#!/usr/bin/env python3
"""
Miradi Project Switcher

A utility for managing and switching between Miradi conservation projects in Neo4j.
This script allows you to see available projects, check what's currently loaded,
and switch to a different project.

Usage:
    python switch_project.py                    # List available projects and current status
    python switch_project.py <project_name>     # Switch to a specific project
    python switch_project.py --list             # List available projects only

Features:
    - Lists all available .xmpz2 projects in data/sample_projects/
    - Shows currently loaded project information
    - Allows switching to a different project (clear + load)
    - Clean, formatted output with project metadata
"""

import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to suppress validation warnings
logging.getLogger('src.etl.schema_mapper').setLevel(logging.CRITICAL)
logging.getLogger('src.graph.models').setLevel(logging.CRITICAL)
logging.getLogger('root').setLevel(logging.CRITICAL)

# Suppress specific loggers that print validation errors
import warnings
warnings.filterwarnings('ignore')

from src.etl.neo4j_loader import load_miradi_project


def format_time(seconds):
    """Format time duration in a human-readable way."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def format_number(num):
    """Format numbers with thousands separators."""
    return f"{num:,}"


def extract_project_name(project_path):
    """Extract a clean project name from the file path."""
    filename = project_path.stem  # Remove .xmpz2 extension
    
    # Remove version numbers (e.g., _v0.111)
    import re
    clean_name = re.sub(r'_v\d+\.\d+.*$', '', filename)
    
    # Replace underscores with spaces and title case
    clean_name = clean_name.replace('_', ' ').title()
    
    return clean_name


def get_current_project():
    """Get information about the currently loaded project."""
    try:
        from src.graph.neo4j_connection import Neo4jConnection
        
        conn = Neo4jConnection()
        conn.connect()
        
        # Query for current project metadata
        query = """
        MATCH (p:PROJECT {id: 'current_project'})
        RETURN p.name as name,
               p.filename as filename,
               p.file_path as file_path,
               p.loaded_at as loaded_at,
               p.nodes_count as nodes_count,
               p.relationships_count as relationships_count,
               p.elements_parsed as elements_parsed,
               p.schema_coverage as schema_coverage,
               p.load_time as load_time
        """
        
        result = conn.execute_query(query)
        conn.close()
        
        if result:
            return result[0]
        else:
            return None
            
    except Exception as e:
        return None


def get_available_projects(directory="data/sample_projects"):
    """Get list of available .xmpz2 project files."""
    project_dir = Path(directory)
    
    if not project_dir.exists():
        return []
    
    project_files = list(project_dir.glob("*.xmpz2"))
    project_files.sort()  # Sort for consistent ordering
    
    # Convert to project info
    projects = []
    for project_file in project_files:
        project_name = extract_project_name(project_file)
        projects.append({
            'name': project_name,
            'filename': project_file.name,
            'path': project_file
        })
    
    return projects


def show_current_project():
    """Display information about the currently loaded project."""
    current = get_current_project()
    
    print("📊 CURRENT PROJECT STATUS")
    print("=" * 60)
    
    if current:
        # Parse datetime
        loaded_at = current['loaded_at']
        if hasattr(loaded_at, 'strftime'):
            loaded_time = loaded_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            loaded_time = str(loaded_at)
        
        print(f"📁 Project: {current['name']}")
        print(f"📄 File: {current['filename']}")
        print(f"📍 Path: {current['file_path']}")
        print(f"⏰ Loaded: {loaded_time}")
        print(f"🔗 Nodes: {format_number(current['nodes_count'])}")
        print(f"🔗 Relationships: {format_number(current['relationships_count'])}")
        print(f"📈 Elements: {format_number(current['elements_parsed'])}")
        print(f"🎯 Coverage: {current['schema_coverage']:.1f}%")
        print(f"⏱️  Load Time: {format_time(current['load_time'])}")
        
        return current
    else:
        print("❌ No project currently loaded")
        print("   Use 'python switch_project.py <project_name>' to load a project")
        
        return None


def show_available_projects():
    """Display list of available projects."""
    projects = get_available_projects()
    
    print("📂 AVAILABLE PROJECTS")
    print("=" * 60)
    
    if not projects:
        print("❌ No .xmpz2 project files found in data/sample_projects/")
        return projects
    
    print(f"Found {len(projects)} available projects:")
    print()
    
    for i, project in enumerate(projects, 1):
        print(f"{i:2d}. {project['name']}")
        print(f"    📄 {project['filename']}")
        print()
    
    return projects


def switch_to_project(project_identifier):
    """
    Switch to a specific project by name or filename.
    
    Args:
        project_identifier: Project name or filename to switch to
        
    Returns:
        bool: True if successful, False otherwise
    """
    projects = get_available_projects()
    
    if not projects:
        print("❌ No projects available to switch to")
        return False
    
    # Find matching project
    target_project = None
    
    # Try exact name match first
    for project in projects:
        if project['name'].lower() == project_identifier.lower():
            target_project = project
            break
    
    # Try filename match
    if not target_project:
        for project in projects:
            if project['filename'].lower() == project_identifier.lower():
                target_project = project
                break
    
    # Try partial name match
    if not target_project:
        for project in projects:
            if project_identifier.lower() in project['name'].lower():
                target_project = project
                break
    
    if not target_project:
        print(f"❌ Project not found: {project_identifier}")
        print()
        print("Available projects:")
        for project in projects:
            print(f"   • {project['name']} ({project['filename']})")
        return False
    
    print("=" * 60)
    print("🔄 SWITCHING PROJECT")
    print("=" * 60)
    print(f"📁 Target: {target_project['name']}")
    print(f"📄 File: {target_project['filename']}")
    print()
    
    try:
        # Load the project with clearing
        print("🗑️  Clearing current project...")
        print("🔄 Loading new project...")
        
        stats = load_miradi_project(str(target_project['path']), clear_existing=True)
        
        if stats['success']:
            print()
            print("✅ PROJECT SWITCH SUCCESSFUL!")
            print("=" * 60)
            print(f"📁 New Project: {target_project['name']}")
            print(f"🔗 Nodes: {format_number(stats['loading']['nodes']['total_nodes'])}")
            print(f"🔗 Relationships: {format_number(stats['loading']['relationships']['total_relationships'])}")
            print(f"⏱️  Switch Time: {format_time(stats['pipeline_time'])}")
            print()
            print("🎉 You can now query the new project data!")
            print("=" * 60)
            
            return True
        else:
            error_msg = stats.get('error', 'Unknown error')
            print()
            print("❌ PROJECT SWITCH FAILED")
            print("=" * 60)
            print(f"Error: {error_msg}")
            print("=" * 60)
            
            return False
            
    except Exception as e:
        print()
        print("❌ UNEXPECTED ERROR DURING SWITCH")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("=" * 60)
        
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Manage and switch between Miradi conservation projects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python switch_project.py                    # Show current status and available projects
    python switch_project.py "Bulgul Rangers"   # Switch to Bulgul Rangers project
    python switch_project.py --list             # List available projects only

Project Matching:
    • Exact name match: "Bulgul Rangers"
    • Filename match: "Bulgul_Rangers_v0.111.xmpz2"
    • Partial name match: "bulgul" or "rangers"

Requirements:
    • Neo4j database running (test with: python test_neo4j_connection.py)
    • Valid .env file with Neo4j credentials
    • Miradi project files in data/sample_projects/ directory
        """
    )
    
    parser.add_argument(
        'project',
        nargs='?',
        help='Project name or filename to switch to (optional)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available projects only'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌿 MIRADI PROJECT SWITCHER")
    print("=" * 60)
    print()
    
    # Handle different modes
    if args.list:
        # List mode - show available projects only
        show_available_projects()
        
    elif args.project:
        # Switch mode - switch to specified project
        success = switch_to_project(args.project)
        sys.exit(0 if success else 1)
        
    else:
        # Status mode - show current project and available projects
        current = show_current_project()
        print()
        show_available_projects()
        
        if current:
            print("💡 To switch projects:")
            print("   python switch_project.py <project_name>")
        else:
            print("💡 To load a project:")
            print("   python switch_project.py <project_name>")
        print("=" * 60)


if __name__ == "__main__":
    main()
