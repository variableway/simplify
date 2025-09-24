"""
Project management module for the Test Case Generator.

This module provides the ProjectManager class for managing projects,
test cases, and related data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import Project, TestCase, Requirement, Component, TestSuite
from .config import Config
from ..utils.logging import get_logger


class ProjectManager:
    """Project manager for handling projects and test cases."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the project manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.logger = get_logger()
        self.current_project: Optional[Project] = None
    
    def create_project(
        self,
        name: str,
        description: str = "",
        created_by: Optional[str] = None
    ) -> Project:
        """Create a new project.
        
        Args:
            name: Project name
            description: Project description
            created_by: Creator of the project
            
        Returns:
            Created project
        """
        project = Project(
            name=name,
            description=description,
            created_by=created_by
        )
        
        self.current_project = project
        self.logger.info(f"Created new project: {name}")
        return project
    
    def load_project(self, file_path: Union[str, Path]) -> Project:
        """Load project from file.
        
        Args:
            file_path: Path to project file
            
        Returns:
            Loaded project
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Project file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert dict to Project object
            project = Project(**data)
            self.current_project = project
            
            self.logger.info(f"Loaded project: {project.name}")
            return project
            
        except Exception as e:
            self.logger.error(f"Error loading project from {file_path}: {e}")
            raise
    
    def save_project(self, project: Optional[Project] = None, file_path: Optional[Union[str, Path]] = None) -> Path:
        """Save project to file.
        
        Args:
            project: Project to save (uses current project if None)
            file_path: Path to save project (auto-generated if None)
            
        Returns:
            Path where project was saved
        """
        project = project or self.current_project
        if not project:
            raise ValueError("No project to save")
        
        if not file_path:
            # Auto-generate filename
            safe_name = project.name.replace(' ', '_').lower()
            file_path = Path(self.config.output_dir) / f"{safe_name}_project.json"
        else:
            file_path = Path(file_path)
        
        # Ensure output directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project.dict(), f, indent=2, default=str)
            
            self.logger.info(f"Saved project to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error saving project to {file_path}: {e}")
            raise
    
    def add_test_cases(self, test_cases: List[TestCase], project: Optional[Project] = None) -> None:
        """Add test cases to project.
        
        Args:
            test_cases: List of test cases to add
            project: Project to add to (uses current project if None)
        """
        project = project or self.current_project
        if not project:
            raise ValueError("No project to add test cases to")
        
        # Create a test suite for the new test cases
        suite = TestSuite(
            name=f"Generated Test Cases - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=f"Auto-generated test cases from screenshots",
            test_cases=[tc.id for tc in test_cases],
            created_by="testcase_generator"
        )
        
        project.test_suites.append(suite)
        
        # Update project metadata
        project.updated_at = datetime.utcnow()
        
        self.logger.info(f"Added {len(test_cases)} test cases to project {project.name}")
    
    def add_requirements(self, requirements: List[Requirement], project: Optional[Project] = None) -> None:
        """Add requirements to project.
        
        Args:
            requirements: List of requirements to add
            project: Project to add to (uses current project if None)
        """
        project = project or self.current_project
        if not project:
            raise ValueError("No project to add requirements to")
        
        project.requirements.extend(requirements)
        project.updated_at = datetime.utcnow()
        
        self.logger.info(f"Added {len(requirements)} requirements to project {project.name}")
    
    def add_components(self, components: List[Component], project: Optional[Project] = None) -> None:
        """Add components to project.
        
        Args:
            components: List of components to add
            project: Project to add to (uses current project if None)
        """
        project = project or self.current_project
        if not project:
            raise ValueError("No project to add components to")
        
        project.components.extend(components)
        project.updated_at = datetime.utcnow()
        
        self.logger.info(f"Added {len(components)} components to project {project.name}")
    
    def get_all_test_cases(self, project: Optional[Project] = None) -> List[TestCase]:
        """Get all test cases from project.
        
        Args:
            project: Project to get test cases from (uses current project if None)
            
        Returns:
            List of all test cases
        """
        project = project or self.current_project
        if not project:
            return []
        
        # In a real implementation, you would fetch test cases by ID
        # For now, return empty list as we don't have a database
        return []
    
    def get_project_summary(self, project: Optional[Project] = None) -> Dict[str, Any]:
        """Get project summary statistics.
        
        Args:
            project: Project to summarize (uses current project if None)
            
        Returns:
            Project summary dictionary
        """
        project = project or self.current_project
        if not project:
            return {}
        
        return {
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            'created_by': project.created_by,
            'requirements_count': len(project.requirements),
            'components_count': len(project.components),
            'flows_count': len(project.flows),
            'test_suites_count': len(project.test_suites),
            'test_cases_count': sum(len(suite.test_cases) for suite in project.test_suites)
        }
    
    def export_test_cases(
        self,
        project: Optional[Project] = None,
        output_format: str = "json",
        output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """Export test cases from project.
        
        Args:
            project: Project to export from (uses current project if None)
            output_format: Export format (json, csv, excel)
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path where test cases were exported
        """
        project = project or self.current_project
        if not project:
            raise ValueError("No project to export from")
        
        if not output_path:
            safe_name = project.name.replace(' ', '_').lower()
            output_path = Path(self.config.output_dir) / f"{safe_name}_test_cases.{output_format}"
        else:
            output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get all test cases
        test_cases = self.get_all_test_cases(project)
        
        if output_format == "json":
            self._export_to_json(test_cases, output_path)
        elif output_format == "csv":
            self._export_to_csv(test_cases, output_path)
        elif output_format == "excel":
            self._export_to_excel(test_cases, output_path)
        else:
            raise ValueError(f"Unsupported export format: {output_format}")
        
        self.logger.info(f"Exported {len(test_cases)} test cases to {output_path}")
        return output_path
    
    def _export_to_json(self, test_cases: List[TestCase], output_path: Path) -> None:
        """Export test cases to JSON format."""
        data = {
            'test_cases': [tc.dict() for tc in test_cases],
            'exported_at': datetime.utcnow().isoformat(),
            'count': len(test_cases)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _export_to_csv(self, test_cases: List[TestCase], output_path: Path) -> None:
        """Export test cases to CSV format."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not test_cases:
                return
            
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'ID', 'Title', 'Type', 'Priority', 'Preconditions', 
                'Steps', 'Expected Result', 'Covered Requirements', 'Covered Components'
            ])
            
            # Write test cases
            for tc in test_cases:
                writer.writerow([
                    tc.id,
                    tc.title,
                    tc.test_type,
                    tc.priority,
                    '; '.join(tc.preconditions),
                    '; '.join(tc.steps),
                    tc.expected_result,
                    '; '.join(tc.covered_requirements),
                    '; '.join(tc.covered_components)
                ])
    
    def _export_to_excel(self, test_cases: List[TestCase], output_path: Path) -> None:
        """Export test cases to Excel format."""
        try:
            import pandas as pd
            
            if not test_cases:
                return
            
            # Convert test cases to DataFrame
            data = []
            for tc in test_cases:
                data.append({
                    'ID': tc.id,
                    'Title': tc.title,
                    'Type': tc.test_type,
                    'Priority': tc.priority,
                    'Preconditions': '; '.join(tc.preconditions),
                    'Steps': '; '.join(tc.steps),
                    'Expected Result': tc.expected_result,
                    'Covered Requirements': '; '.join(tc.covered_requirements),
                    'Covered Components': '; '.join(tc.covered_components),
                    'Created At': tc.created_at,
                    'Updated At': tc.updated_at
                })
            
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False, sheet_name='Test Cases')
            
        except ImportError:
            self.logger.error("pandas not available for Excel export, falling back to CSV")
            self._export_to_csv(test_cases, output_path.with_suffix('.csv'))
    
    def list_projects(self, projects_dir: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """List available projects.
        
        Args:
            projects_dir: Directory to search for projects (uses output_dir if None)
            
        Returns:
            List of project information dictionaries
        """
        if not projects_dir:
            projects_dir = Path(self.config.output_dir)
        else:
            projects_dir = Path(projects_dir)
        
        if not projects_dir.exists():
            return []
        
        projects = []
        for project_file in projects_dir.glob("*_project.json"):
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                projects.append({
                    'name': data.get('name', 'Unknown'),
                    'file_path': str(project_file),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'requirements_count': len(data.get('requirements', [])),
                    'components_count': len(data.get('components', [])),
                    'test_suites_count': len(data.get('test_suites', []))
                })
            except Exception as e:
                self.logger.error(f"Error reading project file {project_file}: {e}")
                continue
        
        return projects
