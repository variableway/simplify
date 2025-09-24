"""
Generate command for creating test cases.

This module provides the CLI command for generating test cases from various inputs.
"""

import typer
import sys
from pathlib import Path
from typing import Optional, List
from enum import Enum

from ...core.config import Config
from ...core.generator import TestCaseGenerator
from ...core.project import ProjectManager
from ...utils.logging import get_logger


class OutputFormat(str, Enum):
    excel = "excel"
    csv = "csv"
    json = "json"
    testrail = "testrail"

class TestType(str, Enum):
    FUNC = "FUNC"
    BOUND = "BOUND"
    NEG = "NEG"
    PERM = "PERM"
    SEC = "SEC"
    PERF = "PERF"
    A11Y = "A11Y"

def generate_cmd(screenshots: Optional[Path] = typer.Option(None, "-s", "--screenshots", 
                                                          help="Screenshot file or directory containing screenshots"),
                requirements: Optional[Path] = typer.Option(None, "-r", "--requirements", 
                                                           help="Requirements text file (optional context)"),
                figma: Optional[str] = typer.Option(None, "-f", "--figma", 
                                                   help="Figma file ID (optional context)"),
                api_spec: Optional[Path] = typer.Option(None, "-a", "--api-spec", 
                                                       help="API specification file (optional context)"),
                output: Optional[Path] = typer.Option(None, "-o", "--output", 
                                                     help="Output file path for generated test cases"),
                output_format: OutputFormat = typer.Option(OutputFormat.excel, "--format", 
                                                          help="Output format"),
                types: Optional[List[TestType]] = typer.Option(None, "-t", "--types", 
                                                              help="Types of test cases to generate"),
                context: Optional[str] = typer.Option(None, "-c", "--context", 
                                                     help="Additional context for AI generation"),
                dry_run: bool = typer.Option(False, "--dry-run", 
                                            help="Show what would be generated without creating files")):
    """
    Generate test cases from screenshots using AI vision models.
    
    This command uploads screenshots to AI APIs and generates comprehensive test cases
    based on visual analysis. Additional context from requirements, Figma, or API specs
    can be provided to improve generation quality.
    
    Examples:
    
    \b
    # Generate from single screenshot
    testcase-gen generate -s screenshot.png
    
    \b
    # Generate from multiple screenshots
    testcase-gen generate -s ./screenshots/
    
    \b
    # Generate with additional context
    testcase-gen generate -s screenshot.png -r requirements.txt -c "This is a login page"
    
    \b
    # Generate specific test types only
    testcase-gen generate -s screenshot.png -t FUNC -t BOUND -t NEG
    """
    logger = get_logger()
    config = Config()
    
    # Validate inputs
    if not screenshots:
        typer.echo("❌ Error: Screenshots are required for AI-based generation", err=True)
        typer.echo("Use --help to see available options")
        raise typer.Exit(1)
    
    # Set default output path if not provided
    if not output:
        output = Path(config.output_dir) / f"test_cases.{output_format}"
    
    # Set default test types if not provided
    if not types:
        types = [TestType.FUNC, TestType.BOUND, TestType.NEG]
    
    # Prepare additional context
    additional_context = context or ""
    if requirements:
        additional_context += f"\nRequirements context from: {requirements}"
    if figma:
        additional_context += f"\nFigma context from file: {figma}"
    if api_spec:
        additional_context += f"\nAPI spec context from: {api_spec}"
    
    try:
        logger.info(f"Starting screenshot-based test case generation...")
        logger.info(f"Screenshots: {screenshots}")
        logger.info(f"Additional context: {requirements}, {figma}, {api_spec}")
        logger.info(f"Output: {output} ({output_format})")
        logger.info(f"Test types: {types}")
        
        if dry_run:
            typer.echo("🔍 Dry run mode - showing what would be generated:")
            typer.echo(f"  • Screenshots: {screenshots}")
            typer.echo(f"  • Test types: {', '.join([t.value for t in types])}")
            typer.echo(f"  • Additional context: {bool(additional_context)}")
            typer.echo(f"  • Output file: {output}")
            typer.echo("✅ Dry run complete - no files created")
            return
        
        # Import the screenshot parser
        from ...core.parsers.screenshots import ScreenshotParser
        
        # Initialize screenshot parser with config
        parser_config = {
            'api_key': config.llm.api_key,
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'model': config.llm.model,
            'max_tokens': config.llm.max_tokens,
            'temperature': config.llm.temperature
        }
        
        screenshot_parser = ScreenshotParser(parser_config)
        
        typer.echo("🚀 Generating test cases from screenshots...")
        
        # Get screenshot paths
        screenshot_paths = []
        screenshots_path = Path(screenshots)
        
        if screenshots_path.is_file():
            screenshot_paths = [screenshots_path]
        elif screenshots_path.is_dir():
            # Find all image files in directory
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
            for ext in image_extensions:
                screenshot_paths.extend(screenshots_path.glob(f"*{ext}"))
                screenshot_paths.extend(screenshots_path.glob(f"*{ext.upper()}"))
        else:
            typer.echo(f"❌ Error: Screenshots path not found: {screenshots}", err=True)
            raise typer.Exit(1)
        
        if not screenshot_paths:
            typer.echo(f"❌ Error: No image files found in: {screenshots}", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"📸 Found {len(screenshot_paths)} screenshot(s) to process")
        
        # Generate test cases
        with typer.progressbar(screenshot_paths, label='Processing screenshots') as progress:
            all_test_cases = []
            for screenshot_path in progress:
                try:
                    test_cases = screenshot_parser.generate_test_cases_from_screenshot(
                        screenshot_path, 
                        [t.value for t in types], 
                        additional_context
                    )
                    all_test_cases.extend(test_cases)
                except Exception as e:
                    logger.error(f"Error processing {screenshot_path}: {e}")
                    typer.echo(f"⚠️  Warning: Failed to process {screenshot_path}: {e}")
                    continue
        
        if not all_test_cases:
            typer.echo("❌ Error: No test cases were generated", err=True)
            raise typer.Exit(1)
        
        # TODO: Export test cases to specified format
        # For now, just show the results
        typer.echo("✅ Test case generation completed!")
        typer.echo(f"📁 Generated {len(all_test_cases)} test cases")
        
        # Show summary
        typer.echo(f"\n📊 Generation Summary:")
        typer.echo(f"  • Test cases generated: {len(all_test_cases)}")
        typer.echo(f"  • Screenshots processed: {len(screenshot_paths)}")
        typer.echo(f"  • Test types: {', '.join([t.value for t in types])}")
        
        # Show sample test cases
        typer.echo(f"\n📋 Sample Test Cases:")
        for i, tc in enumerate(all_test_cases[:3]):  # Show first 3
            typer.echo(f"  {i+1}. {tc.title} [{tc.test_type}] [{tc.priority}]")
        
        if len(all_test_cases) > 3:
            typer.echo(f"  ... and {len(all_test_cases) - 3} more")
        
        typer.echo(f"\n💡 Tip: Use 'testcase-gen export' to save test cases to file")
        
    except Exception as e:
        logger.exception("Error during test case generation")
        typer.echo(f"❌ Error generating test cases: {e}", err=True)
        raise typer.Exit(1)
