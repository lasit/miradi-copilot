#!/usr/bin/env python3
"""Test spatial data extraction from diagram factors."""

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

print("🗺️  TESTING SPATIAL DATA EXTRACTION")
print("=" * 60)

# Test 1: Check if diagram factors have location and size data
print("\n1. Checking Diagram Factor Spatial Properties")
result = conn.execute_query('''
MATCH (df:DIAGRAM_FACTOR)
RETURN df.id as factor_id, df.location as location, df.size as size
ORDER BY df.id
LIMIT 10
''')

print(f"Found {len(result)} diagram factors with spatial data:")
for row in result:
    print(f"  Factor {row['factor_id']}: location={row['location']}, size={row['size']}")

# Test 2: Count factors with actual coordinates vs defaults
print("\n2. Spatial Data Statistics")
result = conn.execute_query('''
MATCH (df:DIAGRAM_FACTOR)
WHERE df.location IS NOT NULL AND df.size IS NOT NULL
RETURN 
    count(df) as total_factors,
    sum(CASE WHEN df.location = '[0.0, 0.0]' THEN 1 ELSE 0 END) as default_locations,
    sum(CASE WHEN df.size = '[100.0, 50.0]' THEN 1 ELSE 0 END) as default_sizes,
    sum(CASE WHEN df.location <> '[0.0, 0.0]' THEN 1 ELSE 0 END) as actual_locations,
    sum(CASE WHEN df.size <> '[100.0, 50.0]' THEN 1 ELSE 0 END) as actual_sizes
''')

if result:
    stats = result[0]
    print(f"Total diagram factors: {stats['total_factors']}")
    print(f"Factors with actual coordinates: {stats['actual_locations']}")
    print(f"Factors using default coordinates: {stats['default_locations']}")
    print(f"Factors with actual sizes: {stats['actual_sizes']}")
    print(f"Factors using default sizes: {stats['default_sizes']}")

# Test 3: Show some examples of actual spatial data
print("\n3. Examples of Actual Spatial Coordinates")
result = conn.execute_query('''
MATCH (df:DIAGRAM_FACTOR)
WHERE df.location <> '[0.0, 0.0]' OR df.size <> '[100.0, 50.0]'
RETURN df.id as factor_id, df.location as location, df.size as size, df.wrapped_factor_id as wrapped_id
ORDER BY df.id
LIMIT 5
''')

print(f"Found {len(result)} factors with non-default spatial data:")
for row in result:
    print(f"  Factor {row['factor_id']} (wraps {row['wrapped_id']}): location={row['location']}, size={row['size']}")

# Test 4: Check if spatial data is properly formatted as arrays
print("\n4. Spatial Data Format Validation")
result = conn.execute_query('''
MATCH (df:DIAGRAM_FACTOR)
WHERE df.location IS NOT NULL
RETURN df.location as location, df.size as size
LIMIT 3
''')

print("Sample spatial data formats:")
for row in result:
    print(f"  Location: {row['location']} (type: {type(row['location'])})")
    print(f"  Size: {row['size']} (type: {type(row['size'])})")

# Test 5: Check if we can query by spatial bounds
print("\n5. Spatial Query Test")
try:
    # This will only work if the data is stored as proper arrays, not strings
    result = conn.execute_query('''
    MATCH (df:DIAGRAM_FACTOR)
    WHERE df.location IS NOT NULL
    WITH df, 
         CASE WHEN df.location STARTS WITH '[' 
              THEN toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0])
              ELSE 0.0 END as x_coord,
         CASE WHEN df.location STARTS WITH '[' 
              THEN toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1])
              ELSE 0.0 END as y_coord
    WHERE x_coord > 100 AND y_coord > 100
    RETURN count(df) as factors_in_bounds
    ''')
    
    if result:
        print(f"Factors with coordinates > (100, 100): {result[0]['factors_in_bounds']}")
    
except Exception as e:
    print(f"Spatial query failed: {e}")
    print("This suggests spatial data might be stored as strings rather than arrays")

conn.close()
print("\n✅ Spatial data test complete!")
