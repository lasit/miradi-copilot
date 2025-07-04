#!/usr/bin/env python3
"""
Generate Schema Discovery Log

This script processes all Miradi projects in data/sample_projects/ and generates
a comprehensive schema discovery log in docs/schemas/schema-discovery-log.md.

The log categorizes elements by their frequency across projects to help understand
which parts of the Miradi schema are essential vs optional.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# Add src to path so we can import the schema explorer
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.schema_explorer import MiradiSchemaExplorer


def get_file_stats(file_path: Path) -> dict:
    """Get file statistics including size and modification date."""
    stat = file_path.stat()
    return {
        'size_bytes': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'modified_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    }


def categorize_elements_by_frequency(file_element_presence: dict, total_files: int) -> dict:
    """Categorize elements based on how frequently they appear across projects."""
    categories = {
        'core': [],      # In ALL projects
        'common': [],    # In 75%+ of projects
        'optional': [],  # In 25-74% of projects
        'rare': []       # In <25% of projects
    }
    
    for element, files_with_element in file_element_presence.items():
        frequency = len(files_with_element) / total_files
        
        if frequency == 1.0:
            categories['core'].append(element)
        elif frequency >= 0.75:
            categories['common'].append(element)
        elif frequency >= 0.25:
            categories['optional'].append(element)
        else:
            categories['rare'].append(element)
    
    return categories


def generate_schema_discovery_log():
    """Generate the schema discovery log from sample projects."""
    
    # Set up paths
    sample_projects_dir = Path("data/sample_projects")
    output_file = Path("docs/schemas/schema-discovery-log.md")
    
    if not sample_projects_dir.exists():
        print(f"Error: Sample projects directory not found: {sample_projects_dir}")
        return
    
    # Find all .xmpz2 files
    xmpz2_files = list(sample_projects_dir.glob("*.xmpz2"))
    
    if not xmpz2_files:
        print(f"No .xmpz2 files found in {sample_projects_dir}")
        return
    
    print(f"Found {len(xmpz2_files)} .xmpz2 files to analyze")
    
    # Create explorer and process all files
    explorer = MiradiSchemaExplorer()
    
    # Collect file statistics
    file_stats = {}
    for file_path in xmpz2_files:
        file_stats[file_path.name] = get_file_stats(file_path)
    
    # Process all files
    for file_path in xmpz2_files:
        explorer.analyze_file_for_batch(file_path)
    
    if not explorer.processed_files:
        print("No files were successfully processed")
        return
    
    # Categorize elements by frequency
    total_files = len(explorer.processed_files)
    element_categories = categorize_elements_by_frequency(explorer.file_element_presence, total_files)
    
    # Generate the report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("# Miradi Schema Discovery Log\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This log tracks the analysis of Miradi project files to understand schema variations and element usage patterns.\n\n")
        
        # Analysis Summary
        f.write("## Analysis Summary\n\n")
        f.write(f"- **Total Projects Analyzed:** {total_files}\n")
        f.write(f"- **Unique Element Types Found:** {len(explorer.element_counts)}\n")
        f.write(f"- **Total Element Instances:** {sum(explorer.element_counts.values())}\n\n")
        
        # Project List
        f.write("## Projects Analyzed\n\n")
        f.write("| Project File | Size (MB) | Last Modified | Elements Found |\n")
        f.write("|--------------|-----------|---------------|----------------|\n")
        
        for file_name in sorted(explorer.processed_files):
            stats = file_stats.get(file_name, {})
            size_mb = stats.get('size_mb', 'Unknown')
            modified = stats.get('modified_date', 'Unknown')
            
            # Count unique elements in this file
            elements_in_file = len([elem for elem, files in explorer.file_element_presence.items() 
                                  if file_name in files])
            
            f.write(f"| {file_name} | {size_mb} | {modified} | {elements_in_file} |\n")
        
        f.write("\n")
        
        # Element Distribution Overview
        f.write("## Element Distribution Overview\n\n")
        f.write("| Category | Count | Description |\n")
        f.write("|----------|-------|-------------|\n")
        f.write(f"| **Core Elements** | {len(element_categories['core'])} | Present in ALL projects (100%) |\n")
        f.write(f"| **Common Elements** | {len(element_categories['common'])} | Present in 75%+ of projects |\n")
        f.write(f"| **Optional Elements** | {len(element_categories['optional'])} | Present in 25-74% of projects |\n")
        f.write(f"| **Rare Elements** | {len(element_categories['rare'])} | Present in <25% of projects |\n")
        f.write("\n")
        
        # Core Elements (Essential Schema)
        f.write("## Core Elements (Essential Schema)\n\n")
        f.write("These elements appear in **ALL** analyzed projects and represent the essential Miradi schema:\n\n")
        
        core_elements = sorted(element_categories['core'])
        for element in core_elements:
            count = explorer.element_counts[element]
            f.write(f"- `{element}` ({count} total occurrences)\n")
        
        f.write(f"\n**Total Core Elements:** {len(core_elements)}\n\n")
        
        # Common Elements
        f.write("## Common Elements (Frequently Used)\n\n")
        f.write("These elements appear in 75% or more of projects:\n\n")
        
        common_elements = sorted(element_categories['common'])
        for element in common_elements:
            count = explorer.element_counts[element]
            files_with_element = len(explorer.file_element_presence[element])
            percentage = round((files_with_element / total_files) * 100)
            f.write(f"- `{element}` ({count} occurrences, {percentage}% of projects)\n")
        
        f.write(f"\n**Total Common Elements:** {len(common_elements)}\n\n")
        
        # Optional Elements
        f.write("## Optional Elements (Moderately Used)\n\n")
        f.write("These elements appear in 25-74% of projects:\n\n")
        
        optional_elements = sorted(element_categories['optional'])
        for element in optional_elements:
            count = explorer.element_counts[element]
            files_with_element = len(explorer.file_element_presence[element])
            percentage = round((files_with_element / total_files) * 100)
            f.write(f"- `{element}` ({count} occurrences, {percentage}% of projects)\n")
        
        f.write(f"\n**Total Optional Elements:** {len(optional_elements)}\n\n")
        
        # Rare Elements
        f.write("## Rare Elements (Seldom Used)\n\n")
        f.write("These elements appear in less than 25% of projects:\n\n")
        
        rare_elements = sorted(element_categories['rare'])
        for element in rare_elements:
            count = explorer.element_counts[element]
            files_with_element = explorer.file_element_presence[element]
            file_list = sorted(files_with_element)
            f.write(f"- `{element}` ({count} occurrences in {len(files_with_element)} projects: {', '.join(file_list)})\n")
        
        f.write(f"\n**Total Rare Elements:** {len(rare_elements)}\n\n")
        
        # Element Usage Statistics
        f.write("## Element Usage Statistics\n\n")
        
        # Most frequent elements
        f.write("### Most Frequently Used Elements\n\n")
        f.write("| Element | Total Occurrences | Projects Using | Frequency |\n")
        f.write("|---------|-------------------|----------------|----------|\n")
        
        for element, count in explorer.element_counts.most_common(20):
            files_with_element = len(explorer.file_element_presence[element])
            percentage = round((files_with_element / total_files) * 100)
            f.write(f"| `{element}` | {count} | {files_with_element}/{total_files} | {percentage}% |\n")
        
        f.write("\n")
        
        # Project-specific elements
        f.write("### Project-Specific Elements\n\n")
        f.write("Elements that appear in only one project:\n\n")
        
        single_project_elements = [elem for elem, files in explorer.file_element_presence.items() 
                                 if len(files) == 1]
        
        if single_project_elements:
            # Group by project
            by_project = defaultdict(list)
            for element in single_project_elements:
                project = list(explorer.file_element_presence[element])[0]
                by_project[project].append(element)
            
            for project in sorted(by_project.keys()):
                elements = sorted(by_project[project])
                f.write(f"**{project}:**\n")
                for element in elements:
                    count = explorer.element_counts[element]
                    f.write(f"- `{element}` ({count} occurrences)\n")
                f.write("\n")
        else:
            f.write("No elements are unique to a single project.\n\n")
        
        # Recommendations
        f.write("## Recommendations for Parser Implementation\n\n")
        f.write("### Priority 1: Core Elements\n")
        f.write("Implement parsers for all core elements first, as they appear in every project:\n")
        f.write(f"- {len(core_elements)} elements to implement\n")
        f.write("- These represent the essential Miradi schema\n")
        f.write("- Required for basic project functionality\n\n")
        
        f.write("### Priority 2: Common Elements\n")
        f.write("Implement parsers for common elements to support most use cases:\n")
        f.write(f"- {len(common_elements)} additional elements\n")
        f.write("- Will support 75%+ of project features\n")
        f.write("- Good return on investment for development effort\n\n")
        
        f.write("### Priority 3: Optional Elements\n")
        f.write("Consider implementing based on specific user needs:\n")
        f.write(f"- {len(optional_elements)} elements with moderate usage\n")
        f.write("- Implement based on user feedback and requirements\n")
        f.write("- May be project-type or workflow specific\n\n")
        
        f.write("### Priority 4: Rare Elements\n")
        f.write("Implement only if specifically required:\n")
        f.write(f"- {len(rare_elements)} elements with limited usage\n")
        f.write("- May be legacy, experimental, or highly specialized\n")
        f.write("- Consider graceful handling rather than full parsing\n\n")
        
        # Validation Rules
        f.write("## Validation Rules Discovered\n\n")
        f.write("### Required Elements (Core Schema)\n")
        f.write("These elements should be considered required in any Miradi project:\n\n")
        
        # List core elements that appear frequently
        high_frequency_core = [(elem, explorer.element_counts[elem]) for elem in core_elements 
                              if explorer.element_counts[elem] > total_files]
        high_frequency_core.sort(key=lambda x: x[1], reverse=True)
        
        for element, count in high_frequency_core[:10]:
            avg_per_project = round(count / total_files, 1)
            f.write(f"- `{element}`: Average {avg_per_project} per project\n")
        
        f.write("\n### Optional Elements Patterns\n")
        f.write("Elements that may be optional based on project type or complexity:\n\n")
        
        # Show some optional elements with their usage patterns
        for element in optional_elements[:10]:
            files_with_element = len(explorer.file_element_presence[element])
            percentage = round((files_with_element / total_files) * 100)
            f.write(f"- `{element}`: Used in {percentage}% of projects\n")
        
        f.write("\n")
        
        # Future Analysis
        f.write("## Future Analysis Recommendations\n\n")
        f.write("1. **Version Analysis**: Track how element usage changes across Miradi versions\n")
        f.write("2. **Project Type Analysis**: Categorize projects and analyze element usage by type\n")
        f.write("3. **Attribute Analysis**: Examine which attributes are required vs optional for each element\n")
        f.write("4. **Relationship Analysis**: Map parent-child relationships and their consistency\n")
        f.write("5. **Data Quality Analysis**: Identify common data quality issues and validation needs\n\n")
        
        # Methodology
        f.write("## Analysis Methodology\n\n")
        f.write("### Data Collection\n")
        f.write("- Extracted and analyzed XML structure from .xmpz2 files\n")
        f.write("- Counted element occurrences across all projects\n")
        f.write("- Tracked which projects contain each element type\n")
        f.write("- Recorded element attributes and hierarchical relationships\n\n")
        
        f.write("### Categorization Criteria\n")
        f.write("- **Core**: Present in 100% of projects\n")
        f.write("- **Common**: Present in 75-99% of projects\n")
        f.write("- **Optional**: Present in 25-74% of projects\n")
        f.write("- **Rare**: Present in <25% of projects\n\n")
        
        f.write("### Tools Used\n")
        f.write("- Custom Python schema explorer\n")
        f.write("- XML parsing with ElementTree\n")
        f.write("- Statistical analysis of element frequency\n")
        f.write("- Cross-project comparison algorithms\n\n")
    
    print(f"Schema discovery log generated: {output_file}")
    
    # Print summary to console
    print(f"\nAnalysis Summary:")
    print(f"- Projects analyzed: {total_files}")
    print(f"- Core elements (100%): {len(element_categories['core'])}")
    print(f"- Common elements (75%+): {len(element_categories['common'])}")
    print(f"- Optional elements (25-74%): {len(element_categories['optional'])}")
    print(f"- Rare elements (<25%): {len(element_categories['rare'])}")


if __name__ == "__main__":
    generate_schema_discovery_log()
