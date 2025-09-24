"""
Test Case Generator - A comprehensive tool for generating test cases from requirements, prototypes, and screenshots.

This package provides a complete solution for test case generation following a 9-layer architecture:
1. Collection Layer: Requirements, prototypes, API specs, screenshots
2. Parsing Layer: Text parsing, prototype parsing, OCR
3. Semantic Modeling Layer: Unified domain model
4. Generation Layer: LLM + rule engine for test case generation
5. Gap Analysis Layer: Coverage matrix, constraint coverage, parameter combinations
6. Management Layer: Test case library, versioning, execution records
7. Collaboration Layer: Task assignment, progress tracking
8. Integration Layer: Jira, TestRail, Git, Slack, CI
9. Metrics & Feedback Layer: Defect analysis, coverage metrics
"""

__version__ = "0.1.0"
__author__ = "DamnPatrick"

from .core.models import (
    Requirement,
    Component,
    TestCase,
    TestSuite,
    Project,
    Constraint,
    Flow,
    CoverageMatrix,
)

from .cli.main import cli

__all__ = [
    "Requirement",
    "Component", 
    "TestCase",
    "TestSuite",
    "Project",
    "Constraint",
    "Flow",
    "CoverageMatrix",
    "cli",
]
