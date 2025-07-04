from src.etl import MiradiParser
import os
import sys
import time
from pathlib import Path

def test_all_projects():
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
    
    # Sort files for consistent output
    xmpz2_files.sort()
    
    print(f"🔍 Found {len(xmpz2_files)} Miradi projects to test")
    print("=" * 80)
    
    # Track overall statistics
    total_projects = len(xmpz2_files)
    successful_projects = 0
    failed_projects = 0
    total_elements = 0
    total_targets = 0
    total_strategies = 0
    total_activities = 0
    total_results_chains = 0
    total_conceptual_models = 0
    total_threats = 0
    
    project_results = []
    
    # Create parser once
    parser = MiradiParser()
    
    # Test each project
    for i, filename in enumerate(xmpz2_files, 1):
        file_path = os.path.join(sample_dir, filename)
        file_size = Path(file_path).stat().st_size / (1024 * 1024)  # Size in MB
        
        print(f"\n[{i}/{total_projects}] 🔍 Testing: {filename}")
        print(f"📁 Size: {file_size:.2f} MB")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Parse the project
            data = parser.parse_all(file_path)
            summary = parser.get_parsing_summary()
            
            # Extract counts
            targets_count = len(data.get('conservation_targets', []))
            strategies_count = len(data.get('strategies', []))
            activities_count = len(data.get('activities', []))
            results_chains_count = len(data.get('results_chains', []))
            conceptual_models_count = len(data.get('conceptual_models', []))
            threats_count = len(data.get('threats', []))
            
            parse_time = time.time() - start_time
            
            # Display results
            print(f"✅ Successfully parsed in {parse_time:.2f}s")
            print(f"📊 Total elements: {summary['total_elements']:,}")
            print(f"📈 Coverage: {summary['coverage']['known_element_coverage']:.1f}%")
            print(f"🎯 Conservation targets: {targets_count}")
            print(f"⚡ Strategies: {strategies_count}")
            print(f"📋 Activities: {activities_count}")
            print(f"🔗 Results chains: {results_chains_count}")
            print(f"🗺️  Conceptual models: {conceptual_models_count}")
            print(f"⚠️  Threats: {threats_count}")
            
            # Show element breakdown
            breakdown = summary['element_breakdown']
            print(f"📈 Element breakdown:")
            print(f"   • Must-support: {breakdown['must_support']:,} ({breakdown['must_support']/summary['total_elements']*100:.1f}%)")
            print(f"   • Should-support: {breakdown['should_support']:,} ({breakdown['should_support']/summary['total_elements']*100:.1f}%)")
            print(f"   • Optional: {breakdown['optional']:,} ({breakdown['optional']/summary['total_elements']*100:.1f}%)")
            print(f"   • Edge case: {breakdown['edge_case']:,} ({breakdown['edge_case']/summary['total_elements']*100:.1f}%)")
            print(f"   • Unknown: {breakdown['unknown']:,} ({breakdown['unknown']/summary['total_elements']*100:.1f}%)")
            
            # Show top elements
            top_elements = summary['top_elements']
            if top_elements:
                print(f"🔝 Top elements:")
                for elem, count in list(top_elements.items())[:5]:
                    print(f"   • {elem}: {count:,}")
            
            # Show unknown elements if any
            if summary['element_breakdown']['unknown'] > 0:
                print(f"❓ Unknown elements: {summary['element_breakdown']['unknown']}")
                unknown_list = list(summary['unknown_elements'])[:3]
                print(f"   Types: {', '.join(unknown_list)}")
                if len(summary['unknown_elements']) > 3:
                    print(f"   ... and {len(summary['unknown_elements']) - 3} more")
            
            # Track for summary
            successful_projects += 1
            total_elements += summary['total_elements']
            total_targets += targets_count
            total_strategies += strategies_count
            total_activities += activities_count
            total_results_chains += results_chains_count
            total_conceptual_models += conceptual_models_count
            total_threats += threats_count
            
            # Store result
            project_results.append({
                'filename': filename,
                'size_mb': file_size,
                'parse_time': parse_time,
                'success': True,
                'total_elements': summary['total_elements'],
                'coverage': summary['coverage']['known_element_coverage'],
                'targets': targets_count,
                'strategies': strategies_count,
                'activities': activities_count,
                'results_chains': results_chains_count,
                'conceptual_models': conceptual_models_count,
                'threats': threats_count,
                'unknown_elements': summary['element_breakdown']['unknown']
            })
            
        except Exception as e:
            parse_time = time.time() - start_time
            print(f"❌ Failed to parse in {parse_time:.2f}s")
            print(f"   Error: {str(e)}")
            
            failed_projects += 1
            
            # Store failed result
            project_results.append({
                'filename': filename,
                'size_mb': file_size,
                'parse_time': parse_time,
                'success': False,
                'error': str(e)
            })
    
    # Print overall summary
    print("\n" + "=" * 80)
    print("📊 OVERALL SUMMARY")
    print("=" * 80)
    
    print(f"📁 Projects tested: {total_projects}")
    print(f"✅ Successful: {successful_projects} ({successful_projects/total_projects*100:.1f}%)")
    print(f"❌ Failed: {failed_projects} ({failed_projects/total_projects*100:.1f}%)")
    
    if successful_projects > 0:
        print(f"\n📈 Aggregate Statistics:")
        print(f"📊 Total elements parsed: {total_elements:,}")
        print(f"🎯 Total conservation targets: {total_targets:,}")
        print(f"⚡ Total strategies: {total_strategies:,}")
        print(f"📋 Total activities: {total_activities:,}")
        print(f"🔗 Total results chains: {total_results_chains:,}")
        print(f"🗺️  Total conceptual models: {total_conceptual_models:,}")
        print(f"⚠️  Total threats: {total_threats:,}")
        
        print(f"\n📊 Averages per project:")
        print(f"📊 Elements: {total_elements/successful_projects:.0f}")
        print(f"🎯 Targets: {total_targets/successful_projects:.1f}")
        print(f"⚡ Strategies: {total_strategies/successful_projects:.1f}")
        print(f"📋 Activities: {total_activities/successful_projects:.1f}")
        print(f"🔗 Results chains: {total_results_chains/successful_projects:.1f}")
        print(f"🗺️  Conceptual models: {total_conceptual_models/successful_projects:.1f}")
        print(f"⚠️  Threats: {total_threats/successful_projects:.1f}")
    
    # Show project comparison table
    print(f"\n📋 PROJECT COMPARISON TABLE")
    print("-" * 120)
    print(f"{'Project':<35} {'Size(MB)':<8} {'Time(s)':<7} {'Elements':<8} {'Targets':<7} {'Strategies':<10} {'Activities':<10} {'Chains':<6} {'Models':<6} {'Threats':<7}")
    print("-" * 120)
    
    for result in project_results:
        if result['success']:
            print(f"{result['filename']:<35} {result['size_mb']:<8.2f} {result['parse_time']:<7.2f} {result['total_elements']:<8,} {result['targets']:<7} {result['strategies']:<10} {result['activities']:<10} {result['results_chains']:<6} {result['conceptual_models']:<6} {result['threats']:<7}")
        else:
            print(f"{result['filename']:<35} {result['size_mb']:<8.2f} {result['parse_time']:<7.2f} {'FAILED':<8} {'—':<7} {'—':<10} {'—':<10} {'—':<6} {'—':<6} {'—':<7}")
    
    # Performance insights
    if successful_projects > 0:
        successful_results = [r for r in project_results if r['success']]
        avg_parse_time = sum(r['parse_time'] for r in successful_results) / len(successful_results)
        fastest = min(successful_results, key=lambda x: x['parse_time'])
        slowest = max(successful_results, key=lambda x: x['parse_time'])
        largest = max(successful_results, key=lambda x: x['total_elements'])
        
        print(f"\n⚡ PERFORMANCE INSIGHTS")
        print("-" * 60)
        print(f"⏱️  Average parse time: {avg_parse_time:.2f}s")
        print(f"🏃 Fastest: {fastest['filename']} ({fastest['parse_time']:.2f}s)")
        print(f"🐌 Slowest: {slowest['filename']} ({slowest['parse_time']:.2f}s)")
        print(f"📊 Largest: {largest['filename']} ({largest['total_elements']:,} elements)")
        
        # Elements per second
        total_time = sum(r['parse_time'] for r in successful_results)
        elements_per_second = total_elements / total_time if total_time > 0 else 0
        print(f"🚀 Processing rate: {elements_per_second:,.0f} elements/second")
    
    print(f"\n🎉 Testing complete!")
    
    if failed_projects > 0:
        print(f"\n⚠️  {failed_projects} project(s) failed to parse. Check error messages above.")
        return 1
    else:
        print(f"✅ All {successful_projects} projects parsed successfully!")
        return 0

if __name__ == "__main__":
    exit_code = test_all_projects()
    sys.exit(exit_code)
