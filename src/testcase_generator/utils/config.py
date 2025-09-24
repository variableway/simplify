"""
Configuration management for the Test Case Generator.

This module provides configuration loading, validation, and management functionality.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, validator


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, local)")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    model: str = Field(default="gpt-4", description="Model name to use")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    @validator('temperature')
    def temperature_must_be_valid(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v


class IntegrationConfig(BaseModel):
    """Configuration for external integrations."""
    testrail: Optional[Dict[str, str]] = Field(None, description="TestRail configuration")
    jira: Optional[Dict[str, str]] = Field(None, description="Jira configuration")
    figma: Optional[Dict[str, str]] = Field(None, description="Figma configuration")
    confluence: Optional[Dict[str, str]] = Field(None, description="Confluence configuration")


class ParsingConfig(BaseModel):
    """Configuration for parsing different input formats."""
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requirements parsing config")
    figma: Dict[str, Any] = Field(default_factory=dict, description="Figma parsing config")
    screenshots: Dict[str, Any] = Field(default_factory=dict, description="Screenshot parsing config")
    api_specs: Dict[str, Any] = Field(default_factory=dict, description="API specs parsing config")


class GenerationConfig(BaseModel):
    """Configuration for test case generation."""
    test_case_types: List[str] = Field(
        default=["FUNC", "BOUND", "NEG", "PERM", "SEC", "PERF"],
        description="Types of test cases to generate"
    )
    priorities: List[str] = Field(
        default=["P0", "P1", "P2"],
        description="Priority levels to use"
    )
    max_cases_per_requirement: int = Field(
        default=10,
        description="Maximum test cases per requirement"
    )
    enable_ai_generation: bool = Field(default=True, description="Enable AI-based generation")
    enable_rule_generation: bool = Field(default=True, description="Enable rule-based generation")


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    file_path: Optional[str] = Field(None, description="Log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size in bytes")
    backup_count: int = Field(default=5, description="Number of backup files to keep")


class Config(BaseModel):
    """Main configuration class."""
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    integrations: IntegrationConfig = Field(
        default_factory=IntegrationConfig,
        description="External integrations"
    )
    parsing: ParsingConfig = Field(default_factory=ParsingConfig, description="Parsing configuration")
    generation: GenerationConfig = Field(
        default_factory=GenerationConfig,
        description="Generation configuration"
    )
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    
    # General settings
    project_name: str = Field(default="Test Case Generator", description="Project name")
    output_dir: str = Field(default="./output", description="Output directory")
    temp_dir: str = Field(default="./temp", description="Temporary directory")
    cache_dir: str = Field(default="./cache", description="Cache directory")
    
    # Environment variables
    environment: str = Field(default="development", description="Environment (dev, staging, prod)")
    debug: bool = Field(default=False, description="Debug mode")

    class Config:
        env_prefix = "TCG_"
        case_sensitive = False

    @validator('environment')
    def environment_must_be_valid(cls, v):
        valid_envs = ['development', 'staging', 'production']
        if v not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v

    def load_from_file(self, config_path: Union[str, Path]) -> 'Config':
        """Load configuration from a YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return Config(**config_data)

    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to a YAML file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.dict(), f, default_flow_style=False, indent=2)

    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with TCG_ prefix."""
        env_key = f"TCG_{key.upper()}"
        return os.getenv(env_key, default)

    def update_from_env(self) -> None:
        """Update configuration from environment variables."""
        # Update LLM config
        if api_key := self.get_env_var("LLM_API_KEY"):
            self.llm.api_key = api_key
        if provider := self.get_env_var("LLM_PROVIDER"):
            self.llm.provider = provider
        if model := self.get_env_var("LLM_MODEL"):
            self.llm.model = model
        
        # Update integrations
        if testrail_url := self.get_env_var("TESTRAIL_URL"):
            if not self.integrations.testrail:
                self.integrations.testrail = {}
            self.integrations.testrail["url"] = testrail_url
        
        if testrail_username := self.get_env_var("TESTRAIL_USERNAME"):
            if not self.integrations.testrail:
                self.integrations.testrail = {}
            self.integrations.testrail["username"] = testrail_username
        
        if testrail_api_key := self.get_env_var("TESTRAIL_API_KEY"):
            if not self.integrations.testrail:
                self.integrations.testrail = {}
            self.integrations.testrail["api_key"] = testrail_api_key
        
        # Update general settings
        if project_name := self.get_env_var("PROJECT_NAME"):
            self.project_name = project_name
        if output_dir := self.get_env_var("OUTPUT_DIR"):
            self.output_dir = output_dir
        if debug := self.get_env_var("DEBUG"):
            self.debug = debug.lower() in ('true', '1', 'yes', 'on')

    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [self.output_dir, self.temp_dir, self.cache_dir]
        if self.logging.file_path:
            directories.append(Path(self.logging.file_path).parent)
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check required API keys
        if self.llm.provider in ['openai', 'anthropic'] and not self.llm.api_key:
            issues.append(f"API key required for {self.llm.provider} provider")
        
        # Check directory permissions
        for directory in [self.output_dir, self.temp_dir, self.cache_dir]:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                issues.append(f"Cannot create directory: {directory}")
        
        # Check integration configurations
        if self.integrations.testrail:
            required_fields = ['url', 'username', 'api_key']
            missing_fields = [field for field in required_fields 
                            if not self.integrations.testrail.get(field)]
            if missing_fields:
                issues.append(f"TestRail missing required fields: {missing_fields}")
        
        return issues


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from file or create default configuration."""
    if config_path is None:
        # Look for config files in common locations
        config_paths = [
            Path("config/config.yaml"),
            Path("config.yaml"),
            Path("~/.testcase-generator/config.yaml").expanduser(),
        ]
        
        for path in config_paths:
            if path.exists():
                config_path = path
                break
    
    if config_path and Path(config_path).exists():
        config = Config().load_from_file(config_path)
    else:
        config = Config()
    
    # Update from environment variables
    config.update_from_env()
    
    # Create necessary directories
    config.create_directories()
    
    return config


def create_default_config(config_path: Union[str, Path]) -> None:
    """Create a default configuration file."""
    config = Config()
    config.save_to_file(config_path)
    print(f"Default configuration created at: {config_path}")


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
