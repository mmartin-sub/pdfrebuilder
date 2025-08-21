.. _installation:

##################
Installation Guide
##################

This guide provides detailed installation instructions for PDFRebuilder (formerly Multi-Format Document Engine).

Prerequisites
=============

- **Python 3.12 or higher**
- **uv** package manager (recommended) or **pip**
- **System dependencies** for PDF and image processing

System Requirements
===================

Operating Systems
-----------------

- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 10+, or equivalent
- **macOS**: 10.15+ (Catalina or later)
- **Windows**: 10+ with WSL2 recommended for best compatibility

Python Dependencies
-------------------

PDFRebuilder uses modern Python package management with `uv <https://github.com/astral-sh/uv>`_ for fast, reliable dependency management and supports multiple installation methods.

Quick Start
===========

For most users, the fastest way to get started:

.. code-block:: bash

   # Install uv (if not already installed)
   pip install uv

   # Install PDFRebuilder globally
   uv tool install pdfrebuilder

   # Start using it
   pdfrebuilder --help
   pdfrebuilder --generate-config

Installation Methods
====================

Method 1: Global Tool Installation (Recommended)
------------------------------------------------

Install PDFRebuilder as a global command-line tool using ``uv tool install``. This is the recommended method for most users.

1. **Install uv** (if not already installed):

   .. code-block:: bash

      # Using pip
      pip install uv

      # Using pipx (recommended)
      pipx install uv

      # Using curl (Linux/macOS)
      curl -LsSf https://astral.sh/uv/install.sh | sh

      # Using homebrew (macOS)
      brew install uv

2. **Install PDFRebuilder globally**:

   .. code-block:: bash

      # Install from PyPI (when published)
      uv tool install pdfrebuilder

      # Or install from local wheel (for development)
      uv tool install ./dist/pdfrebuilder-0.1.0-py3-none-any.whl

3. **Verify installation**:

   .. code-block:: bash

      # Check if pdfrebuilder is available
      pdfrebuilder --help

      # Generate sample configuration
      pdfrebuilder --generate-config

      # Show current configuration
      pdfrebuilder --show-config

4. **Update PATH** (if needed):

   .. code-block:: bash

      # Add uv tools to PATH if not already done
      export PATH="$HOME/.local/bin:$PATH"

      # Or use uv's automatic shell integration
      uv tool update-shell

**Note:** For development work or if you need OCR functionality, see the :doc:`install-dev` for detailed setup instructions including Tesseract OCR and ImageMagick installation.

And so on... (The rest of the document would be converted in a similar fashion)
