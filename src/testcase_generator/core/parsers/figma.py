"""
Simple Figma parser for extracting basic component information.

This module provides basic functionality to extract components from Figma files
using the Figma API and convert them to Component objects.
"""

import requests
from typing import Any, Dict, List, Optional, Union

from ...utils.logging import get_logger, log_api_call
from ..models import Component, ComponentType, Constraint, ConstraintType


class FigmaParser:
    """Simple parser for extracting components from Figma files."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Figma parser.
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config or {}
        self.logger = get_logger()
        
        # Figma API configuration
        self.api_key = self.config.get('api_key')
        self.base_url = 'https://api.figma.com/v1'
        
        # Component type mapping
        self.component_mapping = {
            'RECTANGLE': ComponentType.BUTTON,
            'TEXT': ComponentType.INPUT,
            'COMPONENT': ComponentType.BUTTON,
            'COMPONENT_SET': ComponentType.DROPDOWN,
            'FRAME': ComponentType.CARD,
            'GROUP': ComponentType.CARD,
            'INSTANCE': ComponentType.BUTTON,
        }
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get basic file information from Figma.
        
        Args:
            file_id: Figma file ID
            
        Returns:
            File information dictionary
            
        Raises:
            requests.RequestException: If API call fails
            ValueError: If API key is not configured
        """
        if not self.api_key:
            raise ValueError("Figma API key not configured")
        
        url = f"{self.base_url}/files/{file_id}"
        headers = {"X-Figma-Token": self.api_key}
        
        try:
            log_api_call("Figma", url, "GET")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            log_api_call("Figma", url, "GET", response.status_code)
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Figma API call failed: {e}")
            raise
    
    def extract_components_from_file(self, file_id: str) -> List[Component]:
        """Extract components from a Figma file.
        
        Args:
            file_id: Figma file ID
            
        Returns:
            List of Component objects
        """
        try:
            self.logger.info(f"Extracting components from Figma file: {file_id}")
            
            # Get file information
            file_info = self.get_file_info(file_id)
            
            # Extract components from document
            components = []
            document = file_info.get('document', {})
            
            if 'children' in document:
                components.extend(self._extract_components_from_node(document, file_id))
            
            self.logger.info(f"Extracted {len(components)} components from Figma file")
            return components
            
        except Exception as e:
            self.logger.error(f"Error extracting components from Figma file: {e}")
            raise
    
    def _extract_components_from_node(self, node: Dict[str, Any], file_id: str, screen: str = "Main") -> List[Component]:
        """Recursively extract components from a Figma node.
        
        Args:
            node: Figma node dictionary
            file_id: Figma file ID
            screen: Current screen name
            
        Returns:
            List of Component objects
        """
        components = []
        
        # Check if this node is a component
        if self._is_component_node(node):
            component = self._create_component_from_node(node, file_id, screen)
            if component:
                components.append(component)
        
        # Process children
        if 'children' in node:
            for child in node['children']:
                # Update screen name if this is a frame/page
                child_screen = screen
                if child.get('type') in ['FRAME', 'PAGE']:
                    child_screen = child.get('name', screen)
                
                components.extend(self._extract_components_from_node(child, file_id, child_screen))
        
        return components
    
    def _is_component_node(self, node: Dict[str, Any]) -> bool:
        """Check if a node represents a component.
        
        Args:
            node: Figma node dictionary
            
        Returns:
            True if node is a component
        """
        node_type = node.get('type', '')
        
        # Check if it's a component type
        if node_type in self.component_mapping:
            return True
        
        # Check if it has component-like properties
        if 'name' in node and node['name']:
            name_lower = node['name'].lower()
            component_keywords = ['button', 'input', 'field', 'dropdown', 'select', 'checkbox', 'radio', 'link']
            if any(keyword in name_lower for keyword in component_keywords):
                return True
        
        return False
    
    def _create_component_from_node(self, node: Dict[str, Any], file_id: str, screen: str) -> Optional[Component]:
        """Create a Component object from a Figma node.
        
        Args:
            node: Figma node dictionary
            file_id: Figma file ID
            screen: Screen name
            
        Returns:
            Component object or None if invalid
        """
        try:
            # Extract basic information
            node_id = node.get('id', '')
            name = node.get('name', 'Unnamed Component')
            node_type = node.get('type', '')
            
            # Map to component type
            component_type = self.component_mapping.get(node_type, ComponentType.BUTTON)
            
            # Extract properties
            properties = self._extract_node_properties(node)
            
            # Extract constraints
            constraints = self._extract_constraints(node)
            
            # Create component
            component = Component(
                id=f"FIGMA-{node_id}",
                name=name,
                component_type=component_type,
                screen=screen,
                description=f"Component extracted from Figma file {file_id}",
                properties=properties,
                constraints=constraints,
                source='figma',
                source_id=node_id,
                metadata={
                    'figma_file_id': file_id,
                    'figma_node_id': node_id,
                    'figma_type': node_type,
                    'original_node': node
                }
            )
            
            return component
            
        except Exception as e:
            self.logger.error(f"Error creating component from node: {e}")
            return None
    
    def _extract_node_properties(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract properties from a Figma node.
        
        Args:
            node: Figma node dictionary
            
        Returns:
            Properties dictionary
        """
        properties = {}
        
        # Extract size information
        if 'absoluteBoundingBox' in node:
            bbox = node['absoluteBoundingBox']
            properties['width'] = bbox.get('width', 0)
            properties['height'] = bbox.get('height', 0)
            properties['x'] = bbox.get('x', 0)
            properties['y'] = bbox.get('y', 0)
        
        # Extract text content if it's a text node
        if node.get('type') == 'TEXT' and 'characters' in node:
            properties['text'] = node['characters']
        
        # Extract fill color if available
        if 'fills' in node and node['fills']:
            fill = node['fills'][0]
            if 'color' in fill:
                color = fill['color']
                properties['fill_color'] = {
                    'r': color.get('r', 0),
                    'g': color.get('g', 0),
                    'b': color.get('b', 0),
                    'a': color.get('a', 1)
                }
        
        # Extract other relevant properties
        if 'visible' in node:
            properties['visible'] = node['visible']
        
        if 'locked' in node:
            properties['locked'] = node['locked']
        
        return properties
    
    def _extract_constraints(self, node: Dict[str, Any]) -> List[Constraint]:
        """Extract constraints from a Figma node.
        
        Args:
            node: Figma node dictionary
            
        Returns:
            List of Constraint objects
        """
        constraints = []
        
        # Extract text length constraints for text nodes
        if node.get('type') == 'TEXT' and 'style' in node:
            style = node['style']
            
            # Check for character limits
            if 'textCase' in style:
                constraints.append(Constraint(
                    target_type='field',
                    target_id=node.get('id', ''),
                    constraint_type=ConstraintType.PATTERN,
                    parameters={'pattern': 'text_case', 'value': style['textCase']},
                    description=f"Text case: {style['textCase']}"
                ))
        
        # Extract size constraints
        if 'absoluteBoundingBox' in node:
            bbox = node['absoluteBoundingBox']
            width = bbox.get('width', 0)
            height = bbox.get('height', 0)
            
            if width > 0:
                constraints.append(Constraint(
                    target_type='component',
                    target_id=node.get('id', ''),
                    constraint_type=ConstraintType.RANGE,
                    parameters={'min': 0, 'max': width, 'field': 'width'},
                    description=f"Width constraint: 0-{width}"
                ))
            
            if height > 0:
                constraints.append(Constraint(
                    target_type='component',
                    target_id=node.get('id', ''),
                    constraint_type=ConstraintType.RANGE,
                    parameters={'min': 0, 'max': height, 'field': 'height'},
                    description=f"Height constraint: 0-{height}"
                ))
        
        return constraints
    
    def get_component_screenshots(self, file_id: str, node_ids: List[str]) -> Dict[str, str]:
        """Get screenshot URLs for specific components.
        
        Args:
            file_id: Figma file ID
            node_ids: List of node IDs to get screenshots for
            
        Returns:
            Dictionary mapping node IDs to screenshot URLs
        """
        if not self.api_key:
            raise ValueError("Figma API key not configured")
        
        url = f"{self.base_url}/images/{file_id}"
        headers = {"X-Figma-Token": self.api_key}
        
        params = {
            'ids': ','.join(node_ids),
            'format': 'png',
            'scale': 2
        }
        
        try:
            log_api_call("Figma Images", url, "GET")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            log_api_call("Figma Images", url, "GET", response.status_code)
            result = response.json()
            
            return result.get('images', {})
            
        except requests.RequestException as e:
            self.logger.error(f"Figma images API call failed: {e}")
            raise
