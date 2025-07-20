# Test Fixtures and Utilities Guide

This document provides comprehensive guidance on using the standardized test fixtures and utilities available in the test suite.

## Overview

The test suite provides a standardized set of fixtures and utilities to ensure consistent testing practices across all test files. These fixtures handle common testing needs like temporary directories, font files, configuration files, and cleanup.

## Standardized Directory Fixtures

### `test_temp_dir`

Provides a temporary directory for test files that is automatically cleaned up after the test completes.

```python
def test_my_function(test_temp_dir):
    # Create a test file in the temporary directory
    test_file = os.path.join(test_temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    # Use the file in your test
    result = my_function(test_file)
    assert result is not None
    # Directory is automatically cleaned up after test
```

### `test_fonts_dir`

Provides a fonts directory for test font files with automatic cleanup.

```python
def test_font_processing(test_fonts_dir):
    # Create a test font file
    font_path = os.path.join(test_fonts_dir, "TestFont.ttf")
    with open(font_path, "wb") as f:
        f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)  # Minimal font header

    # Test font processing
    result = process_font(font_path)
    assert result.success
    # Fonts directory is automatically cleaned up
```

### `test_reports_dir`

Provides a reports directory for test output files, logs, and reports.

```python
def test_report_generation(test_reports_dir):
    # Generate a test report
    report_path = os.path.join(test_reports_dir, "test_report.json")
    generate_report(report_path, {"status": "success"})

    # Verify report was created
    assert os.path.exists(report_path)
    # Reports directory is automatically cleaned up
```

### `test_output_dir`

Provides a general output directory for any test files that don't fit specific categories.

```python
def test_file_generation(test_output_dir):
    output_file = os.path.join(test_output_dir, "output.pdf")
    generate_pdf(output_file)
    assert os.path.exists(output_file)
```

### `temp_font_dir` (Legacy)

Backward compatibility fixture that provides the same functionality as `test_fonts_dir`.

```python
def test_legacy_font_code(temp_font_dir):
    # This works for existing tests that use the old fixture name
    font_file = os.path.join(temp_font_dir, "font.ttf")
    # ... test code
```

## Utility Fixtures

### `sample_pdf_path`

Provides access to sample PDF files for testing.

```python
def test_pdf_processing(sample_pdf_path):
    # Get path to a sample PDF
    pdf_path = sample_pdf_path("sample.pdf")

    # Process the PDF
    result = process_pdf(pdf_path)
    assert result is not None
```

### `create_test_font`

Utility fixture for creating test font files with proper headers.

```python
def test_font_creation(test_fonts_dir, create_test_font):
    # Create a test font file
    font_path = os.path.join(test_fonts_dir, "TestFont.ttf")
    created_path = create_test_font(font_path, "TestFont")

    assert os.path.exists(created_path)
    assert created_path == font_path
```

### `create_test_config`

Utility fixture for creating test configuration files.

```python
def test_config_processing(test_temp_dir, create_test_config):
    config_data = {
        "version": "1.0",
        "settings": {"debug": True}
    }

    config_path = os.path.join(test_temp_dir, "config.json")
    created_path = create_test_config(config_path, config_data)

    # Process the configuration
    result = process_config(created_path)
    assert result.success
```

## Font Error Handling Fixtures

### `font_error_validation`

Provides utilities for validating font error handling in tests.

```python
def test_font_error_handling(font_error_validation):
    # Test code that might generate font errors
    process_fonts(["NonexistentFont"])

    # Validate error handling
    font_error_validation.assert_no_critical_errors()

    # Or check for expected errors
    errors = font_error_validation.get_font_errors()
    assert len(errors) > 0
```

### `mock_font_registration_failure`

Provides utilities for mocking font registration failures.

```python
def test_font_failure_handling(mock_font_registration_failure):
    # Mock a font registration failure
    with mock_font_registration_failure("need_font_file"):
        result = register_font("TestFont")
        assert not result.success
```

### `font_system_health_check`

Provides font system health checking capabilities.

```python
def test_font_system_health(font_system_health_check):
    health_report = font_system_health_check()
    assert health_report["system_status"] == "healthy"
```

## Test Utilities Module

The `tests/test_utils.py` module provides additional utility classes and functions:

### `TestFileManager`

Manages test files and directories with automatic cleanup.

```python
from tests.test_utils import TestFileManager

def test_with_file_manager():
    manager = TestFileManager("my_test")

    # Create temporary directory
    temp_dir = manager.create_temp_dir("fonts")

    # Create test files
    font_file = manager.create_font_file(os.path.join(temp_dir, "font.ttf"))
    config_file = manager.create_test_file(
        os.path.join(temp_dir, "config.json"),
        {"version": "1.0"}
    )

    # Use the files in your test
    process_files([font_file, config_file])

    # Cleanup is automatic, but can be called explicitly
    manager.cleanup()
```

### `TestDataGenerator`

Generates test data for various testing scenarios.

```python
from tests.test_utils import TestDataGenerator

def test_with_generated_data():
    # Generate font test data
    fonts = TestDataGenerator.create_font_test_data(num_fonts=5)

    # Generate document test data
    document = TestDataGenerator.create_document_test_data(pages=2, elements_per_page=3)

    # Generate drawing test data
    shapes = TestDataGenerator.create_drawing_test_data(num_shapes=4)

    # Use the generated data in tests
    process_document(document)
```

### `TestAssertions`

Custom assertions for testing.

```python
from tests.test_utils import TestAssertions

def test_with_custom_assertions(test_output_dir):
    output_file = os.path.join(test_output_dir, "output.json")
    generate_output(output_file)

    # Use custom assertions
    TestAssertions.assert_file_exists(output_file)
    TestAssertions.assert_file_not_empty(output_file)
    TestAssertions.assert_json_file_valid(output_file)
```

## Configuration

### Test Settings

Test-related settings are configured in `src/settings.py`:

```python
# Test framework configuration
"test_framework": {
    "cleanup_after_tests": True,
    "preserve_test_outputs": False,
    "generate_test_reports": True,
    "max_test_output_size_mb": 100,
    "test_timeout_seconds": 300,
    "font_test_timeout_seconds": 60,
    "enable_performance_tracking": True,
    "enable_memory_monitoring": True,
    "test_data_retention_days": 7,
},

# Test fixture configuration
"test_fixtures": {
    "auto_cleanup": True,
    "preserve_on_failure": True,
    "create_debug_outputs": True,
    "mock_external_dependencies": True,
    "use_temporary_directories": True,
    "font_fixture_timeout": 30,
},
```

### Directory Structure

The test fixtures create and manage the following directory structure:

```
output/
└── tests/
    ├── temp/           # Temporary files (test_temp_dir)
    ├── fonts/          # Test font files (test_fonts_dir)
    ├── reports/        # Test reports and logs (test_reports_dir)
    ├── sample/         # Sample test data (test_sample_dir)
    ├── fixtures/       # Test fixtures (test_fixtures_dir)
    └── debug/          # Debug outputs (test_debug_dir)
```

## Best Practices

### 1. Use Appropriate Fixtures

Choose the most specific fixture for your needs:

```python
# Good: Use specific fixture for fonts
def test_font_processing(test_fonts_dir):
    font_path = os.path.join(test_fonts_dir, "font.ttf")
    # ...

# Avoid: Using generic fixture for specific needs
def test_font_processing(test_temp_dir):  # Less clear intent
    font_path = os.path.join(test_temp_dir, "font.ttf")
    # ...
```

### 2. Leverage Utility Functions

Use the utility functions for common operations:

```python
from tests.test_utils import TestFileManager, TestDataGenerator

def test_complex_scenario():
    manager = TestFileManager("complex_test")

    # Generate test data
    document_data = TestDataGenerator.create_document_test_data()

    # Create test files
    config_file = manager.create_test_file("config.json", document_data)

    # Run test
    result = process_document(config_file)
    assert result.success

    # Cleanup is automatic
```

### 3. Handle Cleanup Properly

Most fixtures handle cleanup automatically, but you can control it:

```python
def test_with_manual_cleanup(test_temp_dir):
    # Create test files
    test_file = os.path.join(test_temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")

    # Test code here

    # Cleanup happens automatically after test
    # No manual cleanup needed unless you want to clean up early
```

### 4. Use Descriptive Test Names

The fixtures use test names for directory creation, so use descriptive names:

```python
# Good: Descriptive test name
def test_font_registration_with_missing_file(test_fonts_dir):
    # Creates directory: .../fonts/TestClass_test_font_registration_with_missing_file/
    pass

# Avoid: Generic test name
def test_1(test_fonts_dir):
    # Creates directory: .../fonts/TestClass_test_1/
    pass
```

### 5. Combine Fixtures Effectively

You can use multiple fixtures together:

```python
def test_complete_workflow(test_fonts_dir, test_temp_dir, test_reports_dir, create_test_font):
    # Create font file
    font_path = os.path.join(test_fonts_dir, "TestFont.ttf")
    create_test_font(font_path)

    # Create config file
    config_path = os.path.join(test_temp_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump({"font": "TestFont"}, f)

    # Process and generate report
    result = process_config(config_path)
    report_path = os.path.join(test_reports_dir, "result.json")
    generate_report(report_path, result)

    # All directories are cleaned up automatically
```

## Migration from Old Patterns

If you have existing tests using old patterns, here's how to migrate:

### Old Pattern (Manual Directory Management)

```python
def test_old_pattern():
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    try:
        font_file = os.path.join(temp_dir, "font.ttf")
        with open(font_file, "wb") as f:
            f.write(b"font data")

        # Test code
        result = process_font(font_file)
        assert result.success
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
```

### New Pattern (Using Fixtures)

```python
def test_new_pattern(test_fonts_dir, create_test_font):
    font_file = os.path.join(test_fonts_dir, "font.ttf")
    create_test_font(font_file)

    # Test code
    result = process_font(font_file)
    assert result.success
    # Cleanup is automatic
```

## Troubleshooting

### Common Issues

1. **Fixture not found**: Make sure you're importing from the correct module and that the fixture is defined in `conftest.py`.

2. **Directory not cleaned up**: Check if the test is failing before cleanup. Fixtures preserve directories on test failure by default.

3. **Permission errors**: On some systems, you might need to handle file permissions explicitly.

4. **Path separator issues**: Use `os.path.join()` or `pathlib.Path` for cross-platform compatibility.

### Debugging

Enable debug output to see fixture behavior:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_debug(test_temp_dir):
    print(f"Using temp directory: {test_temp_dir}")
    # Test code
```

### Performance

For tests that create many files, consider using `TestFileManager` for better performance:

```python
def test_many_files():
    manager = TestFileManager("performance_test")

    # Create many files efficiently
    for i in range(100):
        manager.create_test_file(f"file_{i}.txt", f"content {i}")

    # Test code

    # Single cleanup call for all files
    manager.cleanup()
```

This standardized approach ensures consistent, reliable, and maintainable tests across the entire test suite.
