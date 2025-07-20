# Implementation Plan

- [x] 1. Update default test environment to include all dev and test requirements
  - Modify [tool.hatch.envs.default] dependencies to include all packages from 'dev' optional group
  - Add all packages from 'test' optional group to default test environment
  - Add all packages from 'validation' optional group for complete test coverage
  - Add all packages from 'psd' optional group for complete test coverage
  - Ensure test environment has everything needed for development and testing
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_

- [x] 2. Verify and update optional dependency groups in pyproject.toml
  - Ensure 'psd' optional dependency group includes psd-tools>=1.10.9 and numpy>=1.24.0
  - Ensure 'validation' optional dependency group includes scikit-image>=0.25.2
  - Update 'all' optional dependency group to include all missing dependencies
  - Verify dependency versions match existing patterns in pyproject.toml
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3. Create comprehensive installation documentation with pip and uv examples
  - Create docs/OPTIONAL_DEPENDENCIES.md with detailed installation instructions
  - Include pip install examples: `pip install -e .[psd]`, `pip install -e .[validation]`, etc.
  - Include uv pip install examples: `uv pip install -e .[psd]`, `uv pip install -e .[all]`
  - Document hatch environment usage: `hatch env create`, `hatch shell`
  - Include troubleshooting section for common dependency issues
  - _Requirements: 5.4_

- [x] 4. Add pytest markers for optional dependency test categories
  - Add 'psd' marker for PSD-related tests in pyproject.toml pytest configuration
  - Add 'validation' marker for image validation tests
  - Add 'ocr' marker for OCR-related tests
  - Add 'optional_deps' marker for tests requiring any optional dependencies
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 5. Update test modules to use pytest.importorskip for optional dependencies
  - Update tests/test_engine_modules.py to use pytest.importorskip for psd_tools
  - Update tests/test_visual_validation.py to use pytest.importorskip for skimage
  - Update tests/test_psd_extraction.py to use pytest.importorskip appropriately
  - Add appropriate pytest markers to test classes requiring optional dependencies
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 6. Create test scripts for different dependency scenarios
  - Add test-core script for running tests without optional dependency markers
  - Add test-psd script for running PSD-specific tests only
  - Add test-validation script for running validation tests only
  - Update default test script to run all tests with full dependency environment
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 7. Update documentation references and cross-links
  - Update README.md to reference docs/OPTIONAL_DEPENDENCIES.md
  - Update docs/INSTALLATION.md to mention optional dependency groups
  - Add cross-references between installation docs and optional dependency docs
  - Include examples of both pip and uv installation commands
  - _Requirements: 5.4_

- [x] 8. Verify test discovery and execution works correctly
  - Test that `hatch run pytest --collect-only` completes without ImportError
  - Test that `pip install -e .` followed by pytest shows appropriate skips
  - Test that `uv pip install -e .[all]` allows all tests to run
  - Validate that test markers work correctly for selective test execution
  - _Requirements: 1.1, 1.2, 1.3, 2.4_