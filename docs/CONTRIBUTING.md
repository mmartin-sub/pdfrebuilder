# Contributing to Multi-Format Document Engine

Thank you for your interest in contributing to the Multi-Format Document Engine! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project follows a code of conduct that ensures a welcoming environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [Hatch](https://hatch.pypa.io/) for environment management
- [uv](https://github.com/astral-sh/uv) for fast package management
- Git for version control

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/yourusername/multi-format-document-engine.git
   cd multi-format-document-engine
   ```

2. **Set up development environment**

   ```bash
   # Create and activate development environment
   hatch env create
   hatch shell

   ```

3. **Verify setup**

   ```bash
   # Run tests to ensure everything works
   hatch run test

   # Validate documentation
   make docs-validate
   ```

## Contribution Workflow

### 1. Choose an Issue

- Look for issues labeled `good first issue` for beginners
- Check existing issues and discussions before starting work
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 3. Make Changes

- Follow the coding standards outlined below
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Test Your Changes

```bash
# Run the full test suite
hatch run test

# Run specific tests
hatch run pytest tests/test_your_feature.py

# Test documentation
make docs-validate

# Run linting and formatting
hatch run lint
hatch run format
```

## Coding Standards

### Python Code Style

- **Formatter**: Black with line length 120
- **Linter**: Ruff for style enforcement
- **Type Hints**: Use type hints for all public functions
- **Docstrings**: Follow Google-style docstrings

#### Example Function

```python
def extract_text_elements(
    page: fitz.Page,
    normalize_spacing: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract text elements from a PDF page.

    Args:
        page: PyMuPDF page object to extract text from
        normalize_spacing: Whether to normalize character spacing

    Returns:
        List of text element dictionaries with position and content

    Raises:
        ValueError: If page is invalid or cannot be processed

    Example:
        ```python
        import fitz
        doc = fitz.open("document.pdf")
        elements = extract_text_elements(doc[0])
        ```
    """
    # Implementation here
    pass
```

### Code Organization

- **Modules**: Keep modules focused and cohesive
- **Functions**: Limit functions to 50 lines when possible
- **Classes**: Use composition over inheritance
- **Imports**: Group imports (standard library, third-party, local)

### Error Handling

```python
# Use specific exception types
try:
    result = process_document(doc)
except DocumentParsingError as e:
    logger.error(f"Failed to parse document: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise DocumentProcessingError(f"Processing failed: {e}") from e
```

## Testing Guidelines

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Documentation Tests**: Validate code examples in docs

### Writing Tests

```python
import pytest
from pdfrebuilder.engine.document_parser import DocumentParser

class TestDocumentParser:
    """Test cases for DocumentParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DocumentParser(engine="fitz")

    def test_parse_valid_pdf(self):
        """Test parsing a valid PDF document."""
        # Arrange
        pdf_path = "tests/fixtures/sample.pdf"

        # Act
        result = self.parser.parse(pdf_path)

        # Assert
        assert result is not None
        assert result.metadata["format"] == "PDF"
        assert len(result.pages) > 0

    def test_parse_invalid_file(self):
        """Test parsing an invalid file raises appropriate error."""
        with pytest.raises(DocumentParsingError):
            self.parser.parse("nonexistent.pdf")
```

### Test Coverage

- Aim for 80%+ test coverage
- Focus on critical paths and edge cases
- Include tests for error conditions

## Documentation Guidelines

### Documentation Types

1. **API Documentation**: Auto-generated from docstrings
2. **User Guides**: Step-by-step tutorials
3. **Reference Documentation**: Configuration and CLI reference
4. **Examples**: Working code examples

### Writing Documentation

- **Clear and Concise**: Use simple language
- **Working Examples**: All code examples must execute
- **Up-to-Date**: Keep documentation synchronized with code
- **Accessible**: Consider different skill levels

### Documentation Testing

All documentation is automatically tested:

```bash
# Validate all documentation aspects
make docs-validate
```

## Submitting Changes

### Pull Request Process

1. **Ensure Quality**

   ```bash
   # Run all checks before submitting
   hatch run test
   hatch run lint:lint
   python scripts/validate_docs.py --all
   ```

2. **Create Pull Request**
   - Use descriptive title and description
   - Reference related issues
   - Include screenshots for UI changes
   - Add tests for new functionality

3. **Pull Request Template**

   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement

   ## Testing
   - [ ] Tests pass locally
   - [ ] Added tests for new functionality
   - [ ] Documentation updated

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

### Review Process

- All changes require review from maintainers
- Address feedback promptly and professionally
- Be open to suggestions and improvements
- Maintain a collaborative attitude

## Feature Development Guidelines

### Planning New Features

1. **Create an Issue**: Describe the feature and use case
   - Use the feature request template
   - Include user stories and acceptance criteria
   - Discuss impact on existing functionality
   - Consider backward compatibility

2. **Design Discussion**: Discuss implementation approach
   - Create design document for complex features
   - Consider multiple implementation options
   - Discuss with maintainers and community
   - Plan for testing and documentation

3. **Create Spec**: For complex features, create a specification
   - Use the `.kiro/specs/` directory structure
   - Include requirements, design, and implementation tasks
   - Follow the spec-driven development process
   - Get approval before implementation

4. **Implementation**: Follow the development workflow
   - Create feature branch from develop
   - Implement incrementally with tests
   - Update documentation continuously
   - Request reviews early and often

### Feature Development Checklist

Before submitting a feature PR, ensure:

- [ ] **Requirements**: Clear user stories and acceptance criteria
- [ ] **Design**: Architecture decisions documented
- [ ] **Implementation**: Code follows project standards
- [ ] **Tests**: Comprehensive test coverage (unit, integration, e2e)
- [ ] **Documentation**: API docs, user guides, and examples updated
- [ ] **Performance**: Performance impact assessed
- [ ] **Security**: Security implications reviewed
- [ ] **Backward Compatibility**: Existing functionality preserved

### Engine Abstraction

When adding new engines or formats:

```python
# Follow the engine interface pattern
class NewFormatParser(DocumentParserBase):
    """Parser for new document format."""

    def parse(self, file_path: str) -> UniversalDocument:
        """Parse document and return universal format."""
        # Implementation specific to new format
        pass

    def get_supported_features(self) -> List[str]:
        """Return list of supported features."""
        return ["text_extraction", "image_extraction"]

    def validate_feature_support(self, feature: str) -> bool:
        """Check if feature is supported by this engine."""
        return feature in self.get_supported_features()
```

### Configuration Changes

When modifying configuration formats, ensure that changes are backward compatible whenever possible. If breaking changes are necessary, they must be clearly documented in the release notes.

### Feature Lifecycle Management

#### Alpha Features

- Experimental features behind feature flags
- Limited documentation and support
- May have breaking changes between versions
- Clearly marked as experimental in docs

#### Beta Features

- Stable API but may have minor changes
- Full documentation and examples
- Supported but may have known limitations
- Feedback actively collected from users

#### Stable Features

- Guaranteed API stability
- Full test coverage and documentation
- Production-ready with full support
- Breaking changes only in major versions

#### Deprecated Features

- Marked as deprecated in documentation
- Deprecation warnings in code
- Migration path provided
- Removed after appropriate notice period

## Bug Fixing Guidelines

### Bug Report Analysis

1. **Reproduce the Issue**: Create minimal reproduction case
   - Use the bug report template
   - Create minimal test case that reproduces the issue
   - Test across different environments if applicable
   - Document exact steps to reproduce

2. **Identify Root Cause**: Use debugging tools and logs
   - Use debugger and logging to trace execution
   - Check related code and recent changes
   - Review similar issues and their solutions
   - Consider edge cases and boundary conditions

3. **Design Fix**: Consider edge cases and side effects
   - Plan fix to address root cause, not just symptoms
   - Consider impact on other parts of the system
   - Design for maintainability and clarity
   - Plan for comprehensive testing

4. **Test Thoroughly**: Include regression tests
   - Write test that reproduces the original issue
   - Add tests for edge cases and boundary conditions
   - Ensure existing tests still pass
   - Test fix across different environments

### Bug Fix Process

```python
# Example bug fix with comprehensive testing
def fix_text_spacing_issue(text_blocks: List[Dict]) -> List[Dict]:
    """
    Fix issue with incorrect text spacing normalization.

    Fixes: Issue #123 - Text spacing incorrectly normalized for certain fonts

    The issue occurred when fonts with natural spacing were incorrectly
    identified as having spacing issues, leading to over-normalization.

    Args:
        text_blocks: List of text block dictionaries to process

    Returns:
        List of text blocks with corrected spacing logic

    Raises:
        ValueError: If text_blocks contains invalid data
    """
    for block in text_blocks:
        # Apply fix with proper edge case handling
        if block.get("adjust_spacing") and block.get("font_details"):
            font_name = block["font_details"].get("name", "")

            # Skip normalization for fonts known to have natural spacing
            if font_name in NATURAL_SPACING_FONTS:
                block["adjust_spacing"] = False
                continue

            # Apply more conservative spacing detection
            if _has_excessive_spacing(block["raw_text"]):
                block["text"] = _normalize_spacing(block["raw_text"])
            else:
                block["text"] = block["raw_text"]
                block["adjust_spacing"] = False

    return text_blocks

# Corresponding test
def test_text_spacing_fix_regression():
    """Test that text spacing fix doesn't break existing functionality."""
    # Test case that reproduces the original issue
    test_blocks = [
        {
            "raw_text": "N o r m a l   T e x t",
            "font_details": {"name": "Arial-Regular"},
            "adjust_spacing": True
        },
        {
            "raw_text": "Natural Text",
            "font_details": {"name": "Times-Roman"},
            "adjust_spacing": True
        }
    ]

    result = fix_text_spacing_issue(test_blocks)

    # First block should be normalized (excessive spacing)
    assert result[0]["text"] == "Normal Text"
    assert result[0]["adjust_spacing"] == True

    # Second block should not be normalized (natural spacing)
    assert result[1]["text"] == "Natural Text"
    assert result[1]["adjust_spacing"] == False
```

### Bug Priority and Severity Guidelines

#### Critical (P0)

- Security vulnerabilities
- Data corruption or loss
- Complete system failure
- **Response Time**: Within 24 hours
- **Fix Timeline**: Emergency patch within 48 hours

#### High (P1)

- Major functionality broken
- Performance degradation > 50%
- Incorrect output affecting many users
- **Response Time**: Within 48 hours
- **Fix Timeline**: Next patch release

#### Medium (P2)

- Minor functionality issues
- Performance degradation < 50%
- Workaround available
- **Response Time**: Within 1 week
- **Fix Timeline**: Next minor release

#### Low (P3)

- Cosmetic issues
- Enhancement requests
- Documentation errors
- **Response Time**: Within 2 weeks
- **Fix Timeline**: Next major release

### Bug Fix Documentation

Every bug fix should include:

1. **Issue Reference**: Link to GitHub issue
2. **Root Cause Analysis**: Explanation of what caused the bug
3. **Fix Description**: What was changed and why
4. **Test Coverage**: New tests added to prevent regression
5. **Performance Impact**: If fix affects performance

### Bug Reporting Guidelines

When reporting bugs, include:

#### Required Information

- **Environment**: OS, Python version, package versions
- **Reproduction Steps**: Minimal steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Sample Files**: Minimal test files that demonstrate the issue

#### Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Environment
- OS: [e.g., Ubuntu 20.04, Windows 10, macOS 12]
- Python Version: [e.g., 3.9.7]
- Package Version: [e.g., 1.2.3]
- Dependencies: [relevant package versions]

## Reproduction Steps
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Sample Files
Attach minimal files that reproduce the issue

## Additional Context
Any other relevant information
```

#### Bug Triage Process

1. **Initial Review**: Maintainers review within 48 hours
2. **Reproduction**: Attempt to reproduce the issue
3. **Priority Assignment**: Based on severity and impact
4. **Assignment**: Assign to appropriate maintainer or contributor
5. **Resolution**: Fix implemented and tested
6. **Verification**: Original reporter verifies fix

### Regression Prevention

To prevent regressions:

1. **Comprehensive Testing**: Add tests for the specific bug
2. **Edge Case Coverage**: Test boundary conditions
3. **Integration Testing**: Test interaction with other components
4. **Performance Testing**: Ensure fix doesn't degrade performance
5. **Documentation Updates**: Update docs if behavior changes

## Performance Considerations

### Optimization Guidelines

- **Profile Before Optimizing**: Use profiling tools to identify bottlenecks
- **Measure Impact**: Benchmark performance improvements
- **Memory Efficiency**: Consider memory usage for large documents
- **Caching**: Implement appropriate caching strategies

### Performance Testing

```python
import time
import pytest

def test_large_document_performance():
    """Test performance with large documents."""
    start_time = time.time()

    # Process large document
    result = process_large_document("large_test.pdf")

    processing_time = time.time() - start_time

    # Assert reasonable performance
    assert processing_time < 30.0  # Should complete within 30 seconds
    assert result is not None
```

## Getting Help

### Resources

- **Documentation**: Check docs/ directory
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Learn from existing pull requests

### Communication

- **Be Specific**: Provide detailed information about issues
- **Be Patient**: Maintainers review contributions as time permits
- **Be Collaborative**: Work together to improve the project

## Documentation Maintenance Procedures

### Documentation Quality Metrics

The project maintains high documentation quality through automated metrics and validation:

#### Coverage Metrics

- **API Documentation Coverage**: Target 90%+ of public APIs documented
- **Code Example Coverage**: All major features must have working examples
- **Configuration Coverage**: All configuration options documented with examples
- **Test Coverage**: Documentation tests must maintain 80%+ pass rate

#### Quality Thresholds

```bash
# Check current documentation metrics
python scripts/validate_docs.py --coverage

# Quality gates (enforced in CI):
# - API documentation coverage: >= 90%
# - Code example validation: >= 95% pass rate
# - Configuration example validation: >= 100% pass rate
# - Link validation: >= 100% pass rate
```

#### Automated Quality Checks

- **Daily**: Automated link validation and example testing
- **Weekly**: Full documentation coverage analysis
- **Per PR**: Complete validation suite runs on all changes
- **Release**: Comprehensive documentation audit

### Documentation Update Workflows

#### Automatic Updates

The following documentation is automatically updated:

1. **API Documentation**: Generated from docstrings on code changes
2. **Configuration Reference**: Updated when `src/settings.py` changes
3. **CLI Reference**: Updated when `main.py` or CLI modules change
4. **Example Validation**: All examples tested on every commit

#### Manual Update Triggers

Contributors should update documentation when:

- Adding new features or APIs
- Changing configuration options
- Modifying CLI interfaces
- Fixing bugs that affect documented behavior
- Adding new examples or tutorials

#### Documentation Review Process

1. **Automated Validation**: All PRs trigger documentation validation
2. **Peer Review**: Documentation changes require maintainer review
3. **User Testing**: Complex guides tested by community members
4. **Quarterly Audit**: Comprehensive documentation review every quarter

### Maintenance Responsibilities

#### Core Maintainers

- Review documentation PRs within 48 hours
- Maintain documentation infrastructure and tooling
- Conduct quarterly documentation audits
- Update contribution guidelines as needed

#### Contributors

- Update documentation for code changes
- Test examples before submitting
- Follow documentation style guidelines
- Report documentation issues and gaps

#### Community

- Provide feedback on documentation clarity
- Suggest improvements and corrections
- Contribute examples and use cases
- Help with translation and localization

## Automated Documentation Workflows

### Continuous Integration

The project uses automated workflows to maintain documentation quality:

```yaml
# Documentation validation runs on:
# - Every push to main/develop branches
# - Every pull request
# - Daily scheduled runs
# - Manual triggers

# Validation includes:
# - Code example execution
# - API reference validation
# - Configuration example testing
# - Link checking
# - Coverage reporting
```

### Quality Gates

Pull requests must pass these documentation quality gates:

1. **Code Examples**: All examples must execute successfully
2. **API References**: All referenced APIs must exist and match signatures
3. **Configuration**: All config examples must be valid
4. **Links**: All internal links must resolve correctly
5. **Coverage**: New code must include appropriate documentation

### Automated Fixes

Some documentation issues are automatically fixed:

- **Link Updates**: Internal links updated when files move
- **API Signatures**: Method signatures updated from code changes
- **Example Formatting**: Code examples auto-formatted with Black
- **Broken Link Detection**: Automated detection and notification

## Documentation Contribution Guidelines

### Documentation Standards

All documentation contributions must meet these standards:

#### Content Quality

- **Accuracy**: All information must be current and correct
- **Completeness**: Cover all aspects of the topic thoroughly
- **Clarity**: Use clear, concise language appropriate for the target audience
- **Consistency**: Follow established terminology and formatting conventions

#### Code Examples

- **Executable**: All code examples must run successfully
- **Complete**: Include necessary imports and setup code
- **Tested**: Examples are automatically tested in CI/CD
- **Commented**: Explain complex or non-obvious code sections

#### API Documentation

- **Comprehensive**: Document all public classes, methods, and functions
- **Type Hints**: Include proper type annotations
- **Examples**: Provide usage examples for complex APIs
- **Error Handling**: Document exceptions and error conditions

### Documentation Review Process

1. **Self-Review**: Check your documentation against the standards above
2. **Automated Validation**: All documentation is automatically validated
3. **Peer Review**: Maintainers review all documentation changes
4. **User Testing**: Complex guides may be tested by community members

### Documentation Maintenance Responsibilities

#### For Contributors

- Update documentation when making code changes
- Test all code examples before submitting
- Follow the documentation style guide
- Report documentation issues and gaps

#### For Maintainers

- Review documentation PRs within 48 hours
- Maintain documentation infrastructure
- Conduct quarterly documentation audits
- Update contribution guidelines as needed

## Quality Assurance

### Automated Quality Checks

The project maintains documentation quality through:

- **Daily**: Link validation and example testing
- **Weekly**: Full documentation coverage analysis
- **Per PR**: Complete validation suite
- **Release**: Comprehensive documentation audit

### Quality Metrics

Documentation quality is measured by:

- **API Coverage**: Target 90%+ of public APIs documented
- **Example Pass Rate**: Target 95%+ of examples working
- **Configuration Coverage**: Target 100% of config options documented
- **Link Validation**: Target 100% of internal links working

### Quality Gates

Pull requests must pass these quality gates:

1. **Code Examples**: All examples execute successfully
2. **API References**: All referenced APIs exist and match signatures
3. **Configuration**: All config examples are valid
4. **Links**: All internal links resolve correctly
5. **Coverage**: New code includes appropriate documentation

## Recognition

Contributors are recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor statistics
- Documentation contributor hall of fame
- Annual contributor appreciation posts

### Special Recognition

- **Documentation Champions**: Contributors who significantly improve docs
- **Example Masters**: Contributors who create excellent working examples
- **Quality Guardians**: Contributors who help maintain documentation quality
- **Community Helpers**: Contributors who assist others with documentation

## Getting Support

### Resources

- **Documentation**: Check docs/ directory first
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Learn from existing pull requests

### Communication Guidelines

- **Be Specific**: Provide detailed information about issues
- **Be Patient**: Maintainers review contributions as time permits
- **Be Collaborative**: Work together to improve the project
- **Be Respectful**: Follow the code of conduct in all interactions

Thank you for contributing to the Multi-Format Document Engine!
