# Changelog

All notable changes to the Multi-Format Document Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Development environment setup procedures
- Troubleshooting guide for common development issues

### Changed

- Improved documentation structure and organization

### Security

- Enhanced XML processing security with defusedxml
- Input validation and sanitization improvements

## [0.1.0] - Development Version

**Status**: Pre-release development version

### Added

- PDF extraction and reconstruction capabilities
- Basic PSD file support with layer extraction
- Universal Document Structure Schema v1.0
- Engine abstraction layer for multiple PDF backends
- Font management system with automatic downloading
- Visual validation tools for document comparison
- Comprehensive test suite with coverage reporting
- Documentation system with API reference
- CLI interface with multiple operation modes
- Configuration override system with JSON5 support

### Core Features

- **PDF Processing**: Text, image, and vector graphics extraction with accurate positioning
- **PSD Processing**: Layer-based extraction with hierarchy preservation
- **Engine Abstraction**: PyMuPDF (fitz) engine with extensible architecture
- **Font Management**: Automatic font detection, downloading, and caching
- **Visual Validation**: Pixel-perfect comparison with configurable thresholds

### Development Tools

- Hatch with UV for environment and dependency management
- Black for code formatting (line-length: 120)
- Ruff for linting and style enforcement
- MyPy for type checking
- Pytest for testing with coverage reporting
- Bandit for security analysis

### Key Dependencies

- PyMuPDF >= 1.26.23 (PDF processing)
- Pillow (Image processing)
- json5 (Configuration with comments)
- fonttools (Font analysis and manipulation)
- defusedxml >= 0.7.1 (Secure XML processing)
- psd-tools >= 1.9 (PSD file processing)
- opencv-python >= 4.5 (Visual validation)

### Known Limitations

- PSD layer effects not fully supported
- Limited support for complex PDF forms
- Large file processing may require memory optimization
- Some font configurations require manual setup

### Development Notes

- This is a pre-release version under active development
- APIs and configuration formats may change
- Comprehensive documentation available for developers

## Development Guidelines

### Contributing to Changelog

When contributing changes during development:

1. Add entries to the [Unreleased] section
2. Use these categories:
   - `Added` for new features
   - `Changed` for changes in existing functionality
   - `Fixed` for bug fixes
   - `Security` for security improvements

3. Include notes about configuration or API changes
4. Reference issue numbers where applicable

### Python Version Support

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.9 | Minimum | Supported but not recommended |
| 3.10 | Supported | Good for development |
| 3.11 | Supported | Performance improvements |
| 3.12 | Recommended | Current default version |
| 3.13 | Testing | Future support |

### Development Dependencies

Key dependencies are updated regularly during development:

- **PyMuPDF**: Core PDF processing - test thoroughly after updates
- **Pillow**: Image processing - verify image functionality
- **psd-tools**: PSD processing - test PSD features
- **defusedxml**: Security - keep updated for security fixes

For detailed development procedures, see [CONTRIBUTING.md](docs/CONTRIBUTING.md).
