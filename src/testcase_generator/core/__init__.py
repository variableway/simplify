"""
Core module containing domain models, parsers, generators, and analyzers.

This module implements the core business logic of the test case generator:
- Domain models for requirements, components, test cases
- Parsers for different input formats
- Generators for creating test cases
- Analyzers for gap analysis and coverage
"""

from .models import *
from .parsers import *
from .generators import *
from .analyzers import *

__all__ = [
    # Models
    "Requirement",
    "Component",
    "TestCase",
    "TestSuite", 
    "Project",
    "Constraint",
    "Flow",
    "CoverageMatrix",
    # Parsers
    "RequirementsParser",
    "FigmaParser",
    "ScreenshotParser",
    "APISpecParser",
    # Generators
    "LLMGenerator",
    "RuleEngine",
    "PromptTemplates",
    # Analyzers
    "CoverageAnalyzer",
    "GapAnalyzer",
    "ConstraintAnalyzer",
]
