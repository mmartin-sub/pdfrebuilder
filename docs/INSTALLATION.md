# Installation Guide

This guide provides detailed installation instructions for PDFRebuilder (formerly Multi-Format Document Engine).

## Prerequisites

- **Python 3.11 or higher** (Python 3.12 recommended)
- **uv** package manager (recommended) or **pip**
- **System dependencies** for PDF and image processing

## System Requirements

### Operating Systems

- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 10+, or equivalent
- **macOS**: 10.15+ (Catalina or later)
- **Windows**: 10+ with WSL2 recommended for best compatibility

### Python Dependencies

PDFRebuilder uses modern Python package management with [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management and supports multiple installation methods.

## Quick Start

For most users, the fastest way to get started:

```bash
# Install uv (if not already installed)
pip install uv

# Install PDFRebuilder globally
uv tool install pdfrebuilder

# Start using it
pdfrebuilder --help
pdfrebuilder --generate-config
```

## Installation Methods

### Method 1: Global Tool Installation (Recommended)

Install PDFRebuilder as a global command-line tool using `uv tool install`. This is the recommended method for most users.

1. **Install uv** (if not already installed):

   ```bash
   # Using pip
   pip install uv

   # Using pipx (recommended)
   pipx install uv

   # Using curl (Linux/macOS)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Using homebrew (macOS)
   brew install uv
   ```

2. **Install PDFRebuilder globally**:

   ```bash
   # Install from PyPI (when published)
   uv tool install pdfrebuilder

   # Or install from local wheel (for development)
   uv tool install ./dist/pdfrebuilder-0.1.0-py3-none-any.whl
   ```

3. **Verify installation**:

   ```bash
   # Check if pdfrebuilder is available
   pdfrebuilder --help

   # Generate sample configuration
   pdfrebuilder --generate-config

   # Show current configuration
   pdfrebuilder --show-config
   ```

4. **Update PATH** (if needed):

   ```bash
   # Add uv tools to PATH if not already done
   export PATH="$HOME/.local/bin:$PATH"

   # Or use uv's automatic shell integration
   uv tool update-shell
   ```

**Note:** For development work or if you need OCR functionality, see the [Development Installation Guide](INSTALL-dev.md) for detailed setup instructions including Tesseract OCR and ImageMagick installation.

### Method 2: Isolated Execution with uvx

Run PDFRebuilder without permanent installation using `uvx`. This method downloads and runs the tool in an isolated environment.

```bash
# Run directly without installing (from PyPI)
uvx pdfrebuilder --help
uvx pdfrebuilder --mode extract --input document.pdf

# Run from local wheel
uvx --from ./dist/pdfrebuilder-0.1.0-py3-none-any.whl pdfrebuilder --help

# Run with specific Python version
uvx --python 3.12 pdfrebuilder --help
```

### Method 3: Library Installation

Install PDFRebuilder as a Python library for programmatic use in your projects.

```bash
# Install as project dependency
uv add pdfrebuilder

# Or using pip
pip install pdfrebuilder

# Install with optional dependencies
uv add "pdfrebuilder[psd,wand,all]"
```

Then use in Python code:

```python
from pdfrebuilder import extract, rebuild, compare
from pdfrebuilder.config import ConfigManager

# Use as library
config_manager = ConfigManager()
document = extract("input.pdf", engine="auto")
rebuild(document, "output.pdf")
```

### Method 4: Development Installation

For development work, contributing to the project, or when you need access to the full source code.

1. **Install development tools**:

   ```bash
   # Install uv and hatch
   pip install uv hatch

   # Or using pipx (recommended)
   pipx install uv
   pipx install hatch
   ```

2. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd pdfrebuilder
   ```

3. **Create and activate development environment**:

   ```bash
   # Using hatch (recommended for development)
   hatch env create
   hatch shell

   # Or using uv (with all optional dependencies)
   uv sync --extra all

   # Or with specific dependencies only
   uv sync --extra dev --extra test --extra ocr
   ```

4. **Verify development installation**:

   ```bash
   # Check main application
   hatch run python main.py --help

   # Verify PyMuPDF version
   hatch run python -c "import fitz; print(f'PyMuPDF version: {fitz.__version__}')"

   # Run basic tests
   hatch run test

   # Run development tools
   hatch run lint:style --check
   hatch run lint:lint
   ```

### Method 5: Building from Source

Build and install your own wheel from source code.

```bash
# Clone repository
git clone <repository-url>
cd pdfrebuilder

# Build wheel
uv build

# Install the built wheel globally
uv tool install ./dist/pdfrebuilder-0.1.0-py3-none-any.whl

# Or install as library
uv pip install ./dist/pdfrebuilder-0.1.0-py3-none-any.whl
```

## Development Installation

For development work, additional tools and dependencies are needed:

```bash
# Create development environment with all optional dependencies
hatch env create

# Activate development environment
hatch shell

# Verify development tools
hatch run lint:style --check  # Black formatting
hatch run lint:lint           # Ruff linting
hatch run lint:typing         # MyPy type checking

# Run comprehensive tests
hatch run test                # Basic tests
hatch run test-cov           # Tests with coverage

# Install pre-commit hooks (if available)
# hatch run pre-commit install
```

### Optional Dependencies

The project supports several optional dependency groups. For detailed installation instructions with both pip and uv examples, see [OPTIONAL_DEPENDENCIES.md](OPTIONAL_DEPENDENCIES.md).

Quick overview:

```bash
# For OCR functionality (requires Tesseract OCR system installation)
pip install "pdfrebuilder[ocr]"

# For PSD file support (experimental)
pip install "pdfrebuilder[psd]"

# For Wand/ImageMagick support (includes OCR, requires ImageMagick system installation)
pip install "pdfrebuilder[wand]"

# For enhanced validation features
pip install "pdfrebuilder[validation]"

# For CLI enhancements
pip install "pdfrebuilder[cli]"

# For development tools (includes OCR for testing)
pip install "pdfrebuilder[dev]"

# Install all optional dependencies
pip install "pdfrebuilder[all]"
```

#### OCR Functionality (Optional)

For text extraction from images and PSD files, install Tesseract OCR:

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
pip install "pdfrebuilder[ocr]"
```

**macOS:**

```bash
brew install tesseract
pip install "pdfrebuilder[ocr]"
```

**Windows:**

1. Download Tesseract from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. `pip install "pdfrebuilder[ocr]"`

#### Advanced Image Processing (Optional)

For PSD file support and advanced image processing, install ImageMagick:

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install libmagickwand-dev
pip install "pdfrebuilder[wand]"
```

**macOS:**

```bash
brew install imagemagick
pip install "pdfrebuilder[wand]"
```

## System Dependencies

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies for PDF and image processing
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

### macOS

```bash
# Using Homebrew
brew install freetype jpeg libpng pkg-config

# Ensure Xcode command line tools are installed
xcode-select --install
```

### Windows

For Windows users, we recommend using WSL2 (Windows Subsystem for Linux) for the best compatibility:

```powershell
# Install WSL2 and Ubuntu
wsl --install -d Ubuntu

# Then follow Linux installation instructions within WSL2
```

## Troubleshooting

### Common Issues

1. **Python version compatibility**:

   ```bash
   # Check Python version
   python --version
   # Should be 3.11 or higher, 3.12 recommended

   # If using multiple Python versions
   python3.12 -m pip install uv
   ```

2. **uv tool install PATH issues**:

   ```bash
   # If pdfrebuilder command not found after uv tool install
   export PATH="$HOME/.local/bin:$PATH"

   # Make permanent by adding to shell profile
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   # or for zsh
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

   # Or use uv's automatic shell integration
   uv tool update-shell
   ```

3. **uv installation issues**:

   ```bash
   # If uv installation fails, try different methods
   pip install --upgrade uv
   # or
   pipx install uv
   # or
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **PyMuPDF installation issues**:

   ```bash
   # If PyMuPDF fails to install, try updating pip first
   pip install --upgrade pip setuptools wheel

   # For development installations
   hatch env create --force
   ```

5. **Permission errors**:

   ```bash
   # uv tool install handles permissions automatically
   # Never use sudo with uv or pip for user installations

   # If needed, install uv with --user flag
   pip install --user uv
   ```

6. **Missing system dependencies**:

   ```bash
   # On Linux, install development packages
   sudo apt install python3-dev build-essential

   # On macOS, ensure Xcode tools are installed
   xcode-select --install
   ```

7. **Configuration directory issues**:

   ```bash
   # If configuration generation fails
   mkdir -p ~/.config/pdfrebuilder
   chmod 755 ~/.config/pdfrebuilder

   # Test configuration system
   pdfrebuilder --generate-config
   pdfrebuilder --show-config
   ```

8. **Tesseract OCR issues**:

   ```bash
   # If OCR functionality is not working
   # First, verify Tesseract is installed
   tesseract --version

   # If not installed, install system package
   sudo apt-get install tesseract-ocr  # Linux
   brew install tesseract              # macOS

   # Then install Python package
   pip install pytesseract

   # Test OCR availability
   python -c "
   from src.engine.extract_wand_content import check_tesseract_availability
   is_available, info = check_tesseract_availability()
   print(f'OCR available: {is_available}')
   if not is_available: print(f'Error: {info[\"error\"]}')
   "
   ```

9. **ImageMagick/Wand issues**:

   ```bash
   # If Wand functionality is not working
   # Install ImageMagick system package first
   sudo apt-get install libmagickwand-dev  # Linux
   brew install imagemagick                # macOS

   # Then install Python package
   pip install Wand

   # Test Wand availability
   python -c "
   from src.engine.extract_wand_content import check_wand_availability
   is_available, info = check_wand_availability()
   print(f'Wand available: {is_available}')
   if not is_available: print(f'Error: {info[\"error\"]}')
   "
   ```

### Environment Issues

If you encounter environment-related problems:

```bash
# Clean and recreate environment
hatch env remove
hatch env create

# Check environment status
hatch env show

# Run with verbose output for debugging
hatch run --verbose python main.py --help
```

### Getting Help

If you encounter issues:

1. **Check the troubleshooting guide**: [docs/guides/troubleshooting.md](guides/troubleshooting.md)
2. **Review system requirements**: Ensure all prerequisites are met
3. **Check logs**: Look for error messages in console output
4. **Search existing issues**: Check the project repository for similar problems
5. **Create a new issue**: Include detailed error information, system details, and steps to reproduce

## Verification

After installation, verify everything works correctly:

### For Global Tool Installation

```bash
# Test basic functionality
pdfrebuilder --help

# Test configuration system
pdfrebuilder --generate-config
pdfrebuilder --show-config

# Test with sample document (if available)
pdfrebuilder --mode extract --input sample.pdf --config output.json
```

### For Library Installation

```bash
# Check PyMuPDF version and functionality
python -c "
import fitz
print(f'PyMuPDF version: {fitz.__version__}')
doc = fitz.open()
print('PyMuPDF working correctly')
"

# Test library import
python -c "
from pdfrebuilder.config import ConfigManager
config = ConfigManager()
print('PDFRebuilder library working correctly')
"
```

### For Development Installation

```bash
# Test main application
hatch run python main.py --help

# Run tests to verify installation
hatch run test

# Test development tools
hatch run lint:style --check
```

### Automated Verification

Use the provided verification script to check your installation:

```bash
# For development installations
hatch run python scripts/verify_installation.py

# For global installations (if you have the source)
python scripts/verify_installation.py
```

This script will check:

- Python version compatibility
- uv installation and functionality
- PDFRebuilder CLI availability
- Library import capabilities
- Key dependencies
- Configuration system functionality

## Next Steps

After successful installation:

1. **Basic Usage**: See [Getting Started Guide](guides/getting-started.md)
2. **Examples**: Explore [examples/](../examples/) directory
3. **API Documentation**: Review [API Reference](api/) for development
4. **Configuration**: Check [Configuration Reference](reference/configuration.md)
5. **CLI Usage**: See [CLI Reference](reference/cli.md) for command-line options
