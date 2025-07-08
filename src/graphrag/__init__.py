"""
Miradi Co-Pilot GraphRAG Module

This module provides natural language interface capabilities for querying Miradi conservation
project data stored in Neo4j graph database. It combines graph retrieval with language model
generation to answer complex conservation planning questions.

Key Components:
- context_retriever: Extract relevant conservation subgraphs
- conservation_prompts: Domain-specific prompt templates
- query_router: Route natural language queries to graph patterns
- context_assembler: Combine graph and text context for LLM consumption
- llm_integration: Claude Sonnet 3.5 integration for natural language responses
- engine: Complete GraphRAG pipeline orchestration
- config: Configuration management for API keys and settings
"""

from .context_retriever import ConservationContextRetriever
from .conservation_prompts import ConservationPromptTemplates
from .query_router import ConservationQueryRouter
from .context_assembler import ConservationContextAssembler
from .llm_integration import LLMManager, ClaudeLLMProvider, LLMResponse
from .engine import MiradiGraphRAGEngine, GraphRAGResponse, create_graphrag_engine
from .config import get_config, validate_config, create_env_template
from .example_usage import MiradiGraphRAG

__version__ = "2.0.0"
__author__ = "Miradi Co-Pilot Team"

__all__ = [
    # Core GraphRAG Components
    "ConservationContextRetriever",
    "ConservationPromptTemplates", 
    "ConservationQueryRouter",
    "ConservationContextAssembler",
    
    # LLM Integration
    "LLMManager",
    "ClaudeLLMProvider", 
    "LLMResponse",
    
    # Complete Engine
    "MiradiGraphRAGEngine",
    "GraphRAGResponse",
    "create_graphrag_engine",
    
    # Configuration
    "get_config",
    "validate_config",
    "create_env_template",
    
    # Legacy
    "MiradiGraphRAG"
]
