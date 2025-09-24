"""
Validation utilities for the Test Case Generator.

This module provides input validation functions and custom validators.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logging import log_validation_error


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_requirement_id(requirement_id: str) -> bool:
    """Validate requirement ID format."""
    if not requirement_id:
        log_validation_error("requirement_id", requirement_id, "Requirement ID cannot be empty")
        return False
    
    # Check for valid format (e.g., REQ-001, REQ_USER_001)
    pattern = r'^[A-Z]+[-_][A-Z0-9_]+$'
    if not re.match(pattern, requirement_id):
        log_validation_error("requirement_id", requirement_id, 
                           "Requirement ID must match pattern: REQ-001 or REQ_USER_001")
        return False
    
    return True


def validate_priority(priority: str) -> bool:
    """Validate priority value."""
    valid_priorities = ['P0', 'P1', 'P2', 'P3']
    if priority not in valid_priorities:
        log_validation_error("priority", priority, 
                           f"Priority must be one of: {valid_priorities}")
        return False
    
    return True


def validate_test_case_type(test_type: str) -> bool:
    """Validate test case type."""
    valid_types = ['FUNC', 'BOUND', 'NEG', 'PERM', 'SEC', 'PERF', 'A11Y']
    if test_type not in valid_types:
        log_validation_error("test_type", test_type, 
                           f"Test case type must be one of: {valid_types}")
        return False
    
    return True


def validate_component_type(component_type: str) -> bool:
    """Validate component type."""
    valid_types = [
        'button', 'input', 'dropdown', 'checkbox', 'radio', 
        'textarea', 'link', 'image', 'table', 'modal', 'card', 'navigation'
    ]
    if component_type not in valid_types:
        log_validation_error("component_type", component_type, 
                           f"Component type must be one of: {valid_types}")
        return False
    
    return True


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> bool:
    """Validate file path."""
    file_path = Path(file_path)
    
    if not file_path.is_absolute():
        file_path = file_path.resolve()
    
    if must_exist and not file_path.exists():
        log_validation_error("file_path", str(file_path), "File does not exist")
        return False
    
    if must_exist and not file_path.is_file():
        log_validation_error("file_path", str(file_path), "Path is not a file")
        return False
    
    return True


def validate_directory_path(dir_path: Union[str, Path], must_exist: bool = True) -> bool:
    """Validate directory path."""
    dir_path = Path(dir_path)
    
    if not dir_path.is_absolute():
        dir_path = dir_path.resolve()
    
    if must_exist and not dir_path.exists():
        log_validation_error("directory_path", str(dir_path), "Directory does not exist")
        return False
    
    if must_exist and not dir_path.is_dir():
        log_validation_error("directory_path", str(dir_path), "Path is not a directory")
        return False
    
    return True


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url:
        log_validation_error("url", url, "URL cannot be empty")
        return False
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        log_validation_error("url", url, "Invalid URL format")
        return False
    
    return True


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        log_validation_error("email", email, "Email cannot be empty")
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        log_validation_error("email", email, "Invalid email format")
        return False
    
    return True


def validate_api_key(api_key: str, provider: str) -> bool:
    """Validate API key format based on provider."""
    if not api_key:
        log_validation_error("api_key", api_key, f"API key for {provider} cannot be empty")
        return False
    
    # Basic length check
    if len(api_key) < 10:
        log_validation_error("api_key", api_key, f"API key for {provider} too short")
        return False
    
    # Provider-specific validation
    if provider.lower() == 'openai':
        if not api_key.startswith('sk-'):
            log_validation_error("api_key", api_key, "OpenAI API key should start with 'sk-'")
            return False
    elif provider.lower() == 'anthropic':
        if not api_key.startswith('sk-ant-'):
            log_validation_error("api_key", api_key, "Anthropic API key should start with 'sk-ant-'")
            return False
    
    return True


def validate_json_data(data: Any, required_fields: List[str]) -> bool:
    """Validate JSON data has required fields."""
    if not isinstance(data, dict):
        log_validation_error("json_data", str(type(data)), "Data must be a dictionary")
        return False
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        log_validation_error("json_data", str(data), 
                           f"Missing required fields: {missing_fields}")
        return False
    
    return True


def validate_test_steps(steps: List[str]) -> bool:
    """Validate test case steps."""
    if not steps:
        log_validation_error("test_steps", str(steps), "Test case must have at least one step")
        return False
    
    for i, step in enumerate(steps):
        if not step or not step.strip():
            log_validation_error("test_steps", f"Step {i+1}", "Test step cannot be empty")
            return False
        
        if len(step.strip()) < 5:
            log_validation_error("test_steps", f"Step {i+1}", "Test step too short")
            return False
    
    return True


def validate_coverage_percentage(percentage: float) -> bool:
    """Validate coverage percentage."""
    if not isinstance(percentage, (int, float)):
        log_validation_error("coverage_percentage", str(percentage), 
                           "Coverage percentage must be a number")
        return False
    
    if not 0 <= percentage <= 100:
        log_validation_error("coverage_percentage", str(percentage), 
                           "Coverage percentage must be between 0 and 100")
        return False
    
    return True


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate configuration dictionary."""
    errors = []
    
    # Check required top-level fields
    required_fields = ['llm', 'parsing', 'generation']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required configuration field: {field}")
    
    # Validate LLM configuration
    if 'llm' in config:
        llm_config = config['llm']
        if 'provider' not in llm_config:
            errors.append("LLM provider not specified")
        elif llm_config['provider'] in ['openai', 'anthropic']:
            if 'api_key' not in llm_config or not llm_config['api_key']:
                errors.append(f"API key required for {llm_config['provider']}")
    
    # Validate generation configuration
    if 'generation' in config:
        gen_config = config['generation']
        if 'max_cases_per_requirement' in gen_config:
            max_cases = gen_config['max_cases_per_requirement']
            if not isinstance(max_cases, int) or max_cases < 1:
                errors.append("max_cases_per_requirement must be a positive integer")
    
    return errors


def validate_input(input_data: Any, input_type: str) -> bool:
    """Generic input validation based on type."""
    if input_type == 'requirement_id':
        return validate_requirement_id(input_data)
    elif input_type == 'priority':
        return validate_priority(input_data)
    elif input_type == 'test_case_type':
        return validate_test_case_type(input_data)
    elif input_type == 'component_type':
        return validate_component_type(input_data)
    elif input_type == 'file_path':
        return validate_file_path(input_data)
    elif input_type == 'directory_path':
        return validate_directory_path(input_data)
    elif input_type == 'url':
        return validate_url(input_data)
    elif input_type == 'email':
        return validate_email(input_data)
    elif input_type == 'test_steps':
        return validate_test_steps(input_data)
    elif input_type == 'coverage_percentage':
        return validate_coverage_percentage(input_data)
    else:
        log_validation_error("input_type", input_type, f"Unknown validation type: {input_type}")
        return False


def validate_all_inputs(inputs: Dict[str, Any]) -> Dict[str, bool]:
    """Validate multiple inputs and return validation results."""
    results = {}
    
    for key, value in inputs.items():
        # Determine validation type based on key name
        if 'id' in key.lower() and 'requirement' in key.lower():
            validation_type = 'requirement_id'
        elif 'priority' in key.lower():
            validation_type = 'priority'
        elif 'type' in key.lower() and 'test' in key.lower():
            validation_type = 'test_case_type'
        elif 'type' in key.lower() and 'component' in key.lower():
            validation_type = 'component_type'
        elif 'path' in key.lower() and 'file' in key.lower():
            validation_type = 'file_path'
        elif 'path' in key.lower() and 'dir' in key.lower():
            validation_type = 'directory_path'
        elif 'url' in key.lower():
            validation_type = 'url'
        elif 'email' in key.lower():
            validation_type = 'email'
        elif 'steps' in key.lower():
            validation_type = 'test_steps'
        elif 'coverage' in key.lower() and 'percentage' in key.lower():
            validation_type = 'coverage_percentage'
        else:
            # Default validation - just check if not empty
            results[key] = value is not None and str(value).strip() != ""
            continue
        
        results[key] = validate_input(value, validation_type)
    
    return results


def sanitize_input(input_data: str) -> str:
    """Sanitize input data by removing potentially harmful characters."""
    if not isinstance(input_data, str):
        return str(input_data)
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_data)
    
    # Limit length to prevent abuse
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000] + "..."
    
    return sanitized.strip()


def validate_and_sanitize(input_data: str, validation_type: str) -> str:
    """Validate and sanitize input data."""
    sanitized = sanitize_input(input_data)
    
    if not validate_input(sanitized, validation_type):
        raise ValidationError(f"Validation failed for {validation_type}: {sanitized}")
    
    return sanitized
