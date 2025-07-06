#!/usr/bin/env python3
"""
Analyze Results Chain Factors and Relationships

This script provides a comprehensive analysis of what factors are contained in a results chain
and how they relate to each other, helping verify that the parser is extracting all required
conservation elements and relationships correctly.
"""

from src.graph.neo4j_connection import Neo4jConnection
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_results_chain_factors(chain_id='6085'):
    """Analyze all factors and relationships in a specific results chain."""
    
    conn = Neo4jConnection(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    conn.connect()
    
    print(f"🔍 COMPREHENSIVE RESULTS CHAIN ANALYSIS - CHAIN {chain_id}")
    print("=" * 80)
    
    # 1. Basic Results Chain Info
    print("\n1. RESULTS CHAIN OVERVIEW")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})
    RETURN rc.id, rc.name, rc.identifier, rc.details
    ''', {'chain_id': chain_id})
    
    if result:
        rc = result[0]
        print(f"   ID: {rc['rc.id']}")
        print(f"   Name: {rc['rc.name']}")
        print(f"   Identifier: {rc['rc.identifier']}")
        print(f"   Details: {rc['rc.details']}")
    else:
        print(f"   ❌ Results Chain {chain_id} not found!")
        return
    
    # 2. Element Type Breakdown
    print("\n2. ELEMENT TYPE BREAKDOWN")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (element) WHERE element.id = df.wrapped_factor_id
    RETURN labels(element)[0] as element_type, 
           count(*) as count,
           collect(element.name)[0..3] as sample_names
    ORDER BY count DESC
    ''', {'chain_id': chain_id})
    
    total_elements = 0
    for row in result:
        count = row['count']
        total_elements += count
        sample_names = [name for name in row['sample_names'] if name]
        print(f"   • {row['element_type']}: {count} elements")
        if sample_names:
            print(f"     Examples: {', '.join(sample_names[:2])}")
    
    print(f"\n   📊 Total Elements: {total_elements}")
    
    # 3. Conservation Targets Analysis
    print("\n3. CONSERVATION TARGETS")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (target:CONSERVATION_TARGET) WHERE target.id = df.wrapped_factor_id
    RETURN target.id, target.name, target.viability_status
    ORDER BY target.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Conservation Targets:")
        for row in result:
            print(f"   • {row['target.id']}: {row['target.name']}")
            if row['target.viability_status']:
                print(f"     Viability: {row['target.viability_status']}")
    else:
        print("   ❌ No Conservation Targets found in this results chain")
    
    # 4. Threats Analysis
    print("\n4. THREATS")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (threat:THREAT) WHERE threat.id = df.wrapped_factor_id
    RETURN threat.id, threat.name, threat.is_direct_threat
    ORDER BY threat.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Threats:")
        for row in result:
            threat_type = "Direct" if row['threat.is_direct_threat'] == 'true' else "Contributing Factor"
            print(f"   • {row['threat.id']}: {row['threat.name']} ({threat_type})")
    else:
        print("   ❌ No Threats found in this results chain")
    
    # 5. Strategies Analysis
    print("\n5. STRATEGIES")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (strategy:STRATEGY) WHERE strategy.id = df.wrapped_factor_id
    OPTIONAL MATCH (strategy)<-[:IMPLEMENTS]-(activity:ACTIVITY)
    RETURN strategy.id, strategy.name, strategy.status,
           count(DISTINCT activity) as activity_count
    ORDER BY strategy.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Strategies:")
        for row in result:
            print(f"   • {row['strategy.id']}: {row['strategy.name']}")
            if row['strategy.status']:
                print(f"     Status: {row['strategy.status']}")
            print(f"     Activities: {row['activity_count']}")
    else:
        print("   ❌ No Strategies found in this results chain")
    
    # 6. Activities Analysis
    print("\n6. ACTIVITIES")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (activity:ACTIVITY) WHERE activity.id = df.wrapped_factor_id
    OPTIONAL MATCH (activity)-[:IMPLEMENTS]->(strategy:STRATEGY)
    RETURN activity.id, activity.name, activity.identifier,
           strategy.name as implements_strategy
    ORDER BY activity.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Activities:")
        for row in result:
            print(f"   • {row['activity.id']}: {row['activity.name']}")
            if row['activity.identifier']:
                print(f"     Identifier: {row['activity.identifier']}")
            if row['implements_strategy']:
                print(f"     Implements: {row['implements_strategy']}")
    else:
        print("   ❌ No Activities found in this results chain")
    
    # 7. Intermediate Results Analysis
    print("\n7. INTERMEDIATE RESULTS")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (result:INTERMEDIATE_RESULT) WHERE result.id = df.wrapped_factor_id
    RETURN result.id, result.name, result.details
    ORDER BY result.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Intermediate Results:")
        for row in result:
            print(f"   • {row['result.id']}: {row['result.name']}")
            if row['result.details']:
                print(f"     Details: {row['result.details'][:100]}...")
    else:
        print("   ❌ No Intermediate Results found in this results chain")
    
    # 8. Threat Reduction Results Analysis
    print("\n8. THREAT REDUCTION RESULTS")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (trr:THREAT_REDUCTION_RESULT) WHERE trr.id = df.wrapped_factor_id
    RETURN trr.id, trr.name, trr.details
    ORDER BY trr.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Threat Reduction Results:")
        for row in result:
            print(f"   • {row['trr.id']}: {row['trr.name']}")
            if row['trr.details']:
                print(f"     Details: {row['trr.details'][:100]}...")
    else:
        print("   ❌ No Threat Reduction Results found in this results chain")
    
    # 9. Indicators Analysis
    print("\n9. INDICATORS")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (indicator:INDICATOR) WHERE indicator.id = df.wrapped_factor_id
    OPTIONAL MATCH (indicator)-[:MEASURES]->(measured)
    RETURN indicator.id, indicator.name, 
           collect(DISTINCT labels(measured)[0]) as measures_types
    ORDER BY indicator.name
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Indicators:")
        for row in result:
            print(f"   • {row['indicator.id']}: {row['indicator.name']}")
            if row['measures_types'] and row['measures_types'] != [None]:
                print(f"     Measures: {', '.join(row['measures_types'])}")
    else:
        print("   ❌ No Indicators found in this results chain")
    
    # 10. Conservation Relationships Analysis
    print("\n10. CONSERVATION RELATIONSHIPS WITHIN RESULTS CHAIN")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (element) WHERE element.id = df.wrapped_factor_id
    WITH collect(DISTINCT element.id) as chain_element_ids
    
    MATCH (source)-[rel:IMPLEMENTS|MITIGATES|THREATENS|CONTRIBUTES_TO|ENHANCES|MEASURES]-(target)
    WHERE source.id IN chain_element_ids AND target.id IN chain_element_ids
    
    RETURN type(rel) as relationship_type,
           count(*) as count,
           collect(DISTINCT labels(source)[0])[0..3] as source_types,
           collect(DISTINCT labels(target)[0])[0..3] as target_types
    ORDER BY count DESC
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {sum(row['count'] for row in result)} relationships:")
        for row in result:
            print(f"   • {row['relationship_type']}: {row['count']} relationships")
            print(f"     From: {', '.join(row['source_types'])}")
            print(f"     To: {', '.join(row['target_types'])}")
    else:
        print("   ❌ No conservation relationships found within this results chain")
    
    # 11. Theory of Change Pathways
    print("\n11. THEORY OF CHANGE PATHWAYS")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: $chain_id})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
    MATCH (element) WHERE element.id = df.wrapped_factor_id
    WITH collect(DISTINCT element.id) as chain_element_ids
    
    // Find Strategy -> Target pathways
    MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
    WHERE strategy.id IN chain_element_ids 
      AND threat.id IN chain_element_ids 
      AND target.id IN chain_element_ids
    
    RETURN strategy.name as strategy_name,
           threat.name as threat_name,
           target.name as target_name
    LIMIT 5
    ''', {'chain_id': chain_id})
    
    if result:
        print(f"   Found {len(result)} Strategy-Threat-Target pathways:")
        for row in result:
            print(f"   • {row['strategy_name']} → mitigates → {row['threat_name']} → threatens → {row['target_name']}")
    else:
        print("   ❌ No complete Strategy-Threat-Target pathways found")
    
    # 12. Missing Elements Check
    print("\n12. MISSING ELEMENTS CHECK")
    
    # Check for elements that should be in results chains but aren't parsed
    missing_checks = [
        ("OBJECTIVE", "Objectives"),
        ("GOAL", "Goals"),
        ("KEY_ECOLOGICAL_ATTRIBUTE", "Key Ecological Attributes"),
        ("STRESS", "Stresses"),
        ("BIOPHYSICAL_FACTOR", "Biophysical Factors"),
        ("BIOPHYSICAL_RESULT", "Biophysical Results")
    ]
    
    for node_type, description in missing_checks:
        result = conn.execute_query(f'''
        MATCH (rc:RESULTS_CHAIN {{id: $chain_id}})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
        MATCH (element:{node_type}) WHERE element.id = df.wrapped_factor_id
        RETURN count(element) as count
        ''', {'chain_id': chain_id})
        
        count = result[0]['count'] if result else 0
        if count > 0:
            print(f"   ✅ {description}: {count} found")
        else:
            print(f"   ⚠️  {description}: None found (may not exist in this chain)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("🎯 ANALYSIS SUMMARY:")
    print("This analysis shows all conservation elements and relationships")
    print("within the results chain. Use this to verify that the parser is")
    print("extracting all required factors for complete conservation planning.")

if __name__ == "__main__":
    analyze_results_chain_factors()
