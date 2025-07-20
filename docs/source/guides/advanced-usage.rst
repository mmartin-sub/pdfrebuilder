Advanced Usage
==============

This guide covers advanced features and customization options for the Multi-Format Document Engine.

Multi-Format Support
---------------------

PDF Processing
~~~~~~~~~~~~~~

The engine supports comprehensive PDF processing with multiple backends:

.. code-block:: python

   from pdfrebuilder.engine import PDFEngineSelector

   # Select optimal PDF engine
   selector = PDFEngineSelector()
   engine = selector.get_optimal_engine(
       document_path="input.pdf",
       requirements=["text_extraction", "image_processing"]
   )

PSD Processing
~~~~~~~~~~~~~~

For Adobe Photoshop files (requires psd-tools):

.. code-block:: python

   from pdfrebuilder.engine import PSDProcessor

   # Process PSD file
   processor = PSDProcessor()
   layout = processor.extract("design.psd")

Custom Configuration
--------------------

Manual Overrides
~~~~~~~~~~~~~~~~

Use manual_overrides.json5 for fine-tuning extraction results:

.. code-block:: json5

   {
     // Template mode for complex graphics
     "use_original_as_template": true,

     // Font corrections
     "text_fonts": {
       "Arial-Bold": "Arial-Bold.ttf",
       "CustomFont": "custom-font.ttf"
     },

     // Text block corrections
     "text_block_overrides": {
       "block_135_1409": {
         "font": "DancingScript-Regular",
         "color": 4209970,
         "text": "Corrected text content"
       }
     },

     // Image positioning
     "image_bboxes": {
       "image_1_fbc04c5c.jpeg": [270.0, 265.0, 965.0, 1308.0]
     }
   }

Engine Configuration
~~~~~~~~~~~~~~~~~~~~

Configure processing engines for optimal performance:

.. code-block:: python

   from pdfrebuilder.config import EngineConfig

   config = EngineConfig(
       pdf_engine="pymupdf",  # or "reportlab"
       image_quality="high",
       text_extraction_mode="precise",
       memory_optimization=True
   )

Visual Validation
-----------------

Quality Assurance
~~~~~~~~~~~~~~~~~

Validate document reconstruction quality:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator

   validator = VisualValidator()
   result = validator.compare_documents(
       original="input.pdf",
       reconstructed="output.pdf",
       threshold=0.95
   )

   if result.similarity < 0.9:
       print(f"Quality warning: {result.similarity:.2%} similarity")

Performance Optimization
-------------------------

Memory Management
~~~~~~~~~~~~~~~~~

For large documents, optimize memory usage:

.. code-block:: python

   from pdfrebuilder.engine import PerformanceConfig

   config = PerformanceConfig(
       chunk_size=1024*1024,  # 1MB chunks
       max_memory_usage="2GB",
       enable_caching=True,
       parallel_processing=True
   )

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple documents efficiently:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor

   processor = BatchProcessor(
       input_directory="input/",
       output_directory="output/",
       parallel_workers=4
   )

   results = processor.process_all()

Error Handling
--------------

Robust Error Management
~~~~~~~~~~~~~~~~~~~~~~~

Handle processing errors gracefully:

.. code-block:: python

   from pdfrebuilder.exceptions import ProcessingError, ValidationError

   try:
       layout = engine.extract("problematic.pdf")
   except ProcessingError as e:
       print(f"Processing failed: {e}")
       # Fallback to template mode
       layout = engine.extract("problematic.pdf", use_template=True)
   except ValidationError as e:
       print(f"Validation failed: {e}")
       # Continue with warnings

Integration Examples
--------------------

CI/CD Integration
~~~~~~~~~~~~~~~~~

Integrate with continuous integration:

.. code-block:: yaml

   # .github/workflows/document-processing.yml
   name: Document Processing
   on: [push]
   jobs:
     process:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Setup Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.11'
         - name: Install dependencies
           run: |
             pip install hatch
             hatch env create
         - name: Process documents
           run: hatch run python scripts/batch_process.py

API Integration
~~~~~~~~~~~~~~~

Use as a library in larger applications:

.. code-block:: python

   from pdfrebuilder import DocumentEngine
   from flask import Flask, request, send_file

   app = Flask(__name__)
   engine = DocumentEngine()

   @app.route('/process', methods=['POST'])
   def process_document():
       file = request.files['document']
       layout = engine.extract(file)
       output = engine.rebuild(layout)
       return send_file(output, as_attachment=True)
