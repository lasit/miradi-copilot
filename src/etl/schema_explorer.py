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
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import glob


class MiradiSchemaExplorer:
    """Explores the structure of Miradi .xmpz2 files."""
    
    def __init__(self):
        self.element_counts = Counter()
        self.element_attributes = defaultdict(set)
        self.element_hierarchy = defaultdict(set)
        self.xml_files_found = []
        self.processed_files = []
        self.file_element_presence = defaultdict(set)  # Track which files contain each element
    
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
    
    def analyze_file_for_batch(self, file_path: Path) -> None:
        """
        Analyze a single file as part of batch processing.
        
        Args:
            file_path: Path to the .xmpz2 file to analyze
        """
        current_file_elements = set()
        
        try:
            print(f"Processing: {file_path.name}")
            
            # Extract the file
            temp_dir = self.extract_xmpz2_file(file_path)
            
            try:
                # Find XML files
                xml_files = self.find_xml_files(temp_dir)
                
                if not xml_files:
                    print(f"  No XML files found in {file_path.name}")
                    return
                
                # Analyze each XML file
                for xml_file in xml_files:
                    self._analyze_xml_for_batch(xml_file, current_file_elements)
                
                # Track which elements appear in this file
                for element in current_file_elements:
                    self.file_element_presence[element].add(file_path.name)
                
                self.processed_files.append(file_path.name)
                print(f"  Found {len(current_file_elements)} unique elements")
                
            finally:
                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")
    
    def _analyze_xml_for_batch(self, xml_file: Path, current_file_elements: set) -> None:
        """
        Analyze XML structure for batch processing.
        
        Args:
            xml_file: Path to the XML file to analyze
            current_file_elements: Set to track elements in current file
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Recursively analyze all elements
            self._analyze_element_for_batch(root, current_file_elements, parent_tag=None)
            
        except ET.ParseError as e:
            print(f"    Error parsing XML file {xml_file.name}: {e}")
        except Exception as e:
            print(f"    Unexpected error analyzing {xml_file.name}: {e}")
    
    def _analyze_element_for_batch(self, element: ET.Element, current_file_elements: set, parent_tag: str = None) -> None:
        """
        Recursively analyze an XML element for batch processing.
        
        Args:
            element: The XML element to analyze
            current_file_elements: Set to track elements in current file
            parent_tag: Tag name of the parent element
        """
        tag = element.tag
        
        # Track element in current file
        current_file_elements.add(tag)
        
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
            self._analyze_element_for_batch(child, current_file_elements, parent_tag=tag)
    
    def process_directory(self, directory_path: str) -> None:
        """
        Process all .xmpz2 files in a directory.
        
        Args:
            directory_path: Path to directory containing .xmpz2 files
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        # Find all .xmpz2 files
        xmpz2_files = list(directory.glob("*.xmpz2"))
        
        if not xmpz2_files:
            print(f"No .xmpz2 files found in {directory}")
            return
        
        print(f"Found {len(xmpz2_files)} .xmpz2 files to process")
        
        # Process each file
        for file_path in xmpz2_files:
            self.analyze_file_for_batch(file_path)
        
        print(f"\nCompleted processing {len(self.processed_files)} files")
    
    def generate_markdown_report(self, output_path: str = "docs/discovered_schema.md") -> None:
        """
        Generate a comprehensive markdown report of discovered schema.
        
        Args:
            output_path: Path where to save the markdown report
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        total_files = len(self.processed_files)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Miradi Schema Discovery Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Files Processed:** {total_files}\n")
            f.write(f"- **Unique Element Types:** {len(self.element_counts)}\n")
            f.write(f"- **Total Element Instances:** {sum(self.element_counts.values())}\n\n")
            
            if self.processed_files:
                f.write("### Processed Files\n\n")
                for file_name in sorted(self.processed_files):
                    f.write(f"- {file_name}\n")
                f.write("\n")
            
            # Element frequency table
            f.write("## Element Frequency\n\n")
            f.write("| Element | Count | Files Present | Universality |\n")
            f.write("|---------|-------|---------------|-------------|\n")
            
            for element, count in self.element_counts.most_common():
                files_with_element = len(self.file_element_presence[element])
                universality = "All" if files_with_element == total_files else f"{files_with_element}/{total_files}"
                f.write(f"| `{element}` | {count} | {files_with_element} | {universality} |\n")
            
            f.write("\n")
            
            # Universal vs Partial elements
            if total_files > 1:
                universal_elements = [elem for elem in self.element_counts.keys() 
                                    if len(self.file_element_presence[elem]) == total_files]
                partial_elements = [elem for elem in self.element_counts.keys() 
                                  if len(self.file_element_presence[elem]) < total_files]
                
                f.write("## Element Distribution\n\n")
                f.write(f"### Universal Elements ({len(universal_elements)})\n")
                f.write("Elements that appear in ALL processed files:\n\n")
                for element in sorted(universal_elements):
                    f.write(f"- `{element}`\n")
                f.write("\n")
                
                f.write(f"### Partial Elements ({len(partial_elements)})\n")
                f.write("Elements that appear in SOME but not all files:\n\n")
                for element in sorted(partial_elements):
                    files_with_element = len(self.file_element_presence[element])
                    f.write(f"- `{element}` (in {files_with_element}/{total_files} files)\n")
                f.write("\n")
            
            # Element details
            f.write("## Element Details\n\n")
            
            for element in sorted(self.element_counts.keys()):
                f.write(f"### `{element}`\n\n")
                f.write(f"- **Occurrences:** {self.element_counts[element]}\n")
                
                if total_files > 1:
                    files_with_element = len(self.file_element_presence[element])
                    f.write(f"- **Present in:** {files_with_element}/{total_files} files\n")
                    if files_with_element < total_files:
                        file_list = sorted(self.file_element_presence[element])
                        f.write(f"- **Files:** {', '.join(file_list)}\n")
                
                # Attributes
                if element in self.element_attributes and self.element_attributes[element]:
                    attrs = sorted(self.element_attributes[element])
                    f.write(f"- **Attributes:** {', '.join(f'`{attr}`' for attr in attrs)}\n")
                else:
                    f.write("- **Attributes:** None\n")
                
                # Parent elements
                parents = [parent for parent, children in self.element_hierarchy.items() 
                          if element in children]
                if parents:
                    f.write(f"- **Parent Elements:** {', '.join(f'`{parent}`' for parent in sorted(parents))}\n")
                
                # Child elements
                if element in self.element_hierarchy:
                    children = sorted(self.element_hierarchy[element])
                    f.write(f"- **Child Elements:** {', '.join(f'`{child}`' for child in children)}\n")
                
                f.write("\n")
            
            # Hierarchy visualization
            f.write("## Element Hierarchy\n\n")
            f.write("Parent-child relationships discovered:\n\n")
            
            for parent in sorted(self.element_hierarchy.keys()):
                children = sorted(self.element_hierarchy[parent])
                f.write(f"- `{parent}`\n")
                for child in children:
                    f.write(f"  - `{child}`\n")
            
            f.write("\n")
            
            # Attributes summary
            f.write("## Attribute Summary\n\n")
            f.write("All attributes found across all elements:\n\n")
            
            all_attributes = set()
            for attrs in self.element_attributes.values():
                all_attributes.update(attrs)
            
            for attr in sorted(all_attributes):
                elements_with_attr = [elem for elem, attrs in self.element_attributes.items() 
                                    if attr in attrs]
                f.write(f"- `{attr}`: Used by {', '.join(f'`{elem}`' for elem in sorted(elements_with_attr))}\n")
        
        print(f"Markdown report saved to: {output_file}")
    
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
    # Single file exploration
    python schema_explorer.py sample_project.xmpz2
    
    # Directory batch processing with markdown report
    python schema_explorer.py --directory /path/to/miradi/files --report
    
    # Custom report output location
    python schema_explorer.py --directory ./data --report --output custom_report.md
        """
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to the Miradi .xmpz2 file or directory (when using --directory)"
    )
    
    parser.add_argument(
        "--directory", "-d",
        action="store_true",
        help="Process all .xmpz2 files in the specified directory"
    )
    
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Generate markdown report (automatically enabled for directory processing)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="docs/discovered_schema.md",
        help="Output path for markdown report (default: docs/discovered_schema.md)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if not args.path:
        parser.error("Path argument is required")
    
    if args.verbose:
        print("Verbose mode enabled")
    
    # Create explorer
    explorer = MiradiSchemaExplorer()
    
    try:
        if args.directory:
            # Process directory
            print(f"Processing directory: {args.path}")
            explorer.process_directory(args.path)
            
            # Always generate report for directory processing
            if explorer.processed_files:
                explorer.generate_markdown_report(args.output)
            else:
                print("No files were processed, skipping report generation")
        
        else:
            # Process single file
            explorer.explore_file(args.path)
            
            # Generate report if requested
            if args.report:
                # For single file, we need to set up the processed_files list
                explorer.processed_files = [Path(args.path).name]
                explorer.generate_markdown_report(args.output)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
