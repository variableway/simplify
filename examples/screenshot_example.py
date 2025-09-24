#!/usr/bin/env python3
"""
Example script demonstrating screenshot-based test case generation.

This script shows how to use the Test Case Generator to generate test cases
from screenshots using AI vision models.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testcase_generator.core.parsers.screenshots import ScreenshotParser
from testcase_generator.utils.config import Config
from testcase_generator.utils.logging import setup_logging


def main():
    """Main example function."""
    print("🚀 Test Case Generator - Screenshot Example")
    print("=" * 50)
    
    # Setup logging
    config = Config()
    setup_logging(config)
    
    # Check if API key is configured
    if not config.llm.api_key:
        print("❌ Error: OpenAI API key not configured")
        print("Please set the TCG_LLM_API_KEY environment variable")
        print("Example: export TCG_LLM_API_KEY='your-api-key-here'")
        return
    
    # Initialize screenshot parser
    parser_config = {
        'api_key': config.llm.api_key,
        'api_url': 'https://api.openai.com/v1/chat/completions',
        'model': config.llm.model,
        'max_tokens': config.llm.max_tokens,
        'temperature': config.llm.temperature
    }
    
    screenshot_parser = ScreenshotParser(parser_config)
    
    # Example screenshot path (you can change this)
    screenshot_path = Path("test_data/img/1.png")  # Using existing test image
    
    if not screenshot_path.exists():
        print(f"❌ Error: Screenshot not found: {screenshot_path}")
        print("Please provide a valid screenshot path")
        return
    
    print(f"📸 Processing screenshot: {screenshot_path}")
    
    # Additional context for better generation
    additional_context = """
    This is a web application screenshot. Please focus on:
    - User interface elements (buttons, forms, navigation)
    - Input fields and their validation
    - User workflows and interactions
    - Error states and edge cases
    - Accessibility considerations
    """
    
    try:
        # Generate test cases
        print("🤖 Generating test cases using AI vision...")
        
        test_cases = screenshot_parser.generate_test_cases_from_screenshot(
            screenshot_path,
            test_types=['FUNC', 'BOUND', 'NEG', 'PERM', 'SEC'],
            additional_context=additional_context
        )
        
        print(f"✅ Generated {len(test_cases)} test cases!")
        print("\n📋 Generated Test Cases:")
        print("-" * 50)
        
        for i, tc in enumerate(test_cases, 1):
            print(f"\n{i}. {tc.title}")
            print(f"   Type: {tc.test_type}")
            print(f"   Priority: {tc.priority}")
            print(f"   Steps:")
            for j, step in enumerate(tc.steps, 1):
                print(f"     {j}. {step}")
            print(f"   Expected: {tc.expected_result}")
            if tc.metadata.get('covered_elements'):
                print(f"   Elements: {tc.metadata['covered_elements']}")
        
        print(f"\n📊 Summary:")
        print(f"  • Total test cases: {len(test_cases)}")
        print(f"  • Functional tests: {sum(1 for tc in test_cases if tc.test_type == 'FUNC')}")
        print(f"  • Boundary tests: {sum(1 for tc in test_cases if tc.test_type == 'BOUND')}")
        print(f"  • Negative tests: {sum(1 for tc in test_cases if tc.test_type == 'NEG')}")
        print(f"  • Permission tests: {sum(1 for tc in test_cases if tc.test_type == 'PERM')}")
        print(f"  • Security tests: {sum(1 for tc in test_cases if tc.test_type == 'SEC')}")
        
    except Exception as e:
        print(f"❌ Error generating test cases: {e}")
        return
    
    print("\n🎉 Example completed successfully!")
    print("\n💡 Next steps:")
    print("  1. Try with your own screenshots")
    print("  2. Use the CLI: testcase-gen generate -s your_screenshot.png")
    print("  3. Add context: testcase-gen generate -s screenshot.png -c 'This is a login page'")


if __name__ == "__main__":
    main()
