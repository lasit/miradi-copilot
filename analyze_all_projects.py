#!/usr/bin/env python3
"""
Miradi Project Analyzer

A comprehensive analysis tool for all Miradi conservation projects in the sample
projects directory. This script analyzes each project separately without loading
them into Neo4j, providing detailed reports and comparisons.

Usage:
    python analyze_all_projects.py
    python analyze_all_projects.py --detailed
    python analyze_all_projects.py --export report.json

Features:
    - Analyzes all .xmpz2 files in data/sample_projects/ without loading
    - Provides parsing statistics and schema coverage for each project
    - Generates comparative analysis across projects
    - Exports detailed reports in JSON format
    - Clean, formatted output with project comparisons
"""

import sys
import logging
import argparse
import time
import json
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

from src.etl.miradi_parser import MiradiParser
from src.etl.schema_mapper import MiradiToGraphMapper


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


def find_project_files(directory="data/sample_projects"):
    """Find all .xmpz2 project files in the specified directory."""
    project_dir = Path(directory)
    
    if not project_dir.exists():
        print(f"❌ Error: Project directory not found: {directory}")
        return []
    
    project_files = list(project_dir.glob("*.xmpz2"))
    project_files.sort()  # Sort for consistent ordering
    
    return project_files


def analyze_single_project(project_file, project_num, total_projects, detailed=False):
    """
    Analyze a single project without loading into Neo4j.
    
    Args:
        project_file: Path to the project file
        project_num: Current project number (1-based)
        total_projects: Total number of projects
        detailed: Whether to include detailed analysis
        
    Returns:
        dict: Analysis results or None if failed
    """
    project_name = extract_project_name(project_file)
    
    print(f"📁 [{project_num}/{total_projects}] {project_name}")
    print(f"   🔍 Analyzing...")
    
    start_time = time.time()
    
    try:
        # Initialize parser and mapper
        parser = MiradiParser()
        mapper = MiradiToGraphMapper()
        
        # Parse the project
        parsed_data = parser.parse_all(str(project_file))
        parsing_summary = parser.get_parsing_summary()
        
        # Convert to graph format (without loading)
        graph_result = mapper.map_project_to_graph(parsed_data)
        
        analysis_time = time.time() - start_time
        
        # Calculate statistics
        total_elements = parsing_summary['total_elements']
        coverage = parsing_summary['coverage']['known_element_coverage']
        nodes_count = len(graph_result.nodes)
        relationships_count = len(graph_result.relationships)
        conversion_errors = len(graph_result.errors)
        
        print(f"   ✅ Complete! {format_number(total_elements)} elements, {coverage:.1f}% coverage ({format_time(analysis_time)})")
        
        # Build analysis result
        result = {
            'success': True,
            'project_name': project_name,
            'filename': project_file.name,
            'file_path': str(project_file),
            'analysis_time': analysis_time,
            
            # Parsing statistics
            'parsing': {
                'total_elements': total_elements,
                'element_breakdown': parsing_summary['element_breakdown'],
                'coverage': parsing_summary['coverage']
            },
            
            # Graph conversion statistics
            'graph': {
                'nodes_count': nodes_count,
                'relationships_count': relationships_count,
                'conversion_errors': conversion_errors,
                'node_counts': graph_result.stats.get('node_counts', {}),
                'relationship_counts': graph_result.stats.get('relationship_counts', {})
            }
        }
        
        if detailed:
            result['detailed'] = {
                'conversion_errors': graph_result.errors[:10],  # First 10 errors
                'conversion_warnings': graph_result.warnings[:10],  # First 10 warnings
                'unknown_elements': parsing_summary.get('unknown_elements', [])
            }
        
        return result
        
    except Exception as e:
        analysis_time = time.time() - start_time
        print(f"   ❌ Error: {str(e)}")
        
        return {
            'success': False,
            'project_name': project_name,
            'filename': project_file.name,
            'file_path': str(project_file),
            'error': str(e),
            'analysis_time': analysis_time
        }


def analyze_all_projects(detailed=False, export_file=None):
    """
    Analyze all Miradi projects and generate comprehensive report.
    
    Args:
        detailed: Whether to include detailed analysis
        export_file: Optional file path to export JSON report
        
    Returns:
        bool: True if at least one project analyzed successfully
    """
    print("=" * 70)
    print("🔍 MIRADI PROJECT ANALYZER")
    print("=" * 70)
    
    # Find all project files
    project_files = find_project_files()
    
    if not project_files:
        print("❌ No .xmpz2 project files found in data/sample_projects/")
        return False
    
    print(f"📂 Found {len(project_files)} Miradi projects to analyze")
    print("   (Analysis only - no data will be loaded into Neo4j)")
    print()
    
    # Analyze each project
    print("🚀 Starting project analysis...")
    print("=" * 70)
    
    batch_start_time = time.time()
    results = []
    
    for i, project_file in enumerate(project_files, 1):
        result = analyze_single_project(project_file, i, len(project_files), detailed)
        results.append(result)
        print()  # Add spacing between projects
    
    batch_time = time.time() - batch_start_time
    
    # Calculate summary statistics
    successful_projects = [r for r in results if r['success']]
    failed_projects = [r for r in results if not r['success']]
    
    if successful_projects:
        total_elements = sum(r['parsing']['total_elements'] for r in successful_projects)
        avg_coverage = sum(r['parsing']['coverage']['known_element_coverage'] for r in successful_projects) / len(successful_projects)
        total_nodes = sum(r['graph']['nodes_count'] for r in successful_projects)
        total_relationships = sum(r['graph']['relationships_count'] for r in successful_projects)
        total_errors = sum(r['graph']['conversion_errors'] for r in successful_projects)
    else:
        total_elements = avg_coverage = total_nodes = total_relationships = total_errors = 0
    
    # Display summary
    print("=" * 70)
    print("📊 PROJECT ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully Analyzed: {len(successful_projects)}/{len(project_files)}")
    print(f"❌ Analysis Failures: {len(failed_projects)}")
    print(f"⏱️  Total Analysis Time: {format_time(batch_time)}")
    print()
    
    if successful_projects:
        print("📈 AGGREGATE STATISTICS:")
        print(f"   • Total Elements Parsed: {format_number(total_elements)}")
        print(f"   • Average Schema Coverage: {avg_coverage:.1f}%")
        print(f"   • Total Potential Nodes: {format_number(total_nodes)}")
        print(f"   • Total Potential Relationships: {format_number(total_relationships)}")
        print(f"   • Total Conversion Issues: {format_number(total_errors)}")
        print()
    
    if successful_projects:
        print("✅ PROJECT ANALYSIS RESULTS:")
        for result in successful_projects:
            coverage = result['parsing']['coverage']['known_element_coverage']
            elements = result['parsing']['total_elements']
            nodes = result['graph']['nodes_count']
            relationships = result['graph']['relationships_count']
            errors = result['graph']['conversion_errors']
            
            print(f"   • {result['project_name']}:")
            print(f"     📊 {format_number(elements)} elements, {coverage:.1f}% coverage")
            print(f"     🔗 {format_number(nodes)} nodes, {format_number(relationships)} relationships")
            if errors > 0:
                print(f"     ⚠️  {format_number(errors)} conversion issues")
        print()
    
    if failed_projects:
        print("❌ ANALYSIS FAILURES:")
        for result in failed_projects:
            print(f"   • {result['project_name']}: {result['error']}")
        print()
    
    # Export detailed report if requested
    if export_file and successful_projects:
        try:
            report_data = {
                'analysis_summary': {
                    'total_projects': len(project_files),
                    'successful_analyses': len(successful_projects),
                    'failed_analyses': len(failed_projects),
                    'analysis_time': batch_time,
                    'aggregate_stats': {
                        'total_elements': total_elements,
                        'average_coverage': avg_coverage,
                        'total_nodes': total_nodes,
                        'total_relationships': total_relationships,
                        'total_errors': total_errors
                    }
                },
                'project_results': successful_projects,
                'failed_projects': failed_projects
            }
            
            with open(export_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"📄 Detailed report exported to: {export_file}")
            print()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not export report: {e}")
            print()
    
    if successful_projects:
        print("🎉 Project analysis completed!")
        print("   Use 'python load_project.py <project>' to load a specific project into Neo4j.")
        print("   Use 'python switch_project.py' to manage loaded projects.")
    else:
        print("😞 No projects were analyzed successfully.")
        print("   Check project file integrity and parser compatibility.")
    
    print("=" * 70)
    
    return len(successful_projects) > 0


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Analyze all Miradi conservation projects without loading',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze_all_projects.py                    # Basic analysis
    python analyze_all_projects.py --detailed         # Detailed analysis with errors
    python analyze_all_projects.py --export report.json  # Export detailed JSON report

Features:
    • Analyzes all .xmpz2 files from data/sample_projects/
    • Shows parsing statistics and schema coverage
    • Provides comparative analysis across projects
    • No Neo4j database required (analysis only)
    • Optional detailed error reporting and JSON export

Output:
    • Project-by-project analysis results
    • Aggregate statistics across all projects
    • Schema coverage and conversion metrics
    • Optional detailed JSON report for further analysis
        """
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed analysis with conversion errors and warnings'
    )
    
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export detailed analysis report to JSON file'
    )
    
    args = parser.parse_args()
    
    # Analyze all projects
    success = analyze_all_projects(detailed=args.detailed, export_file=args.export)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
