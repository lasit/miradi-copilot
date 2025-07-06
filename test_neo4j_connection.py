"""
Test Neo4j connection with proper environment loading.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_connection():
    """Test Neo4j connection with loaded environment."""
    
    print("=" * 60)
    print("NEO4J CONNECTION TEST")
    print("=" * 60)
    
    # Show loaded environment variables
    print("Environment variables:")
    print(f"  NEO4J_URI: {os.getenv('NEO4J_URI')}")
    print(f"  NEO4J_USER: {os.getenv('NEO4J_USER')}")
    print(f"  NEO4J_PASSWORD: {'***' if os.getenv('NEO4J_PASSWORD') else 'NOT SET'}")
    print(f"  NEO4J_DATABASE: {os.getenv('NEO4J_DATABASE')}")
    
    try:
        from src.graph.neo4j_connection import Neo4jConnection
        
        print("\nTesting connection...")
        conn = Neo4jConnection()
        conn.connect()
        print("✅ Successfully connected to Neo4j!")
        
        # Test basic query
        result = conn.execute_query("RETURN 1 as test, datetime() as timestamp")
        if result:
            print(f"✅ Query test passed: {result[0]}")
        
        # Get database info
        db_info = conn.get_database_info()
        print(f"✅ Database info: {db_info.get('version', 'Unknown version')}")
        
        conn.close()
        print("✅ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        # Provide specific guidance based on error type
        error_str = str(e)
        if "ServiceUnavailable" in error_str:
            print("\n💡 SOLUTION: Start Neo4j database")
            print("   Option 1 - Docker:")
            print("   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:latest")
            print("\n   Option 2 - Neo4j Desktop:")
            print("   Download from https://neo4j.com/download/ and create a database with password 'password123'")
            
        elif "AuthError" in error_str:
            print("\n💡 SOLUTION: Check password")
            print("   Make sure Neo4j password is 'password123' or update .env file")
            
        return False


if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Neo4j is ready for Miradi data loading!")
    else:
        print("\n⚠️  Fix Neo4j setup before loading data")
