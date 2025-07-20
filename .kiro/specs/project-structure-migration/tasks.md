# Implementation Plan

- [x] 1. Preparation and Analysis
  - Create backup branch and analyze current structure
  - Scan all files for import patterns and dependencies
  - Create migration validation scripts
  - _Requirements: 1.1, 2.1, 5.1_

- [x] 1.1 Create migration analysis script
  - Write script to scan all Python files for import statements
  - Generate dependency map of internal imports
  - Identify all files that need import updates
  - _Requirements: 2.1, 2.2_

- [x] 1.2 Create import transformation script
  - Write automated script to update import statements
  - Handle different import patterns (absolute, relative, from imports)
  - Include validation to ensure imports resolve correctly
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 1.3 Create validation test script
  - Write comprehensive validation script to test migration
  - Include import resolution testing, CLI testing, and example execution
  - Test package installation and public API access
  - _Requirements: 4.1, 4.2, 4.3, 5.4_

- [x] 2. Set up new package structure
  - Create the new `src/pdfrebuilder/` directory structure
  - Create all necessary `__init__.py` files with proper exports
  - Set up the core/ subdirectory for main functionality
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2.1 Create main package __init__.py
  - Write `src/pdfrebuilder/__init__.py` with public API exports
  - Export key functions and classes for external use
  - Include version information and package metadata
  - _Requirements: 1.2, 5.5_

- [x] 2.2 Create core module structure
  - Create `src/pdfrebuilder/core/` directory and `__init__.py`
  - Set up proper exports for core functionality
  - Prepare for moving main PDF processing modules
  - _Requirements: 1.3, 1.4_

- [x] 2.3 Create subpackage __init__.py files
  - Create `__init__.py` files for all subpackages (engine, models, config, etc.)
  - Set up proper exports and imports for each subpackage
  - Ensure clean public interfaces for each module group
  - _Requirements: 1.3, 1.4_

- [x] 3. Migrate core functionality modules
  - Move main PDF processing files to `src/pdfrebuilder/core/`
  - Update imports in moved modules to use new package structure
  - Test core functionality after each module move
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 3.1 Move and update core PDF processing files
  - Move `src/compare_pdfs_visual.py` to `src/pdfrebuilder/core/`
  - Move `src/generate_debug_pdf_layers.py` to `src/pdfrebuilder/core/`
  - Move `src/pdf_engine.py` to `src/pdfrebuilder/core/`
  - Move `src/recreate_pdf_from_config.py` to `src/pdfrebuilder/core/`
  - Move `src/render.py` to `src/pdfrebuilder/core/`
  - Update all imports in these files to use new package structure
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 3.2 Move utility modules to package root
  - Move `src/settings.py` to `src/pdfrebuilder/settings.py`
  - Move `src/fritz.py` to `src/pdfrebuilder/fritz.py`
  - Move `src/font_utils.py` to `src/pdfrebuilder/font_utils.py`
  - Update imports in these files to use new package structure
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 3.3 Test core functionality after migration
  - Run tests for core PDF processing functionality
  - Verify all imports resolve correctly in moved modules
  - Test basic functionality to ensure no regressions
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 4. Migrate subpackages
  - Move all subpackage directories to `src/pdfrebuilder/`
  - Update internal imports within each subpackage
  - Test each subpackage after migration
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 4.1 Move config subpackage
  - Move `src/config/` to `src/pdfrebuilder/config/`
  - Update imports in config modules to use new package structure
  - Test configuration loading and management functionality
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 4.2 Move engine subpackage
  - Move `src/engine/` to `src/pdfrebuilder/engine/`
  - Update imports in all engine modules to use new package structure
  - Test PDF engine functionality and engine selection
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 4.3 Move models subpackage
  - Move `src/models/` to `src/pdfrebuilder/models/`
  - Update imports in model modules to use new package structure
  - Test data model functionality and schema validation
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 4.4 Move remaining subpackages
  - Move `src/font/` to `src/pdfrebuilder/font/`
  - Move `src/security/` to `src/pdfrebuilder/security/`
  - Move `src/tools/` to `src/pdfrebuilder/tools/`
  - Move `src/utils/` to `src/pdfrebuilder/utils/`
  - Update imports in all moved modules
  - _Requirements: 1.1, 2.1, 2.2_

- [x] 5. Consolidate and update CLI
  - Merge the duplicate CLI implementations into single consolidated CLI
  - Update CLI imports to use new package structure
  - Test all CLI commands and functionality
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.1 Consolidate CLI implementations
  - Merge functionality from `src/cli.py` and `src/pdfrebuilder/cli.py`
  - Create single `src/pdfrebuilder/cli.py` with all CLI functionality
  - Remove duplicate CLI file and resolve any conflicts
  - _Requirements: 3.1, 3.2_

- [x] 5.2 Move CLI subpackage
  - Move `src/cli/` to `src/pdfrebuilder/cli/`
  - Update imports in CLI command modules
  - Integrate CLI subcommands with main CLI module
  - _Requirements: 3.1, 3.4_

- [x] 5.3 Update CLI imports and test functionality
  - Update all imports in consolidated CLI to use new package structure
  - Test all CLI commands (extract, generate, full, debug modes)
  - Test CLI argument parsing and configuration loading
  - _Requirements: 3.3, 3.4, 3.5_

- [-] 6. Update tests and test configuration
  - Update all test imports to use new package structure
  - Update test configuration files for new structure
  - Run full test suite to ensure no regressions
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 6.1 Update test imports
  - Scan all test files for imports that need updating
  - Update test imports to use new `pdfrebuilder.*` package structure
  - Update test fixtures and configuration references
  - _Requirements: 4.1, 4.2_

- [ ] 6.2 Update test configuration
  - Update `pytest.ini` and `pyproject.toml` test configuration if needed
  - Update any test-specific configuration files
  - Ensure test discovery works with new package structure
  - _Requirements: 4.4, 4.5_

- [ ] 6.3 Run full test suite validation
  - Execute complete test suite to verify all tests pass
  - Fix any remaining import issues or test failures
  - Validate that test coverage is maintained
  - _Requirements: 4.3, 4.4, 4.5_

- [ ] 7. Update scripts and examples
  - Update all scripts in `scripts/` directory to use new imports
  - Update all examples in `examples/` directory to use new imports
  - Test script and example execution
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 7.1 Update script imports
  - Scan all scripts for imports that need updating
  - Update script imports to use new package structure
  - Test critical scripts to ensure they work correctly
  - _Requirements: 6.1, 6.4_

- [ ] 7.2 Update example imports
  - Update all example files to use new package imports
  - Update example documentation and README files
  - Test example execution to ensure they work correctly
  - _Requirements: 6.2, 6.3_

- [ ] 7.3 Create migration helper script
  - Create script to help users migrate their own code
  - Include common import transformation patterns
  - Provide validation and testing utilities
  - _Requirements: 7.2, 7.4_

- [ ] 8. Update configuration files
  - Update `pyproject.toml` with new package configuration
  - Update linting and type checking configuration
  - Update build system configuration
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 8.1 Update pyproject.toml package configuration
  - Verify CLI entry point configuration is correct
  - Update any package-specific configuration settings
  - Update linting tool configuration for new package structure
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 8.2 Update development tool configuration
  - Update mypy configuration for new package structure
  - Update ruff/black configuration if needed
  - Update any other development tool configurations
  - _Requirements: 5.4_

- [ ] 8.3 Test package installation and CLI entry point
  - Test package installation in clean environment
  - Test CLI entry point works correctly after installation
  - Verify public API is accessible after installation
  - _Requirements: 5.2, 5.5_

- [ ] 9. Update documentation
  - Update all documentation to use new import paths
  - Update API documentation and examples
  - Update installation and development setup instructions
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [ ] 9.1 Update code examples in documentation
  - Scan all documentation files for code examples
  - Update import statements in documentation examples
  - Update any module path references in documentation
  - _Requirements: 8.1, 8.2_

- [ ] 9.2 Update API documentation
  - Update API documentation to reflect new package structure
  - Update module references and import examples
  - Regenerate any auto-generated API documentation
  - _Requirements: 8.2, 8.3_

- [ ] 9.3 Update setup and installation documentation
  - Update installation instructions for new package structure
  - Update development setup instructions
  - Update troubleshooting guides with new module paths
  - _Requirements: 8.3, 8.4, 8.5_

- [ ] 9.4 Update README and main documentation
  - Update main README with new import examples
  - Update any configuration documentation
  - Update docstrings that reference module paths
  - _Requirements: 8.6, 8.7, 8.8_

- [ ] 10. Final cleanup and validation
  - Remove old duplicate files and empty directories
  - Run comprehensive validation of entire migration
  - Create migration summary and changelog
  - _Requirements: 1.5, 7.1, 7.3, 7.5_

- [ ] 10.1 Clean up old structure
  - Remove the old duplicate `src/pdfrebuilder/` directory
  - Clean up any remaining duplicate files
  - Remove empty directories and unused files
  - _Requirements: 1.5_

- [ ] 10.2 Run comprehensive final validation
  - Run full test suite one final time
  - Test CLI functionality comprehensively
  - Test package installation and import
  - Test all examples and critical scripts
  - _Requirements: 7.1, 7.3_

- [ ] 10.3 Create migration documentation
  - Document the migration process and changes made
  - Create changelog entry for the structural changes
  - Update version number to reflect breaking changes
  - Create migration guide for any external users
  - _Requirements: 7.2, 7.4, 7.5_