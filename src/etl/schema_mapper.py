"""
Miradi Schema Mapper

This module converts parsed Miradi XML data into graph format using the models defined in src/graph/models.py.
It handles the complex mapping from Miradi's XML structure to Neo4j-compatible nodes and relationships while
preserving conservation semantics and visual diagram information.

The mapper processes all must-support elements and creates appropriate graph structures for GraphRAG queries
and conservation analysis.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from ..graph.models import (
    MiradiNode, MiradiRelationship, GraphConversionResult,
    NodeType, RelationshipType,
    create_conservation_target_node, create_threat_node, 
    create_strategy_node, create_activity_node,
    create_threatens_relationship, create_implements_relationship,
    create_belongs_to_project_relationship
)

# Set up logging
logger = logging.getLogger(__name__)


class MiradiToGraphMapper:
    """
    Converts parsed Miradi data to graph format.
    
    This class handles the complex mapping from Miradi XML elements to graph nodes and relationships,
    preserving conservation semantics while optimizing for graph database operations.
    """
    
    def __init__(self):
        """Initialize the mapper with tracking for processed elements."""
        self.processed_elements: Set[str] = set()
        self.element_id_to_uuid: Dict[str, str] = {}
        self.diagram_factor_mappings: Dict[str, str] = {}  # DiagramFactorId -> WrappedFactorId
        
    def map_project_to_graph(self, parsed_data: Dict[str, Any]) -> GraphConversionResult:
        """
        Convert parsed Miradi data to graph format.
        
        Args:
            parsed_data: Dictionary containing parsed Miradi elements from MiradiParser
            
        Returns:
            GraphConversionResult containing nodes, relationships, and statistics
        """
        logger.info("Starting Miradi to graph conversion")
        start_time = datetime.now()
        
        # Initialize result container
        result = GraphConversionResult()
        
        try:
            # Extract project metadata for context
            project_metadata = parsed_data.get('project_metadata', {})
            result.source_file = project_metadata.get('source_file', 'unknown')
            
            logger.info(f"Converting project: {project_metadata.get('name', 'Unnamed Project')}")
            
            # Build element ID to UUID mapping for relationship creation
            self._build_id_uuid_mapping(parsed_data)
            
            # Build diagram factor mappings
            self._build_diagram_factor_mappings(parsed_data)
            
            # Create project node
            project_node = self._create_project_node(project_metadata)
            result.add_node(project_node)
            project_id = project_node.id
            
            # Create conservation element nodes
            conservation_targets = self._create_conservation_target_nodes(
                parsed_data.get('conservation_targets', [])
            )
            for node in conservation_targets:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            threats = self._create_threat_nodes(parsed_data.get('threats', []))
            for node in threats:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            strategies = self._create_strategy_nodes(parsed_data.get('strategies', []))
            for node in strategies:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            activities = self._create_activity_nodes(parsed_data.get('activities', []))
            for node in activities:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            # Create monitoring and planning nodes
            intermediate_results = self._create_intermediate_result_nodes(
                parsed_data.get('intermediate_results', [])
            )
            for node in intermediate_results:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            indicators = self._create_indicator_nodes(parsed_data.get('indicators', []))
            for node in indicators:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            objectives = self._create_objective_nodes(parsed_data.get('objectives', []))
            for node in objectives:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            goals = self._create_goal_nodes(parsed_data.get('goals', []))
            for node in goals:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            key_ecological_attributes = self._create_key_ecological_attribute_nodes(
                parsed_data.get('key_ecological_attributes', [])
            )
            for node in key_ecological_attributes:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            contributing_factors = self._create_contributing_factor_nodes(
                parsed_data.get('contributing_factors', [])
            )
            for node in contributing_factors:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            threat_reduction_results = self._create_threat_reduction_result_nodes(
                parsed_data.get('threat_reduction_results', [])
            )
            for node in threat_reduction_results:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            resources = self._create_resource_nodes(parsed_data.get('resources', []))
            for node in resources:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            # Create visual representation nodes
            conceptual_models = self._create_conceptual_model_nodes(
                parsed_data.get('conceptual_models', [])
            )
            for node in conceptual_models:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            results_chains = self._create_results_chain_nodes(
                parsed_data.get('results_chains', [])
            )
            for node in results_chains:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            diagram_factors = self._create_diagram_factor_nodes(
                parsed_data.get('diagram_factors', [])
            )
            for node in diagram_factors:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            diagram_links = self._create_diagram_link_nodes(
                parsed_data.get('diagram_links', [])
            )
            for node in diagram_links:
                result.add_node(node)
                result.add_relationship(
                    create_belongs_to_project_relationship(node.id, project_id)
                )
            
            # Create relationships between elements
            relationships = self._create_relationships(parsed_data)
            for relationship in relationships:
                result.add_relationship(relationship)
            
            # Create diagram-specific relationships
            diagram_relationships = self._create_diagram_relationships(parsed_data)
            for relationship in diagram_relationships:
                result.add_relationship(relationship)
            
            # Log conversion summary
            conversion_time = datetime.now() - start_time
            logger.info(f"Conversion completed in {conversion_time.total_seconds():.2f} seconds")
            logger.info(f"Created {len(result.nodes)} nodes and {len(result.relationships)} relationships")
            
            # Log node type breakdown
            node_counts = result.stats.get('node_counts', {})
            for node_type, count in node_counts.items():
                logger.info(f"  {node_type}: {count} nodes")
            
            # Validate the result
            validation_errors = result.validate()
            if validation_errors:
                for error in validation_errors:
                    result.add_error(error)
                    logger.error(f"Validation error: {error}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error during graph conversion: {str(e)}"
            logger.error(error_msg, exc_info=True)
            result.add_error(error_msg)
            return result
    
    def _build_id_uuid_mapping(self, parsed_data: Dict[str, Any]):
        """Build mapping from element IDs to UUIDs for relationship creation."""
        logger.debug("Building ID to UUID mapping")
        
        # Map all element types that have IDs and UUIDs
        element_types = [
            'conservation_targets', 'threats', 'strategies', 'activities',
            'intermediate_results', 'indicators', 'objectives', 'resources',
            'conceptual_models', 'results_chains', 'diagram_factors', 'diagram_links'
        ]
        
        for element_type in element_types:
            elements = parsed_data.get(element_type, [])
            for element in elements:
                # Handle both ParsedElement objects and plain dictionaries
                if hasattr(element, 'data'):
                    # ParsedElement object
                    element_data = element.data
                else:
                    # Plain dictionary
                    element_data = element
                
                element_id = element_data.get('id')
                element_uuid = element_data.get('uuid')
                if element_id and element_uuid:
                    self.element_id_to_uuid[element_id] = element_uuid
        
        logger.debug(f"Built mapping for {len(self.element_id_to_uuid)} elements")
    
    def _build_diagram_factor_mappings(self, parsed_data: Dict[str, Any]):
        """Build mapping from DiagramFactor IDs to wrapped element IDs."""
        logger.debug("Building diagram factor mappings")
        
        diagram_factors = parsed_data.get('diagram_factors', [])
        for factor in diagram_factors:
            # Handle both ParsedElement objects and plain dictionaries
            factor_data = self._extract_element_data(factor)
            
            factor_id = factor_data.get('id')
            wrapped_id = factor_data.get('wrapped_factor_id')
            if factor_id and wrapped_id:
                self.diagram_factor_mappings[factor_id] = wrapped_id
        
        logger.debug(f"Built diagram mappings for {len(self.diagram_factor_mappings)} factors")
    
    def _extract_element_data(self, element: Any) -> Dict[str, Any]:
        """
        Extract data from element, handling both ParsedElement objects and plain dictionaries.
        
        Args:
            element: Either a ParsedElement object with .data attribute or a plain dictionary
            
        Returns:
            Dictionary containing element data with processed fields
        """
        if hasattr(element, 'data'):
            # ParsedElement object - merge processed fields with raw data
            data = element.data.copy()
            
            # Add the processed fields from ParsedElement attributes
            if hasattr(element, 'element_id') and element.element_id:
                data['id'] = element.element_id
            if hasattr(element, 'name') and element.name:
                data['name'] = element.name
            if hasattr(element, 'uuid') and element.uuid:
                data['uuid'] = element.uuid
            
            return data
        else:
            # Plain dictionary
            return element
    
    def _create_project_node(self, project_data: Dict[str, Any]) -> MiradiNode:
        """Create the main project node."""
        logger.debug("Creating project node")
        
        project_id = project_data.get('id', 'project_1')
        project_name = project_data.get('name', 'Unnamed Project')
        
        # Extract project properties
        properties = {
            'description': project_data.get('description', ''),
            'start_date': project_data.get('start_date', ''),
            'expected_end_date': project_data.get('expected_end_date', ''),
            'data_effective_date': project_data.get('data_effective_date', ''),
            'currency_symbol': project_data.get('currency_symbol', ''),
            'work_plan_time_unit': project_data.get('work_plan_time_unit', ''),
            'factor_mode': project_data.get('factor_mode', ''),
            'target_mode': project_data.get('target_mode', ''),
            'threat_rating_mode': project_data.get('threat_rating_mode', ''),
            'share_outside_organization': project_data.get('share_outside_organization', ''),
            'source_file': project_data.get('source_file', '')
        }
        
        return MiradiNode(
            id=project_id,
            node_type=NodeType.PROJECT,
            name=project_name,
            properties=properties,
            source_element="ConservationProject"
        )
    
    def _create_conservation_target_nodes(self, targets: List[Any]) -> List[MiradiNode]:
        """Create conservation target nodes from BiodiversityTarget elements."""
        logger.debug(f"Creating {len(targets)} conservation target nodes")
        
        nodes = []
        for target in targets:
            # Extract data from element (handles both ParsedElement and dict)
            target_data = self._extract_element_data(target)
            
            target_id = target_data.get('id')
            target_name = target_data.get('name', f'Target {target_id}')
            target_uuid = target_data.get('uuid')
            
            if not target_id:
                logger.warning("Skipping target without ID")
                continue
            
            # Extract target-specific properties
            properties = {
                'identifier': target_data.get('identifier', ''),
                'details': target_data.get('details', ''),
                'viability_mode': target_data.get('viability_mode', ''),
                'calculated_threat_rating': target_data.get('calculated_threat_rating', ''),
                'calculated_viability_status': target_data.get('calculated_viability_status', ''),
                'comments': target_data.get('comments', ''),
                'current_status_justification': target_data.get('current_status_justification', '')
            }
            
            node = create_conservation_target_node(
                target_id=target_id,
                name=target_name,
                uuid=target_uuid,
                properties=properties
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} conservation target nodes")
        return nodes
    
    def _create_threat_nodes(self, threats: List[Any]) -> List[MiradiNode]:
        """Create threat nodes from Cause elements."""
        logger.debug(f"Creating {len(threats)} threat nodes")
        
        nodes = []
        for threat in threats:
            # Extract data from element (handles both ParsedElement and dict)
            threat_data = self._extract_element_data(threat)
            
            threat_id = threat_data.get('id')
            threat_name = threat_data.get('name', f'Threat {threat_id}')
            threat_uuid = threat_data.get('uuid')
            
            if not threat_id:
                logger.warning("Skipping threat without ID")
                continue
            
            # Extract threat-specific properties
            properties = {
                'identifier': threat_data.get('identifier', ''),
                'details': threat_data.get('details', ''),
                'is_direct_threat': threat_data.get('is_direct_threat', ''),
                'calculated_threat_rating': threat_data.get('calculated_threat_rating', ''),
                'comments': threat_data.get('comments', '')
            }
            
            node = create_threat_node(
                threat_id=threat_id,
                name=threat_name,
                uuid=threat_uuid,
                properties=properties
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} threat nodes")
        return nodes
    
    def _create_strategy_nodes(self, strategies: List[Any]) -> List[MiradiNode]:
        """Create strategy nodes from Strategy elements."""
        logger.debug(f"Creating {len(strategies)} strategy nodes")
        
        nodes = []
        for strategy in strategies:
            # Extract data from element (handles both ParsedElement and dict)
            strategy_data = self._extract_element_data(strategy)
            
            strategy_id = strategy_data.get('id')
            strategy_name = strategy_data.get('name', f'Strategy {strategy_id}')
            strategy_uuid = strategy_data.get('uuid')
            
            if not strategy_id:
                logger.warning("Skipping strategy without ID")
                continue
            
            # Extract strategy-specific properties
            properties = {
                'identifier': strategy_data.get('identifier', ''),
                'details': strategy_data.get('details', ''),
                'status': strategy_data.get('status', ''),
                'feasibility_rating': strategy_data.get('feasibility_rating', ''),
                'impact_rating': strategy_data.get('impact_rating', ''),
                'evidence_confidence': strategy_data.get('evidence_confidence', ''),
                'evidence_notes': strategy_data.get('evidence_notes', ''),
                'comments': strategy_data.get('comments', ''),
                'ordered_activity_ids': str(strategy_data.get('ordered_activity_ids', [])),
                'calculated_costs': strategy_data.get('calculated_costs', ''),
                'timeframe_ids': str(strategy_data.get('timeframe_ids', []))
            }
            
            node = create_strategy_node(
                strategy_id=strategy_id,
                name=strategy_name,
                uuid=strategy_uuid,
                properties=properties
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} strategy nodes")
        return nodes
    
    def _create_activity_nodes(self, activities: List[Any]) -> List[MiradiNode]:
        """Create activity nodes from Task elements."""
        logger.debug(f"Creating {len(activities)} activity nodes")
        
        nodes = []
        for activity in activities:
            # Extract data from element (handles both ParsedElement and dict)
            activity_data = self._extract_element_data(activity)
            
            activity_id = activity_data.get('id')
            activity_name = activity_data.get('name', f'Activity {activity_id}')
            activity_uuid = activity_data.get('uuid')
            
            if not activity_id:
                logger.warning("Skipping activity without ID")
                continue
            
            # Extract activity-specific properties
            properties = {
                'identifier': activity_data.get('identifier', ''),
                'details': activity_data.get('details', ''),
                'comments': activity_data.get('comments', ''),
                'calculated_costs': activity_data.get('calculated_costs', ''),
                'is_monitoring_activity': activity_data.get('is_monitoring_activity', ''),
                'assigned_leader_resource_id': activity_data.get('assigned_leader_resource_id', ''),
                'resource_assignment_ids': str(activity_data.get('resource_assignment_ids', [])),
                'expense_assignment_ids': str(activity_data.get('expense_assignment_ids', [])),
                'timeframe_ids': str(activity_data.get('timeframe_ids', [])),
                'progress_report_ids': str(activity_data.get('progress_report_ids', [])),
                'ordered_sub_task_ids': str(activity_data.get('ordered_sub_task_ids', []))
            }
            
            node = create_activity_node(
                activity_id=activity_id,
                name=activity_name,
                uuid=activity_uuid,
                properties=properties
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} activity nodes")
        return nodes
    
    def _create_intermediate_result_nodes(self, results: List[Any]) -> List[MiradiNode]:
        """Create intermediate result nodes."""
        logger.debug(f"Creating {len(results)} intermediate result nodes")
        
        nodes = []
        for result in results:
            # Extract data from element (handles both ParsedElement and dict)
            result_data = self._extract_element_data(result)
            
            result_id = result_data.get('id')
            result_name = result_data.get('name', f'Result {result_id}')
            result_uuid = result_data.get('uuid')
            
            if not result_id:
                logger.warning("Skipping intermediate result without ID")
                continue
            
            properties = {
                'identifier': result_data.get('identifier', ''),
                'details': result_data.get('details', ''),
                'comments': result_data.get('comments', ''),
                'evidence_notes': result_data.get('evidence_notes', ''),
                'indicator_ids': str(result_data.get('indicator_ids', [])),
                'objective_ids': str(result_data.get('objective_ids', []))
            }
            
            node = MiradiNode(
                id=result_id,
                node_type=NodeType.INTERMEDIATE_RESULT,
                name=result_name,
                uuid=result_uuid,
                properties=properties,
                source_element="IntermediateResult"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} intermediate result nodes")
        return nodes
    
    def _create_indicator_nodes(self, indicators: List[Any]) -> List[MiradiNode]:
        """Create indicator nodes."""
        logger.debug(f"Creating {len(indicators)} indicator nodes")
        
        nodes = []
        for indicator in indicators:
            # Extract data from element (handles both ParsedElement and dict)
            indicator_data = self._extract_element_data(indicator)
            
            indicator_id = indicator_data.get('id')
            indicator_name = indicator_data.get('name', f'Indicator {indicator_id}')
            indicator_uuid = indicator_data.get('uuid')
            
            if not indicator_id:
                logger.warning("Skipping indicator without ID")
                continue
            
            properties = {
                'identifier': indicator_data.get('identifier', ''),
                'details': indicator_data.get('details', ''),
                'comments': indicator_data.get('comments', ''),
                'relevant_activity_ids': str(indicator_data.get('relevant_activity_ids', [])),
                'relevant_strategy_ids': str(indicator_data.get('relevant_strategy_ids', [])),
                'measurement_ids': str(indicator_data.get('measurement_ids', [])),
                'thresholds': indicator_data.get('thresholds', ''),
                'viability_ratings_evidence_confidence': indicator_data.get('viability_ratings_evidence_confidence', ''),
                'viability_ratings_comments': indicator_data.get('viability_ratings_comments', '')
            }
            
            node = MiradiNode(
                id=indicator_id,
                node_type=NodeType.INDICATOR,
                name=indicator_name,
                uuid=indicator_uuid,
                properties=properties,
                source_element="Indicator"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} indicator nodes")
        return nodes
    
    def _create_objective_nodes(self, objectives: List[Any]) -> List[MiradiNode]:
        """Create objective nodes."""
        logger.debug(f"Creating {len(objectives)} objective nodes")
        
        nodes = []
        for objective in objectives:
            # Extract data from element (handles both ParsedElement and dict)
            objective_data = self._extract_element_data(objective)
            
            objective_id = objective_data.get('id')
            objective_name = objective_data.get('name', f'Objective {objective_id}')
            objective_uuid = objective_data.get('uuid')
            
            if not objective_id:
                logger.warning("Skipping objective without ID")
                continue
            
            properties = {
                'identifier': objective_data.get('identifier', ''),
                'evidence_confidence': objective_data.get('evidence_confidence', ''),
                'evidence_notes': objective_data.get('evidence_notes', ''),
                'relevant_activity_ids': str(objective_data.get('relevant_activity_ids', [])),
                'relevant_strategy_ids': str(objective_data.get('relevant_strategy_ids', [])),
                'relevant_indicator_ids': str(objective_data.get('relevant_indicator_ids', []))
            }
            
            node = MiradiNode(
                id=objective_id,
                node_type=NodeType.OBJECTIVE,
                name=objective_name,
                uuid=objective_uuid,
                properties=properties,
                source_element="Objective"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} objective nodes")
        return nodes
    
    def _create_goal_nodes(self, goals: List[Any]) -> List[MiradiNode]:
        """Create goal nodes."""
        logger.debug(f"Creating {len(goals)} goal nodes")
        
        nodes = []
        for goal in goals:
            # Extract data from element (handles both ParsedElement and dict)
            goal_data = self._extract_element_data(goal)
            
            goal_id = goal_data.get('id')
            goal_name = goal_data.get('name', f'Goal {goal_id}')
            goal_uuid = goal_data.get('uuid')
            
            if not goal_id:
                logger.warning("Skipping goal without ID")
                continue
            
            properties = {
                'identifier': goal_data.get('identifier', ''),
                'details': goal_data.get('details', ''),
                'relevant_indicator_ids': str(goal_data.get('relevant_indicator_ids', [])),
                'relevant_strategy_ids': str(goal_data.get('relevant_strategy_ids', []))
            }
            
            node = MiradiNode(
                id=goal_id,
                node_type=NodeType.GOAL,
                name=goal_name,
                uuid=goal_uuid,
                properties=properties,
                source_element="Goal"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} goal nodes")
        return nodes
    
    def _create_key_ecological_attribute_nodes(self, attributes: List[Any]) -> List[MiradiNode]:
        """Create key ecological attribute nodes."""
        logger.debug(f"Creating {len(attributes)} key ecological attribute nodes")
        
        nodes = []
        for attribute in attributes:
            # Extract data from element (handles both ParsedElement and dict)
            attribute_data = self._extract_element_data(attribute)
            
            attribute_id = attribute_data.get('id')
            attribute_name = attribute_data.get('name', f'Key Ecological Attribute {attribute_id}')
            attribute_uuid = attribute_data.get('uuid')
            
            if not attribute_id:
                logger.warning("Skipping key ecological attribute without ID")
                continue
            
            properties = {
                'identifier': attribute_data.get('identifier', ''),
                'details': attribute_data.get('details', ''),
                'indicator_ids': str(attribute_data.get('indicator_ids', []))
            }
            
            node = MiradiNode(
                id=attribute_id,
                node_type=NodeType.KEY_ECOLOGICAL_ATTRIBUTE,
                name=attribute_name,
                uuid=attribute_uuid,
                properties=properties,
                source_element="KeyEcologicalAttribute"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} key ecological attribute nodes")
        return nodes
    
    def _create_contributing_factor_nodes(self, factors: List[Any]) -> List[MiradiNode]:
        """Create contributing factor nodes."""
        logger.debug(f"Creating {len(factors)} contributing factor nodes")
        
        nodes = []
        for factor in factors:
            # Extract data from element (handles both ParsedElement and dict)
            factor_data = self._extract_element_data(factor)
            
            factor_id = factor_data.get('id')
            factor_name = factor_data.get('name', f'Contributing Factor {factor_id}')
            factor_uuid = factor_data.get('uuid')
            
            if not factor_id:
                logger.warning("Skipping contributing factor without ID")
                continue
            
            properties = {
                'identifier': factor_data.get('identifier', ''),
                'details': factor_data.get('details', '')
            }
            
            node = MiradiNode(
                id=factor_id,
                node_type=NodeType.CONTRIBUTING_FACTOR,
                name=factor_name,
                uuid=factor_uuid,
                properties=properties,
                source_element="ContributingFactor"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} contributing factor nodes")
        return nodes
    
    def _create_threat_reduction_result_nodes(self, results: List[Any]) -> List[MiradiNode]:
        """Create threat reduction result nodes."""
        logger.debug(f"Creating {len(results)} threat reduction result nodes")
        
        nodes = []
        for result in results:
            # Extract data from element (handles both ParsedElement and dict)
            result_data = self._extract_element_data(result)
            
            result_id = result_data.get('id')
            result_name = result_data.get('name', f'Threat Reduction Result {result_id}')
            result_uuid = result_data.get('uuid')
            
            if not result_id:
                logger.warning("Skipping threat reduction result without ID")
                continue
            
            properties = {
                'identifier': result_data.get('identifier', ''),
                'details': result_data.get('details', ''),
                'indicator_ids': str(result_data.get('indicator_ids', [])),
                'objective_ids': str(result_data.get('objective_ids', []))
            }
            
            node = MiradiNode(
                id=result_id,
                node_type=NodeType.THREAT_REDUCTION_RESULT,
                name=result_name,
                uuid=result_uuid,
                properties=properties,
                source_element="ThreatReductionResult"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} threat reduction result nodes")
        return nodes
    
    def _create_resource_nodes(self, resources: List[Any]) -> List[MiradiNode]:
        """Create resource nodes."""
        logger.debug(f"Creating {len(resources)} resource nodes")
        
        nodes = []
        for resource in resources:
            # Extract data from element (handles both ParsedElement and dict)
            resource_data = self._extract_element_data(resource)
            
            resource_id = resource_data.get('id')
            resource_name = resource_data.get('given_name', f'Resource {resource_id}')
            resource_uuid = resource_data.get('uuid')
            
            if not resource_id:
                logger.warning("Skipping resource without ID")
                continue
            
            properties = {
                'resource_type': resource_data.get('resource_type', ''),
                'surname': resource_data.get('surname', ''),
                'organization': resource_data.get('organization', ''),
                'email': resource_data.get('email', ''),
                'phone_number': resource_data.get('phone_number', ''),
                'roles_description': resource_data.get('roles_description', ''),
                'comments': resource_data.get('comments', '')
            }
            
            node = MiradiNode(
                id=resource_id,
                node_type=NodeType.RESOURCE,
                name=resource_name,
                uuid=resource_uuid,
                properties=properties,
                source_element="Resource"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} resource nodes")
        return nodes
    
    def _create_conceptual_model_nodes(self, models: List[Any]) -> List[MiradiNode]:
        """Create conceptual model nodes."""
        logger.debug(f"Creating {len(models)} conceptual model nodes")
        
        nodes = []
        for model in models:
            # Extract data from element (handles both ParsedElement and dict)
            model_data = self._extract_element_data(model)
            
            model_id = model_data.get('id')
            model_name = model_data.get('name', f'Conceptual Model {model_id}')
            model_uuid = model_data.get('uuid')
            
            if not model_id:
                logger.warning("Skipping conceptual model without ID")
                continue
            
            properties = {
                'identifier': model_data.get('identifier', ''),
                'details': model_data.get('details', ''),
                'comments': model_data.get('comments', ''),
                'diagram_factor_ids': str(model_data.get('diagram_factor_ids', [])),
                'diagram_link_ids': str(model_data.get('diagram_link_ids', [])),
                'selected_tagged_object_set_ids': str(model_data.get('selected_tagged_object_set_ids', [])),
                'hidden_types_container': model_data.get('hidden_types_container', ''),
                'is_progress_status_display_enabled': model_data.get('is_progress_status_display_enabled', ''),
                'is_result_status_display_enabled': model_data.get('is_result_status_display_enabled', ''),
                'is_tagging_enabled': model_data.get('is_tagging_enabled', ''),
                'zoom_scale': model_data.get('zoom_scale', '')
            }
            
            node = MiradiNode(
                id=model_id,
                node_type=NodeType.CONCEPTUAL_MODEL,
                name=model_name,
                uuid=model_uuid,
                properties=properties,
                source_element="ConceptualModel"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} conceptual model nodes")
        return nodes
    
    def _create_results_chain_nodes(self, chains: List[Any]) -> List[MiradiNode]:
        """Create results chain nodes."""
        logger.debug(f"Creating {len(chains)} results chain nodes")
        
        nodes = []
        for chain in chains:
            # Extract data from element (handles both ParsedElement and dict)
            chain_data = self._extract_element_data(chain)
            
            chain_id = chain_data.get('id')
            chain_name = chain_data.get('name', f'Results Chain {chain_id}')
            chain_uuid = chain_data.get('uuid')
            
            if not chain_id:
                logger.warning("Skipping results chain without ID")
                continue
            
            properties = {
                'identifier': chain_data.get('identifier', ''),
                'details': chain_data.get('details', ''),
                'comments': chain_data.get('comments', ''),
                'diagram_factor_ids': str(chain_data.get('diagram_factor_ids', [])),
                'diagram_link_ids': str(chain_data.get('diagram_link_ids', [])),
                'selected_tagged_object_set_ids': str(chain_data.get('selected_tagged_object_set_ids', [])),
                'hidden_types_container': chain_data.get('hidden_types_container', ''),
                'is_progress_status_display_enabled': chain_data.get('is_progress_status_display_enabled', ''),
                'is_result_status_display_enabled': chain_data.get('is_result_status_display_enabled', ''),
                'is_tagging_enabled': chain_data.get('is_tagging_enabled', ''),
                'zoom_scale': chain_data.get('zoom_scale', '')
            }
            
            node = MiradiNode(
                id=chain_id,
                node_type=NodeType.RESULTS_CHAIN,
                name=chain_name,
                uuid=chain_uuid,
                properties=properties,
                source_element="ResultsChain"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} results chain nodes")
        return nodes
    
    def _create_diagram_factor_nodes(self, factors: List[Any]) -> List[MiradiNode]:
        """Create diagram factor nodes."""
        logger.debug(f"Creating {len(factors)} diagram factor nodes")
        
        nodes = []
        for factor in factors:
            # Extract data from element (handles both ParsedElement and dict)
            factor_data = self._extract_element_data(factor)
            
            factor_id = factor_data.get('id')
            factor_name = f'Diagram Factor {factor_id}'
            factor_uuid = factor_data.get('uuid')
            
            if not factor_id:
                logger.warning("Skipping diagram factor without ID")
                continue
            
            properties = {
                'wrapped_factor_id': factor_data.get('wrapped_factor_id', ''),
                'location': str(factor_data.get('location', {})),
                'size': str(factor_data.get('size', {})),
                'style': factor_data.get('style', ''),
                'z_index': factor_data.get('z_index', ''),
                'font_size': factor_data.get('font_size', ''),
                'font_color': factor_data.get('font_color', ''),
                'font_style': factor_data.get('font_style', ''),
                'background_color': factor_data.get('background_color', ''),
                'tagged_object_set_ids': str(factor_data.get('tagged_object_set_ids', [])),
                'group_box_children_ids': str(factor_data.get('group_box_children_ids', []))
            }
            
            node = MiradiNode(
                id=factor_id,
                node_type=NodeType.DIAGRAM_FACTOR,
                name=factor_name,
                uuid=factor_uuid,
                properties=properties,
                source_element="DiagramFactor"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} diagram factor nodes")
        return nodes
    
    def _create_diagram_link_nodes(self, links: List[Any]) -> List[MiradiNode]:
        """Create diagram link nodes."""
        logger.debug(f"Creating {len(links)} diagram link nodes")
        
        nodes = []
        for link in links:
            # Extract data from element (handles both ParsedElement and dict)
            link_data = self._extract_element_data(link)
            
            link_id = link_data.get('id')
            link_name = f'Diagram Link {link_id}'
            link_uuid = link_data.get('uuid')
            
            if not link_id:
                logger.warning("Skipping diagram link without ID")
                continue
            
            properties = {
                'from_diagram_factor_id': link_data.get('from_diagram_factor_id', ''),
                'to_diagram_factor_id': link_data.get('to_diagram_factor_id', ''),
                'is_bidirectional_link': link_data.get('is_bidirectional_link', ''),
                'is_uncertain_link': link_data.get('is_uncertain_link', ''),
                'z_index': link_data.get('z_index', ''),
                'bend_points': str(link_data.get('bend_points', [])),
                'color': link_data.get('color', ''),
                'annotation': link_data.get('annotation', ''),
                'grouped_diagram_link_ids': str(link_data.get('grouped_diagram_link_ids', []))
            }
            
            node = MiradiNode(
                id=link_id,
                node_type=NodeType.DIAGRAM_LINK,
                name=link_name,
                uuid=link_uuid,
                properties=properties,
                source_element="DiagramLink"
            )
            nodes.append(node)
        
        logger.debug(f"Created {len(nodes)} diagram link nodes")
        return nodes
    
    def _create_relationships(self, parsed_data: Dict[str, Any]) -> List[MiradiRelationship]:
        """Create relationships between conservation elements."""
        logger.debug("Creating conservation relationships")
        logger.debug(f"Creating relationships from parsed data keys: {list(parsed_data.keys())}")
        
        relationships = []
        
        # Create IMPLEMENTS relationships (Activity -> Strategy)
        logger.debug("Creating IMPLEMENTS relationships (Activity -> Strategy)")
        strategies = parsed_data.get('strategies', [])
        implements_count = 0
        
        for strategy in strategies:
            # Extract data from element (handles both ParsedElement and dict)
            strategy_data = self._extract_element_data(strategy)
            
            strategy_id = strategy_data.get('id')
            
            # Look for ordered activity IDs in the strategy data
            activity_ids = []
            
            # Check for StrategyOrderedActivityIds in the raw data structure
            raw_data = strategy_data.get('children', {})
            ordered_activities = raw_data.get('StrategyOrderedActivityIds', {})
            
            if isinstance(ordered_activities, dict):
                activity_children = ordered_activities.get('children', {})
                activity_id_elements = activity_children.get('ActivityId', [])
                
                # Handle both single ActivityId and list of ActivityIds
                if isinstance(activity_id_elements, list):
                    for activity_elem in activity_id_elements:
                        if isinstance(activity_elem, dict) and 'text' in activity_elem:
                            activity_ids.append(activity_elem['text'])
                elif isinstance(activity_id_elements, dict) and 'text' in activity_id_elements:
                    activity_ids.append(activity_id_elements['text'])
            
            logger.debug(f"Strategy {strategy_id} has {len(activity_ids)} activities: {activity_ids}")
            
            for i, activity_id in enumerate(activity_ids):
                if activity_id and strategy_id:
                    rel = create_implements_relationship(
                        activity_id=activity_id,
                        strategy_id=strategy_id,
                        properties={'sequence_order': i}
                    )
                    relationships.append(rel)
                    implements_count += 1
        
        logger.debug(f"Created {implements_count} IMPLEMENTS relationships")
        
        # Create conservation relationships from diagram links
        logger.debug("Creating conservation relationships from diagram links")
        diagram_links = parsed_data.get('diagram_links', [])
        threatens_count = 0
        mitigates_count = 0
        contributes_count = 0
        enhances_count = 0
        
        for link in diagram_links:
            link_data = self._extract_element_data(link)
            
            from_diagram_factor_id = link_data.get('from_diagram_factor_id')
            to_diagram_factor_id = link_data.get('to_diagram_factor_id')
            
            if not from_diagram_factor_id or not to_diagram_factor_id:
                continue
            
            # Get the actual conservation element IDs using diagram factor mappings
            from_element_id = self.diagram_factor_mappings.get(from_diagram_factor_id)
            to_element_id = self.diagram_factor_mappings.get(to_diagram_factor_id)
            
            if not from_element_id or not to_element_id:
                logger.debug(f"Skipping diagram link - missing wrapped factor mapping: {from_diagram_factor_id} -> {to_diagram_factor_id}")
                continue
            
            # Determine relationship type based on element types in the link
            # Extract element types from the raw data structure
            raw_data = link_data.get('children', {})
            
            # Get "from" element type
            from_factor_data = raw_data.get('DiagramLinkFromDiagramFactorId', {})
            from_linkable_data = from_factor_data.get('children', {}).get('LinkableFactorId', {})
            from_children = from_linkable_data.get('children', {})
            from_element_type = None
            for element_type in from_children.keys():
                from_element_type = element_type
                break
            
            # Get "to" element type
            to_factor_data = raw_data.get('DiagramLinkToDiagramFactorId', {})
            to_linkable_data = to_factor_data.get('children', {}).get('LinkableFactorId', {})
            to_children = to_linkable_data.get('children', {})
            to_element_type = None
            for element_type in to_children.keys():
                to_element_type = element_type
                break
            
            logger.debug(f"Diagram link: {from_element_type}({from_element_id}) -> {to_element_type}({to_element_id})")
            
            # Create THREATENS relationships (Threat/Cause -> Target)
            if (from_element_type in ['CauseId', 'DirectThreatId'] and 
                to_element_type in ['BiodiversityTargetId', 'HumanWellbeingTargetId']):
                
                rel = create_threatens_relationship(
                    threat_id=from_element_id,  # Use actual threat element ID
                    target_id=to_element_id,   # Use actual target element ID
                    properties={
                        'threat_type': 'direct',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    }
                )
                relationships.append(rel)
                threatens_count += 1
                logger.debug(f"Created THREATENS: {from_element_id} -> {to_element_id}")
            
            # Create MITIGATES relationships (Strategy -> Threat)
            elif (from_element_type in ['StrategyId'] and 
                  to_element_type in ['CauseId', 'DirectThreatId']):
                
                rel = MiradiRelationship(
                    source_id=from_element_id,  # Use actual strategy element ID
                    target_id=to_element_id,    # Use actual threat element ID
                    relationship_type=RelationshipType.MITIGATES,
                    properties={
                        'mitigation_type': 'direct',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    },
                    source_element="DiagramLink"
                )
                relationships.append(rel)
                mitigates_count += 1
                logger.debug(f"Created MITIGATES: {from_element_id} -> {to_element_id}")
            
            # Create CONTRIBUTES_TO relationships (Strategy -> Result)
            elif (from_element_type in ['StrategyId'] and 
                  to_element_type in ['ThreatReductionResultId', 'IntermediateResultId']):
                
                rel = MiradiRelationship(
                    source_id=from_element_id,  # Use actual strategy element ID
                    target_id=to_element_id,    # Use actual result element ID
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    properties={
                        'contribution_type': 'direct',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    },
                    source_element="DiagramLink"
                )
                relationships.append(rel)
                contributes_count += 1
                logger.debug(f"Created CONTRIBUTES_TO: {from_element_id} -> {to_element_id}")
            
            # Create ENHANCES relationships (Result -> Target)
            elif (from_element_type in ['ThreatReductionResultId', 'IntermediateResultId'] and 
                  to_element_type in ['BiodiversityTargetId', 'HumanWellbeingTargetId']):
                
                rel = MiradiRelationship(
                    source_id=from_element_id,  # Use actual result element ID
                    target_id=to_element_id,    # Use actual target element ID
                    relationship_type=RelationshipType.ENHANCES,
                    properties={
                        'result_type': 'direct',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    },
                    source_element="DiagramLink"
                )
                relationships.append(rel)
                enhances_count += 1
                logger.debug(f"Created ENHANCES: {from_element_id} -> {to_element_id}")
            
            # MISSING: Create CONTRIBUTES_TO relationships (IntermediateResult -> IntermediateResult)
            elif (from_element_type in ['IntermediateResultId'] and 
                  to_element_type in ['IntermediateResultId']):
                
                rel = MiradiRelationship(
                    source_id=from_element_id,  # Use actual IR element ID
                    target_id=to_element_id,    # Use actual IR element ID
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    properties={
                        'contribution_type': 'intermediate_result_chain',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    },
                    source_element="DiagramLink"
                )
                relationships.append(rel)
                contributes_count += 1
                logger.debug(f"Created CONTRIBUTES_TO (IR->IR): {from_element_id} -> {to_element_id}")
            
            # MISSING: Create CONTRIBUTES_TO relationships (IntermediateResult -> ThreatReductionResult)
            elif (from_element_type in ['IntermediateResultId'] and 
                  to_element_type in ['ThreatReductionResultId']):
                
                rel = MiradiRelationship(
                    source_id=from_element_id,  # Use actual IR element ID
                    target_id=to_element_id,    # Use actual TRR element ID
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    properties={
                        'contribution_type': 'intermediate_to_threat_reduction',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    },
                    source_element="DiagramLink"
                )
                relationships.append(rel)
                contributes_count += 1
                logger.debug(f"Created CONTRIBUTES_TO (IR->TRR): {from_element_id} -> {to_element_id}")
            
            # MISSING: Create CONTRIBUTES_TO relationships (ThreatReductionResult -> ThreatReductionResult)
            elif (from_element_type in ['ThreatReductionResultId'] and 
                  to_element_type in ['ThreatReductionResultId']):
                
                rel = MiradiRelationship(
                    source_id=from_element_id,  # Use actual TRR element ID
                    target_id=to_element_id,    # Use actual TRR element ID
                    relationship_type=RelationshipType.CONTRIBUTES_TO,
                    properties={
                        'contribution_type': 'threat_reduction_chain',
                        'source_diagram_link': link_data.get('id'),
                        'from_element_type': from_element_type,
                        'to_element_type': to_element_type,
                        'from_diagram_factor': from_diagram_factor_id,
                        'to_diagram_factor': to_diagram_factor_id
                    },
                    source_element="DiagramLink"
                )
                relationships.append(rel)
                contributes_count += 1
                logger.debug(f"Created CONTRIBUTES_TO (TRR->TRR): {from_element_id} -> {to_element_id}")
        
        logger.debug(f"Created {threatens_count} THREATENS relationships from diagram links")
        logger.debug(f"Created {mitigates_count} MITIGATES relationships from diagram links")
        
        # Create MEASURES relationships (Indicator -> various elements)
        indicators = parsed_data.get('indicators', [])
        for indicator in indicators:
            # Extract data from element (handles both ParsedElement and dict)
            indicator_data = self._extract_element_data(indicator)
            
            indicator_id = indicator_data.get('id')
            
            # Indicators measure activities
            activity_ids = indicator_data.get('relevant_activity_ids', [])
            for activity_id in activity_ids:
                if activity_id and indicator_id:
                    rel = MiradiRelationship(
                        source_id=indicator_id,
                        target_id=activity_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'activity'},
                        source_element="IndicatorRelevantActivityIds"
                    )
                    relationships.append(rel)
            
            # Indicators measure strategies
            strategy_ids = indicator_data.get('relevant_strategy_ids', [])
            for strategy_id in strategy_ids:
                if strategy_id and indicator_id:
                    rel = MiradiRelationship(
                        source_id=indicator_id,
                        target_id=strategy_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'strategy'},
                        source_element="IndicatorRelevantStrategyIds"
                    )
                    relationships.append(rel)
        
        # Create DEFINES relationships (Objective -> various elements)
        objectives = parsed_data.get('objectives', [])
        for objective in objectives:
            # Extract data from element (handles both ParsedElement and dict)
            objective_data = self._extract_element_data(objective)
            
            objective_id = objective_data.get('id')
            
            # Objectives define activities
            activity_ids = objective_data.get('relevant_activity_ids', [])
            for activity_id in activity_ids:
                if activity_id and objective_id:
                    rel = MiradiRelationship(
                        source_id=objective_id,
                        target_id=activity_id,
                        relationship_type=RelationshipType.DEFINES,
                        properties={'definition_type': 'activity'},
                        source_element="ObjectiveRelevantActivityIds"
                    )
                    relationships.append(rel)
            
            # Objectives define strategies
            strategy_ids = objective_data.get('relevant_strategy_ids', [])
            for strategy_id in strategy_ids:
                if strategy_id and objective_id:
                    rel = MiradiRelationship(
                        source_id=objective_id,
                        target_id=strategy_id,
                        relationship_type=RelationshipType.DEFINES,
                        properties={'definition_type': 'strategy'},
                        source_element="ObjectiveRelevantStrategyIds"
                    )
                    relationships.append(rel)
            
            # MISSING: Objectives measure indicators
            indicator_ids = objective_data.get('relevant_indicator_ids', [])
            for indicator_id in indicator_ids:
                if indicator_id and objective_id:
                    rel = MiradiRelationship(
                        source_id=objective_id,
                        target_id=indicator_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'indicator'},
                        source_element="ObjectiveRelevantIndicatorIds"
                    )
                    relationships.append(rel)
        
        # MISSING: Create relationships from Intermediate Results
        logger.debug("Creating relationships from Intermediate Results")
        intermediate_results = parsed_data.get('intermediate_results', [])
        for result in intermediate_results:
            # Extract data from element (handles both ParsedElement and dict)
            result_data = self._extract_element_data(result)
            
            result_id = result_data.get('id')
            
            # Intermediate Results have indicators
            indicator_ids = result_data.get('indicator_ids', [])
            for indicator_id in indicator_ids:
                if indicator_id and result_id:
                    rel = MiradiRelationship(
                        source_id=result_id,
                        target_id=indicator_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'intermediate_result'},
                        source_element="IntermediateResultIndicatorIds"
                    )
                    relationships.append(rel)
            
            # Intermediate Results have objectives
            objective_ids = result_data.get('objective_ids', [])
            for objective_id in objective_ids:
                if objective_id and result_id:
                    rel = MiradiRelationship(
                        source_id=result_id,
                        target_id=objective_id,
                        relationship_type=RelationshipType.DEFINES,
                        properties={'definition_type': 'intermediate_result'},
                        source_element="IntermediateResultObjectiveIds"
                    )
                    relationships.append(rel)
        
        # MISSING: Create relationships from Threat Reduction Results
        logger.debug("Creating relationships from Threat Reduction Results")
        threat_reduction_results = parsed_data.get('threat_reduction_results', [])
        for result in threat_reduction_results:
            # Extract data from element (handles both ParsedElement and dict)
            result_data = self._extract_element_data(result)
            
            result_id = result_data.get('id')
            
            # Threat Reduction Results have indicators
            indicator_ids = result_data.get('indicator_ids', [])
            for indicator_id in indicator_ids:
                if indicator_id and result_id:
                    rel = MiradiRelationship(
                        source_id=result_id,
                        target_id=indicator_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'threat_reduction_result'},
                        source_element="ThreatReductionResultIndicatorIds"
                    )
                    relationships.append(rel)
            
            # Threat Reduction Results have objectives
            objective_ids = result_data.get('objective_ids', [])
            for objective_id in objective_ids:
                if objective_id and result_id:
                    rel = MiradiRelationship(
                        source_id=result_id,
                        target_id=objective_id,
                        relationship_type=RelationshipType.DEFINES,
                        properties={'definition_type': 'threat_reduction_result'},
                        source_element="ThreatReductionResultObjectiveIds"
                    )
                    relationships.append(rel)
        
        # MISSING: Create relationships from Goals
        logger.debug("Creating relationships from Goals")
        goals = parsed_data.get('goals', [])
        for goal in goals:
            # Extract data from element (handles both ParsedElement and dict)
            goal_data = self._extract_element_data(goal)
            
            goal_id = goal_data.get('id')
            
            # Goals relate to strategies
            strategy_ids = goal_data.get('relevant_strategy_ids', [])
            for strategy_id in strategy_ids:
                if strategy_id and goal_id:
                    rel = MiradiRelationship(
                        source_id=goal_id,
                        target_id=strategy_id,
                        relationship_type=RelationshipType.DEFINES,
                        properties={'definition_type': 'goal_strategy'},
                        source_element="GoalRelevantStrategyIds"
                    )
                    relationships.append(rel)
            
            # Goals relate to indicators
            indicator_ids = goal_data.get('relevant_indicator_ids', [])
            for indicator_id in indicator_ids:
                if indicator_id and goal_id:
                    rel = MiradiRelationship(
                        source_id=goal_id,
                        target_id=indicator_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'goal'},
                        source_element="GoalRelevantIndicatorIds"
                    )
                    relationships.append(rel)
        
        # MISSING: Create relationships from Key Ecological Attributes
        logger.debug("Creating relationships from Key Ecological Attributes")
        key_ecological_attributes = parsed_data.get('key_ecological_attributes', [])
        for attribute in key_ecological_attributes:
            # Extract data from element (handles both ParsedElement and dict)
            attribute_data = self._extract_element_data(attribute)
            
            attribute_id = attribute_data.get('id')
            
            # Key Ecological Attributes have indicators
            indicator_ids = attribute_data.get('indicator_ids', [])
            for indicator_id in indicator_ids:
                if indicator_id and attribute_id:
                    rel = MiradiRelationship(
                        source_id=attribute_id,
                        target_id=indicator_id,
                        relationship_type=RelationshipType.MEASURES,
                        properties={'measurement_type': 'key_ecological_attribute'},
                        source_element="KeyEcologicalAttributeIndicatorIds"
                    )
                    relationships.append(rel)
        
        # Create CONTAINS relationships (Model/Chain -> DiagramFactor)
        conceptual_models = parsed_data.get('conceptual_models', [])
        for model in conceptual_models:
            # Extract data from element (handles both ParsedElement and dict)
            model_data = self._extract_element_data(model)
            
            model_id = model_data.get('id')
            factor_ids = model_data.get('diagram_factor_ids', [])
            
            for factor_id in factor_ids:
                if factor_id and model_id:
                    rel = MiradiRelationship(
                        source_id=model_id,
                        target_id=factor_id,
                        relationship_type=RelationshipType.CONTAINS,
                        properties={'container_type': 'conceptual_model'},
                        source_element="ConceptualModelDiagramFactorIds"
                    )
                    relationships.append(rel)
        
        results_chains = parsed_data.get('results_chains', [])
        for chain in results_chains:
            # Extract data from element (handles both ParsedElement and dict)
            chain_data = self._extract_element_data(chain)
            
            chain_id = chain_data.get('id')
            factor_ids = chain_data.get('diagram_factor_ids', [])
            
            for factor_id in factor_ids:
                if factor_id and chain_id:
                    rel = MiradiRelationship(
                        source_id=chain_id,
                        target_id=factor_id,
                        relationship_type=RelationshipType.CONTAINS,
                        properties={'container_type': 'results_chain'},
                        source_element="ResultsChainDiagramFactorIds"
                    )
                    relationships.append(rel)
        
        logger.debug(f"Created {len(relationships)} conservation relationships")
        return relationships
    
    def _create_diagram_relationships(self, parsed_data: Dict[str, Any]) -> List[MiradiRelationship]:
        """Create diagram-specific relationships."""
        logger.debug("Creating diagram relationships")
        
        relationships = []
        
        # Create HAS_DIAGRAM_REPRESENTATION relationships (Element -> DiagramFactor)
        diagram_factors = parsed_data.get('diagram_factors', [])
        for factor in diagram_factors:
            # Extract data from element (handles both ParsedElement and dict)
            factor_data = self._extract_element_data(factor)
            
            factor_id = factor_data.get('id')
            wrapped_id = factor_data.get('wrapped_factor_id')
            
            if factor_id and wrapped_id:
                rel = MiradiRelationship(
                    source_id=wrapped_id,
                    target_id=factor_id,
                    relationship_type=RelationshipType.PART_OF,  # Using PART_OF for diagram representation
                    properties={'representation_type': 'diagram_factor'},
                    source_element="DiagramFactorWrappedFactorId"
                )
                relationships.append(rel)
        
        # Create LINKS relationships (DiagramLink -> DiagramFactor connections)
        diagram_links = parsed_data.get('diagram_links', [])
        for link in diagram_links:
            # Extract data from element (handles both ParsedElement and dict)
            link_data = self._extract_element_data(link)
            
            link_id = link_data.get('id')
            from_factor_id = link_data.get('from_diagram_factor_id')
            to_factor_id = link_data.get('to_diagram_factor_id')
            
            if link_id and from_factor_id:
                # Link connects from a diagram factor
                rel = MiradiRelationship(
                    source_id=link_id,
                    target_id=from_factor_id,
                    relationship_type=RelationshipType.LINKS,
                    properties={
                        'link_direction': 'from',
                        'is_bidirectional': link_data.get('is_bidirectional_link', ''),
                        'is_uncertain': link_data.get('is_uncertain_link', '')
                    },
                    source_element="DiagramLinkFromDiagramFactorId"
                )
                relationships.append(rel)
            
            if link_id and to_factor_id:
                # Link connects to a diagram factor
                rel = MiradiRelationship(
                    source_id=link_id,
                    target_id=to_factor_id,
                    relationship_type=RelationshipType.LINKS,
                    properties={
                        'link_direction': 'to',
                        'is_bidirectional': link_data.get('is_bidirectional_link', ''),
                        'is_uncertain': link_data.get('is_uncertain_link', '')
                    },
                    source_element="DiagramLinkToDiagramFactorId"
                )
                relationships.append(rel)
        
        logger.debug(f"Created {len(relationships)} diagram relationships")
        return relationships


# Utility function for external use
def convert_miradi_to_graph(parsed_data: Dict[str, Any]) -> GraphConversionResult:
    """
    Convenience function to convert parsed Miradi data to graph format.
    
    Args:
        parsed_data: Dictionary containing parsed Miradi elements from MiradiParser
        
    Returns:
        GraphConversionResult containing nodes, relationships, and statistics
    """
    mapper = MiradiToGraphMapper()
    return mapper.map_project_to_graph(parsed_data)
