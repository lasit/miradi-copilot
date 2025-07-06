#!/usr/bin/env python3
"""Debug spatial data extraction by examining XML structure."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def debug_spatial_xml(file_path: str):
    """Debug the XML structure for spatial data."""
    print("🔍 DEBUGGING SPATIAL XML STRUCTURE")
    print("=" * 60)
    
    # Extract the .xmpz2 file
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Find project.xml
        xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
        if not xml_files:
            print("No XML files found!")
            return
        
        project_xml = xml_files[0]
        print(f"Reading XML file: {project_xml}")
        
        # Read and parse XML
        with zip_ref.open(project_xml) as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
    
    # Find DiagramFactorPool
    diagram_factor_pool = None
    for elem in root.iter():
        if elem.tag.endswith('DiagramFactorPool'):
            diagram_factor_pool = elem
            break
    
    if diagram_factor_pool is None:
        print("❌ DiagramFactorPool not found!")
        return
    
    print(f"✅ Found DiagramFactorPool")
    
    # Find first few DiagramFactor elements
    diagram_factors = []
    for elem in diagram_factor_pool.iter():
        if elem.tag.endswith('DiagramFactor'):
            diagram_factors.append(elem)
            if len(diagram_factors) >= 3:  # Just examine first 3
                break
    
    print(f"Found {len(diagram_factors)} DiagramFactor elements to examine")
    
    # Examine each diagram factor
    for i, factor in enumerate(diagram_factors):
        print(f"\n📍 DIAGRAM FACTOR {i+1}")
        print("-" * 40)
        
        # Get factor ID
        factor_id = factor.get('Id', 'Unknown')
        print(f"Factor ID: {factor_id}")
        
        # Look for DiagramFactorLocation
        location_found = False
        size_found = False
        
        for child in factor:
            child_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            
            if child_name == 'DiagramFactorLocation':
                print(f"✅ Found DiagramFactorLocation:")
                location_found = True
                
                # Look for x and y coordinates
                for coord in child:
                    coord_name = coord.tag.split('}')[-1] if '}' in coord.tag else coord.tag
                    coord_value = coord.text if coord.text else 'None'
                    print(f"   {coord_name}: {coord_value}")
            
            elif child_name == 'DiagramFactorSize':
                print(f"✅ Found DiagramFactorSize:")
                size_found = True
                
                # Look for width and height
                for dim in child:
                    dim_name = dim.tag.split('}')[-1] if '}' in dim.tag else dim.tag
                    dim_value = dim.text if dim.text else 'None'
                    print(f"   {dim_name}: {dim_value}")
            
            elif child_name in ['DiagramFactorWrappedFactorId', 'DiagramFactorUUID']:
                print(f"📋 {child_name}: Found")
        
        if not location_found:
            print("❌ DiagramFactorLocation NOT found")
        if not size_found:
            print("❌ DiagramFactorSize NOT found")
        
        # Show raw XML for this factor (truncated)
        raw_xml = ET.tostring(factor, encoding='unicode')
        if len(raw_xml) > 500:
            raw_xml = raw_xml[:500] + "..."
        print(f"\n📄 Raw XML (truncated):")
        print(raw_xml)

if __name__ == "__main__":
    debug_spatial_xml("data/sample_projects/Bulgul_Rangers_v0.111.xmpz2")
