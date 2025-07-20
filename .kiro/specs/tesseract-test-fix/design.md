# Design Document

## Overview

This design addresses the failing Tesseract OCR availability test by fixing the test expectations, adding proper optional dependency management, and improving documentation. The solution involves updating the test to match the actual function behavior, configuring pytesseract as an optional dependency, and documenting the installation requirements.

## Architecture

The fix involves three main components:

1. **Test Fix**: Update the failing test to properly mock and expect the correct error messages
2. **Dependency Management**: Add pytesseract as an optional dependency in the appropriate groups
3. **Documentation Update**: Add clear installation instructions for Tesseract OCR

## Components and Interfaces

### Test Component

**File**: `tests/test_wand_engine.py`

The test `test_check_tesseract_availability_not_installed` needs to be updated to:
- Mock `pytesseract.get_tesseract_version()` instead of `subprocess.run`
- Expect the correct error message: "pytesseract is not installed" for ImportError
- Add additional test cases for different failure scenarios

**Current Implementation Issue**:
```python
# Current test mocks subprocess.run but function uses pytesseract
with patch("subprocess.run", side_effect=FileNotFoundError("tesseract not found")):
    is_available, info = check_tesseract_availability()
    self.assertIn("Tesseract OCR is not installed", info["error"])  # Wrong expectation
```

**Fixed Implementation**:
```python
# Mock the actual function call and expect correct message
with patch("src.engine.extract_wand_content.pytesseract", side_effect=ImportError("No module named 'pytesseract'")):
    is_available, info = check_tesseract_availability()
    self.assertIn("pytesseract is not installed", info["error"])  # Correct expectation
```

### Dependency Management Component

**File**: `pyproject.toml`

Add pytesseract to optional dependency groups:

```toml
[project.optional-dependencies]
# Existing groups...
ocr = [
    "pytesseract>=0.3.10",
]
test = [
    # existing test dependencies...
    "pytesseract>=0.3.10",  # Add to test group
]
dev = [
    # existing dev dependencies...
    "pytesseract>=0.3.10",  # Add to dev group
]
all = [
    # existing all dependencies...
    "pytesseract>=0.3.10",  # Add to all group
]
```

### Documentation Component

**Files**: 
- `docs/INSTALLATION.md`
- `docs/INSTALL-dev.md` (new file)

Add Tesseract installation instructions and optional dependency information.

## Data Models

### Test Data Structure

The test should validate the correct return structure from `check_tesseract_availability()`:

```python
# Success case
(True, {
    "tesseract_version": "tesseract 5.x.x",
    "status": "available"
})

# ImportError case  
(False, {
    "error": "pytesseract is not installed",
    "install_command": "pip install pytesseract",
    "additional_info": "You also need to install Tesseract OCR on your system."
})

# Other exception case
(False, {
    "error": "Tesseract OCR is not available: {specific_error}",
    "install_command": {
        "windows": "Download from https://github.com/UB-Mannheim/tesseract/wiki",
        "macos": "brew install tesseract",
        "ubuntu": "apt-get install tesseract-ocr",
        "centos": "yum install tesseract"
    }
})
```

## Error Handling

### Test Error Scenarios

1. **ImportError**: When pytesseract module is not installed
   - Mock: `ImportError("No module named 'pytesseract'")`
   - Expected: `"pytesseract is not installed"`

2. **TesseractNotFoundError**: When tesseract binary is not available
   - Mock: `pytesseract.TesseractNotFoundError("tesseract is not installed")`
   - Expected: `"Tesseract OCR is not available: tesseract is not installed"`

3. **General Exception**: Other tesseract-related errors
   - Mock: `Exception("Some other error")`
   - Expected: `"Tesseract OCR is not available: Some other error"`

### Graceful Degradation

The system should handle missing Tesseract gracefully:
- Tests should be skippable when Tesseract is not available
- OCR functionality should be optional
- Clear error messages should guide users to installation

## Testing Strategy

### Test Cases to Update

1. **Fix existing test**: `test_check_tesseract_availability_not_installed`
   - Update mocking to use correct import path
   - Update expected error message

2. **Add new test cases**:
   - `test_check_tesseract_availability_binary_not_found`: Test when pytesseract is installed but tesseract binary is missing
   - `test_check_tesseract_availability_other_error`: Test other exception scenarios
   - `test_check_tesseract_availability_success`: Test successful detection

3. **Add conditional test skipping**:
   ```python
   @unittest.skipIf(not _tesseract_available(), "Tesseract not available")
   def test_tesseract_functionality(self):
       # Tests that require actual Tesseract
   ```

### Mock Strategy

Use proper mocking hierarchy:
```python
# Mock at the module level where it's imported
@patch('src.engine.extract_wand_content.pytesseract')
def test_check_tesseract_availability_not_installed(self, mock_pytesseract):
    mock_pytesseract.get_tesseract_version.side_effect = ImportError("No module named 'pytesseract'")
    # Test implementation
```

## Implementation Plan

### Phase 1: Fix the Failing Test

1. Update the test to mock the correct function call
2. Update the expected error message
3. Ensure the test passes with the current implementation

### Phase 2: Add Optional Dependencies

1. Update `pyproject.toml` to include pytesseract in appropriate groups
2. Verify that `hatch env create` installs pytesseract for development
3. Test that the optional dependency works correctly

### Phase 3: Enhance Test Coverage

1. Add additional test cases for different error scenarios
2. Add conditional test skipping for tests that require Tesseract
3. Ensure all test scenarios are properly covered

### Phase 4: Update Documentation

1. Create `docs/INSTALL-dev.md` with development-specific installation instructions
2. Update `docs/INSTALLATION.md` to mention Tesseract requirements
3. Document the optional dependency groups and how to use them

## Configuration Changes

### pyproject.toml Updates

```toml
[project.optional-dependencies]
# Add new OCR group
ocr = [
    "pytesseract>=0.3.10",
]

# Update existing groups
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "pytesseract>=0.3.10",  # Add this
]

dev = [
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pytesseract>=0.3.10",  # Add this
]

all = [
    "pytesseract>=0.3.10",  # Add this
    # ... other dependencies
]
```

### Environment Variables

Consider adding environment variable support for Tesseract path:
```python
# In check_tesseract_availability function
tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')
```

## Validation

### Success Criteria

1. **Test Passes**: The failing test `test_check_tesseract_availability_not_installed` passes
2. **Optional Dependencies Work**: Installing with `pip install -e .[test]` includes pytesseract
3. **Documentation Complete**: Clear installation instructions are available
4. **Graceful Degradation**: System works without Tesseract when OCR is not needed

### Testing Validation

```bash
# Test with pytesseract installed
hatch run test tests/test_wand_engine.py::TestWandEngine::test_check_tesseract_availability_not_installed

# Test without pytesseract (in clean environment)
python -m venv clean_env
source clean_env/bin/activate
pip install -e .  # Without [test] group
python -m pytest tests/test_wand_engine.py::TestWandEngine::test_check_tesseract_availability_not_installed
```

## Migration Strategy

### Backward Compatibility

- Existing functionality remains unchanged
- Tests that don't require Tesseract continue to work
- Optional dependency approach ensures no breaking changes

### Rollout Plan

1. **Development Environment**: Update development dependencies first
2. **CI/CD**: Ensure CI systems install the test dependencies
3. **Documentation**: Update all relevant documentation
4. **User Communication**: Inform users about the optional OCR functionality

## Dependencies

### System Dependencies

- **Tesseract OCR**: System-level installation required for actual OCR functionality
- **pytesseract**: Python wrapper for Tesseract (added as optional dependency)

### Installation Commands by OS

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki

# Python package (optional)
pip install pytesseract
# or
pip install -e .[ocr]
```