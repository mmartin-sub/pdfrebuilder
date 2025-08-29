# Font Management System Tests

This directory contains comprehensive tests for the Font Management System, which provides font validation, substitution tracking, and reporting capabilities for the Multi-Format Document Engine.

## Configurable Output Directory

All test outputs (temporary files, downloaded fonts, test reports) can be configured to go to a specific directory:

### Environment Variable

```bash
export TEST_OUTPUT_DIR=/path/to/test/output
python -m tests.test_font_management_suite
```

### Command Line Options

```bash
# Using the test runner script
python tests/run_font_tests.py --output-dir /path/to/test/output

# Using the test suite directly
python -m tests.test_font_management_suite --output-dir /path/to/test/output
```

### Default Behavior

- Default output directory: `tests/resources/`
- Directory structure:

  ```
  tests/resources/
  ├── temp/           # Temporary test files (organized by test name)
  ├── fonts/          # Downloaded and test font files
  └── reports/        # Test reports and logs
  ```

### CLI Features

```bash
# Run tests with custom output directory
python tests/run_font_tests.py --output-dir ./custom_output

# Clean output directory before running tests
python tests/run_font_tests.py --clean-output

# Generate detailed test reports
python tests/run_font_tests.py --generate-report

# Verbose output
python tests/run_font_tests.py --verbose

# List all available tests
python tests/run_font_tests.py --list-tests
```

## Test Files Overview

### Core Font Management Tests

- **`test_font_manager.py`** - Tests for basic font management functionality
  - Font discovery and scanning
  - Font coverage checking
  - Font registration and caching
  - Google Fonts integration
  - Error handling and fallback mechanisms

- **`test_font_substitution.py`** - Tests for font substitution logic
  - Glyph coverage analysis
  - Fallback font selection
  - Substitution tracking and logging

- **`test_google_fonts_integration.py`** - Tests for Google Fonts API integration
  - Font downloading from Google Fonts
  - CSS parsing and font URL extraction
  - Error handling for network issues
  - Font file organization and storage

### Font Validation Tests

- **`test_font_validation_integration.py`** - Integration tests for font validation system
  - Document font validation
  - Font availability checking
  - Substitution tracking integration
  - Validation report generation
  - HTML report generation with font information

## Font Validation Features Tested

### 1. Font Availability Checking (Requirement 5.1)

- ✅ Verifies that required fonts are available in the system
- ✅ Identifies missing fonts and provides clear messaging
- ✅ Distinguishes between standard PDF fonts and custom fonts
- ✅ Scans local font directories for available fonts

### 2. Font Substitution Information (Requirement 5.2)

- ✅ Tracks font substitutions when they occur
- ✅ Records original font, substituted font, and reason for substitution
- ✅ Associates substitutions with specific text elements and pages
- ✅ Includes substitution information in validation reports

### 3. Clear Font-Related Messaging (Requirement 5.3)

- ✅ Provides informative messages about missing fonts
- ✅ Explains reasons for font substitutions
- ✅ Offers recommendations for resolving font issues
- ✅ Uses appropriate severity levels (info, warning, error)

### 4. Font Information in Validation Reports (Requirement 5.4)

- ✅ Includes comprehensive font validation data in JSON reports
- ✅ Generates HTML reports with font validation sections
- ✅ Shows font substitution tables with detailed information
- ✅ Displays font coverage issues and missing characters
- ✅ Provides font validation summary and status

## Test Coverage

The test suite covers:

- **Font Discovery**: 8 test cases
- **Font Coverage**: 5 test cases
- **Font Registration**: 10 test cases
- **Google Fonts Integration**: 16 test cases
- **Font Substitution**: 12 test cases
- **Font Validation Integration**: 14 test cases

**Total: 68 test cases** covering all aspects of the font management system.

## Running the Tests

### Run All Font Tests

```bash
hatch run test tests/test_font_manager.py tests/test_font_substitution.py tests/test_font_validation_integration.py tests/test_google_fonts_integration.py
```

### Run Individual Test Files

```bash
# Basic font management
hatch run test tests/test_font_manager.py

# Font substitution logic
hatch run test tests/test_font_substitution.py

# Font validation integration
hatch run test tests/test_font_validation_integration.py

# Google Fonts integration
hatch run test tests/test_google_fonts_integration.py
```

### Run Specific Test Cases

```bash
# Test font availability checking
hatch run test tests/test_font_validation_integration.py::TestFontValidationIntegration::test_font_availability_checking

# Test font substitution tracking
hatch run test tests/test_font_validation_integration.py::TestFontValidationIntegration::test_font_substitution_tracking

# Test validation report generation
hatch run test tests/test_font_validation_integration.py::TestFontValidationIntegration::test_validation_report_with_font_data
```

## Font Validation Demo

A demonstration script is available to show the font validation system in action:

```bash
python tests/demos/demo_font_validation.py
```

This script:

- Creates a sample document with various font requirements
- Performs font validation and shows results
- Simulates font substitutions
- Generates comprehensive validation reports
- Saves reports for inspection

## Test Data and Fixtures

The tests use:

- Temporary directories for isolated testing
- Mock font files and configurations
- Sample layout configurations with various font requirements
- Simulated font substitution scenarios
- Mock Google Fonts API responses

## Integration with Document Processing

The font validation system integrates with:

- **Document Validation Pipeline**: Adds font validation to visual comparison
- **Validation Reports**: Includes font information in JSON and HTML reports
- **Font Registration**: Tracks substitutions during font registration
- **Error Handling**: Provides clear messaging for font-related issues

## Error Handling Coverage

Tests verify proper handling of:

- Missing font files
- Corrupted font files
- Network errors during Google Fonts download
- Invalid font configurations
- Font coverage issues
- Font loading errors

## Validation Report Features

The font validation system adds these sections to validation reports:

### JSON Reports

- `metadata.font_validation` object with complete font validation data
- Font requirements, availability, and missing fonts lists
- Detailed substitution information with element and page references
- Font coverage issues with missing character details
- Validation messages with appropriate severity levels

### HTML Reports

- **Font Validation Status** section with pass/fail indicator
- **Font Substitutions** table showing original → substituted mappings
- **Font Coverage Issues** table with missing character details
- **Missing Fonts** list with clear highlighting
- **Font Validation Messages** with formatted severity levels

This comprehensive test suite ensures that the font validation system meets all requirements and provides reliable font handling for document processing workflows.
