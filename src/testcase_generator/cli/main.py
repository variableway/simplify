"""
Main CLI entry point for the Test Case Generator.

This module provides the command-line interface for the test case generator.
"""

import sys
from pathlib import Path
from typing import Optional

import typer

from ..utils.config import get_config, create_default_config
from ..utils.logging import setup_logging, get_logger, log_startup, log_shutdown
from .commands.generate import generate_cmd
from .commands.analyze import analyze_cmd
from .commands.export import export_cmd
from .commands.manage import manage_cmd

# Create the main CLI app
app = typer.Typer(
    name="testcase-gen",
    help="Test Case Generator - Generate test cases from screenshots using AI vision models",
    add_completion=False
)

# Add subcommands
app.add_typer(generate_cmd, name="generate", help="Generate test cases from screenshots")
app.add_typer(analyze_cmd, name="analyze", help="Analyze test coverage and identify gaps")
app.add_typer(export_cmd, name="export", help="Export test cases to various formats")
app.add_typer(manage_cmd, name="manage", help="Manage projects and test cases")

@app.callback()
def main(
    config: Optional[Path] = typer.Option(None, "-c", "--config", help="Configuration file path"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable verbose logging"),
    debug: bool = typer.Option(False, "-d", "--debug", help="Enable debug mode"),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir", help="Output directory")
):
    """
    Test Case Generator - Generate test cases from screenshots using AI vision models.
    
    This tool helps you automatically generate comprehensive test cases by analyzing
    screenshots and using AI vision models to understand UI elements and interactions.
    """
    # Load configuration
    try:
        if config:
            cfg = get_config()
            cfg.load_from_file(config)
        else:
            cfg = get_config()
        
        # Override with CLI options
        if verbose or debug:
            cfg.logging.level = 'DEBUG' if debug else 'INFO'
        if debug:
            cfg.debug = True
        if output_dir:
            cfg.output_dir = str(output_dir)
        
        # Setup logging
        setup_logging(cfg)
        
        log_startup()
        
    except Exception as e:
        typer.echo(f"Error loading configuration: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def init(output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path")):
    """Initialize a new project with default configuration."""
    if not output:
        output = Path.cwd() / "config.yaml"
    else:
        output = Path(output)
    
    try:
        create_default_config(output)
        typer.echo(f"✅ Default configuration created at: {output}")
        typer.echo("📝 Edit the configuration file and run 'testcase-gen generate' to start generating test cases.")
    except Exception as e:
        typer.echo(f"❌ Error creating configuration: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from .. import __version__
    typer.echo(f"Test Case Generator v{__version__}")


@app.command()
def config():
    """Show current configuration."""
    config = get_config()
    
    typer.echo("📋 Current Configuration:")
    typer.echo(f"  Project Name: {config.project_name}")
    typer.echo(f"  Output Directory: {config.output_dir}")
    typer.echo(f"  LLM Provider: {config.llm['provider']}")
    typer.echo(f"  LLM Model: {config.llm['model']}")
    typer.echo(f"  Debug Mode: {config.debug}")
    typer.echo(f"  Log Level: {config.get('logging.level', 'INFO')}")


@app.command()
def validate():
    """Validate current configuration."""
    config = get_config()
    
    typer.echo("🔍 Validating configuration...")
    
    issues = config._config.validate_config()
    
    if not issues:
        typer.echo("✅ Configuration is valid!")
    else:
        typer.echo("❌ Configuration issues found:")
        for issue in issues:
            typer.echo(f"  • {issue}")
        raise typer.Exit(1)


def cli():
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        typer.echo("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger = get_logger()
        logger.exception("Unexpected error occurred")
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)
    finally:
        log_shutdown()


if __name__ == '__main__':
    cli()