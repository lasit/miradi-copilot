"""
Neo4j Loader for Miradi Projects

This module provides a complete pipeline for loading Miradi conservation projects into Neo4j database.
It handles constraint creation, indexing, batch operations, and transaction management for optimal
performance and data integrity.

The loader integrates the MiradiParser, MiradiToGraphMapper, and Neo4jConnection components to provide
a seamless end-to-end loading process.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime

from ..graph.neo4j_connection import Neo4jConnection, Neo4jConnectionError
from ..graph.models import (
    MiradiNode, MiradiRelationship, GraphConversionResult, 
    NodeType, RelationshipType
)
from .miradi_parser import MiradiParser
from .schema_mapper import MiradiToGraphMapper

# Set up logging
logger = logging.getLogger(__name__)


class Neo4jLoaderError(Exception):
    """Custom exception for Neo4j loader issues."""
    pass


class Neo4jLoader:
    """
    Neo4j loader for Miradi conservation projects.
    
    This class provides a complete pipeline for loading Miradi projects into Neo4j with
    constraint creation, indexing, batch operations, and comprehensive error handling.
    
    Example:
        # Basic usage
        conn = Neo4jConnection()
        conn.connect()
        loader = Neo4jLoader(conn)
        
        # Load a project
        stats = loader.load_project("project.xmpz2")
        
        # Or load components separately
        loader.create_constraints()
        loader.create_indexes()
        loader.load_nodes(nodes)
        loader.load_relationships(relationships)
    """
    
    def __init__(
        self,
        connection: Neo4jConnection,
        batch_size: int = 1000,
        enable_progress_logging: bool = True
    ):
        """
        Initialize Neo4j loader.
        
        Args:
            connection: Active Neo4jConnection instance
            batch_size: Number of items to process in each batch
            enable_progress_logging: Whether to log progress during loading
            
        Raises:
            Neo4jLoaderError: If connection is not active
        """
        if not connection.check_connection():
            raise Neo4jLoaderError("Neo4j connection is not active")
        
        self.connection = connection
        self.batch_size = batch_size
        self.enable_progress_logging = enable_progress_logging
        
        # Initialize components
        self.parser = MiradiParser()
        self.mapper = MiradiToGraphMapper()
        
        logger.info(f"Initialized Neo4j loader with batch size {batch_size}")
    
    def create_constraints(self) -> Dict[str, bool]:
        """
        Create uniqueness constraints for all node types.
        
        Creates constraints on the uuid property for each NodeType to ensure data integrity
        and improve query performance.
        
        Returns:
            Dictionary mapping constraint names to success status
            
        Raises:
            Neo4jLoaderError: If constraint creation fails
        """
        logger.info("Creating Neo4j constraints...")
        
        constraints = {}
        constraint_queries = []
        
        # Generate constraint queries for each node type
        for node_type in NodeType:
            constraint_name = f"{node_type.value.lower()}_uuid_unique"
            constraint_query = f"""
                CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
                FOR (n:{node_type.value}) REQUIRE n.uuid IS UNIQUE
            """
            constraint_queries.append((constraint_name, constraint_query))
        
        # Execute constraint creation
        for constraint_name, query in constraint_queries:
            try:
                self.connection.execute_write_query(query.strip())
                constraints[constraint_name] = True
                logger.debug(f"Created constraint: {constraint_name}")
                
            except Exception as e:
                logger.warning(f"Failed to create constraint {constraint_name}: {e}")
                constraints[constraint_name] = False
        
        successful_constraints = sum(1 for success in constraints.values() if success)
        total_constraints = len(constraints)
        
        logger.info(f"Created {successful_constraints}/{total_constraints} constraints")
        
        if successful_constraints == 0:
            raise Neo4jLoaderError("Failed to create any constraints")
        
        return constraints
    
    def create_indexes(self) -> Dict[str, bool]:
        """
        Create indexes for better query performance.
        
        Creates indexes on commonly queried properties like id, name, and node_type
        for all node types.
        
        Returns:
            Dictionary mapping index names to success status
            
        Raises:
            Neo4jLoaderError: If index creation fails
        """
        logger.info("Creating Neo4j indexes...")
        
        indexes = {}
        index_queries = []
        
        # Generate index queries for each node type
        for node_type in NodeType:
            node_label = node_type.value
            
            # Index on id property
            id_index_name = f"{node_label.lower()}_id_index"
            id_index_query = f"""
                CREATE INDEX {id_index_name} IF NOT EXISTS
                FOR (n:{node_label}) ON (n.id)
            """
            index_queries.append((id_index_name, id_index_query))
            
            # Index on name property
            name_index_name = f"{node_label.lower()}_name_index"
            name_index_query = f"""
                CREATE INDEX {name_index_name} IF NOT EXISTS
                FOR (n:{node_label}) ON (n.name)
            """
            index_queries.append((name_index_name, name_index_query))
            
            # Index on node_type property
            type_index_name = f"{node_label.lower()}_type_index"
            type_index_query = f"""
                CREATE INDEX {type_index_name} IF NOT EXISTS
                FOR (n:{node_label}) ON (n.node_type)
            """
            index_queries.append((type_index_name, type_index_query))
        
        # Execute index creation
        for index_name, query in index_queries:
            try:
                self.connection.execute_write_query(query.strip())
                indexes[index_name] = True
                logger.debug(f"Created index: {index_name}")
                
            except Exception as e:
                logger.warning(f"Failed to create index {index_name}: {e}")
                indexes[index_name] = False
        
        successful_indexes = sum(1 for success in indexes.values() if success)
        total_indexes = len(indexes)
        
        logger.info(f"Created {successful_indexes}/{total_indexes} indexes")
        
        return indexes
    
    def clear_database(self, confirm: bool = False) -> bool:
        """
        Clear all data from the database.
        
        WARNING: This will delete ALL nodes and relationships in the database.
        Use with extreme caution.
        
        Args:
            confirm: Must be True to actually perform the deletion
            
        Returns:
            True if database was cleared, False otherwise
            
        Raises:
            Neo4jLoaderError: If clearing fails
        """
        if not confirm:
            logger.warning("Database clear requested but not confirmed")
            return False
        
        logger.warning("Clearing Neo4j database - ALL DATA WILL BE DELETED")
        
        try:
            # Delete all relationships first
            rel_result = self.connection.execute_write_query(
                "MATCH ()-[r]-() DELETE r RETURN count(r) as deleted_relationships"
            )
            deleted_relationships = rel_result[0].get('deleted_relationships', 0) if rel_result else 0
            
            # Delete all nodes
            node_result = self.connection.execute_write_query(
                "MATCH (n) DELETE n RETURN count(n) as deleted_nodes"
            )
            deleted_nodes = node_result[0].get('deleted_nodes', 0) if node_result else 0
            
            logger.warning(f"Deleted {deleted_relationships} relationships and {deleted_nodes} nodes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            raise Neo4jLoaderError(f"Failed to clear database: {e}")
    
    def load_nodes(self, nodes: List[MiradiNode]) -> Dict[str, Any]:
        """
        Load nodes into Neo4j using batch operations.
        
        Args:
            nodes: List of MiradiNode objects to load
            
        Returns:
            Dictionary with loading statistics
            
        Raises:
            Neo4jLoaderError: If node loading fails
        """
        if not nodes:
            logger.info("No nodes to load")
            return {'total_nodes': 0, 'batches': 0, 'load_time': 0}
        
        logger.info(f"Loading {len(nodes)} nodes in batches of {self.batch_size}")
        start_time = time.time()
        
        # Group nodes by type for efficient loading
        nodes_by_type = {}
        for node in nodes:
            node_type = node.node_type.value
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        total_loaded = 0
        total_batches = 0
        
        # Load each node type separately
        for node_type, type_nodes in nodes_by_type.items():
            logger.info(f"Loading {len(type_nodes)} {node_type} nodes")
            
            # Process in batches
            for i in range(0, len(type_nodes), self.batch_size):
                batch = type_nodes[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches += 1
                
                # Convert nodes to Neo4j format
                batch_data = [node.to_neo4j_dict() for node in batch]
                
                # Create batch loading query
                query = f"""
                    UNWIND $nodes as nodeData
                    CREATE (n:{node_type})
                    SET n = nodeData
                    RETURN count(n) as created
                """
                
                try:
                    result = self.connection.execute_write_query(
                        query, 
                        parameters={'nodes': batch_data}
                    )
                    
                    created_count = result[0].get('created', 0) if result else 0
                    total_loaded += created_count
                    
                    if self.enable_progress_logging:
                        logger.info(f"  Batch {batch_num}: Created {created_count} {node_type} nodes")
                    
                except Exception as e:
                    logger.error(f"Failed to load {node_type} batch {batch_num}: {e}")
                    raise Neo4jLoaderError(f"Failed to load {node_type} nodes: {e}")
        
        load_time = time.time() - start_time
        
        logger.info(f"Successfully loaded {total_loaded} nodes in {total_batches} batches ({load_time:.2f}s)")
        
        return {
            'total_nodes': total_loaded,
            'batches': total_batches,
            'load_time': load_time,
            'nodes_by_type': {k: len(v) for k, v in nodes_by_type.items()}
        }
    
    def load_relationships(self, relationships: List[MiradiRelationship]) -> Dict[str, Any]:
        """
        Load relationships into Neo4j using batch operations.
        
        Args:
            relationships: List of MiradiRelationship objects to load
            
        Returns:
            Dictionary with loading statistics
            
        Raises:
            Neo4jLoaderError: If relationship loading fails
        """
        if not relationships:
            logger.info("No relationships to load")
            return {'total_relationships': 0, 'batches': 0, 'load_time': 0}
        
        logger.info(f"Loading {len(relationships)} relationships in batches of {self.batch_size}")
        start_time = time.time()
        
        # Group relationships by type for efficient loading
        relationships_by_type = {}
        for rel in relationships:
            rel_type = rel.relationship_type.value
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append(rel)
        
        total_loaded = 0
        total_batches = 0
        
        # Load each relationship type separately
        for rel_type, type_relationships in relationships_by_type.items():
            logger.info(f"Loading {len(type_relationships)} {rel_type} relationships")
            
            # Process in batches
            for i in range(0, len(type_relationships), self.batch_size):
                batch = type_relationships[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches += 1
                
                # Convert relationships to Neo4j format
                batch_data = []
                for rel in batch:
                    rel_data = rel.to_neo4j_dict()
                    rel_data['source_id'] = rel.source_id
                    rel_data['target_id'] = rel.target_id
                    batch_data.append(rel_data)
                
                # Create batch loading query
                query = f"""
                    UNWIND $relationships as relData
                    MATCH (source {{id: relData.source_id}})
                    MATCH (target {{id: relData.target_id}})
                    CREATE (source)-[r:{rel_type}]->(target)
                    SET r = apoc.map.removeKeys(relData, ['source_id', 'target_id'])
                    RETURN count(r) as created
                """
                
                # Fallback query without APOC
                fallback_query = f"""
                    UNWIND $relationships as relData
                    MATCH (source {{id: relData.source_id}})
                    MATCH (target {{id: relData.target_id}})
                    CREATE (source)-[r:{rel_type}]->(target)
                    SET r.relationship_type = relData.relationship_type,
                        r.created_at = relData.created_at,
                        r.source_element = relData.source_element,
                        r.confidence = relData.confidence
                    RETURN count(r) as created
                """
                
                try:
                    # Try with APOC first, fallback to manual property setting
                    try:
                        result = self.connection.execute_write_query(
                            query, 
                            parameters={'relationships': batch_data}
                        )
                    except Exception:
                        # Fallback without APOC
                        result = self.connection.execute_write_query(
                            fallback_query, 
                            parameters={'relationships': batch_data}
                        )
                    
                    created_count = result[0].get('created', 0) if result else 0
                    total_loaded += created_count
                    
                    if self.enable_progress_logging:
                        logger.info(f"  Batch {batch_num}: Created {created_count} {rel_type} relationships")
                    
                except Exception as e:
                    logger.error(f"Failed to load {rel_type} batch {batch_num}: {e}")
                    raise Neo4jLoaderError(f"Failed to load {rel_type} relationships: {e}")
        
        load_time = time.time() - start_time
        
        logger.info(f"Successfully loaded {total_loaded} relationships in {total_batches} batches ({load_time:.2f}s)")
        
        return {
            'total_relationships': total_loaded,
            'batches': total_batches,
            'load_time': load_time,
            'relationships_by_type': {k: len(v) for k, v in relationships_by_type.items()}
        }
    
    def load_project(
        self, 
        project_file: str,
        create_constraints: bool = True,
        create_indexes: bool = True,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Complete pipeline to load a Miradi project into Neo4j.
        
        This method provides the full end-to-end pipeline:
        1. Parse Miradi file
        2. Convert to graph format
        3. Create constraints and indexes (optional)
        4. Load nodes and relationships
        5. Return comprehensive statistics
        
        Args:
            project_file: Path to Miradi project file (.xmpz2)
            create_constraints: Whether to create uniqueness constraints
            create_indexes: Whether to create performance indexes
            clear_existing: Whether to clear existing data first (DANGEROUS)
            
        Returns:
            Dictionary with comprehensive loading statistics
            
        Raises:
            Neo4jLoaderError: If any step of the pipeline fails
        """
        logger.info(f"Starting complete project load pipeline for: {project_file}")
        pipeline_start = time.time()
        
        try:
            # Validate file exists
            if not Path(project_file).exists():
                raise Neo4jLoaderError(f"Project file not found: {project_file}")
            
            # Step 1: Clear existing data if requested
            if clear_existing:
                logger.warning("Clearing existing database data")
                self.clear_database(confirm=True)
            
            # Step 2: Create constraints and indexes
            constraints_stats = {}
            indexes_stats = {}
            
            if create_constraints:
                logger.info("Creating database constraints...")
                constraints_stats = self.create_constraints()
            
            if create_indexes:
                logger.info("Creating database indexes...")
                indexes_stats = self.create_indexes()
            
            # Step 3: Parse Miradi file
            logger.info("Parsing Miradi project file...")
            parse_start = time.time()
            
            parsed_data = self.parser.parse_all(project_file)
            parsing_summary = self.parser.get_parsing_summary()
            
            parse_time = time.time() - parse_start
            logger.info(f"Parsing completed in {parse_time:.2f}s - {parsing_summary['total_elements']} elements")
            
            # Step 4: Convert to graph format
            logger.info("Converting to graph format...")
            convert_start = time.time()
            
            graph_result = self.mapper.map_project_to_graph(parsed_data)
            
            convert_time = time.time() - convert_start
            logger.info(f"Graph conversion completed in {convert_time:.2f}s - {len(graph_result.nodes)} nodes, {len(graph_result.relationships)} relationships")
            
            # Check for conversion errors
            if graph_result.errors:
                logger.warning(f"Graph conversion had {len(graph_result.errors)} errors")
                for error in graph_result.errors:
                    logger.warning(f"  Conversion error: {error}")
            
            # Step 5: Load nodes
            logger.info("Loading nodes into Neo4j...")
            nodes_stats = self.load_nodes(graph_result.nodes)
            
            # Step 6: Load relationships
            logger.info("Loading relationships into Neo4j...")
            relationships_stats = self.load_relationships(graph_result.relationships)
            
            # Calculate total pipeline time
            pipeline_time = time.time() - pipeline_start
            
            # Compile comprehensive statistics
            stats = {
                'project_file': project_file,
                'pipeline_time': pipeline_time,
                'success': True,
                'timestamp': datetime.now().isoformat(),
                
                # Parsing statistics
                'parsing': {
                    'parse_time': parse_time,
                    'total_elements': parsing_summary['total_elements'],
                    'element_breakdown': parsing_summary['element_breakdown'],
                    'coverage': parsing_summary['coverage']
                },
                
                # Graph conversion statistics
                'conversion': {
                    'convert_time': convert_time,
                    'total_nodes': len(graph_result.nodes),
                    'total_relationships': len(graph_result.relationships),
                    'conversion_errors': len(graph_result.errors),
                    'conversion_warnings': len(graph_result.warnings),
                    'node_counts': graph_result.stats.get('node_counts', {}),
                    'relationship_counts': graph_result.stats.get('relationship_counts', {})
                },
                
                # Database loading statistics
                'loading': {
                    'nodes': nodes_stats,
                    'relationships': relationships_stats,
                    'constraints': constraints_stats,
                    'indexes': indexes_stats
                }
            }
            
            # Log final summary
            logger.info("=" * 60)
            logger.info("PROJECT LOAD PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"📁 Project: {Path(project_file).name}")
            logger.info(f"⏱️  Total time: {pipeline_time:.2f}s")
            logger.info(f"📊 Elements parsed: {parsing_summary['total_elements']:,}")
            logger.info(f"🔗 Nodes created: {nodes_stats['total_nodes']:,}")
            logger.info(f"🔗 Relationships created: {relationships_stats['total_relationships']:,}")
            logger.info(f"📈 Coverage: {parsing_summary['coverage']['known_element_coverage']:.1f}%")
            
            if graph_result.errors:
                logger.warning(f"⚠️  Conversion errors: {len(graph_result.errors)}")
            
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            pipeline_time = time.time() - pipeline_start
            error_msg = f"Project load pipeline failed after {pipeline_time:.2f}s: {e}"
            logger.error(error_msg)
            
            # Return error statistics
            return {
                'project_file': project_file,
                'pipeline_time': pipeline_time,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


def load_miradi_project(
    project_file: str,
    connection: Optional[Neo4jConnection] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to load a Miradi project into Neo4j.
    
    Args:
        project_file: Path to Miradi project file
        connection: Neo4j connection (creates new one if None)
        **kwargs: Additional arguments for Neo4jLoader.load_project()
        
    Returns:
        Loading statistics dictionary
        
    Example:
        # With existing connection
        stats = load_miradi_project("project.xmpz2", connection=conn)
        
        # With automatic connection
        stats = load_miradi_project("project.xmpz2")
    """
    if connection is None:
        # Create temporary connection
        with Neo4jConnection() as conn:
            loader = Neo4jLoader(conn)
            return loader.load_project(project_file, **kwargs)
    else:
        # Use provided connection
        loader = Neo4jLoader(connection)
        return loader.load_project(project_file, **kwargs)


if __name__ == "__main__":
    # Example usage when run directly
    import sys
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.etl.neo4j_loader <project_file.xmpz2>")
        print("   or: python src/etl/neo4j_loader.py <project_file.xmpz2>")
        sys.exit(1)
    
    project_file = sys.argv[1]
    
    try:
        # Load project with automatic connection
        stats = load_miradi_project(project_file)
        
        if stats['success']:
            print(f"✅ Successfully loaded {project_file}")
            print(f"   Nodes: {stats['loading']['nodes']['total_nodes']:,}")
            print(f"   Relationships: {stats['loading']['relationships']['total_relationships']:,}")
            print(f"   Time: {stats['pipeline_time']:.2f}s")
        else:
            print(f"❌ Failed to load {project_file}: {stats.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error loading project: {e}")
        sys.exit(1)
