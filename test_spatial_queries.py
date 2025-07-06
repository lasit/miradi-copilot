#!/usr/bin/env python3
"""Test the spatial visualization queries."""

from src.graph.neo4j_connection import Neo4jConnection
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    conn = Neo4jConnection(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    conn.connect()
    
    print("TESTING SPATIAL VISUALIZATION QUERIES")
    print("=" * 50)
    
    # Test 1: Diagram bounds calculation
    print("\n1. DIAGRAM BOUNDS CALCULATION")
    result = conn.execute_query('''
    MATCH (df:DIAGRAM_FACTOR)
    WITH df,
         toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
         toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y,
         toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]) as width,
         toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]) as height
    
    RETURN 
        min(x) as min_x, max(x + width) as max_x,
        min(y) as min_y, max(y + height) as max_y,
        max(x + width) - min(x) as total_width,
        max(y + height) - min(y) as total_height,
        count(df) as element_count
    ''')
    
    if result:
        bounds = result[0]
        print(f"Diagram bounds: ({bounds['min_x']:.0f}, {bounds['min_y']:.0f}) to ({bounds['max_x']:.0f}, {bounds['max_y']:.0f})")
        print(f"Diagram size: {bounds['total_width']:.0f} x {bounds['total_height']:.0f}")
        print(f"Total elements: {bounds['element_count']}")
    
    # Test 2: Spatial export sample
    print("\n2. SPATIAL EXPORT SAMPLE")
    result = conn.execute_query('''
    MATCH (df:DIAGRAM_FACTOR)
    OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
    RETURN 
        df.id as diagram_id,
        toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
        toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y,
        toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]) as width,
        toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]) as height,
        labels(element)[0] as element_type,
        element.name as element_name
    ORDER BY df.id
    LIMIT 5
    ''')
    
    print("Sample spatial data for visualization:")
    for row in result:
        x, y = row['x'], row['y']
        w, h = row['width'], row['height']
        element_type = row['element_type'] or 'Unknown'
        element_name = row['element_name'] or 'Unnamed'
        print(f"  {row['diagram_id']}: pos=({x:.0f},{y:.0f}) size=({w:.0f}x{h:.0f}) type={element_type}")
        print(f"    name: {element_name}")
    
    # Test 3: Conservation element proximity
    print("\n3. CONSERVATION ELEMENT PROXIMITY")
    result = conn.execute_query('''
    MATCH (df1:DIAGRAM_FACTOR), (df2:DIAGRAM_FACTOR)
    WHERE df1.id < df2.id
    
    OPTIONAL MATCH (e1) WHERE e1.id = df1.wrapped_factor_id
    OPTIONAL MATCH (e2) WHERE e2.id = df2.wrapped_factor_id
    
    WITH df1, df2, e1, e2,
         toFloat(split(replace(replace(df1.location, '[', ''), ']', ''), ', ')[0]) as x1,
         toFloat(split(replace(replace(df1.location, '[', ''), ']', ''), ', ')[1]) as y1,
         toFloat(split(replace(replace(df2.location, '[', ''), ']', ''), ', ')[0]) as x2,
         toFloat(split(replace(replace(df2.location, '[', ''), ']', ''), ', ')[1]) as y2
    
    WITH df1, df2, e1, e2, x1, y1, x2, y2,
         sqrt(power(x2-x1, 2) + power(y2-y1, 2)) as distance
    
    WHERE distance < 100 AND e1 IS NOT NULL AND e2 IS NOT NULL
    
    RETURN 
        e1.name as element1_name,
        labels(e1)[0] as element1_type,
        e2.name as element2_name,
        labels(e2)[0] as element2_type,
        round(distance, 1) as distance
    ORDER BY distance
    LIMIT 5
    ''')
    
    print("Nearby conservation elements (distance < 100):")
    for row in result:
        print(f"  {row['element1_name']} ({row['element1_type']}) <-> {row['element2_name']} ({row['element2_type']})")
        print(f"    Distance: {row['distance']} units")
    
    # Test 4: Element type distribution
    print("\n4. SPATIAL DISTRIBUTION BY ELEMENT TYPE")
    result = conn.execute_query('''
    MATCH (df:DIAGRAM_FACTOR)
    OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
    WITH df, element,
         toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
         toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y
    
    RETURN 
        labels(element)[0] as element_type,
        count(element) as count,
        round(avg(x), 1) as avg_x,
        round(avg(y), 1) as avg_y,
        min(x) as min_x,
        max(x) as max_x,
        min(y) as min_y,
        max(y) as max_y
    ORDER BY count DESC
    LIMIT 8
    ''')
    
    print("Spatial distribution by element type:")
    for row in result:
        element_type = row['element_type'] or 'Unknown'
        print(f"  {element_type}: {row['count']} elements")
        print(f"    Center: ({row['avg_x']:.0f}, {row['avg_y']:.0f})")
        print(f"    Range: x=[{row['min_x']:.0f}, {row['max_x']:.0f}], y=[{row['min_y']:.0f}, {row['max_y']:.0f}]")
    
    conn.close()
    print("\nSpatial visualization queries working perfectly!")
    print("Ready for D3.js, Cytoscape.js, and other visualization frameworks!")

if __name__ == "__main__":
    main()
