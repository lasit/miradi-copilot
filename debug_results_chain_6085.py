#!/usr/bin/env python3
"""Debug results chain 6085 to understand why CONTAINS relationships aren't being created."""

from src.graph.neo4j_connection import Neo4jConnection
import os
from dotenv import load_dotenv

load_dotenv()

def debug_results_chain_6085():
    """Debug the specific results chain 6085 to understand the missing CONTAINS relationships."""
    
    conn = Neo4jConnection(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    conn.connect()
    
    print("🔍 DEBUGGING RESULTS CHAIN 6085 - VISITOR MANAGEMENT")
    print("=" * 70)
    
    # 1. Check if results chain exists
    print("\n1. RESULTS CHAIN EXISTENCE CHECK")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: '6085'})
    RETURN rc.id, rc.name, rc.details, keys(rc) as properties
    ''')
    
    if result:
        rc = result[0]
        print(f"✅ Results Chain Found: {rc['rc.name']} (ID: {rc['rc.id']})")
        print(f"   Properties: {rc['properties']}")
    else:
        print("❌ Results Chain 6085 not found!")
        return
    
    # 2. Check for diagram_factor_ids property
    print("\n2. DIAGRAM FACTOR IDS PROPERTY CHECK")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: '6085'})
    RETURN rc.diagram_factor_ids
    ''')
    
    if result:
        diagram_factor_ids = result[0]['rc.diagram_factor_ids']
        print(f"   diagram_factor_ids property: {diagram_factor_ids}")
        
        if diagram_factor_ids and diagram_factor_ids != '[]':
            print("✅ Results chain has diagram_factor_ids")
        else:
            print("❌ Results chain has empty or missing diagram_factor_ids")
    
    # 3. Look for diagram factors that might belong to this results chain
    print("\n3. SEARCH FOR RELATED DIAGRAM FACTORS")
    result = conn.execute_query('''
    MATCH (df:DIAGRAM_FACTOR)
    OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
    WITH df, element
    WHERE element.name CONTAINS 'Visitor' OR element.name CONTAINS 'Management'
       OR df.wrapped_factor_id STARTS WITH '6085'
       OR df.wrapped_factor_id CONTAINS '6085'
    RETURN df.id, df.wrapped_factor_id, element.name, labels(element)[0] as element_type
    ORDER BY df.id
    LIMIT 10
    ''')
    
    print(f"   Found {len(result)} potentially related diagram factors:")
    for row in result:
        print(f"   • DF {row['df.id']} wraps {row['df.wrapped_factor_id']} ({row['element_type']}) - {row['element.name']}")
    
    # 4. Check for elements that might belong to visitor management
    print("\n4. SEARCH FOR VISITOR MANAGEMENT ELEMENTS")
    result = conn.execute_query('''
    MATCH (n)
    WHERE n.name CONTAINS 'Visitor' OR n.name CONTAINS 'Management'
    RETURN labels(n)[0] as type, n.id, n.name
    ORDER BY type, n.name
    ''')
    
    print(f"   Found {len(result)} elements with 'Visitor' or 'Management' in name:")
    for row in result:
        print(f"   • {row['type']} {row['n.id']}: {row['n.name']}")
    
    # 5. Check if there are any CONTAINS relationships at all
    print("\n5. CONTAINS RELATIONSHIPS CHECK")
    result = conn.execute_query('''
    MATCH (source)-[r:CONTAINS]->(target)
    RETURN labels(source)[0] as source_type, source.id, source.name,
           labels(target)[0] as target_type, target.id
    ORDER BY source_type, source.id
    LIMIT 10
    ''')
    
    if result:
        print(f"   Found {len(result)} CONTAINS relationships (showing first 10):")
        for row in result:
            print(f"   • {row['source_type']} {row['source.id']} CONTAINS {row['target_type']} {row['target.id']}")
    else:
        print("   ❌ NO CONTAINS relationships found in entire database!")
    
    # 6. Check results chain properties in detail
    print("\n6. DETAILED RESULTS CHAIN PROPERTIES")
    result = conn.execute_query('''
    MATCH (rc:RESULTS_CHAIN {id: '6085'})
    RETURN rc
    ''')
    
    if result:
        rc_props = result[0]['rc']
        print("   All properties:")
        for key, value in rc_props.items():
            print(f"     {key}: {value}")
    
    # 7. Alternative approach - find elements by proximity or pattern
    print("\n7. ALTERNATIVE ELEMENT DISCOVERY")
    result = conn.execute_query('''
    // Look for elements with IDs that might be related to 6085
    MATCH (n)
    WHERE n.id STARTS WITH '6' AND toInteger(n.id) > 6080 AND toInteger(n.id) < 6090
    RETURN labels(n)[0] as type, n.id, n.name
    ORDER BY toInteger(n.id)
    ''')
    
    print(f"   Elements with IDs near 6085:")
    for row in result:
        print(f"   • {row['type']} {row['n.id']}: {row['n.name']}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSIS SUMMARY:")
    print("If diagram_factor_ids is empty, the parser didn't extract the factor IDs correctly.")
    print("If no CONTAINS relationships exist, the schema mapper didn't create them.")
    print("This will help us identify where the issue is in the pipeline.")

if __name__ == "__main__":
    debug_results_chain_6085()
