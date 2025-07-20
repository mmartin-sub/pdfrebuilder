# Implementation Plan

- [x] 1. Audit and consolidate hardcoded paths in test files
  - [x] 1.1 Update `tests/config.py` sample path resolution
    - Change `get_sample_input_path()` to use `tests/sample/` instead of `input/`
    - Update function to return `os.path.join("tests", "sample", filename)`
    - _Requirements: 1.1, 1.2_

  - [x] 1.2 Fix hardcoded paths in `tests/test_pdf_extraction.py`
    - Replace `"input/sample/sample.pdf"` with `get_sample_input_path("sample.pdf")`
    - Replace `"output/debug"` with `get_config_value("test_output_dir")`
    - Add proper imports from `tests.config`
    - _Requirements: 1.3, 3.2_

  - [x] 1.3 Fix hardcoded paths in `tests/test_psd_extraction.py`
    - Replace `"input/sample/sample1.psd"` with `get_sample_input_path("sample1.psd")`
    - Replace `"output/debug"` with `get_config_value("test_output_dir")`
    - Add proper imports from `tests.config`
    - _Requirements: 1.3, 3.2_

  - [x] 1.4 Fix hardcoded paths in `tests/test_e2e_pdf_pipeline.py`
    - Replace `INPUT_DIR = os.path.join("input", "sample")` with sample path from config
    - Replace `OUTPUT_DIR = "output"` with `get_config_value("test_output_dir")`
    - Update `PDF_FILES` to use configurable sample directory
    - _Requirements: 1.3, 3.2_

- [x] 2. Consolidate output directory usage
  - [x] 2.1 Fix hardcoded output paths in `tests/test_fitz_return_value.py`
    - Replace `OUTPUT_DIR = "output"` with `get_config_value("test_output_dir")`
    - Replace `FONT_DIR = "downloaded_fonts"` with `get_config_value("downloaded_fonts_dir")`
    - Add imports from `src.settings`
    - _Requirements: 2.1, 3.1_

  - [x] 2.2 Fix hardcoded paths in `tests/test_both_null_edge_case.py`
    - Replace hardcoded `OUTPUT_DIR` with `get_config_value("test_output_dir")`
    - Use proper path resolution from settings
    - _Requirements: 2.1, 3.1_

  - [x] 2.3 Fix hardcoded paths in `tests/test_visual_validation.py`
    - Replace `TEST_IMAGE_DIR = "tests/temp_test_images"` with config-based path
    - Use `get_config_value("test_temp_dir")` for temporary test files
    - _Requirements: 2.1, 3.1_

  - [x] 2.4 Fix hardcoded paths in `tests/test_e2e_pdf_regeneration.py`
    - Replace `TEST_OUTPUT_DIR = "tests/temp_e2e_output"` with config-based path
    - Use existing test configuration infrastructure
    - _Requirements: 2.1, 3.1_

- [x] 3. Validate all path references use configuration
  - Search all test files for remaining hardcoded strings like `"output"`, `"input"`, `"tests/"`
  - Ensure all directory references go through `get_config_value()` or `tests.config` functions
  - Remove any remaining hardcoded path constants
  - _Requirements: 3.1, 3.2, 3.3_
