#!/usr/bin/env python3
"""Test the main inspection queries against the current Neo4j database."""

from src.graph.neo4j_connection import Neo4jConnection
import os
from dotenv import load_dotenv
import json

load_dotenv()

def test_project_overview():
    """Test the main project overview query."""
    
    conn = Neo4jConnection(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    conn.connect()
    
    print("🔍 TESTING PROJECT OVERVIEW QUERY")
    print("=" * 60)
    
    # Main project overview query (fixed for Cypher aggregation rules)
    query = """
    MATCH (p:PROJECT {id: 'current_project'})
    WITH p.name as project_name, p.filename as filename, p.loaded_at as loaded_at, 
         p.file_path as file_path, p.schema_coverage as schema_coverage, p.load_time as load_time

    OPTIONAL MATCH (target:CONSERVATION_TARGET)
    OPTIONAL MATCH (threat:THREAT)
    OPTIONAL MATCH (strategy:STRATEGY)
    OPTIONAL MATCH (activity:ACTIVITY)
    OPTIONAL MATCH (indicator:INDICATOR)
    OPTIONAL MATCH (rc:RESULTS_CHAIN)

    RETURN {
        project_info: {
            name: project_name,
            filename: filename,
            loaded_at: loaded_at,
            file_path: file_path,
            schema_coverage: schema_coverage,
            load_time: load_time
        },
        
        element_counts: {
            conservation_targets: count(DISTINCT target),
            threats: count(DISTINCT threat),
            strategies: count(DISTINCT strategy),
            activities: count(DISTINCT activity),
            indicators: count(DISTINCT indicator),
            results_chains: count(DISTINCT rc)
        },
        
        conservation_targets: collect(DISTINCT {
            id: target.id, 
            name: target.name,
            viability_status: target.viability_status
        }),
        
        indicators: collect(DISTINCT {
            id: indicator.id, 
            name: indicator.name,
            measurement_type: indicator.measurement_type
        }),
        
        results_chains: collect(DISTINCT {
            id: rc.id, 
            name: rc.name,
            description: rc.details
        })
    } AS project_overview
    """
    
    try:
        result = conn.execute_query(query)
        
        if result:
            overview = result[0]['project_overview']
            
            # Display project info
            project_info = overview['project_info']
            print("📁 PROJECT INFORMATION:")
            print(f"   Name: {project_info['name']}")
            print(f"   Filename: {project_info['filename']}")
            print(f"   Loaded: {project_info['loaded_at']}")
            print(f"   Schema Coverage: {project_info['schema_coverage']}%")
            print(f"   Load Time: {project_info['load_time']}s")
            
            # Display element counts
            counts = overview['element_counts']
            print(f"\n📊 ELEMENT COUNTS:")
            print(f"   Conservation Targets: {counts['conservation_targets']}")
            print(f"   Threats: {counts['threats']}")
            print(f"   Strategies: {counts['strategies']}")
            print(f"   Activities: {counts['activities']}")
            print(f"   Indicators: {counts['indicators']}")
            print(f"   Results Chains: {counts['results_chains']}")
            
            # Display conservation targets
            targets = overview['conservation_targets']
            print(f"\n🎯 CONSERVATION TARGETS ({len(targets)}):")
            for target in targets[:5]:  # Show first 5
                if target['id']:  # Filter out null entries
                    print(f"   • {target['name']} (ID: {target['id']})")
            if len(targets) > 5:
                print(f"   ... and {len(targets) - 5} more")
            
            # Display indicators
            indicators = overview['indicators']
            valid_indicators = [i for i in indicators if i['id']]
            print(f"\n📈 INDICATORS ({len(valid_indicators)}):")
            for indicator in valid_indicators[:5]:  # Show first 5
                print(f"   • {indicator['name']} (ID: {indicator['id']})")
            if len(valid_indicators) > 5:
                print(f"   ... and {len(valid_indicators) - 5} more")
            
            # Display results chains
            chains = overview['results_chains']
            valid_chains = [c for c in chains if c['id']]
            print(f"\n🔗 RESULTS CHAINS ({len(valid_chains)}):")
            for chain in valid_chains[:5]:  # Show first 5
                print(f"   • {chain['name']} (ID: {chain['id']})")
            if len(valid_chains) > 5:
                print(f"   ... and {len(valid_chains) - 5} more")
            
            print("\n✅ Project overview query successful!")
            
        else:
            print("❌ No results returned - check if project is loaded")
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    finally:
        conn.close()

def test_spatial_coverage():
    """Test spatial data coverage query."""
    
    conn = Neo4jConnection(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    conn.connect()
    
    print("\n🗺️  TESTING SPATIAL DATA COVERAGE")
    print("=" * 60)
    
    query = """
    MATCH (df:DIAGRAM_FACTOR)
    WITH df,
         CASE WHEN df.location <> '{}' AND df.location IS NOT NULL THEN 1 ELSE 0 END as has_location,
         CASE WHEN df.size <> '{}' AND df.size IS NOT NULL THEN 1 ELSE 0 END as has_size
    RETURN {
        total_diagram_factors: count(df),
        factors_with_location: sum(has_location),
        factors_with_size: sum(has_size),
        spatial_coverage_percent: round(100.0 * sum(has_location) / count(df), 1),
        size_coverage_percent: round(100.0 * sum(has_size) / count(df), 1)
    } AS spatial_coverage
    """
    
    try:
        result = conn.execute_query(query)
        
        if result:
            coverage = result[0]['spatial_coverage']
            print(f"📊 SPATIAL DATA COVERAGE:")
            print(f"   Total Diagram Factors: {coverage['total_diagram_factors']}")
            print(f"   Factors with Location: {coverage['factors_with_location']}")
            print(f"   Factors with Size: {coverage['factors_with_size']}")
            print(f"   Spatial Coverage: {coverage['spatial_coverage_percent']}%")
            print(f"   Size Coverage: {coverage['size_coverage_percent']}%")
            
            if coverage['spatial_coverage_percent'] == 100.0:
                print("   ✅ Perfect spatial data coverage!")
            elif coverage['spatial_coverage_percent'] > 80.0:
                print("   ✅ Good spatial data coverage")
            else:
                print("   ⚠️  Limited spatial data coverage")
                
        else:
            print("❌ No spatial data found")
            
    except Exception as e:
        print(f"❌ Spatial query failed: {e}")
    
    finally:
        conn.close()

def test_relationship_summary():
    """Test relationship summary query."""
    
    conn = Neo4jConnection(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    conn.connect()
    
    print("\n🔗 TESTING RELATIONSHIP SUMMARY")
    print("=" * 60)
    
    query = """
    MATCH ()-[r]->()
    RETURN type(r) as relationship_type, count(r) as count
    ORDER BY count DESC
    """
    
    try:
        result = conn.execute_query(query)
        
        if result:
            print("📊 RELATIONSHIP BREAKDOWN:")
            total_relationships = sum(row['count'] for row in result)
            
            for row in result:
                rel_type = row['relationship_type']
                count = row['count']
                percentage = (count / total_relationships) * 100
                print(f"   • {rel_type}: {count} ({percentage:.1f}%)")
            
            print(f"\n   Total Relationships: {total_relationships}")
            print("   ✅ Relationship summary successful!")
            
        else:
            print("❌ No relationships found")
            
    except Exception as e:
        print(f"❌ Relationship query failed: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🧪 TESTING CYPHER INSPECTION QUERIES")
    print("=" * 60)
    print("Testing key queries from cypher_inspection_queries.cypher")
    print()
    
    test_project_overview()
    test_spatial_coverage()
    test_relationship_summary()
    
    print("\n" + "=" * 60)
    print("🎉 Testing complete!")
    print("\nNext steps:")
    print("1. Copy queries from cypher_inspection_queries.cypher")
    print("2. Paste into Neo4j Browser for interactive exploration")
    print("3. Modify queries as needed for your analysis")
