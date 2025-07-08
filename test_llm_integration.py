"""
Test LLM Integration for Miradi Co-Pilot GraphRAG

This script tests the Claude LLM integration without requiring a full project setup.
It verifies that the LLM components work correctly with proper configuration.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graphrag.config import validate_config, get_config
from src.graphrag.llm_integration import ClaudeLLMProvider, LLMManager
from src.graphrag.conservation_prompts import ConservationPromptTemplates

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test configuration validation."""
    print("🔧 Testing Configuration...")
    
    validation = validate_config()
    
    print(f"Configuration Valid: {validation['valid']}")
    
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    config_info = validation['config']
    print(f"Anthropic API Configured: {config_info['anthropic_configured']}")
    print(f"Primary Model: {config_info['primary_model']}")
    
    return validation['valid']


def test_claude_provider():
    """Test Claude LLM provider directly."""
    print("\n🤖 Testing Claude LLM Provider...")
    
    try:
        # Initialize provider
        provider = ClaudeLLMProvider()
        print(f"✅ Provider initialized with model: {provider.primary_model}")
        
        # Test connection
        print("Testing API connection...")
        connection_ok = provider.test_connection()
        print(f"Connection test: {'✅ Success' if connection_ok else '❌ Failed'}")
        
        if connection_ok:
            # Test simple query
            print("Testing simple conservation query...")
            response = provider.generate_response(
                system_prompt="You are a conservation planning expert.",
                user_prompt="Explain the importance of biodiversity conservation in 2 sentences."
            )
            
            if response.success:
                print(f"✅ Query successful:")
                print(f"   Model: {response.model_used}")
                print(f"   Tokens: {response.tokens_used}")
                print(f"   Cost: ${response.cost_estimate:.4f}")
                print(f"   Response: {response.content[:100]}...")
                return True
            else:
                print(f"❌ Query failed: {response.error_message}")
                return False
        
        return connection_ok
        
    except Exception as e:
        print(f"❌ Provider test failed: {e}")
        return False


def test_llm_manager():
    """Test LLM manager with conservation prompts."""
    print("\n🎯 Testing LLM Manager with Conservation Prompts...")
    
    try:
        # Initialize manager
        manager = LLMManager()
        print("✅ LLM Manager initialized")
        
        # Get conservation prompt template
        prompt_templates = ConservationPromptTemplates()
        template = prompt_templates.get_threat_analysis_template()
        
        # Create test context
        test_context = """
CONSERVATION THREAT DATA:
- Coastal Development: High severity threat affecting marine habitats
- Water Pollution: Medium severity threat from agricultural runoff
- Climate Change: High severity long-term threat to all ecosystems

THREAT RELATIONSHIPS:
- Coastal Development THREATENS Marine Protected Areas
- Water Pollution THREATENS Coral Reef Systems
- Climate Change THREATENS All Conservation Targets
"""
        
        # Create full prompt
        full_prompt = prompt_templates.create_full_prompt(
            template=template,
            query="What are the main threats to marine ecosystems?",
            graph_context=test_context,
            additional_context={
                "relationships": "- Coastal Development THREATENS Marine Protected Areas\n- Water Pollution THREATENS Coral Reef Systems\n- Climate Change THREATENS All Conservation Targets",
                "spatial_info": "Marine ecosystems located in coastal regions"
            }
        )
        
        print("Testing conservation query with domain expertise...")
        response = manager.query_conservation_data(
            system_prompt=full_prompt['system'],
            user_prompt=full_prompt['user'],
            query_category="threat_analysis"
        )
        
        if response.success:
            print(f"✅ Conservation query successful:")
            print(f"   Model: {response.model_used}")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Cost: ${response.cost_estimate:.4f}")
            print(f"   Response length: {len(response.content)} characters")
            print(f"\n💬 Conservation Analysis Preview:")
            print(response.content[:300] + "..." if len(response.content) > 300 else response.content)
            return True
        else:
            print(f"❌ Conservation query failed: {response.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ LLM Manager test failed: {e}")
        return False


def test_system_status():
    """Test system status reporting."""
    print("\n📊 Testing System Status...")
    
    try:
        manager = LLMManager()
        status = manager.get_status()
        
        print(f"Connection Status: {status['connection_status']}")
        print(f"Provider: {status['provider']}")
        print(f"Ready: {status['ready']}")
        
        if 'model_info' in status:
            model_info = status['model_info']
            print(f"Primary Model: {model_info['primary_model']}")
            print(f"Fallback Model: {model_info['fallback_model']}")
            print(f"Max Tokens: {model_info['max_tokens']}")
            print(f"Temperature: {model_info['temperature']}")
        
        return status['ready']
        
    except Exception as e:
        print(f"❌ Status test failed: {e}")
        return False


def main():
    """Run all LLM integration tests."""
    print("🌿 Miradi Co-Pilot LLM Integration Tests")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_configuration()
    
    if not config_ok:
        print("\n❌ Configuration issues detected. Please set ANTHROPIC_API_KEY.")
        print("Create a .env file with:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        return False
    
    # Test Claude provider
    provider_ok = test_claude_provider()
    
    # Test LLM manager
    manager_ok = test_llm_manager()
    
    # Test system status
    status_ok = test_system_status()
    
    # Summary
    print(f"\n📋 Test Summary")
    print("=" * 30)
    print(f"Configuration: {'✅' if config_ok else '❌'}")
    print(f"Claude Provider: {'✅' if provider_ok else '❌'}")
    print(f"LLM Manager: {'✅' if manager_ok else '❌'}")
    print(f"System Status: {'✅' if status_ok else '❌'}")
    
    all_passed = config_ok and provider_ok and manager_ok and status_ok
    print(f"\nOverall: {'✅ All tests passed!' if all_passed else '❌ Some tests failed'}")
    
    if all_passed:
        print("\n🎉 LLM integration is ready for conservation queries!")
        print("Next steps:")
        print("1. Load a Miradi project into Neo4j")
        print("2. Run: python examples/natural_language_queries.py")
        print("3. Try queries like 'What threatens the coastal ecosystems?'")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
