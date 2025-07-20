Error Codes
===========

This section provides a comprehensive reference for error codes and troubleshooting information.

Exit Codes
----------

Command Line Exit Codes
~~~~~~~~~~~~~~~~~~~~~~~~

The CLI returns the following exit codes:

.. list-table::
   :header-rows: 1
   :widths: 10 20 70

   * - Code
     - Name
     - Description
   * - 0
     - SUCCESS
     - Operation completed successfully
   * - 1
     - GENERAL_ERROR
     - General error or unspecified failure
   * - 2
     - INVALID_ARGUMENTS
     - Invalid command line arguments
   * - 3
     - FILE_NOT_FOUND
     - Input file or configuration file not found
   * - 4
     - PERMISSION_DENIED
     - Insufficient permissions to read/write files
   * - 5
     - PROCESSING_ERROR
     - Error during document processing
   * - 6
     - VALIDATION_FAILED
     - Document validation failed
   * - 7
     - QUALITY_THRESHOLD_NOT_MET
     - Output quality below specified threshold
   * - 8
     - TIMEOUT_EXCEEDED
     - Processing timeout exceeded
   * - 9
     - OUT_OF_MEMORY
     - Insufficient memory for processing
   * - 10
     - CONFIGURATION_ERROR
     - Invalid configuration or settings

Exception Classes
-----------------

Core Exceptions
~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.exceptions import (
       PDFRebuilderError,
       ProcessingError,
       ValidationError,
       ConfigurationError,
       FontError,
       EngineError
   )

**PDFRebuilderError**
  Base exception class for all PDFRebuilder errors

**ProcessingError**
  Raised when document processing fails

**ValidationError**
  Raised when document validation fails

**ConfigurationError**
  Raised when configuration is invalid

**FontError**
  Raised when font-related operations fail

**EngineError**
  Raised when engine operations fail

Processing Errors
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Error Code
     - Exception
     - Description
   * - PE001
     - ExtractionError
     - Failed to extract content from document
   * - PE002
     - RenderingError
     - Failed to render document from layout
   * - PE003
     - CorruptedDocumentError
     - Input document is corrupted or invalid
   * - PE004
     - UnsupportedFormatError
     - Document format not supported
   * - PE005
     - MemoryError
     - Insufficient memory for processing
   * - PE006
     - TimeoutError
     - Processing timeout exceeded
   * - PE007
     - DependencyError
     - Required dependency not available

Font Errors
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Error Code
     - Exception
     - Description
   * - FE001
     - FontNotFoundError
     - Required font not found on system
   * - FE002
     - FontLoadError
     - Failed to load font file
   * - FE003
     - FontEncodingError
     - Font encoding not supported
   * - FE004
     - FontEmbeddingError
     - Failed to embed font in output
   * - FE005
     - FontSubstitutionError
     - Font substitution failed
   * - FE006
     - FontMetricsError
     - Invalid font metrics

Validation Errors
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Error Code
     - Exception
     - Description
   * - VE001
     - SimilarityError
     - Document similarity below threshold
   * - VE002
     - TextAccuracyError
     - Text accuracy below threshold
   * - VE003
     - LayoutError
     - Layout accuracy below threshold
   * - VE004
     - ColorAccuracyError
     - Color accuracy below threshold
   * - VE005
     - StructureError
     - Document structure mismatch
   * - VE006
     - ContentMissingError
     - Expected content missing from output

Configuration Errors
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Error Code
     - Exception
     - Description
   * - CE001
     - InvalidConfigError
     - Configuration file is invalid
   * - CE002
     - MissingConfigError
     - Required configuration missing
   * - CE003
     - ConfigParseError
     - Failed to parse configuration file
   * - CE004
     - OverrideError
     - Invalid manual override
   * - CE005
     - SettingsError
     - Invalid settings value
   * - CE006
     - PathError
     - Invalid file or directory path

Engine Errors
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Error Code
     - Exception
     - Description
   * - EE001
     - EngineNotFoundError
     - Requested engine not available
   * - EE002
     - EngineInitError
     - Failed to initialize engine
   * - EE003
     - EngineCompatibilityError
     - Engine not compatible with document
   * - EE004
     - EngineFeatureError
     - Required feature not supported by engine
   * - EE005
     - EngineVersionError
     - Engine version incompatible
   * - EE006
     - EngineConfigError
     - Invalid engine configuration

Common Error Scenarios
----------------------

File Access Issues
~~~~~~~~~~~~~~~~~~

**Error**: ``FileNotFoundError: [Errno 2] No such file or directory: 'input.pdf'``

**Cause**: Input file does not exist or path is incorrect

**Solution**:

.. code-block:: bash

   # Check file exists
   ls -la input.pdf

   # Use absolute path
   python main.py --input /full/path/to/input.pdf --output output.pdf

**Error**: ``PermissionError: [Errno 13] Permission denied: 'output.pdf'``

**Cause**: Insufficient permissions to write output file

**Solution**:

.. code-block:: bash

   # Check directory permissions
   ls -la output/

   # Fix permissions
   chmod 755 output/

   # Use different output directory
   python main.py --input input.pdf --output /tmp/output.pdf

Memory Issues
~~~~~~~~~~~~~

**Error**: ``MemoryError: Unable to allocate memory for processing``

**Cause**: Document too large for available memory

**Solution**:

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine, PerformanceConfig

   # Enable memory optimization
   config = PerformanceConfig(
       memory_optimization=True,
       max_memory_usage="1GB",
       chunk_processing=True
   )

   engine = DocumentEngine(performance_config=config)

**Error**: ``ProcessingError: Out of memory during image extraction``

**Cause**: Large images consuming too much memory

**Solution**:

.. code-block:: python

   from pdfrebuilder.engine import ProcessingConfig

   config = ProcessingConfig(
       image_quality="medium",  # Reduce from "high"
       min_image_size=(50, 50)  # Skip small images
   )

Font Problems
~~~~~~~~~~~~~

**Error**: ``FontNotFoundError: Font 'CustomFont-Regular' not found``

**Cause**: Required font not installed on system

**Solution**:

.. code-block:: bash

   # Download essential fonts
   python scripts/download_fonts.py

   # Or use font substitution
   # In manual_overrides.json5:
   {
     "text_fonts": {
       "CustomFont-Regular": "Arial-Regular.ttf"
     }
   }

**Error**: ``FontEncodingError: Unsupported font encoding``

**Cause**: Font uses unsupported encoding

**Solution**:

.. code-block:: json5

   // manual_overrides.json5
   {
     "text_block_overrides": {
       "problematic_block": {
         "font": "Arial-Regular",
         "text": "Manually corrected text"
       }
     }
   }

Processing Failures
~~~~~~~~~~~~~~~~~~~

**Error**: ``ProcessingError: Failed to extract text from page 3``

**Cause**: Complex or corrupted page content

**Solution**:

.. code-block:: python

   # Enable template mode
   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()
   layout = engine.extract("input.pdf", use_template=True)

**Error**: ``RenderingError: Failed to render vector graphics``

**Cause**: Complex vector graphics not supported

**Solution**:

.. code-block:: json5

   // manual_overrides.json5
   {
     "use_original_as_template": true,
     "processing_hints": {
       "complex_graphics_pages": [2, 3, 5]  // Use template for these pages
     }
   }

Validation Issues
~~~~~~~~~~~~~~~~~

**Error**: ``ValidationError: Document similarity 0.75 below threshold 0.9``

**Cause**: Output quality below acceptable threshold

**Solution**:

.. code-block:: python

   # Lower threshold or improve processing
   from pdfrebuilder.engine import ValidationConfig

   config = ValidationConfig(
       similarity_threshold=0.8,  # Lower threshold
       ignore_minor_differences=True
   )

   # Or use higher quality processing
   from pdfrebuilder.engine import ProcessingConfig

   processing_config = ProcessingConfig(
       text_extraction_mode="precise",
       image_quality="maximum",
       use_template_fallback=True
   )

Debugging Techniques
--------------------

Enable Debug Logging
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   # Enable debug logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine(debug=True)

Generate Debug Output
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate debug visualization
   python main.py --mode debug --config layout.json --debugoutput debug.pdf

Use Exception Handling
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine
   from pdfrebuilder.exceptions import ProcessingError, FontError

   engine = DocumentEngine()

   try:
       layout = engine.extract("input.pdf")
       engine.rebuild(layout, "output.pdf")

   except FontError as e:
       print(f"Font issue: {e}")
       # Try with font substitution

   except ProcessingError as e:
       print(f"Processing failed: {e}")
       # Try with template mode
       layout = engine.extract("input.pdf", use_template=True)
       engine.rebuild(layout, "output.pdf")

   except Exception as e:
       print(f"Unexpected error: {e}")
       # Log full traceback for debugging
       import traceback
       traceback.print_exc()

Error Recovery Strategies
-------------------------

Automatic Fallbacks
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine, ProcessingConfig
   from pdfrebuilder.exceptions import ProcessingError

   def robust_processing(input_path, output_path):
       strategies = [
           # Strategy 1: High precision
           ProcessingConfig(
               text_extraction_mode="precise",
               image_quality="high"
           ),
           # Strategy 2: Balanced with template fallback
           ProcessingConfig(
               text_extraction_mode="balanced",
               use_template_fallback=True
           ),
           # Strategy 3: Template mode only
           ProcessingConfig(
               use_template_mode=True
           )
       ]

       for i, config in enumerate(strategies):
           try:
               engine = DocumentEngine(config=config)
               layout = engine.extract(input_path)
               engine.rebuild(layout, output_path)
               print(f"Success with strategy {i+1}")
               return True

           except ProcessingError as e:
               print(f"Strategy {i+1} failed: {e}")
               continue

       print("All strategies failed")
       return False

Partial Processing
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def process_pages_individually(input_path, output_path):
       from pdfrebuilder.engine import DocumentEngine

       engine = DocumentEngine()

       try:
           # Try processing all pages
           layout = engine.extract(input_path)
           engine.rebuild(layout, output_path)

       except ProcessingError:
           # Fall back to page-by-page processing
           page_count = engine.get_page_count(input_path)
           successful_pages = []

           for page_num in range(page_count):
               try:
                   page_layout = engine.extract_page(input_path, page_num)
                   successful_pages.append(page_layout)

               except ProcessingError as e:
                   print(f"Failed to process page {page_num}: {e}")
                   # Use template for failed page
                   page_layout = engine.extract_page(input_path, page_num, use_template=True)
                   successful_pages.append(page_layout)

           # Combine successful pages
           combined_layout = engine.combine_pages(successful_pages)
           engine.rebuild(combined_layout, output_path)

Getting Help
------------

Collecting Diagnostic Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.utils import collect_diagnostic_info

   # Collect system and error information
   diagnostic_info = collect_diagnostic_info(
       input_file="problematic.pdf",
       error_log="error.log",
       include_system_info=True,
       include_font_info=True
   )

   # Save diagnostic report
   with open("diagnostic_report.json", "w") as f:
       json.dump(diagnostic_info, f, indent=2)

Reporting Issues
~~~~~~~~~~~~~~~~

When reporting issues, include:

1. **Error message and stack trace**
2. **Input document characteristics** (size, complexity, format)
3. **System information** (OS, Python version, dependencies)
4. **Configuration used** (settings, overrides)
5. **Diagnostic report** (if available)

**Example issue report:**

.. code-block:: text

   Error: ProcessingError: Failed to extract text from page 2

   System: Ubuntu 20.04, Python 3.11.2
   PDFRebuilder version: 1.0.0
   Input: 15-page PDF, 5.2MB, contains complex tables

   Configuration:
   - text_extraction_mode: precise
   - image_quality: high
   - use_template_fallback: true

   Stack trace:
   [Include full stack trace here]

   Diagnostic report attached: diagnostic_report.json
