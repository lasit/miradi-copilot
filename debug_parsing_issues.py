#!/usr/bin/env python3
"""
Debug Parsing Issues

Investigates specific parsing problems:
1. Why activities have null element_id values
2. Why there are duplicate activities (same name, different UUIDs)
3. Why the project name is "Unnamed Project"
4. Count actual unique elements vs what's being created
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter
import zipfile
import json

# Add src to path
sys.path.insert(0, 'src')

from src.etl.miradi_parser import MiradiParser


def debug_xml_structure(project_file):
    """Debug the raw XML structure to understand the data."""
    print("=" * 60)
    print("🔍 DEBUGGING XML STRUCTURE")
    print("=" * 60)
    
    # Extract and parse XML
    with zipfile.ZipFile(project_file, 'r') as zip_file:
        xml_content = zip_file.read('project.xml')
        root = ET.fromstring(xml_content)
    
    print(f"📁 Root element: {root.tag}")
    print(f"📁 Root attributes: {root.attrib}")
    print()
    
    # Find project metadata
    print("🏷️  PROJECT METADATA:")
    project_summary = root.find('.//ProjectSummary')
    if project_summary is not None:
        print(f"   ProjectSummary found: {project_summary.attrib}")
        for child in project_summary:
            if 'name' in child.tag.lower() or 'title' in child.tag.lower():
                print(f"   • {child.tag}: {child.text}")
    
    # Look for project name in different locations
    for elem in root.iter():
        if 'name' in elem.tag.lower() and 'project' in elem.tag.lower():
            print(f"   • {elem.tag}: {elem.text}")
    
    print()
    
    # Find all pools
    print("🏊 ELEMENT POOLS:")
    pools = {}
    for pool in root.findall('.//Pool'):
        pool_type = pool.get('PoolName', 'Unknown')
        elements = pool.findall('.//Object')
        pools[pool_type] = len(elements)
        print(f"   • {pool_type}: {len(elements)} elements")
        
        # Debug first few elements in each pool
        if pool_type == 'TaskPool' and len(elements) > 0:
            print(f"     First 3 {pool_type} elements:")
            for i, elem in enumerate(elements[:3]):
                print(f"       [{i+1}] ID: {elem.get('Id')}, UUID: {elem.get('UUID')}")
                # Look for name
                name_elem = elem.find('.//Name')
                if name_elem is not None:
                    print(f"           Name: {name_elem.text}")
                # Show all attributes
                print(f"           Attributes: {elem.attrib}")
    
    print()
    return root, pools


def debug_activity_extraction(root):
    """Debug activity extraction specifically."""
    print("🎯 DEBUGGING ACTIVITY EXTRACTION")
    print("=" * 60)
    
    # Find TaskPool
    task_pool = root.find('.//Pool[@PoolName="TaskPool"]')
    if task_pool is None:
        print("❌ No TaskPool found!")
        return
    
    tasks = task_pool.findall('.//Object')
    print(f"📊 Found {len(tasks)} tasks in TaskPool")
    print()
    
    # Analyze each task
    task_data = []
    for i, task in enumerate(tasks):
        task_info = {
            'index': i + 1,
            'id': task.get('Id'),
            'uuid': task.get('UUID'),
            'attributes': dict(task.attrib)
        }
        
        # Find name
        name_elem = task.find('.//Name')
        task_info['name'] = name_elem.text if name_elem is not None else None
        
        # Find all child elements
        task_info['children'] = [child.tag for child in task]
        
        task_data.append(task_info)
        
        # Print first 5 tasks in detail
        if i < 5:
            print(f"Task {i+1}:")
            print(f"   ID: {task_info['id']}")
            print(f"   UUID: {task_info['uuid']}")
            print(f"   Name: {task_info['name']}")
            print(f"   Attributes: {task_info['attributes']}")
            print(f"   Children: {task_info['children']}")
            print()
    
    # Check for duplicates
    names = [t['name'] for t in task_data if t['name']]
    name_counts = Counter(names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        print("⚠️  DUPLICATE TASK NAMES:")
        for name, count in duplicates.items():
            print(f"   • '{name}': {count} occurrences")
            # Show the duplicates
            matching_tasks = [t for t in task_data if t['name'] == name]
            for task in matching_tasks:
                print(f"     - ID: {task['id']}, UUID: {task['uuid']}")
        print()
    
    # Check for null IDs
    null_ids = [t for t in task_data if t['id'] is None]
    if null_ids:
        print(f"❌ {len(null_ids)} tasks have null IDs:")
        for task in null_ids[:3]:  # Show first 3
            print(f"   • Name: {task['name']}, UUID: {task['uuid']}")
        print()
    
    return task_data


def debug_parser_extraction(project_file):
    """Debug the parser's extraction process."""
    print("🔧 DEBUGGING PARSER EXTRACTION")
    print("=" * 60)
    
    parser = MiradiParser()
    
    # Parse the project
    parsed_data = parser.parse_all(str(project_file))
    
    # Check project metadata
    print("📋 PROJECT METADATA:")
    project_meta = parsed_data.get('project_metadata', {})
    for key, value in project_meta.items():
        print(f"   • {key}: {value}")
    print()
    
    # Check activities
    activities = parsed_data.get('activities', [])
    print(f"🎯 ACTIVITIES EXTRACTED: {len(activities)}")
    
    if activities:
        print("First 5 activities:")
        for i, activity in enumerate(activities[:5]):
            print(f"   [{i+1}] ID: {activity.element_id}, UUID: {activity.uuid}")
            print(f"       Name: {activity.name}")
            print(f"       Attributes: {getattr(activity, 'attributes', 'N/A')}")
            print()
    
    # Check for null element_ids
    null_id_activities = [a for a in activities if a.element_id is None]
    if null_id_activities:
        print(f"❌ {len(null_id_activities)} activities have null element_id:")
        for activity in null_id_activities[:3]:
            print(f"   • Name: {activity.name}, UUID: {activity.uuid}")
            print(f"     Attributes: {activity.attributes}")
        print()
    
    # Check for duplicates
    activity_names = [a.name for a in activities if a.name]
    name_counts = Counter(activity_names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        print("⚠️  DUPLICATE ACTIVITY NAMES IN PARSED DATA:")
        for name, count in duplicates.items():
            print(f"   • '{name}': {count} occurrences")
            matching_activities = [a for a in activities if a.name == name]
            for activity in matching_activities:
                print(f"     - ID: {activity.element_id}, UUID: {activity.uuid}")
        print()
    
    # Get parsing summary
    summary = parser.get_parsing_summary()
    print("📊 PARSING SUMMARY:")
    print(f"   • Total elements: {summary['total_elements']}")
    print(f"   • Element breakdown: {summary['element_breakdown']}")
    print(f"   • Coverage: {summary['coverage']['known_element_coverage']:.1f}%")
    print()
    
    return parsed_data, summary


def debug_id_extraction_logic():
    """Debug the ID extraction logic in the parser."""
    print("🔍 DEBUGGING ID EXTRACTION LOGIC")
    print("=" * 60)
    
    # Read the parser source to understand ID extraction
    parser_file = Path('src/etl/miradi_parser.py')
    if parser_file.exists():
        with open(parser_file, 'r') as f:
            content = f.read()
        
        # Find extract_activities method
        lines = content.split('\n')
        in_extract_activities = False
        method_lines = []
        
        for line in lines:
            if 'def extract_activities(' in line:
                in_extract_activities = True
            elif in_extract_activities and line.strip().startswith('def ') and 'extract_activities' not in line:
                break
            
            if in_extract_activities:
                method_lines.append(line)
        
        print("📝 extract_activities method:")
        for i, line in enumerate(method_lines[:30]):  # First 30 lines
            print(f"   {i+1:2d}: {line}")
        
        if len(method_lines) > 30:
            print(f"   ... ({len(method_lines) - 30} more lines)")
        print()


def compare_xml_vs_parsed(project_file):
    """Compare what's in XML vs what gets parsed."""
    print("⚖️  COMPARING XML VS PARSED DATA")
    print("=" * 60)
    
    # Get XML data
    root, pools = debug_xml_structure(project_file)
    
    # Get parsed data
    parser = MiradiParser()
    parsed_data = parser.parse_all(str(project_file))
    
    print("📊 COMPARISON:")
    print(f"   XML TaskPool: {pools.get('TaskPool', 0)} tasks")
    print(f"   Parsed activities: {len(parsed_data.get('activities', []))}")
    print()
    
    # Check other element types
    element_mapping = {
        'TargetPool': 'conservation_targets',
        'CausePool': 'threats',
        'StrategyPool': 'strategies',
        'ResultsChainPool': 'results_chains',
        'ConceptualModelPool': 'conceptual_models'
    }
    
    for xml_pool, parsed_key in element_mapping.items():
        xml_count = pools.get(xml_pool, 0)
        parsed_count = len(parsed_data.get(parsed_key, []))
        print(f"   {xml_pool}: {xml_count} → {parsed_key}: {parsed_count}")
    
    print()


def main():
    """Main debug function."""
    if len(sys.argv) != 2:
        print("Usage: python debug_parsing_issues.py <project_file.xmpz2>")
        sys.exit(1)
    
    project_file = Path(sys.argv[1])
    if not project_file.exists():
        print(f"❌ Project file not found: {project_file}")
        sys.exit(1)
    
    print("🐛 MIRADI PARSING ISSUES DEBUGGER")
    print("=" * 60)
    print(f"📁 Project: {project_file.name}")
    print()
    
    try:
        # 1. Debug XML structure
        root, pools = debug_xml_structure(project_file)
        
        # 2. Debug activity extraction from XML
        task_data = debug_activity_extraction(root)
        
        # 3. Debug parser extraction
        parsed_data, summary = debug_parser_extraction(project_file)
        
        # 4. Debug ID extraction logic
        debug_id_extraction_logic()
        
        # 5. Compare XML vs parsed
        compare_xml_vs_parsed(project_file)
        
        print("✅ Debug analysis complete!")
        print()
        print("🔧 RECOMMENDED FIXES:")
        print("1. Check ID extraction in extract_activities() method")
        print("2. Investigate duplicate activity sources")
        print("3. Fix project name extraction in extract_project_metadata()")
        print("4. Add validation for null element_ids")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
