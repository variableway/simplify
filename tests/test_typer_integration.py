"""
Test Typer integration and CLI functionality.

This module tests the Typer-based CLI integration.
"""

import pytest
from typer.testing import CliRunner
from pathlib import Path

from src.testcase_generator.cli.main import app
from src.testcase_generator.core.config import Config
from src.testcase_generator.core.generator import TestCaseGenerator
from src.testcase_generator.core.project import ProjectManager


class TestTyperIntegration:
    """Test Typer CLI integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_app_help(self):
        """Test that the app shows help."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Test Case Generator" in result.output
    
    def test_generate_help(self):
        """Test generate command help."""
        result = self.runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate test cases from screenshots" in result.output
    
    def test_analyze_help(self):
        """Test analyze command help."""
        result = self.runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze test coverage" in result.output
    
    def test_export_help(self):
        """Test export command help."""
        result = self.runner.invoke(app, ["export", "--help"])
        assert result.exit_code == 0
        assert "Export test cases" in result.output
    
    def test_manage_help(self):
        """Test manage command help."""
        result = self.runner.invoke(app, ["manage", "--help"])
        assert result.exit_code == 0
        assert "项目管理命令组" in result.output
    
    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Test Case Generator v" in result.output
    
    def test_config_command(self):
        """Test config command."""
        result = self.runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Current Configuration" in result.output
    
    def test_generate_without_screenshots(self):
        """Test generate command without required screenshots."""
        result = self.runner.invoke(app, ["generate"])
        assert result.exit_code == 1
        assert "Screenshots are required" in result.output
    
    def test_generate_dry_run(self):
        """Test generate command with dry run."""
        # Create a dummy screenshot file for testing
        test_image = Path("test_data/img/1.png")
        if test_image.exists():
            result = self.runner.invoke(app, ["generate", "-s", str(test_image), "--dry-run"])
            assert result.exit_code == 0
            assert "Dry run mode" in result.output


class TestCoreModules:
    """Test core modules integration."""
    
    def test_config_creation(self):
        """Test Config class creation."""
        config = Config()
        assert config is not None
        assert config.project_name == "Test Case Generator"
        assert config.llm is not None
    
    def test_generator_creation(self):
        """Test TestCaseGenerator creation."""
        config = Config()
        generator = TestCaseGenerator(config)
        assert generator is not None
        assert generator.config is not None
    
    def test_project_manager_creation(self):
        """Test ProjectManager creation."""
        config = Config()
        manager = ProjectManager(config)
        assert manager is not None
        assert manager.config is not None
    
    def test_project_creation(self):
        """Test project creation."""
        config = Config()
        manager = ProjectManager(config)
        
        project = manager.create_project(
            name="Test Project",
            description="A test project"
        )
        
        assert project is not None
        assert project.name == "Test Project"
        assert project.description == "A test project"
    
    def test_project_summary(self):
        """Test project summary generation."""
        config = Config()
        manager = ProjectManager(config)
        
        project = manager.create_project("Test Project")
        summary = manager.get_project_summary(project)
        
        assert summary is not None
        assert summary['name'] == "Test Project"
        assert 'requirements_count' in summary
        assert 'components_count' in summary
        assert 'test_cases_count' in summary


class TestCLICommands:
    """Test individual CLI commands."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_manage_create_project(self):
        """Test manage create-project command."""
        result = self.runner.invoke(app, [
            "manage", "create-project", 
            "--name", "Test Project",
            "--description", "A test project"
        ])
        assert result.exit_code == 0
        assert "项目创建完成" in result.output
    
    def test_manage_show_project(self):
        """Test manage show-project command."""
        result = self.runner.invoke(app, ["manage", "show-project"])
        assert result.exit_code == 0
        assert "项目信息" in result.output
    
    def test_manage_list_test_cases(self):
        """Test manage list-test-cases command."""
        result = self.runner.invoke(app, ["manage", "list-test-cases"])
        assert result.exit_code == 0
        assert "Test Cases" in result.output
    
    def test_manage_backup(self):
        """Test manage backup command."""
        result = self.runner.invoke(app, ["manage", "backup"])
        assert result.exit_code == 0
        assert "Backup completed" in result.output
    
    def test_manage_cleanup(self):
        """Test manage cleanup command."""
        result = self.runner.invoke(app, ["manage", "cleanup", "--dry-run"])
        assert result.exit_code == 0
        assert "Files that would be cleaned" in result.output


if __name__ == "__main__":
    pytest.main([__file__])
