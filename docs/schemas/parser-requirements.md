# Miradi Parser Requirements

**Generated:** 2025-07-05 06:32:48  
**Based on analysis of:** 11 Miradi projects (689 unique elements, 619,358 total instances)

This document defines the requirements for implementing Miradi XML parsers based on empirical analysis of real-world conservation projects. Elements are categorized by frequency to guide implementation priorities.

## Executive Summary

| Category | Element Count | Coverage | Implementation Priority |
|----------|---------------|----------|------------------------|
| **Must-Support** | 173 | 100% of projects | **Priority 1** - Essential |
| **Should-Support** | 65 | 75%+ of projects | **Priority 2** - High value |
| **Optional** | 267 | 25-74% of projects | **Priority 3** - Conditional |
| **Edge Cases** | 184 | <25% of projects | **Priority 4** - Special handling |

## Must-Support Elements (100% Coverage)

These **173 elements** appear in ALL analyzed projects and represent the essential Miradi schema. Any parser implementation MUST support these elements for basic functionality.

### Core Project Structure
```xml
<!-- Root and project metadata -->
ConservationProject
ProjectSummary
ProjectSummaryProjectId
ProjectSummaryProjectName
ProjectSummaryFactorMode
ProjectSummaryTargetMode
ProjectSummaryThreatRatingMode
ProjectSummaryWorkPlanTimeUnit
ProjectSummaryShareOutsideOrganization
ProjectSummaryExtendedProgressReportIds

<!-- Project planning and scope -->
ProjectPlanning
ProjectPlanningCurrencySymbol
ProjectPlanningDayColumnsVisibility
ProjectPlanningQuarterColumnsVisibility
ProjectScope
ProjectLocation

<!-- Export metadata -->
ExportDetails
ExportTime
ExporterName
ExporterVersion
ExternalApp
ExternalProjectId
ProjectId
```

### Conservation Elements
```xml
<!-- Biodiversity targets (core conservation objects) -->
BiodiversityTarget
BiodiversityTargetId
BiodiversityTargetName
BiodiversityTargetUUID
BiodiversityTargetViabilityMode
BiodiversityTargetPool

<!-- Strategies (conservation actions) -->
Strategy
StrategyId
StrategyName
StrategyUUID
StrategyStatus
StrategyOrderedActivityIds
StrategyPool

<!-- Intermediate results (outcomes) -->
IntermediateResult
IntermediateResultId
IntermediateResultName
IntermediateResultUUID
IntermediateResultPool

<!-- Tasks (activities) -->
Task
TaskIdentifier
TaskName
TaskUUID
TaskDetails
TaskPool
```

### Diagram System
```xml
<!-- Conceptual models -->
ConceptualModel
ConceptualModelName
ConceptualModelUUID
ConceptualModelDiagramFactorIds
ConceptualModelDiagramLinkIds
ConceptualModelSelectedTaggedObjectSetIds
ConceptualModelPool

<!-- Results chains -->
ResultsChain
ResultsChainName
ResultsChainUUID
ResultsChainIdentifier
ResultsChainDiagramFactorIds
ResultsChainDiagramLinkIds
ResultsChainSelectedTaggedObjectSetIds
ResultsChainPool

<!-- Diagram factors (visual elements) -->
DiagramFactor
DiagramFactorId
DiagramFactorUUID
DiagramFactorLocation
DiagramFactorSize
DiagramFactorStyle
DiagramFactorWrappedFactorId
DiagramFactorZIndex
DiagramFactorFontSize
DiagramFactorFontColor
DiagramFactorBackgroundColor
DiagramFactorTaggedObjectSetIds
DiagramFactorGroupBoxChildrenIds
DiagramFactorPool

<!-- Diagram links (connections) -->
DiagramLink
DiagramLinkId
DiagramLinkUUID
DiagramLinkFromDiagramFactorId
DiagramLinkToDiagramFactorId
DiagramLinkIsBidirectionalLink
DiagramLinkIsUncertainLink
DiagramLinkZIndex
DiagramLinkBendPoints
DiagramLinkColor
DiagramLinkPool

<!-- Geometric elements -->
DiagramPoint
DiagramSize
x, y, width, height
```

### Supporting Infrastructure
```xml
<!-- Group boxes (visual containers) -->
GroupBox
GroupBoxId
GroupBoxName
GroupBoxUUID
GroupBoxPool

<!-- Text boxes (annotations) -->
TextBox
TextBoxId
TextBoxName
TextBoxUUID
TextBoxPool

<!-- Taxonomy system -->
TaxonomyClassificationContainer

<!-- Extra data (extensibility) -->
ExtraData
ExtraDataItem
ExtraDataItemValue
ExtraDataSection

<!-- Linkable factors -->
LinkableFactorId
WrappedByDiagramFactorId

<!-- Activity references -->
ActivityId

<!-- Style system -->
Style

<!-- Dashboard -->
Dashboard
DashboardUUID
DashboardStatusEntries
DashboardPool

<!-- Planning views -->
PlanningViewConfiguration
PlanningViewConfigurationName
PlanningViewConfigurationUUID
PlanningViewConfigurationDiagramDataInclusion
PlanningViewConfigurationStrategyObjectiveOrder
PlanningViewConfigurationTargetNodePosition
PlanningViewConfigurationPool

<!-- Taxonomy association pools (all types) -->
AssumptionTaxonomyAssociationPool
BiodiversityTargetTaxonomyAssociationPool
BiophysicalFactorTaxonomyAssociationPool
BiophysicalResultTaxonomyAssociationPool
ConceptualModelTaxonomyAssociationPool
ContributingFactorTaxonomyAssociationPool
DirectThreatTaxonomyAssociationPool
ExpenseAssignmentTaxonomyAssociationPool
GoalTaxonomyAssociationPool
HumanWellbeingTargetTaxonomyAssociationPool
IndicatorTaxonomyAssociationPool
IntermediateResultTaxonomyAssociationPool
KeyEcologicalAttributeTaxonomyAssociationPool
MethodTaxonomyAssociationPool
ObjectiveTaxonomyAssociationPool
OutputTaxonomyAssociationPool
ProjectResourceTaxonomyAssociationPool
ResourceAssignmentTaxonomyAssociationPool
ResultsChainTaxonomyAssociationPool
StrategyTaxonomyAssociationPool
StressBasedThreatRatingPool
StressTaxonomyAssociationPool
SubAssumptionTaxonomyAssociationPool
TaskTaxonomyAssociationPool
ThreatReductionResultTaxonomyAssociationPool

<!-- Threat rating -->
SimpleThreatRatingPool

<!-- Organization data -->
MiradiShareProjectData
MiradiShareProjectDataProgramId
MiradiShareProjectDataProgramName
MiradiShareProjectDataProgramTaxonomySetName
MiradiShareProjectDataProgramTaxonomySetVersion
MiradiShareProjectDataProgramTaxonomySetVersionId
MiradiShareProjectDataProgramUrl
MiradiShareProjectDataProjectId
MiradiShareProjectDataProjectTemplateId
MiradiShareProjectDataProjectTemplateName
MiradiShareProjectDataProjectUrl
MiradiShareProjectDataProjectVersion
MiradiShareProjectDataTaxonomyAssociationPool

<!-- Partner organization data -->
FOSProjectData
FOSProjectDataTrainingType
RareProjectData
TNCProjectData
WCSProjectData
WWFProjectData

<!-- HTML elements (for rich text) -->
br, div

<!-- Generic code containers -->
code
```

### Implementation Notes for Must-Support Elements

1. **All elements MUST be parsed** - Missing any of these will break basic project functionality
2. **UUIDs are critical** - All UUID fields must be preserved for referential integrity
3. **Diagram system is essential** - Visual representation is core to Miradi's value proposition
4. **Taxonomy system is universal** - Every project uses taxonomic classification
5. **Rich text support** - Handle `div` and `br` elements for formatted text content

## Should-Support Elements (75%+ Coverage)

These **65 elements** appear in 75% or more projects and provide significant value. Implementing these covers most real-world use cases.

### Enhanced Conservation Features
```xml
<!-- Indicators (monitoring) -->
Indicator (91% of projects)
IndicatorId
IndicatorName
IndicatorUUID
IndicatorIdentifier
IndicatorDetails
IndicatorRelevantActivityIds
IndicatorRelevantStrategyIds
IndicatorPool

<!-- Threat reduction results -->
ThreatReductionResult (91% of projects)
ThreatReductionResultId
ThreatReductionResultName
ThreatReductionResultUUID
ThreatReductionResultPool

<!-- Enhanced target information -->
BiodiversityTargetDetails (91% of projects)
BiodiversityTargetIdentifier (82% of projects)
BiodiversityTargetCalculatedThreatRating (82% of projects)

<!-- Enhanced strategy information -->
StrategyDetails (91% of projects)
StrategyIdentifier (91% of projects)
```

### Resource Management
```xml
<!-- Resources (people and organizations) -->
Resource (82% of projects)
ResourceId
ResourceUUID
ResourceGivenName
ResourceResourceType
ResourcePool

<!-- Resource assignments -->
ResourceAssignment (82% of projects)
ResourceAssignmentId
ResourceAssignmentUUID
ResourceAssignmentResourceId
ResourceAssignmentPool

<!-- Cost calculations -->
CalculatedCosts (82% of projects)
CalculatedStartDate (82% of projects)
CalculatedEndDate (82% of projects)
CalculatedWho (82% of projects)
```

### Progress Tracking
```xml
<!-- Progress reports -->
ProgressReport (82% of projects)
ProgressReportId
ProgressReportUUID
ProgressReportPool

<!-- Project timeline -->
ProjectPlanningStartDate (91% of projects)
ProjectPlanningExpectedEndDate (91% of projects)
ProjectPlanningWorkPlanStartDate (91% of projects)
ProjectPlanningWorkPlanEndDate (91% of projects)
ProjectSummaryDataEffectiveDate (91% of projects)
```

### Taxonomy System
```xml
<!-- Taxonomy definitions -->
Taxonomy (82% of projects)
TaxonomyAssociation
TaxonomyAssociationDescription
TaxonomyAssociationLabel
TaxonomyAssociationMultiSelect
TaxonomyAssociationSelectionType
TaxonomyAssociationTaxonomyCode
TaxonomyElement
TaxonomyElementDescription
TaxonomyElementLabel
TaxonomyElementUserCode
TaxonomyElements
TaxonomyPool
TaxonomyTopLevelElementCodeContainer
TaxonomyVersion
```

### Enhanced Diagram Features
```xml
<!-- Diagram enhancements -->
DiagramLinkGroupedDiagramLinkIds (91% of projects)
ResultsChainZoomScale (82% of projects)

<!-- Task enhancements -->
TaskCalculatedCosts (82% of projects)
TaskComments (82% of projects)
TaskResourceAssignmentIds (82% of projects)

<!-- Intermediate result enhancements -->
IntermediateResultIndicatorIds (82% of projects)
```

### Accounting Integration
```xml
<!-- Accounting classification -->
AccountingClassificationContainer (82% of projects)
```

### Implementation Notes for Should-Support Elements

1. **High ROI features** - These elements provide significant functionality for most users
2. **Monitoring capabilities** - Indicators and progress tracking are widely used
3. **Resource planning** - Most projects involve resource allocation and cost tracking
4. **Taxonomy integration** - Classification systems are nearly universal
5. **Graceful degradation** - Projects without these elements should still function

## Optional Elements (25-74% Coverage)

These **267 elements** appear in 25-74% of projects. Implementation should be based on specific user needs and project requirements.

### Advanced Conservation Features (73% coverage)
```xml
<!-- Threats and causes -->
Cause
CauseId
CauseName
CauseUUID
CauseDetails
CauseCalculatedThreatRating
CauseIsDirectThreat
CausePool

<!-- Goals -->
Goal
GoalId
GoalName
GoalUUID
GoalPool
GoalRelevantIndicatorIds

<!-- Threat ratings -->
SimpleThreatRating
SimpleThreatRatingCalculatedThreatTargetRating
SimpleThreatRatingIsNotApplicable
SimpleThreatRatingTargetId
SimpleThreatRatingThreatId

<!-- Work planning -->
DateUnitWorkUnits
WorkUnitsDateUnit
NumberOfUnits
WorkUnitsQuarter
CalculatedWorkUnitsEntry
CalculatedWorkUnitsEntryDetails
CalculatedWorkUnitsEntryResourceId
CalculatedWorkUnitsTotal
CalculatedWorkUnitsEntries

<!-- Timeframes -->
Timeframe
TimeframeId
TimeframeUUID
TimeframeDetails
TimeframePool
TimeframesDateUnit
TimeframesYear
DateUnitTimeframe
CalculatedTimeframe
CalculatedTotalBudgetCost
CalculatedWorkCostTotal

<!-- Strategy enhancements -->
StrategyCalculatedCosts
StrategyFeasibilityRating
StrategyImpactRating
StrategyTimeframe
StrategyTimeframeIds

<!-- Task enhancements -->
TaskTimeframe
TaskTimeframeIds
TaskProgressReportIds
TaskIsMonitoringActivity
TaskOrderedSubTaskIds

<!-- Progress reporting -->
ProgressReportDetails
ProgressReportProgressDate
ProgressReportProgressStatus

<!-- Results chain enhancements -->
ResultsChainDetails
DiagramFactorFontStyle
DiagramLinkAnnotation

<!-- Project planning -->
ProjectPlanningIncludeWorkPlanDiagramData
```

### Measurement and Monitoring (64% coverage)
```xml
<!-- Measurements -->
Measurement
MeasurementId
MeasurementUUID
MeasurementDate
MeasurementDetail
MeasurementPool

<!-- Objectives -->
Objective
ObjectiveId
ObjectiveName
ObjectiveUUID
ObjectiveEvidenceConfidence
ObjectivePool
ObjectiveRelevantIndicatorIds

<!-- Indicator enhancements -->
IndicatorMeasurementIds
IndicatorViabilityRatingsEvidenceConfidence

<!-- Target enhancements -->
BiodiversityTargetCalculatedViabilityStatus
BiodiversityTargetGoalIds
BiodiversityTargetKeyEcologicalAttributeIds

<!-- Intermediate result enhancements -->
IntermediateResultDetails
IntermediateResultIdentifier

<!-- Threat reduction result enhancements -->
ThreatReductionResultDetails
ThreatReductionResultIndicatorIds
ThreatReductionResultObjectiveIds

<!-- Taxonomy classifications -->
TaxonomyClassification
TaxonomyClassificationTaxonomyCode
TaxonomyClassificationTaxonomyElementCodeContainer
TaxonomyElementChildCodeContainer

<!-- Project scope -->
ProjectScopeProjectVision
ProjectScopeShortProjectScope
ProjectSummaryCalculatedOverallProjectThreatRating
ProjectSummaryCalculatedOverallProjectViabilityRating
ProjectSummaryProjectDescription

<!-- Resource details -->
ResourceAssignmentDetails
ResourceRoleCodesContainer

<!-- Results chain features -->
ResultsChainComments
ResultsChainHiddenTypesContainer
ResultsChainIsProgressStatusDisplayEnabled
ResultsChainIsResultStatusDisplayEnabled
ResultsChainIsTaggingEnabled

<!-- Threat rating details -->
SimpleThreatRatingIrreversibilityRating
SimpleThreatRatingScopeRating
SimpleThreatRatingSeverityRating
TimeframesFullProjectTimespan
```

### Financial Management (55% coverage)
```xml
<!-- Expenses -->
Expense
ExpenseAssignment
ExpenseAssignmentId
ExpenseAssignmentUUID
ExpenseAssignmentDetails
ExpenseAssignmentName
ExpenseAssignmentPool
ExpensesDateUnit
ExpensesYear
DateUnitExpense

<!-- Calculated expenses -->
CalculatedExpenseEntries
CalculatedExpenseEntry
CalculatedExpenseEntryDetails
CalculatedExpenseTotal

<!-- Project planning financial -->
ProjectPlanningFullTimeEmployeeDaysPerYear
ProjectPlanningPlanningComments
ProjectPlanningFiscalYearStart
```

### Key Ecological Attributes (45% coverage)
```xml
<!-- KEAs -->
KeyEcologicalAttribute
KeyEcologicalAttributeId
KeyEcologicalAttributeName
KeyEcologicalAttributeUUID
KeyEcologicalAttributeIndicatorIds
KeyEcologicalAttributeKeyEcologicalAttributeType
KeyEcologicalAttributePool

<!-- Accounting codes -->
AccountingCode
AccountingCodeId
AccountingCodeCode
AccountingCodeName
AccountingCodeUUID
AccountingCodePool

<!-- Target enhancements -->
BiodiversityTargetComments
BiodiversityTargetCurrentStatusJustification
BiodiversityTargetSubTargetIds

<!-- Strategy enhancements -->
StrategyComments
StrategyEvidenceNotes
StrategyIndicatorIds
StrategyObjectiveIds
StrategyOutputIds

<!-- Task enhancements -->
TaskAssignedLeaderResourceId
TaskEvidenceNotes
TaskExpenseAssignmentIds
TaskOutputIds

<!-- Indicator enhancements -->
IndicatorComments
IndicatorThresholds
IndicatorViabilityRatingsComments

<!-- Measurement enhancements -->
MeasurementMeasurementValue
MeasurementRating
MeasurementTrend

<!-- Objective enhancements -->
ObjectiveIdentifier
ObjectiveRelevantActivityIds
ObjectiveRelevantStrategyIds

<!-- Group box enhancements -->
GroupBoxComments
GroupBoxDetails
GroupBoxIdentifier

<!-- Text box enhancements -->
TextBoxComments
TextBoxDetails
TextBoxIdentifier

<!-- Conceptual model enhancements -->
ConceptualModelComments
ConceptualModelDetails
ConceptualModelIdentifier
ConceptualModelHiddenTypesContainer
ConceptualModelIsProgressStatusDisplayEnabled
ConceptualModelIsResultStatusDisplayEnabled
ConceptualModelIsTaggingEnabled

<!-- Cause enhancements -->
CauseIdentifier
CauseObjectiveIds

<!-- Goal enhancements -->
GoalIdentifier
GoalEvidenceConfidence
GoalRelevantActivityIds
GoalRelevantStrategyIds

<!-- Intermediate result enhancements -->
IntermediateResultComments
IntermediateResultEvidenceNotes
IntermediateResultObjectiveIds

<!-- Strategy enhancements -->
StrategyEvidenceConfidence

<!-- Threat reduction result enhancements -->
ThreatReductionResultIdentifier
ThreatReductionResultRelatedDirectThreatId

<!-- Rich text elements -->
b, i

<!-- Tagged object sets -->
TaggedObjectSet
TaggedObjectSetName
TaggedObjectSetUUID
TaggedObjectSetPool

<!-- Planning view configurations -->
PlanningViewConfigurationColumnNamesContainer
PlanningViewConfigurationRowObjectTypesContainer

<!-- Conceptual model zoom -->
ConceptualModelZoomScale
```

### Implementation Notes for Optional Elements

1. **Conditional implementation** - Implement based on user requirements and project types
2. **Feature flags** - Consider making these configurable features
3. **Graceful handling** - Unknown elements should not break parsing
4. **Progressive enhancement** - Basic functionality works without these elements
5. **User feedback driven** - Prioritize based on actual user needs

## Edge Cases and Special Handling (<25% Coverage)

These **184 elements** appear in less than 25% of projects and require special handling strategies.

### Marine/Aquatic Specializations (Single project: Miradi_Marine_Example_v0.48.xmpz2)
```xml
<!-- Marine-specific elements -->
BiophysicalFactor, BiophysicalFactorId, BiophysicalFactorName, BiophysicalFactorPool, BiophysicalFactorUUID
BiophysicalResult, BiophysicalResultId, BiophysicalResultName, BiophysicalResultPool, BiophysicalResultUUID
Stress, StressId, StressName, StressPool, StressUUID
StressCalculatedStressRating, StressScopeRating, StressSeverityRating
IUCNRedListSpecies, IUCNRedListSpeciesName, IUCNRedListSpeciesPool, IUCNRedListSpeciesUUID
Method, MethodId, MethodName, MethodPool, MethodUUID
GeospatialLocation, latitude, longitude
```

### Financial Specializations (Single project: Miradi_Marine_Example_v0.48.xmpz2)
```xml
<!-- Funding sources -->
FundingSource, FundingSourceId, FundingSourceCode, FundingSourceName, FundingSourcePool, FundingSourceUUID
CalculatedExpenseEntryFundingSourceId
CalculatedWorkUnitsEntryFundingSourceId
ExpenseAssignmentFundingSourceId
ResourceAssignmentFundingSourceId

<!-- Advanced financial planning -->
ProjectPlanningBudgetSecuredPercent
ProjectPlanningKeyFundingSources
ProjectPlanningTotalBudgetForFunding
```

### Organization Management (Single project: Miradi_Marine_Example_v0.48.xmpz2)
```xml
<!-- Organizations -->
Organization, OrganizationName, OrganizationPool, OrganizationUUID
OrganizationComments, OrganizationEmail, OrganizationGivenName, OrganizationIdentifier
OrganizationPhoneNumber, OrganizationRolesDescription, OrganizationSurname

<!-- Progress tracking -->
Progress, ProgressPercent, ProgressPercentId, ProgressPercentPool, ProgressPercentUUID
ProgressPercentDetails, ProgressPercentPercentComplete, ProgressPercentPercentDate
```

### Project-Specific Customizations
```xml
<!-- Venezuela project specific -->
ProjectScopeAccessInformation, ProjectScopeBiologicalDescription, ProjectScopeCulturalDescription
ProjectScopeCurrentLandUses, ProjectScopeHistoricalDescription, ProjectScopeLegalStatus
ProjectScopeLegislativeContext, ProjectScopeManagementResources, ProjectScopePhysicalDescription
ProjectScopeSocioEconomicInformation, ProjectScopeVisitationInformation

<!-- Strategic plan specific -->
ol (ordered lists)
ObjectiveEvidenceNotes

<!-- Adaptive management specific -->
TimeframeName

<!-- Various project customizations -->
ConceptualModelExtendedProgressReportIds
FutureStatusComment, FutureStatusName
ScopeBoxComments, ScopeBoxIdentifier
SimpleThreatRatingEvidenceConfidence
```

### Legacy and Experimental Elements
```xml
<!-- Assumptions (limited use) -->
Assumption, AssumptionId, AssumptionName, AssumptionUUID
AssumptionComments, AssumptionDetails, AssumptionEvidenceNotes
AssumptionFutureInformationNeeds, AssumptionIdentifier, AssumptionImplications

<!-- Human wellbeing targets (limited adoption) -->
HumanWellbeingTarget, HumanWellbeingTargetId, HumanWellbeingTargetName
HumanWellbeingTargetUUID, HumanWellbeingTargetViabilityMode

<!-- Sub-targets (limited use) -->
SubTarget, SubTargetId, SubTargetName, SubTargetPool, SubTargetUUID

<!-- Extended progress reporting -->
ExtendedProgressReport, ExtendedProgressReportId, ExtendedProgressReportUUID
ExtendedProgressReportDetails, ExtendedProgressReportLessonsLearned, ExtendedProgressReportNextSteps

<!-- Future status tracking -->
FutureStatus, FutureStatusId, FutureStatusUUID
FutureStatusDate, FutureStatusDetails, FutureStatusRating, FutureStatusSummary

<!-- Result reporting -->
ResultReport, ResultReportId, ResultReportUUID
ResultReportDetails, ResultReportResultDate, ResultReportResultStatus

<!-- Scope boxes -->
ScopeBox, ScopeBoxId, ScopeBoxName, ScopeBoxPool, ScopeBoxUUID
ScopeBoxScopeBoxTypeCode

<!-- Standard classifications -->
CauseStandardClassification, CauseStandardClassificationContainer
StrategyStandardClassification, StrategyStandardClassificationContainer
```

### Special Handling Strategies

#### 1. Unknown Element Handling
```python
def handle_unknown_element(element_name, element_content):
    """
    Strategy for handling unknown/rare elements
    """
    # Log for analysis
    logger.info(f"Unknown element encountered: {element_name}")
    
    # Store as raw XML for potential future processing
    return {
        'element_type': 'unknown',
        'name': element_name,
        'raw_xml': element_content,
        'parsed_at': datetime.now()
    }
```

#### 2. Project Type Detection
```python
def detect_project_specialization(project_elements):
    """
    Detect project type based on specialized elements
    """
    if 'BiophysicalFactor' in project_elements:
        return 'marine'
    elif 'HumanWellbeingTarget' in project_elements:
        return 'social'
    elif 'FundingSource' in project_elements:
        return 'financial_detailed'
    else:
        return 'standard'
```

#### 3. Graceful Degradation
```python
def parse_with_fallback(element, parsers):
    """
    Parse with fallback to generic handling
    """
    element_name = element.tag
    
    if element_name in parsers:
        return parsers[element_name](element)
    elif element_name in RARE_ELEMENTS:
        return handle_rare_element(element)
    else:
        return handle_unknown_element(element_name, element)
```

#### 4. Feature Flags
```python
FEATURE_FLAGS = {
    'marine_elements': False,
    'financial_tracking': True,
    'extended_reporting': False,
    'assumptions': False,
    'human_wellbeing': False
}

def should_parse_element(element_name):
    """
    Check if element should be parsed based on feature flags
    """
    if element_name in MARINE_ELEMENTS:
        return FEATURE_FLAGS['marine_elements']
    elif element_name in FINANCIAL_ELEMENTS:
        return FEATURE_FLAGS['financial_tracking']
    # ... etc
    return True  # Default to parsing
```

## Implementation Recommendations

### Phase 1: Core Implementation (Must-Support)
- **Timeline**: 2-3 months
- **Elements**: 173 core elements
- **Goal**: Basic project functionality
- **Success Criteria**: Can load and display any Miradi project

### Phase 2: Enhanced Features (Should-Support)
- **Timeline**: 1-2 months
- **Elements**: 65 additional elements
- **Goal**: Support 90%+ of real-world use cases
- **Success Criteria**: Full functionality for most projects

### Phase 3: Advanced Features (Optional)
- **Timeline**: 3-6 months (iterative)
- **Elements**: 267 conditional elements
- **Goal**: Support specialized workflows
- **Success Criteria**: Feature-complete for specific domains

### Phase 4: Edge Cases (Special Handling)
- **Timeline**: Ongoing
- **Elements**: 184 rare elements
- **Goal**: Robust handling of all variations
- **Success Criteria**: No project fails to load

### Validation Strategy

#### Required Element Validation
```python
REQUIRED_ELEMENTS = [
    'ConservationProject',
    'ProjectSummary',
    'BiodiversityTargetPool',
    'StrategyPool',
    'TaskPool',
    'DiagramFactorPool',
    'DiagramLinkPool'
]

def validate_required_elements(project_xml):
    """Validate that all required elements are present"""
    missing = []
    for element in REQUIRED_ELEMENTS:
        if not project_xml.find(f".//{element}"):
            missing.append(element)
    
    if missing:
        raise ValidationError(f"Missing required elements: {missing}")
```

#### Data Integrity Checks
```python
def validate_references(project_data):
    """Validate that all ID references are valid"""
    # Check that all referenced IDs exist
    # Validate UUID uniqueness
    # Ensure referential integrity
    pass
```

### Error Handling Guidelines

1. **Fail Fast for Core Elements** - Missing must-support elements should cause immediate failure
2. **Graceful Degradation for Optional Elements** - Log warnings but continue processing
3. **Store Unknown Elements** - Preserve rare/unknown elements for future analysis
4. **Detailed Error Messages** - Provide actionable feedback for validation failures
5. **Recovery Strategies** - Attempt to repair common data issues automatically

### Performance Considerations

1. **Streaming Parser** - Use SAX or iterative parsing for large files
2. **Lazy Loading** - Load optional elements only when needed
3. **Caching Strategy** - Cache parsed taxonomy and reference data
4. **Memory Management** - Process large projects in chunks
5. **Index Creation** - Build indexes for frequently accessed elements

### Testing Strategy

1. **Core Element Tests** - Ensure all 173 must-support elements parse correctly
2. **Reference Project Tests** - Test against all 11 analyzed projects
3. **Edge Case Tests** - Specific tests for rare element handling
4. **Performance Tests** - Validate performance with large projects
5. **Regression Tests** - Ensure changes don't break existing functionality

This requirements document provides a data-driven foundation for implementing robust Miradi parsers that can handle the full spectrum of real-world conservation projects while prioritizing development effort for maximum impact.
