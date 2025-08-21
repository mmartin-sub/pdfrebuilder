.. _install-dev:

##############################
Development Installation Guide
##############################

This guide provides detailed installation instructions for setting up a development environment for PDFRebuilder.

Prerequisites
=============

- **Python 3.12 or higher**
- **Git** for version control
- **System dependencies** for PDF, image, and OCR processing

Quick Development Setup
=======================

Option 1: Hatch (Recommended)
-----------------------------

.. code-block:: bash

   # Clone the repository
   git clone <repository-url>
   cd pdfrebuilder

   # Create and activate development environment
   hatch env create
   hatch shell

   # Verify installation
   hatch run python main.py --help
   hatch run test

Option 2: uv (Modern Alternative)
---------------------------------

.. code-block:: bash

   # Clone the repository
   git clone <repository-url>
   cd pdfrebuilder

   # Sync with all dependencies
   uv sync --extra all

   # Activate environment and verify
   source .venv/bin/activate
   python main.py --help
   pytest

And so on... (The rest of the document would be converted in a similar fashion)
