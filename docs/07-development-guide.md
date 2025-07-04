# Development Guide for Cline-Assisted Development

## Overview

This guide provides best practices for developing the Miradi Co-Pilot system using Cline AI assistance. It focuses on maximizing productivity while maintaining code quality, avoiding common pitfalls, and establishing clear workflows for AI-assisted development.

## Working with Cline Effectively

### Core Principles

1. **Clarity Over Brevity**: Provide detailed, specific requirements rather than vague descriptions
2. **Incremental Development**: Build features step-by-step rather than attempting large changes
3. **Context Preservation**: Maintain clear context about project structure and existing code
4. **Verification First**: Always test and review AI-generated code before proceeding

### Session Management

**Start Each Session with Context**:
```
I'm working on the Miradi Co-Pilot project. This is a conservation planning system that:
- Processes Miradi XML/JSON files into Neo4j graph database
- Uses GraphRAG for intelligent querying
- Has FastAPI backend and Streamlit frontend
- Current focus: [specific component/feature]
```

**Maintain Session Scope**:
- Define clear boundaries for what will be worked on
- Avoid mixing unrelated features in one session
- Document decisions and rationale as you go

## Component Isolation Rules

### 1. One Component Per Session

**Good Session Scope**:
- "Implement Miradi XML parser for ConservationTarget nodes"
- "Create FastAPI endpoint for threat analysis queries"
- "Build Streamlit component for file upload"

**Bad Session Scope**:
- "Build the entire ETL pipeline"
- "Create all API endpoints"
- "Implement the complete frontend"

### 2. Clear Module Boundaries

**Respect Architecture Layers**:
```
etl/          # Data processing only
├── parsers/  # File format handling
├── transformers/  # Data transformation
└── loaders/  # Database loading

api/          # API layer only
├── routes/   # Endpoint definitions
├── models/   # Pydantic schemas
└── services/ # Business logic

graph/        # Graph operations only
├── queries/  # Cypher query builders
├── models/   # Graph data models
└── utils/    # Graph utilities
```

**Session Boundaries**:
- Stay within one module per session
- Clearly define interfaces between modules
- Document dependencies and data flow

### 3. Explicit File Modification Scope

**Before Starting Development**:
```
In this session, I plan to modify:
- etl/parsers/miradi_xml.py (create new)
- etl/models/conservation_target.py (create new)
- tests/test_miradi_parser.py (create new)

I will NOT modify:
- Existing API endpoints
- Database schema
- Frontend components
```

## Prompt Patterns

### Parser Development

**Effective Prompt Structure**:
```
Create a Miradi XML parser for ConservationTarget elements with these requirements:

Context:
- Miradi files contain conservation planning data in XML format
- ConservationTarget represents species/habitats being protected
- Must extract: id, name, type, viability_rating, description

Technical Requirements:
- Use Python's xml.etree.ElementTree
- Handle missing optional fields gracefully
- Validate required fields (id, name, type)
- Return structured data matching our domain model

Input Format:
<ConservationTarget id="123">
  <Name>Amur Leopard</Name>
  <Type>Species</Type>
  <ViabilityRating>Poor</ViabilityRating>
  <Description>Critically endangered big cat</Description>
</ConservationTarget>

Expected Output:
ConservationTargetData(
  id="123",
  name="Amur Leopard",
  type="Species",
  viability_rating="Poor",
  description="Critically endangered big cat"
)

Please include error handling and unit tests.
```

### Graph Query Development

**Effective Prompt Structure**:
```
Create a Neo4j query function to find conservation targets under high threat pressure.

Context:
- Using our established graph schema (ConservationTarget, DirectThreat, AFFECTS relationship)
- Need to identify targets for priority conservation action
- Query will be used in GraphRAG context assembly

Requirements:
- Find targets with threats rated "High" or "Very High" severity
- Include threat details and relationship properties
- Return structured data for further processing
- Handle cases where targets have no threats

Expected Function Signature:
def find_threatened_targets(
    tx: neo4j.Transaction,
    severity_threshold: List[str] = ["High", "Very High"]
) -> List[ThreatenedTargetResult]

Please include:
- Cypher query with proper parameterization
- Result processing and validation
- Error handling for database issues
- Unit tests with mock data
```

### API Endpoint Development

**Effective Prompt Structure**:
```
Create a FastAPI endpoint for threat analysis queries.

Context:
- Part of our conservation analysis API
- Will be called by Streamlit frontend
- Uses Neo4j graph queries for data retrieval
- Follows our established API patterns

Requirements:
- Endpoint: GET /api/analysis/threats
- Query parameters: project_id (required), severity_filter (optional)
- Response: List of threats with target relationships
- Include proper error handling and validation

Request/Response Format:
GET /api/analysis/threats?project_id=123&severity_filter=High

Response:
{
  "threats": [
    {
      "id": "threat_1",
      "name": "Illegal Logging",
      "severity": "High",
      "affected_targets": [
        {"id": "target_1", "name": "Forest Ecosystem", "impact_scope": "Large"}
      ]
    }
  ],
  "total_count": 1
}

Please include:
- Pydantic models for request/response
- Proper HTTP status codes
- Error handling with meaningful messages
- OpenAPI documentation
- Unit tests
```

## Anti-Patterns to Avoid

### 1. Don't Ask Cline to Refactor Everything

**❌ Bad Approach**:
```
"Refactor the entire codebase to use better patterns"
"Optimize all the code for performance"
"Update everything to follow best practices"
```

**✅ Good Approach**:
```
"Refactor the ConservationTarget parser to use dataclasses instead of dictionaries"
"Optimize the threat analysis query that's currently taking 5+ seconds"
"Update the file upload endpoint to follow our established error handling pattern"
```

### 2. Avoid Vague Requirements

**❌ Bad Requirements**:
```
"Make the API better"
"Fix the performance issues"
"Add more features to the frontend"
"Improve the data processing"
```

**✅ Good Requirements**:
```
"Add input validation to the file upload API endpoint to reject files larger than 10MB"
"Optimize the graph traversal query for strategy impact analysis to return results in <2 seconds"
"Add a progress indicator to the Streamlit file processing component"
"Implement incremental loading in the ETL pipeline to handle updated Miradi files"
```

### 3. Prevent Scope Creep

**Warning Signs**:
- Session objectives keep expanding
- "While we're at it, let's also..." requests
- Mixing bug fixes with new features
- Adding requirements mid-development

**Mitigation Strategies**:
- Write down session objectives at the start
- Create a "parking lot" for new ideas
- Finish current scope before expanding
- Document decisions and trade-offs

### 4. Avoid Context Loss

**❌ Context-Losing Patterns**:
```
"Add error handling" (to what?)
"Make it more efficient" (which part?)
"Follow the same pattern" (which pattern?)
```

**✅ Context-Preserving Patterns**:
```
"Add error handling to the Miradi XML parser for malformed XML files"
"Optimize the Neo4j query in find_threatened_targets() that currently scans all nodes"
"Follow the same validation pattern used in the ConservationTarget model for the new DirectThreat model"
```

## Testing Strategy with Cline

### Test-Driven Development with AI

**1. Define Tests First**:
```
Before implementing the Miradi parser, create comprehensive tests that define:
- Valid XML parsing scenarios
- Error handling for malformed XML
- Edge cases (missing fields, empty values)
- Performance requirements (parse 1000 targets in <5 seconds)
```

**2. Implement with Tests**:
```
Now implement the Miradi parser to pass these tests:
[paste test code]

Ensure the implementation:
- Passes all existing tests
- Handles the edge cases defined
- Meets performance requirements
- Follows our established patterns
```

### Maintaining Test Coverage

**Coverage Requirements**:
- All new functions must have unit tests
- API endpoints must have integration tests
- Critical paths must have end-to-end tests
- Error conditions must be tested

**Testing Checklist for AI-Generated Code**:
- [ ] Unit tests cover happy path scenarios
- [ ] Error conditions are tested
- [ ] Edge cases are handled
- [ ] Integration points are tested
- [ ] Performance requirements are verified
- [ ] Tests are maintainable and readable

### Test Organization

```
tests/
├── unit/
│   ├── test_parsers.py      # ETL component tests
│   ├── test_graph_queries.py # Graph operation tests
│   └── test_api_models.py   # API model tests
├── integration/
│   ├── test_api_endpoints.py # API integration tests
│   └── test_etl_pipeline.py  # ETL integration tests
└── e2e/
    └── test_user_workflows.py # End-to-end scenarios
```

## Code Review Checklist

### Pre-Review Verification

**Before Requesting Review**:
- [ ] All tests pass locally
- [ ] Code follows project style guidelines
- [ ] Documentation is updated
- [ ] No debugging code or comments left
- [ ] Error handling is appropriate

### AI-Generated Code Review Points

**1. Logic Verification**:
- [ ] Algorithm correctness
- [ ] Edge case handling
- [ ] Error condition management
- [ ] Performance implications

**2. Integration Concerns**:
- [ ] Follows established patterns
- [ ] Compatible with existing interfaces
- [ ] Proper dependency management
- [ ] Configuration handling

**3. Security Considerations**:
- [ ] Input validation and sanitization
- [ ] SQL injection prevention (Cypher injection)
- [ ] Authentication/authorization checks
- [ ] Sensitive data handling

**4. Maintainability**:
- [ ] Code is readable and well-commented
- [ ] Functions have single responsibilities
- [ ] Naming conventions are consistent
- [ ] Documentation is accurate

### Common AI Code Issues

**Watch Out For**:
- Overly complex solutions to simple problems
- Missing error handling for external dependencies
- Hardcoded values that should be configurable
- Inefficient algorithms or data structures
- Missing logging for debugging
- Incomplete type hints

**Verification Steps**:
1. Run the code with various inputs
2. Test error conditions manually
3. Check performance with realistic data volumes
4. Verify integration with existing components
5. Review for security vulnerabilities

## Effective Collaboration Patterns

### Session Planning

**Start of Session Checklist**:
- [ ] Review previous session outcomes
- [ ] Define current session objectives
- [ ] Identify files that will be modified
- [ ] Set success criteria
- [ ] Note any constraints or dependencies

**End of Session Checklist**:
- [ ] All tests pass
- [ ] Code is committed with clear messages
- [ ] Documentation is updated
- [ ] Next steps are documented
- [ ] Any issues are logged

### Communication Patterns

**Effective Feedback**:
```
The ConservationTarget parser works well for basic cases, but I found these issues:

1. Performance: Takes 30 seconds for large files (>1000 targets)
   - Expected: <5 seconds
   - Suggestion: Use iterative parsing instead of loading entire XML

2. Error Handling: Crashes on malformed XML
   - Expected: Graceful error with specific message
   - Test case: [provide specific XML that fails]

3. Validation: Accepts empty name fields
   - Expected: Validation error for required fields
   - Business rule: name and id are mandatory

Please address these issues while maintaining the current API interface.
```

**Progress Updates**:
```
Session Progress Update:

Completed:
✅ Miradi XML parser for ConservationTarget
✅ Unit tests with 95% coverage
✅ Integration with ETL pipeline

In Progress:
🔄 DirectThreat parser (80% complete)
🔄 Relationship extraction logic

Next Steps:
📋 ContributingFactor parser
📋 End-to-end ETL testing
📋 Performance optimization

Blockers:
❌ Need clarification on Miradi relationship format
❌ Waiting for sample files with complex structures
```

## Project-Specific Guidelines

### Miradi Co-Pilot Conventions

**File Naming**:
- Parsers: `miradi_{element_type}_parser.py`
- Models: `{domain_concept}_model.py`
- Queries: `{analysis_type}_queries.py`
- Tests: `test_{component_name}.py`

**Code Organization**:
- Keep domain logic separate from infrastructure
- Use dependency injection for external services
- Follow the established error handling patterns
- Maintain consistent logging throughout

**Documentation Requirements**:
- All public functions must have docstrings
- Complex algorithms need inline comments
- API endpoints need OpenAPI documentation
- Database queries need performance notes

### Quality Gates

**Before Merging Code**:
- [ ] All tests pass (unit, integration, e2e)
- [ ] Code coverage meets minimum threshold (80%)
- [ ] Performance benchmarks are met
- [ ] Security scan passes
- [ ] Documentation is complete
- [ ] Code review is approved

This guide ensures that AI-assisted development maintains high quality standards while maximizing productivity and avoiding common pitfalls in complex conservation software development.
