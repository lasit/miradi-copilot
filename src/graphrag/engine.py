"""
Miradi Co-Pilot GraphRAG Engine

This module provides the complete GraphRAG engine that orchestrates the entire pipeline
from natural language query to Claude-generated conservation planning responses.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.graphrag.query_router import ConservationQueryRouter, QueryIntent
from src.graphrag.context_retriever import ConservationContextRetriever, RetrievalResult
from src.graphrag.context_assembler import ConservationContextAssembler, AssembledContext
from src.graphrag.llm_integration import LLMManager, LLMResponse
from src.graph.neo4j_connection import Neo4jConnection


@dataclass
class GraphRAGResponse:
    """Complete response from the GraphRAG system."""
    query: str
    natural_language_response: str
    query_intent: QueryIntent
    retrieval_result: RetrievalResult
    assembled_context: AssembledContext
    llm_response: LLMResponse
    total_time: float
    success: bool
    error_message: Optional[str] = None


class MiradiGraphRAGEngine:
    """
    Complete GraphRAG engine for Miradi conservation planning.
    
    This class orchestrates the entire pipeline:
    1. Natural language query routing and intent classification
    2. Graph database context retrieval using specialized patterns
    3. Context assembly with conservation domain expertise
    4. Claude LLM generation for natural language responses
    5. Response formatting and metadata tracking
    """
    
    def __init__(self, neo4j_connection: Optional[Neo4jConnection] = None, anthropic_api_key: Optional[str] = None):
        """
        Initialize the complete GraphRAG engine.
        
        Args:
            neo4j_connection: Neo4j connection for graph data. If None, creates new connection.
            anthropic_api_key: Anthropic API key for Claude. If None, reads from environment.
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.neo4j = neo4j_connection or Neo4jConnection()
        
        # Connect to Neo4j if not already connected
        if not self.neo4j.is_connected:
            try:
                self.neo4j.connect()
                self.logger.info("Connected to Neo4j database")
            except Exception as e:
                self.logger.error(f"Failed to connect to Neo4j: {e}")
        
        self.query_router = ConservationQueryRouter()
        self.context_retriever = ConservationContextRetriever(self.neo4j)
        self.context_assembler = ConservationContextAssembler()
        
        # Initialize LLM manager
        try:
            self.llm_manager = LLMManager(anthropic_api_key)
            self.llm_available = True
            self.logger.info("GraphRAG engine initialized with Claude LLM integration")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM manager: {e}")
            self.llm_manager = None
            self.llm_available = False
            self.logger.warning("GraphRAG engine initialized without LLM integration")
    
    def query(self, natural_language_query: str) -> GraphRAGResponse:
        """
        Process a complete natural language conservation query.
        
        Args:
            natural_language_query: Natural language question about conservation planning
            
        Returns:
            GraphRAGResponse with natural language conservation advice
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Processing GraphRAG query: {natural_language_query}")
        
        try:
            # Step 1: Route the query and extract intent
            self.logger.info("Step 1: Routing query and extracting intent...")
            query_intent = self.query_router.route_query(natural_language_query)
            self.logger.info(f"Query routed to category: {query_intent.category} (confidence: {query_intent.confidence:.2f})")
            
            # Step 2: Retrieve relevant context from graph database
            self.logger.info("Step 2: Retrieving context from graph database...")
            retrieval_result = self.context_retriever.retrieve_context_by_category(
                category=query_intent.category,
                query_params=query_intent.parameters
            )
            self.logger.info(f"Retrieved {retrieval_result.record_count} records in {retrieval_result.execution_time:.3f}s")
            
            # Step 3: Assemble context for LLM consumption
            self.logger.info("Step 3: Assembling context for LLM...")
            assembled_context = self.context_assembler.assemble_context(
                query_intent=query_intent,
                retrieval_result=retrieval_result
            )
            self.logger.info(f"Assembled context with {assembled_context.token_count} tokens")
            
            # Step 4: Generate natural language response with Claude
            if self.llm_available:
                self.logger.info("Step 4: Generating natural language response with Claude...")
                llm_response = self.llm_manager.query_conservation_data(
                    system_prompt=assembled_context.system_prompt,
                    user_prompt=assembled_context.user_prompt,
                    query_category=query_intent.category
                )
                
                if llm_response.success:
                    self.logger.info(f"Claude response generated: {llm_response.tokens_used} tokens, ${llm_response.cost_estimate:.4f}")
                    natural_language_response = llm_response.content
                else:
                    self.logger.error(f"Claude response failed: {llm_response.error_message}")
                    natural_language_response = self._create_fallback_response(assembled_context, query_intent)
            else:
                self.logger.warning("LLM not available, creating fallback response...")
                llm_response = self._create_mock_llm_response()
                natural_language_response = self._create_fallback_response(assembled_context, query_intent)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            self.logger.info(f"GraphRAG query completed successfully in {total_time:.3f}s")
            
            return GraphRAGResponse(
                query=natural_language_query,
                natural_language_response=natural_language_response,
                query_intent=query_intent,
                retrieval_result=retrieval_result,
                assembled_context=assembled_context,
                llm_response=llm_response,
                total_time=total_time,
                success=True
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            error_message = f"GraphRAG query failed: {e}"
            self.logger.error(error_message)
            
            return GraphRAGResponse(
                query=natural_language_query,
                natural_language_response=f"I apologize, but I encountered an error processing your conservation query: {e}",
                query_intent=QueryIntent("error", 0.0, {}, [], []),
                retrieval_result=RetrievalResult([], "error", "none", {}, 0.0, 0),
                assembled_context=AssembledContext("", "", "", {}, 0),
                llm_response=self._create_mock_llm_response(error=str(e)),
                total_time=total_time,
                success=False,
                error_message=error_message
            )
    
    def _create_fallback_response(self, assembled_context: AssembledContext, query_intent: QueryIntent) -> str:
        """
        Create a fallback response when LLM is not available.
        
        Args:
            assembled_context: Assembled context from graph data
            query_intent: Query intent and parameters
            
        Returns:
            Fallback natural language response
        """
        category = query_intent.category
        graph_summary = assembled_context.graph_summary
        
        fallback_response = f"""
**Conservation Analysis Results**

**Query Category**: {category.replace('_', ' ').title()}
**Confidence**: {query_intent.confidence:.2f}

**Graph Data Summary**:
{graph_summary}

**Analysis**:
Based on the conservation data retrieved from your Miradi project, I found {assembled_context.metadata.get('record_count', 0)} relevant records. The data shows relationships between conservation targets, threats, strategies, and activities that are relevant to your query.

**Note**: This is a simplified response as the AI language model is not currently available. For detailed conservation analysis and recommendations, please ensure the ANTHROPIC_API_KEY is properly configured.

**Next Steps**:
1. Review the graph data summary above
2. Consider the relationships between conservation elements
3. Use the Cypher query patterns for deeper analysis
4. Configure Claude integration for detailed AI-powered insights
"""
        
        return fallback_response.strip()
    
    def _create_mock_llm_response(self, error: Optional[str] = None) -> LLMResponse:
        """
        Create a mock LLM response for fallback scenarios.
        
        Args:
            error: Optional error message
            
        Returns:
            Mock LLMResponse object
        """
        return LLMResponse(
            content="Fallback response - LLM not available",
            model_used="none",
            tokens_used=0,
            response_time=0.0,
            cost_estimate=0.0,
            success=False,
            error_message=error or "LLM not available"
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the GraphRAG system.
        
        Returns:
            Dictionary with status information for all components
        """
        # Test Neo4j connection
        try:
            db_stats = self.context_retriever.get_database_stats()
            neo4j_status = "connected" if db_stats else "disconnected"
            neo4j_ready = bool(db_stats)
        except Exception as e:
            neo4j_status = f"error: {e}"
            neo4j_ready = False
            db_stats = {}
        
        # Get LLM status
        if self.llm_manager:
            llm_status = self.llm_manager.get_status()
        else:
            llm_status = {
                "connection_status": "not_initialized",
                "provider": "none",
                "ready": False
            }
        
        return {
            "graphrag_engine": {
                "status": "initialized",
                "components": {
                    "query_router": "ready",
                    "context_retriever": "ready" if neo4j_ready else "not_ready",
                    "context_assembler": "ready",
                    "llm_manager": "ready" if self.llm_available else "not_ready"
                }
            },
            "neo4j": {
                "status": neo4j_status,
                "ready": neo4j_ready,
                "database_stats": db_stats
            },
            "llm": llm_status,
            "overall_ready": neo4j_ready and self.llm_available
        }
    
    def get_suggested_queries(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get suggested conservation queries for testing.
        
        Args:
            category: Specific category to get suggestions for
            
        Returns:
            Dictionary of suggested queries by category
        """
        return self.query_router.get_suggested_queries(category)
    
    def test_end_to_end(self) -> Dict[str, Any]:
        """
        Test the complete GraphRAG pipeline with a simple query.
        
        Returns:
            Test results with performance metrics
        """
        test_query = "What are the main conservation targets in this project?"
        
        self.logger.info("Running end-to-end GraphRAG test...")
        
        try:
            response = self.query(test_query)
            
            return {
                "test_query": test_query,
                "success": response.success,
                "total_time": response.total_time,
                "query_category": response.query_intent.category,
                "records_retrieved": response.retrieval_result.record_count,
                "context_tokens": response.assembled_context.token_count,
                "llm_tokens": response.llm_response.tokens_used,
                "llm_cost": response.llm_response.cost_estimate,
                "response_length": len(response.natural_language_response),
                "error_message": response.error_message
            }
            
        except Exception as e:
            return {
                "test_query": test_query,
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close all connections and clean up resources."""
        if self.context_retriever:
            self.context_retriever.close()
        
        self.logger.info("GraphRAG engine closed")


# Convenience function for quick usage
def create_graphrag_engine(neo4j_connection: Optional[Neo4jConnection] = None, 
                          anthropic_api_key: Optional[str] = None) -> MiradiGraphRAGEngine:
    """
    Create a GraphRAG engine with optional custom connections.
    
    Args:
        neo4j_connection: Custom Neo4j connection
        anthropic_api_key: Anthropic API key for Claude
        
    Returns:
        Initialized MiradiGraphRAGEngine
    """
    return MiradiGraphRAGEngine(neo4j_connection, anthropic_api_key)
