# Screenshot-Based Test Case Generation Guide

## Overview

The Test Case Generator uses AI vision models to analyze screenshots and automatically generate comprehensive test cases. This approach is simple, powerful, and requires minimal setup.

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -e .

# Set your OpenAI API key
export TCG_LLM_API_KEY="your-openai-api-key-here"

# Initialize configuration
testcase-gen init
```

### 2. Basic Usage

```bash
# Generate test cases from a single screenshot
testcase-gen generate -s screenshot.png

# Generate from multiple screenshots in a directory
testcase-gen generate -s ./screenshots/

# Generate with specific test types
testcase-gen generate -s screenshot.png -t FUNC -t BOUND -t NEG

# Generate with additional context
testcase-gen generate -s screenshot.png -c "This is a login page for a banking app"
```

### 3. Advanced Usage

```bash
# Generate with requirements context
testcase-gen generate -s screenshot.png -r requirements.txt

# Generate with Figma context
testcase-gen generate -s screenshot.png -f abc123def456

# Generate with API spec context
testcase-gen generate -s screenshot.png -a api-spec.yaml

# Dry run to see what would be generated
testcase-gen generate -s screenshot.png --dry-run
```

## How It Works

### 1. Image Processing
- Screenshots are automatically resized and optimized for API upload
- Supports PNG, JPG, JPEG, BMP, and TIFF formats
- Images are encoded to base64 for API transmission

### 2. AI Analysis
- Uses OpenAI's GPT-4 Vision model for visual analysis
- Analyzes UI elements, interactions, and user flows
- Identifies potential test scenarios and edge cases

### 3. Test Case Generation
- Generates multiple types of test cases:
  - **FUNC**: Functional tests for core features
  - **BOUND**: Boundary value and edge case tests
  - **NEG**: Negative tests for error handling
  - **PERM**: Permission and authorization tests
  - **SEC**: Security vulnerability tests
  - **PERF**: Performance-related tests
  - **A11Y**: Accessibility tests

### 4. Context Enhancement
- Additional context from requirements, Figma, or API specs improves generation quality
- AI uses context to understand business rules and constraints
- Better context leads to more relevant and comprehensive test cases

## Example Output

```
📸 Found 1 screenshot(s) to process
🚀 Generating test cases from screenshots...
Processing screenshots: 100%|████████████| 1/1 [00:15<00:00, 15.2s/it]
✅ Test case generation completed!
📁 Generated 8 test cases

📊 Generation Summary:
  • Test cases generated: 8
  • Screenshots processed: 1
  • Test types: FUNC, BOUND, NEG, PERM, SEC

📋 Sample Test Cases:
  1. User Login - Valid Credentials [FUNC] [P0]
  2. Password Field - Maximum Length Validation [BOUND] [P1]
  3. Login Button - Invalid Credentials [NEG] [P1]
  4. Admin Panel Access Control [PERM] [P0]
  5. SQL Injection Prevention [SEC] [P1]
  ... and 3 more
```

## Configuration

### Environment Variables

```bash
# Required
export TCG_LLM_API_KEY="your-openai-api-key"

# Optional
export TCG_LLM_MODEL="gpt-4-vision-preview"
export TCG_LLM_TEMPERATURE="0.7"
export TCG_OUTPUT_DIR="./output"
```

### Configuration File

Edit `config.yaml` to customize settings:

```yaml
llm:
  provider: "openai"
  model: "gpt-4-vision-preview"
  temperature: 0.7
  max_tokens: 2000

generation:
  test_case_types: ["FUNC", "BOUND", "NEG", "PERM", "SEC"]
  max_cases_per_requirement: 10
```

## Best Practices

### 1. Screenshot Quality
- Use high-resolution screenshots (at least 1024x768)
- Ensure UI elements are clearly visible
- Include all relevant screens in your workflow

### 2. Context Provision
- Provide clear, descriptive context about the application
- Include business rules and constraints
- Mention specific user roles or permissions

### 3. Test Type Selection
- Start with FUNC, BOUND, and NEG for basic coverage
- Add PERM and SEC for security-critical applications
- Include A11Y for accessibility compliance

### 4. Batch Processing
- Process multiple screenshots together for comprehensive coverage
- Use consistent naming for related screenshots
- Group screenshots by feature or user flow

## Troubleshooting

### Common Issues

**1. API Key Not Set**
```
❌ Error: OpenAI API key not configured
```
Solution: Set the `TCG_LLM_API_KEY` environment variable

**2. No Image Files Found**
```
❌ Error: No image files found in: ./screenshots/
```
Solution: Ensure directory contains supported image formats (PNG, JPG, etc.)

**3. API Rate Limits**
```
❌ Error: API call failed: 429 Too Many Requests
```
Solution: Wait and retry, or use a different API key

**4. Invalid Image Format**
```
❌ Error: Unsupported image format: gif
```
Solution: Convert to supported format (PNG, JPG, JPEG, BMP, TIFF)

### Debug Mode

Enable debug logging for detailed information:

```bash
testcase-gen generate -s screenshot.png --debug
```

## Examples

### Example 1: Login Page
```bash
testcase-gen generate -s login-page.png -c "Banking application login page with username, password, and remember me checkbox"
```

### Example 2: E-commerce Checkout
```bash
testcase-gen generate -s checkout-flow/ -c "E-commerce checkout process with payment forms and validation"
```

### Example 3: Admin Dashboard
```bash
testcase-gen generate -s admin-dashboard.png -c "Admin dashboard with user management, role-based access, and data tables"
```

## Next Steps

1. **Export Test Cases**: Use `testcase-gen export` to save results
2. **Integrate with Test Management**: Export to TestRail, Jira, or Excel
3. **Customize Prompts**: Modify the AI prompts for your specific needs
4. **Batch Processing**: Process multiple screenshots for complete coverage
5. **Review and Refine**: Review generated test cases and provide feedback

## Support

For questions or issues:
- Check the logs for detailed error information
- Use `--debug` flag for verbose output
- Review the configuration file for proper settings
- Ensure API key has sufficient credits and permissions
