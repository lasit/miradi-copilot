# Miradi Co-Pilot Architecture Overview

## System Overview

Miradi Co-Pilot is a GraphRAG-powered natural language interface for Miradi conservation projects. The system transforms Miradi XML/JSON files into an intelligent Neo4j graph database, enabling sophisticated conservation planning analysis through graph relationships and AI-powered querying.

## Current Implementation Status

### ✅ **Fully Implemented Components**
- **ETL Pipeline**: Complete Miradi parsing and Neo4j loading
- **Graph Data Model**: Conservation-specific nodes and relationships
- **Neo4j Integration**: Batch loading, constraints, and indexes
- **Project Management**: Single-project mode with switching capabilities
- **Analysis Tools**: Comprehensive project analysis without database loading
- **Conservation Relationships**: THREATENS, MITIGATES, CONTRIBUTES_TO, ENHANCES, IMPLEMENTS

### 🚧 **In Development**
- **GraphRAG Engine**: Graph-aware query generation
- **Natural Language Interface**: LLM integration for conservation queries

### 📋 **Planned Components**
- **FastAPI Backend**: RESTful API endpoints
- **Streamlit Frontend**: Web-based user interface
- **Multi-project Analysis**: Cross-project conservation insights

## System Architecture

### Current 3-Tier Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                        │
├─────────────────────────────────────────────────────────────┤
│  • Command-Line Tools (load_project.py, switch_project.py) │
│  • Analysis Scripts (analyze_all_projects.py)              │
│  • Project Management (PROJECT nodes with metadata)        │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      API/LOGIC TIER                        │
├─────────────────────────────────────────────────────────────┤
│  • MiradiParser (src/etl/miradi_parser.py)                │
│  • MiradiToGraphMapper (src/etl/schema_mapper.py)         │
│  • Neo4jLoader (src/etl/neo4j_loader.py)                  │
│  • Conservation Logic (relationship mapping)               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA TIER                            │
├─────────────────────────────────────────────────────────────┤
│  • Neo4j Graph Database (conservation nodes & relationships)│
│  • Miradi Project Files (.xmpz2 archives)                 │
│  • Project Metadata (PROJECT nodes with load statistics)   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MiradiParser (`src/etl/miradi_parser.py`)

**Purpose**: Extracts conservation elements from Miradi XML/JSON files.

**Key Features**:
- **173 Must-Support Elements**: Complete implementation of core Miradi elements
- **ZIP Archive Processing**: Handles .xmpz2 files automatically
- **Configurable Unknown Element Handling**: LOG, ERROR, STORE, or IGNORE strategies
- **Comprehensive Validation**: Ensures data integrity and required elements
- **XML Namespace Support**: Correctly processes Miradi's namespaced XML

**Core Methods**:
```python
class MiradiParser:
    def parse_all(self, file_path: str) -> Dict[str, Any]
    def extract_conservation_targets(self, root: ET.Element) -> List[ParsedElement]
    def extract_threats(self, root: ET.Element) -> List[ParsedElement]
    def extract_strategies(self, root: ET.Element) -> List[ParsedElement]
    def extract_activities(self, root: ET.Element) -> List[ParsedElement]
    def extract_results_chains(self, root: ET.Element) -> List[ParsedElement]
    def extract_conceptual_models(self, root: ET.Element) -> List[ParsedElement]
    def extract_diagram_factors(self, root: ET.Element) -> List[ParsedElement]
    def extract_diagram_links(self, root: ET.Element) -> List[ParsedElement]
    def get_parsing_summary(self) -> Dict[str, Any]
```

**Statistics from Real Projects**:
- **11 projects analyzed**: 8,488 total elements parsed
- **100% schema coverage**: All known elements successfully processed
- **689 unique element types**: Comprehensive Miradi schema understanding

### 2. MiradiToGraphMapper (`src/etl/schema_mapper.py`)

**Purpose**: Converts parsed Miradi data into graph nodes and relationships.

**Key Features**:
- **Conservation Domain Logic**: Maps Miradi concepts to graph structures
- **Relationship Discovery**: Extracts conservation relationships from diagram data
- **Node Type Mapping**: Converts Miradi elements to typed graph nodes
- **UUID Preservation**: Maintains referential integrity across transformations
- **Validation**: Ensures graph consistency and relationship validity

**Core Methods**:
```python
class MiradiToGraphMapper:
    def map_project_to_graph(self, parsed_data: Dict[str, Any]) -> GraphConversionResult
    def map_conservation_targets(self, targets: List[ParsedElement]) -> List[MiradiNode]
    def map_threats(self, threats: List[ParsedElement]) -> List[MiradiNode]
    def map_strategies(self, strategies: List[ParsedElement]) -> List[MiradiNode]
    def map_activities(self, activities: List[ParsedElement]) -> List[MiradiNode]
    def map_results(self, results: List[ParsedElement]) -> List[MiradiNode]
    def extract_conservation_relationships(self, parsed_data: Dict[str, Any]) -> List[MiradiRelationship]
```

**Conservation Relationship Logic**:
```python
# Threat-Target relationships from conceptual models
if source_type == "DirectThreat" and target_type == "Target":
    relationship_type = RelationshipType.THREATENS

# Strategy-Threat mitigation from results chains  
elif source_type == "Strategy" and target_type == "DirectThreat":
    relationship_type = RelationshipType.MITIGATES

# Strategy-Result contribution from results chains
elif source_type == "Strategy" and target_type in ["Result", "IntermediateResult"]:
    relationship_type = RelationshipType.CONTRIBUTES_TO

# Result-Target enhancement from results chains
elif source_type in ["Result", "IntermediateResult"] and target_type == "Target":
    relationship_type = RelationshipType.ENHANCES

# Activity-Strategy implementation
elif source_type == "Task" and target_type == "Strategy":
    relationship_type = RelationshipType.IMPLEMENTS
```

### 3. Neo4jLoader (`src/etl/neo4j_loader.py`)

**Purpose**: Handles database operations, constraints, and batch loading.

**Key Features**:
- **Batch Operations**: Efficient loading of large datasets (1000 items per batch)
- **Constraint Management**: Automatic UUID uniqueness constraints
- **Index Creation**: Performance indexes on id, name, node_type properties
- **Transaction Management**: ACID compliance for data integrity
- **Error Handling**: Graceful failure handling with detailed error reporting

**Core Methods**:
```python
class Neo4jLoader:
    def __init__(self, connection: Neo4jConnection, batch_size: int = 1000)
    def create_constraints(self) -> Dict[str, bool]
    def create_indexes(self) -> Dict[str, bool]
    def load_nodes(self, nodes: List[MiradiNode]) -> Dict[str, Any]
    def load_relationships(self, relationships: List[MiradiRelationship]) -> Dict[str, Any]
    def load_project(self, project_file: str, **kwargs) -> Dict[str, Any]
    def clear_database(self, confirm: bool = False) -> bool
```

**Performance Optimizations**:
- **Batch Size**: Configurable batch size (default: 1000)
- **Connection Pooling**: Managed by Neo4j driver
- **Parallel Processing**: Concurrent node and relationship loading
- **Memory Management**: Streaming processing for large projects

### 4. Neo4jConnection (`src/graph/neo4j_connection.py`)

**Purpose**: Manages database connections and query execution.

**Key Features**:
- **Connection Management**: Automatic connection handling with retry logic
- **Query Execution**: Support for read and write queries with parameters
- **Error Handling**: Comprehensive error handling and logging
- **Context Manager**: Automatic resource cleanup

**Core Methods**:
```python
class Neo4jConnection:
    def connect(self) -> None
    def close(self) -> None
    def check_connection(self) -> bool
    def execute_query(self, query: str, parameters: Dict = None) -> List[Dict]
    def execute_write_query(self, query: str, parameters: Dict = None) -> List[Dict]
```

## Data Flow

### ETL Pipeline Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Miradi File   │───▶│  MiradiParser   │───▶│ Parsed Elements │
│   (.xmpz2)      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Neo4j Graph   │◀───│   Neo4jLoader   │◀───│ Graph Mapper    │
│   Database      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Detailed Processing Steps

1. **File Validation**: Verify .xmpz2 format and extract XML content
2. **XML Parsing**: Parse Miradi XML with namespace handling
3. **Element Extraction**: Extract conservation elements using specialized methods
4. **Data Validation**: Validate required elements and data integrity
5. **Graph Mapping**: Convert parsed elements to graph nodes and relationships
6. **Relationship Discovery**: Extract conservation relationships from diagram data
7. **Database Preparation**: Create constraints and indexes in Neo4j
8. **Batch Loading**: Load nodes and relationships in optimized batches
9. **Metadata Storage**: Store project metadata in PROJECT node
10. **Validation**: Verify successful loading and relationship integrity

## Graph Schema

### Node Types (with typical counts from Bulgul Rangers project)

| Node Type | Count | Description |
|-----------|-------|-------------|
| `CONSERVATION_TARGET` | 12 | Biodiversity targets and conservation objects |
| `DIRECT_THREAT` | 8 | Threats directly impacting conservation targets |
| `CONTRIBUTING_FACTOR` | 15 | Indirect factors contributing to threats |
| `STRATEGY` | 18 | Conservation strategies and interventions |
| `ACTIVITY` | 45 | Specific activities implementing strategies |
| `RESULT` | 25 | Expected outcomes from strategies |
| `CONCEPTUAL_MODEL` | 3 | Conceptual models showing threat-target relationships |
| `RESULTS_CHAIN` | 8 | Results chains linking strategies to outcomes |
| `DIAGRAM_FACTOR` | 892 | Visual elements in conceptual models |
| `DIAGRAM_LINK` | 341 | Connections between diagram elements |
| `PROJECT` | 1 | Project metadata and loading information |

### Relationship Types (with counts from Bulgul Rangers project)

| Relationship | Count | Description |
|--------------|-------|-------------|
| `THREATENS` | 95 | Direct threat impacts conservation target |
| `MITIGATES` | 83 | Strategy reduces or eliminates threat |
| `CONTRIBUTES_TO` | 86 | Strategy produces specific result |
| `ENHANCES` | 79 | Result improves conservation target |
| `IMPLEMENTS` | 191 | Activity executes strategy |
| `BELONGS_TO_PROJECT` | 1,366 | Element belongs to project |
| `PART_OF` | 582 | Element is part of larger structure |
| `LINKS` | 872 | General diagram connections |

### Conservation Logic Relationships

The system implements core conservation planning logic through graph relationships:

```cypher
// Threat-Target Impact Chain
(threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)

// Strategy-Threat Mitigation Chain  
(strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)

// Strategy-Result-Target Enhancement Chain
(strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)-[:ENHANCES]->(target:CONSERVATION_TARGET)

// Activity-Strategy Implementation Chain
(activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)

// Complete Conservation Logic Chain
(activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
```

## Project Management

### Single-Project Mode Design

The system implements a single-project mode for clean data separation:

**Design Rationale**:
- **Data Integrity**: Prevents mixing of conservation data from different projects
- **Performance**: Optimized queries without project filtering overhead
- **Simplicity**: Clear mental model for users working with one project at a time
- **Flexibility**: Easy switching between projects without data conflicts

**PROJECT Node Schema**:
```cypher
CREATE (p:PROJECT {
  id: 'current_project',
  name: 'Bulgul Rangers',
  filename: 'Bulgul_Rangers_v0.111.xmpz2',
  file_path: 'data/sample_projects/Bulgul_Rangers_v0.111.xmpz2',
  loaded_at: datetime(),
  nodes_count: 1367,
  relationships_count: 3194,
  elements_parsed: 1373,
  schema_coverage: 100.0,
  load_time: 13.4
})
```

**Project Switching Process**:
1. **Clear Database**: Remove all existing nodes and relationships
2. **Load New Project**: Parse and load the target project
3. **Update Metadata**: Store new project information in PROJECT node
4. **Verify Integrity**: Confirm successful loading and relationship creation

## Command-Line Interface

### Project Loading (`load_project.py`)

```bash
# Load project with database clearing
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2 --clear

# Load project without clearing (append mode)
python load_project.py data/sample_projects/Miradi_Marine_Example_v0.48.xmpz2
```

**Features**:
- **Clean Output**: Suppressed validation warnings for better UX
- **Progress Tracking**: Real-time loading progress with statistics
- **Error Handling**: Helpful troubleshooting messages
- **Metadata Storage**: Automatic project metadata tracking

### Project Management (`switch_project.py`)

```bash
# Show current project status and available projects
python switch_project.py

# Switch to a different project
python switch_project.py "Miradi Marine"

# List available projects only
python switch_project.py --list
```

**Features**:
- **Current Status**: Shows loaded project with metadata
- **Available Projects**: Lists all .xmpz2 files in data/sample_projects/
- **Smart Matching**: Supports exact name, filename, or partial matching
- **Automatic Switching**: Handles clear + load process seamlessly

### Project Analysis (`analyze_all_projects.py`)

```bash
# Basic analysis of all projects
python analyze_all_projects.py

# Detailed analysis with error reporting
python analyze_all_projects.py --detailed

# Export detailed JSON report
python analyze_all_projects.py --export analysis_report.json
```

**Features**:
- **No Database Required**: Pure analysis without Neo4j loading
- **Comprehensive Statistics**: Coverage, nodes, relationships, conversion issues
- **Comparative Analysis**: Side-by-side comparison of all projects
- **Export Capability**: Detailed JSON reports for further analysis

## Performance Characteristics

### Loading Performance (from real projects)

| Project | Elements | Nodes | Relationships | Load Time |
|---------|----------|-------|---------------|-----------|
| Bulgul Rangers | 1,373 | 1,367 | 3,194 | 13.4s |
| Miradi Marine | 317 | 310 | 613 | 2.4s |
| Mardbalk HCP | 1,420 | 1,413 | 3,369 | 26.7s |
| Wardaman Rangers | 896 | 889 | 2,107 | 26.2s |

### Optimization Strategies

**Database Optimizations**:
- **Batch Loading**: 1000 items per batch for optimal throughput
- **Constraints**: UUID uniqueness constraints for data integrity
- **Indexes**: Automatic indexes on frequently queried properties
- **Connection Pooling**: Managed by Neo4j driver for efficiency

**Memory Management**:
- **Streaming Processing**: Large files processed in chunks
- **Garbage Collection**: Explicit cleanup of large data structures
- **Batch Size Tuning**: Configurable batch sizes for different environments

## Error Handling and Validation

### Validation Warnings

**Expected Conversion Issues**: 1,383 total across all 11 projects
- **Cause**: Diagram links to unimplemented element types
- **Impact**: Core conservation relationships work correctly
- **Examples**: ThreatReductionResult, IntermediateResult, Objective elements

**Handling Strategy**:
- **Log and Continue**: Validation warnings don't stop processing
- **Core Functionality**: Essential conservation relationships always work
- **Future Enhancement**: Add parsers for missing element types

### Error Recovery

**File Processing Errors**:
- **Format Validation**: Verify .xmpz2 structure before processing
- **XML Validation**: Handle malformed XML gracefully
- **Partial Success**: Continue processing even with some element failures

**Database Errors**:
- **Connection Retry**: Automatic retry logic for transient failures
- **Transaction Rollback**: ACID compliance for data integrity
- **Constraint Violations**: Clear error messages for duplicate data

## Future Architecture Evolution

### GraphRAG Integration (Phase 2)

**Planned Components**:
- **Graph Query Generator**: Convert natural language to Cypher queries
- **Context Assembly**: Combine graph structure with textual content
- **LLM Integration**: OpenAI/Anthropic APIs for conservation domain queries
- **Response Generation**: Contextually aware conservation planning assistance

**Architecture Extension**:
```
Current ETL Pipeline
        ↓
Neo4j Graph Database
        ↓
GraphRAG Engine ← LLM APIs
        ↓
Natural Language Interface
        ↓
Conservation Planning Assistant
```

### API and Web Interface (Phase 3)

**FastAPI Backend**:
- **RESTful Endpoints**: Project management and query APIs
- **Authentication**: User management and project access control
- **Real-time Updates**: WebSocket support for live project updates

**Streamlit Frontend**:
- **File Upload Interface**: Drag-and-drop project loading
- **Graph Visualization**: Interactive conservation relationship displays
- **Query Interface**: Natural language query with visual results
- **Dashboard**: Conservation metrics and project insights

This architecture provides a robust, scalable foundation for intelligent analysis of Miradi conservation projects, with clear separation of concerns and extensible design for future GraphRAG and web interface development.
