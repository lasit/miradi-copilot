"""
Miradi Co-Pilot GraphRAG Example Usage

This script demonstrates how to use the GraphRAG system for conservation planning queries.
It shows the complete pipeline from natural language query to structured response.
"""

import logging
from typing import Dict, Any, Optional

from src.graphrag.query_router import ConservationQueryRouter
from src.graphrag.context_retriever import ConservationContextRetriever
from src.graphrag.context_assembler import ConservationContextAssembler
from src.graph.neo4j_connection import Neo4jConnection


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MiradiGraphRAG:
    """
    Complete GraphRAG system for Miradi conservation planning queries.
    
    This class orchestrates the entire pipeline from natural language query
    to context-rich prompts ready for language model generation.
    """
    
    def __init__(self, neo4j_connection=None):
        """
        Initialize the GraphRAG system.
        
        Args:
            neo4j_connection: Optional Neo4j connection. If None, creates a new one.
        """
        self.neo4j = neo4j_connection or Neo4jConnection()
        self.query_router = ConservationQueryRouter()
        self.context_retriever = ConservationContextRetriever(self.neo4j)
        self.context_assembler = ConservationContextAssembler()
        
        logger.info("Miradi GraphRAG system initialized")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language conservation query through the complete pipeline.
        
        Args:
            query: Natural language query about conservation planning
            
        Returns:
            Dictionary containing the complete GraphRAG response
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Route the query to determine intent and extract parameters
        query_intent = self.query_router.route_query(query)
        logger.info(f"Query routed to category: {query_intent.category} (confidence: {query_intent.confidence:.2f})")
        
        # Step 2: Retrieve relevant context from the graph database
        retrieval_result = self.context_retriever.retrieve_context_by_category(
            category=query_intent.category,
            query_params=query_intent.parameters
        )
        logger.info(f"Retrieved {retrieval_result.record_count} records in {retrieval_result.execution_time:.3f}s")
        
        # Step 3: Assemble the complete context for LLM consumption
        assembled_context = self.context_assembler.assemble_context(
            query_intent=query_intent,
            retrieval_result=retrieval_result
        )
        logger.info(f"Assembled context with {assembled_context.token_count} tokens")
        
        # Return complete response
        return {
            'query': query,
            'intent': {
                'category': query_intent.category,
                'confidence': query_intent.confidence,
                'keywords': query_intent.keywords,
                'entities': query_intent.entities,
                'parameters': query_intent.parameters
            },
            'retrieval': {
                'pattern_used': retrieval_result.pattern_used,
                'record_count': retrieval_result.record_count,
                'execution_time': retrieval_result.execution_time
            },
            'context': {
                'system_prompt': assembled_context.system_prompt,
                'user_prompt': assembled_context.user_prompt,
                'graph_summary': assembled_context.graph_summary,
                'token_count': assembled_context.token_count
            },
            'metadata': assembled_context.metadata
        }
    
    def get_database_overview(self) -> Dict[str, Any]:
        """Get an overview of the conservation database."""
        return self.context_retriever.get_database_stats()
    
    def get_suggested_queries(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get suggested queries for testing the system."""
        if category:
            return {category: self.query_router.get_suggested_queries(category)}
        
        # Get suggestions for all categories
        suggestions = {}
        for cat in ['threat_analysis', 'strategy_evaluation', 'theory_of_change', 
                   'monitoring', 'spatial_analysis', 'target_analysis']:
            suggestions[cat] = self.query_router.get_suggested_queries(cat)
        
        return suggestions
    
    def close(self):
        """Close database connections."""
        self.context_retriever.close()


def demonstrate_graphrag_system():
    """
    Demonstrate the complete GraphRAG system with example queries.
    
    This function shows how to use the system for various conservation planning queries.
    """
    print("🌿 Miradi Co-Pilot GraphRAG System Demonstration")
    print("=" * 60)
    
    try:
        # Initialize the system
        print("\n1. Initializing GraphRAG system...")
        graphrag = MiradiGraphRAG()
        
        # Get database overview
        print("\n2. Database Overview:")
        db_stats = graphrag.get_database_overview()
        if db_stats:
            print(f"   Total nodes: {db_stats.get('total_nodes', 'Unknown')}")
            print(f"   Total relationships: {db_stats.get('total_relationships', 'Unknown')}")
            print("   Node types:", list(db_stats.get('node_counts', {}).keys())[:5])
        else:
            print("   Database statistics not available")
        
        # Example queries for different categories
        example_queries = [
            "What threatens the coastal ecosystems?",
            "Which strategies are most effective against poaching?", 
            "How does fire management help wildlife?",
            "What indicators track water quality?",
            "Show me threats near the forest areas",
            "What is the viability status of our targets?"
        ]
        
        print(f"\n3. Processing {len(example_queries)} example queries...")
        
        for i, query in enumerate(example_queries, 1):
            print(f"\n--- Query {i}: {query} ---")
            
            try:
                # Process the query
                result = graphrag.process_query(query)
                
                # Display results
                intent = result['intent']
                retrieval = result['retrieval']
                context = result['context']
                
                print(f"Category: {intent['category']} (confidence: {intent['confidence']:.2f})")
                print(f"Keywords: {', '.join(intent['keywords'])}")
                print(f"Retrieved: {retrieval['record_count']} records using {retrieval['pattern_used']}")
                print(f"Context: {context['token_count']} tokens")
                
                # Show a snippet of the graph summary
                summary = context['graph_summary']
                if summary:
                    lines = summary.split('\n')
                    print(f"Summary: {lines[0] if lines else 'No summary available'}")
                
            except Exception as e:
                print(f"Error processing query: {e}")
        
        print(f"\n4. Available query categories and suggestions:")
        suggestions = graphrag.get_suggested_queries()
        for category, queries in suggestions.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for query in queries[:2]:  # Show first 2 suggestions
                print(f"  - {query}")
        
        # Close the system
        graphrag.close()
        print(f"\n✅ GraphRAG demonstration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        logger.error(f"GraphRAG demonstration failed: {e}")


def test_specific_query(query: str):
    """
    Test a specific query through the GraphRAG system.
    
    Args:
        query: Natural language conservation query to test
    """
    print(f"🔍 Testing Query: {query}")
    print("=" * 60)
    
    try:
        # Initialize system
        graphrag = MiradiGraphRAG()
        
        # Process query
        result = graphrag.process_query(query)
        
        # Display detailed results
        print(f"\n📊 Query Analysis:")
        intent = result['intent']
        print(f"   Category: {intent['category']}")
        print(f"   Confidence: {intent['confidence']:.2f}")
        print(f"   Keywords: {intent['keywords']}")
        print(f"   Entities: {intent['entities']}")
        print(f"   Parameters: {intent['parameters']}")
        
        print(f"\n🔍 Data Retrieval:")
        retrieval = result['retrieval']
        print(f"   Pattern: {retrieval['pattern_used']}")
        print(f"   Records: {retrieval['record_count']}")
        print(f"   Time: {retrieval['execution_time']:.3f}s")
        
        print(f"\n📝 Generated Context:")
        context = result['context']
        print(f"   Token count: {context['token_count']}")
        print(f"   Graph summary: {context['graph_summary'][:200]}...")
        
        print(f"\n🤖 System Prompt (first 300 chars):")
        print(f"   {context['system_prompt'][:300]}...")
        
        print(f"\n👤 User Prompt (first 300 chars):")
        print(f"   {context['user_prompt'][:300]}...")
        
        # Close system
        graphrag.close()
        print(f"\n✅ Query test completed!")
        
    except Exception as e:
        print(f"\n❌ Error testing query: {e}")
        logger.error(f"Query test failed: {e}")


if __name__ == "__main__":
    # Run the demonstration
    demonstrate_graphrag_system()
    
    print("\n" + "=" * 60)
    print("💡 To test a specific query, use:")
    print("   from src.graphrag.example_usage import test_specific_query")
    print("   test_specific_query('Your conservation question here')")
