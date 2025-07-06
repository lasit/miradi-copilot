"""
Miradi Graph Models

This module defines the data structures for converting Miradi XML project data into Neo4j graph format.
The models bridge the gap between Miradi's XML schema and the graph database representation used for
GraphRAG queries and conservation analysis.

## Miradi XML to Graph Mapping

### Core Conservation Elements (Must-Support - 100% coverage)

**Conservation Targets (BiodiversityTarget)**
- XML: `<BiodiversityTarget>` with BiodiversityTargetId, BiodiversityTargetName, BiodiversityTargetUUID
- Graph: `CONSERVATION_TARGET` nodes with conservation-specific properties
- Purpose: Species, habitats, or ecological systems being conserved

**Threats (Cause/DirectThreat)**
- XML: `<Cause>` elements with CauseId, CauseName, CauseIsDirectThreat
- Graph: `THREAT` nodes representing human activities harming targets
- Purpose: Direct pressures on conservation targets (habitat loss, overexploitation, etc.)

**Strategies (Strategy)**
- XML: `<Strategy>` with StrategyId, StrategyName, StrategyOrderedActivityIds
- Graph: `STRATEGY` nodes representing conservation interventions
- Purpose: Actions designed to mitigate threats or enhance targets

**Activities (Task)**
- XML: `<Task>` elements with TaskId, TaskName, TaskIdentifier
- Graph: `ACTIVITY` nodes representing specific actions within strategies
- Purpose: Concrete implementation steps for strategies

**Intermediate Results (IntermediateResult)**
- XML: `<IntermediateResult>` with IntermediateResultId, IntermediateResultName
- Graph: `INTERMEDIATE_RESULT` nodes representing outcomes in results chains
- Purpose: Measurable outcomes between activities and ultimate goals

### Monitoring and Planning Elements (Should-Support - 75%+ coverage)

**Indicators (Indicator)**
- XML: `<Indicator>` with IndicatorId, IndicatorName, IndicatorRelevantActivityIds
- Graph: `INDICATOR` nodes for monitoring variables
- Purpose: Measurable variables providing evidence of progress

**Objectives (Objective)**
- XML: `<Objective>` with ObjectiveId, ObjectiveName, ObjectiveRelevantStrategyIds
- Graph: `OBJECTIVE` nodes for specific goals
- Purpose: SMART goals defining desired future states

**Resources (Resource)**
- XML: `<Resource>` with ResourceId, ResourceGivenName, ResourceResourceType
- Graph: `RESOURCE` nodes for people and organizations
- Purpose: Human and organizational resources implementing strategies

### Visual Representation Elements (Must-Support - 100% coverage)

**Conceptual Models (ConceptualModel)**
- XML: `<ConceptualModel>` with ConceptualModelDiagramFactorIds, ConceptualModelDiagramLinkIds
- Graph: `CONCEPTUAL_MODEL` nodes containing visual representations
- Purpose: Visual models showing target-threat-strategy relationships

**Results Chains (ResultsChain)**
- XML: `<ResultsChain>` with ResultsChainDiagramFactorIds, ResultsChainDiagramLinkIds
- Graph: `RESULTS_CHAIN` nodes showing theory of change
- Purpose: Logical frameworks connecting strategies to outcomes

**Diagram Factors (DiagramFactor)**
- XML: `<DiagramFactor>` with DiagramFactorWrappedFactorId, DiagramFactorLocation
- Graph: `DIAGRAM_FACTOR` nodes for visual elements
- Purpose: Visual representations of conservation elements in diagrams

**Diagram Links (DiagramLink)**
- XML: `<DiagramLink>` with DiagramLinkFromDiagramFactorId, DiagramLinkToDiagramFactorId
- Graph: `DIAGRAM_LINK` nodes for visual connections
- Purpose: Visual connections between diagram factors

### Relationship Mapping Strategy

**Conservation Logic Relationships:**
- THREATENS: Derived from threat rating data (SimpleThreatRating elements)
- MITIGATES: Inferred from strategy targeting and threat reduction focus
- CONTRIBUTES_TO: Built from results chain logic and intermediate results
- IMPLEMENTS: Derived from StrategyOrderedActivityIds linking tasks to strategies
- MEASURES: Built from IndicatorRelevantActivityIds and IndicatorRelevantStrategyIds

**Structural Relationships:**
- BELONGS_TO_PROJECT: All elements connected to root ConservationProject
- CONTAINS: Models and chains contain their diagram factors
- LINKS: Diagram links connect diagram factors for visual representation

**Data Preservation:**
- All UUIDs preserved for referential integrity
- Element properties stored as node properties
- Relationship properties capture connection metadata
- Visual layout information maintained for diagram reconstruction

### Implementation Notes

1. **Must-Support Priority**: All 173 must-support elements from parser requirements are handled
2. **Graceful Degradation**: Optional elements enhance but don't break core functionality
3. **Performance Optimization**: Node types and relationships designed for efficient querying
4. **Conservation Semantics**: Maintains domain meaning while optimizing for graph operations
5. **Visual Fidelity**: Preserves diagram structure for reconstruction in user interfaces

This mapping enables powerful GraphRAG queries while maintaining the semantic richness of
conservation planning concepts and supporting visual representation needs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class NodeType(Enum):
    """
    Graph node types representing Miradi conservation and structural elements.
    
    Based on must-support elements from parser requirements and conservation domain model.
    """
    
    # Core Conservation Elements (from domain model)
    PROJECT = "PROJECT"                           # ConservationProject root element
    CONSERVATION_TARGET = "CONSERVATION_TARGET"   # BiodiversityTarget elements
    THREAT = "THREAT"                            # Cause elements (DirectThreat)
    STRATEGY = "STRATEGY"                        # Strategy elements
    INTERMEDIATE_RESULT = "INTERMEDIATE_RESULT"   # IntermediateResult elements
    ACTIVITY = "ACTIVITY"                        # Task elements (activities within strategies)
    
    # Monitoring and Planning Elements
    INDICATOR = "INDICATOR"                      # Indicator elements
    OBJECTIVE = "OBJECTIVE"                      # Objective elements  
    RESOURCE = "RESOURCE"                        # Resource elements (people/organizations)
    
    # Visual Representation Elements
    CONCEPTUAL_MODEL = "CONCEPTUAL_MODEL"        # ConceptualModel elements
    RESULTS_CHAIN = "RESULTS_CHAIN"             # ResultsChain elements
    DIAGRAM_FACTOR = "DIAGRAM_FACTOR"           # DiagramFactor elements
    DIAGRAM_LINK = "DIAGRAM_LINK"               # DiagramLink elements


class RelationshipType(Enum):
    """
    Graph relationship types representing conservation logic and structural connections.
    
    Based on Miradi domain model relationships and graph schema design.
    """
    
    # Core Conservation Relationships
    THREATENS = "THREATENS"                      # Threat -> ConservationTarget (from threat ratings)
    MITIGATES = "MITIGATES"                     # Strategy -> Threat (threat reduction focus)
    CONTRIBUTES_TO = "CONTRIBUTES_TO"           # Strategy -> IntermediateResult (results chains)
    ENHANCES = "ENHANCES"                       # Strategy -> ConservationTarget (direct benefit)
    MEASURES = "MEASURES"                       # Indicator -> Target/Result/Strategy
    IMPLEMENTS = "IMPLEMENTS"                   # Activity -> Strategy (from StrategyOrderedActivityIds)
    DEFINES = "DEFINES"                         # Objective -> Target/Threat/Strategy
    
    # Structural Relationships
    BELONGS_TO_PROJECT = "BELONGS_TO_PROJECT"   # All elements -> Project
    CONTAINS = "CONTAINS"                       # Model/Chain -> DiagramFactor
    LINKS = "LINKS"                            # DiagramLink connecting DiagramFactors
    
    # Dependency Relationships
    DEPENDS_ON = "DEPENDS_ON"                   # Strategy/Activity dependencies
    PART_OF = "PART_OF"                        # Activity -> Strategy containment


@dataclass
class MiradiNode:
    """
    Represents a node in the Miradi graph structure.
    
    Maps Miradi XML elements to graph nodes with preserved properties and metadata.
    """
    
    # Core identification (from XML)
    id: str                                     # Element ID from XML (e.g., BiodiversityTargetId)
    node_type: NodeType                         # Graph node type classification
    name: str                                   # Element name (e.g., BiodiversityTargetName)
    uuid: Optional[str] = None                  # Element UUID for referential integrity
    
    # Element properties (from XML content)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata for processing
    source_element: Optional[str] = None        # Original XML element name
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate node data after initialization."""
        if not self.id:
            raise ValueError("Node ID is required")
        if not self.name:
            raise ValueError("Node name is required")
    
    def to_neo4j_dict(self) -> Dict[str, Any]:
        """
        Convert node to Neo4j-compatible dictionary.
        
        Returns:
            Dictionary suitable for Neo4j node creation
        """
        node_data = {
            'id': self.id,                          # Keep 'id' for internal use
            'element_id': self.id,                  # Add 'element_id' for query compatibility
            'name': self.name,
            'node_type': self.node_type.value,
            'created_at': self.created_at.isoformat()
        }
        
        if self.uuid:
            node_data['uuid'] = self.uuid
        
        if self.source_element:
            node_data['source_element'] = self.source_element
        
        # Add all properties, ensuring Neo4j compatibility
        for key, value in self.properties.items():
            if value is not None:
                # Convert complex types to strings for Neo4j storage
                if isinstance(value, (list, dict)):
                    node_data[key] = str(value)
                else:
                    node_data[key] = value
        
        return node_data


@dataclass
class MiradiRelationship:
    """
    Represents a relationship in the Miradi graph structure.
    
    Maps Miradi XML relationships to graph edges with properties and metadata.
    """
    
    # Core relationship definition
    source_id: str                              # Source node ID
    target_id: str                              # Target node ID
    relationship_type: RelationshipType         # Relationship classification
    
    # Relationship properties (from XML or inferred)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata for processing
    source_element: Optional[str] = None        # Source XML element/attribute
    confidence: Optional[str] = None            # Confidence in relationship (High/Medium/Low)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate relationship data after initialization."""
        if not self.source_id:
            raise ValueError("Source ID is required")
        if not self.target_id:
            raise ValueError("Target ID is required")
        if self.source_id == self.target_id:
            raise ValueError("Self-relationships not allowed")
    
    def to_neo4j_dict(self) -> Dict[str, Any]:
        """
        Convert relationship to Neo4j-compatible dictionary.
        
        Returns:
            Dictionary suitable for Neo4j relationship creation
        """
        rel_data = {
            'relationship_type': self.relationship_type.value,
            'created_at': self.created_at.isoformat()
        }
        
        if self.source_element:
            rel_data['source_element'] = self.source_element
        
        if self.confidence:
            rel_data['confidence'] = self.confidence
        
        # Add all properties, ensuring Neo4j compatibility
        for key, value in self.properties.items():
            if value is not None:
                # Convert complex types to strings for Neo4j storage
                if isinstance(value, (list, dict)):
                    rel_data[key] = str(value)
                else:
                    rel_data[key] = value
        
        return rel_data


@dataclass
class GraphConversionResult:
    """
    Container for the result of converting Miradi data to graph format.
    
    Provides nodes, relationships, and statistics for the conversion process.
    """
    
    # Conversion output
    nodes: List[MiradiNode] = field(default_factory=list)
    relationships: List[MiradiRelationship] = field(default_factory=list)
    
    # Conversion statistics
    stats: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    source_file: Optional[str] = None
    conversion_time: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate statistics after initialization."""
        self._calculate_stats()
    
    def _calculate_stats(self):
        """Calculate conversion statistics."""
        # Node statistics
        node_counts = {}
        for node in self.nodes:
            node_type = node.node_type.value
            node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        # Relationship statistics
        relationship_counts = {}
        for rel in self.relationships:
            rel_type = rel.relationship_type.value
            relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
        
        # Overall statistics
        self.stats.update({
            'total_nodes': len(self.nodes),
            'total_relationships': len(self.relationships),
            'node_counts': node_counts,
            'relationship_counts': relationship_counts,
            'conversion_time': self.conversion_time.isoformat(),
            'has_errors': len(self.errors) > 0,
            'has_warnings': len(self.warnings) > 0
        })
    
    def add_node(self, node: MiradiNode):
        """Add a node and update statistics."""
        self.nodes.append(node)
        self._calculate_stats()
    
    def add_relationship(self, relationship: MiradiRelationship):
        """Add a relationship and update statistics."""
        self.relationships.append(relationship)
        self._calculate_stats()
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self._calculate_stats()
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
        self._calculate_stats()
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[MiradiNode]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes if node.node_type == node_type]
    
    def get_relationships_by_type(self, rel_type: RelationshipType) -> List[MiradiRelationship]:
        """Get all relationships of a specific type."""
        return [rel for rel in self.relationships if rel.relationship_type == rel_type]
    
    def get_node_by_id(self, node_id: str) -> Optional[MiradiNode]:
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def validate(self) -> List[str]:
        """
        Validate the graph structure and return any issues.
        
        Returns:
            List of validation error messages
        """
        validation_errors = []
        
        # Check for duplicate node IDs
        node_ids = [node.id for node in self.nodes]
        duplicate_ids = set([id for id in node_ids if node_ids.count(id) > 1])
        if duplicate_ids:
            validation_errors.append(f"Duplicate node IDs found: {duplicate_ids}")
        
        # Check relationship references
        valid_node_ids = set(node_ids)
        for rel in self.relationships:
            if rel.source_id not in valid_node_ids:
                validation_errors.append(f"Relationship references invalid source ID: {rel.source_id}")
            if rel.target_id not in valid_node_ids:
                validation_errors.append(f"Relationship references invalid target ID: {rel.target_id}")
        
        # Check for orphaned nodes (no relationships)
        nodes_in_relationships = set()
        for rel in self.relationships:
            nodes_in_relationships.add(rel.source_id)
            nodes_in_relationships.add(rel.target_id)
        
        orphaned_nodes = valid_node_ids - nodes_in_relationships
        if orphaned_nodes:
            # Filter out project nodes which are expected to be targets only
            project_nodes = {node.id for node in self.nodes if node.node_type == NodeType.PROJECT}
            orphaned_non_project = orphaned_nodes - project_nodes
            if orphaned_non_project:
                validation_errors.append(f"Orphaned nodes found: {orphaned_non_project}")
        
        return validation_errors
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """
        Create a summary dictionary for reporting.
        
        Returns:
            Summary of conversion results
        """
        return {
            'source_file': self.source_file,
            'conversion_time': self.conversion_time.isoformat(),
            'statistics': self.stats,
            'validation_errors': self.validate(),
            'processing_errors': self.errors,
            'processing_warnings': self.warnings
        }


# Utility functions for common operations

def create_conservation_target_node(
    target_id: str,
    name: str,
    uuid: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiNode:
    """Create a conservation target node from Miradi BiodiversityTarget data."""
    return MiradiNode(
        id=target_id,
        node_type=NodeType.CONSERVATION_TARGET,
        name=name,
        uuid=uuid,
        properties=properties or {},
        source_element="BiodiversityTarget"
    )


def create_threat_node(
    threat_id: str,
    name: str,
    uuid: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiNode:
    """Create a threat node from Miradi Cause data."""
    return MiradiNode(
        id=threat_id,
        node_type=NodeType.THREAT,
        name=name,
        uuid=uuid,
        properties=properties or {},
        source_element="Cause"
    )


def create_strategy_node(
    strategy_id: str,
    name: str,
    uuid: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiNode:
    """Create a strategy node from Miradi Strategy data."""
    return MiradiNode(
        id=strategy_id,
        node_type=NodeType.STRATEGY,
        name=name,
        uuid=uuid,
        properties=properties or {},
        source_element="Strategy"
    )


def create_activity_node(
    activity_id: str,
    name: str,
    uuid: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiNode:
    """Create an activity node from Miradi Task data."""
    return MiradiNode(
        id=activity_id,
        node_type=NodeType.ACTIVITY,
        name=name,
        uuid=uuid,
        properties=properties or {},
        source_element="Task"
    )


def create_threatens_relationship(
    threat_id: str,
    target_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiRelationship:
    """Create a threatens relationship from threat rating data."""
    return MiradiRelationship(
        source_id=threat_id,
        target_id=target_id,
        relationship_type=RelationshipType.THREATENS,
        properties=properties or {},
        source_element="SimpleThreatRating"
    )


def create_implements_relationship(
    activity_id: str,
    strategy_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiRelationship:
    """Create an implements relationship from strategy activity ordering."""
    return MiradiRelationship(
        source_id=activity_id,
        target_id=strategy_id,
        relationship_type=RelationshipType.IMPLEMENTS,
        properties=properties or {},
        source_element="StrategyOrderedActivityIds"
    )


def create_belongs_to_project_relationship(
    element_id: str,
    project_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> MiradiRelationship:
    """Create a belongs-to-project relationship for any project element."""
    return MiradiRelationship(
        source_id=element_id,
        target_id=project_id,
        relationship_type=RelationshipType.BELONGS_TO_PROJECT,
        properties=properties or {},
        source_element="ConservationProject"
    )
