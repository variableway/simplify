"""
Core configuration module for the Test Case Generator.

This module provides a simplified configuration interface that wraps
the existing utils.config.Config class for easier access.
"""

from typing import Any, Dict, Optional
from ..utils.config import Config as BaseConfig, get_config as get_base_config


class Config:
    """Simplified configuration interface for core modules."""
    
    def __init__(self, config: Optional[BaseConfig] = None):
        """Initialize configuration.
        
        Args:
            config: Optional BaseConfig instance. If None, uses global config.
        """
        self._config = config or get_base_config()
    
    @property
    def llm(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            'api_key': self._config.llm.api_key,
            'provider': self._config.llm.provider,
            'model': self._config.llm.model,
            'temperature': self._config.llm.temperature,
            'max_tokens': self._config.llm.max_tokens,
            'timeout': self._config.llm.timeout
        }
    
    @property
    def output_dir(self) -> str:
        """Get output directory."""
        return self._config.output_dir
    
    @property
    def temp_dir(self) -> str:
        """Get temporary directory."""
        return self._config.temp_dir
    
    @property
    def cache_dir(self) -> str:
        """Get cache directory."""
        return self._config.cache_dir
    
    @property
    def project_name(self) -> str:
        """Get project name."""
        return self._config.project_name
    
    @property
    def debug(self) -> bool:
        """Get debug mode."""
        return self._config.debug
    
    @property
    def generation(self) -> Dict[str, Any]:
        """Get generation configuration."""
        return {
            'test_case_types': self._config.generation.test_case_types,
            'priorities': self._config.generation.priorities,
            'max_cases_per_requirement': self._config.generation.max_cases_per_requirement,
            'enable_ai_generation': self._config.generation.enable_ai_generation,
            'enable_rule_generation': self._config.generation.enable_rule_generation
        }
    
    @property
    def integrations(self) -> Dict[str, Any]:
        """Get integrations configuration."""
        return {
            'testrail': self._config.integrations.testrail or {},
            'jira': self._config.integrations.jira or {},
            'figma': self._config.integrations.figma or {},
            'confluence': self._config.integrations.confluence or {}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = getattr(value, k)
            return value
        except AttributeError:
            return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return self._config.dict()
