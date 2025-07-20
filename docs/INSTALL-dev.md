# Development Installation Guide

This guide provides detailed installation instructions for setting up a development environment for PDFRebuilder.

## Prerequisites

- **Python 3.11 or higher** (Python 3.12 recommended)
- **Git** for version control
- **System dependencies** for PDF, image, and OCR processing

## Quick Development Setup

### Option 1: Hatch (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd pdfrebuilder

# Create and activate development environment
hatch env create
hatch shell

# Verify installation
hatch run python main.py --help
hatch run test
```

### Option 2: uv (Modern Alternative)

```bash
# Clone the repository
git clone <repository-url>
cd pdfrebuilder

# Sync with all dependencies
uv sync --extra all

# Activate environment and verify
source .venv/bin/activate
python main.py --help
pytest
```

## System Dependencies

### Required System Dependencies

These are required for core PDF processing functionality:

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y \
    python3-dev \
    build-essential \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config
```

#### macOS

```bash
# Using Homebrew
brew install freetype jpeg libpng pkg-config

# Ensure Xcode command line tools are installed
xcode-select --install
```

#### Windows

For Windows users, we recommend using WSL2 (Windows Subsystem for Linux):

```powershell
# Install WSL2 and Ubuntu
wsl --install -d Ubuntu

# Then follow Linux installation instructions within WSL2
```

### Optional System Dependencies

These are optional but recommended for full functionality:

#### Tesseract OCR (for OCR functionality)

Tesseract OCR is required for text extraction from images and PSD files. It's included as an optional dependency in the development environment.

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**macOS:**

```bash
brew install tesseract
```

**Windows (WSL2):**

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**Windows (Native):**
Download from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

#### ImageMagick (for Wand engine)

ImageMagick is required for advanced image processing and PSD support.

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install libmagickwand-dev
```

**macOS:**

```bash
brew install imagemagick
```

**Windows (WSL2):**

```bash
sudo apt-get install libmagickwand-dev
```

## Development Environment Setup

### Method 1: Using Hatch (Recommended)

Hatch automatically manages dependencies and virtual environments:

```bash
# Install hatch if not already installed
pip install hatch

# Create development environment with all dependencies
hatch env create

# Activate the environment
hatch shell

# Verify installation
python main.py --help
pytest --version
```

### Method 2: Using uv (Modern Approach)

```bash
# Install uv if not already installed
pip install uv

# Sync with all optional dependencies (recommended for development)
uv sync --extra all

# Or sync with specific optional dependencies
uv sync --extra dev --extra test --extra ocr

# Or sync with development dependencies only
uv sync --dev

# Activate environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Verify installation
python main.py --help
```

### Method 3: Manual pip Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install in development mode with all optional dependencies
pip install -e .[dev,test,all]

# Verify installation
python main.py --help
```

## Optional Dependency Groups

PDFRebuilder supports several optional dependency groups for different functionality:

### Core Optional Groups

```bash
# OCR functionality (includes pytesseract)
pip install -e .[ocr]

# PSD file support
pip install -e .[psd]

# Wand/ImageMagick support (includes OCR)
pip install -e .[wand]

# Enhanced validation features
pip install -e .[validation]

# CLI enhancements
pip install -e .[cli]
```

### Development Groups

```bash
# Testing dependencies (includes OCR for test coverage)
pip install -e .[test]

# Development tools (includes OCR, linting, formatting)
pip install -e .[dev]

# Performance testing
pip install -e .[performance]

# All dependencies
pip install -e .[all]
```

### Using uv with Optional Dependencies

```bash
# Sync with all optional dependencies (recommended)
uv sync --extra all

# Sync with specific optional groups
uv sync --extra ocr --extra psd --extra wand

# Sync with development and testing dependencies
uv sync --extra dev --extra test

# Add new dependencies and sync
uv add pytesseract --optional ocr
uv sync --extra ocr
```

### Using Hatch with Optional Dependencies

```bash
# Install specific optional groups
hatch env create --template dev
hatch run --env dev python main.py --help

# Or modify pyproject.toml and recreate environment
hatch env remove
hatch env create
```

## Verifying Installation

### Basic Verification

```bash
# Check Python version
python --version  # Should be 3.11+

# Check main application
python main.py --help

# Check core dependencies
python -c "import fitz; print(f'PyMuPDF version: {fitz.__version__}')"
python -c "import PIL; print(f'Pillow version: {PIL.__version__}')"
```

### OCR Functionality Verification

```bash
# Check if pytesseract is installed
python -c "import pytesseract; print(f'pytesseract version: {pytesseract.__version__}')"

# Check if Tesseract binary is available
tesseract --version

# Test OCR functionality in code
python -c "
from src.engine.extract_wand_content import check_tesseract_availability
is_available, info = check_tesseract_availability()
print(f'Tesseract available: {is_available}')
if is_available:
    print(f'Version: {info[\"tesseract_version\"]}')
else:
    print(f'Error: {info[\"error\"]}')
"
```

### Wand/ImageMagick Verification

```bash
# Check if Wand is installed
python -c "import wand; print('Wand available')"

# Check ImageMagick version
python -c "
from wand.version import MAGICK_VERSION, VERSION
print(f'Wand version: {VERSION}')
print(f'ImageMagick version: {MAGICK_VERSION}')
"

# Test Wand functionality
python -c "
from src.engine.extract_wand_content import check_wand_availability
is_available, info = check_wand_availability()
print(f'Wand available: {is_available}')
if is_available:
    print(f'Wand version: {info[\"wand_version\"]}')
    print(f'ImageMagick version: {info[\"imagemagick_version\"]}')
else:
    print(f'Error: {info[\"error\"]}')
"
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
hatch run test

# Run with coverage
hatch run test-cov

# Run specific test categories
hatch run test-unit
hatch run test-integration
hatch run test-performance
```

### OCR-Related Tests

```bash
# Run OCR-specific tests
hatch run test tests/test_wand_engine.py -k tesseract -v

# Run tests that require actual Tesseract installation
hatch run test tests/test_wand_engine.py::TestWandEngine::test_tesseract_actual_functionality -v

# Skip OCR tests if Tesseract is not available (tests will auto-skip)
hatch run test tests/test_wand_engine.py -v
```

### Test Environment Without OCR

To test the behavior when OCR is not available:

```bash
# Create a clean environment without OCR dependencies
python -m venv test_env_no_ocr
source test_env_no_ocr/bin/activate

# Install without OCR dependencies
pip install -e .

# Run tests (OCR tests should be skipped)
python -m pytest tests/test_wand_engine.py -k tesseract -v
```

## Development Tools

### Code Quality Tools

```bash
# Format code with Black
hatch run lint:style

# Lint with Ruff
hatch run lint:lint

# Type checking with MyPy
hatch run lint:typing

# Security scanning
hatch run security-scan

# Dead code detection
hatch run vulture-check
```

### Pre-commit Hooks (if available)

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Troubleshooting

### Common Issues

#### 1. Tesseract Not Found

**Error:** `"Tesseract OCR is not available: tesseract is not installed or it's not in your PATH"`

**Solution:**

```bash
# Install Tesseract system package
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # macOS

# Verify installation
tesseract --version

# If installed but not in PATH, set environment variable
export TESSERACT_CMD=/usr/local/bin/tesseract  # Adjust path as needed
```

#### 2. ImageMagick/Wand Issues

**Error:** `"Python-Wand is not installed"` or ImageMagick errors

**Solution:**

```bash
# Install ImageMagick system package first
sudo apt-get install libmagickwand-dev  # Linux
brew install imagemagick                # macOS

# Then install Python package
pip install Wand

# Verify installation
python -c "from wand.image import Image; print('Wand working')"
```

#### 3. PyMuPDF Installation Issues

**Error:** PyMuPDF compilation errors

**Solution:**

```bash
# Update pip and build tools
pip install --upgrade pip setuptools wheel

# Install system dependencies
sudo apt-get install python3-dev build-essential  # Linux

# Try installing with verbose output
pip install --verbose PyMuPDF
```

#### 4. Permission Errors

**Error:** Permission denied during installation

**Solution:**

```bash
# Never use sudo with pip for user installations
# Use virtual environments instead
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Or use user installation
pip install --user -e .[dev]
```

#### 5. Environment Issues

**Error:** Dependencies not found or version conflicts

**Solution:**

```bash
# Clean and recreate environment
hatch env remove
hatch env create

# Or with manual venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Testing Installation

Use the provided verification script:

```bash
# Run comprehensive installation verification
hatch run python scripts/verify_installation.py

# Check specific components
python scripts/verify_installation.py --check-ocr
python scripts/verify_installation.py --check-wand
```

### Getting Help

If you encounter issues:

1. **Check system requirements**: Ensure all prerequisites are met
2. **Review error messages**: Look for specific missing dependencies
3. **Check logs**: Enable verbose output for detailed error information
4. **Search existing issues**: Check the project repository for similar problems
5. **Create a new issue**: Include detailed error information, system details, and steps to reproduce

## Environment Variables

### Optional Configuration

```bash
# Tesseract binary path (if not in system PATH)
export TESSERACT_CMD=/usr/local/bin/tesseract

# ImageMagick configuration
export MAGICK_HOME=/usr/local

# Development settings
export PYTHONPATH=.
export FONTTOOLS_LOG_LEVEL=WARNING
```

### For Testing

```bash
# Suppress verbose logging during tests
export FONTTOOLS_LOG_LEVEL=WARNING

# Enable debug mode for development
export DEBUG=1
```

## Next Steps

After successful development environment setup:

1. **Run the test suite**: `hatch run test` to ensure everything works
2. **Try the examples**: Explore the `examples/` directory
3. **Read the API documentation**: Review `docs/api/` for development guidance
4. **Check the contributing guide**: See `docs/CONTRIBUTING.md` for development workflow
5. **Set up your IDE**: Configure your editor with the project's linting and formatting tools

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

### PyCharm

1. Set Python interpreter to `.venv/bin/python`
2. Configure Black as the code formatter
3. Enable Ruff for linting
4. Set pytest as the test runner
