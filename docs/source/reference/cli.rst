CLI Reference
=============

This section provides a complete reference for the command-line interface of the Multi-Format Document Engine.

Main Commands
-------------

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Extract layout from PDF
   hatch run python main.py --input document.pdf --mode extract

   # Generate PDF from layout
   hatch run python main.py --mode generate --config layout_config.json --output result.pdf

   # Full pipeline (extract + generate)
   hatch run python main.py --input document.pdf --output result.pdf

Command Options
~~~~~~~~~~~~~~~

.. code-block:: bash

   python main.py [OPTIONS]

**Global Options:**

``--input PATH``
  Input document file path (required for extract and full modes)

``--output PATH``
  Output document file path (required for generate and full modes)

``--config PATH``
  Configuration file path (default: layout_config.json)

``--mode MODE``
  Processing mode: extract, generate, debug, or full (default: full)

``--overrides PATH``
  Manual overrides file path (default: manual_overrides.json5)

``--verbose, -v``
  Enable verbose output

``--quiet, -q``
  Suppress non-error output

``--debug``
  Enable debug mode with detailed logging

``--help, -h``
  Show help message and exit

``--version``
  Show version information

Processing Modes
----------------

Extract Mode
~~~~~~~~~~~~

Extract layout information from a document:

.. code-block:: bash

   python main.py --mode extract --input document.pdf [OPTIONS]

**Extract-specific options:**

``--extract-images / --no-extract-images``
  Enable/disable image extraction (default: enabled)

``--extract-text / --no-extract-text``
  Enable/disable text extraction (default: enabled)

``--extract-vectors / --no-extract-vectors``
  Enable/disable vector graphics extraction (default: enabled)

``--normalize-spacing / --no-normalize-spacing``
  Enable/disable text spacing normalization (default: enabled)

``--precision MODE``
  Text extraction precision: fast, balanced, precise (default: balanced)

``--image-quality QUALITY``
  Image extraction quality: low, medium, high, maximum (default: high)

**Examples:**

.. code-block:: bash

   # Basic extraction
   python main.py --mode extract --input document.pdf

   # High precision extraction
   python main.py --mode extract --input document.pdf --precision precise

   # Extract without images
   python main.py --mode extract --input document.pdf --no-extract-images

   # Custom config output
   python main.py --mode extract --input document.pdf --config custom_layout.json

Generate Mode
~~~~~~~~~~~~~

Generate a document from layout configuration:

.. code-block:: bash

   python main.py --mode generate --config layout.json --output result.pdf [OPTIONS]

**Generate-specific options:**

``--quality QUALITY``
  Output quality: draft, normal, high, maximum (default: high)

``--template / --no-template``
  Use original document as template (default: auto-detect)

``--compress LEVEL``
  Compression level: none, low, medium, high (default: medium)

``--embed-fonts MODE``
  Font embedding: none, subset, full (default: subset)

**Examples:**

.. code-block:: bash

   # Basic generation
   python main.py --mode generate --config layout.json --output result.pdf

   # Maximum quality output
   python main.py --mode generate --config layout.json --output result.pdf --quality maximum

   # Force template mode
   python main.py --mode generate --config layout.json --output result.pdf --template

   # No compression
   python main.py --mode generate --config layout.json --output result.pdf --compress none

Debug Mode
~~~~~~~~~~

Generate debug output with layer visualization:

.. code-block:: bash

   python main.py --mode debug --config layout.json --debugoutput debug.pdf [OPTIONS]

**Debug-specific options:**

``--debugoutput PATH``
  Debug output file path (required for debug mode)

``--show-layers / --no-show-layers``
  Show individual layers (default: enabled)

``--show-bboxes / --no-show-bboxes``
  Show element bounding boxes (default: enabled)

``--show-text / --no-show-text``
  Show text elements (default: enabled)

``--show-images / --no-show-images``
  Show image elements (default: enabled)

``--show-vectors / --no-show-vectors``
  Show vector elements (default: enabled)

``--color-code / --no-color-code``
  Use color coding for element types (default: enabled)

**Examples:**

.. code-block:: bash

   # Basic debug output
   python main.py --mode debug --config layout.json --debugoutput debug.pdf

   # Show only text elements
   python main.py --mode debug --config layout.json --debugoutput debug.pdf \
     --no-show-images --no-show-vectors

   # Debug with bounding boxes
   python main.py --mode debug --config layout.json --debugoutput debug.pdf \
     --show-bboxes

Full Mode
~~~~~~~~~

Complete pipeline from input to output:

.. code-block:: bash

   python main.py --input document.pdf --output result.pdf [OPTIONS]

Combines extract and generate modes with all their options.

**Examples:**

.. code-block:: bash

   # Basic full processing
   python main.py --input document.pdf --output result.pdf

   # High quality processing
   python main.py --input document.pdf --output result.pdf \
     --precision precise --quality maximum

   # Processing with custom overrides
   python main.py --input document.pdf --output result.pdf \
     --overrides custom_overrides.json5

Batch Processing
----------------

Batch Script
~~~~~~~~~~~~

Use the batch processing script for multiple files:

.. code-block:: bash

   python scripts/batch_process.py [OPTIONS]

**Batch options:**

``--input-dir PATH``
  Input directory containing PDF files (required)

``--output-dir PATH``
  Output directory for processed files (required)

``--pattern PATTERN``
  File pattern to match (default: *.pdf)

``--recursive / --no-recursive``
  Process subdirectories recursively (default: disabled)

``--workers COUNT``
  Number of parallel workers (default: 4)

``--timeout SECONDS``
  Timeout per file in seconds (default: 300)

``--continue-on-error / --stop-on-error``
  Continue processing after errors (default: continue)

``--quality-threshold FLOAT``
  Minimum quality threshold (0.0-1.0, default: 0.9)

``--move-failed / --no-move-failed``
  Move failed files to separate directory (default: enabled)

**Examples:**

.. code-block:: bash

   # Basic batch processing
   python scripts/batch_process.py --input-dir input/ --output-dir output/

   # Parallel processing with 8 workers
   python scripts/batch_process.py --input-dir input/ --output-dir output/ --workers 8

   # Recursive processing
   python scripts/batch_process.py --input-dir input/ --output-dir output/ --recursive

   # Custom quality threshold
   python scripts/batch_process.py --input-dir input/ --output-dir output/ \
     --quality-threshold 0.95

Validation Commands
-------------------

Validation Script
~~~~~~~~~~~~~~~~~

Validate processed documents:

.. code-block:: bash

   python scripts/validate_documents.py [OPTIONS]

**Validation options:**

``--original-dir PATH``
  Directory containing original documents (required)

``--processed-dir PATH``
  Directory containing processed documents (required)

``--threshold FLOAT``
  Similarity threshold (0.0-1.0, default: 0.9)

``--report-dir PATH``
  Directory for validation reports (default: validation_reports/)

``--format FORMAT``
  Report format: html, json, pdf (default: html)

``--parallel / --no-parallel``
  Enable parallel validation (default: enabled)

**Examples:**

.. code-block:: bash

   # Basic validation
   python scripts/validate_documents.py \
     --original-dir input/ --processed-dir output/

   # Strict validation with detailed reports
   python scripts/validate_documents.py \
     --original-dir input/ --processed-dir output/ \
     --threshold 0.95 --format pdf

   # Generate JSON reports
   python scripts/validate_documents.py \
     --original-dir input/ --processed-dir output/ \
     --format json --report-dir reports/

Font Management
---------------

Font Commands
~~~~~~~~~~~~~

Manage fonts for document processing:

.. code-block:: bash

   # Download essential fonts
   python scripts/download_fonts.py [OPTIONS]

**Font download options:**

``--font-dir PATH``
  Font installation directory (default: ./fonts/)

``--essential-only / --all-fonts``
  Download only essential fonts (default: essential only)

``--update / --no-update``
  Update existing fonts (default: no update)

**Examples:**

.. code-block:: bash

   # Download essential fonts
   python scripts/download_fonts.py

   # Download to custom directory
   python scripts/download_fonts.py --font-dir /usr/local/share/fonts/

   # Download all available fonts
   python scripts/download_fonts.py --all-fonts

Font Analysis
~~~~~~~~~~~~~

Analyze font usage in documents:

.. code-block:: bash

   python scripts/analyze_fonts.py --input document.pdf [OPTIONS]

**Font analysis options:**

``--input PATH``
  Input document to analyze (required)

``--output PATH``
  Output report file (default: font_analysis.json)

``--check-availability / --no-check-availability``
  Check font availability on system (default: enabled)

``--suggest-replacements / --no-suggest-replacements``
  Suggest font replacements (default: enabled)

**Examples:**

.. code-block:: bash

   # Analyze document fonts
   python scripts/analyze_fonts.py --input document.pdf

   # Generate detailed report
   python scripts/analyze_fonts.py --input document.pdf \
     --output detailed_font_report.json --suggest-replacements

Utility Commands
----------------

Configuration Tools
~~~~~~~~~~~~~~~~~~~

Generate configuration templates:

.. code-block:: bash

   # Generate default configuration
   python scripts/generate_config.py --type default --output config.toml

   # Generate batch configuration
   python scripts/generate_config.py --type batch --output batch_config.json

   # Generate override template
   python scripts/generate_config.py --type overrides --output overrides.json5

System Information
~~~~~~~~~~~~~~~~~~

Get system information for troubleshooting:

.. code-block:: bash

   python scripts/system_info.py [OPTIONS]

**System info options:**

``--output PATH``
  Output file for system information (default: stdout)

``--format FORMAT``
  Output format: text, json (default: text)

``--include-fonts / --no-include-fonts``
  Include font information (default: enabled)

**Examples:**

.. code-block:: bash

   # Display system information
   python scripts/system_info.py

   # Save to file
   python scripts/system_info.py --output system_info.txt

   # JSON format
   python scripts/system_info.py --format json --output system_info.json

Performance Testing
~~~~~~~~~~~~~~~~~~~

Run performance benchmarks:

.. code-block:: bash

   python scripts/benchmark.py [OPTIONS]

**Benchmark options:**

``--test-dir PATH``
  Directory containing test documents (default: test_documents/)

``--output PATH``
  Benchmark results file (default: benchmark_results.json)

``--iterations COUNT``
  Number of test iterations (default: 3)

``--memory-profile / --no-memory-profile``
  Include memory profiling (default: enabled)

**Examples:**

.. code-block:: bash

   # Run basic benchmark
   python scripts/benchmark.py

   # Detailed benchmark with memory profiling
   python scripts/benchmark.py --iterations 5 --memory-profile

   # Custom test documents
   python scripts/benchmark.py --test-dir my_test_docs/

Environment Variables
---------------------

CLI-Specific Variables
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Default input/output directories
   export PDFREBUILDER_INPUT_DIR="./input"
   export PDFREBUILDER_OUTPUT_DIR="./output"

   # Default configuration files
   export PDFREBUILDER_CONFIG_FILE="./config.toml"
   export PDFREBUILDER_OVERRIDES_FILE="./overrides.json5"

   # Processing defaults
   export PDFREBUILDER_DEFAULT_MODE="full"
   export PDFREBUILDER_DEFAULT_QUALITY="high"
   export PDFREBUILDER_DEFAULT_PRECISION="balanced"

   # Batch processing defaults
   export PDFREBUILDER_BATCH_WORKERS="4"
   export PDFREBUILDER_BATCH_TIMEOUT="300"

   # Debug settings
   export PDFREBUILDER_DEBUG="false"
   export PDFREBUILDER_VERBOSE="false"

Exit Codes
----------

The CLI uses the following exit codes:

- ``0``: Success
- ``1``: General error
- ``2``: Invalid arguments
- ``3``: File not found
- ``4``: Permission denied
- ``5``: Processing error
- ``6``: Validation failed
- ``7``: Quality threshold not met
- ``8``: Timeout exceeded
- ``9``: Out of memory
- ``10``: Configuration error

Examples by Use Case
--------------------

Document Conversion
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert PDF with high quality
   python main.py --input report.pdf --output report_processed.pdf \
     --quality maximum --precision precise

   # Convert with template mode for complex graphics
   python main.py --input complex_design.pdf --output design_processed.pdf \
     --template --quality maximum

Quality Assurance
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Process with validation
   python main.py --input document.pdf --output result.pdf --debug
   python scripts/validate_documents.py \
     --original-dir . --processed-dir . \
     --threshold 0.95

Batch Operations
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Process entire directory
   python scripts/batch_process.py \
     --input-dir documents/ \
     --output-dir processed/ \
     --workers 8 \
     --quality-threshold 0.9

Troubleshooting
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Debug processing issues
   python main.py --input problematic.pdf --mode debug \
     --debugoutput debug.pdf --verbose

   # Analyze system capabilities
   python scripts/system_info.py --include-fonts

   # Check font availability
   python scripts/analyze_fonts.py --input problematic.pdf
