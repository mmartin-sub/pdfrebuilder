Multi-Format Document Engine Documentation
==========================================

Welcome to the Multi-Format Document Engine documentation. This tool provides powerful capabilities for extracting, analyzing, and rebuilding document layouts with high fidelity across multiple formats including PDF and PSD.

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   guides/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/index

.. toctree::
   :maxdepth: 2
   :caption: Examples:

   examples/index

.. toctree::
   :maxdepth: 2
   :caption: Reference:

   reference/index

Quick Start
-----------

The Multi-Format Document Engine is a Python tool for deconstructing document layouts into human-readable JSON format and rebuilding visually similar documents from that data.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install with Hatch (recommended)
   pip install hatch
   hatch env create
   hatch shell

   # Or install directly
   pip install pdfrebuilder

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder import DocumentEngine

   # Extract layout from PDF
   engine = DocumentEngine()
   layout = engine.extract("input.pdf")

   # Rebuild document
   engine.rebuild(layout, "output.pdf")

Features
--------

* **Layout Extraction**: Extract text blocks, images, and vector graphics from documents
* **JSON Configuration**: Save layout information in structured format
* **Document Reconstruction**: Generate new documents from JSON with visual fidelity
* **Multi-Format Support**: Support for PDF and PSD formats
* **Template Mode**: Use original document as pixel-perfect background
* **Visual Debugging**: Multi-page debug output showing layers

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
