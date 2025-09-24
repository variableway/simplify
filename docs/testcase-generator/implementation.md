# Test Case Generator Implementation Plan

## Project Overview

Based on the comprehensive requirements in `testcase-generator.md`, this project implements a complete solution for generating test cases from requirements, prototypes, and screenshots. The implementation follows a phased approach: CLI application first, then UI interface.

## Architecture Overview

The system follows the 9-layer architecture defined in the requirements:

1. **采集层 (Collection Layer)**: Requirements, prototypes, API specs, screenshots
2. **解析层 (Parsing Layer)**: Text parsing, prototype parsing, OCR
3. **语义建模层 (Semantic Modeling Layer)**: Unified domain model
4. **生成层 (Generation Layer)**: LLM + rule engine for test case generation
5. **缺口分析层 (Gap Analysis Layer)**: Coverage matrix, constraint coverage, parameter combinations
6. **管理层 (Management Layer)**: Test case library, versioning, execution records
7. **协作层 (Collaboration Layer)**: Task assignment, progress tracking
8. **集成层 (Integration Layer)**: Jira, TestRail, Git, Slack, CI
9. **度量与反馈层 (Metrics & Feedback Layer)**: Defect analysis, coverage metrics

## Project Structure

```
simplify/
├── src/
│   ├── testcase_generator/
│   │   ├── __init__.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # CLI entry point
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── generate.py      # Generate test cases
│   │   │   │   ├── analyze.py       # Gap analysis
│   │   │   │   ├── export.py        # Export to various formats
│   │   │   │   └── manage.py        # Test case management
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       └── formatters.py    # Output formatting
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # Domain models
│   │   │   ├── parsers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── requirements.py  # Requirements parsing
│   │   │   │   ├── figma.py         # Figma API integration
│   │   │   │   ├── screenshots.py   # OCR and image analysis
│   │   │   │   └── api_specs.py     # OpenAPI parsing
│   │   │   ├── generators/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── llm_generator.py # LLM-based generation
│   │   │   │   ├── rule_engine.py   # Rule-based generation
│   │   │   │   └── templates.py     # Prompt templates
│   │   │   ├── analyzers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── coverage.py      # Coverage analysis
│   │   │   │   ├── gap_analysis.py  # Gap detection
│   │   │   │   └── constraints.py   # Constraint coverage
│   │   │   └── integrations/
│   │   │       ├── __init__.py
│   │   │       ├── testrail.py      # TestRail integration
│   │   │       ├── jira.py          # Jira integration
│   │   │       └── figma_api.py     # Figma API client
│   │   ├── ui/
│   │   │   ├── __init__.py
│   │   │   ├── web/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── app.py           # Flask/FastAPI app
│   │   │   │   ├── templates/       # HTML templates
│   │   │   │   ├── static/          # CSS/JS assets
│   │   │   │   └── routes/          # API routes
│   │   │   └── components/          # Reusable UI components
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── config.py            # Configuration management
│   │       ├── logging.py           # Logging setup
│   │       └── validators.py        # Input validation
│   └── tests/
│       ├── __init__.py
│       ├── unit/
│       ├── integration/
│       └── fixtures/
├── docs/
│   ├── api/                         # API documentation
│   ├── user_guide/                  # User documentation
│   └── development/                 # Development docs
├── config/
│   ├── config.yaml                  # Main configuration
│   ├── prompts/                     # LLM prompt templates
│   └── templates/                   # Output templates
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Phase 1: CLI Application Development

### 🎯 **Screenshot-Based Approach (Primary Focus)**

The implementation focuses on a **screenshot-first approach** where users can:
1. **Upload screenshots** directly to AI vision APIs (OpenAI GPT-4 Vision)
2. **Generate test cases** automatically from visual analysis
3. **Add context** from requirements, Figma, or API specs for better results
4. **Export results** to various formats (Excel, JSON, TestRail)

**Key Benefits:**
- ✅ **Simple workflow**: Just upload screenshots and get test cases
- ✅ **AI-powered analysis**: Uses advanced vision models for comprehensive coverage
- ✅ **No complex parsing**: Avoids complex document parsing and OCR
- ✅ **Visual understanding**: AI can understand UI elements, flows, and interactions
- ✅ **Context-aware**: Additional context improves generation quality

### Task Breakdown

#### 1.1 Project Setup and Core Infrastructure (Week 1) ✅ COMPLETED
- [x] **1.1.1** Set up Python project structure with proper packaging
  - Created modular package structure with clear separation of concerns
  - Implemented proper `__init__.py` files with exports
  - Set up CLI module structure with commands
- [x] **1.1.2** Configure development environment (poetry/uv, pre-commit, testing)
  - Updated `pyproject.toml` with comprehensive dependencies
  - Added development tools: black, isort, flake8, mypy, pytest
  - Created `.pre-commit-config.yaml` for code quality
  - Configured pytest with coverage reporting
- [x] **1.1.3** Create base domain models (Requirement, Component, TestCase, etc.)
  - Implemented comprehensive Pydantic models for all domain entities
  - Added enums for types, priorities, and constraints
  - Included validation and serialization capabilities
- [x] **1.1.4** Implement configuration management system
  - Created flexible configuration system with YAML support
  - Added environment variable integration
  - Implemented validation and error handling
  - Created default configuration template
- [x] **1.1.5** Set up logging and error handling framework
  - Implemented structured logging with colored console output
  - Added file rotation and multiple log levels
  - Created comprehensive validation utilities
  - Set up error handling and context logging

#### 1.2 Data Collection and Parsing Layer (Week 2) ✅ COMPLETED
- [x] **1.2.1** Implement requirements parser (Confluence, Word, PDF, plain text)
  - ✅ Created simple text-based requirements parser
  - ✅ Supports basic requirement ID extraction and priority mapping
  - ✅ Handles plain text input with simple formatting
- [x] **1.2.2** Implement Figma API integration
  - ✅ Created basic Figma API client for component extraction
  - ✅ Extracts components, properties, and constraints
  - ✅ Maps Figma node types to component types
- [x] **1.2.3** Implement screenshot AI vision integration
  - ✅ **MAIN FEATURE**: AI-powered screenshot analysis using OpenAI Vision API
  - ✅ Encodes images to base64 for API upload
  - ✅ Generates comprehensive test cases from visual analysis
  - ✅ Supports multiple image formats and batch processing
- [x] **1.2.4** Implement API specification parser (OpenAPI/Swagger)
  - ✅ Created basic OpenAPI/Swagger parser
  - ✅ Extracts endpoints, parameters, and generates test cases
  - ✅ Supports JSON and YAML formats

#### 1.3 Core Modules Implementation ✅ COMPLETED
- [x] **1.3.1** Implement Config module
  - ✅ Created simplified configuration interface wrapping BaseConfig
  - ✅ Provides easy access to LLM, output, and generation settings
  - ✅ Supports configuration validation and error handling
- [x] **1.3.2** Implement TestCaseGenerator core class
  - ✅ Main orchestrator for test case generation from multiple sources
  - ✅ Integrates all parsers (screenshots, requirements, figma, api)
  - ✅ Supports comprehensive generation with context fusion
  - ✅ Includes duplicate removal and quality control
- [x] **1.3.3** Implement ProjectManager class
  - ✅ Manages projects, test cases, and related data
  - ✅ Supports project creation, loading, and saving
  - ✅ Provides export functionality (JSON, CSV, Excel)
  - ✅ Includes project statistics and summary generation

#### 1.3 Semantic Modeling and Data Fusion (Week 2-3)
- [ ] **1.3.1** Create unified domain model for all input sources
- [ ] **1.3.2** Implement data fusion logic to merge parsed data
- [ ] **1.3.3** Create constraint extraction and validation system
- [ ] **1.3.4** Implement flow reconstruction from components

#### 1.4 Test Case Generation Engine (Week 3-4)
- [ ] **1.4.1** Implement LLM integration (OpenAI, Anthropic, local models)
- [ ] **1.4.2** Create prompt templates for different test case types
  - Functional test cases
  - Boundary value testing
  - Negative testing
  - Security testing
  - Performance testing
- [ ] **1.4.3** Implement rule-based generation for specific patterns
- [ ] **1.4.4** Create test case classification and prioritization system

#### 1.5 Gap Analysis and Coverage (Week 4-5)
- [ ] **1.5.1** Implement requirement coverage analysis
- [ ] **1.5.2** Create constraint coverage checking
- [ ] **1.5.3** Implement parameter combination analysis (Pairwise testing)
- [ ] **1.5.4** Create state transition coverage analysis
- [ ] **1.5.5** Implement defect-based gap analysis

#### 1.6 CLI Interface Development (Week 5-6) ✅ COMPLETED
- [x] **1.6.1** Implement CLI framework using Typer
  - ✅ Migrated from Click to Typer for better type safety and modern CLI experience
  - ✅ Implemented comprehensive command structure with subcommands
- [x] **1.6.2** Create command structure:
  - ✅ `generate`: Generate test cases from screenshots using AI vision
  - ✅ `analyze`: Perform gap analysis and coverage checking
  - ✅ `export`: Export test cases to various formats (Excel, CSV, JSON, TestRail)
  - ✅ `manage`: Test case management operations (create, show, list, backup, cleanup)
- [x] **1.6.3** Implement interactive mode for guided workflows
  - ✅ Added progress bars and verbose output options
  - ✅ Implemented dry-run mode for testing
- [x] **1.6.4** Add progress indicators and verbose output options
  - ✅ Integrated Typer progress bars for long-running operations
  - ✅ Added comprehensive logging and error handling

#### 1.7 Export and Integration (Week 6-7)
- [ ] **1.7.1** Implement TestRail API integration
- [ ] **1.7.2** Implement Jira integration for requirements and defects
- [ ] **1.7.3** Create Excel/CSV export functionality
- [ ] **1.7.4** Implement JSON/XML export for data exchange
- [ ] **1.7.5** Create import functionality for existing test cases

#### 1.8 Testing and Documentation (Week 7-8)
- [ ] **1.8.1** Write comprehensive unit tests
- [ ] **1.8.2** Create integration tests for external APIs
- [ ] **1.8.3** Write CLI documentation and help text
- [ ] **1.8.4** Create user guide and examples
- [ ] **1.8.5** Performance testing and optimization

## Phase 2: Web UI Development

### Task Breakdown

#### 2.1 Web Application Foundation (Week 9-10)
- [ ] **2.1.1** Set up web framework (FastAPI or Flask)
- [ ] **2.1.2** Create API endpoints for all CLI functionality
- [ ] **2.1.3** Implement authentication and authorization
- [ ] **2.1.4** Set up database for user data and project management

#### 2.2 Frontend Development (Week 10-12)
- [ ] **2.2.1** Create responsive web interface using modern framework
- [ ] **2.2.2** Implement file upload for requirements, prototypes, screenshots
- [ ] **2.2.3** Create interactive test case generation interface
- [ ] **2.2.4** Build gap analysis dashboard with visualizations
- [ ] **2.2.5** Implement test case management interface

#### 2.3 Advanced Features (Week 12-14)
- [ ] **2.3.1** Real-time collaboration features
- [ ] **2.3.2** Advanced filtering and search capabilities
- [ ] **2.3.3** Custom report generation
- [ ] **2.3.4** Integration with external tools (Slack, email notifications)
- [ ] **2.3.5** Version control and change tracking

## Technical Specifications

### Dependencies

#### Core Dependencies
- `click` or `typer`: CLI framework
- `pydantic`: Data validation and serialization
- `requests`: HTTP client for API integrations
- `openai` or `anthropic`: LLM integration
- `pandas`: Data manipulation and analysis
- `pyyaml`: Configuration management

#### Parsing Dependencies
- `beautifulsoup4`: HTML/XML parsing
- `python-docx`: Word document parsing
- `PyPDF2` or `pdfplumber`: PDF parsing
- `tesseract` or `paddleocr`: OCR functionality
- `opencv-python`: Image processing

#### Web Dependencies
- `fastapi` or `flask`: Web framework
- `uvicorn`: ASGI server
- `jinja2`: Template engine
- `sqlalchemy`: Database ORM
- `alembic`: Database migrations

### Configuration Schema

```yaml
# config/config.yaml
llm:
  provider: "openai"  # openai, anthropic, local
  api_key: "${LLM_API_KEY}"
  model: "gpt-4"
  temperature: 0.7

integrations:
  testrail:
    url: "${TESTRAIL_URL}"
    username: "${TESTRAIL_USERNAME}"
    api_key: "${TESTRAIL_API_KEY}"
  
  jira:
    url: "${JIRA_URL}"
    username: "${JIRA_USERNAME}"
    api_token: "${JIRA_API_TOKEN}"
  
  figma:
    api_key: "${FIGMA_API_KEY}"

parsing:
  requirements:
    formats: ["confluence", "word", "pdf", "text"]
    priority_keywords: ["must", "should", "could", "won't"]
  
  figma:
    file_id: "${FIGMA_FILE_ID}"
    components: ["button", "input", "dropdown", "checkbox"]

generation:
  test_case_types: ["FUNC", "BOUND", "NEG", "PERM", "SEC", "PERF"]
  priorities: ["P0", "P1", "P2"]
  max_cases_per_requirement: 10
```

## Success Metrics

### Phase 1 (CLI) Success Criteria
- [ ] Generate 80%+ of main flow test cases in < 10 minutes
- [ ] Achieve 95%+ requirement-test case traceability
- [ ] Support 5+ input formats (Confluence, Figma, PDF, etc.)
- [ ] Export to 3+ management platforms (TestRail, Jira, Excel)
- [ ] Process 100+ requirements without performance degradation

### Phase 2 (UI) Success Criteria
- [ ] Non-technical users can generate test cases in < 5 minutes
- [ ] Real-time collaboration with 5+ concurrent users
- [ ] 99%+ uptime for web application
- [ ] Mobile-responsive interface
- [ ] Integration with 3+ external tools

## Risk Mitigation

### Technical Risks
- **LLM API costs**: Implement caching and batch processing
- **API rate limits**: Add retry logic and rate limiting
- **Data privacy**: Support local LLM models and data encryption
- **Performance**: Implement async processing and caching

### Business Risks
- **User adoption**: Create comprehensive documentation and training
- **Integration complexity**: Start with simple integrations, expand gradually
- **Maintenance overhead**: Design modular architecture for easy updates

## Next Steps

1. **Immediate Actions**:
   - Set up development environment
   - Create project structure
   - Implement basic domain models
   - Set up CI/CD pipeline

2. **Week 1 Deliverables**:
   - Working CLI skeleton
   - Basic requirements parser
   - Configuration system
   - Initial test framework

3. **Month 1 Goal**:
   - Complete CLI application with core functionality
   - Generate test cases from real requirements
   - Export to TestRail/Excel

4. **Month 2 Goal**:
   - Launch web UI
   - User testing and feedback
   - Performance optimization

This implementation plan provides a structured approach to building a comprehensive test case generation system that addresses all requirements from the original document while maintaining flexibility for future enhancements.
