"""
Basic structure tests for the Test Case Generator.

This module tests the basic functionality of the core components.
"""

import pytest
from pathlib import Path

from src.testcase_generator.core.models import (
    Requirement, Component, TestCase, TestSuite, Project,
    Priority, TestCaseType, ComponentType
)
from src.testcase_generator.utils.config import Config, load_config
from src.testcase_generator.utils.logging import get_logger
from src.testcase_generator.utils.validators import validate_requirement_id, validate_priority


class TestDomainModels:
    """Test domain models functionality."""
    
    def test_requirement_creation(self):
        """Test requirement model creation."""
        req = Requirement(
            id="REQ-001",
            title="User Login",
            description="Users must be able to log in with valid credentials",
            priority=Priority.P0,
            source="Confluence"
        )
        
        assert req.id == "REQ-001"
        assert req.title == "User Login"
        assert req.priority == Priority.P0
        assert req.source == "Confluence"
    
    def test_component_creation(self):
        """Test component model creation."""
        comp = Component(
            id="CMP-001",
            name="Login Button",
            component_type=ComponentType.BUTTON,
            screen="Login Page",
            source="Figma"
        )
        
        assert comp.id == "CMP-001"
        assert comp.name == "Login Button"
        assert comp.component_type == ComponentType.BUTTON
        assert comp.screen == "Login Page"
    
    def test_test_case_creation(self):
        """Test test case model creation."""
        tc = TestCase(
            title="Valid Login Test",
            test_type=TestCaseType.FUNC,
            priority=Priority.P0,
            steps=["Open login page", "Enter valid credentials", "Click login"],
            expected_result="User is logged in successfully"
        )
        
        assert tc.title == "Valid Login Test"
        assert tc.test_type == TestCaseType.FUNC
        assert tc.priority == Priority.P0
        assert len(tc.steps) == 3
    
    def test_project_creation(self):
        """Test project model creation."""
        project = Project(
            name="Test Project",
            description="A test project"
        )
        
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert len(project.requirements) == 0
        assert len(project.components) == 0


class TestConfiguration:
    """Test configuration functionality."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        
        assert config.project_name == "Test Case Generator"
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"
        assert config.generation.max_cases_per_requirement == 10
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        issues = config.validate_config()
        
        # Should have issues about missing API key
        assert len(issues) > 0
        assert any("API key" in issue for issue in issues)


class TestValidators:
    """Test validation functionality."""
    
    def test_requirement_id_validation(self):
        """Test requirement ID validation."""
        assert validate_requirement_id("REQ-001") == True
        assert validate_requirement_id("REQ_USER_001") == True
        assert validate_requirement_id("invalid") == False
        assert validate_requirement_id("") == False
    
    def test_priority_validation(self):
        """Test priority validation."""
        assert validate_priority("P0") == True
        assert validate_priority("P1") == True
        assert validate_priority("P2") == True
        assert validate_priority("P3") == True
        assert validate_priority("INVALID") == False


class TestLogging:
    """Test logging functionality."""
    
    def test_logger_creation(self):
        """Test logger creation."""
        logger = get_logger()
        assert logger is not None
        assert logger.name == "testcase_generator"
    
    def test_logger_methods(self):
        """Test logger methods."""
        logger = get_logger()
        
        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")


class TestProjectStructure:
    """Test project structure and imports."""
    
    def test_core_imports(self):
        """Test core module imports."""
        from src.testcase_generator.core import models
        from src.testcase_generator.core.models import Requirement, Component, TestCase
        
        assert models is not None
        assert Requirement is not None
        assert Component is not None
        assert TestCase is not None
    
    def test_utils_imports(self):
        """Test utils module imports."""
        from src.testcase_generator.utils import config, logging, validators
        from src.testcase_generator.utils.config import Config
        from src.testcase_generator.utils.logging import get_logger
        from src.testcase_generator.utils.validators import validate_requirement_id
        
        assert config is not None
        assert logging is not None
        assert validators is not None
        assert Config is not None
        assert get_logger is not None
        assert validate_requirement_id is not None
    
    def test_cli_imports(self):
        """Test CLI module imports."""
        from src.testcase_generator.cli import main
        from src.testcase_generator.cli.main import cli
        
        assert main is not None
        assert cli is not None


if __name__ == "__main__":
    pytest.main([__file__])
