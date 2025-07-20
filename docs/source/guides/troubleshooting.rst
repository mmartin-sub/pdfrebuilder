Troubleshooting
===============

This guide helps you resolve common issues when using the Multi-Format Document Engine.

Installation Issues
-------------------

Dependency Problems
~~~~~~~~~~~~~~~~~~~

**Problem**: Missing dependencies or version conflicts

**Solution**:

.. code-block:: bash

   # Clean environment and reinstall
   hatch env remove docs
   hatch env create
   hatch shell

   # Or install specific dependencies
   pip install PyMuPDF>=1.26 reportlab>=4.0.0

**Problem**: FontTools installation fails

**Solution**:

.. code-block:: bash

   # Install with specific extras
   pip install "fonttools[ufo,lxml,woff,unicode]>=4.47.0"

Python Version Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem**: Unsupported Python version

**Solution**: Ensure you're using Python 3.11 or higher:

.. code-block:: bash

   python --version
   # Should show Python 3.11.x or higher

Processing Issues
-----------------

PDF Extraction Problems
~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Text extraction produces garbled output

**Symptoms**:
- Incorrect character encoding
- Missing or wrong characters
- Spacing issues

**Solutions**:

1. Check font availability:

.. code-block:: python

   from pdfrebuilder.font_utils import check_font_availability

   missing_fonts = check_font_availability("input.pdf")
   if missing_fonts:
       print(f"Missing fonts: {missing_fonts}")

2. Use manual overrides:

.. code-block:: json5

   // manual_overrides.json5
   {
     "text_block_overrides": {
       "block_135_1409": {
         "text": "Corrected text content",
         "font": "Arial-Regular"
       }
     }
   }

3. Enable template mode:

.. code-block:: json5

   {
     "use_original_as_template": true
   }

**Problem**: Images not extracted properly

**Solutions**:

1. Check image format support:

.. code-block:: python

   from pdfrebuilder.engine import ImageExtractor

   extractor = ImageExtractor()
   supported_formats = extractor.get_supported_formats()
   print(f"Supported formats: {supported_formats}")

2. Adjust image extraction settings:

.. code-block:: python

   from pdfrebuilder.engine import ExtractionConfig

   config = ExtractionConfig(
       min_image_size=(50, 50),
       image_quality="high",
       extract_vector_graphics=True
   )

Memory Issues
~~~~~~~~~~~~~

**Problem**: Out of memory errors during processing

**Symptoms**:
- Process killed unexpectedly
- "MemoryError" exceptions
- System becomes unresponsive

**Solutions**:

1. Enable memory optimization:

.. code-block:: python

   from pdfrebuilder.engine import PerformanceConfig

   config = PerformanceConfig(
       memory_optimization=True,
       max_memory_usage="2GB",
       chunk_processing=True
   )

2. Process pages individually:

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()

   # Process one page at a time
   for page_num in range(engine.get_page_count("large_document.pdf")):
       page_layout = engine.extract_page("large_document.pdf", page_num)
       # Process page_layout...

3. Use batch processing with limits:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor

   processor = BatchProcessor(
       max_concurrent_files=1,
       memory_cleanup_interval=5
   )

Font Issues
-----------

Missing Fonts
~~~~~~~~~~~~~

**Problem**: Fonts not found or incorrectly substituted

**Solutions**:

1. Install missing fonts:

.. code-block:: bash

   # Download essential fonts
   hatch run python scripts/download_essential_fonts.py

2. Configure font paths:

.. code-block:: python

   from pdfrebuilder.font_utils import add_font_directory

   add_font_directory("/path/to/custom/fonts")

3. Use font mapping:

.. code-block:: json5

   // manual_overrides.json5
   {
     "text_fonts": {
       "MissingFont-Regular": "Arial-Regular.ttf",
       "CustomFont-Bold": "Arial-Bold.ttf"
     }
   }

Font Rendering Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem**: Text appears with wrong styling or size

**Solutions**:

1. Check font metrics:

.. code-block:: python

   from pdfrebuilder.font_utils import analyze_font_metrics

   metrics = analyze_font_metrics("problematic.pdf")
   print(f"Font issues: {metrics.issues}")

2. Adjust font scaling:

.. code-block:: json5

   {
     "text_block_overrides": {
       "block_123_456": {
         "font_size_multiplier": 1.2,
         "line_height_multiplier": 1.1
       }
     }
   }

Performance Issues
------------------

Slow Processing
~~~~~~~~~~~~~~~

**Problem**: Document processing takes too long

**Solutions**:

1. Enable parallel processing:

.. code-block:: python

   from pdfrebuilder.engine import BatchProcessor

   processor = BatchProcessor(
       parallel_workers=4,
       enable_gpu_acceleration=True  # if available
   )

2. Optimize extraction settings:

.. code-block:: python

   from pdfrebuilder.engine import ExtractionConfig

   config = ExtractionConfig(
       text_extraction_mode="fast",  # vs "precise"
       skip_complex_graphics=True,
       image_downsampling=True
   )

3. Use caching:

.. code-block:: python

   from pdfrebuilder.engine import CacheConfig

   config = CacheConfig(
       enable_font_cache=True,
       enable_image_cache=True,
       cache_directory="/tmp/pdfrebuilder_cache"
   )

Quality Issues
--------------

Low Similarity Scores
~~~~~~~~~~~~~~~~~~~~~

**Problem**: Visual validation shows low similarity

**Solutions**:

1. Analyze validation results:

.. code-block:: python

   from pdfrebuilder.engine import VisualValidator

   validator = VisualValidator()
   result = validator.compare_documents("original.pdf", "output.pdf")

   print(f"Overall similarity: {result.similarity:.2%}")
   print(f"Text accuracy: {result.text_accuracy:.2%}")
   print(f"Layout accuracy: {result.layout_accuracy:.2%}")

   # Identify specific issues
   for issue in result.quality_issues:
       print(f"Issue: {issue.type} - {issue.description}")

2. Enable template mode for complex documents:

.. code-block:: json5

   {
     "use_original_as_template": true,
     "template_quality": "high"
   }

3. Fine-tune extraction parameters:

.. code-block:: python

   from pdfrebuilder.engine import QualityConfig

   config = QualityConfig(
       text_precision_mode=True,
       preserve_exact_positioning=True,
       maintain_color_accuracy=True
   )

Error Messages
--------------

Common Error Messages
~~~~~~~~~~~~~~~~~~~~~

**Error**: ``ModuleNotFoundError: No module named 'fitz'``

**Solution**:

.. code-block:: bash

   pip install PyMuPDF>=1.26

**Error**: ``ImportError: cannot import name 'normalize_text_spacing'``

**Solution**: This indicates a module structure issue. Ensure you're using the correct import paths:

.. code-block:: python

   # Correct import
   from pdfrebuilder.tools.generic import normalize_text_spacing

**Error**: ``FileNotFoundError: [Errno 2] No such file or directory: 'layout_config.json'``

**Solution**: Ensure the configuration file exists or create it:

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()
   layout = engine.extract("input.pdf")

   # Save configuration
   import json
   with open("layout_config.json", "w") as f:
       json.dump(layout, f, indent=2)

**Error**: ``ValidationError: Document similarity below threshold``

**Solution**: Adjust validation thresholds or improve processing:

.. code-block:: python

   from pdfrebuilder.engine import ValidationConfig

   config = ValidationConfig(
       similarity_threshold=0.85,  # Lower threshold
       ignore_minor_differences=True
   )

Debugging Techniques
--------------------

Enable Debug Mode
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine(debug=True)

Generate Debug Output
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate debug PDF with layer visualization
   hatch run python main.py --mode debug --config layout.json --debugoutput debug_layers.pdf

Inspect Intermediate Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()

   # Extract with intermediate results
   result = engine.extract("input.pdf", save_intermediates=True)

   # Inspect extracted elements
   for page in result.pages:
       print(f"Page {page.number}: {len(page.elements)} elements")
       for element in page.elements:
           print(f"  {element.type}: {element.bbox}")

Getting Help
------------

Log Collection
~~~~~~~~~~~~~~

When reporting issues, collect relevant logs:

.. code-block:: python

   import logging
   from pdfrebuilder.engine import DocumentEngine

   # Configure detailed logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('pdfrebuilder_debug.log'),
           logging.StreamHandler()
       ]
   )

   # Run your problematic code
   engine = DocumentEngine()
   # ... your code here

System Information
~~~~~~~~~~~~~~~~~~

Collect system information for bug reports:

.. code-block:: python

   from pdfrebuilder.utils import get_system_info

   info = get_system_info()
   print(f"Python version: {info.python_version}")
   print(f"Platform: {info.platform}")
   print(f"Available memory: {info.memory_gb}GB")
   print(f"PDFRebuilder version: {info.pdfrebuilder_version}")
   print(f"Dependencies: {info.dependencies}")

Performance Profiling
~~~~~~~~~~~~~~~~~~~~~~

Profile performance issues:

.. code-block:: python

   from pdfrebuilder.engine import PerformanceProfiler

   profiler = PerformanceProfiler()

   with profiler.profile("document_processing"):
       engine = DocumentEngine()
       result = engine.extract("problematic.pdf")

   # Generate performance report
   report = profiler.generate_report()
   report.save("performance_report.html")
