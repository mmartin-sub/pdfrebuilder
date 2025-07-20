# Optional Dependencies Guide

This document explains how to install and use optional dependencies in PDFRebuilder. Optional dependencies provide additional functionality for specific use cases while keeping the core installation lightweight.

## Available Optional Dependency Groups

### Core Groups

- **`psd`**: PSD file processing support
- **`validation`**: Image validation and comparison tools
- **`ocr`**: Optical Character Recognition support
- **`wand`**: ImageMagick-based image processing
- **`cli`**: Enhanced command-line interface tools

### Development Groups

- **`test`**: Testing framework and utilities
- **`dev`**: Development tools (linting, formatting, type checking)
- **`performance`**: Performance testing and benchmarking tools
- **`all`**: All optional dependencies combined

## Installation Examples

### Using pip

```bash
# Install core package only
pip install -e .

# Install with PSD support
pip install -e .[psd]

# Install with image validation support
pip install -e .[validation]

# Install with OCR support
pip install -e .[ocr]

# Install with multiple optional groups
pip install -e .[psd,validation,ocr]

# Install with all optional dependencies
pip install -e .[all]

# Install for development (includes dev tools and test dependencies)
pip install -e .[dev,test]
```

### Using uv

```bash
# Install core package only
uv pip install -e .

# Install with PSD support
uv pip install -e .[psd]

# Install with image validation support
uv pip install -e .[validation]

# Install with OCR support
uv pip install -e .[ocr]

# Install with multiple optional groups
uv pip install -e .[psd,validation,ocr]

# Install with all optional dependencies
uv pip install -e .[all]

# Install for development
uv pip install -e .[dev,test]
```

### Using Hatch (Recommended for Development)

```bash
# Create and activate development environment (includes all dependencies)
hatch env create
hatch shell

# Run tests in the development environment
hatch run test

# Run specific test categories
hatch run test-psd
hatch run test-validation
hatch run test-core
```

## Dependency Details

### PSD Support (`psd`)

- **Dependencies**: `psd-tools>=1.10.9`, `numpy>=1.24.0`
- **Purpose**: Process Adobe Photoshop PSD files
- **Use case**: Extract layers, text, and images from PSD files

### Image Validation (`validation`)

- **Dependencies**: `scikit-image>=0.25.2`, `opencv-python>=4.12.0`, `numpy>=1.24.0`
- **Purpose**: Advanced image comparison and validation
- **Use case**: Visual diff generation, structural similarity analysis

### OCR Support (`ocr`)

- **Dependencies**: `pytesseract>=0.3.13`
- **Purpose**: Optical Character Recognition
- **Use case**: Extract text from images and scanned documents
- **Note**: Requires system-level Tesseract OCR installation

### Wand Support (`wand`)

- **Dependencies**: `Wand>=0.6.13`, `pytesseract>=0.3.13`
- **Purpose**: ImageMagick-based image processing
- **Use case**: Advanced image manipulation and format conversion
- **Note**: Requires system-level ImageMagick installation

## System Dependencies

Some optional dependencies require system-level packages:

### Tesseract OCR (for `ocr` group)

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### ImageMagick (for `wand` group)

```bash
# Ubuntu/Debian
sudo apt-get install imagemagick libmagickwand-dev

# macOS
brew install imagemagick

# Windows
# Download from: https://imagemagick.org/script/download.php#windows
```

## Testing with Optional Dependencies

### Running All Tests

```bash
# With hatch (recommended)
hatch run test

# With pip/uv (install all dependencies first)
pip install -e .[all]
pytest

# Or with uv
uv pip install -e .[all]
pytest
```

### Running Specific Test Categories

```bash
# Core tests only (no optional dependencies)
hatch run test-core
# or
pytest -m "not psd and not validation and not ocr"

# PSD-related tests only
hatch run test-psd
# or
pytest -m psd

# Validation tests only
hatch run test-validation
# or
pytest -m validation

# OCR tests only
pytest -m ocr
```

## Troubleshooting

### ImportError: No module named 'psd_tools'

```bash
# Install PSD support
pip install -e .[psd]
# or
uv pip install -e .[psd]
```

### ImportError: No module named 'skimage'

```bash
# Install validation support
pip install -e .[validation]
# or
uv pip install -e .[validation]
```

### ImportError: No module named 'pytesseract'

```bash
# Install OCR support
pip install -e .[ocr]
# or
uv pip install -e .[ocr]

# Also install system Tesseract (see System Dependencies above)
```

### Test Discovery Failures

If you encounter ImportError during test discovery:

1. **Install development dependencies**:

   ```bash
   pip install -e .[dev,test,all]
   ```

2. **Use hatch for development** (recommended):

   ```bash
   hatch env create
   hatch run test
   ```

3. **Check missing dependencies**:

   ```bash
   pytest --collect-only
   ```

### Performance Issues

For better performance with large dependency sets:

1. **Use uv instead of pip**:

   ```bash
   uv pip install -e .[all]
   ```

2. **Use hatch environments**:

   ```bash
   hatch env create  # Creates environment with all dependencies
   hatch shell       # Activates the environment
   ```

## Development Workflow

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd pdfrebuilder

# Set up development environment
hatch env create
hatch shell

# Verify installation
hatch run test --collect-only
```

### Adding New Optional Dependencies

1. **Add to appropriate group in `pyproject.toml`**:

   ```toml
   [project.optional-dependencies]
   mygroup = [
       "new-package>=1.0.0",
   ]
   ```

2. **Update the `all` group**:

   ```toml
   all = [
       # ... existing dependencies
       "new-package>=1.0.0",
   ]
   ```

3. **Update this documentation** with the new group details.

4. **Add pytest markers** if needed for test categorization.

## See Also

- [Installation Guide](INSTALLATION.md) - Basic installation instructions
- [Development Setup](INSTALL-dev.md) - Development-specific setup
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
