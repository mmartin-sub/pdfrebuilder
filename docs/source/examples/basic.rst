Basic Examples
==============

This section contains simple usage examples to get you started with the Multi-Format Document Engine.

Simple PDF Processing
---------------------

Extract and Rebuild
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine
   import json

   # Create engine instance
   engine = DocumentEngine()

   # Extract layout from PDF
   layout = engine.extract("input.pdf")

   # Save layout configuration
   with open("layout_config.json", "w") as f:
       json.dump(layout, f, indent=2)

   # Rebuild PDF from layout
   engine.rebuild(layout, "output.pdf")

   print("Document processed successfully!")

Command Line Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Extract layout
   hatch run python main.py --input document.pdf --mode extract

   # Generate PDF from layout
   hatch run python main.py --mode generate --config layout_config.json --output result.pdf

Basic Configuration
-------------------

Simple Override Example
~~~~~~~~~~~~~~~~~~~~~~~

Create a manual_overrides.json5 file for basic corrections:

.. code-block:: json5

   {
     // Use original as template for complex graphics
     "use_original_as_template": true,

     // Fix a specific text block
     "text_block_overrides": {
       "block_100_200": {
         "text": "Corrected Text",
         "font": "Arial-Regular"
       }
     }
   }

Font Management
~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.font.utils import download_essential_fonts, check_font_availability

   # Download common fonts
   download_essential_fonts()

   # Check what fonts are needed for a document
   missing_fonts = check_font_availability("document.pdf")
   if missing_fonts:
       print(f"Missing fonts: {missing_fonts}")

Working with Images
-------------------

Extract Images
~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()
   layout = engine.extract("document_with_images.pdf")

   # Images are automatically extracted to ./images/ directory
   print("Images extracted to ./images/")

   # Access image information
   for page in layout['document_structure']:
       for element in page['layers'][0]['content']:
           if element['type'] == 'image':
               print(f"Image: {element['image_file']}")
               print(f"Position: {element['bbox']}")

Modify Image Positions
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json5

   // manual_overrides.json5
   {
     "image_bboxes": {
       "image_1_abc123.jpeg": [100, 200, 400, 600]  // [x1, y1, x2, y2]
     }
   }

Text Processing
---------------

Handle Text Spacing
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine

   # Enable automatic text spacing normalization
   engine = DocumentEngine()
   layout = engine.extract("document.pdf", normalize_spacing=True)

   # Check for spacing issues
   for page in layout['document_structure']:
       for element in page['layers'][0]['content']:
           if element['type'] == 'text':
               if element.get('adjust_spacing'):
                   print(f"Normalized: '{element['raw_text']}' -> '{element['text']}'")

Custom Text Corrections
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json5

   // manual_overrides.json5
   {
     "text_block_overrides": {
       "block_150_300": {
         "text": "Manually corrected text",
         "font": "Times-Roman",
         "color": 0  // Black
       }
     }
   }

Quality Validation
------------------

Basic Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator

   validator = VisualValidator()

   # Compare original and reconstructed
   result = validator.compare_documents("original.pdf", "output.pdf")

   print(f"Similarity: {result.similarity:.1%}")

   if result.similarity > 0.9:
       print("✓ High quality reconstruction")
   else:
       print("⚠ Quality may need improvement")

Debug Mode
~~~~~~~~~~

.. code-block:: bash

   # Generate debug PDF showing layers
   hatch run python main.py --mode debug --config layout_config.json --debugoutput debug.pdf

Error Handling
--------------

Basic Error Handling
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine
   from pdfrebuilder.exceptions import ProcessingError

   engine = DocumentEngine()

   try:
       layout = engine.extract("document.pdf")
       engine.rebuild(layout, "output.pdf")
       print("Success!")

   except ProcessingError as e:
       print(f"Processing failed: {e}")
       # Try with template mode as fallback
       try:
           layout = engine.extract("document.pdf", use_template=True)
           engine.rebuild(layout, "output.pdf")
           print("Success with template mode!")
       except Exception as e:
           print(f"Failed completely: {e}")

File Organization
-----------------

Organize Output Files
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from pdfrebuilder.engine import DocumentEngine

   # Create organized directory structure
   os.makedirs("output/processed", exist_ok=True)
   os.makedirs("output/configs", exist_ok=True)
   os.makedirs("output/images", exist_ok=True)

   engine = DocumentEngine()

   # Process with organized output
   layout = engine.extract("input.pdf")

   # Save configuration
   import json
   with open("output/configs/layout.json", "w") as f:
       json.dump(layout, f, indent=2)

   # Generate output
   engine.rebuild(layout, "output/processed/result.pdf")

Batch Processing Simple
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()
   input_dir = "input/"
   output_dir = "output/"

   # Process all PDFs in directory
   for filename in os.listdir(input_dir):
       if filename.endswith('.pdf'):
           input_path = os.path.join(input_dir, filename)
           output_path = os.path.join(output_dir, f"processed_{filename}")

           try:
               layout = engine.extract(input_path)
               engine.rebuild(layout, output_path)
               print(f"✓ Processed: {filename}")
           except Exception as e:
               print(f"✗ Failed: {filename} - {e}")

Configuration Examples
----------------------

Basic Settings
~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine, ProcessingConfig

   config = ProcessingConfig(
       extract_images=True,
       normalize_text_spacing=True,
       preserve_fonts=True,
       output_quality="high"
   )

   engine = DocumentEngine(config=config)

Memory-Efficient Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine, PerformanceConfig

   config = PerformanceConfig(
       memory_optimization=True,
       max_memory_usage="1GB",
       process_pages_individually=True
   )

   engine = DocumentEngine(performance_config=config)

Integration Examples
--------------------

Simple Web Service
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask, request, send_file
   from pdfrebuilder.engine import DocumentEngine
   import tempfile
   import os

   app = Flask(__name__)
   engine = DocumentEngine()

   @app.route('/process', methods=['POST'])
   def process_pdf():
       if 'file' not in request.files:
           return 'No file uploaded', 400

       file = request.files['file']

       # Save uploaded file
       with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
           file.save(tmp_input.name)

           # Process document
           layout = engine.extract(tmp_input.name)

           # Generate output
           with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
               engine.rebuild(layout, tmp_output.name)

               # Clean up input
               os.unlink(tmp_input.name)

               return send_file(tmp_output.name, as_attachment=True,
                              download_name='processed.pdf')

   if __name__ == '__main__':
       app.run(debug=True)

Simple Automation Script
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   #!/usr/bin/env python3
   """
   Simple automation script for document processing
   """

   import sys
   import os
   from pdfrebuilder.engine import DocumentEngine

   def main():
       if len(sys.argv) != 3:
           print("Usage: python process.py <input.pdf> <output.pdf>")
           sys.exit(1)

       input_file = sys.argv[1]
       output_file = sys.argv[2]

       if not os.path.exists(input_file):
           print(f"Error: Input file '{input_file}' not found")
           sys.exit(1)

       engine = DocumentEngine()

       try:
           print(f"Processing {input_file}...")
           layout = engine.extract(input_file)
           engine.rebuild(layout, output_file)
           print(f"✓ Successfully created {output_file}")

       except Exception as e:
           print(f"✗ Error processing document: {e}")
           sys.exit(1)

   if __name__ == '__main__':
       main()
