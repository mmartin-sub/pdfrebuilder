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

- **Activate the virtual environment**:

  ```bash
  hatch shell
  ```

- **Run the test suite**:

  ```bash
  hatch run test
  ```

- **Run linters and formatters**:

  ```bash
  # Check formatting and linting
  hatch run check

  # Apply formatting fixes
  hatch run format
  ```

- **Build the documentation**:

  ```bash
  hatch run docs:build
  ```

## Testing Instructions

- All code changes must be accompanied by relevant tests.
- The full test suite must pass before submitting work. Run it with `hatch run test`.
- Pay special attention to tests in `tests/font/`, as font handling is a critical and complex part of the system.
- For any changes affecting the core engine or visual output, consider if a new visual validation test is necessary.

## Agent Directives

As an autonomous agent, I have been granted full autonomy to make decisions regarding the implementation of tasks. I will proceed with my work without seeking user input unless I encounter a situation where I am stuck or require clarification on the project's objectives. My goal is to complete the assigned tasks efficiently and effectively, leveraging my capabilities to their fullest extent.
