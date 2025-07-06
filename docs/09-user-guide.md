# Miradi Co-Pilot User Guide

This guide provides step-by-step instructions for using Miradi Co-Pilot to load, analyze, and query conservation projects.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Loading Projects](#loading-projects)
3. [Managing Projects](#managing-projects)
4. [Analyzing Projects](#analyzing-projects)
5. [Querying Conservation Data](#querying-conservation-data)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

Before using Miradi Co-Pilot, ensure you have:

1. **Neo4j Database** running (version 4.4+)
2. **Python 3.8+** installed
3. **Project dependencies** installed (`pip install -r requirements.txt`)
4. **Environment configuration** set up (`.env` file)

### Quick Setup Verification

Test your setup with these commands:

```bash
# Test Neo4j connection
python test_neo4j_connection.py

# Test with sample data
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2 --clear
```

If both commands succeed, you're ready to use Miradi Co-Pilot!

## Loading Projects

### Single Project Loading

Use `load_project.py` to load individual Miradi projects into Neo4j.

#### Basic Usage

```bash
# Load a project (keeps existing data)
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2

# Load a project (clears database first) - RECOMMENDED
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2 --clear
```

#### Understanding the Output

```
🌿 MIRADI PROJECT LOADER
============================================================
📁 Project: Bulgul Rangers
📄 File: Bulgul_Rangers_v0.111.xmpz2
📍 Path: data\sample_projects\Bulgul_Rangers_v0.111.xmpz2

🗑️  Clearing Neo4j database...
   ✅ Cleared 1,367 nodes and 3,194 relationships

🔄 Loading project...
   • Parsing Miradi XML...
   • Converting to graph format...
   • Creating database constraints...
   • Loading nodes and relationships...

✅ SUCCESS!
============================================================
📊 LOADING STATISTICS
============================================================
📈 Elements Parsed: 1,373
🎯 Schema Coverage: 100.0%
🔗 Nodes Created: 1,367
🔗 Relationships Created: 3,194
⏱️  Total Time: 13.4s

🔗 RELATIONSHIP BREAKDOWN:
   • BELONGS_TO_PROJECT: 1,366
   • CONTRIBUTES_TO: 86
   • ENHANCES: 79
   • IMPLEMENTS: 191
   • LINKS: 872
   • MITIGATES: 83
   • PART_OF: 582
   • THREATENS: 95
   📝 Stored project metadata: Bulgul Rangers

🎉 Project successfully loaded into Neo4j!
   You can now query the conservation data using Cypher or GraphRAG.
============================================================
```

#### Key Statistics Explained

- **Elements Parsed**: Total Miradi elements found in the project file
- **Schema Coverage**: Percentage of elements successfully processed
- **Nodes Created**: Graph nodes representing conservation concepts
- **Relationships Created**: Connections between conservation elements
- **Relationship Breakdown**: Types and counts of conservation relationships

#### When to Use `--clear`

**Use `--clear` when**:
- Loading your first project
- Switching to a different project
- You want to ensure clean data (recommended)

**Don't use `--clear` when**:
- Adding supplementary data to an existing project
- You specifically want to append data

### Loading Different Project Types

Miradi Co-Pilot supports various conservation project types:

```bash
# Indigenous land management
python load_project.py data/sample_projects/Bulgul_Rangers_v0.111.xmpz2 --clear

# Marine conservation
python load_project.py data/sample_projects/Miradi_Marine_Example_v0.48.xmpz2 --clear

# Habitat conservation planning
python load_project.py data/sample_projects/Mardbalk_HCP_v0.96.xmpz2 --clear

# Traditional ecological knowledge
python load_project.py data/sample_projects/Caring_for_Country_v0.18.xmpz2 --clear
```

## Managing Projects

### Checking Current Project Status

Use `switch_project.py` to see what's currently loaded:

```bash
python switch_project.py
```

**Example Output**:
```
🌿 MIRADI PROJECT SWITCHER
============================================================

📊 CURRENT PROJECT STATUS
============================================================
📁 Project: Bulgul Rangers
📄 File: Bulgul_Rangers_v0.111.xmpz2
📍 Path: data\sample_projects\Bulgul_Rangers_v0.111.xmpz2
⏰ Loaded: 2025-07-05 18:48:04
🔗 Nodes: 1,367
🔗 Relationships: 3,194
📈 Elements: 1,373
🎯 Coverage: 100.0%
⏱️  Load Time: 13.4s

📂 AVAILABLE PROJECTS
============================================================
Found 11 available projects:

 1. Bulgul Rangers
    📄 Bulgul_Rangers_v0.111.xmpz2

 2. Caring For Country
    📄 Caring_for_Country_v0.18.xmpz2

 3. Miradi Marine Example
    📄 Miradi_Marine_Example_v0.48.xmpz2
 ...
```

### Switching Between Projects

Switch to a different project using flexible matching:

```bash
# Exact project name
python switch_project.py "Bulgul Rangers"

# Partial name matching
python switch_project.py "Marine"

# Filename matching
python switch_project.py "Miradi_Marine_Example_v0.48.xmpz2"
```

**Example Switch Output**:
```
🔄 SWITCHING PROJECT
============================================================
📁 Target: Miradi Marine Example
📄 File: Miradi_Marine_Example_v0.48.xmpz2

🗑️  Clearing current project...
🔄 Loading new project...

✅ PROJECT SWITCH SUCCESSFUL!
============================================================
📁 New Project: Miradi Marine Example
🔗 Nodes: 310
🔗 Relationships: 613
⏱️  Switch Time: 2.4s

🎉 You can now query the new project data!
```

### Listing Available Projects

```bash
# Show only available projects
python switch_project.py --list
```

## Analyzing Projects

### Comprehensive Project Analysis

Use `analyze_all_projects.py` to analyze projects without loading them into Neo4j:

```bash
# Basic analysis of all projects
python analyze_all_projects.py
```

**Example Output**:
```
🔍 MIRADI PROJECT ANALYZER
======================================================================
📂 Found 11 Miradi projects to analyze
   (Analysis only - no data will be loaded into Neo4j)

🚀 Starting project analysis...
======================================================================
📁 [1/11] Bulgul Rangers
   🔍 Analyzing...
   ✅ Complete! 1,373 elements, 100.0% coverage (3.4s)

📁 [2/11] Caring For Country
   🔍 Analyzing...
   ✅ Complete! 759 elements, 100.0% coverage (2.8s)
...

======================================================================
📊 PROJECT ANALYSIS SUMMARY
======================================================================
✅ Successfully Analyzed: 11/11
❌ Analysis Failures: 0
⏱️  Total Analysis Time: 18.9s

📈 AGGREGATE STATISTICS:
   • Total Elements Parsed: 8,488
   • Average Schema Coverage: 100.0%
   • Total Potential Nodes: 8,412
   • Total Potential Relationships: 19,884
   • Total Conversion Issues: 1,383
```

### Detailed Analysis with Error Reporting

```bash
# Include detailed error information
python analyze_all_projects.py --detailed
```

### Exporting Analysis Reports

```bash
# Export detailed JSON report
python analyze_all_projects.py --export analysis_report.json
```

The exported JSON contains:
- Project-by-project analysis results
- Aggregate statistics across all projects
- Detailed error information
- Schema coverage metrics

## Querying Conservation Data

Once a project is loaded, you can query the conservation data using Neo4j's Cypher query language.

### Accessing Neo4j Browser

1. Open your web browser
2. Navigate to `http://localhost:7474`
3. Login with your Neo4j credentials
4. Use the query examples below

### Basic Conservation Queries

#### 1. Find All Conservation Targets

```cypher
MATCH (target:CONSERVATION_TARGET)
RETURN target.name, target.id, target.node_type
ORDER BY target.name
```

#### 2. Find All Threats

```cypher
MATCH (threat:DIRECT_THREAT)
RETURN threat.name, threat.id, threat.node_type
ORDER BY threat.name
```

#### 3. Find All Strategies

```cypher
MATCH (strategy:STRATEGY)
RETURN strategy.name, strategy.id, strategy.node_type
ORDER BY strategy.name
```

### Conservation Relationship Queries

#### 1. Find Threats to Specific Targets

```cypher
MATCH (threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
WHERE target.name CONTAINS "Woodland"
RETURN threat.name as threat, target.name as target
ORDER BY threat.name
```

#### 2. Find Strategies That Mitigate Threats

```cypher
MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)
RETURN strategy.name as strategy, threat.name as threat
ORDER BY strategy.name
```

#### 3. Find Complete Conservation Logic Chains

```cypher
MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
RETURN activity.name as activity,
       strategy.name as strategy,
       threat.name as threat,
       target.name as target
ORDER BY target.name, threat.name
```

#### 4. Find Results Chains

```cypher
MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN strategy.name as strategy,
       result.name as result,
       target.name as target
ORDER BY target.name
```

### Advanced Analysis Queries

#### 1. Count Relationships by Type

```cypher
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
```

#### 2. Find Most Connected Conservation Elements

```cypher
MATCH (n)
WHERE n.node_type IN ['CONSERVATION_TARGET', 'DIRECT_THREAT', 'STRATEGY']
WITH n, size((n)--()) as connections
RETURN n.name, n.node_type, connections
ORDER BY connections DESC
LIMIT 10
```

#### 3. Find Strategies Without Activities

```cypher
MATCH (strategy:STRATEGY)
WHERE NOT (strategy)<-[:IMPLEMENTS]-(:ACTIVITY)
RETURN strategy.name, strategy.id
ORDER BY strategy.name
```

#### 4. Find Targets Without Strategies

```cypher
MATCH (target:CONSERVATION_TARGET)
WHERE NOT (target)<-[:ENHANCES]-(:RESULT)<-[:CONTRIBUTES_TO]-(:STRATEGY)
RETURN target.name, target.id
ORDER BY target.name
```

### Project Metadata Queries

#### 1. Get Current Project Information

```cypher
MATCH (p:PROJECT {id: 'current_project'})
RETURN p.name as project_name,
       p.filename as filename,
       p.loaded_at as loaded_at,
       p.nodes_count as nodes,
       p.relationships_count as relationships,
       p.schema_coverage as coverage
```

#### 2. Get Node Type Counts

```cypher
MATCH (n)
WHERE n.node_type IS NOT NULL
RETURN n.node_type as node_type, count(n) as count
ORDER BY count DESC
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Neo4j connection failed"

**Problem**: Cannot connect to Neo4j database

**Solutions**:
```bash
# Test connection
python test_neo4j_connection.py

# Check if Neo4j is running
docker ps  # If using Docker

# Verify .env file settings
cat .env
```

**Check these settings**:
- `NEO4J_URI=bolt://localhost:7687`
- `NEO4J_USER=neo4j`
- `NEO4J_PASSWORD=your_password`

#### 2. "Project file not found"

**Problem**: Cannot find the specified .xmpz2 file

**Solutions**:
```bash
# Check file exists
ls data/sample_projects/

# Use full path
python load_project.py /full/path/to/project.xmpz2

# Check file permissions
ls -la data/sample_projects/project.xmpz2
```

#### 3. "Constraint validation failed"

**Problem**: Trying to load duplicate data

**Solutions**:
```bash
# Clear database before loading
python load_project.py project.xmpz2 --clear

# Or manually clear database
python clear_neo4j.py
```

#### 4. "Validation warnings during loading"

**Problem**: Seeing many "invalid source ID" warnings

**This is normal!** These warnings indicate:
- Diagram links to unimplemented element types
- Core conservation relationships still work correctly
- No action needed - the system handles this gracefully

#### 5. "Memory issues with large projects"

**Problem**: System runs out of memory

**Solutions**:
- Close other applications
- Use a machine with more RAM
- Process smaller projects first
- Contact support for optimization tips

### Getting Help

#### 1. Check System Status

```bash
# Test Neo4j connection
python test_neo4j_connection.py

# Test parser with sample data
python test_parser_basic.py

# Test schema mapping
python test_schema_mapper.py
```

#### 2. Enable Detailed Logging

Add to your script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 3. Check Project File Integrity

```bash
# Analyze without loading
python analyze_all_projects.py --detailed
```

## Best Practices

### 1. Project Management

**Always use `--clear` when switching projects**:
```bash
python load_project.py new_project.xmpz2 --clear
```

**Check current status before loading**:
```bash
python switch_project.py
```

**Use project switching for convenience**:
```bash
python switch_project.py "Marine"
```

### 2. Data Analysis

**Start with analysis before loading**:
```bash
python analyze_all_projects.py
```

**Export analysis for documentation**:
```bash
python analyze_all_projects.py --export project_analysis.json
```

### 3. Querying

**Start with simple queries**:
```cypher
MATCH (n) RETURN count(n)  // Count all nodes
```

**Use LIMIT for large results**:
```cypher
MATCH (n:CONSERVATION_TARGET) RETURN n LIMIT 10
```

**Check relationship types first**:
```cypher
MATCH ()-[r]->() RETURN DISTINCT type(r)
```

### 4. Performance

**For large projects**:
- Use `--clear` to avoid constraint conflicts
- Close unnecessary applications
- Monitor system resources
- Consider batch processing for multiple projects

**For complex queries**:
- Use indexes (automatically created)
- Add LIMIT clauses
- Profile queries with `PROFILE` prefix
- Use specific node labels in MATCH clauses

### 5. Data Integrity

**Always verify successful loading**:
- Check the success message
- Verify node and relationship counts
- Run a simple query to confirm data

**Regular maintenance**:
```bash
# Clear database periodically
python clear_neo4j.py

# Reload current project
python switch_project.py "Current Project Name"
```

### 6. Backup and Recovery

**Before major operations**:
1. Note current project name
2. Export analysis if needed
3. Have project files backed up

**Recovery process**:
```bash
# Clear and reload
python load_project.py backup_project.xmpz2 --clear
```

## Next Steps

Once you're comfortable with basic operations:

1. **Explore Advanced Queries**: Try complex conservation analysis queries
2. **Analyze Multiple Projects**: Compare different conservation approaches
3. **Export Data**: Use analysis exports for reporting
4. **Integration**: Prepare for GraphRAG and API integration
5. **Custom Analysis**: Develop project-specific queries

For advanced usage and development, see:
- [API Reference](10-api-reference.md)
- [Sample Queries](sample-queries.md)
- [Architecture Overview](01-architecture-overview.md)
