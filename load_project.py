#!/usr/bin/env python3
"""
Miradi Project Loader

A clean interface for loading individual Miradi conservation projects into Neo4j.
This script provides formatted output and suppresses technical validation warnings
for a better user experience.

Usage:
    python load_project.py <project_file.xmpz2>
    python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2

Features:
    - Clean, formatted output
    - Automatic environment loading
    - Progress indicators
    - Error handling with helpful messages
    - Suppressed validation warnings for cleaner output
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

# Redirect stderr temporarily to suppress validation errors
import os
import sys
from contextlib import redirect_stderr
from io import StringIO

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


def clear_database():
    """Clear the Neo4j database before loading."""
    print("🗑️  Clearing Neo4j database...")
    
    try:
        from src.graph.neo4j_connection import Neo4jConnection
        
        conn = Neo4jConnection()
        conn.connect()
        
        # Delete all relationships
        rel_result = conn.execute_write_query(
            "MATCH ()-[r]-() DELETE r RETURN count(r) as deleted"
        )
        deleted_rels = rel_result[0].get('deleted', 0) if rel_result else 0
        
        # Delete all nodes
        node_result = conn.execute_write_query(
            "MATCH (n) DELETE n RETURN count(n) as deleted"
        )
        deleted_nodes = node_result[0].get('deleted', 0) if node_result else 0
        
        conn.close()
        
        print(f"   ✅ Cleared {format_number(deleted_nodes)} nodes and {format_number(deleted_rels)} relationships")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to clear database: {e}")
        return False


def extract_project_name(project_path):
    """Extract a clean project name from the file path."""
    filename = project_path.stem  # Remove .xmpz2 extension
    
    # Remove version numbers (e.g., _v0.111)
    import re
    clean_name = re.sub(r'_v\d+\.\d+.*$', '', filename)
    
    # Replace underscores with spaces and title case
    clean_name = clean_name.replace('_', ' ').title()
    
    return clean_name


def store_project_metadata(project_path, stats):
    """Store project metadata in a PROJECT node."""
    try:
        from src.graph.neo4j_connection import Neo4jConnection
        
        conn = Neo4jConnection()
        conn.connect()
        
        project_name = extract_project_name(project_path)
        
        # Create or update PROJECT node
        query = """
        MERGE (p:PROJECT {id: 'current_project'})
        SET p.name = $name,
            p.filename = $filename,
            p.file_path = $file_path,
            p.loaded_at = datetime(),
            p.nodes_count = $nodes_count,
            p.relationships_count = $relationships_count,
            p.elements_parsed = $elements_parsed,
            p.schema_coverage = $schema_coverage,
            p.load_time = $load_time
        RETURN p.name as project_name
        """
        
        result = conn.execute_write_query(query, parameters={
            'name': project_name,
            'filename': project_path.name,
            'file_path': str(project_path),
            'nodes_count': stats['loading']['nodes']['total_nodes'],
            'relationships_count': stats['loading']['relationships']['total_relationships'],
            'elements_parsed': stats['parsing']['total_elements'],
            'schema_coverage': stats['parsing']['coverage']['known_element_coverage'],
            'load_time': stats['pipeline_time']
        })
        
        conn.close()
        
        if result:
            print(f"   📝 Stored project metadata: {result[0]['project_name']}")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Warning: Could not store project metadata: {e}")
        return False


def load_project(project_file, clear_db=False):
    """
    Load a single Miradi project with clean output.
    
    Args:
        project_file: Path to the .xmpz2 project file
        clear_db: Whether to clear the database before loading
        
    Returns:
        bool: True if successful, False otherwise
    """
    project_path = Path(project_file)
    
    # Validate file exists
    if not project_path.exists():
        print(f"❌ Error: Project file not found: {project_file}")
        return False
    
    if not project_path.suffix.lower() == '.xmpz2':
        print(f"❌ Error: File must be a .xmpz2 Miradi project file")
        return False
    
    project_name = extract_project_name(project_path)
    
    print("=" * 60)
    print("🌿 MIRADI PROJECT LOADER")
    print("=" * 60)
    print(f"📁 Project: {project_name}")
    print(f"📄 File: {project_path.name}")
    print(f"📍 Path: {project_path}")
    print()
    
    # Clear database if requested
    if clear_db:
        if not clear_database():
            print("❌ Failed to clear database. Aborting.")
            return False
        print()
    
    try:
        print("🔄 Loading project...")
        print("   • Parsing Miradi XML...")
        print("   • Converting to graph format...")
        print("   • Creating database constraints...")
        print("   • Loading nodes and relationships...")
        
        # Load the project with clear_existing=True to handle any conflicts
        stats = load_miradi_project(str(project_file), clear_existing=clear_db)
        
        if stats['success']:
            # Extract statistics
            nodes_count = stats['loading']['nodes']['total_nodes']
            relationships_count = stats['loading']['relationships']['total_relationships']
            total_time = stats['pipeline_time']
            elements_parsed = stats['parsing']['total_elements']
            coverage = stats['parsing']['coverage']['known_element_coverage']
            
            print()
            print("✅ SUCCESS!")
            print("=" * 60)
            print("📊 LOADING STATISTICS")
            print("=" * 60)
            print(f"📈 Elements Parsed: {format_number(elements_parsed)}")
            print(f"🎯 Schema Coverage: {coverage:.1f}%")
            print(f"🔗 Nodes Created: {format_number(nodes_count)}")
            print(f"🔗 Relationships Created: {format_number(relationships_count)}")
            print(f"⏱️  Total Time: {format_time(total_time)}")
            
            # Show relationship breakdown if available
            rel_counts = stats['conversion']['relationship_counts']
            if rel_counts:
                print()
                print("🔗 RELATIONSHIP BREAKDOWN:")
                for rel_type, count in sorted(rel_counts.items()):
                    if count > 0:
                        print(f"   • {rel_type}: {format_number(count)}")
            
            # Store project metadata
            store_project_metadata(project_path, stats)
            
            print()
            print("🎉 Project successfully loaded into Neo4j!")
            print("   You can now query the conservation data using Cypher or GraphRAG.")
            print("=" * 60)
            
            return True
            
        else:
            error_msg = stats.get('error', 'Unknown error occurred')
            print()
            print("❌ LOADING FAILED")
            print("=" * 60)
            print(f"Error: {error_msg}")
            print()
            print("💡 Troubleshooting:")
            print("   • Check that Neo4j is running")
            print("   • Verify database credentials in .env file")
            print("   • Ensure project file is not corrupted")
            print("   • Try: python test_neo4j_connection.py")
            print("=" * 60)
            
            return False
            
    except Exception as e:
        print()
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("   • Check that Neo4j is running: python test_neo4j_connection.py")
        print("   • Verify environment setup: python test_neo4j_setup.py")
        print("   • Check project file integrity")
        print("=" * 60)
        
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Load a Miradi conservation project into Neo4j',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2
    python load_project.py /path/to/my_project.xmpz2

Requirements:
    • Neo4j database running (test with: python test_neo4j_connection.py)
    • Valid .env file with Neo4j credentials
    • Miradi project file (.xmpz2 format)
        """
    )
    
    parser.add_argument(
        'project_file',
        help='Path to the Miradi project file (.xmpz2)'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear the Neo4j database before loading the project'
    )
    
    args = parser.parse_args()
    
    # Load the project
    success = load_project(args.project_file, clear_db=args.clear)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
