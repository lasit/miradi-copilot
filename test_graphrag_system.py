"""
Test script for the Miradi Co-Pilot GraphRAG system.

This script demonstrates the complete GraphRAG pipeline for conservation planning queries.
Run this script to test the natural language interface over the Miradi graph database.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graphrag.example_usage import MiradiGraphRAG


def test_graphrag_system():
    """Test the complete GraphRAG system with sample queries."""
    print("🌿 Testing Miradi Co-Pilot GraphRAG System")
    print("=" * 50)
    
    # Sample conservation planning queries
    test_queries = [
        "What threatens the coastal ecosystems?",
        "Which strategies are most effective?",
        "How does fire management help wildlife?",
        "What indicators track water quality?",
        "Show me threats near forest areas",
        "What is the status of our conservation targets?"
    ]
    
    try:
        # Initialize the GraphRAG system
        print("\n1. Initializing GraphRAG system...")
        graphrag = MiradiGraphRAG()
        print("   ✅ System initialized successfully")
        
        # Get database overview
        print("\n2. Checking database connection...")
        db_stats = graphrag.get_database_overview()
        if db_stats:
            print(f"   ✅ Connected to database")
            print(f"   📊 Total nodes: {db_stats.get('total_nodes', 'Unknown')}")
            print(f"   🔗 Total relationships: {db_stats.get('total_relationships', 'Unknown')}")
        else:
            print("   ⚠️  Database statistics not available")
        
        # Test each query
        print(f"\n3. Testing {len(test_queries)} conservation queries...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Query {i}: {query} ---")
            
            try:
                # Process the query through the complete pipeline
                result = graphrag.process_query(query)
                
                # Extract results
                intent = result['intent']
                retrieval = result['retrieval']
                context = result['context']
                
                # Display results
                print(f"   🎯 Category: {intent['category']}")
                print(f"   📈 Confidence: {intent['confidence']:.2f}")
                print(f"   🔍 Retrieved: {retrieval['record_count']} records")
                print(f"   ⏱️  Query time: {retrieval['execution_time']:.3f}s")
                print(f"   📝 Context tokens: {context['token_count']}")
                
                # Show keywords if any
                if intent['keywords']:
                    print(f"   🏷️  Keywords: {', '.join(intent['keywords'])}")
                
                # Show brief summary
                summary = context['graph_summary']
                if summary:
                    first_line = summary.split('\n')[0]
                    print(f"   📋 Summary: {first_line}")
                
                print("   ✅ Query processed successfully")
                
            except Exception as e:
                print(f"   ❌ Error processing query: {e}")
        
        # Show available query categories
        print(f"\n4. Available query categories:")
        suggestions = graphrag.get_suggested_queries()
        for category in suggestions.keys():
            print(f"   • {category.replace('_', ' ').title()}")
        
        # Close the system
        graphrag.close()
        print(f"\n✅ GraphRAG system test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ GraphRAG system test failed: {e}")
        return False


def test_specific_query():
    """Test a specific user-provided query."""
    print("\n" + "=" * 50)
    print("🔍 Test a Specific Conservation Query")
    print("=" * 50)
    
    # Get user input
    query = input("\nEnter your conservation planning question: ").strip()
    
    if not query:
        print("No query provided. Skipping specific test.")
        return
    
    try:
        # Initialize system
        graphrag = MiradiGraphRAG()
        
        # Process the query
        print(f"\nProcessing: {query}")
        result = graphrag.process_query(query)
        
        # Display detailed results
        print(f"\n📊 Analysis Results:")
        intent = result['intent']
        print(f"   Category: {intent['category']}")
        print(f"   Confidence: {intent['confidence']:.2f}")
        print(f"   Keywords: {intent['keywords']}")
        print(f"   Entities: {intent['entities']}")
        
        print(f"\n🔍 Data Retrieval:")
        retrieval = result['retrieval']
        print(f"   Pattern: {retrieval['pattern_used']}")
        print(f"   Records: {retrieval['record_count']}")
        print(f"   Time: {retrieval['execution_time']:.3f}s")
        
        print(f"\n📝 Generated Context:")
        context = result['context']
        print(f"   Token count: {context['token_count']}")
        
        # Show graph summary
        print(f"\n📋 Graph Summary:")
        print(context['graph_summary'])
        
        # Show system prompt preview
        print(f"\n🤖 System Prompt Preview (first 200 chars):")
        print(f"   {context['system_prompt'][:200]}...")
        
        graphrag.close()
        print(f"\n✅ Specific query test completed!")
        
    except Exception as e:
        print(f"\n❌ Error testing specific query: {e}")


if __name__ == "__main__":
    print("🚀 Miradi Co-Pilot GraphRAG System Test")
    print("This script tests the natural language interface for conservation planning.")
    print("\nMake sure you have:")
    print("• Neo4j running with conservation data loaded")
    print("• Proper environment variables set (NEO4J_PASSWORD, etc.)")
    
    # Run the main test
    success = test_graphrag_system()
    
    if success:
        # Offer to test a specific query
        print("\n" + "=" * 50)
        response = input("Would you like to test a specific query? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            test_specific_query()
    
    print(f"\n🎉 Test session completed!")
    print(f"\nTo use the GraphRAG system in your code:")
    print(f"   from src.graphrag import MiradiGraphRAG")
    print(f"   graphrag = MiradiGraphRAG()")
    print(f"   result = graphrag.process_query('Your conservation question')")
