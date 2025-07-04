from src.etl import MiradiParser
import os
import sys

def test_parser():
    # Check if sample projects directory exists
    sample_dir = "data/sample_projects"
    if not os.path.exists(sample_dir):
        print(f"❌ Error: {sample_dir} directory not found")
        return
    
    # Get list of .xmpz2 files
    xmpz2_files = [f for f in os.listdir(sample_dir) if f.endswith('.xmpz2')]
    
    if not xmpz2_files:
        print(f"❌ Error: No .xmpz2 files found in {sample_dir}")
        return
    
    # Test with the first project
    test_file = os.path.join(sample_dir, xmpz2_files[0])
    print(f"🔍 Testing with: {xmpz2_files[0]}")
    print("-" * 50)
    
    # Parse the project
    parser = MiradiParser()
    try:
        data = parser.parse_all(test_file)
        summary = parser.get_parsing_summary()
        
        print(f"✅ Successfully parsed project")
        print(f"📊 Total elements: {summary['total_elements']}")
        print(f"📈 Coverage: {summary['coverage']['known_element_coverage']:.1f}%")
        print(f"🎯 Conservation targets: {len(data.get('conservation_targets', []))}")
        print(f"⚡ Strategies: {len(data.get('strategies', []))}")
        print(f"📋 Activities: {len(data.get('activities', []))}")
        print(f"🔗 Results chains: {len(data.get('results_chains', []))}")
        print(f"🗺️  Conceptual models: {len(data.get('conceptual_models', []))}")
        
        # Show unknown elements if any
        if summary['element_breakdown']['unknown'] > 0:
            print(f"\n⚠️  Unknown elements found: {summary['element_breakdown']['unknown']}")
            print("Unknown element types:", ", ".join(list(summary['unknown_elements'])[:5]))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
