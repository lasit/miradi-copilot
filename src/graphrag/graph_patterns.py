"""
Graph Patterns for Conservation Queries

This module defines Cypher query patterns for common conservation planning questions.
Each pattern is designed to extract relevant subgraphs from the Miradi conservation database.
"""

from typing import Dict, List, Any
from enum import Enum


class QueryCategory(Enum):
    """Categories of conservation queries supported by the system."""
    THREAT_ANALYSIS = "threat_analysis"
    STRATEGY_EVALUATION = "strategy_evaluation"
    SPATIAL_ANALYSIS = "spatial_analysis"
    MONITORING = "monitoring"
    THEORY_OF_CHANGE = "theory_of_change"
    TARGET_ANALYSIS = "target_analysis"
    RELATIONSHIP_TRACING = "relationship_tracing"


class ConservationGraphPatterns:
    """
    Predefined Cypher query patterns for conservation planning analysis.
    
    Each pattern is designed to extract specific types of conservation relationships
    and can be parameterized based on user queries.
    """
    
    @staticmethod
    def get_threat_analysis_patterns() -> Dict[str, str]:
        """Patterns for analyzing threats to conservation targets."""
        return {
            "threats_to_target": """
                MATCH (threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
                WHERE target.name CONTAINS $target_name OR target.id = $target_id
                RETURN threat, target, 
                       threat.name as threat_name,
                       target.name as target_name,
                       'THREATENS' as relationship_type
            """,
            
            "all_threats_to_targets": """
                MATCH (threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
                RETURN threat, target,
                       threat.name as threat_name,
                       target.name as target_name,
                       'THREATENS' as relationship_type
                ORDER BY target.name, threat.name
            """,
            
            "threat_impact_chain": """
                MATCH (threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
                OPTIONAL MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat)
                OPTIONAL MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy)
                WHERE threat.name CONTAINS $threat_name OR threat.id = $threat_id
                RETURN threat, target, strategy, activity,
                       threat.name as threat_name,
                       target.name as target_name,
                       strategy.name as strategy_name,
                       activity.name as activity_name
            """,
            
            "threats_by_severity": """
                MATCH (threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
                RETURN threat, target, count(target) as targets_affected,
                       threat.name as threat_name,
                       threat.severity as severity,
                       threat.scope as scope
                ORDER BY targets_affected DESC, threat.severity DESC
            """
        }
    
    @staticmethod
    def get_strategy_evaluation_patterns() -> Dict[str, str]:
        """Patterns for evaluating conservation strategies."""
        return {
            "strategy_effectiveness": """
                MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:THREAT)-[:THREATENS]->(target:CONSERVATION_TARGET)
                WHERE strategy.name CONTAINS $strategy_name OR strategy.id = $strategy_id
                RETURN strategy, threat, target,
                       strategy.name as strategy_name,
                       threat.name as threat_name,
                       target.name as target_name,
                       strategy.status as strategy_status
            """,
            
            "strategy_implementation": """
                MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)
                OPTIONAL MATCH (strategy)-[:MITIGATES]->(threat:THREAT)
                OPTIONAL MATCH (strategy)-[:CONTRIBUTES_TO]->(result)
                WHERE strategy.name CONTAINS $strategy_name OR strategy.id = $strategy_id
                RETURN strategy, activity, threat, result,
                       strategy.name as strategy_name,
                       activity.name as activity_name,
                       threat.name as threat_name,
                       result.name as result_name
            """,
            
            "strategies_by_threat": """
                MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat:THREAT)
                WHERE threat.name CONTAINS $threat_name OR threat.id = $threat_id
                RETURN strategy, threat,
                       strategy.name as strategy_name,
                       strategy.status as strategy_status,
                       threat.name as threat_name
                ORDER BY strategy.status, strategy.name
            """,
            
            "strategy_portfolio": """
                MATCH (strategy:STRATEGY)
                OPTIONAL MATCH (strategy)-[:MITIGATES]->(threat:THREAT)
                OPTIONAL MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy)
                OPTIONAL MATCH (strategy)-[:CONTRIBUTES_TO]->(result)
                RETURN strategy, collect(DISTINCT threat.name) as threats_mitigated,
                       collect(DISTINCT activity.name) as activities,
                       collect(DISTINCT result.name) as results,
                       strategy.name as strategy_name,
                       strategy.status as strategy_status
                ORDER BY strategy.name
            """
        }
    
    @staticmethod
    def get_theory_of_change_patterns() -> Dict[str, str]:
        """Patterns for tracing theory of change pathways."""
        return {
            "full_theory_chain": """
                MATCH path = (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy:STRATEGY)
                             -[:CONTRIBUTES_TO]->(result)
                             -[:ENHANCES]->(target:CONSERVATION_TARGET)
                WHERE activity.name CONTAINS $activity_name OR strategy.name CONTAINS $strategy_name
                RETURN path, nodes(path) as chain_elements,
                       activity.name as activity_name,
                       strategy.name as strategy_name,
                       result.name as result_name,
                       target.name as target_name
            """,
            
            "strategy_to_results": """
                MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result)
                OPTIONAL MATCH (result)-[:ENHANCES]->(target:CONSERVATION_TARGET)
                WHERE strategy.name CONTAINS $strategy_name OR strategy.id = $strategy_id
                RETURN strategy, result, target,
                       strategy.name as strategy_name,
                       result.name as result_name,
                       target.name as target_name,
                       labels(result)[0] as result_type
            """,
            
            "results_chain_analysis": """
                MATCH (rc:RESULTS_CHAIN)-[:CONTAINS]->(df:DIAGRAM_FACTOR)
                MATCH (element) WHERE element.id = df.wrapped_factor_id
                WITH rc, collect(DISTINCT element.id) as chain_element_ids, 
                     collect(DISTINCT element) as chain_elements
                MATCH (element1)-[rel:IMPLEMENTS|CONTRIBUTES_TO|ENHANCES|MITIGATES]-(element2)
                WHERE element1.id IN chain_element_ids AND element2.id IN chain_element_ids
                RETURN element1, rel, element2, rc.name as results_chain_name,
                       element1.name as source_name,
                       element2.name as target_name,
                       type(rel) as relationship_type
            """,
            
            "impact_pathway": """
                MATCH path = (start)-[:IMPLEMENTS|CONTRIBUTES_TO|ENHANCES*1..4]->(end:CONSERVATION_TARGET)
                WHERE start.name CONTAINS $start_element OR start.id = $start_id
                RETURN path, length(path) as pathway_length,
                       start.name as start_name,
                       end.name as target_name,
                       [n in nodes(path) | n.name] as pathway_names
                ORDER BY pathway_length
            """
        }
    
    @staticmethod
    def get_monitoring_patterns() -> Dict[str, str]:
        """Patterns for monitoring and indicator analysis."""
        return {
            "indicators_for_element": """
                MATCH (indicator:INDICATOR)-[:MEASURES]->(element)
                WHERE element.name CONTAINS $element_name OR element.id = $element_id
                RETURN indicator, element,
                       indicator.name as indicator_name,
                       element.name as element_name,
                       labels(element)[0] as element_type,
                       indicator.details as indicator_details
            """,
            
            "monitoring_framework": """
                MATCH (indicator:INDICATOR)-[:MEASURES]->(element)
                OPTIONAL MATCH (objective:OBJECTIVE)-[:DEFINES]->(element)
                RETURN element, indicator, objective,
                       element.name as element_name,
                       labels(element)[0] as element_type,
                       indicator.name as indicator_name,
                       objective.name as objective_name
                ORDER BY element_type, element.name
            """,
            
            "target_monitoring": """
                MATCH (target:CONSERVATION_TARGET)
                OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(target)
                OPTIONAL MATCH (target)-[:HAS_ATTRIBUTE]->(kea:KEY_ECOLOGICAL_ATTRIBUTE)
                OPTIONAL MATCH (kea_indicator:INDICATOR)-[:MEASURES]->(kea)
                RETURN target, indicator, kea, kea_indicator,
                       target.name as target_name,
                       indicator.name as direct_indicator,
                       kea.name as key_attribute,
                       kea_indicator.name as attribute_indicator
            """,
            
            "monitoring_gaps": """
                MATCH (element)
                WHERE element:CONSERVATION_TARGET OR element:STRATEGY OR element:THREAT
                OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(element)
                WITH element, collect(indicator) as indicators
                WHERE size(indicators) = 0
                RETURN element, labels(element)[0] as element_type,
                       element.name as element_name,
                       'No monitoring indicators' as gap_type
            """
        }
    
    @staticmethod
    def get_spatial_analysis_patterns() -> Dict[str, str]:
        """Patterns for spatial analysis of conservation elements."""
        return {
            "elements_in_area": """
                MATCH (element)-[:PART_OF]->(df:DIAGRAM_FACTOR)
                WHERE df.location IS NOT NULL
                WITH element, df, 
                     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ',')[0]) as x,
                     toFloat(split(replace(replace(df.location, '[', ''), ']', ''), ',')[1]) as y
                WHERE x >= $min_x AND x <= $max_x AND y >= $min_y AND y <= $max_y
                RETURN element, df, x, y,
                       element.name as element_name,
                       labels(element)[0] as element_type
            """,
            
            "spatial_relationships": """
                MATCH (element1)-[:PART_OF]->(df1:DIAGRAM_FACTOR),
                      (element2)-[:PART_OF]->(df2:DIAGRAM_FACTOR)
                WHERE df1.location IS NOT NULL AND df2.location IS NOT NULL
                WITH element1, element2, df1, df2,
                     toFloat(split(replace(replace(df1.location, '[', ''), ']', ''), ',')[0]) as x1,
                     toFloat(split(replace(replace(df1.location, '[', ''), ']', ''), ',')[1]) as y1,
                     toFloat(split(replace(replace(df2.location, '[', ''), ']', ''), ',')[0]) as x2,
                     toFloat(split(replace(replace(df2.location, '[', ''), ']', ''), ',')[1]) as y2
                WITH element1, element2, sqrt((x2-x1)^2 + (y2-y1)^2) as distance
                WHERE distance <= $max_distance
                RETURN element1, element2, distance,
                       element1.name as element1_name,
                       element2.name as element2_name,
                       labels(element1)[0] as element1_type,
                       labels(element2)[0] as element2_type
                ORDER BY distance
            """,
            
            "diagram_overview": """
                MATCH (model)-[:CONTAINS]->(df:DIAGRAM_FACTOR)
                MATCH (element) WHERE element.id = df.wrapped_factor_id
                WHERE model:CONCEPTUAL_MODEL OR model:RESULTS_CHAIN
                RETURN model, df, element,
                       model.name as model_name,
                       labels(model)[0] as model_type,
                       element.name as element_name,
                       labels(element)[0] as element_type,
                       df.location as coordinates,
                       df.size as dimensions
            """
        }
    
    @staticmethod
    def get_target_analysis_patterns() -> Dict[str, str]:
        """Patterns for analyzing conservation targets."""
        return {
            "target_viability": """
                MATCH (target:CONSERVATION_TARGET)
                OPTIONAL MATCH (target)-[:HAS_ATTRIBUTE]->(kea:KEY_ECOLOGICAL_ATTRIBUTE)
                OPTIONAL MATCH (indicator:INDICATOR)-[:MEASURES]->(target)
                OPTIONAL MATCH (kea_indicator:INDICATOR)-[:MEASURES]->(kea)
                WHERE target.name CONTAINS $target_name OR target.id = $target_id
                RETURN target, kea, indicator, kea_indicator,
                       target.name as target_name,
                       target.viability_rating as viability,
                       kea.name as key_attribute,
                       indicator.name as target_indicator,
                       kea_indicator.name as attribute_indicator
            """,
            
            "target_threat_pressure": """
                MATCH (target:CONSERVATION_TARGET)<-[:THREATENS]-(threat:THREAT)
                OPTIONAL MATCH (strategy:STRATEGY)-[:MITIGATES]->(threat)
                WHERE target.name CONTAINS $target_name OR target.id = $target_id
                RETURN target, threat, strategy,
                       target.name as target_name,
                       threat.name as threat_name,
                       threat.severity as threat_severity,
                       strategy.name as mitigation_strategy
                ORDER BY threat.severity DESC
            """,
            
            "target_enhancement": """
                MATCH (target:CONSERVATION_TARGET)<-[:ENHANCES]-(result)
                OPTIONAL MATCH (strategy:STRATEGY)-[:CONTRIBUTES_TO]->(result)
                OPTIONAL MATCH (activity:ACTIVITY)-[:IMPLEMENTS]->(strategy)
                WHERE target.name CONTAINS $target_name OR target.id = $target_id
                RETURN target, result, strategy, activity,
                       target.name as target_name,
                       result.name as result_name,
                       labels(result)[0] as result_type,
                       strategy.name as strategy_name,
                       activity.name as activity_name
            """
        }
    
    @staticmethod
    def get_all_patterns() -> Dict[str, Dict[str, str]]:
        """Get all available query patterns organized by category."""
        return {
            QueryCategory.THREAT_ANALYSIS.value: ConservationGraphPatterns.get_threat_analysis_patterns(),
            QueryCategory.STRATEGY_EVALUATION.value: ConservationGraphPatterns.get_strategy_evaluation_patterns(),
            QueryCategory.THEORY_OF_CHANGE.value: ConservationGraphPatterns.get_theory_of_change_patterns(),
            QueryCategory.MONITORING.value: ConservationGraphPatterns.get_monitoring_patterns(),
            QueryCategory.SPATIAL_ANALYSIS.value: ConservationGraphPatterns.get_spatial_analysis_patterns(),
            QueryCategory.TARGET_ANALYSIS.value: ConservationGraphPatterns.get_target_analysis_patterns()
        }
    
    @staticmethod
    def get_pattern_by_name(category: str, pattern_name: str) -> str:
        """Get a specific pattern by category and name."""
        all_patterns = ConservationGraphPatterns.get_all_patterns()
        if category in all_patterns and pattern_name in all_patterns[category]:
            return all_patterns[category][pattern_name]
        raise ValueError(f"Pattern '{pattern_name}' not found in category '{category}'")
