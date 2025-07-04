#!/usr/bin/env python3
"""
Miradi Schema Explorer

A utility script to explore the structure of Miradi .xmpz2 files.
This script extracts and analyzes the XML structure without parsing the content.

Usage:
    python schema_explorer.py <path_to_xmpz2_file>
"""

import argparse
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class MiradiSchemaExplorer:
    """Explores the structure of Miradi .xmpz2 files."""
    
    def __init__(self):
        self.element_counts = Counter()
        self.element_attributes = defaultdict(set)
        self.element_hierarchy = defaultdict(set)
        self.xml_files_found = []
    
    def extract_xmpz2_file(self, file_path: Path) -> Path:
        """
        Extract .xmpz2 file to a temporary directory.
        
        Args:
            file_path: Path to the .xmpz2 file
            
        Returns:
            Path to the temporary directory containing extracted files
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            zipfile.BadZipFile: If the file is not a valid zip file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() in ['.xmpz2', '.zip']:
            print(f"Warning: File extension '{file_path.suffix}' is not .xmpz2")
        
        temp_dir = Path(tempfile.mkdtemp(prefix="miradi_explorer_"))
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                print(f"Extracted {len(zip_ref.namelist())} files to: {temp_dir}")
                
                # List extracted files
                for file_name in zip_ref.namelist():
                    print(f"  - {file_name}")
                    
        except zipfile.BadZipFile as e:
            raise zipfile.BadZipFile(f"Invalid zip file: {file_path}") from e
        
        return temp_dir
    
    def find_xml_files(self, directory: Path) -> List[Path]:
        """
        Find all XML files in the extracted directory.
        
        Args:
            directory: Directory to search for XML files
            
        Returns:
            List of paths to XML files found
        """
        xml_files = []
        
        for file_path in directory.rglob("*.xml"):
            xml_files.append(file_path)
            self.xml_files_found.append(file_path.name)
        
        # Also check for files without extension that might be XML
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix == "":
                try:
                    # Try to parse as XML to see if it's an XML file
                    ET.parse(file_path)
                    xml_files.append(file_path)
                    self.xml_files_found.append(file_path.name)
                    print(f"Found XML file without .xml extension: {file_path.name}")
                except ET.ParseError:
                    # Not an XML file, skip
                    pass
        
        return xml_files
    
    def analyze_xml_structure(self, xml_file: Path) -> None:
        """
        Analyze the structure of an XML file.
        
        Args:
            xml_file: Path to the XML file to analyze
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            print(f"\nAnalyzing XML file: {xml_file.name}")
            print(f"Root element: <{root.tag}>")
            
            if root.attrib:
                print(f"Root attributes: {list(root.attrib.keys())}")
            
            # Recursively analyze all elements
            self._analyze_element(root, parent_tag=None, depth=0)
            
        except ET.ParseError as e:
            print(f"Error parsing XML file {xml_file.name}: {e}")
        except Exception as e:
            print(f"Unexpected error analyzing {xml_file.name}: {e}")
    
    def _analyze_element(self, element: ET.Element, parent_tag: str = None, depth: int = 0) -> None:
        """
        Recursively analyze an XML element and its children.
        
        Args:
            element: The XML element to analyze
            parent_tag: Tag name of the parent element
            depth: Current depth in the XML hierarchy
        """
        tag = element.tag
        
        # Count element occurrences
        self.element_counts[tag] += 1
        
        # Track attributes for this element type
        if element.attrib:
            self.element_attributes[tag].update(element.attrib.keys())
        
        # Track parent-child relationships
        if parent_tag:
            self.element_hierarchy[parent_tag].add(tag)
        
        # Recursively analyze children
        for child in element:
            self._analyze_element(child, parent_tag=tag, depth=depth + 1)
    
    def print_structure_summary(self) -> None:
        """Print a summary of the XML structure found."""
        print("\n" + "="*60)
        print("MIRADI SCHEMA EXPLORATION SUMMARY")
        print("="*60)
        
        print(f"\nXML Files Found: {len(self.xml_files_found)}")
        for xml_file in self.xml_files_found:
            print(f"  - {xml_file}")
        
        print(f"\nTotal Unique Element Types: {len(self.element_counts)}")
        print(f"Total Element Instances: {sum(self.element_counts.values())}")
        
        # Print element counts sorted by frequency
        print("\nElement Frequency (most common first):")
        for element, count in self.element_counts.most_common():
            print(f"  {element:<30} : {count:>6} occurrences")
        
        # Print element attributes
        print("\nElement Attributes:")
        for element in sorted(self.element_attributes.keys()):
            attrs = sorted(self.element_attributes[element])
            print(f"  {element}:")
            for attr in attrs:
                print(f"    - {attr}")
        
        # Print hierarchy relationships
        print("\nElement Hierarchy (parent -> children):")
        for parent in sorted(self.element_hierarchy.keys()):
            children = sorted(self.element_hierarchy[parent])
            print(f"  {parent}:")
            for child in children:
                print(f"    -> {child}")
    
    def explore_file(self, file_path: str) -> None:
        """
        Main method to explore a Miradi .xmpz2 file.
        
        Args:
            file_path: Path to the .xmpz2 file to explore
        """
        try:
            file_path = Path(file_path)
            print(f"Exploring Miradi file: {file_path}")
            
            # Extract the file
            temp_dir = self.extract_xmpz2_file(file_path)
            
            try:
                # Find XML files
                xml_files = self.find_xml_files(temp_dir)
                
                if not xml_files:
                    print("No XML files found in the archive!")
                    return
                
                print(f"\nFound {len(xml_files)} XML file(s)")
                
                # Analyze each XML file
                for xml_file in xml_files:
                    self.analyze_xml_structure(xml_file)
                
                # Print summary
                self.print_structure_summary()
                
            finally:
                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir)
                print(f"\nCleaned up temporary directory: {temp_dir}")
                
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except zipfile.BadZipFile as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


def main():
    """Main entry point for the schema explorer."""
    parser = argparse.ArgumentParser(
        description="Explore the structure of Miradi .xmpz2 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python schema_explorer.py sample_project.xmpz2
    python schema_explorer.py /path/to/miradi/project.xmpz2
        """
    )
    
    parser.add_argument(
        "file_path",
        help="Path to the Miradi .xmpz2 file to explore"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Verbose mode enabled")
    
    # Create explorer and run
    explorer = MiradiSchemaExplorer()
    explorer.explore_file(args.file_path)


if __name__ == "__main__":
    main()
