#!/usr/bin/env python3
"""
Miradi XML Parser

This module provides classes for parsing Miradi .xmpz2 files based on empirical analysis
of real-world conservation projects. The parser is designed to handle the full spectrum
of Miradi schema variations while prioritizing the most essential elements.

Based on analysis of 11 Miradi projects covering 689 unique elements.
"""

import logging
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass, field


# Configure logging
logger = logging.getLogger(__name__)


class UnknownElementHandling(Enum):
    """Strategy for handling unknown elements."""
    LOG = "log"          # Log and continue
    ERROR = "error"      # Raise exception
    STORE = "store"      # Store for later analysis
    IGNORE = "ignore"    # Silently ignore


class ElementPriority(Enum):
    """Element priority levels based on frequency analysis."""
    MUST_SUPPORT = "must_support"      # 100% of projects (173 elements)
    SHOULD_SUPPORT = "should_support"  # 75%+ of projects (65 elements)
    OPTIONAL = "optional"              # 25-74% of projects (267 elements)
    EDGE_CASE = "edge_case"           # <25% of projects (184 elements)


@dataclass
class ParsedElement:
    """Container for parsed element data."""
    element_type: str
    element_id: Optional[str] = None
    uuid: Optional[str] = None
    name: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    raw_xml: Optional[str] = None
    priority: Optional[ElementPriority] = None


@dataclass
class ParsingStats:
    """Statistics about the parsing process."""
    total_elements: int = 0
    must_support_elements: int = 0
    should_support_elements: int = 0
    optional_elements: int = 0
    edge_case_elements: int = 0
    unknown_elements: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    element_counts: Dict[str, int] = field(default_factory=Counter)
    unknown_element_names: Set[str] = field(default_factory=set)


class MiradiParsingError(Exception):
    """Exception raised during Miradi parsing."""
    pass


class MiradiValidationError(MiradiParsingError):
    """Exception raised during validation."""
    pass


class BaseParser(ABC):
    """
    Abstract base class for Miradi parsers.
    
    Defines the interface for extracting different types of conservation elements
    from Miradi project files.
    """
    
    def __init__(self, unknown_element_handling: UnknownElementHandling = UnknownElementHandling.LOG):
        """
        Initialize the base parser.
        
        Args:
            unknown_element_handling: Strategy for handling unknown elements
        """
        self.unknown_element_handling = unknown_element_handling
        self.stats = ParsingStats()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def extract_project_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract project metadata from ProjectSummary elements.
        
        Args:
            root: Root XML element
            
        Returns:
            Dictionary containing project metadata
        """
        pass
    
    @abstractmethod
    def extract_conservation_targets(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract biodiversity targets from BiodiversityTarget elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed biodiversity target elements
        """
        pass
    
    @abstractmethod
    def extract_threats(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract threats from Cause/DirectThreat elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed threat elements
        """
        pass
    
    @abstractmethod
    def extract_strategies(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract conservation strategies from Strategy elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed strategy elements
        """
        pass
    
    @abstractmethod
    def extract_results_chains(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract results chains from ResultsChain elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed results chain elements
        """
        pass
    
    @abstractmethod
    def extract_conceptual_models(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract conceptual models from ConceptualModel elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed conceptual model elements
        """
        pass
    
    @abstractmethod
    def extract_activities(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract activities from Task elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed activity (task) elements
        """
        pass
    
    @abstractmethod
    def parse_all(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Orchestrate all extractors to parse a complete Miradi project.
        
        Args:
            file_path: Path to the .xmpz2 file
            
        Returns:
            Dictionary containing all parsed project data
        """
        pass


class MiradiParser(BaseParser):
    """
    Concrete implementation of Miradi parser supporting the 173 must-support elements
    identified through empirical analysis of real-world conservation projects.
    """
    
    # Must-support elements (100% coverage) - 173 elements
    MUST_SUPPORT_ELEMENTS = {
        # Core Project Structure
        "ConservationProject", "ProjectSummary", "ProjectSummaryProjectId", 
        "ProjectSummaryProjectName", "ProjectSummaryFactorMode", "ProjectSummaryTargetMode",
        "ProjectSummaryThreatRatingMode", "ProjectSummaryWorkPlanTimeUnit", 
        "ProjectSummaryShareOutsideOrganization", "ProjectSummaryExtendedProgressReportIds",
        "ProjectPlanning", "ProjectPlanningCurrencySymbol", "ProjectPlanningDayColumnsVisibility",
        "ProjectPlanningQuarterColumnsVisibility", "ProjectScope", "ProjectLocation",
        "ExportDetails", "ExportTime", "ExporterName", "ExporterVersion", 
        "ExternalApp", "ExternalProjectId", "ProjectId",
        
        # Conservation Elements
        "BiodiversityTarget", "BiodiversityTargetId", "BiodiversityTargetName", 
        "BiodiversityTargetUUID", "BiodiversityTargetViabilityMode", "BiodiversityTargetPool",
        "Strategy", "StrategyId", "StrategyName", "StrategyUUID", "StrategyStatus", 
        "StrategyOrderedActivityIds", "StrategyPool",
        "IntermediateResult", "IntermediateResultId", "IntermediateResultName", 
        "IntermediateResultUUID", "IntermediateResultPool",
        "Task", "TaskIdentifier", "TaskName", "TaskUUID", "TaskDetails", "TaskPool",
        
        # Diagram System
        "ConceptualModel", "ConceptualModelName", "ConceptualModelUUID", 
        "ConceptualModelDiagramFactorIds", "ConceptualModelDiagramLinkIds", 
        "ConceptualModelSelectedTaggedObjectSetIds", "ConceptualModelPool",
        "ResultsChain", "ResultsChainName", "ResultsChainUUID", "ResultsChainIdentifier",
        "ResultsChainDiagramFactorIds", "ResultsChainDiagramLinkIds", 
        "ResultsChainSelectedTaggedObjectSetIds", "ResultsChainPool",
        "DiagramFactor", "DiagramFactorId", "DiagramFactorUUID", "DiagramFactorLocation",
        "DiagramFactorSize", "DiagramFactorStyle", "DiagramFactorWrappedFactorId",
        "DiagramFactorZIndex", "DiagramFactorFontSize", "DiagramFactorFontColor",
        "DiagramFactorBackgroundColor", "DiagramFactorTaggedObjectSetIds", 
        "DiagramFactorGroupBoxChildrenIds", "DiagramFactorPool",
        "DiagramLink", "DiagramLinkId", "DiagramLinkUUID", "DiagramLinkFromDiagramFactorId",
        "DiagramLinkToDiagramFactorId", "DiagramLinkIsBidirectionalLink", 
        "DiagramLinkIsUncertainLink", "DiagramLinkZIndex", "DiagramLinkBendPoints",
        "DiagramLinkColor", "DiagramLinkPool",
        "DiagramPoint", "DiagramSize", "x", "y", "width", "height",
        
        # Supporting Infrastructure
        "GroupBox", "GroupBoxId", "GroupBoxName", "GroupBoxUUID", "GroupBoxPool",
        "TextBox", "TextBoxId", "TextBoxName", "TextBoxUUID", "TextBoxPool",
        "TaxonomyClassificationContainer", "ExtraData", "ExtraDataItem", 
        "ExtraDataItemValue", "ExtraDataSection", "LinkableFactorId", 
        "WrappedByDiagramFactorId", "ActivityId", "Style",
        "Dashboard", "DashboardUUID", "DashboardStatusEntries", "DashboardPool",
        "PlanningViewConfiguration", "PlanningViewConfigurationName", 
        "PlanningViewConfigurationUUID", "PlanningViewConfigurationDiagramDataInclusion",
        "PlanningViewConfigurationStrategyObjectiveOrder", 
        "PlanningViewConfigurationTargetNodePosition", "PlanningViewConfigurationPool",
        
        # Taxonomy Association Pools
        "AssumptionTaxonomyAssociationPool", "BiodiversityTargetTaxonomyAssociationPool",
        "BiophysicalFactorTaxonomyAssociationPool", "BiophysicalResultTaxonomyAssociationPool",
        "ConceptualModelTaxonomyAssociationPool", "ContributingFactorTaxonomyAssociationPool",
        "DirectThreatTaxonomyAssociationPool", "ExpenseAssignmentTaxonomyAssociationPool",
        "GoalTaxonomyAssociationPool", "HumanWellbeingTargetTaxonomyAssociationPool",
        "IndicatorTaxonomyAssociationPool", "IntermediateResultTaxonomyAssociationPool",
        "KeyEcologicalAttributeTaxonomyAssociationPool", "MethodTaxonomyAssociationPool",
        "ObjectiveTaxonomyAssociationPool", "OutputTaxonomyAssociationPool",
        "ProjectResourceTaxonomyAssociationPool", "ResourceAssignmentTaxonomyAssociationPool",
        "ResultsChainTaxonomyAssociationPool", "StrategyTaxonomyAssociationPool",
        "StressBasedThreatRatingPool", "StressTaxonomyAssociationPool",
        "SubAssumptionTaxonomyAssociationPool", "TaskTaxonomyAssociationPool",
        "ThreatReductionResultTaxonomyAssociationPool", "SimpleThreatRatingPool",
        
        # Organization Data
        "MiradiShareProjectData", "MiradiShareProjectDataProgramId", 
        "MiradiShareProjectDataProgramName", "MiradiShareProjectDataProgramTaxonomySetName",
        "MiradiShareProjectDataProgramTaxonomySetVersion", 
        "MiradiShareProjectDataProgramTaxonomySetVersionId", "MiradiShareProjectDataProgramUrl",
        "MiradiShareProjectDataProjectId", "MiradiShareProjectDataProjectTemplateId",
        "MiradiShareProjectDataProjectTemplateName", "MiradiShareProjectDataProjectUrl",
        "MiradiShareProjectDataProjectVersion", "MiradiShareProjectDataTaxonomyAssociationPool",
        "FOSProjectData", "FOSProjectDataTrainingType", "RareProjectData", 
        "TNCProjectData", "WCSProjectData", "WWFProjectData",
        
        # HTML elements and generic containers
        "br", "div", "code"
    }
    
    # Should-support elements (75%+ coverage) - 65 elements
    SHOULD_SUPPORT_ELEMENTS = {
        "Indicator", "IndicatorId", "IndicatorName", "IndicatorUUID", "IndicatorIdentifier",
        "IndicatorDetails", "IndicatorRelevantActivityIds", "IndicatorRelevantStrategyIds", 
        "IndicatorPool", "ThreatReductionResult", "ThreatReductionResultId", 
        "ThreatReductionResultName", "ThreatReductionResultUUID", "ThreatReductionResultPool",
        "BiodiversityTargetDetails", "BiodiversityTargetIdentifier", 
        "BiodiversityTargetCalculatedThreatRating", "StrategyDetails", "StrategyIdentifier",
        "Resource", "ResourceId", "ResourceUUID", "ResourceGivenName", "ResourceResourceType",
        "ResourcePool", "ResourceAssignment", "ResourceAssignmentId", "ResourceAssignmentUUID",
        "ResourceAssignmentResourceId", "ResourceAssignmentPool", "CalculatedCosts",
        "CalculatedStartDate", "CalculatedEndDate", "CalculatedWho", "ProgressReport",
        "ProgressReportId", "ProgressReportUUID", "ProgressReportPool",
        "ProjectPlanningStartDate", "ProjectPlanningExpectedEndDate", 
        "ProjectPlanningWorkPlanStartDate", "ProjectPlanningWorkPlanEndDate",
        "ProjectSummaryDataEffectiveDate", "Taxonomy", "TaxonomyAssociation",
        "TaxonomyAssociationDescription", "TaxonomyAssociationLabel", 
        "TaxonomyAssociationMultiSelect", "TaxonomyAssociationSelectionType",
        "TaxonomyAssociationTaxonomyCode", "TaxonomyElement", "TaxonomyElementDescription",
        "TaxonomyElementLabel", "TaxonomyElementUserCode", "TaxonomyElements",
        "TaxonomyPool", "TaxonomyTopLevelElementCodeContainer", "TaxonomyVersion",
        "DiagramLinkGroupedDiagramLinkIds", "ResultsChainZoomScale", "TaskCalculatedCosts",
        "TaskComments", "TaskResourceAssignmentIds", "IntermediateResultIndicatorIds",
        "AccountingClassificationContainer"
    }
    
    # Required elements that must be present for basic functionality
    REQUIRED_ELEMENTS = {
        "ConservationProject", "ProjectSummary", "BiodiversityTargetPool", 
        "StrategyPool", "TaskPool", "DiagramFactorPool", "DiagramLinkPool"
    }
    
    def __init__(self, 
                 unknown_element_handling: UnknownElementHandling = UnknownElementHandling.LOG,
                 validate_schema: bool = True,
                 namespace_aware: bool = True):
        """
        Initialize the Miradi parser.
        
        Args:
            unknown_element_handling: Strategy for handling unknown elements
            validate_schema: Whether to validate against known schema
            namespace_aware: Whether to handle XML namespaces
        """
        super().__init__(unknown_element_handling)
        self.validate_schema = validate_schema
        self.namespace_aware = namespace_aware
        self.namespace_map = {}
        
        # Initialize element priority mapping
        self._build_element_priority_map()
        
        self.logger.info(f"Initialized MiradiParser with {len(self.MUST_SUPPORT_ELEMENTS)} must-support elements")
    
    def _build_element_priority_map(self) -> None:
        """Build mapping of element names to their priority levels."""
        self.element_priorities = {}
        
        for element in self.MUST_SUPPORT_ELEMENTS:
            self.element_priorities[element] = ElementPriority.MUST_SUPPORT
        
        for element in self.SHOULD_SUPPORT_ELEMENTS:
            self.element_priorities[element] = ElementPriority.SHOULD_SUPPORT
    
    def _extract_from_zip(self, file_path: Path) -> Path:
        """
        Extract .xmpz2 file to temporary directory.
        
        Args:
            file_path: Path to the .xmpz2 file
            
        Returns:
            Path to temporary directory with extracted files
        """
        if not file_path.exists():
            raise MiradiParsingError(f"File not found: {file_path}")
        
        temp_dir = Path(tempfile.mkdtemp(prefix="miradi_parser_"))
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                self.logger.info(f"Extracted {len(zip_ref.namelist())} files to {temp_dir}")
                
        except zipfile.BadZipFile as e:
            raise MiradiParsingError(f"Invalid zip file: {file_path}") from e
        
        return temp_dir
    
    def _find_project_xml(self, directory: Path) -> Path:
        """
        Find the main project.xml file in the extracted directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            Path to project.xml file
        """
        project_xml = directory / "project.xml"
        if project_xml.exists():
            return project_xml
        
        # Search for any XML file if project.xml not found
        xml_files = list(directory.glob("*.xml"))
        if xml_files:
            self.logger.warning(f"project.xml not found, using {xml_files[0].name}")
            return xml_files[0]
        
        raise MiradiParsingError(f"No XML files found in {directory}")
    
    def _clean_element_name(self, element_name: str) -> str:
        """
        Clean element name by removing namespace prefix.
        
        Args:
            element_name: Raw element name from XML
            
        Returns:
            Cleaned element name
        """
        if '}' in element_name:
            # Remove namespace: {namespace}ElementName -> ElementName
            return element_name.split('}')[-1]
        return element_name
    
    def _handle_unknown_element(self, element: ET.Element) -> Optional[ParsedElement]:
        """
        Handle unknown elements based on configuration.
        
        Args:
            element: Unknown XML element
            
        Returns:
            ParsedElement if stored, None otherwise
        """
        element_name = self._clean_element_name(element.tag)
        self.stats.unknown_elements += 1
        self.stats.unknown_element_names.add(element_name)
        
        if self.unknown_element_handling == UnknownElementHandling.ERROR:
            raise MiradiParsingError(f"Unknown element encountered: {element_name}")
        
        elif self.unknown_element_handling == UnknownElementHandling.LOG:
            self.logger.warning(f"Unknown element: {element_name}")
            
        elif self.unknown_element_handling == UnknownElementHandling.STORE:
            self.logger.info(f"Storing unknown element: {element_name}")
            return ParsedElement(
                element_type=element_name,
                data={'raw_xml': ET.tostring(element, encoding='unicode')},
                priority=ElementPriority.EDGE_CASE
            )
        
        # IGNORE case - do nothing
        return None
    
    def _validate_required_elements(self, root: ET.Element) -> None:
        """
        Validate that all required elements are present.
        
        Args:
            root: Root XML element
            
        Raises:
            MiradiValidationError: If required elements are missing
        """
        if not self.validate_schema:
            return
        
        missing_elements = []
        
        for required_element in self.REQUIRED_ELEMENTS:
            # Search for element with or without namespace
            found = (root.find(f".//{required_element}") is not None or
                    any(self._clean_element_name(elem.tag) == required_element 
                        for elem in root.iter()))
            
            if not found:
                missing_elements.append(required_element)
        
        if missing_elements:
            error_msg = f"Missing required elements: {missing_elements}"
            self.stats.errors.append(error_msg)
            raise MiradiValidationError(error_msg)
    
    def _extract_element_data(self, element: ET.Element) -> Dict[str, Any]:
        """
        Extract data from an XML element.
        
        Args:
            element: XML element to extract data from
            
        Returns:
            Dictionary containing element data
        """
        data = {}
        
        # Extract text content
        if element.text and element.text.strip():
            data['text'] = element.text.strip()
        
        # Extract attributes
        if element.attrib:
            data['attributes'] = dict(element.attrib)
        
        # Extract child elements
        children = {}
        for child in element:
            child_name = self._clean_element_name(child.tag)
            child_data = self._extract_element_data(child)
            
            if child_name in children:
                # Handle multiple children with same name
                if not isinstance(children[child_name], list):
                    children[child_name] = [children[child_name]]
                children[child_name].append(child_data)
            else:
                children[child_name] = child_data
        
        if children:
            data['children'] = children
        
        return data
    
    def _track_element_stats(self, element_name: str) -> None:
        """
        Track statistics for parsed elements.
        
        Args:
            element_name: Name of the element being tracked
        """
        self.stats.total_elements += 1
        self.stats.element_counts[element_name] += 1
        
        priority = self.element_priorities.get(element_name, ElementPriority.EDGE_CASE)
        
        if priority == ElementPriority.MUST_SUPPORT:
            self.stats.must_support_elements += 1
        elif priority == ElementPriority.SHOULD_SUPPORT:
            self.stats.should_support_elements += 1
        elif priority == ElementPriority.OPTIONAL:
            self.stats.optional_elements += 1
        else:
            self.stats.edge_case_elements += 1
    
    def extract_project_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract project metadata from ProjectSummary elements.
        
        Args:
            root: Root XML element
            
        Returns:
            Dictionary containing project metadata
        """
        self.logger.info("Extracting project metadata")
        metadata = {}
        
        # Find ProjectSummary element
        project_summary = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "ProjectSummary":
                project_summary = elem
                break
        
        if project_summary is None:
            self.logger.warning("ProjectSummary element not found")
            return metadata
        
        # Extract key metadata fields
        metadata_fields = [
            "ProjectSummaryProjectId", "ProjectSummaryProjectName", 
            "ProjectSummaryFactorMode", "ProjectSummaryTargetMode",
            "ProjectSummaryThreatRatingMode", "ProjectSummaryWorkPlanTimeUnit",
            "ProjectSummaryShareOutsideOrganization", "ProjectSummaryDataEffectiveDate"
        ]
        
        for field in metadata_fields:
            for elem in project_summary.iter():
                if self._clean_element_name(elem.tag) == field:
                    metadata[field] = self._extract_element_data(elem)
                    self._track_element_stats(field)
                    break
        
        self.logger.info(f"Extracted {len(metadata)} metadata fields")
        return metadata
    
    def extract_conservation_targets(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract biodiversity targets from BiodiversityTarget elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed biodiversity target elements
        """
        self.logger.info("Extracting conservation targets")
        targets = []
        
        # Find BiodiversityTargetPool
        target_pool = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "BiodiversityTargetPool":
                target_pool = elem
                break
        
        if target_pool is None:
            self.logger.warning("BiodiversityTargetPool not found")
            return targets
        
        # Extract individual targets
        for elem in target_pool.iter():
            if self._clean_element_name(elem.tag) == "BiodiversityTarget":
                target_data = self._extract_element_data(elem)
                
                # Extract key identifiers
                target_id = None
                target_uuid = None
                target_name = None
                
                for child in elem.iter():
                    child_name = self._clean_element_name(child.tag)
                    if child_name == "BiodiversityTargetId" and child.text:
                        target_id = child.text.strip()
                    elif child_name == "BiodiversityTargetUUID" and child.text:
                        target_uuid = child.text.strip()
                    elif child_name == "BiodiversityTargetName" and child.text:
                        target_name = child.text.strip()
                
                target = ParsedElement(
                    element_type="BiodiversityTarget",
                    element_id=target_id,
                    uuid=target_uuid,
                    name=target_name,
                    data=target_data,
                    priority=ElementPriority.MUST_SUPPORT
                )
                
                targets.append(target)
                self._track_element_stats("BiodiversityTarget")
        
        self.logger.info(f"Extracted {len(targets)} conservation targets")
        return targets
    
    def extract_threats(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract threats from Cause/DirectThreat elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed threat elements
        """
        self.logger.info("Extracting threats")
        threats = []
        
        # Find CausePool (threats are stored as Cause elements)
        cause_pool = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "CausePool":
                cause_pool = elem
                break
        
        if cause_pool is None:
            self.logger.warning("CausePool not found")
            return threats
        
        # Extract individual causes/threats
        for elem in cause_pool.iter():
            if self._clean_element_name(elem.tag) == "Cause":
                threat_data = self._extract_element_data(elem)
                
                # Extract key identifiers
                threat_id = None
                threat_uuid = None
                threat_name = None
                
                for child in elem.iter():
                    child_name = self._clean_element_name(child.tag)
                    if child_name == "CauseId" and child.text:
                        threat_id = child.text.strip()
                    elif child_name == "CauseUUID" and child.text:
                        threat_uuid = child.text.strip()
                    elif child_name == "CauseName" and child.text:
                        threat_name = child.text.strip()
                
                threat = ParsedElement(
                    element_type="Cause",
                    element_id=threat_id,
                    uuid=threat_uuid,
                    name=threat_name,
                    data=threat_data,
                    priority=ElementPriority.OPTIONAL  # Causes are 73% coverage
                )
                
                threats.append(threat)
                self._track_element_stats("Cause")
        
        self.logger.info(f"Extracted {len(threats)} threats")
        return threats
    
    def extract_strategies(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract conservation strategies from Strategy elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed strategy elements
        """
        self.logger.info("Extracting strategies")
        strategies = []
        
        # Find StrategyPool
        strategy_pool = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "StrategyPool":
                strategy_pool = elem
                break
        
        if strategy_pool is None:
            self.logger.warning("StrategyPool not found")
            return strategies
        
        # Extract individual strategies
        for elem in strategy_pool.iter():
            if self._clean_element_name(elem.tag) == "Strategy":
                strategy_data = self._extract_element_data(elem)
                
                # Extract key identifiers
                strategy_id = None
                strategy_uuid = None
                strategy_name = None
                
                for child in elem.iter():
                    child_name = self._clean_element_name(child.tag)
                    if child_name == "StrategyId" and child.text:
                        strategy_id = child.text.strip()
                    elif child_name == "StrategyUUID" and child.text:
                        strategy_uuid = child.text.strip()
                    elif child_name == "StrategyName" and child.text:
                        strategy_name = child.text.strip()
                
                strategy = ParsedElement(
                    element_type="Strategy",
                    element_id=strategy_id,
                    uuid=strategy_uuid,
                    name=strategy_name,
                    data=strategy_data,
                    priority=ElementPriority.MUST_SUPPORT
                )
                
                strategies.append(strategy)
                self._track_element_stats("Strategy")
        
        self.logger.info(f"Extracted {len(strategies)} strategies")
        return strategies
    
    def extract_results_chains(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract results chains from ResultsChain elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed results chain elements
        """
        self.logger.info("Extracting results chains")
        results_chains = []
        
        # Find ResultsChainPool
        results_chain_pool = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "ResultsChainPool":
                results_chain_pool = elem
                break
        
        if results_chain_pool is None:
            self.logger.warning("ResultsChainPool not found")
            return results_chains
        
        # Extract individual results chains
        for elem in results_chain_pool.iter():
            if self._clean_element_name(elem.tag) == "ResultsChain":
                chain_data = self._extract_element_data(elem)
                
                # Extract key identifiers
                chain_id = None
                chain_uuid = None
                chain_name = None
                
                for child in elem.iter():
                    child_name = self._clean_element_name(child.tag)
                    if child_name == "ResultsChainId" and child.text:
                        chain_id = child.text.strip()
                    elif child_name == "ResultsChainUUID" and child.text:
                        chain_uuid = child.text.strip()
                    elif child_name == "ResultsChainName" and child.text:
                        chain_name = child.text.strip()
                
                chain = ParsedElement(
                    element_type="ResultsChain",
                    element_id=chain_id,
                    uuid=chain_uuid,
                    name=chain_name,
                    data=chain_data,
                    priority=ElementPriority.MUST_SUPPORT
                )
                
                results_chains.append(chain)
                self._track_element_stats("ResultsChain")
        
        self.logger.info(f"Extracted {len(results_chains)} results chains")
        return results_chains
    
    def extract_conceptual_models(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract conceptual models from ConceptualModel elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed conceptual model elements
        """
        self.logger.info("Extracting conceptual models")
        models = []
        
        # Find ConceptualModelPool
        model_pool = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "ConceptualModelPool":
                model_pool = elem
                break
        
        if model_pool is None:
            self.logger.warning("ConceptualModelPool not found")
            return models
        
        # Extract individual conceptual models
        for elem in model_pool.iter():
            if self._clean_element_name(elem.tag) == "ConceptualModel":
                model_data = self._extract_element_data(elem)
                
                # Extract key identifiers
                model_id = None
                model_uuid = None
                model_name = None
                
                for child in elem.iter():
                    child_name = self._clean_element_name(child.tag)
                    if child_name == "ConceptualModelId" and child.text:
                        model_id = child.text.strip()
                    elif child_name == "ConceptualModelUUID" and child.text:
                        model_uuid = child.text.strip()
                    elif child_name == "ConceptualModelName" and child.text:
                        model_name = child.text.strip()
                
                model = ParsedElement(
                    element_type="ConceptualModel",
                    element_id=model_id,
                    uuid=model_uuid,
                    name=model_name,
                    data=model_data,
                    priority=ElementPriority.MUST_SUPPORT
                )
                
                models.append(model)
                self._track_element_stats("ConceptualModel")
        
        self.logger.info(f"Extracted {len(models)} conceptual models")
        return models
    
    def extract_activities(self, root: ET.Element) -> List[ParsedElement]:
        """
        Extract activities from Task elements.
        
        Args:
            root: Root XML element
            
        Returns:
            List of parsed activity (task) elements
        """
        self.logger.info("Extracting activities")
        activities = []
        
        # Find TaskPool
        task_pool = None
        for elem in root.iter():
            if self._clean_element_name(elem.tag) == "TaskPool":
                task_pool = elem
                break
        
        if task_pool is None:
            self.logger.warning("TaskPool not found")
            return activities
        
        # Extract individual tasks/activities
        for elem in task_pool.iter():
            if self._clean_element_name(elem.tag) == "Task":
                activity_data = self._extract_element_data(elem)
                
                # Extract key identifiers
                activity_id = None
                activity_uuid = None
                activity_name = None
                activity_identifier = None
                
                for child in elem.iter():
                    child_name = self._clean_element_name(child.tag)
                    if child_name == "TaskId" and child.text:
                        activity_id = child.text.strip()
                    elif child_name == "TaskUUID" and child.text:
                        activity_uuid = child.text.strip()
                    elif child_name == "TaskName" and child.text:
                        activity_name = child.text.strip()
                    elif child_name == "TaskIdentifier" and child.text:
                        activity_identifier = child.text.strip()
                
                activity = ParsedElement(
                    element_type="Task",
                    element_id=activity_id,
                    uuid=activity_uuid,
                    name=activity_name,
                    data=activity_data,
                    priority=ElementPriority.MUST_SUPPORT
                )
                
                # Add identifier to data if present
                if activity_identifier:
                    activity.data['identifier'] = activity_identifier
                
                activities.append(activity)
                self._track_element_stats("Task")
        
        self.logger.info(f"Extracted {len(activities)} activities")
        return activities
    
    def parse_all(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Orchestrate all extractors to parse a complete Miradi project.
        
        Args:
            file_path: Path to the .xmpz2 file
            
        Returns:
            Dictionary containing all parsed project data
        """
        file_path = Path(file_path)
        self.logger.info(f"Starting to parse Miradi project: {file_path}")
        
        # Reset statistics
        self.stats = ParsingStats()
        
        try:
            # Extract .xmpz2 file
            temp_dir = self._extract_from_zip(file_path)
            
            # Find project.xml
            project_xml_path = self._find_project_xml(temp_dir)
            
            # Parse XML
            tree = ET.parse(project_xml_path)
            root = tree.getroot()
            
            # Validate required elements
            self._validate_required_elements(root)
            
            # Extract all components
            project_data = {
                'metadata': self.extract_project_metadata(root),
                'conservation_targets': self.extract_conservation_targets(root),
                'threats': self.extract_threats(root),
                'strategies': self.extract_strategies(root),
                'activities': self.extract_activities(root),
                'results_chains': self.extract_results_chains(root),
                'conceptual_models': self.extract_conceptual_models(root),
                'parsing_stats': self.stats,
                'file_info': {
                    'source_file': str(file_path),
                    'parsed_at': datetime.now().isoformat(),
                    'temp_directory': str(temp_dir)
                }
            }
            
            self.logger.info(f"Successfully parsed project with {self.stats.total_elements} elements")
            return project_data
            
        except Exception as e:
            error_msg = f"Failed to parse {file_path}: {str(e)}"
            self.logger.error(error_msg)
            self.stats.errors.append(error_msg)
            raise MiradiParsingError(error_msg) from e
    
    def get_parsing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the parsing process.
        
        Returns:
            Dictionary containing parsing statistics and summary
        """
        return {
            'total_elements': self.stats.total_elements,
            'element_breakdown': {
                'must_support': self.stats.must_support_elements,
                'should_support': self.stats.should_support_elements,
                'optional': self.stats.optional_elements,
                'edge_case': self.stats.edge_case_elements,
                'unknown': self.stats.unknown_elements
            },
            'coverage': {
                'must_support_coverage': (self.stats.must_support_elements / max(1, self.stats.total_elements)) * 100,
                'known_element_coverage': ((self.stats.total_elements - self.stats.unknown_elements) / max(1, self.stats.total_elements)) * 100
            },
            'top_elements': dict(self.stats.element_counts.most_common(10)),
            'unknown_elements': list(self.stats.unknown_element_names),
            'errors': self.stats.errors,
            'warnings': self.stats.warnings
        }


def main():
    """
    Simple main function for testing the parser.
    """
    import argparse
    import json
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Parse Miradi .xmpz2 files')
    parser.add_argument('file_path', help='Path to the .xmpz2 file to parse')
    parser.add_argument('--output', '-o', help='Output file for parsed data (JSON)')
    parser.add_argument('--unknown-handling', 
                       choices=['log', 'error', 'store', 'ignore'],
                       default='log',
                       help='How to handle unknown elements')
    parser.add_argument('--no-validation', action='store_true',
                       help='Skip schema validation')
    parser.add_argument('--summary-only', action='store_true',
                       help='Only output parsing summary')
    
    args = parser.parse_args()
    
    try:
        # Create parser
        unknown_handling = UnknownElementHandling(args.unknown_handling)
        miradi_parser = MiradiParser(
            unknown_element_handling=unknown_handling,
            validate_schema=not args.no_validation
        )
        
        # Parse the file
        logger.info(f"Parsing {args.file_path}")
        project_data = miradi_parser.parse_all(args.file_path)
        
        # Get summary
        summary = miradi_parser.get_parsing_summary()
        
        if args.summary_only:
            output_data = summary
        else:
            output_data = project_data
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=str)
            logger.info(f"Results written to {args.output}")
        else:
            print(json.dumps(output_data, indent=2, default=str))
        
        # Print summary to stderr
        print(f"\nParsing Summary:", file=sys.stderr)
        print(f"Total elements: {summary['total_elements']}", file=sys.stderr)
        print(f"Must-support elements: {summary['element_breakdown']['must_support']}", file=sys.stderr)
        print(f"Unknown elements: {summary['element_breakdown']['unknown']}", file=sys.stderr)
        print(f"Known element coverage: {summary['coverage']['known_element_coverage']:.1f}%", file=sys.stderr)
        
        if summary['unknown_elements']:
            print(f"Unknown element types: {', '.join(list(summary['unknown_elements'])[:10])}", file=sys.stderr)
        
        if summary['errors']:
            print(f"Errors: {len(summary['errors'])}", file=sys.stderr)
            for error in summary['errors']:
                print(f"  - {error}", file=sys.stderr)
    
    except Exception as e:
        logger.error(f"Failed to parse file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
