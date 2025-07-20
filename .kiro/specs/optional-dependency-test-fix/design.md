# Design Document

## Overview

This design addresses the failing test imports by implementing conditional imports, proper optional depditional imports, updating test environment configuration, and adding proper dependency management. The solution ensures that test discovery and execution work correctly regardless of which optional dependencies are installed, while providing clear guidance when specific features require additional dependencies.

## Architecture

The fix involves four main components:

1. **Conditional Import System**: Implement try/except import patterns in source modules
2. **Test Environment Enhancement**: Update pyproject.toml to include necessary optional dependencies in test environments
3. **Test Skip Decorators**: Add conditional test skipping based on dependency availability
4. **Dependency Detection Utilities**: Create helper functions to check for optional dependency availability

## Components and Interfaces

### Conditional Import System

**Affected Files**: 
- `src/engine/document_renderer.py`
- `src/engine/validation_manager.py` 
- `src/engine/legacy_validator.py`
- Other modules importing optional dependencies

**Pattern Implementation**:
```python
# Before (causes ImportError)
from psd_tools import PSDImage
from skimage.metrics import structural_similarity as compare_ssim

# After (conditional imports)
try:
    from psd_tools import PSDImage
    HAS_PSD_TOOLS = True
except ImportError:
    PSDImage = None
    HAS_PSD_TOOLS = False

try:
    from skimage.metrics import structural_similarity as compare_ssim
    HAS_SKIMAGE = True
except ImportError:
    compare_ssim = None
    HAS_SKIMAGE = False
```

**Function Guards**:
```python
def render_psd_document(psd_path):
    if not HAS_PSD_TOOLS:
        raise ImportError(
            "PSD support requires psd-tools. Install with: pip install 'pdfrebuilder[psd]'"
        )
    # Implementation using PSDImage
```

### Test Environment Configuration

**File**: `pyproject.toml`

**Current Issue**: The default test environment doesn't include `psd_tools` and `scikit-image`, causing import failures.

**Solution**: Update the test environment dependencies:

```toml
[tool.hatch.envs.default]
python = "3.12"
dependencies = [
  "pytest",
  "pytest-cov",
  "psutil>=7.0.0",
  "opencv-python>=4.12.0",
  "pytesseract>=0.3.13",
  "psd-tools>=1.10.9",      # Add for PSD support
  "scikit-image>=0.25.2",   # Add for image validation
  "numpy>=1.24.0",          # Required by scikit-image
]
```

**Alternative Approach**: Create separate test environments:

```toml
[tool.hatch.envs.test-core]
# Core tests without optional dependencies
dependencies = [
  "pytest",
  "pytest-cov",
]

[tool.hatch.envs.test-full]
# Full tests with all optional dependencies
dependencies = [
  "pytest",
  "pytest-cov",
  "psd-tools>=1.10.9",
  "scikit-image>=0.25.2",
  "numpy>=1.24.0",
  "pytesseract>=0.3.13",
]
```

### Test Skip Decorators

**File**: `tests/conftest.py` (create utility functions)

**Dependency Detection Functions**:
```python
import pytest

def has_psd_tools():
    """Check if psd-tools is available."""
    try:
        import psd_tools
        return True
    except ImportError:
        return False

def has_skimage():
    """Check if scikit-image is available."""
    try:
        import skimage
        return True
    except ImportError:
        return False

def has_tesseract():
    """Check if pytesseract and tesseract are available."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except (ImportError, Exception):
        return False

# Pytest skip decorators
skip_if_no_psd = pytest.mark.skipif(
    not has_psd_tools(),
    reason="psd-tools not available. Install with: pip install 'pdfrebuilder[psd]'"
)

skip_if_no_skimage = pytest.mark.skipif(
    not has_skimage(),
    reason="scikit-image not available. Install with: pip install 'pdfrebuilder[validation]'"
)

skip_if_no_tesseract = pytest.mark.skipif(
    not has_tesseract(),
    reason="tesseract not available. Install with: pip install 'pdfrebuilder[ocr]'"
)
```

**Test Module Updates**:
```python
# tests/test_engine_modules.py
import pytest
from tests.conftest import skip_if_no_psd, skip_if_no_skimage

@skip_if_no_psd
@skip_if_no_skimage
class TestEngineModules:
    def test_document_renderer_import(self):
        from src.engine.document_renderer import RenderingError
        # Test implementation
```

### Conditional Import in Test Modules

**Pattern for Test Files**:
```python
# tests/test_psd_extraction.py
import pytest

try:
    from src.engine.extract_psd_content import extract_psd_content
    HAS_PSD_SUPPORT = True
except ImportError:
    HAS_PSD_SUPPORT = False

@pytest.mark.skipif(not HAS_PSD_SUPPORT, reason="PSD support not available")
class TestPSDExtraction:
    def test_psd_extraction(self):
        # Test implementation
```

## Data Models

### Dependency Status Structure

```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class DependencyStatus:
    """Track status of optional dependencies."""
    name: str
    available: bool
    version: Optional[str] = None
    install_command: Optional[str] = None
    error_message: Optional[str] = None

def get_dependency_status() -> Dict[str, DependencyStatus]:
    """Get status of all optional dependencies."""
    dependencies = {}
    
    # Check psd-tools
    try:
        import psd_tools
        dependencies['psd_tools'] = DependencyStatus(
            name='psd-tools',
            available=True,
            version=psd_tools.__version__,
            install_command="pip install 'pdfrebuilder[psd]'"
        )
    except ImportError as e:
        dependencies['psd_tools'] = DependencyStatus(
            name='psd-tools',
            available=False,
            install_command="pip install 'pdfrebuilder[psd]'",
            error_message=str(e)
        )
    
    # Similar for other dependencies...
    return dependencies
```

## Error Handling

### Import Error Handling Strategy

1. **Module Level**: Use conditional imports with feature flags
2. **Function Level**: Check feature flags before using optional functionality
3. **Test Level**: Skip tests when dependencies are unavailable
4. **User Level**: Provide clear error messages with installation instructions

### Error Message Templates

```python
ERROR_MESSAGES = {
    'psd_tools': (
        "PSD support requires psd-tools. "
        "Install with: pip install 'pdfrebuilder[psd]'"
    ),
    'skimage': (
        "Image validation requires scikit-image. "
        "Install with: pip install 'pdfrebuilder[validation]'"
    ),
    'tesseract': (
        "OCR support requires pytesseract and Tesseract OCR. "
        "Install with: pip install 'pdfrebuilder[ocr]' and install Tesseract OCR system package"
    )
}
```

## Testing Strategy

### Test Categories

1. **Core Tests**: Run without any optional dependencies
2. **Feature Tests**: Run only when specific dependencies are available
3. **Integration Tests**: Test interaction between core and optional features
4. **Dependency Tests**: Test conditional import behavior

### Test Environment Matrix

```bash
# Core functionality only
hatch run test-core:test

# Full functionality with all dependencies
hatch run test-full:test

# Specific feature sets
hatch run test tests/test_pdf_*.py  # PDF-only tests
hatch run test -m "not psd" tests/  # Skip PSD tests
```

### Mock Strategy for Missing Dependencies

```python
# For testing error handling when dependencies are missing
@patch('src.engine.document_renderer.HAS_PSD_TOOLS', False)
def test_psd_functionality_without_dependency(self):
    with pytest.raises(ImportError, match="PSD support requires psd-tools"):
        render_psd_document("test.psd")
```

## Implementation Plan

### Phase 1: Fix Immediate Import Errors

1. **Update source modules** to use conditional imports
2. **Add feature flags** for optional dependencies
3. **Update test environment** to include necessary dependencies

### Phase 2: Enhance Test Infrastructure

1. **Create dependency detection utilities** in conftest.py
2. **Add skip decorators** for optional functionality
3. **Update test modules** to use conditional imports

### Phase 3: Improve User Experience

1. **Add dependency status reporting** functionality
2. **Improve error messages** with installation guidance
3. **Update documentation** about optional dependencies

### Phase 4: Test Environment Optimization

1. **Create multiple test environments** for different dependency sets
2. **Add CI/CD configurations** for testing different combinations
3. **Document testing strategies** for developers

## Configuration Changes

### pyproject.toml Updates

**Immediate Fix** (add to default test environment):
```toml
[tool.hatch.envs.default]
dependencies = [
  "pytest",
  "pytest-cov",
  "psutil>=7.0.0",
  "opencv-python>=4.12.0",
  "pytesseract>=0.3.13",
  "psd-tools>=1.10.9",      # Add this
  "scikit-image>=0.25.2",   # Add this
  "numpy>=1.24.0",          # Add this
]
```

**Long-term Solution** (separate environments):
```toml
[tool.hatch.envs.test-minimal]
dependencies = [
  "pytest",
  "pytest-cov",
]

[tool.hatch.envs.test-pdf]
dependencies = [
  "pytest",
  "pytest-cov",
  "opencv-python>=4.12.0",
]

[tool.hatch.envs.test-psd]
dependencies = [
  "pytest",
  "pytest-cov",
  "psd-tools>=1.10.9",
  "numpy>=1.24.0",
]

[tool.hatch.envs.test-validation]
dependencies = [
  "pytest",
  "pytest-cov",
  "scikit-image>=0.25.2",
  "opencv-python>=4.12.0",
  "numpy>=1.24.0",
]
```

### Test Scripts Updates

```toml
[tool.hatch.envs.default.scripts]
test = "PYTHONPATH=. FONTTOOLS_LOG_LEVEL=WARNING pytest {args:tests/}"
test-core = "PYTHONPATH=. FONTTOOLS_LOG_LEVEL=WARNING pytest -m 'not psd and not validation' {args:tests/}"
test-psd = "PYTHONPATH=. FONTTOOLS_LOG_LEVEL=WARNING pytest -m psd {args:tests/}"
test-validation = "PYTHONPATH=. FONTTOOLS_LOG_LEVEL=WARNING pytest -m validation {args:tests/}"
```

## Validation

### Success Criteria

1. **Test Discovery**: `hatch run pytest --collect-only` completes without ImportError
2. **Core Tests**: Tests run successfully without optional dependencies
3. **Feature Tests**: Tests are properly skipped when dependencies are missing
4. **Full Tests**: All tests pass when all dependencies are installed

### Testing Commands

```bash
# Test current fix
hatch run pytest --collect-only  # Should not fail

# Test with minimal dependencies
pip install -e .
python -m pytest --collect-only  # Should work with skips

# Test with full dependencies
pip install -e .[all]
python -m pytest  # Should run all tests
```

## Migration Strategy

### Immediate Actions (Fix Blocking Issues)

1. Add missing dependencies to default test environment
2. Update modules with conditional imports
3. Verify test discovery works

### Medium-term Improvements

1. Add proper skip decorators
2. Create dependency detection utilities
3. Improve error messages

### Long-term Enhancements

1. Create multiple test environments
2. Add dependency status reporting
3. Optimize CI/CD for different dependency combinations

## Dependencies

### Required Changes

- **pyproject.toml**: Add optional dependencies to test environment
- **Source modules**: Implement conditional imports
- **Test modules**: Add skip decorators and conditional imports
- **conftest.py**: Create dependency detection utilities

### System Requirements

No additional system requirements, but clearer documentation about optional system dependencies (Tesseract OCR) will be provided. Add this
  "numpy>=1.24.0",          # Add this (required by scikit-image)
]

# Alternative: Create separate test environments
[tool.hatch.envs.test-minimal]
dependencies = [
  "pytest",
  "pytest-cov",
]

[tool.hatch.envs.test-full]
dependencies = [
  "pytest",
  "pytest-cov",
  "psd-tools>=1.10.9",
  "scikit-image>=0.25.2",
  "numpy>=1.24.0",
  "pytesseract>=0.3.13",
  "opencv-python>=4.12.0",
  "psutil>=7.0.0",
]

[tool.hatch.envs.test-minimal.scripts]
test = "PYTHONPATH=. pytest {args:tests/unit/core/}"

[tool.hatch.envs.test-full.scripts]
test = "PYTHONPATH=. pytest {args:tests/}"
test-psd = "PYTHONPATH=. pytest {args:tests/unit/psd/ tests/integration/psd/}"
test-validation = "PYTHONPATH=. pytest {args:tests/unit/validation/ tests/integration/validation/}"
```

### pytest Configuration Updates

```toml
[tool.pytest.ini_options]
# Add custom markers for optional dependency tests
markers = [
    "human_review: marks tests requiring human visual review",
    "e2e: marks end-to-end integration tests", 
    "unit: marks unit tests",
    "integration: marks integration tests",
    "performance: marks performance tests",
    "psd: marks tests requiring psd-tools",
    "validation: marks tests requiring scikit-image",
    "ocr: marks tests requiring pytesseract",
    "full_deps: marks tests requiring all optional dependencies",
]
```

## Validation

### Success Criteria

1. **Test Discovery**: `hatch run pytest --collect-only` completes without ImportError
2. **Core Tests Pass**: Tests run successfully without optional dependencies
3. **Feature Tests Skip**: Tests are properly skipped when dependencies are missing
4. **Clear Messages**: Skip messages provide clear installation instructions
5. **Full Tests Pass**: All tests pass when optional dependencies are installed

### Testing Validation Commands

```bash
# Test discovery without optional dependencies
pip uninstall psd-tools scikit-image -y
hatch run pytest --collect-only

# Test core functionality
hatch run test-minimal

# Test with full dependencies
pip install psd-tools scikit-image
hatch run test-full

# Test specific features
hatch run test-psd
hatch run test-validation
```

## Migration Strategy

### Backward Compatibility

- Existing functionality remains unchanged when dependencies are available
- New conditional import system is transparent to users with full installations
- Optional dependency groups maintain existing behavior

### Rollout Plan

1. **Fix Import Errors**: Immediate fix for test discovery issues
2. **Update Test Environment**: Ensure CI/CD systems work correctly
3. **Add Skip Decorators**: Gradual addition of conditional test skipping
4. **Documentation**: Update installation and development guides

## Dependencies

### Required Changes

- **Source Modules**: Add conditional imports and availability flags
- **Test Modules**: Add skip decorators and conditional imports
- **Configuration**: Update pyproject.toml test environment
- **Utilities**: Create dependency checking utilities

### New Dependencies

- No new required dependenci