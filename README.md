# Test Case Generator

A comprehensive tool for generating test cases from requirements, prototypes, and screenshots.

## Overview

The Test Case Generator is a powerful CLI and web application that automatically generates comprehensive test cases by analyzing:

- **Requirements documents** (Confluence, Word, PDF, plain text)
- **Figma prototypes** and design specifications
- **Screenshots** and images (with OCR)
- **API specifications** (OpenAPI/Swagger)

## Features

### 🚀 Core Capabilities
- **Multi-format parsing**: Extract requirements from various document formats
- **AI-powered generation**: Use LLMs to generate comprehensive test cases
- **Gap analysis**: Identify missing test coverage and provide recommendations
- **Multiple export formats**: Export to TestRail, Jira, Excel, and more
- **Coverage tracking**: Monitor test coverage across requirements and components

### 📋 Test Case Types
- **Functional tests** (FUNC): Core functionality testing
- **Boundary value tests** (BOUND): Edge case and limit testing
- **Negative tests** (NEG): Error handling and invalid input testing
- **Permission tests** (PERM): Authorization and access control testing
- **Security tests** (SEC): Security vulnerability testing
- **Performance tests** (PERF): Load and performance testing
- **Accessibility tests** (A11Y): WCAG compliance testing

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd simplify

# Install dependencies
pip install -e .

# Or using uv (recommended)
uv sync
```

### Basic Usage

```bash
# Initialize a new project
testcase-gen init

# Generate test cases from requirements
testcase-gen generate -r requirements.pdf

# Generate from Figma prototype
testcase-gen generate -f abc123def456

# Analyze test coverage
testcase-gen analyze -p project.json

# Export to TestRail
testcase-gen export -i test_cases.json --format testrail --project-id 123
```

### Configuration

Create a configuration file:

```bash
# Generate default config
testcase-gen init -o config.yaml
```

Edit `config.yaml` to configure:
- LLM provider and API keys
- External integrations (TestRail, Jira, Figma)
- Parsing options
- Generation settings

## Architecture

The system follows a 9-layer architecture:

1. **Collection Layer**: Input from various sources
2. **Parsing Layer**: Extract structured data
3. **Semantic Modeling Layer**: Unified domain model
4. **Generation Layer**: AI and rule-based test case creation
5. **Gap Analysis Layer**: Coverage analysis and recommendations
6. **Management Layer**: Test case library and versioning
7. **Collaboration Layer**: Task assignment and progress tracking
8. **Integration Layer**: External tool integrations
9. **Metrics Layer**: Analytics and feedback

## Development

### Project Structure

```
src/testcase_generator/
├── cli/                    # Command-line interface
├── core/                   # Core business logic
│   ├── models.py          # Domain models
│   ├── parsers/           # Input parsers
│   ├── generators/        # Test case generators
│   └── analyzers/         # Gap analysis tools
├── utils/                 # Utilities and helpers
└── ui/                    # Web interface (future)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=testcase_generator

# Run specific test file
pytest tests/test_basic_structure.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[Add your license here]

## Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation
- Contact the maintainers

---

**Status**: 🚧 In Development - Phase 1 (CLI) completed, Phase 2 (Web UI) in progress
