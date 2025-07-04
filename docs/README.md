# Miradi Co-Pilot Documentation

## Overview

This directory contains comprehensive documentation for the Miradi Co-Pilot system, a conservation planning assistant that processes Miradi project files and provides intelligent querying through GraphRAG technology.

## Documentation Structure

### Core Architecture Documentation

#### [01-architecture-overview.md](01-architecture-overview.md)
**System Architecture and Design**
- High-level system architecture (3-tier design)
- Technology choices and rationale
- Core component descriptions (ETL, GraphRAG, API, UI)
- Data flow overview with Mermaid diagrams
- Key design decisions and scalability considerations

#### [02-domain-model.md](02-domain-model.md)
**Conservation Domain Concepts**
- Core Miradi concepts (Targets, Threats, Strategies, etc.)
- Relationship definitions and examples
- Conservation-specific terminology glossary
- Real-world scenarios illustrating concept application
- Essential for understanding the conservation planning framework

#### [03-data-flow.md](03-data-flow.md)
**ETL Pipeline and Data Processing** *(Section headers only)*
- ETL pipeline architecture
- Data validation and quality checks
- Error handling and recovery strategies
- Performance optimization techniques
- Data lineage and auditing

#### [04-graph-schema.md](04-graph-schema.md)
**Neo4j Database Design**
- Complete graph schema definition (8 node types, 10 relationship types)
- Node properties, constraints, and indexes
- Relationship cardinalities and properties
- Common Cypher query patterns for conservation analysis
- Performance optimization guidelines

### Implementation Documentation

#### [06-rag-architecture.md](06-rag-architecture.md)
**GraphRAG Implementation** *(Section headers only)*
- GraphRAG vs traditional RAG comparison
- Graph-aware retrieval strategies
- Embedding and semantic search integration
- Query processing pipeline
- LLM integration and optimization

#### [07-development-guide.md](07-development-guide.md)
**Cline-Assisted Development Guide**
- Best practices for AI-assisted development
- Component isolation rules and session management
- Effective prompt patterns for different development tasks
- Anti-patterns to avoid and quality assurance
- Testing strategies and code review checklists

#### [08-deployment.md](08-deployment.md)
**Production Deployment** *(Section headers only)*
- Infrastructure requirements and container deployment
- Database and application deployment strategies
- Security configuration and monitoring
- Scaling strategies and disaster recovery
- Maintenance and update procedures

### Schema Documentation

#### [schemas/miradi-xml-schema.md](schemas/miradi-xml-schema.md)
**Miradi File Format Documentation** *(Section headers only)*
- XML schema structure and elements
- Relationship definitions and constraints
- Data types and validation rules
- Version differences and migration considerations
- Sample structures and common patterns

#### [schemas/schema-discovery-log.md](schemas/schema-discovery-log.md)
**Schema Analysis Tracking** *(Section headers only)*
- Project file analysis methodology
- Discovery log template for tracking analyzed files
- Schema pattern identification
- Recommendations for parser implementation

### Visual Documentation

#### [diagrams/README.md](diagrams/README.md)
**Diagram Creation and Maintenance Guide**
- Diagram types and tools (Mermaid, Draw.io, etc.)
- File organization and naming conventions
- Standards for colors, typography, and layout
- Maintenance schedule and best practices
- Integration with documentation workflow

## Documentation Categories

### 📋 **Planning and Architecture**
Documents that define the system design and approach:
- 01-architecture-overview.md
- 02-domain-model.md
- 06-rag-architecture.md

### 🔧 **Implementation Guides**
Technical documentation for building the system:
- 03-data-flow.md
- 04-graph-schema.md
- 07-development-guide.md
- schemas/miradi-xml-schema.md

### 🚀 **Operations and Deployment**
Documentation for running and maintaining the system:
- 08-deployment.md
- diagrams/README.md

### 📊 **Analysis and Discovery**
Documentation for understanding and analyzing Miradi data:
- schemas/schema-discovery-log.md

## Documentation Status

### ✅ **Complete Documentation**
- Architecture overview with detailed diagrams
- Domain model with comprehensive examples
- Graph schema with complete specifications
- Development guide with practical patterns
- Diagram standards and maintenance guide

### 📝 **Template Documentation** *(Section headers only)*
Ready for detailed content development:
- Data flow architecture
- GraphRAG implementation details
- Deployment procedures
- Miradi XML schema analysis
- Schema discovery tracking

## Getting Started

### For New Developers
1. Start with [01-architecture-overview.md](01-architecture-overview.md) for system understanding
2. Review [02-domain-model.md](02-domain-model.md) for conservation concepts
3. Study [04-graph-schema.md](04-graph-schema.md) for database design
4. Follow [07-development-guide.md](07-development-guide.md) for development practices

### For Conservation Practitioners
1. Begin with [02-domain-model.md](02-domain-model.md) for Miradi concepts
2. Review [01-architecture-overview.md](01-architecture-overview.md) for system capabilities
3. Refer to schema documentation for data structure understanding

### For System Administrators
1. Review [01-architecture-overview.md](01-architecture-overview.md) for system architecture
2. Study [08-deployment.md](08-deployment.md) for deployment procedures
3. Follow monitoring and maintenance guidelines

## Contributing to Documentation

### Documentation Standards
- Use clear, concise language
- Include practical examples and code snippets
- Maintain consistent formatting and structure
- Update diagrams when making architectural changes

### Review Process
- All documentation changes should be reviewed
- Verify technical accuracy with implementation
- Ensure consistency with existing documentation
- Update related documents when making changes

### Maintenance
- Review documentation quarterly for accuracy
- Update with significant system changes
- Maintain links and references
- Keep examples current and relevant

## Related Resources

### External Documentation
- [Miradi Software Documentation](https://www.miradi.org/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Project Resources
- [Main README](../README.md) - Project overview and setup
- [API Documentation](../api/) - Generated API documentation
- [Test Documentation](../tests/) - Testing guidelines and examples

This documentation provides a comprehensive guide to understanding, developing, and maintaining the Miradi Co-Pilot system.
