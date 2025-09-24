"""
Simple API specs parser for basic OpenAPI/Swagger files.

This module provides basic functionality to parse API specifications
and extract endpoint information for test case generation.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...utils.logging import get_logger, log_file_operation
from ...utils.validators import validate_file_path


class APISpecParser:
    """Simple parser for API specifications."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the API specs parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger()
    
    def parse_api_spec(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse API specification file.
        
        Args:
            file_path: Path to the API spec file (JSON or YAML)
            
        Returns:
            Parsed API specification dictionary
        """
        file_path = Path(file_path)
        
        if not validate_file_path(file_path, must_exist=True):
            raise FileNotFoundError(f"API spec file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
            
            log_file_operation("parse_api_spec", str(file_path), success=True)
            return spec
            
        except Exception as e:
            log_file_operation("parse_api_spec", str(file_path), success=False)
            self.logger.error(f"Error parsing API spec file {file_path}: {e}")
            raise
    
    def extract_endpoints(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoint information from API specification.
        
        Args:
            spec: Parsed API specification
            
        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        
        # Get base URL
        base_url = self._get_base_url(spec)
        
        # Extract paths
        paths = spec.get('paths', {})
        
        for path, path_info in paths.items():
            for method, method_info in path_info.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    endpoint = self._create_endpoint_dict(
                        method.upper(), 
                        path, 
                        method_info, 
                        base_url
                    )
                    endpoints.append(endpoint)
        
        self.logger.info(f"Extracted {len(endpoints)} endpoints from API spec")
        return endpoints
    
    def extract_parameters(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract parameter definitions from API specification.
        
        Args:
            spec: Parsed API specification
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        # Extract global parameters
        global_params = spec.get('parameters', {})
        for param_id, param_info in global_params.items():
            param = self._create_parameter_dict(param_id, param_info, 'global')
            parameters.append(param)
        
        # Extract parameters from components
        components = spec.get('components', {})
        schemas = components.get('schemas', {})
        
        for schema_name, schema_info in schemas.items():
            if 'properties' in schema_info:
                for prop_name, prop_info in schema_info['properties'].items():
                    param = self._create_parameter_dict(
                        f"{schema_name}.{prop_name}", 
                        prop_info, 
                        'schema'
                    )
                    parameters.append(param)
        
        self.logger.info(f"Extracted {len(parameters)} parameters from API spec")
        return parameters
    
    def generate_test_cases_from_endpoints(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate basic test cases from API endpoints.
        
        Args:
            endpoints: List of endpoint dictionaries
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        for endpoint in endpoints:
            method = endpoint['method']
            path = endpoint['path']
            operation_id = endpoint.get('operation_id', f"{method}_{path.replace('/', '_').strip('_')}")
            
            # Generate basic test cases for each endpoint
            test_cases.extend([
                {
                    'id': f"API-{operation_id}-001",
                    'title': f"{method} {path} - Valid Request",
                    'type': 'FUNC',
                    'priority': 'P0',
                    'steps': [
                        f"Prepare valid request data for {method} {path}",
                        f"Send {method} request to {path}",
                        "Verify response status is 200/201"
                    ],
                    'expected_result': f"Request succeeds with valid data",
                    'endpoint': endpoint
                },
                {
                    'id': f"API-{operation_id}-002",
                    'title': f"{method} {path} - Invalid Request",
                    'type': 'NEG',
                    'priority': 'P1',
                    'steps': [
                        f"Prepare invalid request data for {method} {path}",
                        f"Send {method} request to {path}",
                        "Verify response status is 400/422"
                    ],
                    'expected_result': f"Request fails with appropriate error",
                    'endpoint': endpoint
                }
            ])
            
            # Add authentication test for protected endpoints
            if endpoint.get('security'):
                test_cases.append({
                    'id': f"API-{operation_id}-003",
                    'title': f"{method} {path} - Unauthorized Access",
                    'type': 'PERM',
                    'priority': 'P1',
                    'steps': [
                        f"Send {method} request to {path} without authentication",
                        "Verify response status is 401/403"
                    ],
                    'expected_result': f"Request fails with authentication error",
                    'endpoint': endpoint
                })
        
        self.logger.info(f"Generated {len(test_cases)} test cases from {len(endpoints)} endpoints")
        return test_cases
    
    def _get_base_url(self, spec: Dict[str, Any]) -> str:
        """Get base URL from API specification.
        
        Args:
            spec: Parsed API specification
            
        Returns:
            Base URL string
        """
        # Try different ways to get base URL
        if 'servers' in spec and spec['servers']:
            return spec['servers'][0].get('url', '')
        
        if 'host' in spec:
            host = spec['host']
            scheme = spec.get('schemes', ['https'])[0]
            base_path = spec.get('basePath', '')
            return f"{scheme}://{host}{base_path}"
        
        return ''
    
    def _create_endpoint_dict(self, method: str, path: str, method_info: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        """Create endpoint dictionary from API spec data.
        
        Args:
            method: HTTP method
            path: API path
            method_info: Method information from spec
            base_url: Base URL
            
        Returns:
            Endpoint dictionary
        """
        return {
            'method': method,
            'path': path,
            'full_url': f"{base_url}{path}",
            'operation_id': method_info.get('operationId', ''),
            'summary': method_info.get('summary', ''),
            'description': method_info.get('description', ''),
            'tags': method_info.get('tags', []),
            'parameters': method_info.get('parameters', []),
            'request_body': method_info.get('requestBody', {}),
            'responses': method_info.get('responses', {}),
            'security': method_info.get('security', []),
            'deprecated': method_info.get('deprecated', False)
        }
    
    def _create_parameter_dict(self, param_id: str, param_info: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Create parameter dictionary from API spec data.
        
        Args:
            param_id: Parameter identifier
            param_info: Parameter information from spec
            source: Source of the parameter (global, schema, etc.)
            
        Returns:
            Parameter dictionary
        """
        return {
            'id': param_id,
            'name': param_info.get('name', param_id),
            'type': param_info.get('type', 'string'),
            'format': param_info.get('format', ''),
            'description': param_info.get('description', ''),
            'required': param_info.get('required', False),
            'enum': param_info.get('enum', []),
            'minimum': param_info.get('minimum'),
            'maximum': param_info.get('maximum'),
            'min_length': param_info.get('minLength'),
            'max_length': param_info.get('maxLength'),
            'pattern': param_info.get('pattern', ''),
            'source': source,
            'example': param_info.get('example', '')
        }
