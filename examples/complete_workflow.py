#!/usr/bin/env python3
"""
Complete workflow example for the Test Case Generator.

This script demonstrates the complete workflow from screenshot to test cases
using the Typer-based CLI and core modules.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testcase_generator.core.config import Config
from testcase_generator.core.generator import TestCaseGenerator
from testcase_generator.core.project import ProjectManager
from testcase_generator.core.parsers.screenshots import ScreenshotParser
from testcase_generator.utils.logging import setup_logging


def main():
    """Main workflow demonstration."""
    print("🚀 Test Case Generator - Complete Workflow Example")
    print("=" * 60)
    
    # Setup logging
    config = Config()
    setup_logging(config)
    
    # Check if API key is configured
    if not config.llm['api_key']:
        print("❌ Error: OpenAI API key not configured")
        print("Please set the TCG_LLM_API_KEY environment variable")
        print("Example: export TCG_LLM_API_KEY='your-api-key-here'")
        return
    
    try:
        # Step 1: Create a new project
        print("\n📁 Step 1: Creating a new project...")
        project_manager = ProjectManager(config)
        project = project_manager.create_project(
            name="Screenshot Test Project",
            description="A project for testing screenshot-based test case generation",
            created_by="workflow_example"
        )
        print(f"✅ Created project: {project.name}")
        
        # Step 2: Initialize test case generator
        print("\n🤖 Step 2: Initializing test case generator...")
        generator = TestCaseGenerator(config)
        print("✅ Test case generator initialized")
        
        # Step 3: Generate test cases from screenshots
        print("\n📸 Step 3: Generating test cases from screenshots...")
        test_image = Path("test_data/img/1.png")
        
        if not test_image.exists():
            print(f"⚠️  Test image not found: {test_image}")
            print("Please ensure you have test images in the test_data/img/ directory")
            return
        
        # Generate test cases
        test_cases = generator.generate_from_screenshots(
            screenshots=[test_image],
            test_types=['FUNC', 'BOUND', 'NEG', 'PERM', 'SEC'],
            additional_context="This is a web application screenshot. Focus on UI elements and user interactions."
        )
        
        print(f"✅ Generated {len(test_cases)} test cases")
        
        # Step 4: Add test cases to project
        print("\n📋 Step 4: Adding test cases to project...")
        project_manager.add_test_cases(test_cases, project)
        print("✅ Test cases added to project")
        
        # Step 5: Show project summary
        print("\n📊 Step 5: Project summary...")
        summary = project_manager.get_project_summary(project)
        print(f"  • Project: {summary['name']}")
        print(f"  • Test Cases: {summary['test_cases_count']}")
        print(f"  • Requirements: {summary['requirements_count']}")
        print(f"  • Components: {summary['components_count']}")
        
        # Step 6: Export test cases
        print("\n📤 Step 6: Exporting test cases...")
        output_path = project_manager.export_test_cases(
            project=project,
            output_format="json",
            output_path=Path("output") / "generated_test_cases.json"
        )
        print(f"✅ Test cases exported to: {output_path}")
        
        # Step 7: Show sample test cases
        print("\n📋 Step 7: Sample test cases...")
        for i, tc in enumerate(test_cases[:3], 1):
            print(f"\n{i}. {tc.title}")
            print(f"   Type: {tc.test_type}")
            print(f"   Priority: {tc.priority}")
            print(f"   Steps: {len(tc.steps)} steps")
            print(f"   Expected: {tc.expected_result[:50]}...")
        
        if len(test_cases) > 3:
            print(f"\n   ... and {len(test_cases) - 3} more test cases")
        
        # Step 8: Save project
        print("\n💾 Step 8: Saving project...")
        project_file = project_manager.save_project(project)
        print(f"✅ Project saved to: {project_file}")
        
        print("\n🎉 Complete workflow finished successfully!")
        print("\n📝 Next steps:")
        print("  1. Review the generated test cases")
        print("  2. Use the CLI: testcase-gen generate -s your_screenshot.png")
        print("  3. Export to different formats: testcase-gen export")
        print("  4. Analyze coverage: testcase-gen analyze")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_cli_commands():
    """Demonstrate CLI commands."""
    print("\n🔧 CLI Commands Demonstration:")
    print("=" * 40)
    
    commands = [
        ("testcase-gen --help", "Show main help"),
        ("testcase-gen generate --help", "Show generate command help"),
        ("testcase-gen analyze --help", "Show analyze command help"),
        ("testcase-gen export --help", "Show export command help"),
        ("testcase-gen manage --help", "Show manage command help"),
        ("testcase-gen version", "Show version information"),
        ("testcase-gen config", "Show current configuration"),
        ("testcase-gen init", "Initialize configuration"),
    ]
    
    for command, description in commands:
        print(f"  {command:<30} - {description}")
    
    print("\n💡 Example usage:")
    print("  testcase-gen generate -s screenshot.png -t FUNC -t BOUND -t NEG")
    print("  testcase-gen generate -s ./screenshots/ -c 'This is a login page'")
    print("  testcase-gen export -i test_cases.json --format excel")
    print("  testcase-gen manage create-project --name 'My Project'")


if __name__ == "__main__":
    main()
    demonstrate_cli_commands()
