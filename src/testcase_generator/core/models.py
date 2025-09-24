"""
Domain models for the Test Case Generator.

This module defines the core data structures used throughout the application:
- Requirements and their properties
- UI components and constraints
- Test cases and test suites
- Projects and coverage matrices
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class Priority(str, Enum):
    """Priority levels for requirements and test cases."""
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low


class TestCaseType(str, Enum):
    """Types of test cases."""
    FUNC = "FUNC"      # Functional
    BOUND = "BOUND"    # Boundary value
    NEG = "NEG"        # Negative
    PERM = "PERM"      # Permission/Authorization
    SEC = "SEC"        # Security
    PERF = "PERF"      # Performance
    A11Y = "A11Y"      # Accessibility


class ComponentType(str, Enum):
    """Types of UI components."""
    BUTTON = "button"
    INPUT = "input"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    MODAL = "modal"
    CARD = "card"
    NAVIGATION = "navigation"


class ConstraintType(str, Enum):
    """Types of constraints that can be applied to components."""
    REQUIRED = "required"
    MAX_LENGTH = "max_length"
    MIN_LENGTH = "min_length"
    PATTERN = "pattern"
    ENUM = "enum"
    RANGE = "range"
    UNIQUE = "unique"
    DEPENDENCY = "dependency"


class Requirement(BaseModel):
    """A requirement that needs to be tested."""
    id: str = Field(..., description="Unique requirement identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed requirement description")
    priority: Priority = Field(..., description="Requirement priority")
    source: str = Field(..., description="Source of the requirement (e.g., 'Confluence', 'Figma')")
    source_id: Optional[str] = Field(None, description="ID in the source system")
    version: str = Field(default="1.0", description="Requirement version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Requirement tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


class Constraint(BaseModel):
    """A constraint applied to a component or field."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    target_type: str = Field(..., description="Type of target (field, component)")
    target_id: str = Field(..., description="ID of the target")
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Constraint parameters")
    description: Optional[str] = Field(None, description="Human-readable description")

    class Config:
        use_enum_values = True


class Component(BaseModel):
    """A UI component that can be tested."""
    id: str = Field(..., description="Unique component identifier")
    name: str = Field(..., description="Component name")
    component_type: ComponentType = Field(..., description="Type of component")
    screen: str = Field(..., description="Screen or page where component appears")
    description: Optional[str] = Field(None, description="Component description")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Component properties")
    constraints: List[Constraint] = Field(default_factory=list, description="Component constraints")
    source: str = Field(..., description="Source of the component (e.g., 'Figma', 'Screenshot')")
    source_id: Optional[str] = Field(None, description="ID in the source system")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


class Flow(BaseModel):
    """A user flow or workflow."""
    id: str = Field(..., description="Unique flow identifier")
    name: str = Field(..., description="Flow name")
    description: Optional[str] = Field(None, description="Flow description")
    steps: List[str] = Field(..., description="List of step descriptions")
    related_requirements: List[str] = Field(default_factory=list, description="Related requirement IDs")
    related_components: List[str] = Field(default_factory=list, description="Related component IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TestCase(BaseModel):
    """A test case."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="Test case title")
    description: Optional[str] = Field(None, description="Test case description")
    test_type: TestCaseType = Field(..., description="Type of test case")
    priority: Priority = Field(..., description="Test case priority")
    preconditions: List[str] = Field(default_factory=list, description="Preconditions")
    steps: List[str] = Field(..., description="Test steps")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data for the test")
    expected_result: str = Field(..., description="Expected result")
    covered_requirements: List[str] = Field(default_factory=list, description="Covered requirement IDs")
    covered_components: List[str] = Field(default_factory=list, description="Covered component IDs")
    covered_flows: List[str] = Field(default_factory=list, description="Covered flow IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator of the test case")
    status: str = Field(default="draft", description="Test case status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True

    @validator('steps')
    def steps_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Test case must have at least one step')
        return v


class TestSuite(BaseModel):
    """A collection of test cases."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Test suite name")
    description: Optional[str] = Field(None, description="Test suite description")
    test_cases: List[str] = Field(default_factory=list, description="Test case IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator of the test suite")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Project(BaseModel):
    """A project containing requirements, components, and test cases."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    requirements: List[Requirement] = Field(default_factory=list, description="Project requirements")
    components: List[Component] = Field(default_factory=list, description="Project components")
    flows: List[Flow] = Field(default_factory=list, description="Project flows")
    test_suites: List[TestSuite] = Field(default_factory=list, description="Project test suites")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Project creator")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def get_all_test_cases(self) -> List[TestCase]:
        """Get all test cases from all test suites in the project."""
        all_test_cases = []
        for suite in self.test_suites:
            # In a real implementation, you would fetch test cases by ID
            # For now, we'll return an empty list
            pass
        return all_test_cases


class CoverageMatrix(BaseModel):
    """Coverage matrix showing which requirements are covered by which test cases."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str = Field(..., description="Project ID")
    requirement_id: str = Field(..., description="Requirement ID")
    test_case_ids: List[str] = Field(default_factory=list, description="Test case IDs covering this requirement")
    coverage_percentage: float = Field(..., description="Coverage percentage (0-100)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('coverage_percentage')
    def coverage_must_be_valid(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Coverage percentage must be between 0 and 100')
        return v


class GapAnalysis(BaseModel):
    """Results of gap analysis showing missing test coverage."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str = Field(..., description="Project ID")
    analysis_type: str = Field(..., description="Type of gap analysis")
    uncovered_requirements: List[str] = Field(default_factory=list, description="Uncovered requirement IDs")
    uncovered_components: List[str] = Field(default_factory=list, description="Uncovered component IDs")
    uncovered_constraints: List[str] = Field(default_factory=list, description="Uncovered constraint IDs")
    missing_flows: List[str] = Field(default_factory=list, description="Missing flow IDs")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TestExecution(BaseModel):
    """Record of test case execution."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    test_case_id: str = Field(..., description="Test case ID")
    execution_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(..., description="Execution status (passed, failed, blocked, skipped)")
    executed_by: Optional[str] = Field(None, description="Person who executed the test")
    execution_notes: Optional[str] = Field(None, description="Execution notes")
    defects: List[str] = Field(default_factory=list, description="Related defect IDs")
    duration_seconds: Optional[int] = Field(None, description="Execution duration in seconds")
    environment: Optional[str] = Field(None, description="Test environment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
