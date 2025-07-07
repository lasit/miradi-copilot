# Changelog

All notable changes to the Miradi Co-Pilot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2025-01-08 - GraphRAG Foundation

### Added - Phase 4: Complete Natural Language Interface
- **Complete GraphRAG Module Structure** (`src/graphrag/`):
  - `graph_patterns.py` - 25+ specialized Cypher query patterns for 6 conservation categories
  - `conservation_prompts.py` - Domain-specific prompt templates with conservation expertise
  - `query_router.py` - Natural language query classification and parameter extraction
  - `context_retriever.py` - Graph database context extraction with pattern matching
  - `context_assembler.py` - Combines graph data with prompts for LLM consumption
  - `example_usage.py` - Complete GraphRAG orchestration and demonstration
- **Conservation Query Categories**:
  - 🎯 Threat Analysis: "What threatens the coastal ecosystems?"
  - 📊 Strategy Evaluation: "Which strategies are most effective?"
  - 🔄 Theory of Change: "How does fire management help wildlife?"
  - 📈 Monitoring: "What indicators track water quality?"
  - 🗺️ Spatial Analysis: "Show me threats near forest areas"
  - 🎯 Target Analysis: Conservation target status and viability queries
- **Natural Language Processing**:
  - Query intent classification with confidence scoring (0.50-1.00)
  - Conservation entity extraction (targets, threats, strategies, activities, indicators, results)
  - Parameter extraction for spatial, temporal, and domain-specific queries
  - Keyword and entity recognition for conservation terminology
- **Graph Pattern Matching**:
  - 25+ specialized Cypher templates covering all conservation relationships
  - Leverages 5,631 relationships from enhanced relationship parsing
  - Optimized patterns for threat analysis, strategy evaluation, and theory of change
  - Spatial analysis patterns with coordinate and distance support
- **Context Assembly**:
  - Domain-specific prompt engineering for conservation planning
  - 600+ token context generation ready for LLM consumption
  - Role-based system prompts for each query category
  - Structured response formats for actionable conservation insights
- **Testing and Demonstration**:
  - `test_graphrag_system.py` - Comprehensive system testing
  - Interactive query testing with confidence scoring
  - Database connectivity verification
  - Performance benchmarking and metrics

### Enhanced
- **Query Processing Pipeline**: Intent Classification → Entity Extraction → Pattern Matching → Context Retrieval → Context Assembly
- **Performance**: Sub-millisecond query processing with comprehensive error handling
- **Integration Ready**: Compatible with OpenAI, Anthropic, and local language models
- **Production Ready**: Complete natural language interface for conservation planning

### Technical Architecture
- **MiradiGraphRAG Class**: Complete orchestration of the GraphRAG pipeline
- **ConservationQueryRouter**: Routes natural language queries to appropriate analysis categories
- **ConservationContextRetriever**: Executes optimized graph queries based on intent
- **ConservationContextAssembler**: Formats graph data into LLM-ready prompts
- **ConservationPromptTemplates**: Domain-specific prompt engineering for conservation expertise

### Performance Impact
- **Query Classification**: 6 conservation categories with confidence scoring
- **Context Generation**: 600+ token prompts with domain expertise
- **Pattern Coverage**: 25+ Cypher patterns leveraging enhanced relationship parsing
- **Error Handling**: Graceful degradation when database unavailable
- **Logging**: Comprehensive execution tracking and debugging support

## [2.0.0] - 2025-01-08

### Added - Phase 2: Target-Level Conservation Relationships
- **BiodiversityTargetGoalIds**: Goal DEFINES Target relationships (657 relationships)
- **BiodiversityTargetKeyEcologicalAttributeIds**: Target HAS_ATTRIBUTE KEA relationships (42 relationships)
- **BiodiversityTargetIndicatorIds**: Indicator MEASURES Target relationships (738 total MEASURES)
- **BiodiversityTargetStressIds**: Target EXPERIENCES Stress relationships (infrastructure ready)
- **New Node Type**: STRESS node type for stress-based threat assessment
- **New Relationship Types**: HAS_ATTRIBUTE and EXPERIENCES for complete target analysis
- **Enhanced Parser**: Target relationship ID extraction with backward compatibility
- **Complete Target Analysis**: Goal-target linkage, viability assessment, monitoring framework, and stress analysis

### Changed
- **Total Relationships**: Increased from 5,631 to 5,775 (+144 new relationships, +2.5%)
- **Enhanced Conservation Coverage**: Complete target-level conservation analysis now available
- **Parser Enhancement**: Conservation target extraction now includes 4 relationship ID lists
- **Schema Mapper**: Enhanced with comprehensive target relationship creation logic

### Performance
- **Relationship Growth**: +144 new target-level relationships
- **Processing Impact**: Minimal performance impact (+2.5% relationship increase)
- **Backward Compatibility**: All existing functionality preserved
- **Production Ready**: Phase 2 implementation tested and validated

### Added
- Enhanced relationship parsing for complete conservation logic flow
- Support for Intermediate Result → Intermediate Result relationships
- Support for Intermediate Result → Threat Reduction Result relationships  
- Support for Threat Reduction Result → Threat Reduction Result relationships
- Enhanced ID list relationship parsing for 8 additional relationship types
- Complete MEASURES relationship support across all element types
- Complete DEFINES relationship support across all element types
- Comprehensive documentation updates reflecting enhanced capabilities

### Enhanced
- Schema mapper now parses 1,382 additional relationships (+32.5% improvement)
- CONTRIBUTES_TO relationships now support result-to-result chains
- MEASURES relationships now connect 6 different element types to indicators
- DEFINES relationships now connect 4 different element types to objectives
- Graph schema documentation updated with enhanced relationship types
- Implementation status documentation updated with performance metrics

### Fixed
- Missing Intermediate Result → Intermediate Result relationships in results chains
- Missing ID list relationships from IntermediateResult, ThreatReductionResult, Goal, and KeyEcologicalAttribute elements
- Incomplete conservation logic flow in graph visualization
- Gap in results chain connectivity for complex conservation pathways

### Technical Details
- Added IntermediateResultIndicatorIds → MEASURES parsing
- Added IntermediateResultObjectiveIds → DEFINES parsing
- Added ThreatReductionResultIndicatorIds → MEASURES parsing
- Added ThreatReductionResultObjectiveIds → DEFINES parsing
- Added GoalRelevantStrategyIds → DEFINES parsing
- Added GoalRelevantIndicatorIds → MEASURES parsing
- Added KeyEcologicalAttributeIndicatorIds → MEASURES parsing
- Added ObjectiveRelevantIndicatorIds → MEASURES parsing
- Enhanced diagram link processing for IR→IR, IR→TRR, and TRR→TRR relationships

### Performance Impact
- Total relationships increased from ~4,249 to 5,631 (+1,382 relationships)
- MEASURES relationships: 0 → 738 (+738)
- DEFINES relationships: 0 → 644 (+644)
- Complete conservation logic flow now captured in graph database
- Enhanced query capabilities for results chain analysis

## [0.1.0] - 2025-01-07

### Added
- Initial Miradi parser implementation with support for 10+ element types
- Neo4j graph database integration with complete schema
- Schema mapper for converting Miradi XML to graph format
- Support for conservation targets, threats, strategies, and activities
- Basic relationship parsing for THREATENS, MITIGATES, IMPLEMENTS
- Project management tools (load_project.py, switch_project.py)
- Comprehensive documentation suite
- Docker Compose setup for Neo4j
- Sample project analysis capabilities

### Features
- Parse Miradi .xmpz2 files (ZIP archives with XML content)
- Extract conservation elements with full metadata
- Create graph relationships representing conservation logic
- Load data into Neo4j with proper constraints and indexes
- Support for multiple project management
- Spatial data extraction from diagram factors
- Error handling and validation reporting

### Documentation
- Architecture overview and domain model
- Graph schema design with query patterns
- Development guide and deployment instructions
- Implementation status tracking
- Sample queries for conservation analysis

### Performance
- Process 1,000+ element projects in under 30 seconds
- Batch loading with configurable batch sizes
- Memory-efficient streaming for large files
- Comprehensive error reporting and recovery

### Known Limitations
- Limited to core conservation elements (targets, threats, strategies, activities)
- Basic relationship types only
- Some validation warnings for unimplemented element types
- No GraphRAG integration yet
- Command-line interface only

---

## Version History Summary

- **v0.1.0**: Initial release with core Miradi parsing and Neo4j integration
- **Unreleased**: Enhanced relationship parsing with complete conservation logic flow (+1,382 relationships)

## Upgrade Notes

### From v0.1.0 to Unreleased
- **Database Impact**: Significant increase in relationships (32.5% more)
- **Query Changes**: New relationship types available (enhanced MEASURES, DEFINES, CONTRIBUTES_TO)
- **Performance**: Improved conservation logic completeness with minimal performance impact
- **Compatibility**: Fully backward compatible, existing queries continue to work
- **Recommended Action**: Clear and reload projects to benefit from enhanced relationships

### Migration Steps
1. Clear existing Neo4j database: `python clear_neo4j.py`
2. Reload project with enhanced parser: `python load_project.py`
3. Verify enhanced relationships with sample queries
4. Update any custom queries to leverage new relationship types

## Future Roadmap

### Phase 2: GraphRAG Integration (Q2 2025)
- Natural language query interface
- LLM integration for conservation domain queries
- Context-aware response generation
- Conservation-specific prompt engineering

### Phase 3: Web Interface (Q3 2025)
- FastAPI backend with REST endpoints
- Streamlit frontend for interactive analysis
- File upload and project management UI
- Graph visualization capabilities

### Phase 4: Advanced Analytics (Q4 2025)
- Cross-project conservation analysis
- Strategy effectiveness metrics
- Threat assessment algorithms
- Monitoring and evaluation frameworks

## Contributing

Please read our contributing guidelines and ensure all changes are documented in this changelog following the established format.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
