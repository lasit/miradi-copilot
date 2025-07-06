# Miradi Co-Pilot

A GraphRAG-powered natural language interface for Miradi conservation projects using Neo4j, Python, and FastAPI.

## 🌿 Overview

Miradi Co-Pilot transforms Miradi conservation planning projects into an intelligent graph database, enabling natural language queries about conservation strategies, threats, targets, and their relationships. The system processes Miradi XML/JSON files into Neo4j and provides GraphRAG capabilities for conservation planning assistance.

## ✨ Current Capabilities

### ✅ **Fully Implemented**
- **Miradi XML/JSON Parser**: Complete parsing of Miradi project files (.xmpz2) with robust handling of scattered XML structures
- **Graph Data Model**: Conservation-specific graph schema with accurate relationship mapping
- **Neo4j Integration**: Full ETL pipeline with batch loading, constraints, and dual field support
- **Conservation Relationships**: THREATENS, MITIGATES, CONTRIBUTES_TO, ENHANCES, IMPLEMENTS connecting actual conservation elements
- **Project Management**: Single-project mode with switching capabilities and proper metadata extraction
- **Analysis Tools**: Comprehensive project analysis without database loading
- **Data Integrity**: Zero null IDs, consistent field naming, and accurate conservation relationships

### 📊 **System Statistics** (from 11 sample projects)
- **8,488 total elements** parsed across all projects
- **100% schema coverage** for known Miradi elements
- **19,884 relationships** including conservation logic
- **8,412 nodes** representing conservation concepts
- **11 project types** successfully processed

## 🚀 Quick Start

### Prerequisites

1. **Neo4j Database** (version 4.4+)
   ```bash
   # Using Docker (recommended)
   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
   
   # Or install locally from https://neo4j.com/download/
   ```

2. **Python 3.8+** with dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j credentials
   ```

### Installation

```bash
git clone https://github.com/lasit/miradi-copilot
cd miradi-copilot
pip install -r requirements.txt
cp .env.example .env
# Configure .env with your Neo4j connection details
```

### Test Your Setup

```bash
# Test Neo4j connection
python test_neo4j_connection.py

# Test with sample data
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2 --clear
```

## 📖 Usage Guide

### 1. **Load a Single Project**

```bash
# Load project (clears database first)
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2 --clear

# Load without clearing (append mode)
python load_project.py data/sample_projects/Miradi_Marine_Example_v0.48.xmpz2
```

**Example Output:**
```
🌿 MIRADI PROJECT LOADER
📁 Project: Bulgul Rangers
✅ SUCCESS!
📊 LOADING STATISTICS
📈 Elements Parsed: 1,373
🎯 Schema Coverage: 100.0%
🔗 Nodes Created: 1,367
🔗 Relationships Created: 3,194
⏱️  Total Time: 13.4s

🔗 RELATIONSHIP BREAKDOWN:
   • THREATENS: 95 (Threat → Target)
   • MITIGATES: 83 (Strategy → Threat)
   • CONTRIBUTES_TO: 86 (Strategy → Result)
   • ENHANCES: 79 (Result → Target)
   • IMPLEMENTS: 191 (Activity → Strategy)
```

### 2. **Manage Projects**

```bash
# Check current project status
python switch_project.py

# Switch to a different project
python switch_project.py "Miradi Marine"

# List available projects
python switch_project.py --list
```

**Example Output:**
```
🌿 MIRADI PROJECT SWITCHER
📊 CURRENT PROJECT STATUS
📁 Project: Bulgul Rangers
⏰ Loaded: 2025-07-05 18:48:04
🔗 Nodes: 1,367
🔗 Relationships: 3,194

📂 AVAILABLE PROJECTS
Found 11 available projects:
 1. Bulgul Rangers
 2. Caring For Country
 3. Miradi Marine Example
 ...
```

### 3. **Analyze Projects (No Database Required)**

```bash
# Basic analysis of all projects
python analyze_all_projects.py

# Detailed analysis with error reporting
python analyze_all_projects.py --detailed

# Export detailed JSON report
python analyze_all_projects.py --export analysis_report.json
```

**Example Output:**
```
🔍 MIRADI PROJECT ANALYZER
✅ Successfully Analyzed: 11/11
📈 AGGREGATE STATISTICS:
   • Total Elements Parsed: 8,488
   • Average Schema Coverage: 100.0%
   • Total Potential Nodes: 8,412
   • Total Potential Relationships: 19,884
```

### 4. **Query Conservation Data**

Once loaded, query your conservation data with Cypher:

```cypher
// Find all threats to a specific target
MATCH (threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
WHERE target.name CONTAINS "Woodland"
RETURN threat.name, target.name

// Find strategies that mitigate threats
MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)
RETURN strategy.name, threat.name

// Find complete threat-strategy-result chains
MATCH (threat:DIRECT_THREAT)<-[:MITIGATES]-(strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)
RETURN threat.name, strategy.name, result.name
```

## 🏗️ Architecture

### System Components

```
Miradi XML/JSON Files (.xmpz2)
           ↓
    MiradiParser (src/etl/miradi_parser.py)
           ↓
    MiradiToGraphMapper (src/etl/schema_mapper.py)
           ↓
    Neo4jLoader (src/etl/neo4j_loader.py)
           ↓
    Neo4j Graph Database
           ↓
    GraphRAG Queries (Future)
```

### Key Classes

- **`MiradiParser`**: Extracts conservation elements from Miradi XML/JSON
- **`MiradiToGraphMapper`**: Converts parsed data to graph nodes and relationships
- **`Neo4jLoader`**: Handles database operations, constraints, and batch loading
- **`Neo4jConnection`**: Manages database connections and query execution

### Data Flow

1. **Parse**: Extract conservation elements from Miradi files
2. **Map**: Convert to graph nodes (Targets, Threats, Strategies) and relationships
3. **Load**: Batch insert into Neo4j with constraints and indexes
4. **Query**: Use Cypher or GraphRAG for conservation analysis

## 📁 Project Structure

```
miradi-copilot/
├── src/
│   ├── etl/                    # ETL Pipeline
│   │   ├── miradi_parser.py    # Miradi XML/JSON parser
│   │   ├── schema_mapper.py    # Graph conversion logic
│   │   └── neo4j_loader.py     # Database loading
│   └── graph/
│       ├── models.py           # Graph data models
│       └── neo4j_connection.py # Database connection
├── data/sample_projects/       # Sample Miradi projects
├── docs/                       # Documentation
├── tests/                      # Test suite
├── load_project.py            # Single project loader
├── switch_project.py          # Project management
├── analyze_all_projects.py    # Analysis tool
└── clear_neo4j.py            # Database utility
```

## 🔗 Conservation Relationships

The system models key conservation planning relationships:

| Relationship | Source | Target | Description |
|--------------|--------|--------|-------------|
| `THREATENS` | Direct Threat | Conservation Target | Threat impacts target |
| `MITIGATES` | Strategy | Direct Threat | Strategy reduces threat |
| `CONTRIBUTES_TO` | Strategy | Result | Strategy produces result |
| `ENHANCES` | Result | Conservation Target | Result improves target |
| `IMPLEMENTS` | Activity | Strategy | Activity executes strategy |

## 📊 Sample Projects

The system includes 11 real conservation projects:

1. **Bulgul Rangers** (1,373 elements) - Indigenous land management
2. **Caring for Country** (759 elements) - Traditional ecological knowledge
3. **Miradi Marine Example** (317 elements) - Marine conservation
4. **Malak Malak Rangers** (1,069 elements) - Cultural landscape management
5. **Mardbalk HCP** (1,420 elements) - Habitat conservation planning
6. **Wardaman IPA Rangers** (896 elements) - Indigenous protected areas
7. And 5 more diverse conservation projects...

## 🛠️ Development

### Running Tests

```bash
# Test Neo4j connection
python test_neo4j_connection.py

# Test parser with sample data
python test_parser_basic.py

# Test schema mapping
python test_schema_mapper.py
```

### Adding New Element Types

1. Add parser method in `src/etl/miradi_parser.py`
2. Add mapping logic in `src/etl/schema_mapper.py`
3. Update graph models in `src/graph/models.py`
4. Add tests in `tests/`

### Performance Optimization

- **Batch Size**: Adjust `batch_size` in Neo4jLoader (default: 1000)
- **Indexes**: Automatic indexes on `id`, `name`, `node_type` properties
- **Constraints**: UUID uniqueness constraints for data integrity
- **Connection Pooling**: Managed by Neo4j driver

## 🚧 Known Limitations

### Missing Element Types
- `ThreatReductionResult` (causes 160 validation warnings)
- `IntermediateResult` (referenced in diagrams)
- `Objective` (linked in result chains)

### Validation Warnings
- **Expected**: 1,383 conversion issues across all projects
- **Cause**: Diagram links to unimplemented element types
- **Impact**: Core conservation relationships work correctly
- **Solution**: Add parsers for missing element types

## 🗺️ Roadmap

### Phase 1: Core ETL ✅ (Completed)
- [x] Miradi XML/JSON parsing
- [x] Graph data model
- [x] Neo4j integration
- [x] Conservation relationships
- [x] Project management tools

### Phase 2: GraphRAG Integration 🚧 (In Progress)
- [ ] LLM integration (OpenAI/Anthropic)
- [ ] Graph-aware query generation
- [ ] Natural language interface
- [ ] Conservation domain prompts

### Phase 3: Advanced Features 📋 (Planned)
- [ ] FastAPI REST endpoints
- [ ] Streamlit web interface
- [ ] Multi-project analysis
- [ ] Conservation metrics dashboard
- [ ] Export capabilities (PDF reports)

### Phase 4: Production Features 📋 (Future)
- [ ] User authentication
- [ ] Project collaboration
- [ ] Version control for projects
- [ ] Advanced analytics
- [ ] Integration with other conservation tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See `docs/` directory
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

## 🙏 Acknowledgments

- **Miradi Software**: For the conservation planning framework
- **Conservation Measures Partnership**: For conservation standards
- **Neo4j**: For the graph database platform
- **Sample Projects**: Provided by conservation organizations worldwide

---

**Ready to transform your conservation planning with AI? Start with `python load_project.py --help`!** 🌿
