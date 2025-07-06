"""
Clear Neo4j database for fresh loading.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clear_database():
    """Clear all data from Neo4j database."""
    
    print("=" * 60)
    print("CLEARING NEO4J DATABASE")
    print("=" * 60)
    
    try:
        from src.graph.neo4j_connection import Neo4jConnection
        
        print("Connecting to Neo4j...")
        conn = Neo4jConnection()
        conn.connect()
        print("✅ Connected successfully")
        
        print("\n⚠️  WARNING: This will delete ALL data in the database!")
        confirm = input("Type 'YES' to confirm deletion: ")
        
        if confirm != 'YES':
            print("❌ Operation cancelled")
            return False
        
        print("\nDeleting all relationships...")
        rel_result = conn.execute_write_query(
            "MATCH ()-[r]-() DELETE r RETURN count(r) as deleted"
        )
        deleted_rels = rel_result[0].get('deleted', 0) if rel_result else 0
        print(f"✅ Deleted {deleted_rels:,} relationships")
        
        print("Deleting all nodes...")
        node_result = conn.execute_write_query(
            "MATCH (n) DELETE n RETURN count(n) as deleted"
        )
        deleted_nodes = node_result[0].get('deleted', 0) if node_result else 0
        print(f"✅ Deleted {deleted_nodes:,} nodes")
        
        print("\nVerifying database is empty...")
        count_result = conn.execute_query(
            "MATCH (n) RETURN count(n) as node_count"
        )
        remaining_nodes = count_result[0].get('node_count', 0) if count_result else 0
        
        if remaining_nodes == 0:
            print("✅ Database successfully cleared!")
        else:
            print(f"⚠️  Warning: {remaining_nodes} nodes still remain")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


if __name__ == "__main__":
    success = clear_database()
    if success:
        print("\n🎉 Database is ready for fresh data loading!")
        print("Now you can run: python -m src.etl.neo4j_loader <project_file>")
    else:
        print("\n❌ Failed to clear database")
