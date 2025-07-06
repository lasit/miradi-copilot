#!/usr/bin/env python3
"""Test for null element IDs in the database."""

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

# Check for null IDs in activities (both id and element_id)
result = conn.execute_query('''
MATCH (a:ACTIVITY)
WHERE a.id IS NULL OR a.element_id IS NULL
RETURN count(a) as null_id_count
''')

print(f'Activities with null id or element_id: {result[0]["null_id_count"]}')

# Check sample activities with both id and element_id
result = conn.execute_query('''
MATCH (a:ACTIVITY)
RETURN a.name, a.id, a.element_id, a.uuid, a.identifier
ORDER BY a.name
LIMIT 5
''')

print('\nSample activities:')
for row in result:
    print(f'  Name: {row["a.name"]}')
    print(f'  ID: {row["a.id"]}')
    print(f'  Element ID: {row["a.element_id"]}')
    print(f'  UUID: {row["a.uuid"]}')
    print(f'  Identifier: {row["a.identifier"]}')
    print()

# Check project name
result = conn.execute_query('''
MATCH (p:PROJECT {id: 'current_project'})
RETURN p.name as project_name
''')

if result:
    print(f'Project name in database: {result[0]["project_name"]}')
else:
    print('No project found in database')

conn.close()
