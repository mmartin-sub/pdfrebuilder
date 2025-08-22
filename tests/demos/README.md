# Demonstration Scripts

This directory contains interactive demonstration scripts that showcase various features and capabilities of the PDF Layout Extractor and Rebuilder system.

## Available Demonstrations

### Font Validation Demo (`demo_font_validation.py`)

Demonstrates the font validation system functionality including:

- **Font Availability Checking**: Verifies which fonts are available in the system
- **Font Substitution Tracking**: Shows how missing fonts are substituted
- **Validation Report Generation**: Creates comprehensive validation reports
- **Font Coverage Analysis**: Analyzes font coverage for document content

**Usage:**

To run the font validation demonstration, execute the following command from the project root:

```bash
python tests/demos/demo_font_validation.py
```

**Output:**

- Console output showing the validation process.
- Generated validation reports in the `output/tests/font_validation_demo_reports/` directory, including both JSON and HTML formats with detailed font analysis.

## Adding New Demonstrations

When adding new demonstration scripts:

1. Create the script in this directory with a descriptive name
2. Include comprehensive docstrings explaining the demonstration
3. Provide clear console output showing the process
4. Generate sample outputs or reports when applicable
5. Update this README with the new demonstration details

## Purpose

These demonstrations serve multiple purposes:

- **Feature Showcase**: Demonstrate system capabilities to users
- **Integration Testing**: Verify that complex workflows function correctly
- **Documentation**: Provide working examples of system usage
- **Development Aid**: Help developers understand system behavior
