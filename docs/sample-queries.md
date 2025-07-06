# Sample Neo4j Queries for Conservation Data

This document provides a comprehensive collection of Cypher queries for analyzing Miradi conservation projects loaded into Neo4j. All examples use real data from the Bulgul Rangers project.

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Conservation Relationship Queries](#conservation-relationship-queries)
3. [Analysis and Metrics](#analysis-and-metrics)
4. [Project Management Queries](#project-management-queries)
5. [Advanced Conservation Analysis](#advanced-conservation-analysis)
6. [Troubleshooting Queries](#troubleshooting-queries)
7. [Performance Optimization](#performance-optimization)

## Basic Queries

### 1. Count All Nodes

```cypher
MATCH (n) 
RETURN count(n) as total_nodes
```

**Expected Result**: `1,367` (for Bulgul Rangers project)

### 2. Count Nodes by Type

```cypher
MATCH (n)
WHERE n.node_type IS NOT NULL
RETURN n.node_type as node_type, count(n) as count
ORDER BY count DESC
```

**Expected Results**:
```
DIAGRAM_FACTOR     892
DIAGRAM_LINK       341
ACTIVITY           45
RESULT             25
STRATEGY           18
CONTRIBUTING_FACTOR 15
CONSERVATION_TARGET 12
RESULTS_CHAIN      8
DIRECT_THREAT      8
CONCEPTUAL_MODEL   3
PROJECT            1
```

### 3. List All Conservation Targets

```cypher
MATCH (target:CONSERVATION_TARGET)
RETURN target.name, target.id, target.uuid
ORDER BY target.name
```

### 4. List All Direct Threats

```cypher
MATCH (threat:DIRECT_THREAT)
RETURN threat.name, threat.id, threat.uuid
ORDER BY threat.name
```

### 5. List All Strategies

```cypher
MATCH (strategy:STRATEGY)
RETURN strategy.name, strategy.id, strategy.uuid
ORDER BY strategy.name
```

## Conservation Relationship Queries

### 1. Find All Threat-Target Relationships

```cypher
MATCH (threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
RETURN threat.name as threat, target.name as target
ORDER BY target.name, threat.name
```

**Example Results**:
```
"Inappropriate fire regimes" → "Eucalyptus tetrodonta woodland"
"Invasive weeds" → "Eucalyptus tetrodonta woodland"
"Feral animals" → "Native fauna assemblages"
```

### 2. Find All Strategy-Threat Mitigation

```cypher
MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)
RETURN strategy.name as strategy, threat.name as threat
ORDER BY threat.name, strategy.name
```

**Example Results**:
```
"Traditional burning practices" → "Inappropriate fire regimes"
"Weed control programs" → "Invasive weeds"
"Feral animal management" → "Feral animals"
```

### 3. Find Strategy-Result-Target Enhancement Chains

```cypher
MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN strategy.name as strategy,
       result.name as result,
       target.name as target
ORDER BY target.name, strategy.name
```

### 4. Find Complete Conservation Logic Chains

```cypher
MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
RETURN activity.name as activity,
       strategy.name as strategy,
       threat.name as threat,
       target.name as target
ORDER BY target.name, threat.name
LIMIT 10
```

### 5. Find Activity-Strategy Implementation

```cypher
MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)
RETURN activity.name as activity, strategy.name as strategy
ORDER BY strategy.name, activity.name
LIMIT 10
```

## Analysis and Metrics

### 1. Count Relationships by Type

```cypher
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
```

**Expected Results**:
```
BELONGS_TO_PROJECT  1,366
LINKS               872
PART_OF             582
IMPLEMENTS          191
THREATENS           95
CONTRIBUTES_TO      86
MITIGATES           83
ENHANCES            79
```

### 2. Find Most Connected Conservation Elements

```cypher
MATCH (n)
WHERE n.node_type IN ['CONSERVATION_TARGET', 'DIRECT_THREAT', 'STRATEGY', 'ACTIVITY']
WITH n, size((n)--()) as connections
RETURN n.name, n.node_type, connections
ORDER BY connections DESC
LIMIT 10
```

### 3. Find Conservation Targets with Most Threats

```cypher
MATCH (target:CONSERVATION_TARGET)<-[:THREATENS]-(threat:DIRECT_THREAT)
WITH target, count(threat) as threat_count
RETURN target.name, threat_count
ORDER BY threat_count DESC
```

### 4. Find Strategies with Most Activities

```cypher
MATCH (strategy:STRATEGY)<-[:IMPLEMENTS]-(activity:ACTIVITY)
WITH strategy, count(activity) as activity_count
RETURN strategy.name, activity_count
ORDER BY activity_count DESC
```

### 5. Find Threats with Most Mitigation Strategies

```cypher
MATCH (threat:DIRECT_THREAT)<-[:MITIGATES]-(strategy:STRATEGY)
WITH threat, count(strategy) as strategy_count
RETURN threat.name, strategy_count
ORDER BY strategy_count DESC
```

## Project Management Queries

### 1. Get Current Project Information

```cypher
MATCH (p:PROJECT {id: 'current_project'})
RETURN p.name as project_name,
       p.filename as filename,
       p.loaded_at as loaded_at,
       p.nodes_count as nodes,
       p.relationships_count as relationships,
       p.schema_coverage as coverage,
       p.load_time as load_time
```

### 2. Verify Project Data Integrity

```cypher
MATCH (p:PROJECT {id: 'current_project'})
WITH p.nodes_count as expected_nodes, p.relationships_count as expected_rels
MATCH (n) WITH expected_nodes, expected_rels, count(n) as actual_nodes
MATCH ()-[r]->() WITH expected_nodes, expected_rels, actual_nodes, count(r) as actual_rels
RETURN expected_nodes, actual_nodes, expected_rels, actual_rels,
       CASE WHEN expected_nodes = actual_nodes AND expected_rels = actual_rels 
            THEN 'VERIFIED' ELSE 'MISMATCH' END as status
```

### 3. Find Elements Not Belonging to Current Project

```cypher
MATCH (n)
WHERE NOT (n)-[:BELONGS_TO_PROJECT]->(:PROJECT {id: 'current_project'})
  AND n.node_type <> 'PROJECT'
RETURN n.node_type, count(n) as orphaned_count
ORDER BY orphaned_count DESC
```

## Advanced Conservation Analysis

### 1. Find Conservation Gaps (Targets Without Strategies)

```cypher
MATCH (target:CONSERVATION_TARGET)
WHERE NOT (target)<-[:ENHANCES]-(:RESULT)<-[:CONTRIBUTES_TO]-(:STRATEGY)
RETURN target.name as unprotected_target, target.id
ORDER BY target.name
```

### 2. Find Unmitigated Threats

```cypher
MATCH (threat:DIRECT_THREAT)
WHERE NOT (threat)<-[:MITIGATES]-(:STRATEGY)
RETURN threat.name as unmitigated_threat, threat.id
ORDER BY threat.name
```

### 3. Find Strategies Without Implementation

```cypher
MATCH (strategy:STRATEGY)
WHERE NOT (strategy)<-[:IMPLEMENTS]-(:ACTIVITY)
RETURN strategy.name as unimplemented_strategy, strategy.id
ORDER BY strategy.name
```

### 4. Find Results Chains (Strategy → Result → Target)

```cypher
MATCH path = (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN strategy.name as strategy,
       result.name as result,
       target.name as target,
       length(path) as chain_length
ORDER BY target.name, strategy.name
```

### 5. Find Multi-Threat Targets (Targets Facing Multiple Threats)

```cypher
MATCH (target:CONSERVATION_TARGET)<-[:THREATENS]-(threat:DIRECT_THREAT)
WITH target, collect(threat.name) as threats, count(threat) as threat_count
WHERE threat_count > 1
RETURN target.name, threats, threat_count
ORDER BY threat_count DESC
```

### 6. Find Multi-Strategy Threats (Threats with Multiple Mitigation Strategies)

```cypher
MATCH (threat:DIRECT_THREAT)<-[:MITIGATES]-(strategy:STRATEGY)
WITH threat, collect(strategy.name) as strategies, count(strategy) as strategy_count
WHERE strategy_count > 1
RETURN threat.name, strategies, strategy_count
ORDER BY strategy_count DESC
```

### 7. Find Conservation Impact Paths

```cypher
MATCH path = (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN activity.name as activity,
       strategy.name as strategy,
       result.name as result,
       target.name as target,
       length(path) as impact_chain_length
ORDER BY target.name
LIMIT 10
```

### 8. Find Threat Mitigation Paths

```cypher
MATCH path = (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
RETURN activity.name as activity,
       strategy.name as strategy,
       threat.name as threat,
       target.name as target,
       length(path) as mitigation_chain_length
ORDER BY target.name
LIMIT 10
```

## Troubleshooting Queries

### 1. Find Nodes with Missing Properties

```cypher
MATCH (n)
WHERE n.name IS NULL OR n.id IS NULL
RETURN n.node_type, count(n) as missing_properties_count
ORDER BY missing_properties_count DESC
```

### 2. Find Duplicate IDs

```cypher
MATCH (n)
WHERE n.id IS NOT NULL
WITH n.id as node_id, collect(n) as nodes
WHERE size(nodes) > 1
RETURN node_id, size(nodes) as duplicate_count, [node IN nodes | node.node_type] as node_types
```

### 3. Find Orphaned Relationships

```cypher
MATCH ()-[r]->()
WHERE startNode(r).id IS NULL OR endNode(r).id IS NULL
RETURN type(r) as relationship_type, count(r) as orphaned_count
```

### 4. Validate Conservation Logic

```cypher
// Check for threats that don't threaten anything
MATCH (threat:DIRECT_THREAT)
WHERE NOT (threat)-[:THREATENS]->()
RETURN 'Threats without targets' as issue, count(threat) as count

UNION

// Check for strategies that don't mitigate or contribute
MATCH (strategy:STRATEGY)
WHERE NOT (strategy)-[:MITIGATES]->() AND NOT (strategy)-[:CONTRIBUTES_TO]->()
RETURN 'Strategies without effects' as issue, count(strategy) as count

UNION

// Check for activities that don't implement anything
MATCH (activity:ACTIVITY)
WHERE NOT (activity)-[:IMPLEMENTS]->()
RETURN 'Activities without strategies' as issue, count(activity) as count
```

### 5. Find Relationship Validation Errors

```cypher
// Find THREATENS relationships not between threats and targets
MATCH (source)-[:THREATENS]->(target)
WHERE NOT (source:DIRECT_THREAT AND target:CONSERVATION_TARGET)
RETURN 'Invalid THREATENS relationship' as error,
       source.node_type as source_type,
       target.node_type as target_type,
       count(*) as count

UNION

// Find MITIGATES relationships not between strategies and threats
MATCH (source)-[:MITIGATES]->(target)
WHERE NOT (source:STRATEGY AND target:DIRECT_THREAT)
RETURN 'Invalid MITIGATES relationship' as error,
       source.node_type as source_type,
       target.node_type as target_type,
       count(*) as count
```

## Performance Optimization

### 1. Check Index Usage

```cypher
CALL db.indexes()
YIELD name, type, state, populationPercent
RETURN name, type, state, populationPercent
ORDER BY name
```

### 2. Profile Query Performance

```cypher
PROFILE
MATCH (threat:DIRECT_THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
RETURN threat.name, target.name
```

### 3. Explain Query Execution Plan

```cypher
EXPLAIN
MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result:RESULT)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN strategy.name, result.name, target.name
```

### 4. Find Expensive Queries (Monitor)

```cypher
// Use this to identify slow queries
CALL dbms.listQueries()
YIELD query, elapsedTimeMillis, allocatedBytes
WHERE elapsedTimeMillis > 1000
RETURN query, elapsedTimeMillis, allocatedBytes
ORDER BY elapsedTimeMillis DESC
```

## Query Templates for Custom Analysis

### 1. Template: Find Elements by Property

```cypher
MATCH (n:NODE_TYPE)
WHERE n.property_name CONTAINS 'search_term'
RETURN n.name, n.property_name
ORDER BY n.name
```

### 2. Template: Find Relationship Patterns

```cypher
MATCH (source:SOURCE_TYPE)-[:RELATIONSHIP_TYPE]->(target:TARGET_TYPE)
WHERE source.property = 'value'
RETURN source.name, target.name
ORDER BY source.name
```

### 3. Template: Count Relationships by Property

```cypher
MATCH (n:NODE_TYPE)-[r:RELATIONSHIP_TYPE]->()
WITH n, count(r) as relationship_count
WHERE relationship_count > threshold
RETURN n.name, relationship_count
ORDER BY relationship_count DESC
```

### 4. Template: Find Paths Between Node Types

```cypher
MATCH path = (start:START_TYPE)-[*1..3]-(end:END_TYPE)
WHERE start.name = 'specific_name'
RETURN path, length(path) as path_length
ORDER BY path_length
LIMIT 10
```

## Conservation-Specific Query Examples

### 1. Ecosystem Health Assessment

```cypher
// Find targets with high threat pressure
MATCH (target:CONSERVATION_TARGET)<-[:THREATENS]-(threat:DIRECT_THREAT)
WITH target, count(threat) as threat_count
MATCH (target)<-[:ENHANCES]-(:RESULT)<-[:CONTRIBUTES_TO]-(strategy:STRATEGY)
WITH target, threat_count, count(strategy) as strategy_count
RETURN target.name,
       threat_count,
       strategy_count,
       CASE 
         WHEN strategy_count >= threat_count THEN 'Well Protected'
         WHEN strategy_count > 0 THEN 'Partially Protected'
         ELSE 'Vulnerable'
       END as protection_status
ORDER BY threat_count DESC, strategy_count ASC
```

### 2. Strategy Effectiveness Analysis

```cypher
// Find strategies addressing multiple threats
MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)
WITH strategy, collect(threat.name) as threats_addressed, count(threat) as threat_count
WHERE threat_count > 1
RETURN strategy.name, threats_addressed, threat_count
ORDER BY threat_count DESC
```

### 3. Implementation Gap Analysis

```cypher
// Find strategies with low implementation
MATCH (strategy:STRATEGY)
OPTIONAL MATCH (strategy)<-[:IMPLEMENTS]-(activity:ACTIVITY)
WITH strategy, count(activity) as activity_count
WHERE activity_count < 2  // Strategies with fewer than 2 activities
RETURN strategy.name, activity_count
ORDER BY activity_count, strategy.name
```

### 4. Conservation Priority Analysis

```cypher
// Find high-priority conservation targets (many threats, few strategies)
MATCH (target:CONSERVATION_TARGET)
OPTIONAL MATCH (target)<-[:THREATENS]-(threat:DIRECT_THREAT)
OPTIONAL MATCH (target)<-[:ENHANCES]-(:RESULT)<-[:CONTRIBUTES_TO]-(strategy:STRATEGY)
WITH target, 
     count(DISTINCT threat) as threat_count,
     count(DISTINCT strategy) as strategy_count
RETURN target.name,
       threat_count,
       strategy_count,
       (threat_count * 1.0 / CASE WHEN strategy_count = 0 THEN 1 ELSE strategy_count END) as priority_score
ORDER BY priority_score DESC
```

## Tips for Writing Effective Queries

### 1. Use Specific Node Labels

```cypher
// Good: Specific labels
MATCH (target:CONSERVATION_TARGET)

// Avoid: Generic matching
MATCH (n) WHERE n.node_type = 'CONSERVATION_TARGET'
```

### 2. Add LIMIT for Large Results

```cypher
MATCH (n:ACTIVITY)
RETURN n.name
ORDER BY n.name
LIMIT 20  // Always limit large result sets
```

### 3. Use WHERE Clauses Effectively

```cypher
// Good: Filter early
MATCH (strategy:STRATEGY)
WHERE strategy.name CONTAINS 'fire'
MATCH (strategy)-[:MITIGATES]->(threat:DIRECT_THREAT)
RETURN strategy.name, threat.name

// Less efficient: Filter late
MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:DIRECT_THREAT)
WHERE strategy.name CONTAINS 'fire'
RETURN strategy.name, threat.name
```

### 4. Use OPTIONAL MATCH for Missing Data

```cypher
MATCH (strategy:STRATEGY)
OPTIONAL MATCH (strategy)<-[:IMPLEMENTS]-(activity:ACTIVITY)
RETURN strategy.name, count(activity) as activity_count
```

These queries provide a comprehensive toolkit for analyzing conservation data in Miradi Co-Pilot. Adapt them to your specific conservation questions and project needs.
