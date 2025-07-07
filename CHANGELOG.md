# Changelog

All notable changes to the Miradi Co-Pilot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
