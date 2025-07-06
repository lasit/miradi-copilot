"""
Debug script to investigate why elements are being skipped during parsing.

This script helps diagnose issues with the MiradiParser and schema mapper
by examining the structure of parsed elements and their data.
"""

from src.etl.miradi_parser import MiradiParser

def debug_parser():
    """Debug the parser to understand element structure and data access."""
    
    print("=" * 60)
    print("MIRADI PARSER DEBUG SCRIPT")
    print("=" * 60)
    
    # Parse the file
    print("Initializing parser...")
    parser = MiradiParser()
    
    print("Parsing Bulgul Rangers project...")
    data = parser.parse_all("data/sample_projects/Bulgul_Rangers_v0.111.xmpz2")
    
    print(f"Parsed data type: {type(data)}")
    print(f"Top-level keys: {list(data.keys())}")
    
    # Check what's in conservation targets
    targets = data.get('conservation_targets', [])
    print(f"\nFound {len(targets)} conservation targets")
    
    if targets:
        # Look at the first target
        first_target = targets[0]
        print(f"\nFirst target type: {type(first_target)}")
        print(f"First target attributes: {dir(first_target)}")
        
        if hasattr(first_target, 'data'):
            print(f"First target has .data attribute")
            print(f"First target data type: {type(first_target.data)}")
            print(f"First target data keys: {list(first_target.data.keys())}")
            print(f"Sample data: {first_target.data}")
            
            # Check specific fields
            target_id = first_target.data.get('id')
            target_name = first_target.data.get('name')
            target_uuid = first_target.data.get('uuid')
            print(f"Target ID: {target_id}")
            print(f"Target Name: {target_name}")
            print(f"Target UUID: {target_uuid}")
        else:
            print(f"First target is plain dictionary")
            print(f"First target keys: {list(first_target.keys())}")
            print(f"Sample data: {first_target}")
    else:
        print("No conservation targets found!")
    
    # Check strategies
    strategies = data.get('strategies', [])
    print(f"\nFound {len(strategies)} strategies")
    if strategies:
        first_strategy = strategies[0]
        print(f"First strategy type: {type(first_strategy)}")
        if hasattr(first_strategy, 'data'):
            print(f"First strategy data keys: {list(first_strategy.data.keys())}")
            strategy_id = first_strategy.data.get('id')
            strategy_name = first_strategy.data.get('name')
            print(f"Strategy ID: {strategy_id}")
            print(f"Strategy Name: {strategy_name}")
        else:
            print(f"First strategy keys: {list(first_strategy.keys())}")
    else:
        print("No strategies found!")
    
    # Check threats
    threats = data.get('threats', [])
    print(f"\nFound {len(threats)} threats")
    if threats:
        first_threat = threats[0]
        print(f"First threat type: {type(first_threat)}")
        if hasattr(first_threat, 'data'):
            print(f"First threat data keys: {list(first_threat.data.keys())}")
            threat_id = first_threat.data.get('id')
            threat_name = first_threat.data.get('name')
            print(f"Threat ID: {threat_id}")
            print(f"Threat Name: {threat_name}")
        else:
            print(f"First threat keys: {list(first_threat.keys())}")
    else:
        print("No threats found!")
    
    # Check activities
    activities = data.get('activities', [])
    print(f"\nFound {len(activities)} activities")
    if activities:
        first_activity = activities[0]
        print(f"First activity type: {type(first_activity)}")
        if hasattr(first_activity, 'data'):
            print(f"First activity data keys: {list(first_activity.data.keys())}")
            activity_id = first_activity.data.get('id')
            activity_name = first_activity.data.get('name')
            print(f"Activity ID: {activity_id}")
            print(f"Activity Name: {activity_name}")
        else:
            print(f"First activity keys: {list(first_activity.keys())}")
    else:
        print("No activities found!")
    
    # Check project metadata
    project_metadata = data.get('project_metadata', {})
    print(f"\nProject metadata type: {type(project_metadata)}")
    print(f"Project metadata: {project_metadata}")
    
    # Get parsing summary
    print("\n" + "=" * 60)
    print("PARSING SUMMARY")
    print("=" * 60)
    
    summary = parser.get_parsing_summary()
    print(f"Total elements: {summary.get('total_elements', 0)}")
    print(f"Element breakdown:")
    for element_type, count in summary.get('element_breakdown', {}).items():
        print(f"  {element_type}: {count}")
    
    coverage = summary.get('coverage', {})
    print(f"\nCoverage:")
    print(f"  Known element coverage: {coverage.get('known_element_coverage', 0):.1f}%")
    print(f"  Must-support coverage: {coverage.get('must_support_coverage', 0):.1f}%")
    
    # Test schema mapper compatibility
    print("\n" + "=" * 60)
    print("SCHEMA MAPPER COMPATIBILITY TEST")
    print("=" * 60)
    
    from src.etl.schema_mapper import MiradiToGraphMapper
    
    mapper = MiradiToGraphMapper()
    
    # Test the helper function
    if targets:
        first_target = targets[0]
        extracted_data = mapper._extract_element_data(first_target)
        print(f"Extracted data type: {type(extracted_data)}")
        print(f"Extracted data keys: {list(extracted_data.keys())}")
        
        # Test accessing properties
        target_id = extracted_data.get('id')
        target_name = extracted_data.get('name')
        print(f"Extracted Target ID: {target_id}")
        print(f"Extracted Target Name: {target_name}")
    
    # Enhanced parser helper method test
    print("\n" + "=" * 60)
    print("PARSER HELPER METHOD TEST")
    print("=" * 60)

    # Test the extraction helper methods directly
    if targets:
        first_target = targets[0]
        if hasattr(first_target, 'data'):
            target_data = first_target.data
            
            # Test ID extraction
            id_from_attributes = target_data.get('attributes', {}).get('Id')
            print(f"\nDirect ID extraction from attributes: {id_from_attributes}")
            
            # Test name extraction
            name_path = target_data.get('children', {}).get('BiodiversityTargetName', {})
            name_from_text = name_path.get('text')
            name_from_div = name_path.get('children', {}).get('div', {}).get('text')
            print(f"Name from text: {name_from_text}")
            print(f"Name from div: {name_from_div}")
            
            # Test UUID extraction
            uuid_from_children = target_data.get('children', {}).get('BiodiversityTargetUUID', {}).get('text')
            print(f"UUID extraction: {uuid_from_children}")
            
            # Test if parser has the helper methods
            if hasattr(parser, '_extract_element_id'):
                extracted_id = parser._extract_element_id(target_data)
                print(f"\nParser._extract_element_id result: {extracted_id}")
            else:
                print("\nParser does not have _extract_element_id method!")
            
            if hasattr(parser, '_extract_element_name'):
                extracted_name = parser._extract_element_name(target_data, 'BiodiversityTargetName')
                print(f"Parser._extract_element_name result: {extracted_name}")
            else:
                print("Parser does not have _extract_element_name method!")
                
            if hasattr(parser, '_extract_element_uuid'):
                extracted_uuid = parser._extract_element_uuid(target_data, 'BiodiversityTargetUUID')
                print(f"Parser._extract_element_uuid result: {extracted_uuid}")
            else:
                print("Parser does not have _extract_element_uuid method!")
        
        # Check the actual ParsedElement attributes
        print(f"\nParsedElement attributes:")
        print(f"  element_id: {first_target.element_id}")
        print(f"  name: {first_target.name}")
        print(f"  uuid: {first_target.uuid}")

    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    debug_parser()
