// ============================================================================
// MIRADI NEO4J DATABASE INSPECTION QUERIES
// ============================================================================
//
// A comprehensive collection of Cypher queries for inspecting and analyzing
// Miradi conservation projects loaded into Neo4j. Each query includes
// documentation, use cases, and expected output descriptions.
//
// Usage: Copy and paste queries into Neo4j Browser or use with Python scripts
// ============================================================================

// ============================================================================
// 1. PROJECT OVERVIEW - MAIN INSPECTION QUERY
// ============================================================================
// Purpose: Get complete project summary with counts and detailed lists
// Use Case: First query to run when inspecting a new project
// Returns: Project metadata, element counts, and lists of key elements
// Performance: Fast - aggregates across all major node types

// PROJECT METADATA QUERY
MATCH (p:PROJECT {id: 'current_project'})
RETURN {
    name: p.name,
    filename: p.filename,
    loaded_at: p.loaded_at,
    file_path: p.file_path,
    schema_coverage: p.schema_coverage,
    load_time: p.load_time
} AS project_info;

// ELEMENT COUNTS QUERY
OPTIONAL MATCH (target:CONSERVATION_TARGET)
OPTIONAL MATCH (threat:THREAT)
OPTIONAL MATCH (strategy:STRATEGY)
OPTIONAL MATCH (activity:ACTIVITY)
OPTIONAL MATCH (indicator:INDICATOR)
OPTIONAL MATCH (rc:RESULTS_CHAIN)

RETURN {
    conservation_targets: count(DISTINCT target),
    threats: count(DISTINCT threat),
    strategies: count(DISTINCT strategy),
    activities: count(DISTINCT activity),
    indicators: count(DISTINCT indicator),
    results_chains: count(DISTINCT rc)
} AS element_counts;

// CONSERVATION TARGETS LIST
MATCH (target:CONSERVATION_TARGET)
RETURN collect({
    id: target.id, 
    name: target.name,
    viability_status: target.viability_status
}) AS conservation_targets;

// INDICATORS LIST
MATCH (indicator:INDICATOR)
RETURN collect({
    id: indicator.id, 
    name: indicator.name,
    measurement_type: indicator.measurement_type
}) AS indicators;

// RESULTS CHAINS LIST
MATCH (rc:RESULTS_CHAIN)
RETURN collect({
    id: rc.id, 
    name: rc.name,
    description: rc.details
}) AS results_chains;

// ============================================================================
// 2. CONSERVATION RELATIONSHIP ANALYSIS
// ============================================================================
// Purpose: Analyze the conservation logic and relationships in the project
// Use Case: Understanding threat-target-strategy connections
// Returns: Relationship counts and examples of conservation logic

// 2.1 RELATIONSHIP SUMMARY
// Shows counts of all relationship types
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;

// 2.2 THREAT-TARGET RELATIONSHIPS
// Purpose: Show which threats affect which conservation targets
// Use Case: Threat assessment and prioritization
MATCH (threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
RETURN {
    threat_target_pairs: collect({
        threat_id: threat.id,
        threat_name: threat.name,
        target_id: target.id,
        target_name: target.name,
        threat_rating: threat.overall_threat_rating
    }),
    total_threat_relationships: count(*)
} AS threat_analysis;

// 2.3 STRATEGY-THREAT MITIGATION
// Purpose: Show which strategies mitigate which threats
// Use Case: Strategy effectiveness analysis
MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:THREAT)
RETURN {
    mitigation_pairs: collect({
        strategy_id: strategy.id,
        strategy_name: strategy.name,
        threat_id: threat.id,
        threat_name: threat.name,
        strategy_status: strategy.status
    }),
    total_mitigation_relationships: count(*)
} AS mitigation_analysis;

// 2.4 MONITORING FRAMEWORK (MEASURES relationships)
// Purpose: Show indicator-activity/strategy monitoring connections
// Use Case: Understanding monitoring coverage
MATCH (indicator:INDICATOR)-[:MEASURES]->(measured)
RETURN {
    monitoring_connections: collect({
        indicator_id: indicator.id,
        indicator_name: indicator.name,
        measures_type: labels(measured)[0],
        measures_id: measured.id,
        measures_name: measured.name
    }),
    total_measures_relationships: count(*),
    unique_indicators: count(DISTINCT indicator),
    monitored_elements: count(DISTINCT measured)
} AS monitoring_analysis;

// ============================================================================
// 3. SPATIAL DATA INSPECTION
// ============================================================================
// Purpose: Analyze spatial data coverage and distribution
// Use Case: Verifying spatial data extraction and visualization readiness

// 3.1 SPATIAL DATA COVERAGE
// Shows how many diagram factors have spatial coordinates
MATCH (df:DIAGRAM_FACTOR)
WITH df,
     CASE WHEN df.location <> '{}' AND df.location IS NOT NULL THEN 1 ELSE 0 END as has_location,
     CASE WHEN df.size <> '{}' AND df.size IS NOT NULL THEN 1 ELSE 0 END as has_size
RETURN {
    total_diagram_factors: count(df),
    factors_with_location: sum(has_location),
    factors_with_size: sum(has_size),
    spatial_coverage_percent: round(100.0 * sum(has_location) / count(df), 1),
    size_coverage_percent: round(100.0 * sum(has_size) / count(df), 1)
} AS spatial_coverage;

// 3.2 SPATIAL BOUNDS CALCULATION
// Calculate the bounding box of all diagram elements
MATCH (df:DIAGRAM_FACTOR)
WHERE df.location <> '{}' AND df.location IS NOT NULL
WITH df,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y,
     toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]) as width,
     toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]) as height

RETURN {
    diagram_bounds: {
        min_x: min(x),
        max_x: max(x + width),
        min_y: min(y),
        max_y: max(y + height),
        total_width: max(x + width) - min(x),
        total_height: max(y + height) - min(y),
        center_x: (max(x + width) + min(x)) / 2,
        center_y: (max(y + height) + min(y)) / 2
    },
    elements_with_coordinates: count(df)
} AS spatial_bounds;

// 3.3 SPATIAL DISTRIBUTION BY ELEMENT TYPE
// Shows how different conservation elements are distributed spatially
MATCH (df:DIAGRAM_FACTOR)
WHERE df.location <> '{}' AND df.location IS NOT NULL
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
WITH df, element,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y

RETURN {
    element_type: labels(element)[0],
    count: count(element),
    spatial_stats: {
        avg_x: round(avg(x), 1),
        avg_y: round(avg(y), 1),
        min_x: min(x),
        max_x: max(x),
        min_y: min(y),
        max_y: max(y)
    }
} AS spatial_distribution
ORDER BY count DESC;

// ============================================================================
// 4. DATA QUALITY CHECKS
// ============================================================================
// Purpose: Identify potential data quality issues
// Use Case: Troubleshooting and data validation

// 4.1 NODES WITHOUT NAMES
// Find nodes that might be missing important name properties
MATCH (n)
WHERE n.name IS NULL OR n.name = ''
RETURN labels(n)[0] as node_type, count(n) as count_without_names
ORDER BY count_without_names DESC;

// 4.2 ORPHANED NODES
// Find nodes that have no relationships (might indicate parsing issues)
MATCH (n)
WHERE NOT (n)-[]-()
RETURN labels(n)[0] as node_type, count(n) as orphaned_count, 
       collect(n.id)[0..5] as sample_ids
ORDER BY orphaned_count DESC;

// 4.3 DIAGRAM FACTORS WITHOUT WRAPPED ELEMENTS
// Find diagram factors that don't link to actual conservation elements
MATCH (df:DIAGRAM_FACTOR)
WHERE NOT EXISTS {
    MATCH (element) WHERE element.id = df.wrapped_factor_id
}
RETURN count(df) as unlinked_diagram_factors,
       collect(df.id)[0..10] as sample_factor_ids;

// 4.4 MISSING CRITICAL RELATIONSHIPS
// Check for conservation elements that might be missing key relationships
MATCH (target:CONSERVATION_TARGET)
WHERE NOT EXISTS { (target)<-[:THREATENS]-() }
RETURN {
    targets_without_threats: count(target),
    sample_targets: collect({id: target.id, name: target.name})[0..5]
} AS targets_missing_threats

UNION ALL

MATCH (threat:THREAT)
WHERE NOT EXISTS { (threat)-[:THREATENS]->() }
RETURN {
    threats_without_targets: count(threat),
    sample_threats: collect({id: threat.id, name: threat.name})[0..5]
} AS threats_missing_targets;

// ============================================================================
// 5. PERFORMANCE AND STATISTICS
// ============================================================================
// Purpose: Database performance metrics and detailed statistics
// Use Case: Understanding database size and query performance

// 5.1 DATABASE SIZE OVERVIEW
// Get overall database statistics
MATCH (n)
OPTIONAL MATCH ()-[r]->()
RETURN {
    total_nodes: count(DISTINCT n),
    total_relationships: count(r),
    node_types: count(DISTINCT labels(n)[0]),
    relationship_types: count(DISTINCT type(r))
} AS database_stats;

// 5.2 NODE TYPE DISTRIBUTION
// Detailed breakdown of all node types
MATCH (n)
RETURN labels(n)[0] as node_type, count(n) as count
ORDER BY count DESC;

// 5.3 RELATIONSHIP TYPE DISTRIBUTION
// Detailed breakdown of all relationship types
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;

// ============================================================================
// 6. CONSERVATION ANALYSIS QUERIES
// ============================================================================
// Purpose: Advanced conservation planning analysis
// Use Case: Strategic conservation planning insights

// 6.1 COMPLETE CONSERVATION PATHWAYS
// Find complete threat-strategy-result-target pathways
MATCH path = (threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
<-[:ENHANCES]-(result)-[:CONTRIBUTES_TO]-(strategy:STRATEGY)
-[:MITIGATES]->(threat)
RETURN {
    pathway: {
        threat_name: threat.name,
        target_name: target.name,
        strategy_name: strategy.name,
        result_name: result.name
    },
    pathway_length: length(path)
} AS conservation_pathways
LIMIT 10;

// 6.2 STRATEGY IMPLEMENTATION ANALYSIS
// Show which strategies have activities and monitoring
MATCH (strategy:STRATEGY)
OPTIONAL MATCH (strategy)<-[:IMPLEMENTS]-(activity:ACTIVITY)
OPTIONAL MATCH (strategy)<-[:MEASURES]-(indicator:INDICATOR)
RETURN {
    strategy_id: strategy.id,
    strategy_name: strategy.name,
    activity_count: count(DISTINCT activity),
    indicator_count: count(DISTINCT indicator),
    implementation_status: CASE 
        WHEN count(DISTINCT activity) > 0 AND count(DISTINCT indicator) > 0 THEN 'Fully Planned'
        WHEN count(DISTINCT activity) > 0 THEN 'Activities Planned'
        WHEN count(DISTINCT indicator) > 0 THEN 'Monitoring Planned'
        ELSE 'Planning Needed'
    END
} AS strategy_implementation
ORDER BY activity_count DESC, indicator_count DESC;

// 6.3 THREAT PRIORITY ANALYSIS
// Analyze threats by number of targets affected and mitigation strategies
MATCH (threat:THREAT)
OPTIONAL MATCH (threat)-[:THREATENS]->(target:CONSERVATION_TARGET)
OPTIONAL MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat)
RETURN {
    threat_id: threat.id,
    threat_name: threat.name,
    threat_rating: threat.overall_threat_rating,
    targets_affected: count(DISTINCT target),
    mitigation_strategies: count(DISTINCT strategy),
    priority_score: count(DISTINCT target) * 
                   CASE threat.overall_threat_rating 
                       WHEN 'High' THEN 3 
                       WHEN 'Medium' THEN 2 
                       WHEN 'Low' THEN 1 
                       ELSE 1 
                   END
} AS threat_priority
ORDER BY priority_score DESC;

// ============================================================================
// 7. QUICK DIAGNOSTIC QUERIES
// ============================================================================
// Purpose: Fast queries for common troubleshooting
// Use Case: Quick health checks and debugging

// 7.1 PROJECT HEALTH CHECK
// Quick overview of project status
MATCH (p:PROJECT {id: 'current_project'})
OPTIONAL MATCH (n)
OPTIONAL MATCH ()-[r]->()
OPTIONAL MATCH (df:DIAGRAM_FACTOR) WHERE df.location <> '{}'
RETURN {
    project_name: p.name,
    loaded_at: p.loaded_at,
    total_nodes: count(DISTINCT n),
    total_relationships: count(r),
    spatial_elements: count(df),
    health_status: CASE 
        WHEN count(DISTINCT n) > 100 AND count(r) > 100 THEN 'Healthy'
        WHEN count(DISTINCT n) > 50 THEN 'Moderate'
        ELSE 'Needs Investigation'
    END
} AS health_check;

// 7.2 RECENT ACTIVITY CHECK
// Check if data was loaded recently
MATCH (p:PROJECT {id: 'current_project'})
RETURN {
    project_name: p.name,
    loaded_at: p.loaded_at,
    hours_since_load: duration.between(p.loaded_at, datetime()).hours,
    is_recent: duration.between(p.loaded_at, datetime()).hours < 24
} AS recent_activity;

// 7.3 CONSERVATION COMPLETENESS CHECK
// Quick check of conservation logic completeness
MATCH (target:CONSERVATION_TARGET)
OPTIONAL MATCH (target)<-[:THREATENS]-(threat:THREAT)
OPTIONAL MATCH (threat)<-[:MITIGATES]-(strategy:STRATEGY)
RETURN {
    total_targets: count(DISTINCT target),
    targets_with_threats: count(DISTINCT CASE WHEN threat IS NOT NULL THEN target END),
    threats_with_strategies: count(DISTINCT CASE WHEN strategy IS NOT NULL THEN threat END),
    conservation_completeness: round(100.0 * count(DISTINCT CASE WHEN strategy IS NOT NULL THEN target END) / count(DISTINCT target), 1)
} AS conservation_completeness;

// ============================================================================
// 8. RESULTS CHAIN VISUALIZATION QUERIES
// ============================================================================
// Purpose: Create Miradi-style results chain visualizations
// Use Case: Recreate the results chain view from Miradi in Neo4j Browser

// 8.1 COMPLETE RESULTS CHAIN VISUALIZATION
// Purpose: Get all elements in a specific results chain with their relationships and spatial data
// Use Case: Recreate the Miradi results chain diagram in Neo4j Browser
// Example: Replace '6085' with any results chain ID

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id

// Get all element IDs in this results chain for filtering relationships
WITH rc, df, element, 
     collect(DISTINCT element.id) as chain_element_ids

// Find relationships between elements within this results chain
OPTIONAL MATCH (element)-[rel:IMPLEMENTS|MITIGATES|THREATENS|CONTRIBUTES_TO|ENHANCES|MEASURES]-(connected)
WHERE connected.id IN chain_element_ids

RETURN rc, df, element, rel, connected,
       labels(element)[0] as element_type,
       labels(connected)[0] as connected_type,
       {
           x: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]),
           y: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]),
           width: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]),
           height: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1])
       } as spatial_data;

// 8.2 RESULTS CHAIN ELEMENTS ONLY (for simpler visualization)
// Purpose: Get just the conservation elements in a results chain without relationships
// Use Case: See what elements are in the results chain

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id
RETURN element, labels(element)[0] as element_type, df.location, df.size
ORDER BY labels(element)[0], element.name;

// 8.2b RESULTS CHAIN ELEMENT TYPE BREAKDOWN
// Purpose: Count elements by type in the results chain
// Use Case: Understanding the composition of the results chain

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id
RETURN labels(element)[0] as element_type, 
       count(*) as count,
       collect(element.name)[0..3] as sample_names
ORDER BY count DESC;

// 8.3 RESULTS CHAIN WITH CONSERVATION RELATIONSHIPS
// Purpose: Show the conservation logic flow within a results chain
// Use Case: Understanding how strategies, activities, outcomes, and threats connect

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id

// Get all element IDs in this results chain for filtering relationships
WITH rc, element, collect(DISTINCT element.id) as chain_element_ids

// Find conservation relationships between elements in this results chain
OPTIONAL MATCH (element)-[rel:IMPLEMENTS|MITIGATES|THREATENS|CONTRIBUTES_TO|ENHANCES]-(connected)
WHERE connected.id IN chain_element_ids

RETURN element, rel, connected,
       labels(element)[0] as from_type,
       labels(connected)[0] as to_type,
       type(rel) as relationship_type
ORDER BY relationship_type, from_type, to_type;

// 8.4 RESULTS CHAIN SPATIAL LAYOUT
// Purpose: Get spatial positioning data for custom visualization
// Use Case: Building custom D3.js, Cytoscape.js, or other visualizations

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id

WITH rc.id as chain_id, rc.name as chain_name, 
     collect({
        id: element.id,
        name: element.name,
        type: labels(element)[0],
        position: {
            x: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]),
            y: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1])
        },
        size: {
            width: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]),
            height: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1])
        },
        diagram_factor_id: df.id
    }) as elements

RETURN {
    results_chain: {
        id: chain_id,
        name: chain_name
    },
    elements: elements
} AS results_chain_layout;

// 8.5 FIND ALL RESULTS CHAINS WITH ELEMENT COUNTS
// Purpose: Overview of all results chains in the project
// Use Case: Choosing which results chain to visualize

MATCH (rc:RESULTS_CHAIN)
OPTIONAL MATCH (rc)-[:CONTAINS]->(df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id

RETURN rc.id, rc.name, rc.identifier,
       count(DISTINCT df) as diagram_factors,
       count(DISTINCT element) as elements,
       collect(DISTINCT labels(element)[0]) as element_types
ORDER BY rc.name;

// 8.6 RESULTS CHAIN CONSERVATION PATHWAY ANALYSIS
// Purpose: Find conservation pathways within a results chain
// Use Case: Understanding the theory of change and conservation logic

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id

// Get all element IDs in this results chain for filtering pathways
WITH rc, collect(DISTINCT element.id) as chain_element_ids

// Find any conservation relationships within this results chain
MATCH (source)-[rel:IMPLEMENTS|MITIGATES|THREATENS|CONTRIBUTES_TO|ENHANCES|MEASURES]-(target)
WHERE source.id IN chain_element_ids AND target.id IN chain_element_ids

RETURN {
    pathway_type: type(rel),
    source_element: {
        id: source.id,
        name: source.name,
        type: labels(source)[0]
    },
    target_element: {
        id: target.id,
        name: target.name,
        type: labels(target)[0]
    },
    relationship_direction: CASE 
        WHEN startNode(rel) = source THEN 'outgoing'
        ELSE 'incoming'
    END
} AS conservation_pathways
ORDER BY pathway_type, source.name
LIMIT 20;

// ============================================================================
// 9. NEW CONSERVATION ELEMENTS ANALYSIS
// ============================================================================
// Purpose: Analyze the newly added conservation element types
// Use Case: Understanding intermediate results, threat reduction results, objectives, goals

// 9.1 INTERMEDIATE RESULTS ANALYSIS
// Purpose: Show intermediate results and their connections
// Use Case: Understanding theory of change progression

MATCH (ir:INTERMEDIATE_RESULT)
OPTIONAL MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(ir)
OPTIONAL MATCH (ir)-[:ENHANCES]->(target:CONSERVATION_TARGET)
OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(ir)

WITH ir.id as ir_id, ir.name as ir_name, ir.identifier as ir_identifier,
     collect(DISTINCT strategy.name) as contributing_strategies,
     collect(DISTINCT target.name) as enhanced_targets,
     collect(DISTINCT indicator.name) as monitoring_indicators,
     count(DISTINCT strategy) as strategy_count,
     count(DISTINCT target) as target_count,
     count(DISTINCT indicator) as indicator_count

RETURN {
    intermediate_result: {
        id: ir_id,
        name: ir_name,
        identifier: ir_identifier
    },
    contributing_strategies: contributing_strategies,
    enhanced_targets: enhanced_targets,
    monitoring_indicators: monitoring_indicators,
    strategy_count: strategy_count,
    target_count: target_count,
    indicator_count: indicator_count
} AS intermediate_result_analysis
ORDER BY ir_name;

// 9.2 THREAT REDUCTION RESULTS ANALYSIS
// Purpose: Show threat reduction results and their impact
// Use Case: Understanding conservation outcomes

MATCH (trr:THREAT_REDUCTION_RESULT)
OPTIONAL MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(trr)
OPTIONAL MATCH (trr)-[:ENHANCES]->(target:CONSERVATION_TARGET)
OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(trr)

WITH trr.id as trr_id, trr.name as trr_name, trr.identifier as trr_identifier,
     collect(DISTINCT strategy.name) as contributing_strategies,
     collect(DISTINCT target.name) as enhanced_targets,
     collect(DISTINCT indicator.name) as monitoring_indicators,
     count(DISTINCT strategy) as strategy_count,
     count(DISTINCT target) as target_count,
     count(DISTINCT indicator) as indicator_count

RETURN {
    threat_reduction_result: {
        id: trr_id,
        name: trr_name,
        identifier: trr_identifier
    },
    contributing_strategies: contributing_strategies,
    enhanced_targets: enhanced_targets,
    monitoring_indicators: monitoring_indicators,
    strategy_count: strategy_count,
    target_count: target_count,
    indicator_count: indicator_count
} AS threat_reduction_analysis
ORDER BY trr_name;

// 9.3 OBJECTIVES ANALYSIS
// Purpose: Show objectives and what they define
// Use Case: Understanding goal-setting framework

MATCH (obj:OBJECTIVE)
OPTIONAL MATCH (obj)-[:DEFINES]->(strategy:STRATEGY)
OPTIONAL MATCH (obj)-[:DEFINES]->(activity:ACTIVITY)
OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(obj)

WITH obj.id as obj_id, obj.name as obj_name, obj.identifier as obj_identifier, 
     obj.evidence_confidence as obj_evidence_confidence,
     collect(DISTINCT strategy.name) as defined_strategies,
     collect(DISTINCT activity.name) as defined_activities,
     collect(DISTINCT indicator.name) as monitoring_indicators,
     count(DISTINCT strategy) as strategy_count,
     count(DISTINCT activity) as activity_count,
     count(DISTINCT indicator) as indicator_count

RETURN {
    objective: {
        id: obj_id,
        name: obj_name,
        identifier: obj_identifier,
        evidence_confidence: obj_evidence_confidence
    },
    defined_strategies: defined_strategies,
    defined_activities: defined_activities,
    monitoring_indicators: monitoring_indicators,
    strategy_count: strategy_count,
    activity_count: activity_count,
    indicator_count: indicator_count
} AS objective_analysis
ORDER BY obj_name;

// 9.4 GOALS ANALYSIS
// Purpose: Show goals and their strategic connections
// Use Case: Understanding high-level conservation aims

MATCH (goal:GOAL)
OPTIONAL MATCH (goal)-[:DEFINES]->(strategy:STRATEGY)
OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(goal)

WITH goal.id as goal_id, goal.name as goal_name, goal.identifier as goal_identifier, 
     goal.details as goal_details,
     collect(DISTINCT strategy.name) as related_strategies,
     collect(DISTINCT indicator.name) as monitoring_indicators,
     count(DISTINCT strategy) as strategy_count,
     count(DISTINCT indicator) as indicator_count

RETURN {
    goal: {
        id: goal_id,
        name: goal_name,
        identifier: goal_identifier,
        details: goal_details
    },
    related_strategies: related_strategies,
    monitoring_indicators: monitoring_indicators,
    strategy_count: strategy_count,
    indicator_count: indicator_count
} AS goal_analysis
ORDER BY goal_name;

// 9.5 COMPLETE THEORY OF CHANGE PATHWAYS
// Purpose: Find complete pathways from activities to conservation outcomes
// Use Case: Understanding the full conservation logic chain

MATCH path = (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)
-[:CONTRIBUTES_TO]->(result)-[:ENHANCES]->(target:CONSERVATION_TARGET)

WHERE result:INTERMEDIATE_RESULT OR result:THREAT_REDUCTION_RESULT

RETURN {
    pathway: {
        activity_name: activity.name,
        activity_identifier: activity.identifier,
        strategy_name: strategy.name,
        result_name: result.name,
        result_type: labels(result)[0],
        target_name: target.name
    },
    pathway_length: length(path),
    pathway_elements: [node in nodes(path) | {name: node.name, type: labels(node)[0]}]
} AS complete_pathways
ORDER BY target.name, strategy.name
LIMIT 20;

// 9.6 CONSERVATION ELEMENT COMPLETENESS CHECK
// Purpose: Check completeness of conservation planning elements
// Use Case: Identifying gaps in conservation planning

MATCH (target:CONSERVATION_TARGET)
OPTIONAL MATCH (target)<-[:THREATENS]-(threat:THREAT)
OPTIONAL MATCH (threat)<-[:MITIGATES]-(strategy:STRATEGY)
OPTIONAL MATCH (strategy)<-[:IMPLEMENTS]-(activity:ACTIVITY)
OPTIONAL MATCH (strategy)-[:CONTRIBUTES_TO]->(result)
OPTIONAL MATCH (result)-[:ENHANCES]->(target)
OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(strategy)

WITH target.id as target_id, target.name as target_name,
     count(DISTINCT threat) as threat_count,
     count(DISTINCT strategy) as strategy_count,
     count(DISTINCT activity) as activity_count,
     count(DISTINCT result) as result_count,
     count(DISTINCT indicator) as indicator_count

RETURN {
    target: {
        id: target_id,
        name: target_name
    },
    conservation_completeness: {
        has_threats: threat_count > 0,
        has_strategies: strategy_count > 0,
        has_activities: activity_count > 0,
        has_results: result_count > 0,
        has_monitoring: indicator_count > 0,
        threat_count: threat_count,
        strategy_count: strategy_count,
        activity_count: activity_count,
        result_count: result_count,
        indicator_count: indicator_count
    },
    completeness_score: CASE 
        WHEN threat_count > 0 AND strategy_count > 0 AND 
             activity_count > 0 AND result_count > 0 AND 
             indicator_count > 0 THEN 'Complete'
        WHEN strategy_count > 0 AND activity_count > 0 THEN 'Partial'
        ELSE 'Minimal'
    END
} AS target_completeness
ORDER BY target_name;

// ============================================================================
// 10. ENHANCED RELATIONSHIP ANALYSIS
// ============================================================================
// Purpose: Analyze the enhanced conservation relationships
// Use Case: Understanding the complete conservation logic framework

// 10.1 CONTRIBUTES_TO RELATIONSHIP ANALYSIS
// Purpose: Show strategy-to-result contribution pathways
// Use Case: Understanding how strategies lead to conservation outcomes

MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result)
RETURN {
    contribution_type: labels(result)[0],
    strategy_name: strategy.name,
    result_name: result.name,
    strategy_status: strategy.status,
    result_identifier: result.identifier
} AS contribution_analysis
ORDER BY labels(result)[0], strategy.name;

// 10.2 ENHANCES RELATIONSHIP ANALYSIS
// Purpose: Show result-to-target enhancement pathways
// Use Case: Understanding how conservation results benefit targets

MATCH (result)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN {
    result_type: labels(result)[0],
    result_name: result.name,
    target_name: target.name,
    result_identifier: result.identifier,
    target_viability: target.viability_status
} AS enhancement_analysis
ORDER BY labels(result)[0], target.name;

// 10.3 DEFINES RELATIONSHIP ANALYSIS
// Purpose: Show objective-to-element definition relationships
// Use Case: Understanding goal-setting and planning framework

MATCH (objective:OBJECTIVE)-[:DEFINES]->(element)
RETURN {
    objective_name: objective.name,
    objective_identifier: objective.identifier,
    defined_element_type: labels(element)[0],
    defined_element_name: element.name,
    evidence_confidence: objective.evidence_confidence
} AS definition_analysis
ORDER BY objective.name, labels(element)[0];

// 10.4 COMPLETE CONSERVATION NETWORK
// Purpose: Show the complete network of conservation relationships
// Use Case: Understanding the full conservation planning framework

MATCH (n)-[r:IMPLEMENTS|MITIGATES|THREATENS|CONTRIBUTES_TO|ENHANCES|MEASURES|DEFINES]-(m)
RETURN {
    relationship_summary: {
        relationship_type: type(r),
        from_type: labels(n)[0],
        to_type: labels(m)[0],
        count: count(*)
    }
} AS relationship_summary
ORDER BY type(r), labels(n)[0], labels(m)[0];

// ============================================================================
// 11. RESULTS CHAIN ENHANCED ANALYSIS
// ============================================================================
// Purpose: Enhanced analysis of results chains with new element types
// Use Case: Complete understanding of results chain composition and logic

// 11.1 RESULTS CHAIN COMPLETE COMPOSITION
// Purpose: Show all element types in a results chain with counts
// Use Case: Understanding the full scope of a results chain

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id

RETURN {
    results_chain: {
        id: rc.id,
        name: rc.name,
        identifier: rc.identifier
    },
    composition: {
        conservation_targets: count(CASE WHEN element:CONSERVATION_TARGET THEN 1 END),
        threats: count(CASE WHEN element:THREAT THEN 1 END),
        strategies: count(CASE WHEN element:STRATEGY THEN 1 END),
        activities: count(CASE WHEN element:ACTIVITY THEN 1 END),
        intermediate_results: count(CASE WHEN element:INTERMEDIATE_RESULT THEN 1 END),
        threat_reduction_results: count(CASE WHEN element:THREAT_REDUCTION_RESULT THEN 1 END),
        indicators: count(CASE WHEN element:INDICATOR THEN 1 END),
        objectives: count(CASE WHEN element:OBJECTIVE THEN 1 END),
        goals: count(CASE WHEN element:GOAL THEN 1 END),
        total_elements: count(element)
    }
} AS complete_composition;

// 11.2 RESULTS CHAIN THEORY OF CHANGE
// Purpose: Show the complete theory of change within a results chain
// Use Case: Understanding the logical flow from activities to conservation outcomes

MATCH (rc:RESULTS_CHAIN {id: '6085'})-[:CONTAINS]->(df:DIAGRAM_FACTOR)
MATCH (element) WHERE element.id = df.wrapped_factor_id
WITH collect(DISTINCT element.id) as chain_element_ids

// Find theory of change pathways within the results chain
MATCH path = (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)
-[:CONTRIBUTES_TO]->(result)-[:ENHANCES]->(target:CONSERVATION_TARGET)

WHERE activity.id IN chain_element_ids 
  AND strategy.id IN chain_element_ids 
  AND result.id IN chain_element_ids 
  AND target.id IN chain_element_ids

RETURN {
    theory_of_change: {
        activity: {name: activity.name, identifier: activity.identifier},
        strategy: {name: strategy.name, status: strategy.status},
        result: {name: result.name, type: labels(result)[0]},
        target: {name: target.name}
    },
    pathway_length: length(path)
} AS theory_of_change_pathways
ORDER BY target.name, strategy.name;

// ============================================================================
// USAGE EXAMPLES AND TIPS
// ============================================================================

/*
USAGE EXAMPLES:

1. Start with Project Overview:
   Run the main PROJECT OVERVIEW query first to get familiar with the project

2. Check Data Quality:
   Run the DATA QUALITY CHECKS to identify any issues

3. Analyze Conservation Logic:
   Use CONSERVATION RELATIONSHIP ANALYSIS to understand the conservation strategy

4. Explore New Elements:
   Use NEW CONSERVATION ELEMENTS ANALYSIS to see intermediate results, objectives, etc.

5. Verify Complete Theory of Change:
   Use ENHANCED RELATIONSHIP ANALYSIS to see the full conservation logic

6. Verify Spatial Data:
   Use SPATIAL DATA INSPECTION if you plan to create visualizations

7. Performance Monitoring:
   Use PERFORMANCE AND STATISTICS for large projects

TIPS:

- Copy individual queries to Neo4j Browser for interactive exploration
- Modify LIMIT clauses to see more/fewer results
- Add WHERE clauses to filter by specific elements
- Use EXPLAIN or PROFILE keywords to analyze query performance
- Combine queries to create custom analysis reports

COMMON MODIFICATIONS:

// Filter by specific element names:
WHERE target.name CONTAINS 'Forest'

// Limit results for large datasets:
LIMIT 20

// Order by different criteria:
ORDER BY target.name ASC

// Add performance profiling:
PROFILE MATCH (n:CONSERVATION_TARGET) RETURN count(n)

NEW ELEMENT QUERIES:

// Find all intermediate results:
MATCH (ir:INTERMEDIATE_RESULT) RETURN ir.name, ir.identifier

// Find all threat reduction results:
MATCH (trr:THREAT_REDUCTION_RESULT) RETURN trr.name, trr.identifier

// Find all objectives:
MATCH (obj:OBJECTIVE) RETURN obj.name, obj.identifier

// Find all goals:
MATCH (goal:GOAL) RETURN goal.name, goal.identifier

// Find complete conservation pathways:
MATCH path = (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)
-[:CONTRIBUTES_TO]->(result)-[:ENHANCES]->(target:CONSERVATION_TARGET)
RETURN path LIMIT 10
*/
