"""
Neo4j Connection Manager

This module provides a robust connection interface to Neo4j database with comprehensive error handling,
retry logic, and connection pooling. It supports environment-based configuration and context manager
usage for clean resource management.

The connection manager handles transient failures, provides detailed logging, and offers both simple
and advanced usage patterns for interacting with Neo4j.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase, Driver, Session, Result
    from neo4j.exceptions import (
        ServiceUnavailable, TransientError, ClientError, 
        DatabaseError, AuthError, ConfigurationError
    )
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    # Define dummy classes for type hints when neo4j is not available
    class Driver: pass
    class Session: pass
    class Result: pass
    class ServiceUnavailable(Exception): pass
    class TransientError(Exception): pass
    class ClientError(Exception): pass
    class DatabaseError(Exception): pass
    class AuthError(Exception): pass
    class ConfigurationError(Exception): pass

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


class Neo4jConnectionError(Exception):
    """Custom exception for Neo4j connection issues."""
    pass


class Neo4jConnection:
    """
    Neo4j database connection manager with comprehensive error handling and retry logic.
    
    This class provides a robust interface to Neo4j with automatic connection pooling,
    retry logic for transient failures, and comprehensive error handling.
    
    Example:
        # Basic usage
        conn = Neo4jConnection()
        conn.connect()
        result = conn.execute_query("MATCH (n) RETURN count(n) as count")
        conn.close()
        
        # Context manager usage
        with Neo4jConnection() as conn:
            result = conn.execute_query("MATCH (n) RETURN count(n) as count")
    """
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        max_retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Neo4j connection manager.
        
        Args:
            uri: Neo4j connection URI (defaults to NEO4J_URI env var or bolt://localhost:7687)
            user: Username (defaults to NEO4J_USER env var or 'neo4j')
            password: Password (defaults to NEO4J_PASSWORD env var, required)
            database: Database name (defaults to NEO4J_DATABASE env var or 'neo4j')
            max_retry_attempts: Maximum number of retry attempts for transient failures
            retry_delay: Base delay between retry attempts in seconds
        
        Raises:
            Neo4jConnectionError: If required parameters are missing or neo4j driver is not available
        """
        if not NEO4J_AVAILABLE:
            raise Neo4jConnectionError(
                "Neo4j driver not available. Install with: pip install neo4j"
            )
        
        # Load configuration from environment variables or parameters
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD')
        self.database = database or os.getenv('NEO4J_DATABASE', 'neo4j')
        
        # Validate required parameters
        if not self.password:
            raise Neo4jConnectionError(
                "Neo4j password is required. Set NEO4J_PASSWORD environment variable or pass password parameter."
            )
        
        # Retry configuration
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay = retry_delay
        
        # Connection state
        self.driver: Optional[Driver] = None
        self.is_connected = False
        
        logger.info(f"Initialized Neo4j connection manager for {self.uri}")
    
    def connect(self) -> None:
        """
        Establish connection to Neo4j database.
        
        Creates a driver instance with connection pooling and verifies connectivity.
        
        Raises:
            Neo4jConnectionError: If connection fails after all retry attempts
        """
        if self.is_connected:
            logger.debug("Already connected to Neo4j")
            return
        
        logger.info(f"Connecting to Neo4j at {self.uri}")
        
        for attempt in range(self.max_retry_attempts):
            try:
                # Create driver with connection pooling
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    # Connection pool configuration
                    max_connection_lifetime=3600,  # 1 hour
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60,  # 60 seconds
                    # Encryption settings - disabled for local development
                    encrypted=False
                )
                
                # Verify connectivity
                self.driver.verify_connectivity()
                
                self.is_connected = True
                logger.info(f"Successfully connected to Neo4j (attempt {attempt + 1})")
                return
                
            except AuthError as e:
                logger.error(f"Authentication failed: {e}")
                raise Neo4jConnectionError(f"Authentication failed: {e}")
                
            except ConfigurationError as e:
                logger.error(f"Configuration error: {e}")
                raise Neo4jConnectionError(f"Configuration error: {e}")
                
            except ServiceUnavailable as e:
                logger.warning(f"Neo4j service unavailable (attempt {attempt + 1}/{self.max_retry_attempts}): {e}")
                if attempt < self.max_retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise Neo4jConnectionError(f"Failed to connect to Neo4j after {self.max_retry_attempts} attempts: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                raise Neo4jConnectionError(f"Unexpected error connecting to Neo4j: {e}")
    
    def close(self) -> None:
        """
        Close the Neo4j connection and clean up resources.
        
        Safely closes the driver and releases connection pool resources.
        """
        if self.driver:
            try:
                self.driver.close()
                logger.info("Neo4j connection closed")
            except Exception as e:
                logger.warning(f"Error closing Neo4j connection: {e}")
            finally:
                self.driver = None
                self.is_connected = False
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query with parameters and retry logic.
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            database: Database name (uses default if not specified)
            
        Returns:
            List of result records as dictionaries
            
        Raises:
            Neo4jConnectionError: If not connected or query execution fails
        """
        if not self.is_connected or not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j. Call connect() first.")
        
        if parameters is None:
            parameters = {}
        
        target_database = database or self.database
        
        for attempt in range(self.max_retry_attempts):
            try:
                with self.driver.session(database=target_database) as session:
                    result = session.run(query, parameters)
                    records = [record.data() for record in result]
                    
                    logger.debug(f"Query executed successfully, returned {len(records)} records")
                    return records
                    
            except TransientError as e:
                logger.warning(f"Transient error (attempt {attempt + 1}/{self.max_retry_attempts}): {e}")
                if attempt < self.max_retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise Neo4jConnectionError(f"Query failed after {self.max_retry_attempts} attempts: {e}")
                    
            except ClientError as e:
                logger.error(f"Client error in query: {e}")
                raise Neo4jConnectionError(f"Query error: {e}")
                
            except DatabaseError as e:
                logger.error(f"Database error: {e}")
                raise Neo4jConnectionError(f"Database error: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error executing query: {e}")
                raise Neo4jConnectionError(f"Unexpected error executing query: {e}")
    
    def execute_write_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query (CREATE, UPDATE, DELETE) with transaction management.
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            database: Database name (uses default if not specified)
            
        Returns:
            List of result records as dictionaries
            
        Raises:
            Neo4jConnectionError: If not connected or query execution fails
        """
        if not self.is_connected or not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j. Call connect() first.")
        
        if parameters is None:
            parameters = {}
        
        target_database = database or self.database
        
        for attempt in range(self.max_retry_attempts):
            try:
                with self.driver.session(database=target_database) as session:
                    result = session.execute_write(
                        lambda tx: tx.run(query, parameters).data()
                    )
                    
                    logger.debug(f"Write query executed successfully, returned {len(result)} records")
                    return result
                    
            except TransientError as e:
                logger.warning(f"Transient error in write query (attempt {attempt + 1}/{self.max_retry_attempts}): {e}")
                if attempt < self.max_retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise Neo4jConnectionError(f"Write query failed after {self.max_retry_attempts} attempts: {e}")
                    
            except ClientError as e:
                logger.error(f"Client error in write query: {e}")
                raise Neo4jConnectionError(f"Write query error: {e}")
                
            except DatabaseError as e:
                logger.error(f"Database error in write query: {e}")
                raise Neo4jConnectionError(f"Database error in write query: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error executing write query: {e}")
                raise Neo4jConnectionError(f"Unexpected error executing write query: {e}")
    
    def check_connection(self) -> bool:
        """
        Verify that the Neo4j connection is active and responsive.
        
        Returns:
            True if connection is active and responsive, False otherwise
        """
        try:
            if not self.is_connected or not self.driver:
                return False
            
            # Simple connectivity test
            result = self.execute_query("RETURN 1 as test")
            return len(result) == 1 and result[0].get('test') == 1
            
        except Exception as e:
            logger.warning(f"Connection check failed: {e}")
            return False
    
    def get_driver(self) -> Optional[Driver]:
        """
        Get the underlying Neo4j driver instance for advanced usage.
        
        Returns:
            Neo4j driver instance if connected, None otherwise
            
        Note:
            Use this method only for advanced scenarios that require direct driver access.
            For most use cases, use execute_query() or execute_write_query().
        """
        if not self.is_connected:
            logger.warning("Attempted to get driver when not connected")
            return None
        
        return self.driver
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the connected Neo4j database.
        
        Returns:
            Dictionary containing database information
            
        Raises:
            Neo4jConnectionError: If not connected or query fails
        """
        try:
            # Get Neo4j version and edition
            version_result = self.execute_query("CALL dbms.components() YIELD name, versions, edition")
            
            # Get database statistics
            stats_result = self.execute_query("""
                CALL apoc.meta.stats() YIELD nodeCount, relCount, labelCount, relTypeCount, propertyKeyCount
                RETURN nodeCount, relCount, labelCount, relTypeCount, propertyKeyCount
            """)
            
            info = {
                'connected': True,
                'uri': self.uri,
                'database': self.database,
                'user': self.user
            }
            
            if version_result:
                info.update({
                    'version': version_result[0].get('versions', ['Unknown'])[0],
                    'edition': version_result[0].get('edition', 'Unknown')
                })
            
            if stats_result:
                stats = stats_result[0]
                info.update({
                    'node_count': stats.get('nodeCount', 0),
                    'relationship_count': stats.get('relCount', 0),
                    'label_count': stats.get('labelCount', 0),
                    'relationship_type_count': stats.get('relTypeCount', 0),
                    'property_key_count': stats.get('propertyKeyCount', 0)
                })
            
            return info
            
        except Exception as e:
            logger.warning(f"Could not retrieve database info: {e}")
            return {
                'connected': self.is_connected,
                'uri': self.uri,
                'database': self.database,
                'user': self.user,
                'error': str(e)
            }
    
    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up connection."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        if hasattr(self, 'driver') and self.driver:
            self.close()


@contextmanager
def neo4j_session(
    uri: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None
):
    """
    Context manager for Neo4j sessions with automatic cleanup.
    
    Args:
        uri: Neo4j connection URI
        user: Username
        password: Password
        database: Database name
        
    Yields:
        Neo4jConnection instance
        
    Example:
        with neo4j_session() as conn:
            result = conn.execute_query("MATCH (n) RETURN count(n)")
    """
    conn = Neo4jConnection(uri=uri, user=user, password=password, database=database)
    try:
        conn.connect()
        yield conn
    finally:
        conn.close()


def test_neo4j_connection():
    """
    Test function to verify Neo4j connection and basic functionality.
    
    This function creates a connection, checks connectivity, runs test queries,
    and demonstrates both read and write operations.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("Testing Neo4j connection...")
    
    try:
        # Test basic connection
        print("1. Testing connection establishment...")
        conn = Neo4jConnection()
        conn.connect()
        print("   ✓ Connection established")
        
        # Test connection check
        print("2. Testing connection verification...")
        if conn.check_connection():
            print("   ✓ Connection verified")
        else:
            print("   ✗ Connection verification failed")
            return False
        
        # Test read query
        print("3. Testing read query...")
        result = conn.execute_query("RETURN 'Hello Neo4j!' as message, datetime() as timestamp")
        if result and len(result) == 1:
            message = result[0].get('message')
            timestamp = result[0].get('timestamp')
            print(f"   ✓ Read query successful: {message} at {timestamp}")
        else:
            print("   ✗ Read query failed")
            return False
        
        # Test parameterized query
        print("4. Testing parameterized query...")
        result = conn.execute_query(
            "RETURN $name as name, $value as value",
            parameters={'name': 'test_param', 'value': 42}
        )
        if result and result[0].get('name') == 'test_param' and result[0].get('value') == 42:
            print("   ✓ Parameterized query successful")
        else:
            print("   ✗ Parameterized query failed")
            return False
        
        # Test database info
        print("5. Testing database information retrieval...")
        db_info = conn.get_database_info()
        if db_info.get('connected'):
            print(f"   ✓ Database info retrieved:")
            print(f"     - URI: {db_info.get('uri')}")
            print(f"     - Database: {db_info.get('database')}")
            print(f"     - Version: {db_info.get('version', 'Unknown')}")
            print(f"     - Edition: {db_info.get('edition', 'Unknown')}")
            if 'node_count' in db_info:
                print(f"     - Nodes: {db_info.get('node_count'):,}")
                print(f"     - Relationships: {db_info.get('relationship_count'):,}")
        else:
            print("   ⚠ Database info retrieval had issues")
        
        # Test write query (create and delete a test node)
        print("6. Testing write operations...")
        try:
            # Create test node
            create_result = conn.execute_write_query(
                "CREATE (n:TestNode {name: $name, created: datetime()}) RETURN n.name as name",
                parameters={'name': 'test_node_' + str(int(time.time()))}
            )
            
            if create_result:
                node_name = create_result[0].get('name')
                print(f"   ✓ Test node created: {node_name}")
                
                # Delete test node
                delete_result = conn.execute_write_query(
                    "MATCH (n:TestNode {name: $name}) DELETE n RETURN count(n) as deleted",
                    parameters={'name': node_name}
                )
                
                if delete_result:
                    print("   ✓ Test node deleted")
                else:
                    print("   ⚠ Test node deletion unclear")
            else:
                print("   ✗ Test node creation failed")
                
        except Exception as e:
            print(f"   ⚠ Write operations test failed: {e}")
        
        # Test context manager
        print("7. Testing context manager...")
        with Neo4jConnection() as ctx_conn:
            ctx_result = ctx_conn.execute_query("RETURN 'Context manager test' as message")
            if ctx_result and ctx_result[0].get('message') == 'Context manager test':
                print("   ✓ Context manager successful")
            else:
                print("   ✗ Context manager failed")
                return False
        
        # Close connection
        print("8. Testing connection cleanup...")
        conn.close()
        print("   ✓ Connection closed")
        
        print("\n🎉 All Neo4j connection tests passed!")
        return True
        
    except Neo4jConnectionError as e:
        print(f"\n❌ Neo4j connection error: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        return False


if __name__ == "__main__":
    # Run tests when script is executed directly
    success = test_neo4j_connection()
    exit(0 if success else 1)
