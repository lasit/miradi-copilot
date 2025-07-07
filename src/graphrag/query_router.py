"""
Conservation Query Router

This module routes natural language queries to appropriate graph patterns and categories.
It analyzes query intent and extracts relevant parameters for conservation planning analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.graphrag.graph_patterns import QueryCategory


@dataclass
class QueryIntent:
    """Container for parsed query intent and parameters."""
    category: str
    confidence: float
    parameters: Dict[str, Any]
    keywords: List[str]
    entities: List[str]


class ConservationQueryRouter:
    """
    Routes natural language queries to appropriate conservation analysis patterns.
    
    This class analyzes conservation planning queries and determines the best
    graph patterns and parameters to use for context retrieval.
    """
    
    def __init__(self):
        """Initialize the query router with conservation domain patterns."""
        self.logger = logging.getLogger(__name__)
        
        # Conservation entity patterns
        self.entity_patterns = {
            'targets': [
                r'\b(?:target|species|habitat|ecosystem|biodiversity|wildlife|forest|marine|coastal|wetland)\b',
                r'\b(?:conservation target|key species|focal species)\b'
            ],
            'threats': [
                r'\b(?:threat|pressure|impact|damage|harm|risk|danger)\b',
                r'\b(?:pollution|poaching|deforestation|climate change|invasive species)\b',
                r'\b(?:human activity|development|agriculture|fishing|hunting)\b'
            ],
            'strategies': [
                r'\b(?:strategy|intervention|action|approach|method|solution)\b',
                r'\b(?:conservation strategy|management strategy|protection)\b',
                r'\b(?:restoration|enforcement|education|outreach)\b'
            ],
            'activities': [
                r'\b(?:activity|task|action|implementation|execution)\b',
                r'\b(?:patrol|monitoring|training|workshop|meeting)\b'
            ],
            'indicators': [
                r'\b(?:indicator|measure|metric|measurement|data|monitoring)\b',
                r'\b(?:track|assess|evaluate|monitor|measure)\b'
            ],
            'results': [
                r'\b(?:result|outcome|impact|effect|change|improvement)\b',
                r'\b(?:intermediate result|threat reduction|enhancement)\b'
            ]
        }
        
        # Query category patterns
        self.category_patterns = {
            QueryCategory.THREAT_ANALYSIS.value: [
                r'\b(?:threat|threaten|impact|affect|harm|damage|risk)\b',
                r'\b(?:what.*threat|which.*threat|threat.*to|pressure.*on)\b',
                r'\b(?:vulnerable|at risk|endangered|impacted)\b'
            ],
            QueryCategory.STRATEGY_EVALUATION.value: [
                r'\b(?:strategy|strategies|effective|implementation|approach)\b',
                r'\b(?:how.*work|which.*best|most effective|successful)\b',
                r'\b(?:mitigate|address|tackle|solve|manage)\b'
            ],
            QueryCategory.THEORY_OF_CHANGE.value: [
                r'\b(?:how.*help|pathway|chain|logic|theory|impact)\b',
                r'\b(?:lead to|result in|contribute to|cause|effect)\b',
                r'\b(?:theory of change|impact pathway|causal chain)\b'
            ],
            QueryCategory.MONITORING.value: [
                r'\b(?:monitor|track|measure|indicator|data|assessment)\b',
                r'\b(?:how.*measure|what.*track|progress|performance)\b',
                r'\b(?:monitoring|evaluation|measurement)\b'
            ],
            QueryCategory.SPATIAL_ANALYSIS.value: [
                r'\b(?:where|location|area|region|spatial|geographic)\b',
                r'\b(?:near|around|in.*area|within|distance)\b',
                r'\b(?:map|coordinate|boundary|zone)\b'
            ],
            QueryCategory.TARGET_ANALYSIS.value: [
                r'\b(?:target|species|habitat|ecosystem|viability)\b',
                r'\b(?:status.*target|health.*target|condition)\b',
                r'\b(?:conservation target|key species|focal species)\b'
            ]
        }
        
        # Spatial keywords for coordinate extraction
        self.spatial_keywords = [
            'north', 'south', 'east', 'west', 'northern', 'southern', 'eastern', 'western',
            'area', 'region', 'zone', 'location', 'near', 'around', 'within', 'distance'
        ]
    
    def route_query(self, query: str) -> QueryIntent:
        """
        Route a natural language query to appropriate conservation analysis category.
        
        Args:
            query: Natural language query string
            
        Returns:
            QueryIntent with category, confidence, and extracted parameters
        """
        query_lower = query.lower()
        
        # Extract entities and keywords
        entities = self._extract_entities(query_lower)
        keywords = self._extract_keywords(query_lower)
        
        # Determine query category
        category, confidence = self._classify_query(query_lower)
        
        # Extract parameters based on category
        parameters = self._extract_parameters(query_lower, category, entities)
        
        self.logger.info(f"Routed query to category: {category} (confidence: {confidence:.2f})")
        
        return QueryIntent(
            category=category,
            confidence=confidence,
            parameters=parameters,
            keywords=keywords,
            entities=entities
        )
    
    def _classify_query(self, query: str) -> Tuple[str, float]:
        """
        Classify query into conservation analysis category.
        
        Args:
            query: Lowercase query string
            
        Returns:
            Tuple of (category, confidence_score)
        """
        category_scores = {}
        
        # Score each category based on pattern matches
        for category, patterns in self.category_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, query):
                    matches += 1
                    # Weight based on pattern specificity
                    if len(pattern) > 20:  # More specific patterns get higher weight
                        score += 2
                    else:
                        score += 1
            
            if matches > 0:
                # Normalize score by number of patterns
                category_scores[category] = score / len(patterns)
        
        # Return highest scoring category or default to general
        if category_scores:
            best_category = max(category_scores.keys(), key=lambda k: category_scores[k])
            confidence = min(category_scores[best_category], 1.0)
            return best_category, confidence
        else:
            return "general", 0.5
    
    def _extract_entities(self, query: str) -> List[str]:
        """
        Extract conservation entities from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of identified entity types
        """
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    entities.append(entity_type)
                    break  # Only add each entity type once
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract relevant keywords from query.
        
        Args:
            query: Lowercase query string
            
        Returns:
            List of conservation-relevant keywords
        """
        # Simple keyword extraction - could be enhanced with NLP
        conservation_keywords = [
            'conservation', 'biodiversity', 'ecosystem', 'habitat', 'species',
            'threat', 'strategy', 'activity', 'indicator', 'monitoring',
            'target', 'goal', 'objective', 'result', 'impact', 'effectiveness'
        ]
        
        found_keywords = []
        words = re.findall(r'\b\w+\b', query)
        
        for word in words:
            if word in conservation_keywords:
                found_keywords.append(word)
        
        return found_keywords
    
    def _extract_parameters(self, query: str, category: str, entities: List[str]) -> Dict[str, Any]:
        """
        Extract query parameters based on category and entities.
        
        Args:
            query: Lowercase query string
            category: Determined query category
            entities: Extracted entity types
            
        Returns:
            Dictionary of query parameters
        """
        parameters = {'query': query}
        
        # Extract named entities (simplified - could use NER)
        parameters.update(self._extract_named_entities(query))
        
        # Category-specific parameter extraction
        if category == QueryCategory.SPATIAL_ANALYSIS.value:
            parameters.update(self._extract_spatial_parameters(query))
        elif category == QueryCategory.MONITORING.value:
            parameters.update(self._extract_monitoring_parameters(query))
        elif category == QueryCategory.THREAT_ANALYSIS.value:
            parameters.update(self._extract_threat_parameters(query))
        elif category == QueryCategory.STRATEGY_EVALUATION.value:
            parameters.update(self._extract_strategy_parameters(query))
        elif category == QueryCategory.TARGET_ANALYSIS.value:
            parameters.update(self._extract_target_parameters(query))
        elif category == QueryCategory.THEORY_OF_CHANGE.value:
            parameters.update(self._extract_theory_parameters(query))
        
        return parameters
    
    def _extract_named_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract named entities like specific targets, threats, strategies.
        
        Args:
            query: Lowercase query string
            
        Returns:
            Dictionary with extracted entity names
        """
        parameters = {}
        
        # Look for quoted strings (specific names)
        quoted_matches = re.findall(r'"([^"]+)"', query)
        if quoted_matches:
            parameters['entity_name'] = quoted_matches[0]
        
        # Look for capitalized words that might be proper names
        # This is simplified - real implementation would use NER
        words = query.split()
        potential_names = []
        
        for i, word in enumerate(words):
            # Look for patterns like "forest management" or "marine protection"
            if i < len(words) - 1:
                bigram = f"{word} {words[i+1]}"
                if any(keyword in bigram for keyword in ['forest', 'marine', 'coastal', 'wildlife']):
                    potential_names.append(bigram)
        
        if potential_names:
            parameters['target_name'] = potential_names[0]
        
        return parameters
    
    def _extract_spatial_parameters(self, query: str) -> Dict[str, Any]:
        """Extract spatial analysis parameters."""
        parameters = {}
        
        # Look for distance mentions
        distance_match = re.search(r'(\d+)\s*(?:km|kilometer|mile|meter)', query)
        if distance_match:
            parameters['max_distance'] = float(distance_match.group(1))
        
        # Look for area mentions
        if any(word in query for word in ['north', 'northern']):
            parameters['region'] = 'north'
        elif any(word in query for word in ['south', 'southern']):
            parameters['region'] = 'south'
        elif any(word in query for word in ['east', 'eastern']):
            parameters['region'] = 'east'
        elif any(word in query for word in ['west', 'western']):
            parameters['region'] = 'west'
        
        return parameters
    
    def _extract_monitoring_parameters(self, query: str) -> Dict[str, Any]:
        """Extract monitoring-specific parameters."""
        parameters = {}
        
        # Look for monitoring gaps
        if any(word in query for word in ['gap', 'missing', 'lack', 'without']):
            parameters['gaps'] = True
        
        # Look for specific monitoring types
        if 'water' in query:
            parameters['monitoring_type'] = 'water'
        elif 'forest' in query:
            parameters['monitoring_type'] = 'forest'
        elif 'wildlife' in query:
            parameters['monitoring_type'] = 'wildlife'
        
        return parameters
    
    def _extract_threat_parameters(self, query: str) -> Dict[str, Any]:
        """Extract threat analysis parameters."""
        parameters = {}
        
        # Look for specific threat types
        threat_types = {
            'pollution': ['pollution', 'contamination', 'waste'],
            'climate': ['climate', 'warming', 'temperature'],
            'invasive': ['invasive', 'alien', 'exotic'],
            'human': ['human', 'development', 'agriculture', 'fishing']
        }
        
        for threat_type, keywords in threat_types.items():
            if any(keyword in query for keyword in keywords):
                parameters['threat_type'] = threat_type
                break
        
        return parameters
    
    def _extract_strategy_parameters(self, query: str) -> Dict[str, Any]:
        """Extract strategy evaluation parameters."""
        parameters = {}
        
        # Look for effectiveness keywords
        if any(word in query for word in ['effective', 'successful', 'best', 'work']):
            parameters['effectiveness'] = True
        
        # Look for implementation keywords
        if any(word in query for word in ['implement', 'execution', 'carry out']):
            parameters['implementation'] = True
        
        return parameters
    
    def _extract_target_parameters(self, query: str) -> Dict[str, Any]:
        """Extract target analysis parameters."""
        parameters = {}
        
        # Look for viability keywords
        if any(word in query for word in ['viability', 'health', 'status', 'condition']):
            parameters['viability'] = True
        
        # Look for specific target types
        target_types = {
            'forest': ['forest', 'tree', 'woodland'],
            'marine': ['marine', 'ocean', 'sea', 'coastal'],
            'wildlife': ['wildlife', 'animal', 'species'],
            'habitat': ['habitat', 'ecosystem']
        }
        
        for target_type, keywords in target_types.items():
            if any(keyword in query for keyword in keywords):
                parameters['target_type'] = target_type
                break
        
        return parameters
    
    def _extract_theory_parameters(self, query: str) -> Dict[str, Any]:
        """Extract theory of change parameters."""
        parameters = {}
        
        # Look for pathway keywords
        if any(word in query for word in ['pathway', 'chain', 'logic', 'flow']):
            parameters['pathway'] = True
        
        # Look for causal keywords
        if any(word in query for word in ['cause', 'effect', 'lead to', 'result in']):
            parameters['causal'] = True
        
        return parameters
    
    def get_suggested_queries(self, category: str) -> List[str]:
        """
        Get suggested queries for a given category.
        
        Args:
            category: Query category
            
        Returns:
            List of example queries for the category
        """
        suggestions = {
            QueryCategory.THREAT_ANALYSIS.value: [
                "What threatens the coastal ecosystems?",
                "Which threats have the highest impact on marine habitats?",
                "Show me all threats to forest biodiversity",
                "What are the main pressures on wildlife populations?"
            ],
            QueryCategory.STRATEGY_EVALUATION.value: [
                "Which strategies are most effective against poaching?",
                "How well do our conservation strategies work?",
                "What activities implement the habitat restoration strategy?",
                "Which strategies address water pollution?"
            ],
            QueryCategory.THEORY_OF_CHANGE.value: [
                "How does fire management help wildlife?",
                "What is the impact pathway from education to conservation?",
                "Trace the logic from anti-poaching to elephant populations",
                "How do community strategies lead to habitat protection?"
            ],
            QueryCategory.MONITORING.value: [
                "What indicators track water quality?",
                "Which targets lack monitoring indicators?",
                "Show me all measurements for forest health",
                "What are the monitoring gaps in our project?"
            ],
            QueryCategory.SPATIAL_ANALYSIS.value: [
                "Show me threats near the forest areas",
                "What conservation targets are in the northern region?",
                "Which strategies operate within 10km of the coast?",
                "Map the spatial distribution of activities"
            ],
            QueryCategory.TARGET_ANALYSIS.value: [
                "What is the viability status of our targets?",
                "Which targets are most threatened?",
                "Show me the health of marine ecosystems",
                "What enhances our conservation targets?"
            ]
        }
        
        return suggestions.get(category, [
            "Tell me about the conservation project",
            "What are the main conservation elements?",
            "Show me the project overview"
        ])
    
    def validate_parameters(self, parameters: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Validate and clean extracted parameters.
        
        Args:
            parameters: Extracted parameters
            category: Query category
            
        Returns:
            Validated and cleaned parameters
        """
        cleaned = {}
        
        # Always include the original query
        if 'query' in parameters:
            cleaned['query'] = parameters['query']
        
        # Category-specific validation
        if category == QueryCategory.SPATIAL_ANALYSIS.value:
            if 'max_distance' in parameters:
                # Ensure distance is reasonable (0-1000 km)
                distance = parameters['max_distance']
                if 0 < distance <= 1000:
                    cleaned['max_distance'] = distance
        
        # Copy other valid parameters
        valid_keys = [
            'target_name', 'threat_name', 'strategy_name', 'activity_name',
            'element_name', 'target_id', 'threat_id', 'strategy_id',
            'effectiveness', 'implementation', 'viability', 'gaps'
        ]
        
        for key in valid_keys:
            if key in parameters and parameters[key]:
                cleaned[key] = parameters[key]
        
        return cleaned
