"""
Core test case generator module.

This module provides the main TestCaseGenerator class that orchestrates
the generation of test cases from various input sources.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import TestCase, Requirement, Component, Project
from .parsers.screenshots import ScreenshotParser
from .parsers.requirements import RequirementsParser
from .parsers.figma import FigmaParser
from .parsers.api_specs import APISpecParser
from .config import Config
from ..utils.logging import get_logger


class TestCaseGenerator:
    """Main test case generator class."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the test case generator.
        
        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.logger = get_logger()
        
        # Initialize parsers
        self._init_parsers()
    
    def _init_parsers(self) -> None:
        """Initialize all parsers."""
        # Screenshot parser
        screenshot_config = {
            'api_key': self.config.llm['api_key'],
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'model': self.config.llm['model'],
            'max_tokens': self.config.llm['max_tokens'],
            'temperature': self.config.llm['temperature']
        }
        self.screenshot_parser = ScreenshotParser(screenshot_config)
        
        # Requirements parser
        self.requirements_parser = RequirementsParser()
        
        # Figma parser
        figma_config = self.config.integrations.get('figma', {})
        self.figma_parser = FigmaParser(figma_config)
        
        # API specs parser
        self.api_parser = APISpecParser()
    
    def generate_from_screenshots(
        self,
        screenshots: Union[Path, List[Path]],
        test_types: Optional[List[str]] = None,
        additional_context: str = "",
        requirements: Optional[List[Requirement]] = None,
        components: Optional[List[Component]] = None
    ) -> List[TestCase]:
        """Generate test cases from screenshots.
        
        Args:
            screenshots: Screenshot file or list of screenshot files
            test_types: List of test case types to generate
            additional_context: Additional context for AI generation
            requirements: Optional requirements for context
            components: Optional components for context
            
        Returns:
            List of generated test cases
        """
        if test_types is None:
            test_types = self.config.generation['test_case_types']
        
        # Prepare context
        context = additional_context
        if requirements:
            context += f"\nRequirements context: {len(requirements)} requirements"
        if components:
            context += f"\nComponents context: {len(components)} components"
        
        # Handle single screenshot vs multiple
        if isinstance(screenshots, Path):
            screenshot_paths = [screenshots]
        else:
            screenshot_paths = screenshots
        
        # Generate test cases
        all_test_cases = []
        for screenshot_path in screenshot_paths:
            try:
                test_cases = self.screenshot_parser.generate_test_cases_from_screenshot(
                    screenshot_path,
                    test_types,
                    context
                )
                all_test_cases.extend(test_cases)
            except Exception as e:
                self.logger.error(f"Error processing screenshot {screenshot_path}: {e}")
                continue
        
        self.logger.info(f"Generated {len(all_test_cases)} test cases from {len(screenshot_paths)} screenshots")
        return all_test_cases
    
    def generate_from_requirements(
        self,
        requirements: List[Requirement],
        test_types: Optional[List[str]] = None,
        additional_context: str = ""
    ) -> List[TestCase]:
        """Generate test cases from requirements.
        
        Args:
            requirements: List of requirements
            test_types: List of test case types to generate
            additional_context: Additional context for AI generation
            
        Returns:
            List of generated test cases
        """
        if test_types is None:
            test_types = self.config.generation['test_case_types']
        
        # For now, this is a placeholder implementation
        # In a full implementation, this would use LLM to generate test cases
        # from requirements without screenshots
        
        test_cases = []
        for req in requirements:
            # Generate basic test cases for each requirement
            test_case = TestCase(
                title=f"Test {req.title}",
                test_type="FUNC",
                priority=req.priority,
                steps=[
                    f"Navigate to the {req.title} feature",
                    "Verify the feature works as expected"
                ],
                expected_result=f"{req.title} works correctly",
                covered_requirements=[req.id],
                metadata={
                    'source': 'requirements',
                    'requirement_id': req.id
                }
            )
            test_cases.append(test_case)
        
        self.logger.info(f"Generated {len(test_cases)} test cases from {len(requirements)} requirements")
        return test_cases
    
    def generate_from_components(
        self,
        components: List[Component],
        test_types: Optional[List[str]] = None,
        additional_context: str = ""
    ) -> List[TestCase]:
        """Generate test cases from components.
        
        Args:
            components: List of components
            test_types: List of test case types to generate
            additional_context: Additional context for AI generation
            
        Returns:
            List of generated test cases
        """
        if test_types is None:
            test_types = self.config.generation['test_case_types']
        
        # For now, this is a placeholder implementation
        # In a full implementation, this would use LLM to generate test cases
        # from component specifications
        
        test_cases = []
        for comp in components:
            # Generate basic test cases for each component
            test_case = TestCase(
                title=f"Test {comp.name} component",
                test_type="FUNC",
                priority="P2",
                steps=[
                    f"Navigate to {comp.screen}",
                    f"Interact with {comp.name}",
                    "Verify component behavior"
                ],
                expected_result=f"{comp.name} component works correctly",
                covered_components=[comp.id],
                metadata={
                    'source': 'components',
                    'component_id': comp.id
                }
            )
            test_cases.append(test_case)
        
        self.logger.info(f"Generated {len(test_cases)} test cases from {len(components)} components")
        return test_cases
    
    def generate_comprehensive(
        self,
        screenshots: Optional[Union[Path, List[Path]]] = None,
        requirements: Optional[List[Requirement]] = None,
        components: Optional[List[Component]] = None,
        test_types: Optional[List[str]] = None,
        additional_context: str = ""
    ) -> List[TestCase]:
        """Generate comprehensive test cases from multiple sources.
        
        Args:
            screenshots: Screenshot file or list of screenshot files
            requirements: List of requirements
            components: List of components
            test_types: List of test case types to generate
            additional_context: Additional context for AI generation
            
        Returns:
            List of generated test cases
        """
        all_test_cases = []
        
        # Generate from screenshots (primary method)
        if screenshots:
            screenshot_cases = self.generate_from_screenshots(
                screenshots, test_types, additional_context, requirements, components
            )
            all_test_cases.extend(screenshot_cases)
        
        # Generate from requirements (if no screenshots)
        if requirements and not screenshots:
            req_cases = self.generate_from_requirements(
                requirements, test_types, additional_context
            )
            all_test_cases.extend(req_cases)
        
        # Generate from components (if no screenshots)
        if components and not screenshots:
            comp_cases = self.generate_from_components(
                components, test_types, additional_context
            )
            all_test_cases.extend(comp_cases)
        
        # Remove duplicates based on title similarity
        unique_cases = self._remove_duplicate_test_cases(all_test_cases)
        
        self.logger.info(f"Generated {len(unique_cases)} unique test cases from all sources")
        return unique_cases
    
    def _remove_duplicate_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Remove duplicate test cases based on title similarity.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of unique test cases
        """
        unique_cases = []
        seen_titles = set()
        
        for tc in test_cases:
            # Simple deduplication based on title
            title_lower = tc.title.lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_cases.append(tc)
        
        return unique_cases
    
    def load_requirements_from_file(self, file_path: Union[str, Path]) -> List[Requirement]:
        """Load requirements from a file.
        
        Args:
            file_path: Path to requirements file
            
        Returns:
            List of requirements
        """
        return self.requirements_parser.extract_requirements_from_file(file_path)
    
    def load_components_from_figma(self, file_id: str) -> List[Component]:
        """Load components from Figma file.
        
        Args:
            file_id: Figma file ID
            
        Returns:
            List of components
        """
        return self.figma_parser.extract_components_from_file(file_id)
    
    def load_api_endpoints_from_spec(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Load API endpoints from specification file.
        
        Args:
            file_path: Path to API spec file
            
        Returns:
            List of API endpoints
        """
        spec = self.api_parser.parse_api_spec(file_path)
        return self.api_parser.extract_endpoints(spec)
