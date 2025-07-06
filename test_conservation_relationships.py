#!/usr/bin/env python3
"""Test conservation relationships to ensure they connect actual conservation elements."""

from src.graph.neo4j_connection import Neo4jConnection
import os
from dotenv import load_dotenv

load_dotenv()

conn = Neo4jConnection(
    uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    user=os.getenv('NEO4J_USER', 'neo4j'),
    password=os.getenv('NEO4J_PASSWORD', 'password')
)

conn.connect()

print("🔍 TESTING CONSERVATION RELATIONSHIPS")
print("=" * 60)

# Test THREATENS relationships
print("\n1. THREATENS Relationships (THREAT → CONSERVATION_TARGET)")
result = conn.execute_query('''
MATCH (t:THREAT)-[r:THREATENS]->(ct:CONSERVATION_TARGET)
RETURN t.name as threat_name, ct.name as target_name, 
       t.node_type as threat_type, ct.node_type as target_type
LIMIT 5
''')

print(f"Found {len(result)} THREATENS relationships:")
for row in result:
    print(f"  {row['threat_name']} → {row['target_name']}")
    print(f"    Types: {row['threat_type']} → {row['target_type']}")

# Test MITIGATES relationships  
print("\n2. MITIGATES Relationships (STRATEGY → THREAT)")
result = conn.execute_query('''
MATCH (s:STRATEGY)-[r:MITIGATES]->(t:THREAT)
RETURN s.name as strategy_name, t.name as threat_name,
       s.node_type as strategy_type, t.node_type as threat_type
LIMIT 5
''')

print(f"Found {len(result)} MITIGATES relationships:")
for row in result:
    print(f"  {row['strategy_name']} → {row['threat_name']}")
    print(f"    Types: {row['strategy_type']} → {row['threat_type']}")

# Test IMPLEMENTS relationships
print("\n3. IMPLEMENTS Relationships (ACTIVITY → STRATEGY)")
result = conn.execute_query('''
MATCH (a:ACTIVITY)-[r:IMPLEMENTS]->(s:STRATEGY)
RETURN a.name as activity_name, s.name as strategy_name,
       a.node_type as activity_type, s.node_type as strategy_type
LIMIT 5
''')

print(f"Found {len(result)} IMPLEMENTS relationships:")
for row in result:
    print(f"  {row['activity_name']} → {row['strategy_name']}")
    print(f"    Types: {row['activity_type']} → {row['strategy_type']}")

# Check for any relationships involving DIAGRAM_FACTOR nodes (should be minimal)
print("\n4. Checking for DIAGRAM_FACTOR in conservation relationships")
result = conn.execute_query('''
MATCH (df:DIAGRAM_FACTOR)-[r:THREATENS|MITIGATES|IMPLEMENTS|CONTRIBUTES_TO|ENHANCES]-(other)
RETURN count(r) as diagram_factor_conservation_rels
''')

diagram_factor_rels = result[0]['diagram_factor_conservation_rels'] if result else 0
print(f"DIAGRAM_FACTOR nodes in conservation relationships: {diagram_factor_rels}")

if diagram_factor_rels > 0:
    print("⚠️  WARNING: DIAGRAM_FACTOR nodes should not be in conservation relationships!")
else:
    print("✅ GOOD: No DIAGRAM_FACTOR nodes in conservation relationships")

# Summary of all conservation relationships
print("\n5. Conservation Relationship Summary")
result = conn.execute_query('''
MATCH ()-[r:THREATENS|MITIGATES|IMPLEMENTS|CONTRIBUTES_TO|ENHANCES]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
''')

print("Conservation relationship counts:")
for row in result:
    print(f"  {row['relationship_type']}: {row['count']}")

conn.close()
print("\n✅ Conservation relationship test complete!")
