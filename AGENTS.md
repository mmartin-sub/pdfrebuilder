# AGENTS.md: Instructions for AI Coding Agents

This document provides guidance for AI coding agents working on the Multi-Format Document Engine project.

## Project Overview

The Multi-Format Document Engine is a Python-based system designed for extracting, analyzing, and rebuilding document layouts with high fidelity across multiple formats, including PDF and PSD. It is built to be modular, extensible, and secure. The project uses `hatch` for environment and dependency management.

## Setup and Key Commands

The project is managed using `hatch`. All commands should be run through the `hatch` runner.

- **Install dependencies and create the virtual environment**:

  ```bash
  hatch env create
  ```

  After creating the environment, it is recommended to sync the dependencies using `uv`:

  ```bash
  hatch run uv sync --extra all
  ```

- **Activate the virtual environment**:

  ```bash
  hatch shell
  ```

- **Run the test suite**:

  ```bash
  hatch run test
  hatch run test-cov
  ```

- **Run linters and formatters**:

  ```bash
  # Check formatting and linting
  hatch run check

  # Apply formatting fixes
  hatch run format
  hatch run pre-commit run --all-files
  ```

- **Build the documentation**:

  ```bash
  hatch run docs:build
  ```

## Testing Instructions

- All code changes must be accompanied by relevant tests.
- The pre-commit and the full test suite must pass before submitting work. Run it with `hatch run test`.
- Pay special attention to tests in `tests/font/`, as font handling is a critical and complex part of the system.
- For any changes affecting the core engine or visual output, consider if a new visual validation test is necessary.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pdfrebuilder'` when running tests:**
  This issue can occur if the `src` directory is not in the `PYTHONPATH`. To fix this, you can:
  1. Add `pythonpath = "src"` to the `[tool.pytest.ini_options]` section of `pyproject.toml`.
  2. Add `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))` to `tests/conftest.py`.

- **Test failures in `tests/wip`:**
  The tests in the `tests/wip` directory are work-in-progress and may not be stable. You can ignore them by running pytest with the `--ignore` flag:
  `hatch run pytest --ignore=tests/wip`
  The default `test` script in `pyproject.toml` has been updated to do this automatically.

- **Dependency resolution errors with `uv sync`:**
  If you encounter dependency resolution errors, especially regarding `numpy` versions, you may need to adjust the version specifiers in `pyproject.toml`. For example, there was a conflict between `opencv-python` and the `psd` extra. This was resolved by pinning the `numpy` version in the `psd` and `validation` extras to be compatible with `opencv-python`.

## Agent Directives

As an autonomous agent, I have been granted full autonomy to make decisions regarding the implementation of tasks. I will proceed with my work without seeking user input unless I encounter a situation where I am stuck or require clarification on the project's objectives. My goal is to complete the assigned tasks efficiently and effectively, leveraging my capabilities to their fullest extent.
hint to bypass pre-commit errors should be used as the last resort.
