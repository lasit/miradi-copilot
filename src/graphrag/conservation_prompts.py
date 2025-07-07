"""
Conservation Domain Prompt Templates

This module provides specialized prompt templates for conservation planning queries.
Each template is designed to help language models understand conservation concepts
and generate accurate responses based on graph data.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A prompt template with system and user message components."""
    system_prompt: str
    user_template: str
    context_template: str
    response_format: str


class ConservationPromptTemplates:
    """
    Domain-specific prompt templates for conservation planning analysis.
    
    These templates help language models understand conservation terminology,
    relationships, and provide accurate responses based on graph data.
    """
    
    @staticmethod
    def get_base_conservation_context() -> str:
        """Base context about conservation planning concepts."""
        return """
You are a conservation planning expert assistant analyzing data from Miradi conservation projects.

CONSERVATION PLANNING CONCEPTS:
- Conservation Targets: Species, habitats, or ecosystems being protected
- Direct Threats: Human activities directly harming conservation targets
- Strategies: Conservation interventions designed to mitigate threats
- Activities: Specific actions that implement strategies
- Results: Expected outcomes from strategies (Intermediate Results, Threat Reduction Results)
- Indicators: Measurable variables for monitoring progress
- Objectives: Specific, measurable goals
- Theory of Change: Logical pathway from activities → strategies → results → target outcomes

RELATIONSHIP TYPES:
- THREATENS: Direct threats impact conservation targets
- MITIGATES: Strategies reduce or address threats
- IMPLEMENTS: Activities execute strategies
- CONTRIBUTES_TO: Strategies produce results; results lead to other results
- ENHANCES: Results improve conservation target status
- MEASURES: Indicators monitor elements; elements measure indicators
- DEFINES: Objectives define goals for elements
- HAS_ATTRIBUTE: Targets have key ecological attributes
- EXPERIENCES: Targets experience stresses

Always provide specific, actionable insights based on the conservation data provided.
"""
    
    @staticmethod
    def get_threat_analysis_template() -> PromptTemplate:
        """Template for threat analysis queries."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

THREAT ANALYSIS EXPERTISE:
You specialize in analyzing threats to conservation targets. Focus on:
- Identifying direct threats and their impacts
- Assessing threat severity and scope
- Analyzing threat-target relationships
- Evaluating mitigation strategies
- Identifying gaps in threat management

Provide clear, actionable threat assessments with specific recommendations.
""",
            user_template="""
Analyze the following conservation threat data and answer this question: {query}

Consider:
- Which threats pose the greatest risk?
- What targets are most vulnerable?
- Are there effective mitigation strategies in place?
- What are the gaps in threat management?
""",
            context_template="""
CONSERVATION THREAT DATA:
{graph_context}

THREAT RELATIONSHIPS:
{relationships}

SPATIAL CONTEXT:
{spatial_info}
""",
            response_format="""
Provide your threat analysis in this format:
1. **Key Threats Identified**: List the main threats with severity levels
2. **Targets at Risk**: Identify which conservation targets are most threatened
3. **Current Mitigation**: Describe existing strategies addressing these threats
4. **Risk Assessment**: Evaluate overall threat pressure and urgency
5. **Recommendations**: Suggest specific actions to address threat gaps
"""
        )
    
    @staticmethod
    def get_strategy_evaluation_template() -> PromptTemplate:
        """Template for strategy evaluation queries."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

STRATEGY EVALUATION EXPERTISE:
You specialize in evaluating conservation strategies. Focus on:
- Assessing strategy effectiveness and implementation
- Analyzing strategy-threat-target relationships
- Evaluating activity implementation
- Identifying strategy gaps and overlaps
- Recommending strategy improvements

Provide evidence-based strategy assessments with clear recommendations.
""",
            user_template="""
Evaluate the following conservation strategy data and answer this question: {query}

Consider:
- How effective are current strategies?
- Which threats are well-addressed vs. under-addressed?
- Are strategies being properly implemented through activities?
- What are the strategy portfolio gaps?
""",
            context_template="""
CONSERVATION STRATEGY DATA:
{graph_context}

STRATEGY IMPLEMENTATION:
{implementation_data}

THREAT MITIGATION:
{mitigation_relationships}
""",
            response_format="""
Provide your strategy evaluation in this format:
1. **Strategy Portfolio Overview**: Summarize the current strategies
2. **Effectiveness Assessment**: Evaluate how well strategies address threats
3. **Implementation Status**: Assess activity implementation of strategies
4. **Coverage Analysis**: Identify well-covered vs. under-addressed threats
5. **Recommendations**: Suggest strategy improvements or additions
"""
        )
    
    @staticmethod
    def get_theory_of_change_template() -> PromptTemplate:
        """Template for theory of change analysis."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

THEORY OF CHANGE EXPERTISE:
You specialize in analyzing conservation theory of change pathways. Focus on:
- Tracing logical pathways from activities to target outcomes
- Identifying complete vs. incomplete impact chains
- Analyzing results chain logic
- Evaluating pathway assumptions
- Identifying missing links in the theory of change

Provide clear pathway analysis with logical flow assessment.
""",
            user_template="""
Analyze the following theory of change data and answer this question: {query}

Consider:
- Are there complete pathways from activities to target outcomes?
- What are the key assumptions in the impact chains?
- Are there missing links or logical gaps?
- How strong is the evidence for the theory of change?
""",
            context_template="""
THEORY OF CHANGE DATA:
{graph_context}

IMPACT PATHWAYS:
{pathway_data}

RESULTS CHAINS:
{results_chain_info}
""",
            response_format="""
Provide your theory of change analysis in this format:
1. **Impact Pathways**: Describe the main pathways from activities to outcomes
2. **Logical Flow**: Assess the strength of the causal logic
3. **Completeness**: Identify complete vs. incomplete chains
4. **Key Assumptions**: Highlight critical assumptions in the pathways
5. **Recommendations**: Suggest improvements to strengthen the theory of change
"""
        )
    
    @staticmethod
    def get_monitoring_template() -> PromptTemplate:
        """Template for monitoring and indicator analysis."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

MONITORING EXPERTISE:
You specialize in conservation monitoring and evaluation. Focus on:
- Analyzing indicator coverage and quality
- Identifying monitoring gaps
- Evaluating measurement frameworks
- Assessing data collection feasibility
- Recommending monitoring improvements

Provide practical monitoring assessments with specific recommendations.
""",
            user_template="""
Analyze the following monitoring data and answer this question: {query}

Consider:
- What elements have good indicator coverage?
- Where are the monitoring gaps?
- Are indicators appropriate and measurable?
- Is the monitoring framework comprehensive?
""",
            context_template="""
MONITORING DATA:
{graph_context}

INDICATOR COVERAGE:
{indicator_data}

MEASUREMENT RELATIONSHIPS:
{measurement_info}
""",
            response_format="""
Provide your monitoring analysis in this format:
1. **Current Coverage**: Describe what is currently being monitored
2. **Monitoring Gaps**: Identify elements lacking indicators
3. **Indicator Quality**: Assess the appropriateness of existing indicators
4. **Framework Assessment**: Evaluate the overall monitoring framework
5. **Recommendations**: Suggest specific monitoring improvements
"""
        )
    
    @staticmethod
    def get_spatial_analysis_template() -> PromptTemplate:
        """Template for spatial analysis queries."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

SPATIAL ANALYSIS EXPERTISE:
You specialize in spatial aspects of conservation planning. Focus on:
- Analyzing spatial relationships between conservation elements
- Identifying geographic patterns and clusters
- Evaluating spatial coverage and gaps
- Assessing landscape-level conservation logic
- Recommending spatial improvements

Provide spatially-informed conservation analysis with geographic insights.
""",
            user_template="""
Analyze the following spatial conservation data and answer this question: {query}

Consider:
- What are the spatial patterns in the data?
- Are there geographic clusters or gaps?
- How do spatial relationships affect conservation logic?
- What are the landscape-level implications?
""",
            context_template="""
SPATIAL CONSERVATION DATA:
{graph_context}

GEOGRAPHIC RELATIONSHIPS:
{spatial_relationships}

LOCATION DATA:
{coordinate_info}
""",
            response_format="""
Provide your spatial analysis in this format:
1. **Spatial Patterns**: Describe key geographic patterns in the data
2. **Geographic Relationships**: Analyze spatial connections between elements
3. **Coverage Assessment**: Evaluate spatial coverage and identify gaps
4. **Landscape Context**: Discuss landscape-level conservation implications
5. **Recommendations**: Suggest spatial improvements or considerations
"""
        )
    
    @staticmethod
    def get_target_analysis_template() -> PromptTemplate:
        """Template for conservation target analysis."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

TARGET ANALYSIS EXPERTISE:
You specialize in conservation target analysis. Focus on:
- Assessing target viability and health
- Analyzing threat pressure on targets
- Evaluating target enhancement strategies
- Assessing monitoring coverage for targets
- Identifying target management priorities

Provide comprehensive target assessments with conservation priorities.
""",
            user_template="""
Analyze the following conservation target data and answer this question: {query}

Consider:
- What is the current status and viability of targets?
- What threats are impacting each target?
- Are there effective enhancement strategies?
- Is monitoring adequate for target assessment?
""",
            context_template="""
CONSERVATION TARGET DATA:
{graph_context}

TARGET VIABILITY:
{viability_data}

THREAT PRESSURE:
{threat_relationships}

ENHANCEMENT STRATEGIES:
{enhancement_info}
""",
            response_format="""
Provide your target analysis in this format:
1. **Target Status**: Summarize current target viability and health
2. **Threat Assessment**: Analyze threats impacting each target
3. **Enhancement Evaluation**: Assess strategies enhancing targets
4. **Monitoring Coverage**: Evaluate target monitoring adequacy
5. **Priorities**: Recommend target management priorities
"""
        )
    
    @staticmethod
    def get_general_query_template() -> PromptTemplate:
        """Template for general conservation queries."""
        return PromptTemplate(
            system_prompt=ConservationPromptTemplates.get_base_conservation_context() + """

GENERAL CONSERVATION EXPERTISE:
You provide comprehensive conservation planning analysis. Focus on:
- Understanding the full conservation context
- Analyzing relationships between all elements
- Providing holistic conservation insights
- Identifying system-wide patterns and gaps
- Recommending integrated conservation approaches

Provide comprehensive, well-reasoned conservation analysis.
""",
            user_template="""
Analyze the following conservation data and answer this question: {query}

Provide a comprehensive analysis considering all relevant conservation planning aspects.
""",
            context_template="""
CONSERVATION PROJECT DATA:
{graph_context}

RELATIONSHIPS:
{relationship_data}

ADDITIONAL CONTEXT:
{supplementary_info}
""",
            response_format="""
Provide your conservation analysis in this format:
1. **Overview**: Summarize the key conservation elements and relationships
2. **Analysis**: Provide detailed analysis relevant to the question
3. **Insights**: Highlight important patterns, gaps, or opportunities
4. **Context**: Explain the broader conservation implications
5. **Recommendations**: Suggest specific, actionable next steps
"""
        )
    
    @staticmethod
    def get_template_by_category(category: str) -> PromptTemplate:
        """Get prompt template by query category."""
        templates = {
            "threat_analysis": ConservationPromptTemplates.get_threat_analysis_template(),
            "strategy_evaluation": ConservationPromptTemplates.get_strategy_evaluation_template(),
            "theory_of_change": ConservationPromptTemplates.get_theory_of_change_template(),
            "monitoring": ConservationPromptTemplates.get_monitoring_template(),
            "spatial_analysis": ConservationPromptTemplates.get_spatial_analysis_template(),
            "target_analysis": ConservationPromptTemplates.get_target_analysis_template(),
            "general": ConservationPromptTemplates.get_general_query_template()
        }
        
        return templates.get(category, ConservationPromptTemplates.get_general_query_template())
    
    @staticmethod
    def format_graph_context(graph_data: List[Dict[str, Any]]) -> str:
        """Format graph query results into readable context."""
        if not graph_data:
            return "No relevant data found in the conservation database."
        
        context_parts = []
        
        # Group data by type
        nodes_by_type = {}
        relationships = []
        
        for record in graph_data:
            for key, value in record.items():
                if isinstance(value, dict) and 'name' in value:
                    # This is likely a node
                    node_type = value.get('node_type', 'Unknown')
                    if node_type not in nodes_by_type:
                        nodes_by_type[node_type] = []
                    nodes_by_type[node_type].append(value)
                elif key.endswith('_name') or key.endswith('_type'):
                    # This is relationship data
                    relationships.append(f"{key}: {value}")
        
        # Format nodes by type
        for node_type, nodes in nodes_by_type.items():
            context_parts.append(f"\n{node_type.upper()}S:")
            for node in nodes:
                name = node.get('name', 'Unnamed')
                details = node.get('details', '')
                if details:
                    context_parts.append(f"- {name}: {details}")
                else:
                    context_parts.append(f"- {name}")
        
        # Add relationships if any
        if relationships:
            context_parts.append("\nRELATIONSHIPS:")
            for rel in relationships[:10]:  # Limit to first 10 relationships
                context_parts.append(f"- {rel}")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def create_full_prompt(template: PromptTemplate, query: str, graph_context: str, 
                          additional_context: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Create a complete prompt with system and user messages."""
        if additional_context is None:
            additional_context = {}
        
        # Format context template
        context = template.context_template.format(
            graph_context=graph_context,
            **additional_context
        )
        
        # Format user message
        user_message = template.user_template.format(query=query) + "\n\n" + context
        
        # Add response format
        user_message += "\n\n" + template.response_format
        
        return {
            "system": template.system_prompt,
            "user": user_message
        }
