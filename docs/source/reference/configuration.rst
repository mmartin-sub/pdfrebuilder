Configuration Reference
=======================

This section provides a complete reference for all configuration options in the Multi-Format Document Engine.

Main Configuration
------------------

Processing Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import ProcessingConfig

   config = ProcessingConfig(
       # Text processing options
       text_extraction_mode="precise",      # "fast", "balanced", "precise"
       normalize_text_spacing=True,         # Auto-fix spacing issues
       preserve_fonts=True,                 # Maintain original fonts
       font_embedding_mode="subset",        # "none", "subset", "full"

       # Image processing options
       extract_images=True,                 # Extract raster images
       image_quality="high",                # "low", "medium", "high", "maximum"
       image_format="original",             # "original", "jpeg", "png"
       min_image_size=(10, 10),            # Minimum image dimensions

       # Vector graphics options
       preserve_vector_graphics=True,       # Extract vector elements
       vector_precision="high",             # "low", "medium", "high"
       simplify_paths=False,               # Simplify complex paths

       # Layout options
       preserve_exact_positioning=True,     # Maintain precise positioning
       snap_to_grid=False,                 # Snap elements to grid
       grid_size=1.0,                      # Grid size in points

       # Quality options
       output_quality="high",              # "draft", "normal", "high", "maximum"
       color_accuracy="high",              # "low", "medium", "high"
       maintain_transparency=True,          # Preserve transparency

       # Template mode options
       use_template_fallback=True,         # Use template mode on errors
       template_quality="high",            # Template rendering quality
       template_compression="medium"        # Template compression level
   )

Performance Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import PerformanceConfig

   config = PerformanceConfig(
       # Memory management
       memory_optimization=True,           # Enable memory optimization
       max_memory_usage="2GB",            # Maximum memory usage
       memory_cleanup_interval=10,        # Clean up every N files

       # Processing options
       parallel_processing=True,           # Enable parallel processing
       max_workers=4,                     # Maximum worker threads
       chunk_processing=True,             # Process in chunks
       chunk_size=1024*1024,             # Chunk size in bytes

       # Caching options
       enable_caching=True,               # Enable result caching
       cache_directory="/tmp/pdfrebuilder", # Cache directory
       cache_size_limit="1GB",            # Maximum cache size
       cache_ttl=3600,                    # Cache TTL in seconds

       # I/O options
       io_buffer_size=65536,              # I/O buffer size
       temp_directory="/tmp",             # Temporary file directory
       cleanup_temp_files=True,           # Auto-cleanup temp files

       # GPU acceleration (if available)
       enable_gpu_acceleration=False,     # Enable GPU processing
       gpu_memory_limit="1GB"             # GPU memory limit
   )

Validation Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import ValidationConfig

   config = ValidationConfig(
       # Quality thresholds
       similarity_threshold=0.9,          # Overall similarity threshold
       text_threshold=0.95,               # Text accuracy threshold
       layout_threshold=0.9,              # Layout accuracy threshold
       color_threshold=0.85,              # Color accuracy threshold
       font_threshold=0.9,                # Font accuracy threshold

       # Validation options
       enable_validation=True,            # Enable automatic validation
       strict_validation=False,           # Strict validation mode
       ignore_minor_differences=True,     # Ignore small differences

       # Comparison settings
       comparison_dpi=150,                # DPI for visual comparison
       comparison_tolerance=5,            # Pixel tolerance
       ignore_metadata=True,              # Ignore metadata differences

       # Reporting options
       generate_diff_images=True,         # Generate visual diffs
       save_validation_reports=True,      # Save detailed reports
       report_format="html",              # "html", "json", "pdf"

       # Performance options
       parallel_validation=True,          # Parallel page validation
       validation_timeout=300             # Validation timeout (seconds)
   )

Manual Overrides
----------------

Override File Format
~~~~~~~~~~~~~~~~~~~~

The manual_overrides.json5 file supports the following structure:

.. code-block:: json5

   {
     // Global settings
     "use_original_as_template": true,
     "template_quality": "high",
     "global_font_scaling": 1.0,
     "global_color_adjustment": 0.0,

     // Text block overrides
     "text_block_overrides": {
       "block_x_y": {
         "text": "Corrected text content",
         "font": "Arial-Regular",
         "font_size": 12.0,
         "font_size_multiplier": 1.1,
         "color": 0,  // RGB as integer
         "color_rgb": [0.0, 0.0, 0.0],  // RGB as array
         "bold": true,
         "italic": false,
         "underline": false,
         "align": "left",  // "left", "center", "right"
         "line_height": 1.2,
         "letter_spacing": 0.0,
         "word_spacing": 0.0,
         "background_color": null,
         "border": {
           "width": 1.0,
           "color": [0.0, 0.0, 0.0],
           "style": "solid"  // "solid", "dashed", "dotted"
         }
       }
     },

     // Font mappings
     "text_fonts": {
       "OriginalFont-Regular": "ReplacementFont-Regular.ttf",
       "MissingFont-Bold": "Arial-Bold.ttf"
     },

     // Image overrides
     "image_bboxes": {
       "image_1_hash.jpeg": [x1, y1, x2, y2],
       "image_2_hash.png": [x1, y1, x2, y2]
     },

     "image_replacements": {
       "image_1_hash.jpeg": "replacement_image.jpg"
     },

     "image_transformations": {
       "image_1_hash.jpeg": {
         "scale": 1.2,
         "rotation": 90,
         "flip_horizontal": false,
         "flip_vertical": false,
         "opacity": 1.0
       }
     },

     // Drawing/vector overrides
     "drawing_overrides": {
       "drawing_0": {
         "color": [1.0, 0.0, 0.0],  // Red stroke
         "fill": [0.0, 1.0, 0.0],   // Green fill
         "width": 2.0,
         "opacity": 0.8,
         "visible": true
       }
     },

     // Page-level overrides
     "page_overrides": {
       "0": {  // Page number
         "background_color": [1.0, 1.0, 1.0],
         "margins": [72, 72, 72, 72],  // top, right, bottom, left
         "rotation": 0,  // degrees
         "scale": 1.0
       }
     },

     // Processing hints
     "processing_hints": {
       "complex_graphics_pages": [0, 2, 5],  // Use template mode for these pages
       "text_heavy_pages": [1, 3, 4],        // Use precise text extraction
       "skip_pages": [],                      // Skip these pages
       "force_ocr_pages": []                  // Force OCR on these pages
     }
   }

Environment Variables
---------------------

The engine supports the following environment variables:

System Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Core settings
   PDFREBUILDER_DEBUG=true                    # Enable debug mode
   PDFREBUILDER_LOG_LEVEL=INFO               # Logging level
   PDFREBUILDER_CONFIG_DIR=/path/to/config   # Configuration directory

   # Performance settings
   PDFREBUILDER_MAX_MEMORY=2GB               # Maximum memory usage
   PDFREBUILDER_WORKERS=4                    # Number of worker processes
   PDFREBUILDER_TEMP_DIR=/tmp/pdfrebuilder   # Temporary directory

   # Cache settings
   PDFREBUILDER_CACHE_ENABLED=true           # Enable caching
   PDFREBUILDER_CACHE_DIR=/var/cache/pdfrebuilder  # Cache directory
   PDFREBUILDER_CACHE_SIZE=1GB               # Maximum cache size

   # Font settings
   PDFREBUILDER_FONT_DIR=/usr/share/fonts    # Additional font directory
   PDFREBUILDER_DOWNLOAD_FONTS=true          # Auto-download missing fonts

   # Processing settings
   PDFREBUILDER_DEFAULT_DPI=150              # Default DPI for processing
   PDFREBUILDER_QUALITY_THRESHOLD=0.9        # Default quality threshold
   PDFREBUILDER_TIMEOUT=300                  # Processing timeout (seconds)

Engine-Specific Settings
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # PyMuPDF settings
   PYMUPDF_FONT_WARNINGS=false              # Suppress font warnings
   PYMUPDF_IMAGE_ALPHA=true                 # Preserve image alpha

   # ReportLab settings
   REPORTLAB_FONT_CACHE=/tmp/rl_fonts       # Font cache directory
   REPORTLAB_COMPRESS_STREAMS=true          # Compress PDF streams

   # Validation settings
   VALIDATION_ENABLED=true                   # Enable validation
   VALIDATION_STRICT=false                   # Strict validation mode
   VALIDATION_DPI=150                        # Validation comparison DPI

Configuration Files
-------------------

Main Configuration File
~~~~~~~~~~~~~~~~~~~~~~~

Create a pdfrebuilder.toml file for project-wide settings:

.. code-block:: toml

   [general]
   debug = false
   log_level = "INFO"
   temp_directory = "/tmp/pdfrebuilder"

   [processing]
   default_quality = "high"
   enable_template_fallback = true
   normalize_text_spacing = true

   [performance]
   max_memory = "2GB"
   parallel_workers = 4
   enable_caching = true
   cache_directory = "/var/cache/pdfrebuilder"

   [validation]
   enable_validation = true
   similarity_threshold = 0.9
   generate_reports = true

   [fonts]
   font_directories = [
       "/usr/share/fonts",
       "/usr/local/share/fonts",
       "./fonts"
   ]
   download_missing_fonts = true

   [engines]
   preferred_pdf_engine = "pymupdf"
   preferred_image_engine = "pillow"

   [output]
   default_format = "pdf"
   compression_level = "medium"
   embed_fonts = "subset"

Batch Configuration
~~~~~~~~~~~~~~~~~~~

Create batch processing configurations:

.. code-block:: json

   {
     "batch_config": {
       "input_directory": "input/",
       "output_directory": "output/",
       "file_pattern": "*.pdf",
       "recursive": false,
       "preserve_structure": true
     },

     "processing": {
       "parallel_workers": 4,
       "timeout_per_file": 300,
       "continue_on_error": true,
       "retry_failed": true,
       "retry_count": 2
     },

     "quality": {
       "enable_validation": true,
       "quality_threshold": 0.9,
       "move_low_quality": true,
       "low_quality_directory": "needs_review/"
     },

     "reporting": {
       "generate_summary": true,
       "detailed_logs": true,
       "save_failed_list": true,
       "email_notifications": false
     }
   }

API Configuration
~~~~~~~~~~~~~~~~~

For API deployments:

.. code-block:: yaml

   # api_config.yml
   server:
     host: "0.0.0.0"
     port: 8080
     workers: 4
     timeout: 300

   processing:
     max_file_size: "50MB"
     allowed_formats: ["pdf"]
     queue_size: 100
     result_ttl: 3600

   storage:
     temp_directory: "/tmp/api_processing"
     cleanup_interval: 300
     max_storage: "10GB"

   security:
     enable_auth: false
     api_key_required: false
     rate_limiting: true
     max_requests_per_minute: 60

   monitoring:
     enable_metrics: true
     metrics_endpoint: "/metrics"
     health_check_endpoint: "/health"

Advanced Configuration
----------------------

Custom Engine Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.engine import EngineConfig, CustomEngine

   class CustomPDFEngine(CustomEngine):
       def __init__(self, config):
           super().__init__(config)
           self.custom_settings = {
               'precision_mode': config.get('precision_mode', True),
               'optimization_level': config.get('optimization_level', 'high'),
               'custom_filters': config.get('custom_filters', [])
           }

       def extract(self, pdf_path):
           # Custom extraction logic
           pass

       def rebuild(self, layout, output_path):
           # Custom rebuild logic
           pass

   # Register custom engine
   from pdfrebuilder.engine import register_engine
   register_engine('custom_pdf', CustomPDFEngine)

Plugin Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pdfrebuilder.plugins import PluginManager

   # Configure plugins
   plugin_config = {
       'ocr_plugin': {
           'enabled': True,
           'engine': 'tesseract',
           'languages': ['eng', 'fra'],
           'confidence_threshold': 0.8
       },
       'watermark_plugin': {
           'enabled': False,
           'text': 'PROCESSED',
           'opacity': 0.3,
           'position': 'center'
       },
       'metadata_plugin': {
           'enabled': True,
           'preserve_original': True,
           'add_processing_info': True
       }
   }

   plugin_manager = PluginManager(plugin_config)

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging.config

   LOGGING_CONFIG = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'standard': {
               'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
           },
           'detailed': {
               'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
           }
       },
       'handlers': {
           'default': {
               'level': 'INFO',
               'formatter': 'standard',
               'class': 'logging.StreamHandler',
           },
           'file': {
               'level': 'DEBUG',
               'formatter': 'detailed',
               'class': 'logging.FileHandler',
               'filename': 'pdfrebuilder.log',
               'mode': 'a',
           },
       },
       'loggers': {
           '': {
               'handlers': ['default', 'file'],
               'level': 'DEBUG',
               'propagate': False
           },
           'pdfrebuilder': {
               'handlers': ['default', 'file'],
               'level': 'DEBUG',
               'propagate': False
           }
       }
   }

   logging.config.dictConfig(LOGGING_CONFIG)
