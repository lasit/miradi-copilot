#!/usr/bin/env python3
"""Check current spatial data in Neo4j."""

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
    
    print("CHECKING CURRENT SPATIAL DATA IN NEO4J")
    print("=" * 50)
    
    # Check current DIAGRAM_FACTOR spatial data
    result = conn.execute_query('''
    MATCH (df:DIAGRAM_FACTOR)
    RETURN df.id, df.location, df.size, df.wrapped_factor_id
    ORDER BY df.id
    LIMIT 10
    ''')
    
    print("Current DIAGRAM_FACTOR spatial data:")
    for row in result:
        print(f"  Factor {row['df.id']}: location={row['df.location']}, size={row['df.size']}")
    
    # Check if we have actual coordinates or empty data
    if result:
        first_location = result[0]['df.location']
        first_size = result[0]['df.size']
        
        print(f"\nFirst factor location: {first_location}")
        print(f"First factor size: {first_size}")
        
        if first_location == '{}' or first_location is None:
            print("\n❌ SPATIAL DATA IS EMPTY - Need to reload project with enhanced parser")
            print("The enhanced parser code exists but the data hasn't been reloaded into Neo4j")
        elif '[' in str(first_location) and ',' in str(first_location):
            print("\n✅ SPATIAL DATA IS POPULATED - Enhanced parser data is loaded")
        else:
            print(f"\n⚠️  SPATIAL DATA FORMAT UNCLEAR: {first_location}")
    
    conn.close()

if __name__ == "__main__":
    main()
