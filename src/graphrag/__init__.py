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
"""

from .context_retriever import ConservationContextRetriever
from .conservation_prompts import ConservationPromptTemplates
from .query_router import ConservationQueryRouter
from .context_assembler import ConservationContextAssembler
from .example_usage import MiradiGraphRAG

__version__ = "1.0.0"
__author__ = "Miradi Co-Pilot Team"

__all__ = [
    "ConservationContextRetriever",
    "ConservationPromptTemplates", 
    "ConservationQueryRouter",
    "ConservationContextAssembler",
    "MiradiGraphRAG"
]
