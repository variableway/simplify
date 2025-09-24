"""
Logging utilities for the Test Case Generator.

This module provides centralized logging configuration and utilities.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .config import Config, get_config


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


class TestCaseGeneratorLogger:
    """Custom logger for the Test Case Generator."""
    
    def __init__(self, name: str = "testcase_generator"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Set up the logger with appropriate handlers and formatters."""
        config = get_config()
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        level = getattr(logging, config.logging.level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if config.debug:
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
        else:
            console_formatter = ColoredFormatter(config.logging.format)
        
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if config.logging.file_path:
            file_path = Path(config.logging.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=config.logging.max_file_size,
                backupCount=config.logging.backup_count
            )
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)


# Global logger instance
_logger: Optional[TestCaseGeneratorLogger] = None


def get_logger(name: str = "testcase_generator") -> TestCaseGeneratorLogger:
    """Get a logger instance."""
    global _logger
    if _logger is None:
        _logger = TestCaseGeneratorLogger(name)
    return _logger


def setup_logging(config: Optional[Config] = None) -> None:
    """Set up logging with the given configuration."""
    if config is None:
        config = get_config()
    
    # Update the global config
    from .config import set_config
    set_config(config)
    
    # Create logger
    global _logger
    _logger = TestCaseGeneratorLogger()


def log_function_call(func_name: str, **kwargs) -> None:
    """Log a function call with parameters."""
    logger = get_logger()
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Calling {func_name}({params})")


def log_performance(operation: str, duration: float) -> None:
    """Log performance metrics."""
    logger = get_logger()
    logger.info(f"Performance: {operation} completed in {duration:.2f}s")


def log_error_with_context(error: Exception, context: str = "") -> None:
    """Log an error with additional context."""
    logger = get_logger()
    if context:
        logger.error(f"Error in {context}: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")
    logger.exception("Full traceback:")


def log_api_call(api_name: str, endpoint: str, method: str, status_code: Optional[int] = None) -> None:
    """Log API calls for debugging."""
    logger = get_logger()
    if status_code:
        logger.debug(f"API Call: {api_name} {method} {endpoint} -> {status_code}")
    else:
        logger.debug(f"API Call: {api_name} {method} {endpoint}")


def log_file_operation(operation: str, file_path: str, success: bool = True) -> None:
    """Log file operations."""
    logger = get_logger()
    status = "success" if success else "failed"
    logger.debug(f"File {operation}: {file_path} -> {status}")


def log_validation_error(field: str, value: str, error: str) -> None:
    """Log validation errors."""
    logger = get_logger()
    logger.warning(f"Validation error in {field}: {error} (value: {value})")


def log_generation_stats(requirement_count: int, component_count: int, test_case_count: int) -> None:
    """Log test case generation statistics."""
    logger = get_logger()
    logger.info(f"Generation complete: {requirement_count} requirements, "
                f"{component_count} components, {test_case_count} test cases")


def log_coverage_analysis(coverage_percentage: float, uncovered_items: int) -> None:
    """Log coverage analysis results."""
    logger = get_logger()
    logger.info(f"Coverage analysis: {coverage_percentage:.1f}% coverage, "
                f"{uncovered_items} uncovered items")


# Convenience functions for common logging patterns
def log_startup() -> None:
    """Log application startup."""
    logger = get_logger()
    logger.info("Test Case Generator starting up...")


def log_shutdown() -> None:
    """Log application shutdown."""
    logger = get_logger()
    logger.info("Test Case Generator shutting down...")


def log_config_loaded(config_path: str) -> None:
    """Log configuration loading."""
    logger = get_logger()
    logger.info(f"Configuration loaded from: {config_path}")


def log_config_error(error: str) -> None:
    """Log configuration errors."""
    logger = get_logger()
    logger.error(f"Configuration error: {error}")


def log_llm_request(prompt_length: int, response_length: int, model: str) -> None:
    """Log LLM request details."""
    logger = get_logger()
    logger.debug(f"LLM request: {model}, prompt: {prompt_length} chars, "
                f"response: {response_length} chars")


def log_export_complete(format: str, file_path: str, item_count: int) -> None:
    """Log export completion."""
    logger = get_logger()
    logger.info(f"Export complete: {format} format, {item_count} items -> {file_path}")


def log_integration_error(service: str, error: str) -> None:
    """Log integration errors."""
    logger = get_logger()
    logger.error(f"Integration error with {service}: {error}")


def log_parsing_error(source: str, error: str) -> None:
    """Log parsing errors."""
    logger = get_logger()
    logger.error(f"Parsing error from {source}: {error}")


def log_gap_analysis_complete(gaps_found: int, recommendations: int) -> None:
    """Log gap analysis completion."""
    logger = get_logger()
    logger.info(f"Gap analysis complete: {gaps_found} gaps found, "
                f"{recommendations} recommendations generated")
