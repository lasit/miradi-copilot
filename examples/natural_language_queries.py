"""
Natural Language Conservation Queries - Miradi Co-Pilot GraphRAG Demo

This script demonstrates the complete GraphRAG system with real conservation
planning queries using Claude Sonnet 3.5 for natural language responses.
"""

import os
import sys
import logging
import time
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graphrag.engine import MiradiGraphRAGEngine
from src.graphrag.config import get_config, validate_config


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConservationQueryDemo:
    """
    Demonstration of natural language conservation queries.
    
    This class provides a comprehensive demo of the GraphRAG system
    with real conservation planning scenarios.
    """
    
    def __init__(self):
        """Initialize the demo with GraphRAG engine."""
        self.engine = None
        self.total_cost = 0.0
        self.total_queries = 0
        
        # Conservation query examples by category
        self.example_queries = {
            "threat_analysis": [
                "What threatens the coastal ecosystems?",
                "Which threats have the highest impact on marine habitats?",
                "Show me all threats to forest biodiversity and their severity levels",
                "What are the main pressures on wildlife populations in this project?"
            ],
            "strategy_evaluation": [
                "Which strategies are most effective against poaching?",
                "How well do our conservation strategies work?",
                "What activities implement the habitat restoration strategy?",
                "Which strategies address water pollution and how effective are they?"
            ],
            "theory_of_change": [
                "How does fire management help wildlife?",
                "What is the impact pathway from education to conservation outcomes?",
                "Trace the logic from anti-poaching activities to elephant population recovery",
                "How do community-based strategies lead to habitat protection?"
            ],
            "monitoring": [
                "What indicators track water quality in our conservation areas?",
                "Which targets lack monitoring indicators?",
                "Show me all measurements for forest health assessment",
                "What are the monitoring gaps in our conservation project?"
            ],
            "spatial_analysis": [
                "Show me threats near the forest areas",
                "What conservation targets are in the northern region?",
                "Which strategies operate within coastal zones?",
                "Map the spatial distribution of conservation activities"
            ],
            "target_analysis": [
                "What is the viability status of our conservation targets?",
                "Which targets are most threatened and need immediate attention?",
                "Show me the health status of marine ecosystems",
                "What conservation results enhance our biodiversity targets?"
            ]
        }
    
    def setup_engine(self) -> bool:
        """
        Set up the GraphRAG engine with configuration validation.
        
        Returns:
            True if setup successful, False otherwise
        """
        print("🌿 Miradi Co-Pilot Natural Language Conservation Queries")
        print("=" * 70)
        
        # Validate configuration
        print("\n1. Validating Configuration...")
        config_validation = validate_config()
        
        if not config_validation['valid']:
            print("❌ Configuration Issues:")
            for issue in config_validation['issues']:
                print(f"   - {issue}")
            print("\nPlease fix configuration issues before running queries.")
            return False
        
        if config_validation['warnings']:
            print("⚠️  Configuration Warnings:")
            for warning in config_validation['warnings']:
                print(f"   - {warning}")
        
        config_info = config_validation['config']
        print(f"✅ Configuration Valid:")
        print(f"   - Anthropic API: {'✓' if config_info['anthropic_configured'] else '✗'}")
        print(f"   - Neo4j Database: {'✓' if config_info['neo4j_configured'] else '✗'}")
        print(f"   - Environment: {config_info['environment']}")
        print(f"   - Primary Model: {config_info['primary_model']}")
        
        # Initialize GraphRAG engine
        print("\n2. Initializing GraphRAG Engine...")
        try:
            self.engine = MiradiGraphRAGEngine()
            
            # Get system status
            status = self.engine.get_system_status()
            
            print(f"   - GraphRAG Engine: {status['graphrag_engine']['status']}")
            print(f"   - Neo4j Connection: {status['neo4j']['status']}")
            print(f"   - Claude LLM: {status['llm']['connection_status']}")
            print(f"   - Overall Ready: {'✅' if status['overall_ready'] else '❌'}")
            
            if not status['overall_ready']:
                print("\n❌ System not ready for queries. Please check:")
                if not status['neo4j']['ready']:
                    print("   - Neo4j database connection")
                if not status['llm']['ready']:
                    print("   - Anthropic API key configuration")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize GraphRAG engine: {e}")
            return False
    
    def run_single_query(self, query: str, show_details: bool = True) -> Dict[str, Any]:
        """
        Run a single conservation query and display results.
        
        Args:
            query: Natural language conservation query
            show_details: Whether to show detailed response information
            
        Returns:
            Dictionary with query results and metrics
        """
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Process the query
            response = self.engine.query(query)
            
            # Update tracking
            self.total_queries += 1
            self.total_cost += response.llm_response.cost_estimate
            
            # Display results
            if response.success:
                print("✅ Query Successful")
                
                if show_details:
                    print(f"📊 Query Analysis:")
                    print(f"   Category: {response.query_intent.category}")
                    print(f"   Confidence: {response.query_intent.confidence:.2f}")
                    print(f"   Keywords: {', '.join(response.query_intent.keywords)}")
                    
                    print(f"🔍 Data Retrieval:")
                    print(f"   Pattern: {response.retrieval_result.pattern_used}")
                    print(f"   Records: {response.retrieval_result.record_count}")
                    print(f"   Time: {response.retrieval_result.execution_time:.3f}s")
                    
                    print(f"🤖 Claude Response:")
                    print(f"   Model: {response.llm_response.model_used}")
                    print(f"   Tokens: {response.llm_response.tokens_used}")
                    print(f"   Cost: ${response.llm_response.cost_estimate:.4f}")
                    print(f"   Time: {response.llm_response.response_time:.3f}s")
                
                print(f"\n💬 Conservation Analysis:")
                print(response.natural_language_response)
                
                return {
                    "success": True,
                    "query": query,
                    "category": response.query_intent.category,
                    "confidence": response.query_intent.confidence,
                    "records_retrieved": response.retrieval_result.record_count,
                    "total_time": response.total_time,
                    "llm_tokens": response.llm_response.tokens_used,
                    "llm_cost": response.llm_response.cost_estimate,
                    "response_length": len(response.natural_language_response)
                }
                
            else:
                print(f"❌ Query Failed: {response.error_message}")
                print(f"💬 Fallback Response:")
                print(response.natural_language_response)
                
                return {
                    "success": False,
                    "query": query,
                    "error": response.error_message,
                    "total_time": response.total_time
                }
                
        except Exception as e:
            print(f"❌ Query Error: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "total_time": time.time() - start_time
            }
    
    def run_category_demo(self, category: str, max_queries: int = 2) -> List[Dict[str, Any]]:
        """
        Run demo queries for a specific conservation category.
        
        Args:
            category: Conservation query category
            max_queries: Maximum number of queries to run
            
        Returns:
            List of query results
        """
        print(f"\n🎯 {category.replace('_', ' ').title()} Queries")
        print("=" * 50)
        
        queries = self.example_queries.get(category, [])[:max_queries]
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n--- Query {i}/{len(queries)} ---")
            result = self.run_single_query(query, show_details=False)
            results.append(result)
            
            # Brief pause between queries
            time.sleep(1)
        
        return results
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """
        Run a comprehensive demo of all conservation query categories.
        
        Returns:
            Summary of demo results
        """
        if not self.setup_engine():
            return {"success": False, "error": "Failed to setup GraphRAG engine"}
        
        print("\n3. Running Conservation Query Demonstrations...")
        
        all_results = []
        category_summaries = {}
        
        # Run queries for each category
        for category in self.example_queries.keys():
            category_results = self.run_category_demo(category, max_queries=1)
            all_results.extend(category_results)
            
            # Summarize category results
            successful = [r for r in category_results if r.get('success', False)]
            category_summaries[category] = {
                "total_queries": len(category_results),
                "successful": len(successful),
                "avg_time": sum(r.get('total_time', 0) for r in successful) / len(successful) if successful else 0,
                "total_cost": sum(r.get('llm_cost', 0) for r in successful)
            }
        
        # Display summary
        print(f"\n📊 Demo Summary")
        print("=" * 50)
        print(f"Total Queries: {self.total_queries}")
        print(f"Total Cost: ${self.total_cost:.4f}")
        print(f"Average Cost per Query: ${self.total_cost/self.total_queries:.4f}" if self.total_queries > 0 else "N/A")
        
        successful_queries = [r for r in all_results if r.get('success', False)]
        if successful_queries:
            avg_time = sum(r['total_time'] for r in successful_queries) / len(successful_queries)
            avg_tokens = sum(r.get('llm_tokens', 0) for r in successful_queries) / len(successful_queries)
            print(f"Success Rate: {len(successful_queries)}/{len(all_results)} ({len(successful_queries)/len(all_results)*100:.1f}%)")
            print(f"Average Response Time: {avg_time:.2f}s")
            print(f"Average Tokens per Query: {avg_tokens:.0f}")
        
        print(f"\n📋 Category Performance:")
        for category, summary in category_summaries.items():
            print(f"   {category.replace('_', ' ').title()}:")
            print(f"     Success: {summary['successful']}/{summary['total_queries']}")
            print(f"     Avg Time: {summary['avg_time']:.2f}s")
            print(f"     Cost: ${summary['total_cost']:.4f}")
        
        # Close engine
        self.engine.close()
        
        return {
            "success": True,
            "total_queries": self.total_queries,
            "successful_queries": len(successful_queries),
            "total_cost": self.total_cost,
            "category_summaries": category_summaries,
            "all_results": all_results
        }
    
    def run_interactive_demo(self):
        """Run an interactive demo where users can input their own queries."""
        if not self.setup_engine():
            return
        
        print("\n🎮 Interactive Conservation Query Mode")
        print("=" * 50)
        print("Enter your conservation planning questions (type 'quit' to exit)")
        print("Examples:")
        for category, queries in list(self.example_queries.items())[:2]:
            print(f"  - {queries[0]}")
        
        while True:
            try:
                query = input("\n🌿 Your conservation question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                self.run_single_query(query)
                
            except KeyboardInterrupt:
                print("\n\nDemo interrupted by user.")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print(f"\n📊 Session Summary:")
        print(f"Total Queries: {self.total_queries}")
        print(f"Total Cost: ${self.total_cost:.4f}")
        
        self.engine.close()


def main():
    """Main function to run the conservation query demo."""
    demo = ConservationQueryDemo()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "interactive":
            demo.run_interactive_demo()
        elif mode == "single" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            if demo.setup_engine():
                demo.run_single_query(query)
                demo.engine.close()
        else:
            print("Usage:")
            print("  python natural_language_queries.py                    # Run comprehensive demo")
            print("  python natural_language_queries.py interactive        # Interactive mode")
            print("  python natural_language_queries.py single 'query'     # Single query")
    else:
        # Run comprehensive demo
        demo.run_comprehensive_demo()


if __name__ == "__main__":
    main()
