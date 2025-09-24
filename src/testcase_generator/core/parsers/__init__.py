"""
Parsers module for extracting data from various input sources.

This module contains parsers for:
- Requirements documents (Confluence, Word, PDF, plain text)
- Figma prototypes and designs
- Screenshots and images (OCR)
- API specifications (OpenAPI/Swagger)
"""

from .requirements import RequirementsParser
from .figma import FigmaParser
from .screenshots import ScreenshotParser
from .api_specs import APISpecParser

__all__ = [
    "RequirementsParser",
    "FigmaParser", 
    "ScreenshotParser",
    "APISpecParser",
]
