# Implementation Plan

## Overview

This implementation plan transforms the current PDF Layout Extractor into `pdfrebuilder`, a modern dual-purpose Python package that works both as a CLI tool and as a library. The plan follows Python 3.12+ best practices and uses the src/ layout structure.

## Tasks

### 1. Configuration System Foundation (Before File Migration)

- [ ] 1.1 Implement configuration data models in current structure
  - Create `src/config/models.py` with Pydantic models for all configuration options
  - Define ExtractionConfig, RebuildConfig, LoggingConfig, PathConfig, SecurityConfig
  - Add validation and type checking for all configuration options
  - Support both environment variables and configuration file options
  - _Requirements: 2.3, 6.5, 8.4_

- [ ] 1.2 Create configuration manager with file and environment support
  - Implement `src/config/manager.py` with ConfigManager class
  - Support loading from TOML/JSON configuration files via CLI --config option
  - Support environment variables with PDFREBUILDER_ prefix for non-sensitive settings
  - Implement hierarchical configuration: CLI args > config file > env vars > defaults
  - Add secure handling for sensitive settings (only in config files, not env vars)
  - _Requirements: 2.1, 2.2, 2.4, 7.1, 7.2, 13.4_

- [ ] 1.3 Add CLI configuration file support to existing main.py
  - Add --config-file option to existing CLI for loading comprehensive configuration
  - Support both TOML and JSON configuration file formats
  - Add --generate-config option to create sample configuration files with all options
  - Implement configuration validation and error reporting
  - Add --show-config option to display current effective configuration
  - Support configuration sections for: paths, logging, engines, extraction, rebuild, security
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 1.4 Create comprehensive configuration file examples
  - Create sample pdfrebuilder.toml with all configuration options documented
  - Add environment-specific configuration examples (dev.toml, prod.toml)
  - Include security-sensitive settings (API keys, paths) in config file only
  - Add configuration for temporary directories, output paths, engine settings
  - Document precedence: CLI args > config file > environment variables > defaults
  - Example structure:

    ```toml
    [paths]
    temp_dir = "/tmp/pdfrebuilder"
    output_dir = "./output"
    cache_dir = "~/.cache/pdfrebuilder"

    [logging]
    level = "INFO"
    format = "standard"  # or "json"
    file = "pdfrebuilder.log"

    [engines]
    input_engine = "auto"
    output_engine = "reportlab"

    [extraction]
    include_text = true
    include_images = true
    include_drawings = true

    [security]
    validate_paths = true
    secure_temp_files = true
    ```

  - _Requirements: 7.1, 7.2, 13.4_

- [ ] 1.5 Implement environment-aware configuration defaults
  - Add environment detection (development, testing, production, CI/CD)
  - Create different default configurations per environment
  - Support PDFREBUILDER_ENV environment variable for environment selection
  - Add container and headless operation detection
  - _Requirements: 8.1, 8.2, 8.3_

### 2. Enhanced Resource and Path Management (Before File Migration)

- [ ] 2.1 Implement configurable temporary directory support
  - Add temp_dir configuration option (config file and CLI --temp-dir)
  - Support PDFREBUILDER_TEMP_DIR environment variable as fallback
  - Implement secure temporary directory creation with proper permissions
  - Add automatic cleanup and resource management
  - _Requirements: 4.3, 4.4, 4.5, 13.3_

- [ ] 2.2 Create secure path management utilities
  - Implement path validation and sanitization functions
  - Add cross-platform path handling with pathlib
  - Create secure file permission setting (600 for config, 644 for output)
  - Add path resolution for configuration directories
  - _Requirements: 12.4, 13.1, 13.2_

- [ ] 2.3 Integrate enhanced configuration with existing settings.py
  - Update existing CONFIG dict to use new configuration system
  - Add backward compatibility layer for existing configuration access
  - Implement configuration migration from old format
  - Add deprecation warnings for direct CONFIG dict access
  - _Requirements: 11.2, 11.4_

### 3. Modern Logging System (Before File Migration)

- [ ] 3.1 Implement structured logging in current structure
  - Create `src/utils/logging.py` with modern logging setup
  - Implement StructuredFormatter for JSON logging output
  - Add configurable log levels, formats, and output destinations
  - Support both console and file logging with rotation
  - _Requirements: 3.1, 3.2, 3.4_

- [ ] 3.2 Add logging configuration to config system
  - Add LoggingConfig model with all logging options
  - Support log file paths, levels, formats in configuration files
  - Add CLI options for common logging settings (--log-level, --log-file, --log-format)
  - Implement environment-specific logging defaults
  - _Requirements: 3.1, 3.3, 3.4_

- [ ] 3.3 Replace existing console_print with proper logging
  - Update existing console_print function to use new logging system
  - Maintain Rich formatting for CLI output while adding proper logging
  - Add structured logging with context information
  - Implement proper error logging with stack traces
  - _Requirements: 3.5, 3.6, 11.1_

### 4. Project Structure Setup (After Configuration Foundation)

- [ ] 4.1 Create new src/ directory structure
  - Create `src/pdfrebuilder/` directory structure with all subdirectories
  - Set up proper `__init__.py` files in each module
  - Add `py.typed` marker file for type hints
  - Use platformdirs for cross-platform directory detection
  - _Requirements: 1.1, 5.1, 12.1, 12.2, 12.3_

- [ ] 4.2 Update pyproject.toml for modern package configuration
  - Update project metadata with new name `pdfrebuilder`
  - Configure src/ layout in build system
  - Add proper entry points for CLI and library
  - Update dependencies with version constraints
  - Add optional dependencies for different engines
  - _Requirements: 5.1, 5.4, 5.5, 10.1, 10.2_

- [ ] 4.3 Create package initialization and exports
  - Implement `src/pdfrebuilder/__init__.py` with clean library API exports
  - Add version information and metadata
  - Export main functions: extract, rebuild, compare, process_pipeline
  - Export main classes: PDFRebuilder, ConfigManager
  - _Requirements: 1.2, 6.1_

### 5. Configuration System Migration to New Structure

- [ ] 5.1 Migrate configuration system to new package structure
  - Move configuration models to `src/pdfrebuilder/models/config.py`
  - Move configuration manager to `src/pdfrebuilder/config/manager.py`
  - Update imports and references throughout codebase
  - Ensure all configuration features work in new structure
  - _Requirements: 2.1, 2.2, 2.4, 7.1, 7.2_

- [ ] 5.2 Add comprehensive configuration file examples
  - Create sample configuration files for different use cases
  - Add configuration templates for development, testing, production
  - Document all configuration options with examples
  - Create configuration validation and schema documentation
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 5.3 Implement configuration migration system
  - Create `src/pdfrebuilder/config/migration.py` for backward compatibility
  - Migrate existing settings.py CONFIG dict to new format
  - Support legacy environment variables with deprecation warnings
  - Automatically migrate old configuration files
  - _Requirements: 11.2, 11.4_

### 6. Logging System Migration to New Structure

- [ ] 6.1 Migrate logging system to new package structure
  - Move logging utilities to `src/pdfrebuilder/utils/logging.py`
  - Update all modules to use new logging system
  - Ensure logging configuration integrates with new config system
  - Test logging in both CLI and library contexts
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 6.2 Create logger hierarchy and utilities
  - Implement get_logger function for consistent logger naming
  - Set up proper logger hierarchy under "pdfrebuilder" namespace
  - Add context managers for temporary log level changes
  - Implement log filtering for sensitive information
  - _Requirements: 3.1, 3.6_

- [ ] 6.3 Add advanced logging features
  - Implement log rotation and archiving
  - Add performance logging and metrics
  - Create debug logging with detailed context
  - Add logging for security-sensitive operations
  - _Requirements: 3.5, 3.6_

### 4. Resource Management System

- [ ] 4.1 Implement resource manager with automatic cleanup
  - Create `src/pdfrebuilder/utils/resources.py` with ResourceManager class
  - Implement context managers for temporary files and directories
  - Use tempfile module for secure temporary file creation
  - Register cleanup handlers with atexit
  - _Requirements: 4.1, 4.2, 9.2, 9.4_

- [ ] 4.2 Add configurable temporary directory support
  - Support custom temporary directory via environment variables
  - Respect container filesystem constraints
  - Implement isolated temporary directories for concurrent instances
  - Add memory usage monitoring for large file processing
  - _Requirements: 4.3, 4.4, 4.5, 8.5, 9.1_

- [ ] 4.3 Integrate resource management with existing code
  - Replace manual directory creation with resource manager
  - Update all temporary file usage to use context managers
  - Ensure proper cleanup in error conditions
  - Add resource usage logging and monitoring
  - _Requirements: 9.3, 9.5_

### 5. Core Library API Implementation

- [ ] 5.1 Create high-level library API functions
  - Implement `src/pdfrebuilder/core/extractor.py` with extract function
  - Implement `src/pdfrebuilder/core/rebuilder.py` with rebuild function
  - Implement `src/pdfrebuilder/core/comparator.py` with compare function
  - Create `src/pdfrebuilder/core/processor.py` with process_pipeline function
  - _Requirements: 6.1, 6.2_

- [ ] 5.2 Implement PDFRebuilder main class
  - Create main PDFRebuilder class for advanced usage
  - Add context manager support (__enter__, __exit__)
  - Implement configuration management integration
  - Add async method variants for all operations
  - _Requirements: 6.3, 6.5_

- [ ] 5.3 Create data models for library interface
  - Implement `src/pdfrebuilder/models/document.py` with DocumentStructure
  - Create ComparisonResult and PipelineResult models
  - Add serialization methods (save/load) for document structures
  - Implement proper error handling with custom exceptions
  - _Requirements: 6.4_

### 6. Engine Abstraction and Migration

- [ ] 6.1 Create base engine interface
  - Implement `src/pdfrebuilder/engines/base.py` with abstract base class
  - Define standard interface for all processing engines
  - Add engine capability detection and metadata
  - Implement engine selection logic with fallbacks
  - _Requirements: 1.2, 6.5_

- [ ] 6.2 Migrate existing engines to new structure
  - Move and refactor existing FitzPDFEngine to `src/pdfrebuilder/engines/fitz_engine.py`
  - Move ReportLab engine to `src/pdfrebuilder/engines/reportlab_engine.py`
  - Move Wand engine to `src/pdfrebuilder/engines/wand_engine.py`
  - Update all engines to use new configuration system
  - _Requirements: 11.1_

- [ ] 6.3 Implement engine plugin system
  - Add entry points for engine discovery
  - Create engine registry and factory pattern
  - Support dynamic engine loading
  - Add engine validation and testing utilities
  - _Requirements: 6.5_

### 7. CLI Interface Implementation

- [ ] 7.1 Create modern CLI with Typer
  - Implement `src/pdfrebuilder/cli/main.py` with Typer-based CLI
  - Create extract, rebuild, pipeline, and compare commands
  - Add rich help text and argument validation
  - Implement proper error handling and user feedback
  - _Requirements: 1.3, 11.1_

- [ ] 7.2 Implement CLI console utilities
  - Create `src/pdfrebuilder/cli/console.py` with Rich-based output
  - Replace existing console_print with Rich console
  - Add progress bars for long-running operations
  - Implement colored output and formatting
  - _Requirements: 1.3_

- [ ] 7.3 Add CLI entry points and __main__.py
  - Create `src/pdfrebuilder/__main__.py` for python -m pdfrebuilder
  - Configure console_scripts entry point in pyproject.toml
  - Test CLI installation and execution
  - Ensure CLI works with all installation methods (pip, uv, uvx)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 10.1, 10.2, 10.3, 10.4_

### 8. Security and Path Management

- [ ] 8.1 Implement secure path utilities
  - Create `src/pdfrebuilder/utils/paths.py` with pathlib-based utilities
  - Add path validation and sanitization functions
  - Implement secure file permission setting
  - Add cross-platform path handling
  - _Requirements: 12.4, 13.2, 13.3_

- [ ] 8.2 Create security utilities module
  - Implement `src/pdfrebuilder/utils/security.py` with security functions
  - Add file permission management (600 for config, 644 for output)
  - Implement input validation and sanitization
  - Add privilege dropping utilities where applicable
  - _Requirements: 13.1, 13.4, 13.5_

- [ ] 8.3 Integrate security measures throughout codebase
  - Update all file operations to use secure permissions
  - Add input validation to all public API functions
  - Implement secure temporary file creation
  - Add security logging for sensitive operations
  - _Requirements: 13.1, 13.2, 13.3_

### 9. Environment Detection and Adaptation

- [ ] 9.1 Implement environment detection utilities
  - Create environment detection functions (development, testing, production, CI/CD)
  - Add container environment detection
  - Implement headless operation detection
  - Create environment-specific configuration defaults
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 9.2 Add environment-aware configuration
  - Implement different default settings per environment
  - Add debug mode with verbose logging for development
  - Create production mode with optimized settings
  - Add CI/CD mode with appropriate test settings
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 9.3 Integrate environment awareness with existing features
  - Update logging configuration based on environment
  - Adjust resource limits based on container constraints
  - Modify output verbosity based on environment
  - Add environment information to error reports
  - _Requirements: 8.5_

### 10. Testing Infrastructure

- [ ] 10.1 Set up comprehensive test structure
  - Create tests/ directory with unit/, integration/, e2e/ subdirectories
  - Implement pytest configuration with proper fixtures
  - Add test utilities for temporary directories and mock data
  - Create sample PDF fixtures for testing
  - _Requirements: All requirements need testing_

- [ ] 10.2 Implement unit tests for core components
  - Write tests for ConfigManager with different environments
  - Test logging system with various configurations
  - Test ResourceManager cleanup and isolation
  - Test all data models and validation
  - _Requirements: 2.1-2.4, 3.1-3.6, 4.1-4.5_

- [ ] 10.3 Create integration tests
  - Test CLI integration with all commands
  - Test library API integration
  - Test engine integration and fallbacks
  - Test cross-platform compatibility
  - _Requirements: 1.1-1.5, 5.1-5.7, 6.1-6.5, 12.1-12.5_

- [ ] 10.4 Add end-to-end tests
  - Test full pipeline with real PDF files
  - Test installation methods (pip, uv, uvx)
  - Test backward compatibility with existing configurations
  - Test security and permission handling
  - _Requirements: 10.1-10.6, 11.1-11.5, 13.1-13.5_

### 11. Documentation and Migration

- [ ] 11.1 Create comprehensive documentation
  - Write README.md with installation and usage examples
  - Create API documentation with examples
  - Add migration guide from old version
  - Document configuration options and environment variables
  - _Requirements: 5.6, 11.1-11.5_

- [ ] 11.2 Implement backward compatibility layer
  - Create compatibility imports for old module paths
  - Add deprecation warnings for old APIs
  - Support legacy configuration file formats
  - Provide migration utilities for existing users
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 11.3 Create migration scripts and tools
  - Build configuration migration script
  - Create project structure migration tool
  - Add validation for migrated configurations
  - Provide rollback capabilities for failed migrations
  - _Requirements: 11.2, 11.5_

### 12. Package Building and Distribution

- [ ] 12.1 Configure build system for src/ layout
  - Update pyproject.toml build configuration
  - Test wheel building with proper package structure
  - Verify entry points work correctly
  - Test installation from built wheel
  - _Requirements: 5.5, 5.6_

- [ ] 12.2 Add package metadata and classifiers
  - Complete project metadata in pyproject.toml
  - Add proper classifiers for PyPI
  - Include license and author information
  - Add project URLs and documentation links
  - _Requirements: 5.1, 5.4_

- [ ] 12.3 Test installation methods
  - Test pip install from source and wheel
  - Test uv add as project dependency
  - Test uv tool install for global installation
  - Test uvx for isolated execution
  - Verify all installation methods provide same functionality
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

### 13. Final Integration and Validation

- [ ] 13.1 Integrate all components
  - Wire together all new modules and systems
  - Update existing code to use new APIs
  - Remove deprecated code and temporary compatibility layers
  - Ensure all tests pass with new architecture
  - _Requirements: All requirements_

- [ ] 13.2 Performance optimization and validation
  - Profile memory usage with new resource management
  - Benchmark performance against old implementation
  - Optimize critical paths identified during testing
  - Validate resource cleanup under various conditions
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 13.3 Security audit and validation
  - Review all file operations for security issues
  - Test permission handling on different platforms
  - Validate input sanitization and path handling
  - Run security scanning tools on final codebase
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 13.4 Cross-platform testing and validation
  - Test on Windows, macOS, and Linux
  - Verify configuration directories are platform-appropriate
  - Test all installation methods on each platform
  - Validate path handling and file operations
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 13.5 Final documentation and release preparation
  - Complete all documentation with real examples
  - Create release notes and changelog
  - Prepare PyPI package description and metadata
  - Create installation and usage guides
  - _Requirements: 5.6, 11.1-11.5_

## Implementation Notes

### Migration Strategy

- Implement new components alongside existing code initially
- Use feature flags to gradually switch to new implementations
- Maintain backward compatibility throughout the process
- Provide clear migration path for existing users

### Testing Strategy

- Test each component in isolation before integration
- Use temporary directories and mock objects for unit tests
- Test with real PDF files for integration tests
- Validate on multiple platforms and Python versions

### Rollout Plan

1. Core infrastructure (config, logging, resources)
2. Library API implementation
3. CLI interface modernization
4. Engine migration and abstraction
5. Security and cross-platform features
6. Testing and documentation
7. Final integration and release

This implementation plan ensures a systematic transformation of the existing codebase into a modern, dual-purpose Python package that follows all Python 3.12+ best practices while maintaining backward compatibility.
