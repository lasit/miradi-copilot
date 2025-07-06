// ============================================================================
// MIRADI SPATIAL VISUALIZATION QUERIES
// ============================================================================
// 
// Comprehensive Cypher queries for recreating Miradi-style diagrams using
// extracted spatial data. All queries leverage 100% spatial data coverage
// with actual coordinates and dimensions from Miradi XML files.
//
// Compatible with D3.js, Cytoscape.js, vis.js, and other visualization libraries
// ============================================================================

// ============================================================================
// 1. COMPLETE SPATIAL DIAGRAM EXPORT
// ============================================================================
// Export complete diagram with all spatial data, styling, and relationships
// Returns nodes and links in format suitable for web visualization frameworks

// NODES: Export all diagram factors with spatial positioning and styling
MATCH (df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element)
WHERE element.id = df.wrapped_factor_id
RETURN {
    // Node identification
    id: df.id,
    diagram_factor_id: df.id,
    element_id: df.wrapped_factor_id,
    element_type: labels(element)[0],
    
    // Spatial positioning (parsed from [x,y] format)
    x: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]),
    y: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]),
    
    // Element dimensions (parsed from [width,height] format)
    width: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]),
    height: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]),
    
    // Visual styling
    font_size: df.font_size,
    font_color: df.font_color,
    font_style: df.font_style,
    background_color: df.background_color,
    z_index: toInteger(df.z_index),
    
    // Element content
    name: element.name,
    label: element.name,
    title: element.name,
    description: element.details,
    
    // Classification for styling
    group: labels(element)[0],
    category: CASE labels(element)[0]
        WHEN 'CONSERVATION_TARGET' THEN 'target'
        WHEN 'THREAT' THEN 'threat'
        WHEN 'STRATEGY' THEN 'strategy'
        WHEN 'ACTIVITY' THEN 'activity'
        WHEN 'INDICATOR' THEN 'indicator'
        ELSE 'other'
    END
} AS nodes

UNION ALL

// LINKS: Export all diagram links with spatial routing
MATCH (dl:DIAGRAM_LINK)
OPTIONAL MATCH (from_df:DIAGRAM_FACTOR {id: dl.from_diagram_factor_id})
OPTIONAL MATCH (to_df:DIAGRAM_FACTOR {id: dl.to_diagram_factor_id})
RETURN {
    // Link identification
    id: dl.id,
    source: dl.from_diagram_factor_id,
    target: dl.to_diagram_factor_id,
    
    // Link properties
    bidirectional: dl.is_bidirectional_link = 'true',
    uncertain: dl.is_uncertain_link = 'true',
    
    // Visual styling
    color: dl.color,
    z_index: toInteger(dl.z_index),
    annotation: dl.annotation,
    
    // Spatial routing (bend points for curved connections)
    bend_points: dl.bend_points,
    
    // Source and target coordinates for routing
    source_x: toFloat(split(replace(replace(from_df.location, '[', ''), ']', ''), ', ')[0]),
    source_y: toFloat(split(replace(replace(from_df.location, '[', ''), ']', ''), ', ')[1]),
    target_x: toFloat(split(replace(replace(to_df.location, '[', ''), ']', ''), ', ')[0]),
    target_y: toFloat(split(replace(replace(to_df.location, '[', ''), ']', ''), ', ')[1])
} AS links;

// ============================================================================
// 2. RESULTS CHAIN SPATIAL VISUALIZATION
// ============================================================================
// Export specific results chains with spatial layout and conservation logic

MATCH (rc:RESULTS_CHAIN)
WHERE rc.name CONTAINS 'Result' OR rc.id = '10001' // Adjust filter as needed

// Get all diagram factors in this results chain
MATCH (rc)-[:CONTAINS]->(df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id

// Get conservation relationships between elements
OPTIONAL MATCH (source_element)-[rel:THREATENS|MITIGATES|CONTRIBUTES_TO|ENHANCES]->(target_element)
WHERE source_element.id = df.wrapped_factor_id

RETURN {
    results_chain: {
        id: rc.id,
        name: rc.name,
        description: rc.details
    },
    
    elements: collect(DISTINCT {
        id: df.id,
        element_id: df.wrapped_factor_id,
        element_type: labels(element)[0],
        name: element.name,
        
        // Spatial positioning
        x: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]),
        y: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]),
        width: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]),
        height: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]),
        
        // Conservation classification
        conservation_role: CASE labels(element)[0]
            WHEN 'CONSERVATION_TARGET' THEN 'target'
            WHEN 'THREAT' THEN 'threat'
            WHEN 'STRATEGY' THEN 'strategy'
            WHEN 'INTERMEDIATE_RESULT' THEN 'result'
            ELSE 'other'
        END
    }),
    
    conservation_relationships: collect(DISTINCT {
        source: source_element.id,
        target: target_element.id,
        relationship: type(rel),
        conservation_logic: type(rel)
    })
};

// ============================================================================
// 3. CONCEPTUAL MODEL SPATIAL VISUALIZATION
// ============================================================================
// Export conceptual models with threat-target relationships and spatial context

MATCH (cm:CONCEPTUAL_MODEL)
WHERE cm.name CONTAINS 'Conceptual' OR cm.id = '10000' // Adjust filter as needed

// Get all elements in this conceptual model
MATCH (cm)-[:CONTAINS]->(df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id

// Get threat-target relationships
OPTIONAL MATCH (threat:THREAT)-[threatens:THREATENS]->(target:CONSERVATION_TARGET)

RETURN {
    conceptual_model: {
        id: cm.id,
        name: cm.name,
        description: cm.details
    },
    
    spatial_elements: collect(DISTINCT {
        id: df.id,
        element_id: df.wrapped_factor_id,
        element_type: labels(element)[0],
        name: element.name,
        
        // Spatial positioning for threat-target layout
        x: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]),
        y: toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]),
        width: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]),
        height: toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]),
        
        // Threat-target classification
        threat_target_role: CASE 
            WHEN labels(element)[0] = 'CONSERVATION_TARGET' THEN 'target'
            WHEN labels(element)[0] = 'THREAT' THEN 'threat'
            WHEN labels(element)[0] = 'STRATEGY' THEN 'intervention'
            ELSE 'other'
        END,
        
        // Visual styling for conservation context
        color_category: CASE labels(element)[0]
            WHEN 'CONSERVATION_TARGET' THEN '#2E8B57'  // Sea green for targets
            WHEN 'THREAT' THEN '#DC143C'              // Crimson for threats
            WHEN 'STRATEGY' THEN '#4169E1'            // Royal blue for strategies
            ELSE '#808080'                            // Gray for others
        END
    }),
    
    threat_relationships: collect(DISTINCT {
        threat_id: threat.id,
        threat_name: threat.name,
        target_id: target.id,
        target_name: target.name,
        relationship_type: 'THREATENS'
    })
};

// ============================================================================
// 4. INTERACTIVE DIAGRAM BUILDER QUERY
// ============================================================================
// Structured data for building interactive conservation diagrams
// Optimized for web frameworks like React, Vue, or Angular

// Export nodes with complete metadata
MATCH (df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
WITH df, element,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y,
     toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]) as width,
     toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]) as height

RETURN {
    diagram_data: {
        nodes: collect({
            // Core identification
            id: df.id,
            elementId: df.wrapped_factor_id,
            type: labels(element)[0],
            
            // Spatial data
            position: { x: x, y: y },
            size: { width: width, height: height },
            
            // Content
            data: {
                label: element.name,
                name: element.name,
                description: element.details,
                identifier: element.identifier
            },
            
            // Styling
            style: {
                fontSize: df.font_size,
                fontColor: df.font_color,
                backgroundColor: df.background_color,
                zIndex: toInteger(df.z_index)
            },
            
            // Conservation metadata
            conservation: {
                category: labels(element)[0],
                role: CASE labels(element)[0]
                    WHEN 'CONSERVATION_TARGET' THEN 'target'
                    WHEN 'THREAT' THEN 'threat'
                    WHEN 'STRATEGY' THEN 'strategy'
                    WHEN 'ACTIVITY' THEN 'activity'
                    WHEN 'INDICATOR' THEN 'indicator'
                    ELSE 'other'
                END
            }
        })
    }
},

// Export edges with conservation relationships
{
    relationships: [
        // Conservation relationships
        {
            type: 'conservation',
            edges: [
                // THREATENS relationships
                MATCH (threat:THREAT)-[r:THREATENS]->(target:CONSERVATION_TARGET)
                RETURN collect({
                    id: 'threatens_' + threat.id + '_' + target.id,
                    source: threat.id,
                    target: target.id,
                    type: 'THREATENS',
                    conservation_logic: 'threat_impact',
                    style: { color: '#DC143C', width: 3 }
                }),
                
                // MITIGATES relationships
                MATCH (strategy:STRATEGY)-[r:MITIGATES]->(threat:THREAT)
                RETURN collect({
                    id: 'mitigates_' + strategy.id + '_' + threat.id,
                    source: strategy.id,
                    target: threat.id,
                    type: 'MITIGATES',
                    conservation_logic: 'threat_reduction',
                    style: { color: '#4169E1', width: 2 }
                })
            ]
        },
        
        // Diagram links (visual connections)
        {
            type: 'diagram',
            edges: [
                MATCH (dl:DIAGRAM_LINK)
                RETURN collect({
                    id: dl.id,
                    source: dl.from_diagram_factor_id,
                    target: dl.to_diagram_factor_id,
                    type: 'DIAGRAM_LINK',
                    bidirectional: dl.is_bidirectional_link = 'true',
                    uncertain: dl.is_uncertain_link = 'true',
                    style: {
                        color: dl.color,
                        zIndex: toInteger(dl.z_index)
                    }
                })
            ]
        }
    ]
};

// ============================================================================
// 5. SPATIAL ANALYSIS QUERIES
// ============================================================================

// 5.1 DIAGRAM BOUNDS CALCULATION
// Calculate the bounding box of all diagram elements
MATCH (df:DIAGRAM_FACTOR)
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
    element_count: count(df)
};

// 5.2 ELEMENT CLUSTERING ANALYSIS
// Analyze spatial clustering of conservation elements
MATCH (df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
WITH df, element,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y

// Group by spatial regions (100-unit grid)
WITH floor(x/100)*100 as grid_x, 
     floor(y/100)*100 as grid_y,
     collect({
         element_type: labels(element)[0],
         element_name: element.name,
         x: x, y: y
     }) as elements_in_region

RETURN {
    spatial_cluster: {
        region: { x: grid_x, y: grid_y },
        element_count: size(elements_in_region),
        element_types: [type IN extract(e IN elements_in_region | e.element_type) | type],
        elements: elements_in_region
    }
}
ORDER BY size(elements_in_region) DESC
LIMIT 10;

// 5.3 CONSERVATION ELEMENT PROXIMITY ANALYSIS
// Find conservation elements that are spatially close to each other
MATCH (df1:DIAGRAM_FACTOR), (df2:DIAGRAM_FACTOR)
WHERE df1.id < df2.id  // Avoid duplicates

OPTIONAL MATCH (e1) WHERE e1.id = df1.wrapped_factor_id
OPTIONAL MATCH (e2) WHERE e2.id = df2.wrapped_factor_id

WITH df1, df2, e1, e2,
     toFloat(split(replace(replace(df1.location, '[', ''), ']', ''), ', ')[0]) as x1,
     toFloat(split(replace(replace(df1.location, '[', ''), ']', ''), ', ')[1]) as y1,
     toFloat(split(replace(replace(df2.location, '[', ''), ']', ''), ', ')[0]) as x2,
     toFloat(split(replace(replace(df2.location, '[', ''), ']', ''), ', ')[1]) as y2

// Calculate Euclidean distance
WITH df1, df2, e1, e2, x1, y1, x2, y2,
     sqrt(power(x2-x1, 2) + power(y2-y1, 2)) as distance

WHERE distance < 200  // Elements within 200 units

RETURN {
    proximity_pair: {
        element1: {
            id: e1.id,
            name: e1.name,
            type: labels(e1)[0],
            position: {x: x1, y: y1}
        },
        element2: {
            id: e2.id,
            name: e2.name,
            type: labels(e2)[0],
            position: {x: x2, y: y2}
        },
        distance: round(distance, 2),
        conservation_relationship: CASE
            WHEN labels(e1)[0] = 'THREAT' AND labels(e2)[0] = 'CONSERVATION_TARGET' THEN 'potential_threat_target'
            WHEN labels(e1)[0] = 'STRATEGY' AND labels(e2)[0] = 'THREAT' THEN 'potential_mitigation'
            WHEN labels(e1)[0] = 'ACTIVITY' AND labels(e2)[0] = 'STRATEGY' THEN 'potential_implementation'
            ELSE 'spatial_proximity'
        END
    }
}
ORDER BY distance
LIMIT 20;

// 5.4 SPATIAL DISTRIBUTION STATISTICS
// Analyze the spatial distribution of different conservation element types
MATCH (df:DIAGRAM_FACTOR)
OPTIONAL MATCH (element) WHERE element.id = df.wrapped_factor_id
WITH df, element,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[0]) as x,
     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ', ')[1]) as y,
     toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[0]) as width,
     toFloat(split(replace(replace(df.size, '[', ''), ']', ''), ', ')[1]) as height

RETURN {
    spatial_distribution: {
        element_type: labels(element)[0],
        count: count(element),
        spatial_stats: {
            avg_x: round(avg(x), 2),
            avg_y: round(avg(y), 2),
            min_x: min(x),
            max_x: max(x),
            min_y: min(y),
            max_y: max(y),
            spread_x: max(x) - min(x),
            spread_y: max(y) - min(y)
        },
        size_stats: {
            avg_width: round(avg(width), 2),
            avg_height: round(avg(height), 2),
            min_width: min(width),
            max_width: max(width),
            min_height: min(height),
            max_height: max(height)
        }
    }
}
ORDER BY count(element) DESC;

// ============================================================================
// USAGE EXAMPLES AND INTEGRATION NOTES
// ============================================================================

/*
INTEGRATION WITH VISUALIZATION LIBRARIES:

1. D3.js Integration:
   - Use the complete spatial diagram export for force-directed layouts
   - Leverage actual coordinates for fixed positioning
   - Apply conservation-specific styling based on element types

2. Cytoscape.js Integration:
   - Convert node positions to Cytoscape format: { x: x, y: y }
   - Use conservation relationships for edge styling
   - Apply spatial clustering for layout optimization

3. vis.js Integration:
   - Map spatial data to vis.js node positions
   - Use conservation logic for edge types and colors
   - Leverage diagram bounds for viewport sizing

4. React/Vue/Angular Integration:
   - Use interactive diagram builder query for component state
   - Implement real-time spatial analysis with proximity queries
   - Build conservation-specific UI components based on element types

CONSERVATION PLANNING APPLICATIONS:

1. Threat Assessment Visualization:
   - Use conceptual model queries to show threat-target relationships
   - Apply spatial proximity analysis for threat impact assessment
   - Visualize mitigation strategies with spatial context

2. Results Chain Analysis:
   - Export results chains with conservation logic flow
   - Show strategy-result-target pathways with spatial layout
   - Analyze intervention effectiveness with spatial clustering

3. Monitoring Dashboard:
   - Integrate indicator spatial data with MEASURES relationships
   - Show monitoring coverage across conservation elements
   - Visualize data collection points with spatial context

4. Adaptive Management:
   - Use spatial analysis for strategy placement optimization
   - Analyze conservation element proximity for synergies
   - Track spatial changes over time with diagram versioning
*/
