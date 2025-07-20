# Testing with Optional Dependencies

This document explains how to handle tests that depend on optional system dependencies like Tesseract OCR and ImageMagick.

## Overview

PDFRebuilder includes optional functionality that depends on external system tools:

- **Tesseract OCR**: For text extraction from images and PSD files
- **ImageMagick**: For advanced image processing and PSD support

Tests are designed to handle these dependencies gracefully, either by mocking their behavior or by conditionally skipping when the actual tools are not available.

## Test Categories

### 1. Mocked Tests

These tests mock the behavior of optional dependencies and should always run:

```python
def test_check_tesseract_availability_not_installed(self):
    """Test Tesseract availability check when pytesseract is not installed."""
    # Mocks the import to simulate missing pytesseract
    # Always runs regardless of actual Tesseract installation
```

**Purpose**: Test error handling and fallback behavior when dependencies are missing.

### 2. Conditional Tests

These tests require actual system dependencies and are skipped when not available:

```python
@unittest.skipIf(not _tesseract_available(), "Tesseract not available")
def test_tesseract_actual_functionality(self):
    """Test actual Tesseract functionality."""
    # Only runs if Tesseract is actually installed
```

**Purpose**: Test integration with real system tools when available.

## Helper Functions

### `_tesseract_available()`

Checks if Tesseract OCR is actually available on the system:

```python
def _tesseract_available():
    """Helper function to check if Tesseract is actually available for testing."""
    try:
        is_available, _ = check_tesseract_availability()
        return is_available
    except Exception:
        return False
```

**Usage**: Use with `@unittest.skipIf` decorator for tests requiring actual Tesseract.

### `_wand_available()` (if needed)

Similar helper for ImageMagick/Wand availability (can be added as needed).

## Running Tests

### All Tests (Default)

```bash
# Run all tests - conditional tests are automatically skipped if dependencies missing
hatch run test
```

### OCR-Specific Tests

```bash
# Run all OCR-related tests (both mocked and conditional)
hatch run test tests/test_wand_engine.py -k tesseract -v

# Run only mocked OCR tests (always run)
hatch run test tests/test_wand_engine.py -k "tesseract and not actual" -v

# Run only conditional OCR tests (require actual Tesseract)
hatch run test tests/test_wand_engine.py -k "tesseract_actual" -v
```

### Testing Without Optional Dependencies

To test behavior when optional dependencies are not available:

```bash
# Create clean environment without optional dependencies
python -m venv test_env_minimal
source test_env_minimal/bin/activate
pip install -e .  # Install without [test] or [ocr] groups

# Run tests - conditional tests should be skipped
python -m pytest tests/test_wand_engine.py -k tesseract -v
```

## Test Output Examples

### When Tesseract is Available

```
tests/test_wand_engine.py::TestWandEngine::test_tesseract_actual_functionality PASSED
```

### When Tesseract is Not Available

```
tests/test_wand_engine.py::TestWandEngine::test_tesseract_actual_functionality SKIPPED (Tesseract not available)
```

## Adding New Optional Dependency Tests

When adding tests for new optional dependencies:

1. **Create a helper function** to check availability:

   ```python
   def _dependency_available():
       try:
           # Check if dependency is available
           return True
       except Exception:
           return False
   ```

2. **Add mocked tests** for error handling:

   ```python
   def test_dependency_not_available(self):
       # Mock the dependency as unavailable
       # Test error handling and fallback behavior
   ```

3. **Add conditional tests** for actual functionality:

   ```python
   @unittest.skipIf(not _dependency_available(), "Dependency not available")
   def test_dependency_actual_functionality(self):
       # Test with actual dependency
   ```

4. **Update documentation** to explain the new dependency and testing approach.

## Best Practices

### Do Mock When

- Testing error handling for missing dependencies
- Testing fallback behavior
- Ensuring tests run in all environments
- Testing specific error conditions

### Do Use Conditional Skipping When

- Testing actual integration with system tools
- Verifying real functionality works correctly
- Testing performance with actual tools
- End-to-end testing with real dependencies

### Don't

- Make tests fail when optional dependencies are missing
- Assume optional dependencies are always available
- Skip mocked tests (they should always run)
- Mix mocked and real dependency usage in the same test

## Environment Setup for Development

For full test coverage including conditional tests:

```bash
# Install all optional dependencies
hatch env create  # Includes OCR dependencies

# Or manually install system dependencies
sudo apt-get install tesseract-ocr libmagickwand-dev  # Linux
brew install tesseract imagemagick                    # macOS

# Verify dependencies are available
python -c "
from tests.test_wand_engine import _tesseract_available
print(f'Tesseract available: {_tesseract_available()}')
"
```

## Continuous Integration

CI environments should install optional dependencies to run all tests:

```yaml
# Example GitHub Actions step
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr libmagickwand-dev

- name: Install Python dependencies
  run: |
    pip install -e .[dev,test,all]
```

This ensures both mocked and conditional tests run in CI, providing comprehensive test coverage.
