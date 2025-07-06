"""
Test Neo4j setup and provide guidance for configuration.
"""

import os
import sys
from pathlib import Path

def check_neo4j_setup():
    """Check Neo4j setup and provide guidance."""
    
    print("=" * 60)
    print("NEO4J SETUP CHECKER")
    print("=" * 60)
    
    issues = []
    
    # 1. Check if neo4j driver is installed
    print("1. Checking Neo4j Python driver...")
    try:
        import neo4j
        print("   ✅ Neo4j Python driver is installed")
        print(f"   📦 Version: {neo4j.__version__}")
    except ImportError:
        print("   ❌ Neo4j Python driver is NOT installed")
        issues.append("Install Neo4j driver: pip install neo4j")
    
    # 2. Check environment variables
    print("\n2. Checking environment variables...")
    
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    neo4j_database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    print(f"   NEO4J_URI: {neo4j_uri}")
    print(f"   NEO4J_USER: {neo4j_user}")
    print(f"   NEO4J_PASSWORD: {'***' if neo4j_password else 'NOT SET'}")
    print(f"   NEO4J_DATABASE: {neo4j_database}")
    
    if not neo4j_password:
        print("   ❌ NEO4J_PASSWORD is not set")
        issues.append("Set NEO4J_PASSWORD environment variable")
    else:
        print("   ✅ NEO4J_PASSWORD is configured")
    
    # 3. Check .env file
    print("\n3. Checking .env file...")
    env_file = Path('.env')
    if env_file.exists():
        print("   ✅ .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'NEO4J_PASSWORD' in content:
                print("   ✅ NEO4J_PASSWORD found in .env file")
            else:
                print("   ⚠️  NEO4J_PASSWORD not found in .env file")
                issues.append("Add NEO4J_PASSWORD to .env file")
    else:
        print("   ⚠️  .env file does not exist")
        issues.append("Create .env file with Neo4j configuration")
    
    # 4. Test connection (if driver is available)
    print("\n4. Testing Neo4j connection...")
    try:
        from src.graph.neo4j_connection import Neo4jConnection
        
        if neo4j_password:
            try:
                conn = Neo4jConnection()
                conn.connect()
                print("   ✅ Successfully connected to Neo4j!")
                
                # Test basic query
                result = conn.execute_query("RETURN 1 as test")
                if result and result[0].get('test') == 1:
                    print("   ✅ Basic query test passed")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Connection failed: {e}")
                if "ServiceUnavailable" in str(e):
                    issues.append("Start Neo4j database service")
                elif "AuthError" in str(e):
                    issues.append("Check Neo4j username/password")
                else:
                    issues.append(f"Fix connection issue: {e}")
        else:
            print("   ⏭️  Skipping connection test (no password)")
            
    except ImportError as e:
        print(f"   ⏭️  Skipping connection test: {e}")
    
    # 5. Summary and recommendations
    print("\n" + "=" * 60)
    if issues:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 SETUP RECOMMENDATIONS:")
        print("\n1. Install Neo4j Desktop or Docker:")
        print("   • Neo4j Desktop: https://neo4j.com/download/")
        print("   • Docker: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
        
        print("\n2. Install Python driver:")
        print("   pip install neo4j")
        
        print("\n3. Create .env file with:")
        print("   NEO4J_URI=bolt://localhost:7687")
        print("   NEO4J_USER=neo4j")
        print("   NEO4J_PASSWORD=your_password_here")
        print("   NEO4J_DATABASE=neo4j")
        
        print("\n4. Alternative: Test without Neo4j")
        print("   Use the parser and schema mapper directly:")
        print("   python test_schema_mapper.py")
        
    else:
        print("✅ ALL CHECKS PASSED!")
        print("Your Neo4j setup is ready for loading Miradi projects.")
    
    print("=" * 60)
    
    return len(issues) == 0


if __name__ == "__main__":
    success = check_neo4j_setup()
    sys.exit(0 if success else 1)
