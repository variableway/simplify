"""
Simple requirements parser for basic text input.

This module provides basic functionality to parse simple text requirements
and convert them to Requirement objects for test case generation.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...utils.logging import get_logger, log_file_operation
from ...utils.validators import validate_file_path
from ..models import Requirement, Priority


class RequirementsParser:
    """Simple parser for extracting requirements from text files."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the requirements parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger()
        
        # Priority keywords mapping
        self.priority_keywords = {
            'must': Priority.P0,
            'required': Priority.P0,
            'critical': Priority.P0,
            'should': Priority.P1,
            'important': Priority.P1,
            'could': Priority.P2,
            'optional': Priority.P2,
            'nice to have': Priority.P3,
            'won\'t': Priority.P3,
            'will not': Priority.P3
        }
        
        # Requirement ID patterns
        self.id_patterns = [
            r'REQ-\d+',
            r'REQ_\w+_\d+',
            r'REQ\w+\d+',
            r'R-\d+',
            r'REQUIREMENT-\d+'
        ]
    
    def extract_requirements_from_text(self, text: str) -> List[Requirement]:
        """Extract requirements from plain text.
        
        Args:
            text: Input text containing requirements
            
        Returns:
            List of Requirement objects
        """
        requirements = []
        lines = text.split('\n')
        
        current_req = {}
        current_description = []
        in_description = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line:
                continue
            
            # Check if line starts a new requirement
            req_id = self._extract_requirement_id(line)
            if req_id:
                # Save previous requirement if exists
                if current_req and current_description:
                    req = self._create_requirement_from_dict(current_req, current_description)
                    if req:
                        requirements.append(req)
                
                # Start new requirement
                current_req = {'id': req_id, 'line_number': line_num}
                current_description = [line]
                in_description = True
                
            elif in_description and line:
                current_description.append(line)
            
            # Check for end of requirement (empty line or new requirement)
            elif in_description and not line:
                in_description = False
        
        # Add the last requirement
        if current_req and current_description:
            req = self._create_requirement_from_dict(current_req, current_description)
            if req:
                requirements.append(req)
        
        self.logger.info(f"Extracted {len(requirements)} requirements from text")
        return requirements
    
    def extract_requirements_from_file(self, file_path: Union[str, Path]) -> List[Requirement]:
        """Extract requirements from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of Requirement objects
        """
        file_path = Path(file_path)
        
        if not validate_file_path(file_path, must_exist=True):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            log_file_operation("read_requirements", str(file_path), success=True)
            return self.extract_requirements_from_text(text)
            
        except Exception as e:
            log_file_operation("read_requirements", str(file_path), success=False)
            self.logger.error(f"Error reading requirements file {file_path}: {e}")
            raise
    
    def _extract_requirement_id(self, line: str) -> Optional[str]:
        """Extract requirement ID from a line.
        
        Args:
            line: Input line
            
        Returns:
            Requirement ID if found, None otherwise
        """
        for pattern in self.id_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group()
        return None
    
    def _extract_priority(self, text: str) -> Priority:
        """Extract priority from text.
        
        Args:
            text: Input text
            
        Returns:
            Priority level
        """
        text_lower = text.lower()
        
        for keyword, priority in self.priority_keywords.items():
            if keyword in text_lower:
                return priority
        
        # Default to P2 if no priority found
        return Priority.P2
    
    def _extract_title(self, lines: List[str]) -> str:
        """Extract title from requirement lines.
        
        Args:
            lines: List of requirement lines
            
        Returns:
            Extracted title
        """
        if not lines:
            return "Untitled Requirement"
        
        # Use first line as title, clean it up
        title = lines[0]
        
        # Remove requirement ID if present
        for pattern in self.id_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE).strip()
        
        # Remove common prefixes
        title = re.sub(r'^(requirement|req|spec|specification):\s*', '', title, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title or "Untitled Requirement"
    
    def _create_requirement_from_dict(self, req_dict: Dict[str, Any], description_lines: List[str]) -> Optional[Requirement]:
        """Create a Requirement object from parsed dictionary.
        
        Args:
            req_dict: Dictionary with requirement data
            description_lines: List of description lines
            
        Returns:
            Requirement object or None if invalid
        """
        try:
            # Extract title
            title = self._extract_title(description_lines)
            
            # Extract priority
            full_text = ' '.join(description_lines)
            priority = self._extract_priority(full_text)
            
            # Create description (join all lines)
            description = ' '.join(description_lines)
            
            return Requirement(
                id=req_dict['id'],
                title=title,
                description=description,
                priority=priority,
                source='text_file',
                metadata={
                    'line_number': req_dict.get('line_number'),
                    'original_text': description
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating requirement from dict: {e}")
            return None
    
    def parse_simple_requirements(self, requirements_text: str) -> List[Requirement]:
        """Parse simple requirements from text input.
        
        This is a simplified version that creates requirements from basic text input
        without requiring specific formatting.
        
        Args:
            requirements_text: Text containing requirements
            
        Returns:
            List of Requirement objects
        """
        requirements = []
        lines = requirements_text.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Create a simple requirement
            req_id = f"REQ-{i:03d}"
            priority = self._extract_priority(line)
            
            requirement = Requirement(
                id=req_id,
                title=line[:100] + "..." if len(line) > 100 else line,
                description=line,
                priority=priority,
                source='manual_input',
                metadata={
                    'line_number': i,
                    'original_text': line
                }
            )
            
            requirements.append(requirement)
        
        self.logger.info(f"Parsed {len(requirements)} simple requirements")
        return requirements
