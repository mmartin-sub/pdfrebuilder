# Tests Directory

This directory contains all test files, utilities, and related artifacts for the `pdfrebuilder` project.

## Test Organization and Directory Structure

The `tests/` directory is organized into several categories to ensure a clean and maintainable test suite.

```
tests/
├── README.md                       # This file
├── conftest.py                     # Pytest configuration and global fixtures
├── font/                           # Tests for font management, substitution, and rendering
├── performance/                    # Performance and benchmarking tests
├── wip/                            # Work-in-progress tests (not run by default)
│   ├── unit/                       # Unit tests for individual components
│   ├── integration/                # Integration tests between components
│   ├── e2e/                        # End-to-end workflow tests
│   ├── security/                   # Security-focused tests
│   └── documentation/              # Documentation validation tests
├── demos/                          # Demonstration scripts for various features
├── fixtures/                       # Test data, configurations, and sample files
├── sample/                         # Sample input documents for testing
├── human_review_outputs/           # Outputs for manual human review
├── backward_compatibility_reports/ # Reports from backward compatibility tests
└── config.py                       # Test-specific configurations
```

- **`font/`**: Contains all tests related to font processing, including validation, substitution, and Google Fonts integration.
- **`performance/`**: Houses tests for benchmarking, memory usage, and processing speed.
- **`wip/`**: A directory for work-in-progress tests that are not yet ready to be included in the main test suite. These tests are excluded from the default `pytest` run.
  - **`unit/`**: Unit tests for individual modules, classes, and functions.
  - **`integration/`**: Tests that verify the interaction between different components of the application.
  - **`e2e/`**: End-to-end tests that simulate real-world usage scenarios.
  - **`security/`**: Tests focused on security aspects, such as input sanitization and vulnerability checks.
  - **`documentation/`**: Tests for validating the accuracy and completeness of the documentation.
- **`demos/`**: Contains scripts that demonstrate specific features of the `pdfrebuilder` tool.
- **`fixtures/`**: Stores test data, configuration files, and other artifacts needed for the tests.
- **`sample/`**: Contains sample PDF and other documents used as input for tests.

### Naming Conventions

- **Test files**: `test_*.py`
- **Demo scripts**: `demo_*.py` (located in `tests/demos/`)
- **Configuration files**: `*.json`, `*.py` (located in `tests/fixtures/`)

### Pre-commit Hooks

This project uses pre-commit hooks to enforce code quality and consistency. The configuration can be found in `.pre-commit-config.yaml`. These hooks help ensure that all committed code adheres to the project's standards.

## Running Tests

All tests are run using the `hatch` command-line tool, which is configured in the `pyproject.toml` file.

### Running All Tests

To run the complete test suite, use the following command:

```bash
hatch run test
```

This command will execute all tests that are not in the `tests/wip` directory.

### Running Specific Tests

You can run specific test files or directories by passing them as arguments to the `pytest` command within the `hatch` environment.

**Run a specific test file:**

```bash
hatch run test tests/font/test_font_substitution.py
```

**Run all tests in a directory:**

```bash
hatch run test tests/font/
```

**Run a specific test function:**

```bash
hatch run test tests/font/test_font_substitution.py::TestFontSubstitutionEngine::test_glyph_coverage_basic_latin
```

### Running Tests with Coverage

To run the tests and generate a coverage report, use the `cov` environment in `hatch`:

```bash
hatch run cov
```

This will run the tests and print a coverage report to the console.

## Adding New Tests

When adding new tests, please adhere to the following guidelines:

1. **File Naming**: Name your test file starting with `test_`.
2. **Location**: Place the test file in the appropriate directory based on its category (e.g., `font`, `performance`, `wip/unit`).
3. **Fixtures**: If you need to add new test data or configuration, place it in the `tests/fixtures/` directory.
4. **Demos**: If you are adding a demonstration for a new feature, place it in the `tests/demos/` directory.
5. **README**: If you add a new top-level test directory, please update this `README.md` file to include it in the directory structure.
