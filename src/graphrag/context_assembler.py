"""
Conservation Context Assembler

This module combines graph data with textual context to create comprehensive
input for language model generation in conservation planning analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.graphrag.context_retriever import RetrievalResult
from src.graphrag.conservation_prompts import ConservationPromptTemplates, PromptTemplate
from src.graphrag.query_router import QueryIntent


@dataclass
class AssembledContext:
    """Container for assembled context ready for LLM consumption."""
    system_prompt: str
    user_prompt: str
    graph_summary: str
    metadata: Dict[str, Any]
    token_count: int


class ConservationContextAssembler:
    """
    Assembles comprehensive context for conservation planning queries.
    
    This class combines graph retrieval results with domain-specific prompts
    to create well-structured input for language model generation.
    """
    
    def __init__(self):
        """Initialize the context assembler."""
        self.logger = logging.getLogger(__name__)
        self.prompt_templates = ConservationPromptTemplates()
    
    def assemble_context(
        self,
        query_intent: QueryIntent,
        retrieval_result: RetrievalResult,
        additional_context: Optional[Dict[str, str]] = None
    ) -> AssembledContext:
        """
        Assemble complete context for conservation planning analysis.
        
        Args:
            query_intent: Parsed query intent and parameters
            retrieval_result: Graph data retrieval results
            additional_context: Optional additional context information
            
        Returns:
            AssembledContext ready for LLM consumption
        """
        # Get appropriate prompt template
        template = self.prompt_templates.get_template_by_category(query_intent.category)
        
        # Format graph data into readable context
        graph_context = self._format_graph_context(retrieval_result)
        
        # Create additional context dictionary
        context_dict = additional_context or {}
        context_dict.update(self._create_context_supplements(retrieval_result, query_intent))
        
        # Generate complete prompt
        full_prompt = self.prompt_templates.create_full_prompt(
            template=template,
            query=query_intent.parameters.get('query', ''),
            graph_context=graph_context,
            additional_context=context_dict
        )
        
        # Create metadata
        metadata = self._create_metadata(query_intent, retrieval_result)
        
        # Estimate token count (rough approximation)
        token_count = self._estimate_token_count(full_prompt['system'] + full_prompt['user'])
        
        self.logger.info(f"Assembled context for {query_intent.category} query ({token_count} tokens)")
        
        return AssembledContext(
            system_prompt=full_prompt['system'],
            user_prompt=full_prompt['user'],
            graph_summary=self._create_graph_summary(retrieval_result),
            metadata=metadata,
            token_count=token_count
        )
    
    def _format_graph_context(self, retrieval_result: RetrievalResult) -> str:
        """
        Format graph retrieval results into readable context.
        
        Args:
            retrieval_result: Graph data from context retriever
            
        Returns:
            Formatted string representation of graph data
        """
        if not retrieval_result.graph_data:
            return "No relevant conservation data found in the database."
        
        # Group data by conservation element types
        elements_by_type = {}
        relationships = []
        
        for record in retrieval_result.graph_data:
            # Process nodes
            for key, value in record.items():
                if isinstance(value, dict) and 'name' in value:
                    element_type = value.get('node_type', 'Unknown')
                    if element_type not in elements_by_type:
                        elements_by_type[element_type] = []
                    
                    # Create element description
                    element_desc = {
                        'name': value.get('name', 'Unnamed'),
                        'id': value.get('id', ''),
                        'details': value.get('details', ''),
                        'status': value.get('status', ''),
                        'type': element_type
                    }
                    
                    # Add type-specific attributes
                    if element_type == 'CONSERVATION_TARGET':
                        element_desc['viability'] = value.get('viability_rating', '')
                    elif element_type == 'THREAT':
                        element_desc['severity'] = value.get('severity', '')
                        element_desc['scope'] = value.get('scope', '')
                    elif element_type == 'STRATEGY':
                        element_desc['status'] = value.get('status', '')
                    
                    elements_by_type[element_type].append(element_desc)
                
                # Process relationships
                elif key.endswith('_name') and 'relationship_type' in record:
                    rel_type = record.get('relationship_type', 'RELATED')
                    source = record.get('element1_name', record.get('source_name', ''))
                    target = record.get('element2_name', record.get('target_name', ''))
                    
                    if source and target:
                        relationships.append(f"{source} {rel_type} {target}")
        
        # Format the context
        context_parts = []
        
        # Add conservation elements by type
        for element_type, elements in elements_by_type.items():
            if elements:
                context_parts.append(f"\n{element_type.replace('_', ' ').title()}s:")
                for element in elements[:10]:  # Limit to first 10 elements
                    name = element['name']
                    details = element.get('details', '')
                    
                    if element_type == 'CONSERVATION_TARGET' and element.get('viability'):
                        context_parts.append(f"- {name} (Viability: {element['viability']})")
                    elif element_type == 'THREAT' and element.get('severity'):
                        context_parts.append(f"- {name} (Severity: {element['severity']})")
                    elif element_type == 'STRATEGY' and element.get('status'):
                        context_parts.append(f"- {name} (Status: {element['status']})")
                    else:
                        context_parts.append(f"- {name}")
                    
                    if details:
                        context_parts.append(f"  Details: {details}")
        
        # Add relationships
        if relationships:
            context_parts.append("\nConservation Relationships:")
            for rel in relationships[:15]:  # Limit to first 15 relationships
                context_parts.append(f"- {rel}")
        
        return "\n".join(context_parts) if context_parts else "No conservation data available."
    
    def _create_context_supplements(
        self,
        retrieval_result: RetrievalResult,
        query_intent: QueryIntent
    ) -> Dict[str, str]:
        """
        Create supplementary context based on query category and results.
        
        Args:
            retrieval_result: Graph retrieval results
            query_intent: Query intent and parameters
            
        Returns:
            Dictionary of supplementary context
        """
        supplements = {}
        
        # Add query metadata
        supplements['query_category'] = query_intent.category
        supplements['confidence'] = f"{query_intent.confidence:.2f}"
        supplements['record_count'] = str(retrieval_result.record_count)
        supplements['execution_time'] = f"{retrieval_result.execution_time:.3f}s"
        
        # Category-specific supplements
        if query_intent.category == 'threat_analysis':
            supplements['relationships'] = self._extract_threat_relationships(retrieval_result)
            supplements['spatial_info'] = self._extract_spatial_info(retrieval_result)
        
        elif query_intent.category == 'strategy_evaluation':
            supplements['implementation_data'] = self._extract_implementation_data(retrieval_result)
            supplements['mitigation_relationships'] = self._extract_mitigation_relationships(retrieval_result)
        
        elif query_intent.category == 'theory_of_change':
            supplements['pathway_data'] = self._extract_pathway_data(retrieval_result)
            supplements['results_chain_info'] = self._extract_results_chain_info(retrieval_result)
        
        elif query_intent.category == 'monitoring':
            supplements['indicator_data'] = self._extract_indicator_data(retrieval_result)
            supplements['measurement_info'] = self._extract_measurement_info(retrieval_result)
        
        elif query_intent.category == 'spatial_analysis':
            supplements['spatial_relationships'] = self._extract_spatial_relationships(retrieval_result)
            supplements['coordinate_info'] = self._extract_coordinate_info(retrieval_result)
        
        elif query_intent.category == 'target_analysis':
            supplements['viability_data'] = self._extract_viability_data(retrieval_result)
            supplements['threat_relationships'] = self._extract_target_threat_relationships(retrieval_result)
            supplements['enhancement_info'] = self._extract_enhancement_info(retrieval_result)
        
        else:  # general queries
            supplements['relationship_data'] = self._extract_general_relationships(retrieval_result)
            supplements['supplementary_info'] = self._extract_general_info(retrieval_result)
        
        return supplements
    
    def _extract_threat_relationships(self, retrieval_result: RetrievalResult) -> str:
        """Extract threat-specific relationships."""
        relationships = []
        for record in retrieval_result.graph_data:
            if record.get('relationship_type') == 'THREATENS':
                threat = record.get('threat_name', '')
                target = record.get('target_name', '')
                if threat and target:
                    relationships.append(f"{threat} threatens {target}")
        
        return "\n".join(relationships) if relationships else "No threat relationships found."
    
    def _extract_spatial_info(self, retrieval_result: RetrievalResult) -> str:
        """Extract spatial information."""
        spatial_info = []
        for record in retrieval_result.graph_data:
            if 'coordinates' in record or 'location' in record:
                element = record.get('element_name', '')
                location = record.get('coordinates', record.get('location', ''))
                if element and location:
                    spatial_info.append(f"{element}: {location}")
        
        return "\n".join(spatial_info) if spatial_info else "No spatial information available."
    
    def _extract_implementation_data(self, retrieval_result: RetrievalResult) -> str:
        """Extract strategy implementation data."""
        implementations = []
        for record in retrieval_result.graph_data:
            if record.get('relationship_type') == 'IMPLEMENTS':
                activity = record.get('activity_name', '')
                strategy = record.get('strategy_name', '')
                if activity and strategy:
                    implementations.append(f"{activity} implements {strategy}")
        
        return "\n".join(implementations) if implementations else "No implementation data found."
    
    def _extract_mitigation_relationships(self, retrieval_result: RetrievalResult) -> str:
        """Extract mitigation relationships."""
        mitigations = []
        for record in retrieval_result.graph_data:
            if record.get('relationship_type') == 'MITIGATES':
                strategy = record.get('strategy_name', '')
                threat = record.get('threat_name', '')
                if strategy and threat:
                    mitigations.append(f"{strategy} mitigates {threat}")
        
        return "\n".join(mitigations) if mitigations else "No mitigation relationships found."
    
    def _extract_pathway_data(self, retrieval_result: RetrievalResult) -> str:
        """Extract theory of change pathway data."""
        pathways = []
        for record in retrieval_result.graph_data:
            rel_type = record.get('relationship_type', '')
            if rel_type in ['CONTRIBUTES_TO', 'ENHANCES']:
                source = record.get('source_name', '')
                target = record.get('target_name', '')
                if source and target:
                    pathways.append(f"{source} {rel_type.lower().replace('_', ' ')} {target}")
        
        return "\n".join(pathways) if pathways else "No pathway data found."
    
    def _extract_results_chain_info(self, retrieval_result: RetrievalResult) -> str:
        """Extract results chain information."""
        chains = []
        for record in retrieval_result.graph_data:
            chain_name = record.get('results_chain_name', '')
            if chain_name:
                chains.append(f"Results Chain: {chain_name}")
        
        return "\n".join(set(chains)) if chains else "No results chain information found."
    
    def _extract_indicator_data(self, retrieval_result: RetrievalResult) -> str:
        """Extract indicator data."""
        indicators = []
        for record in retrieval_result.graph_data:
            if record.get('relationship_type') == 'MEASURES':
                indicator = record.get('indicator_name', '')
                element = record.get('element_name', '')
                if indicator and element:
                    indicators.append(f"{indicator} measures {element}")
        
        return "\n".join(indicators) if indicators else "No indicator data found."
    
    def _extract_measurement_info(self, retrieval_result: RetrievalResult) -> str:
        """Extract measurement information."""
        measurements = []
        for record in retrieval_result.graph_data:
            indicator = record.get('indicator_name', '')
            details = record.get('indicator_details', '')
            if indicator:
                if details:
                    measurements.append(f"{indicator}: {details}")
                else:
                    measurements.append(indicator)
        
        return "\n".join(measurements) if measurements else "No measurement information found."
    
    def _extract_spatial_relationships(self, retrieval_result: RetrievalResult) -> str:
        """Extract spatial relationships."""
        spatial_rels = []
        for record in retrieval_result.graph_data:
            element1 = record.get('element1_name', '')
            element2 = record.get('element2_name', '')
            distance = record.get('distance', '')
            if element1 and element2:
                if distance:
                    spatial_rels.append(f"{element1} is {distance} units from {element2}")
                else:
                    spatial_rels.append(f"{element1} is spatially related to {element2}")
        
        return "\n".join(spatial_rels) if spatial_rels else "No spatial relationships found."
    
    def _extract_coordinate_info(self, retrieval_result: RetrievalResult) -> str:
        """Extract coordinate information."""
        coordinates = []
        for record in retrieval_result.graph_data:
            element = record.get('element_name', '')
            x = record.get('x', '')
            y = record.get('y', '')
            if element and x and y:
                coordinates.append(f"{element}: ({x}, {y})")
        
        return "\n".join(coordinates) if coordinates else "No coordinate information found."
    
    def _extract_viability_data(self, retrieval_result: RetrievalResult) -> str:
        """Extract target viability data."""
        viability = []
        for record in retrieval_result.graph_data:
            target = record.get('target_name', '')
            viability_rating = record.get('viability', '')
            if target and viability_rating:
                viability.append(f"{target}: {viability_rating}")
        
        return "\n".join(viability) if viability else "No viability data found."
    
    def _extract_target_threat_relationships(self, retrieval_result: RetrievalResult) -> str:
        """Extract target-threat relationships."""
        threats = []
        for record in retrieval_result.graph_data:
            target = record.get('target_name', '')
            threat = record.get('threat_name', '')
            severity = record.get('threat_severity', '')
            if target and threat:
                if severity:
                    threats.append(f"{threat} (severity: {severity}) threatens {target}")
                else:
                    threats.append(f"{threat} threatens {target}")
        
        return "\n".join(threats) if threats else "No target-threat relationships found."
    
    def _extract_enhancement_info(self, retrieval_result: RetrievalResult) -> str:
        """Extract target enhancement information."""
        enhancements = []
        for record in retrieval_result.graph_data:
            if record.get('relationship_type') == 'ENHANCES':
                result = record.get('result_name', '')
                target = record.get('target_name', '')
                if result and target:
                    enhancements.append(f"{result} enhances {target}")
        
        return "\n".join(enhancements) if enhancements else "No enhancement information found."
    
    def _extract_general_relationships(self, retrieval_result: RetrievalResult) -> str:
        """Extract general relationships."""
        relationships = []
        for record in retrieval_result.graph_data:
            rel_type = record.get('relationship_type', '')
            source = record.get('element1_name', record.get('source_name', ''))
            target = record.get('element2_name', record.get('target_name', ''))
            if rel_type and source and target:
                relationships.append(f"{source} {rel_type} {target}")
        
        return "\n".join(relationships) if relationships else "No relationships found."
    
    def _extract_general_info(self, retrieval_result: RetrievalResult) -> str:
        """Extract general supplementary information."""
        info = []
        info.append(f"Query pattern used: {retrieval_result.pattern_used}")
        info.append(f"Records retrieved: {retrieval_result.record_count}")
        info.append(f"Execution time: {retrieval_result.execution_time:.3f} seconds")
        
        return "\n".join(info)
    
    def _create_graph_summary(self, retrieval_result: RetrievalResult) -> str:
        """
        Create a concise summary of the graph data.
        
        Args:
            retrieval_result: Graph retrieval results
            
        Returns:
            Brief summary of the retrieved data
        """
        if not retrieval_result.graph_data:
            return "No data retrieved from the conservation database."
        
        # Count elements by type
        element_counts = {}
        relationship_counts = {}
        
        for record in retrieval_result.graph_data:
            for key, value in record.items():
                if isinstance(value, dict) and 'node_type' in value:
                    node_type = value['node_type']
                    element_counts[node_type] = element_counts.get(node_type, 0) + 1
                elif key == 'relationship_type':
                    rel_type = value
                    relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
        
        summary_parts = []
        
        if element_counts:
            summary_parts.append("Conservation Elements:")
            for element_type, count in element_counts.items():
                summary_parts.append(f"- {element_type.replace('_', ' ').title()}: {count}")
        
        if relationship_counts:
            summary_parts.append("Relationships:")
            for rel_type, count in relationship_counts.items():
                summary_parts.append(f"- {rel_type}: {count}")
        
        summary_parts.append(f"Total records: {retrieval_result.record_count}")
        summary_parts.append(f"Query execution: {retrieval_result.execution_time:.3f}s")
        
        return "\n".join(summary_parts)
    
    def _create_metadata(
        self,
        query_intent: QueryIntent,
        retrieval_result: RetrievalResult
    ) -> Dict[str, Any]:
        """
        Create metadata for the assembled context.
        
        Args:
            query_intent: Query intent and parameters
            retrieval_result: Graph retrieval results
            
        Returns:
            Metadata dictionary
        """
        return {
            'query_category': query_intent.category,
            'query_confidence': query_intent.confidence,
            'query_keywords': query_intent.keywords,
            'query_entities': query_intent.entities,
            'graph_pattern': retrieval_result.pattern_used,
            'record_count': retrieval_result.record_count,
            'execution_time': retrieval_result.execution_time,
            'parameters': retrieval_result.parameters
        }
    
    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for the given text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def create_summary_context(self, retrieval_result: RetrievalResult) -> str:
        """
        Create a summary context for quick overview.
        
        Args:
            retrieval_result: Graph retrieval results
            
        Returns:
            Summary context string
        """
        if not retrieval_result.graph_data:
            return "No conservation data available."
        
        # Extract key information
        targets = []
        threats = []
        strategies = []
        
        for record in retrieval_result.graph_data:
            for key, value in record.items():
                if isinstance(value, dict) and 'name' in value:
                    node_type = value.get('node_type', '')
                    name = value.get('name', '')
                    
                    if node_type == 'CONSERVATION_TARGET' and name not in targets:
                        targets.append(name)
                    elif node_type == 'THREAT' and name not in threats:
                        threats.append(name)
                    elif node_type == 'STRATEGY' and name not in strategies:
                        strategies.append(name)
        
        summary_parts = []
        
        if targets:
            summary_parts.append(f"Conservation Targets: {', '.join(targets[:5])}")
            if len(targets) > 5:
                summary_parts.append(f"... and {len(targets) - 5} more")
        
        if threats:
            summary_parts.append(f"Threats: {', '.join(threats[:5])}")
            if len(threats) > 5:
                summary_parts.append(f"... and {len(threats) - 5} more")
        
        if strategies:
            summary_parts.append(f"Strategies: {', '.join(strategies[:5])}")
            if len(strategies) > 5:
                summary_parts.append(f"... and {len(strategies) - 5} more")
        
        return "\n".join(summary_parts) if summary_parts else "Conservation project overview available."
