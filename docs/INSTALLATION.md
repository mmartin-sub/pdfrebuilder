# Installation

This document provides instructions for setting up the `pdfrebuilder` project for development and use.

## Prerequisites

- Python 3.10 or higher
- `hatch` for environment and project management
- `uv` for fast dependency installation (used by hatch)

## Development Setup

The recommended way to set up a development environment is to use `hatch`.

1. **Clone the repository:**

    ```bash
    git clone https://github.com/mmartin-sub/pdfrebuilder.git
    cd pdfrebuilder
    ```

2. **Create the virtual environment and install dependencies:**
    `hatch` will automatically create a virtual environment and install all the necessary dependencies, including optional ones for testing and development.

    ```bash
    hatch env create
    ```

    This command uses `uv` to sync all dependencies specified in `pyproject.toml` under the `all` extra.

3. **Activate the virtual environment:**
    To activate the shell with the virtual environment, run:

    ```bash
    hatch shell
    ```

    You should now have all the dependencies installed and be ready to run the tests or the application.

## Running Tests

To run the test suite, make sure you are inside the `hatch` shell and run:

```bash
pytest
```

Alternatively, you can use the `test` script defined in `pyproject.toml`:

```bash
hatch run test
```

## Basic Usage

To use the `pdfrebuilder` command-line tool, you can run it through `hatch`:

```bash
hatch run pdfrebuilder --help
```

This will show you the available commands and options.
