Getting Started
===============

This guide will help you get started with the Multi-Format Document Engine.

Installation
------------

The Multi-Format Document Engine requires Python 3.11 or higher.

Using Hatch (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install Hatch
   pip install hatch

   # Create and activate environment
   hatch env create
   hatch shell

Direct Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install pdfrebuilder

Basic Usage
-----------

Extracting Document Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder import DocumentEngine

   # Create engine instance
   engine = DocumentEngine()

   # Extract layout from PDF
   layout = engine.extract("input.pdf")

   # Save layout configuration
   with open("layout_config.json", "w") as f:
       json.dump(layout, f, indent=2)

Rebuilding Documents
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from pdfrebuilder import DocumentEngine

   # Load layout configuration
   with open("layout_config.json", "r") as f:
       layout = json.load(f)

   # Create engine instance
   engine = DocumentEngine()

   # Rebuild document
   engine.rebuild(layout, "output.pdf")

Command Line Usage
------------------

Extract Layout
~~~~~~~~~~~~~~

.. code-block:: bash

   # Extract layout from PDF
   hatch run python main.py --input input.pdf --mode extract

   # Extract with custom configuration
   hatch run python main.py --input input.pdf --mode extract --config custom_layout.json

Generate Document
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate PDF from layout
   hatch run python main.py --mode generate --config layout_config.json --output result.pdf

   # Generate with debug output
   hatch run python main.py --mode debug --config layout_config.json --debugoutput debug.pdf

Next Steps
----------

- Read the :doc:`advanced-usage` guide for more complex scenarios
- Explore :doc:`batch-processing` for handling multiple documents
- Learn about :doc:`visual-validation` for quality assurance
