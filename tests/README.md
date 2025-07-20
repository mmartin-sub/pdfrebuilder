# Tests Directory

This directory contains all test files, utilities, and related artifacts for the PDF Layout Extractor and Rebuilder project.

## Directory Structure

```
tests/
├── README.md                   # This file
├── conftest.py                # Pytest configuration and fixtures
├── unit/                      # Unit tests for individual components
│   ├── __init__.py
│   ├── test_configuration.py
│   ├── test_engine_interface.py
│   ├── test_engine_selection.py
│   ├── test_settings.py
│   ├── test_utils.py
│   ├── test_tools_init.py
│   ├── test_models_universal_idm.py
│   ├── test_directory_utils.py
│   ├── test_engine_logging.py
│   ├── test_engine_modules.py
│   ├── test_validation_report.py
│   └── test_logging.py
├── integration/               # Integration tests between components
│   ├── __init__.py
│   ├── test_cross_engine_compatibility.py
│   ├── test_engine_combinations.py
│   ├── test_engine_selection_integration.py
│   ├── test_fitz_reportlab_pipeline.py
│   ├── test_visual_validation.py
│   ├── test_visual_validation_basic.py
│   ├── test_batch_modifier.py
│   ├── test_compare_pdfs_visual.py
│   ├── test_pdf_extraction.py
│   ├── test_psd_extraction.py
│   ├── test_recreate_pdf_from_config.py
│   ├── test_render*.py
│   ├── test_reportlab_engine.py
│   ├── test_wand_*.py
│   ├── test_fitz_*.py
│   ├── test_generate_debug_pdf_layers.py
│   ├── test_both_null_edge_case.py
│   ├── test_debug_pdf_null_color.py
│   └── test_null_color_visual.py
├── performance/               # Performance and benchmarking tests
│   ├── __init__.py
│   ├── test_benchmarks.py
│   ├── test_engine_benchmarks.py
│   ├── test_memory_usage.py
│   └── test_processing_speed.py
├── e2e/                       # End-to-end tests
│   ├── __init__.py
│   ├── test_e2e_human_review.py
│   ├── test_e2e_pdf_pipeline.py
│   └── test_e2e_pdf_regeneration.py
├── security/                  # Security-focused tests
│   ├── __init__.py
│   ├── test_enhanced_security.py
│   ├── test_secure_execution.py
│   ├── test_security_modules.py
│   ├── test_security_utils.py
│   ├── test_subprocess_compatibility.py
│   ├── test_subprocess_security_comprehensive.py
│   ├── test_hash_security_validator.py
│   ├── test_xml_security*.py
│   ├── test_bandit_configuration_validation.py
│   ├── test_validation_report_security.py
│   └── test_xml_backward_compatibility.py
├── documentation/             # Documentation validation tests
│   ├── __init__.py
│   ├── test_api_documentation.py
│   ├── test_api_validator.py
│   ├── test_comprehensive_documentation.py
│   ├── test_documentation_*.py
│   └── test_coverage_improvements.py
├── font/                      # Font-related tests
│   ├── __init__.py
│   ├── test_font_*.py
│   └── test_google_fonts_integration.py
├── utils/                     # Test utilities and runners
│   ├── __init__.py
│   ├── run_*.py
│   ├── verify_*.py
│   ├── validate_*.py
│   ├── font_error_test_utils.py
│   ├── debug_security_test_kill.py
│   ├── test-debug-20250720.py
│   └── wip_test_xml_security_monitoring.py
├── fixtures/                  # Test configuration files and data
│   ├── manual_overrides.json.test
│   ├── test_*.json
│   ├── config.py
│   ├── security_test_config.py
│   └── test_text_render.pdf
├── demos/                     # Demonstration scripts
├── output/                    # Test output files and artifacts
├── sample/                    # Sample test data
├── human_review_outputs/      # Human review test outputs
├── temp_e2e_output/          # Temporary E2E test outputs
└── backward_compatibility_reports/ # Backward compatibility test reports
```

## Organization Standards

### Test Categories

1. **unit/** - Unit tests for individual components and modules
2. **integration/** - Integration tests between components and systems
3. **performance/** - Performance benchmarking and memory usage tests
4. **e2e/** - End-to-end workflow tests
5. **security/** - Security-focused tests and vulnerability checks
6. **documentation/** - Documentation validation and API tests
7. **font/** - Font-related functionality tests
8. **utils/** - Test utilities, runners, and helper scripts
9. **fixtures/** - Test configuration files, data, and artifacts

### File Placement Rules

1. **All test files** must be placed in the appropriate category subdirectory
2. **Test utilities and runners** belong in `tests/utils/`
3. **Demo scripts** should be in `tests/demos/` subdirectory
4. **Test fixtures and data** should be in `tests/fixtures/` subdirectory
5. **Test output files** should be in `tests/output/` or similar subdirectories

### Naming Conventions

- Test files: `test_*.py`
- Test utilities: descriptive names (e.g., `run_tests.py`, `conftest.py`)
- Demo scripts: `demo_*.py` in `tests/demos/`
- Configuration files: `*.json`, `*.json5` in `tests/fixtures/`

### Pre-commit Hooks

A pre-commit hook is configured to prevent:

- Test files (`test_*.py`) from being added to the root directory
- Test directories from being created in the root directory
- Test runner scripts from being placed in `scripts/` directory

This ensures consistent organization and follows Python project conventions.

## Running Tests

### Individual Tests

Run specific test files using pytest:

```bash
hatch run test tests/test_pdf_extraction.py
hatch run test tests/test_psd_extraction.py
```

### All Tests

Run the complete test suite:

```bash
hatch run test
```

### Test Runner with Different Verbosity Levels

Use the convenience script for running tests with different verbosity levels:

```bash
# Default quiet mode
python scripts/run_tests.py

# Verbose mode (INFO level logging)
python scripts/run_tests.py --verbose

# Debug mode (DEBUG level logging)
python scripts/run_tests.py --debug

# Run with coverage reporting
python scripts/run_tests.py --coverage

# Run specific tests
python scripts/run_tests.py tests/test_specific.py
```

## Demonstrations

### Font Validation Demo

Run the font validation demonstration:

```bash
python tests/demos/demo_font_validation.py
```

This demo shows:

- Font availability checking
- Font substitution tracking
- Validation report generation
- Font coverage analysis

## Test Organization

- **Unit tests** (`unit/`): Individual component testing for modules, classes, and functions
- **Integration tests** (`integration/`): Cross-component testing and system integration
- **Performance tests** (`performance/`): Benchmarking, memory usage, and speed testing
- **End-to-end tests** (`e2e/`): Complete workflow testing from input to output
- **Security tests** (`security/`): Security validation, vulnerability checks, and hardening
- **Documentation tests** (`documentation/`): API documentation validation and coverage
- **Font tests** (`font/`): Font management, substitution, and rendering tests
- **Test utilities** (`utils/`): Test runners, validators, and helper scripts
- **Fixtures** (`fixtures/`): Test data, configuration files, and artifacts
- **Demos** (`demos/`): Interactive demonstrations of system features

## Adding New Tests

1. Create test files with the `test_*.py` naming convention
2. Place test data in the `fixtures/` directory
3. Save test outputs in the `output/` directory
4. Add demonstration scripts to the `demos/` directory
5. Update this README when adding new test categories
