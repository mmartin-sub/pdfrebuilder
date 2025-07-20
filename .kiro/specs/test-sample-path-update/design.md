# Design Document

## Overview

This design updates the test suite's sample file path resolution to use `tests/sample/` instead of `input/` directory. The solution centralizes path logic in the test configuration module and updates all references throughout the test suite.

## Architecture

### Current State
- Sample files located in `tests/sample/`
- `get_sample_input_path()` function looks in `input/` directory
- Some tests have hardcoded paths to `input/sample/`
- Tests fail when sample files aren't found in expected location

### Target State
- All sample file references use `tests/sample/` directory
- Centralized path resolution in `tests/config.py`
- Consistent sample file access across all tests
- No dependency on `input/` directory for test execution

## Components and Interfaces

### New Test Configuration Module (`tests/test_config.py`)

**Centralized Test Configuration:**
```python
"""
Test-specific configuration module for managing test paths and settings.
Separates test configuration from main application settings.
"""

import os
from pathlib import Path

class TestPaths:
    """Centralized configuration for all test-related paths"""

    # Base test directory (where this config file is located)
    TEST_BASE_DIR = Path(__file__).parent

    # Sample files directory
    SAMPLE_DIR = TEST_BASE_DIR / "sample"

    # Test output directories
    OUTPUT_DIR = TEST_BASE_DIR / "output"
    TEMP_DIR = TEST_BASE_DIR / "temp"
    REPORTS_DIR = TEST_BASE_DIR / "reports"

    # Specific sample files (can be extended as needed)
    SAMPLE_PDF = SAMPLE_DIR / "sample.pdf"
    DEMO1_PDF = SAMPLE_DIR / "demo1.pdf"
    DEMO2_PDF = SAMPLE_DIR / "demo2.pdf"
    DEMO3_PDF = SAMPLE_DIR / "demo3.pdf"

def get_sample_path(filename: str) -> str:
    """
    Get path to a sample file.

    Args:
        filename: Name of the sample file

    Returns:
        Full path to the sample file
    """
    return str(TestPaths.SAMPLE_DIR / filename)

def get_sample_dir() -> str:
    """
    Get the path to the sample directory.

    Returns:
        Full path to the sample directory
    """
    return str(TestPaths.SAMPLE_DIR)
```

**Updated Main Test Config (`tests/config.py`):**
```python
# Import test-specific paths
from tests.test_config import get_sample_path, get_sample_dir, TestPaths

def get_sample_input_path(filename: str) -> str:
    """
    Get path to a sample input file (delegates to test_config).

    Args:
        filename: Name of the sample file

    Returns:
        Full path to the sample input file
    """
    return get_sample_path(filename)
```

### Test File Updates

**Files to Update:**
1. `tests/test_pdf_extraction.py` - Update hardcoded path in main section
2. `tests/test_psd_extraction.py` - Update hardcoded path in main section
3. Any other test files with hardcoded `input/` references

**Pattern to Replace:**
```python
# OLD
test_input_file = "input/sample/sample.pdf"

# NEW
from tests.test_config import get_sample_path
test_input_file = get_sample_path("sample.pdf")

# OR using predefined constants
from tests.test_config import TestPaths
test_input_file = str(TestPaths.SAMPLE_PDF)
```

## Data Models

### Path Resolution Logic

```
tests/
├── sample/           # Sample files directory
│   ├── sample.pdf
│   ├── demo1.pdf
│   ├── demo2.pdf
│   └── ...
├── config.py         # Updated path resolution
└── test_*.py         # Updated test files
```

### Configuration Architecture Changes

```python
# Before - Hardcoded paths scattered throughout tests
test_input_file = "input/sample/sample.pdf"

# After - Centralized configuration
# tests/test_config.py
class TestPaths:
    SAMPLE_DIR = Path(__file__).parent / "sample"
    SAMPLE_PDF = SAMPLE_DIR / "sample.pdf"

# Usage in tests
from tests.test_config import TestPaths
test_input_file = str(TestPaths.SAMPLE_PDF)
```

## Error Handling

### File Not Found Scenarios
- If sample file doesn't exist in `tests/sample/`, provide clear error message
- Include available sample files in error message for debugging
- Maintain consistent error handling across all test files

### Backward Compatibility
- Log warning if old `input/` paths are detected
- Provide migration guidance in error messages
- Ensure graceful degradation if sample files are missing

## Testing Strategy

### Validation Steps
1. **Path Resolution Test**: Verify `get_sample_input_path()` returns correct paths
2. **File Existence Test**: Confirm all referenced sample files exist
3. **Test Suite Execution**: Run full test suite to ensure no broken references
4. **Integration Test**: Verify tests work with new sample file locations

### Test Cases
```python
def test_sample_path_resolution():
    """Test that sample paths resolve correctly"""
    path = get_sample_input_path("sample.pdf")
    assert path.endswith("tests/sample/sample.pdf")
    assert os.path.exists(path)

def test_sample_directory_exists():
    """Test that sample directory exists and contains files"""
    sample_dir = get_sample_dir()
    assert os.path.exists(sample_dir)
    assert os.path.isdir(sample_dir)

    # Check for expected sample files
    expected_files = ["sample.pdf", "demo1.pdf", "demo2.pdf"]
    for filename in expected_files:
        file_path = os.path.join(sample_dir, filename)
        assert os.path.exists(file_path), f"Missing sample file: {filename}"
```

## Implementation Plan

### Phase 1: Create Test Configuration Module
1. Create new `tests/test_config.py` with centralized path configuration
2. Define `TestPaths` class with all test-related path constants
3. Add helper functions for path resolution
4. Add validation for sample directory existence

### Phase 2: Update Main Test Config
1. Update `tests/config.py` to import from `test_config.py`
2. Maintain backward compatibility for existing `get_sample_input_path()` calls
3. Ensure integration with existing test infrastructure

### Phase 3: Update Test Files
1. Find all hardcoded path references in test files
2. Replace with imports from `tests.test_config`
3. Use either helper functions or direct path constants as appropriate

### Phase 3: Validation and Testing
1. Run test suite to identify any remaining issues
2. Add tests for path resolution functionality
3. Verify all sample files are accessible

### Phase 4: Documentation
1. Update test documentation to reflect new sample file location
2. Add comments explaining the path resolution logic
3. Update any README files that reference sample file locations
