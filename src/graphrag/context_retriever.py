"""
Conservation Context Retriever

This module extracts relevant conservation subgraphs from the Neo4j database
based on natural language queries. It uses predefined graph patterns to
retrieve contextual information for GraphRAG responses.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.graph.neo4j_connection import Neo4jConnection
from src.graphrag.graph_patterns import ConservationGraphPatterns, QueryCategory


@dataclass
class RetrievalResult:
    """Container for context retrieval results."""
    graph_data: List[Dict[str, Any]]
    query_category: str
    pattern_used: str
    parameters: Dict[str, Any]
    execution_time: float
    record_count: int


class ConservationContextRetriever:
    """
    Retrieves relevant conservation context from the graph database.
    
    This class executes Cypher queries based on natural language intent
    and returns structured graph data for use in GraphRAG responses.
    """
    
    def __init__(self, neo4j_connection: Optional[Neo4jConnection] = None):
        """
        Initialize the context retriever.
        
        Args:
            neo4j_connection: Neo4j connection instance. If None, creates a new one.
        """
        self.neo4j = neo4j_connection or Neo4jConnection()
        self.patterns = ConservationGraphPatterns()
        self.logger = logging.getLogger(__name__)
    
    def retrieve_threat_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve threat analysis context from the graph.
        
        Args:
            query_params: Parameters for threat queries (target_name, threat_name, etc.)
            
        Returns:
            RetrievalResult containing threat-related graph data
        """
        import time
        start_time = time.time()
        
        # Determine which threat pattern to use
        if 'target_name' in query_params or 'target_id' in query_params:
            pattern = self.patterns.get_threat_analysis_patterns()['threats_to_target']
            pattern_name = 'threats_to_target'
        elif 'threat_name' in query_params or 'threat_id' in query_params:
            pattern = self.patterns.get_threat_analysis_patterns()['threat_impact_chain']
            pattern_name = 'threat_impact_chain'
        else:
            pattern = self.patterns.get_threat_analysis_patterns()['all_threats_to_targets']
            pattern_name = 'all_threats_to_targets'
        
        # Execute query
        try:
            records = self.neo4j.execute_query(pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} threat records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category=QueryCategory.THREAT_ANALYSIS.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving threat context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category=QueryCategory.THREAT_ANALYSIS.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def retrieve_strategy_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve strategy evaluation context from the graph.
        
        Args:
            query_params: Parameters for strategy queries (strategy_name, threat_name, etc.)
            
        Returns:
            RetrievalResult containing strategy-related graph data
        """
        import time
        start_time = time.time()
        
        # Determine which strategy pattern to use
        if 'strategy_name' in query_params or 'strategy_id' in query_params:
            if 'implementation' in str(query_params.get('query', '')).lower():
                pattern = self.patterns.get_strategy_evaluation_patterns()['strategy_implementation']
                pattern_name = 'strategy_implementation'
            else:
                pattern = self.patterns.get_strategy_evaluation_patterns()['strategy_effectiveness']
                pattern_name = 'strategy_effectiveness'
        elif 'threat_name' in query_params or 'threat_id' in query_params:
            pattern = self.patterns.get_strategy_evaluation_patterns()['strategies_by_threat']
            pattern_name = 'strategies_by_threat'
        else:
            pattern = self.patterns.get_strategy_evaluation_patterns()['strategy_portfolio']
            pattern_name = 'strategy_portfolio'
        
        # Execute query
        try:
            records = self.neo4j.execute_query(pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} strategy records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category=QueryCategory.STRATEGY_EVALUATION.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving strategy context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category=QueryCategory.STRATEGY_EVALUATION.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def retrieve_theory_of_change_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve theory of change context from the graph.
        
        Args:
            query_params: Parameters for theory of change queries
            
        Returns:
            RetrievalResult containing theory of change graph data
        """
        import time
        start_time = time.time()
        
        # Determine which theory of change pattern to use
        if 'activity_name' in query_params or 'strategy_name' in query_params:
            pattern = self.patterns.get_theory_of_change_patterns()['full_theory_chain']
            pattern_name = 'full_theory_chain'
        elif 'start_element' in query_params or 'start_id' in query_params:
            pattern = self.patterns.get_theory_of_change_patterns()['impact_pathway']
            pattern_name = 'impact_pathway'
        else:
            pattern = self.patterns.get_theory_of_change_patterns()['results_chain_analysis']
            pattern_name = 'results_chain_analysis'
        
        # Execute query
        try:
            records = self.neo4j.execute_query(pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} theory of change records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category=QueryCategory.THEORY_OF_CHANGE.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving theory of change context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category=QueryCategory.THEORY_OF_CHANGE.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def retrieve_monitoring_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve monitoring and indicator context from the graph.
        
        Args:
            query_params: Parameters for monitoring queries
            
        Returns:
            RetrievalResult containing monitoring-related graph data
        """
        import time
        start_time = time.time()
        
        # Determine which monitoring pattern to use
        if 'element_name' in query_params or 'element_id' in query_params:
            pattern = self.patterns.get_monitoring_patterns()['indicators_for_element']
            pattern_name = 'indicators_for_element'
        elif 'gaps' in str(query_params.get('query', '')).lower():
            pattern = self.patterns.get_monitoring_patterns()['monitoring_gaps']
            pattern_name = 'monitoring_gaps'
        elif 'target' in str(query_params.get('query', '')).lower():
            pattern = self.patterns.get_monitoring_patterns()['target_monitoring']
            pattern_name = 'target_monitoring'
        else:
            pattern = self.patterns.get_monitoring_patterns()['monitoring_framework']
            pattern_name = 'monitoring_framework'
        
        # Execute query
        try:
            records = self.neo4j.execute_query(pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} monitoring records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category=QueryCategory.MONITORING.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving monitoring context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category=QueryCategory.MONITORING.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def retrieve_spatial_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve spatial analysis context from the graph.
        
        Args:
            query_params: Parameters for spatial queries (coordinates, distances, etc.)
            
        Returns:
            RetrievalResult containing spatial graph data
        """
        import time
        start_time = time.time()
        
        # Determine which spatial pattern to use
        if all(key in query_params for key in ['min_x', 'max_x', 'min_y', 'max_y']):
            pattern = self.patterns.get_spatial_analysis_patterns()['elements_in_area']
            pattern_name = 'elements_in_area'
        elif 'max_distance' in query_params:
            pattern = self.patterns.get_spatial_analysis_patterns()['spatial_relationships']
            pattern_name = 'spatial_relationships'
        else:
            pattern = self.patterns.get_spatial_analysis_patterns()['diagram_overview']
            pattern_name = 'diagram_overview'
        
        # Execute query
        try:
            records = self.neo4j.execute_query(pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} spatial records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category=QueryCategory.SPATIAL_ANALYSIS.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving spatial context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category=QueryCategory.SPATIAL_ANALYSIS.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def retrieve_target_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve conservation target analysis context from the graph.
        
        Args:
            query_params: Parameters for target queries
            
        Returns:
            RetrievalResult containing target-related graph data
        """
        import time
        start_time = time.time()
        
        # Determine which target pattern to use
        if 'viability' in str(query_params.get('query', '')).lower():
            pattern = self.patterns.get_target_analysis_patterns()['target_viability']
            pattern_name = 'target_viability'
        elif 'threat' in str(query_params.get('query', '')).lower():
            pattern = self.patterns.get_target_analysis_patterns()['target_threat_pressure']
            pattern_name = 'target_threat_pressure'
        else:
            pattern = self.patterns.get_target_analysis_patterns()['target_enhancement']
            pattern_name = 'target_enhancement'
        
        # Execute query
        try:
            records = self.neo4j.execute_query(pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} target records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category=QueryCategory.TARGET_ANALYSIS.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving target context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category=QueryCategory.TARGET_ANALYSIS.value,
                pattern_used=pattern_name,
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def retrieve_context_by_category(self, category: str, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve context based on query category.
        
        Args:
            category: Query category (threat_analysis, strategy_evaluation, etc.)
            query_params: Parameters for the query
            
        Returns:
            RetrievalResult containing relevant graph data
        """
        category_methods = {
            QueryCategory.THREAT_ANALYSIS.value: self.retrieve_threat_context,
            QueryCategory.STRATEGY_EVALUATION.value: self.retrieve_strategy_context,
            QueryCategory.THEORY_OF_CHANGE.value: self.retrieve_theory_of_change_context,
            QueryCategory.MONITORING.value: self.retrieve_monitoring_context,
            QueryCategory.SPATIAL_ANALYSIS.value: self.retrieve_spatial_context,
            QueryCategory.TARGET_ANALYSIS.value: self.retrieve_target_context
        }
        
        method = category_methods.get(category)
        if method:
            return method(query_params)
        else:
            self.logger.warning(f"Unknown category: {category}, using general retrieval")
            return self.retrieve_general_context(query_params)
    
    def retrieve_general_context(self, query_params: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve general conservation context when category is unclear.
        
        Args:
            query_params: Parameters for the query
            
        Returns:
            RetrievalResult containing general graph data
        """
        import time
        start_time = time.time()
        
        # Use a general query that gets overview of conservation elements
        general_pattern = """
            MATCH (element)
            WHERE element:CONSERVATION_TARGET OR element:THREAT OR element:STRATEGY OR element:ACTIVITY
            OPTIONAL MATCH (element)-[rel]-(connected)
            WHERE connected:CONSERVATION_TARGET OR connected:THREAT OR connected:STRATEGY OR connected:ACTIVITY
            RETURN element, rel, connected,
                   element.name as element_name,
                   labels(element)[0] as element_type,
                   connected.name as connected_name,
                   labels(connected)[0] as connected_type,
                   type(rel) as relationship_type
            LIMIT 50
        """
        
        try:
            records = self.neo4j.execute_query(general_pattern, query_params)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Retrieved {len(records)} general records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category="general",
                pattern_used="general_overview",
                parameters=query_params,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error retrieving general context: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category="general",
                pattern_used="general_overview",
                parameters=query_params,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def execute_custom_query(self, cypher_query: str, parameters: Optional[Dict[str, Any]] = None) -> RetrievalResult:
        """
        Execute a custom Cypher query for specialized retrieval.
        
        Args:
            cypher_query: Custom Cypher query string
            parameters: Query parameters
            
        Returns:
            RetrievalResult containing query results
        """
        import time
        start_time = time.time()
        
        if parameters is None:
            parameters = {}
        
        try:
            records = self.neo4j.execute_query(cypher_query, parameters)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Executed custom query, retrieved {len(records)} records in {execution_time:.3f}s")
            
            return RetrievalResult(
                graph_data=records,
                query_category="custom",
                pattern_used="custom_query",
                parameters=parameters,
                execution_time=execution_time,
                record_count=len(records)
            )
                
        except Exception as e:
            self.logger.error(f"Error executing custom query: {e}")
            return RetrievalResult(
                graph_data=[],
                query_category="custom",
                pattern_used="custom_query",
                parameters=parameters,
                execution_time=time.time() - start_time,
                record_count=0
            )
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about the conservation database.
        
        Returns:
            Dictionary containing database statistics
        """
        stats_query = """
            MATCH (n)
            RETURN labels(n)[0] as node_type, count(n) as count
            ORDER BY count DESC
        """
        
        try:
            # Get node counts
            node_records = self.neo4j.execute_query(stats_query)
            node_counts = {record['node_type']: record['count'] for record in node_records}
            
            # Get relationship counts
            rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """
            rel_records = self.neo4j.execute_query(rel_query)
            rel_counts = {record['relationship_type']: record['count'] for record in rel_records}
            
            return {
                'node_counts': node_counts,
                'relationship_counts': rel_counts,
                'total_nodes': sum(node_counts.values()),
                'total_relationships': sum(rel_counts.values())
            }
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close the Neo4j connection."""
        if self.neo4j:
            self.neo4j.close()
