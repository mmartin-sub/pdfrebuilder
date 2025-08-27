# Configuration Reference

This document provides a comprehensive reference for all configuration options in the Multi-Format Document Engine.

## Configuration Files Overview

The system uses several configuration files:

1. **layout_config.json**: Main extracted layout data (auto-generated)
2. **manual_overrides.json5**: Manual corrections and customizations
3. **src/settings.py**: Application-wide settings and constants
4. **docs/validation_config.json**: Documentation validation settings

## Universal Document Structure Schema

### Root Configuration Structure

```json5
{
  "version": "1.0",
  "engine": "fitz",
  "engine_version": "PyMuPDF 1.26.23",
  "metadata": {
    "format": "PDF 1.4",
    "title": "Document Title",
    "author": "Author Name",
    "subject": "Document Subject",
    "keywords": "keyword1,keyword2",
    "creator": "Application Name",
    "producer": "PDF Producer",
    "creationDate": "D:20250717183732+00'00'",
    "modDate": "D:20250717183732+00'00'",
    "trapped": "",
    "encryption": null
  },
  "document_structure": [
    // Array of page or canvas objects
  ]
}
```

#### Root Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `version` | string | Yes | Schema version (currently "1.0") |
| `engine` | string | Yes | Processing engine used ("fitz", "psd", etc.) |
| `engine_version` | string | Yes | Version of the processing engine |
| `metadata` | object | Yes | Document metadata |
| `document_structure` | array | Yes | Array of document units (pages/canvas) |

### Document Structure Objects

#### Page Object (PDF Documents)

```json5
{
  "type": "page",
  "page_number": 0,
  "size": [612.0, 792.0],
  "page_background_color": [1.0, 1.0, 1.0],
  "layers": [
    {
      "layer_id": "page_0_base_layer",
      "layer_name": "Page Content",
      "layer_type": "base",
      "bbox": [0, 0, 612.0, 792.0],
      "visibility": true,
      "opacity": 1.0,
      "blend_mode": "Normal",
      "children": [],
      "content": [
        // Array of element objects
      ]
    }
  ]
}
```

#### Page Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be "page" |
| `page_number` | integer | Yes | Zero-based page index |
| `size` | array | Yes | Page dimensions [width, height] |
| `page_background_color` | array | No | RGB color [r, g, b] (0.0-1.0) |
| `layers` | array | Yes | Array of layer objects |

#### Canvas Object (PSD Documents - Future)

```json5
{
  "type": "canvas",
  "canvas_size": [1920, 1080],
  "layers": [
    // Layer objects with rich hierarchy
  ]
}
```

### Layer Objects

#### Layer Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `layer_id` | string | Yes | Unique layer identifier |
| `layer_name` | string | Yes | Human-readable layer name |
| `layer_type` | string | Yes | Layer type ("base", "pixel", "text", "shape", "group") |
| `bbox` | array | Yes | Bounding box [x1, y1, x2, y2] |
| `visibility` | boolean | Yes | Whether layer is visible |
| `opacity` | number | Yes | Layer opacity (0.0-1.0) |
| `blend_mode` | string | Yes | Blend mode ("Normal", "Multiply", etc.) |
| `children` | array | No | Child layers (for group layers) |
| `content` | array | Yes | Array of elements in this layer |

### Element Types

#### Text Elements

```json
{
  "type": "text",
  "bbox": [100.0, 700.0, 200.0, 720.0],
  "raw_text": "O r i g i n a l   T e x t",
  "text": "Original Text",
  "font_details": {
    "name": "Arial-Bold",
    "size": 12.0,
    "color": 0,
    "ascender": 9.0,
    "descender": -2.0,
    "is_superscript": false,
    "is_italic": false,
    "is_serif": false,
    "is_monospaced": false,
    "is_bold": true,
    "original_flags": 16
  },
  "writing_mode": 0,
  "writing_direction": [1.0, 0.0],
  "align": 0,
  "adjust_spacing": true,
  "background_color": null,
  "id": "text_0"
}
```

##### Text Element Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be "text" |
| `bbox` | array | Yes | Bounding box [left, top, right, bottom] |
| `raw_text` | string | Yes | Original text before normalization |
| `text` | string | Yes | Cleaned/normalized text content |
| `font_details` | object | Yes | Font information object |
| `writing_mode` | integer | Yes | Text writing mode (0=horizontal, 1=vertical) |
| `writing_direction` | array | Yes | Direction vector [x, y] |
| `align` | integer | Yes | Text alignment (0=left, 1=center, 2=right) |
| `adjust_spacing` | boolean | Yes | Whether spacing normalization was applied |
| `background_color` | array/null | No | Background color RGB or null |
| `id` | string | Yes | Unique element identifier |

##### Font Details Object

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Font name or "Unnamed-T3" for embedded |
| `size` | number | Yes | Font size in points |
| `color` | integer | Yes | Color as integer (RGB hex) |
| `ascender` | number | Yes | Font ascender metric |
| `descender` | number | Yes | Font descender metric |
| `is_superscript` | boolean | Yes | Whether text is superscript |
| `is_italic` | boolean | Yes | Whether font is italic |
| `is_serif` | boolean | Yes | Whether font is serif |
| `is_monospaced` | boolean | Yes | Whether font is monospaced |
| `is_bold` | boolean | Yes | Whether font is bold |
| `original_flags` | integer | Yes | Raw PyMuPDF font flags |

#### Image Elements

```json
{
  "type": "image",
  "image_file": "./images/img_fbc04c5c.jpeg",
  "bbox": [100.0, 200.0, 300.0, 400.0],
  "id": "image_1"
}
```

##### Image Element Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be "image" |
| `image_file` | string | Yes | Path to extracted image file |
| `bbox` | array | Yes | Position and size [left, top, right, bottom] |
| `id` | string | Yes | Unique element identifier |

#### Drawing/Shape Elements

```json
{
  "type": "drawing",
  "bbox": [100.0, 200.0, 150.0, 250.0],
  "color": null,
  "fill": [0.5, 0.5, 0.5],
  "width": 1.0,
  "drawing_commands": [
    {"cmd": "M", "pts": [100.0, 200.0]},
    {"cmd": "L", "pts": [150.0, 200.0]},
    {"cmd": "L", "pts": [150.0, 250.0]},
    {"cmd": "L", "pts": [100.0, 250.0]},
    {"cmd": "H"}
  ],
  "original_shape_type": "rectangle",
  "stroke_details": null,
  "fill_details": null,
  "id": "drawing_0"
}
```

##### Drawing Element Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be "drawing" |
| `bbox` | array | Yes | Bounding box [left, top, right, bottom] |
| `color` | array/null | No | Stroke color RGB or null |
| `fill` | array/null | No | Fill color RGB or null |
| `width` | number | Yes | Stroke width (default 1.0) |
| `drawing_commands` | array | Yes | Array of drawing command objects |
| `original_shape_type` | string/null | No | Shape hint ("rectangle", "ellipse", etc.) |
| `stroke_details` | object/null | No | Extended stroke properties |
| `fill_details` | object/null | No | Extended fill properties |
| `id` | string | Yes | Unique element identifier |

##### Drawing Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `M` | `[x, y]` | Move to point |
| `L` | `[x, y]` | Line to point |
| `C` | `[x1, y1, x2, y2, x3, y3]` | Cubic Bézier curve |
| `H` | None | Close path |
| `rect` | `[x1, y1, x2, y2]` | Rectangle primitive |
| `ellipse` | `[x1, y1, x2, y2]` | Ellipse primitive |

## Manual Overrides Configuration

The `manual_overrides.json5` file allows manual corrections and customizations:

```json5
{
  // Use original PDF as template background
  "use_original_as_template": true,

  // Override text content and formatting
  "text_block_overrides": {
    "block_100_200": {
      "text": "Corrected text content",
      "font": "Arial-Bold",
      "color": 4209970,
      "bbox": [100, 200, 300, 220]
    }
  },

  // Custom font mappings
  "text_fonts": {
    "ProblematicFont": "Arial.ttf",
    "CustomFont": "CustomFont.ttf"
  },

  // Image position overrides
  "image_bboxes": {
    "image_1_fbc04c5c.jpeg": [100.0, 200.0, 400.0, 600.0]
  },

  // Global settings
  "global_settings": {
    "default_font": "Noto Sans",
    "default_font_size": 12,
    "preserve_original_colors": true
  }
}
```

### Manual Override Properties

#### Text Block Overrides

| Property | Type | Description |
|----------|------|-------------|
| `text` | string | Override text content |
| `font` | string | Override font name |
| `color` | integer | Override text color (RGB integer) |
| `bbox` | array | Override bounding box [left, top, right, bottom] |
| `size` | number | Override font size |
| `adjust_spacing` | boolean | Override spacing adjustment |

#### Font Mappings

Map problematic or missing fonts to available alternatives:

```json5
{
  "text_fonts": {
    "Unnamed-T3": "Arial.ttf",
    "ProprietaryFont": "OpenSans-Regular.ttf"
  }
}
```

#### Image Overrides

```json5
{
  "image_bboxes": {
    "image_filename.jpg": [100.0, 200.0, 400.0, 600.0]
  }
}
```

#### Global Settings

| Property | Type | Description |
|----------|------|-------------|
| `default_font` | string | Default font for missing fonts. "Noto Sans" is a good choice. |
| `default_font_size` | number | Default font size |
| `preserve_original_colors` | boolean | Whether to preserve original colors |
| `normalize_text_spacing` | boolean | Global text spacing normalization |

## Font Management Configuration

The system uses a hierarchical font management system with automatic fallbacks and Google Fonts integration.

### Font Directory Structure

```
fonts/
├── manual/          # Human-managed fonts (highest priority)
│   ├── Arial.ttf
│   ├── CustomFont.otf
│   └── CorporateFont-Regular.ttf
├── auto/            # Library-managed fonts (auto-downloaded)
│   ├── Roboto-Regular.ttf
│   ├── OpenSans-Bold.ttf
│   └── NotoSans-Regular.ttf
└── README.md        # Documentation
```

### Font Resolution Priority

1. Standard PDF Fonts: Built-in fonts (helv, cour, tiro, etc.)
2. Manual Fonts: Fonts in `fonts/manual/` directory
3. Auto Fonts: Fonts in `fonts/auto/` directory
4. Google Fonts: Automatic download to `auto/` directory
5. Fallback: Default font from configuration

### Font Configuration in Manual Overrides

```json5
{
  "text_fonts": {
    // Map problematic fonts to available alternatives
    "Unnamed-T3": "Arial.ttf",
    "ProprietaryFont": "OpenSans-Regular.ttf",

    // Corporate font standardization
    "Arial": "CorporateFont-Regular.ttf",
    "Arial-Bold": "CorporateFont-Bold.ttf",

    // Multi-language support
    "default": "NotoSans-Regular.ttf",
    "chinese": "NotoSansCJK-Regular.ttf",
    "arabic": "NotoSansArabic-Regular.ttf"
  }
}
```

### Font Management Functions

The system provides several utilities for font management:

```python
from src.font_utils import ensure_font_registered, scan_available_fonts, font_covers_text

# Register font on page with glyph coverage check
font_name = ensure_font_registered(page, "Arial", verbose=True, text="Sample text")

# Scan available fonts
font_map = scan_available_fonts("fonts")  # Returns {font_name: font_path}

# Check if font covers specific text
covers_text = font_covers_text("fonts/Arial.ttf", "Hello World")
```

### Common Font Issues and Solutions

#### Issue: "Unnamed-T3" Fonts

Embedded fonts that cannot be extracted appear as "Unnamed-T3". Map them to available fonts:

```json5
{
  "text_fonts": {
    "Unnamed-T3": "Arial.ttf"  // Map embedded fonts to available fonts
  }
}
```

#### Issue: Missing Corporate Fonts

Add custom fonts to the manual directory:

```bash
# Add fonts to manual directory
cp CorporateFont-*.ttf fonts/manual/
```

```json5
{
  "text_fonts": {
    "Arial": "CorporateFont-Regular.ttf",
    "Arial-Bold": "CorporateFont-Bold.ttf"
  }
}
```

#### Issue: Unicode/Multi-language Support

Use Unicode-complete fonts for international text:

```json5
{
  "text_fonts": {
    "default": "NotoSans-Regular.ttf",      // Covers most Unicode
    "fallback": "NotoSansSymbols.ttf"      // Symbol fallback
  }
}
```

### Google Fonts Integration

The system automatically downloads fonts from Google Fonts when needed:

```python
# Automatic download (handled internally by ensure_font_registered)
font_name = ensure_font_registered(page, "Roboto", verbose=True)

# Manual download
from src.font.googlefonts import download_google_font
success = download_google_font("Open Sans", "fonts/auto")
```

### Font Substitution Tracking

The system automatically tracks font substitutions for debugging:

```python
# Font substitutions are tracked automatically
# Each substitution record contains:
# - original_font: The requested font
# - substituted_font: The actual font used
# - reason: Why substitution occurred
# - text_content: The text being rendered (if available)
# - element_id: Element identifier (if available)
# - page_number: Page number (if available)
```

## Application Settings

The `src/settings.py` file contains application-wide configuration through the `CONFIG` dictionary and related utilities:

### Core Configuration Dictionary

```python
CONFIG = {
    # File and directory paths (using lambda functions for dynamic resolution)
    "image_dir": lambda: output_config.get_output_path("images"),
    "config_path": "./layout_config.json",
    "override_config_path": "./override_config.json5",
    "rebuilt_pdf": lambda: output_config.get_output_path("rebuilt.pdf"),
    "diff_image": lambda: output_config.get_output_path("visual_diff.png"),
    "debug_pdf": lambda: output_config.get_output_path("debug_layers.pdf"),

    # Font settings
    "default_font": "Noto Sans",
    "fonts_dir": "fonts",
    "downloaded_fonts_dir": "fonts/auto",
    "manual_fonts_dir": "fonts/manual",

    # Debug and visualization settings
    "debug_font_name": "cour",
    "debug_fontsize": 8,
    "debug_line_height": 1.2,
    "debug_max_height_ratio": 0.8,
    "debug_text_wrap_width": 100,
    "debug_text_padding": 10,
    "debug_font": "Lato-Regular",
    "debug_overlay_width_ratio": 0.33,
    "debug_overlay_bg_color": [0.1, 0.1, 0.1],
    "debug_overlay_text_color": [0.95, 0.95, 0.95],
    "debug_text_background": True,
    "debug_overlay_margin": 10,
    "debug_overlay_width": 450,
    "debug_overlay_height": 180,

    # Processing settings
    "visual_diff_threshold": 5,
    "space_density_threshold": 0.3,
    "ssim_score_display_digits": 3,
    "debug_number_display_digits": 3,

    # Output directory settings (using lambda functions)
    "test_output_dir": lambda: output_config.test_output_dir,
    "test_temp_dir": lambda: output_config.get_test_output_path("temp"),
    "test_fonts_dir": lambda: output_config.get_test_output_path("fonts"),
    "test_reports_dir": lambda: output_config.get_test_output_path("reports"),
    "reports_output_dir": lambda: output_config.reports_output_dir,
    "font_validation_reports_dir": lambda: output_config.get_report_output_path("font_validation"),
    "test_coverage_reports_dir": lambda: output_config.get_report_output_path("test_coverage"),
    "font_validation_demo_reports_dir": lambda: output_config.get_test_output_path("font_validation_demo_reports"),
    "logs_output_dir": lambda: output_config.logs_output_dir,
    "debug_logs_dir": lambda: output_config.get_logs_output_path("debug"),
}

# Standard PDF fonts (always available)
STANDARD_PDF_FONTS = [
    "helv", "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "cour", "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "tiro", "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
    "Symbol", "ZapfDingbats"
]
```

### Output Configuration Management

The system uses an `OutputConfig` class to manage output directories dynamically:

```python
from src.settings import configure_output_directories, get_config_value

# Configure output directories
configure_output_directories(
    base_dir="custom_output",
    test_dir="custom_test_output",
    reports_dir="custom_reports"
)

# Get configuration values (resolves lambda functions)
image_dir = get_config_value('image_dir')
debug_pdf_path = get_config_value('debug_pdf')
```

#### OutputConfig Properties

| Property | Description | Auto-created |
|----------|-------------|--------------|
| `base_output_dir` | Base directory for all outputs | Yes |
| `test_output_dir` | Directory for test outputs | Yes |
| `reports_output_dir` | Directory for reports | Yes |
| `logs_output_dir` | Directory for logs | Yes |

#### OutputConfig Methods

| Method | Description |
|--------|-------------|
| `get_output_path(filename, subdir="")` | Get full output path for a file |
| `get_test_output_path(filename, subdir="")` | Get full test output path |
| `get_report_output_path(filename, subdir="")` | Get full report output path |
| `get_logs_output_path(filename, subdir="")` | Get full logs output path |

### Configuration Categories

#### File and Directory Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `image_dir` | function | `output/images` | Directory for extracted images |
| `config_path` | string | `./layout_config.json` | Main configuration file path |
| `override_config_path` | string | `./override_config.json5` | Override configuration file path |
| `rebuilt_pdf` | function | `output/rebuilt.pdf` | Default rebuilt PDF output path |
| `diff_image` | function | `output/visual_diff.png` | Visual comparison image path |
| `debug_pdf` | function | `output/debug_layers.pdf` | Debug PDF output path |

#### Font Management Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_font` | string | `"Noto Sans"` | Default fallback font |
| `fonts_dir` | string | `"fonts"` | Base fonts directory |
| `downloaded_fonts_dir` | string | `"fonts/auto"` | Auto-downloaded fonts directory |
| `manual_fonts_dir` | string | `"fonts/manual"` | Manually added fonts directory |

#### Debug and Visualization Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `debug_font_name` | string | `"cour"` | Font for debug text |
| `debug_fontsize` | integer | `8` | Font size for debug text |
| `debug_line_height` | float | `1.2` | Line height for debug text |
| `debug_max_height_ratio` | float | `0.8` | Maximum height ratio for debug boxes |
| `debug_text_wrap_width` | integer | `100` | Character width for text wrapping |
| `debug_text_padding` | integer | `10` | Padding inside debug boxes |
| `debug_font` | string | `"Lato-Regular"` | Debug overlay font |
| `debug_overlay_width_ratio` | float | `0.33` | Debug overlay width ratio |
| `debug_overlay_bg_color` | array | `[0.1, 0.1, 0.1]` | Debug overlay background color |
| `debug_overlay_text_color` | array | `[0.95, 0.95, 0.95]` | Debug overlay text color |
| `debug_text_background` | boolean | `True` | Whether to draw debug text background |
| `debug_overlay_margin` | integer | `10` | Margin for debug text box |
| `debug_overlay_width` | integer | `450` | Fixed width for debug text box |
| `debug_overlay_height` | integer | `180` | Fixed height for debug text box |

#### Processing and Validation Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `visual_diff_threshold` | integer | `5` | Visual difference threshold |
| `space_density_threshold` | float | `0.3` | Space density threshold for text normalization |
| `ssim_score_display_digits` | integer | `3` | SSIM score display precision |
| `debug_number_display_digits` | integer | `3` | Debug number display precision |

#### Output Directory Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `test_output_dir` | function | `output/tests` | Test output directory |
| `test_temp_dir` | function | `output/tests/temp` | Temporary test files directory |
| `test_fonts_dir` | function | `output/tests/fonts` | Test fonts directory |
| `test_reports_dir` | function | `output/tests/reports` | Test reports directory |
| `reports_output_dir` | function | `output/reports` | Reports output directory |
| `font_validation_reports_dir` | function | `output/reports/font_validation` | Font validation reports |
| `test_coverage_reports_dir` | function | `output/reports/test_coverage` | Test coverage reports |
| `font_validation_demo_reports_dir` | function | `output/tests/font_validation_demo_reports` | Font validation demo reports |
| `logs_output_dir` | function | `output/logs` | Logs output directory |
| `debug_logs_dir` | function | `output/logs/debug` | Debug logs directory |

## Documentation Validation Configuration

The `docs/validation_config.json` file configures documentation testing:

```json
{
  "validation_settings": {
    "code_examples": {
      "enabled": true,
      "timeout_seconds": 30,
      "skip_patterns": [
        "# Skip validation",
        "# TODO:",
        "# FIXME:"
      ]
    },
    "api_references": {
      "enabled": true,
      "ignore_external_modules": true,
      "project_modules": ["src.*"]
    },
    "configuration_examples": {
      "enabled": true,
      "validate_json": true,
      "validate_json5": true
    }
  }
}
```

### Logging Configuration

The system provides centralized logging configuration:

```python
from src.settings import configure_logging
import logging

# Basic logging setup
configure_logging()

# Custom logging configuration
configure_logging(
    log_file="output/app.log",
    log_level=logging.DEBUG,
    log_format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
```

#### Logging Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_file` | string/None | None | Path to log file (None = console only) |
| `log_level` | int | `logging.INFO` | Logging level |
| `log_format` | string | Standard format | Log message format string |

#### Available Log Levels

| Level | Value | Description |
|-------|-------|-------------|
| `DEBUG` | 10 | Detailed diagnostic information |
| `INFO` | 20 | General information messages |
| `WARNING` | 30 | Warning messages |
| `ERROR` | 40 | Error messages |
| `CRITICAL` | 50 | Critical error messages |

## Environment Variables

The system recognizes these environment variables. For more information on how to manage environment variables and secrets, see the [Secrets Management](../guides/secrets-management.md) guide.

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Python module search path | Current directory |
| `PDF_ENGINE_DEBUG` | Enable debug logging | False |
| `FONT_CACHE_DIR` | Font cache directory | downloaded_fonts |
| `MAX_MEMORY_MB` | Memory limit | 1024 |
| `TEMP_DIR` | Temporary file directory | System temp |

## Command Line Configuration

### Main Application Options

```bash
python main.py [OPTIONS]

Options:
  --input PATH          Input PDF file path
  --output PATH         Output PDF file path
  --config PATH         Configuration file path
  --mode MODE           Processing mode (extract|generate|debug|full)
  --debugoutput PATH    Debug output file path
  --verbose            Enable verbose logging
  --help               Show help message
```

### Processing Modes

| Mode | Description |
|------|-------------|
| `extract` | Extract layout to JSON only |
| `generate` | Generate PDF from existing JSON |
| `debug` | Generate debug visualization |
| `full` | Extract and generate (default) |

### Validation Script Options

```bash
python scripts/validate_docs.py [OPTIONS]

Options:
  --docs-dir PATH       Documentation directory
  --file PATH           Specific file to validate
  --examples           Validate code examples
  --api-refs           Validate API references
  --config             Validate configuration examples
  --all                Run all validations
  --verbose            Verbose output
  --fail-fast          Stop on first failure
```

## Color Formats

The system supports multiple color formats:

### Integer Format

```json5
{
  "color": 0,          // Black
  "color": 16777215,   // White (0xFFFFFF)
  "color": 4209970     // Custom color
}
```

### RGB Array Format

```json5
{
  "color": [0.0, 0.0, 0.0],     // Black
  "color": [1.0, 1.0, 1.0],     // White
  "color": [0.5, 0.3, 0.8]      // Purple
}
```

### Null Format

```json5
{
  "color": null        // No color/transparent
}
```

## Coordinate System

- **Origin**: Bottom-left corner (0, 0)
- **X-axis**: Increases rightward
- **Y-axis**: Increases upward
- **Units**: PDF units (typically 72 per inch)
- **Bounding boxes**: [left, top, right, bottom]

## File Naming Conventions

### Generated Files

| Pattern | Description |
|---------|-------------|
| `layout_config.json` | Main configuration file |
| `manual_overrides.json5` | Manual override file |
| `img_[hash].[ext]` | Extracted images |
| `debug_layers.pdf` | Debug visualization |
| `comparison.pdf` | Visual comparison |

### Element IDs

| Pattern | Description |
|---------|-------------|
| `text_N` | Text elements (N = sequential number) |
| `image_N` | Image elements |
| `drawing_N` | Drawing/shape elements |
| `block_X_Y` | Override blocks (X, Y = coordinates) |

## Validation and Schema

### Schema Validation

```python
# Validate configuration against schema
from src.tools.schema_tools import validate_config

result = validate_config("layout_config.json")
if not result.is_valid:
    print(f"Validation errors: {result.errors}")
```

### Configuration Migration

```python
# Migrate old configuration to new format
from src.tools.schema_tools import migrate_config

migrate_config("old_config.json", "new_config.json")
```

## Configuration Examples for Different Use Cases

### Basic Document Processing

```json5
{
  // Basic configuration for simple PDF processing
  "use_original_as_template": false,
  "global_settings": {
    "default_font": "Noto Sans",
    "default_font_size": 12,
    "preserve_original_colors": true,
    "normalize_text_spacing": true
  }
}
```

### High-Quality Document Reproduction

```json5
{
  // Configuration for maximum fidelity reproduction
  "use_original_as_template": true,
  "global_settings": {
    "preserve_original_colors": true,
    "preserve_original_fonts": true,
    "high_quality_images": true
  },
  "text_fonts": {
    // Map problematic fonts to high-quality alternatives
    "Unnamed-T3": "Times-Roman.ttf",
    "ProprietaryFont": "Arial-Unicode.ttf"
  }
}
```

### Batch Processing Configuration

```json5
{
  // Configuration optimized for batch processing
  "use_original_as_template": false,
  "global_settings": {
    "default_font": "Noto Sans",
    "normalize_text_spacing": true,
    "optimize_for_speed": true,
    "cache_fonts": true
  },
  "text_fonts": {
    // Standardize fonts across all documents
    "Times-Roman": "Arial.ttf",
    "Helvetica": "Arial.ttf",
    "Courier": "CourierNew.ttf"
  }
}
```

### Debug and Development Configuration

```json5
{
  // Configuration for debugging and development
  "use_original_as_template": false,
  "global_settings": {
    "debug_mode": true,
    "verbose_logging": true,
    "preserve_element_ids": true,
    "generate_debug_info": true
  },
  "debug_settings": {
    "highlight_text_blocks": true,
    "show_bounding_boxes": true,
    "color_code_elements": true
  }
}
```

### Corporate Document Processing

```json5
{
  // Configuration for corporate document standardization
  "use_original_as_template": false,
  "global_settings": {
    "default_font": "CorporateFont",
    "enforce_brand_colors": true,
    "standardize_formatting": true
  },
  "text_fonts": {
    // Map all fonts to corporate standards
    "Arial": "CorporateFont-Regular.ttf",
    "Times-Roman": "CorporateFont-Serif.ttf",
    "Helvetica": "CorporateFont-Sans.ttf"
  },
  "color_mappings": {
    // Standardize colors to brand palette
    "0": "#000000",        // Black text
    "16777215": "#FFFFFF", // White backgrounds
    "custom_brand": "#003366" // Corporate blue
  }
}
```

### Multi-Language Document Processing

```json5
{
  // Configuration for multi-language documents
  "global_settings": {
    "unicode_support": true,
    "fallback_fonts": [
      "NotoSans-Regular.ttf",
      "NotoSansCJK-Regular.ttf",
      "NotoSansArabic-Regular.ttf"
    ]
  },
  "text_fonts": {
    // Language-specific font mappings
    "default": "NotoSans-Regular.ttf",
    "chinese": "NotoSansCJK-Regular.ttf",
    "arabic": "NotoSansArabic-Regular.ttf",
    "japanese": "NotoSansCJK-Regular.ttf"
  },
  "text_processing": {
    "preserve_rtl_text": true,
    "handle_complex_scripts": true
  }
}
```

### Performance-Optimized Configuration

```json5
{
  // Configuration optimized for performance
  "global_settings": {
    "optimize_for_speed": true,
    "cache_fonts": true,
    "parallel_processing": true,
    "memory_limit_mb": 2048
  },
  "image_settings": {
    "max_image_size": [1024, 1024],
    "compress_images": true,
    "image_quality": 85
  },
  "font_settings": {
    "font_cache_size": 200,
    "preload_common_fonts": true
  }
}
```

### Accessibility-Focused Configuration

```json5
{
  // Configuration for accessibility compliance
  "global_settings": {
    "ensure_accessibility": true,
    "minimum_font_size": 12,
    "high_contrast_mode": false
  },
  "accessibility_settings": {
    "alt_text_for_images": true,
    "structured_content": true,
    "reading_order_preservation": true,
    "color_contrast_check": true
  },
  "text_fonts": {
    // Use accessibility-friendly fonts
    "default": "OpenDyslexic-Regular.ttf",
    "fallback": "Arial.ttf"
  }
}
```

### Archive and Preservation Configuration

```json5
{
  // Configuration for long-term document preservation
  "use_original_as_template": true,
  "global_settings": {
    "preserve_original_structure": true,
    "embed_all_fonts": true,
    "preserve_metadata": true,
    "pdf_a_compliance": true
  },
  "preservation_settings": {
    "lossless_images": true,
    "preserve_color_profiles": true,
    "maintain_original_resolution": true
  }
}
```

## Application Configuration Examples

### Development Environment Setup

```python
# src/settings.py customization for development
from src.settings import configure_output_directories, configure_logging
import logging

# Configure development directories
configure_output_directories(
    base_dir="dev_output",
    test_dir="dev_tests",
    reports_dir="dev_reports"
)

# Enable debug logging
configure_logging(
    log_file="dev_output/debug.log",
    log_level=logging.DEBUG
)
```

### Production Environment Setup

```python
# Production configuration
from src.settings import configure_output_directories, configure_logging
import logging

# Configure production directories
configure_output_directories(
    base_dir="/var/app/output",
    test_dir="/var/app/tests",
    reports_dir="/var/app/reports"
)

# Production logging
configure_logging(
    log_file="/var/log/pdf_engine.log",
    log_level=logging.INFO,
    log_format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
```

### Testing Environment Setup

```python
# Testing configuration
from src.settings import configure_output_directories
import tempfile
import os

# Use temporary directories for testing
temp_dir = tempfile.mkdtemp()
configure_output_directories(
    base_dir=os.path.join(temp_dir, "output"),
    test_dir=os.path.join(temp_dir, "tests"),
    reports_dir=os.path.join(temp_dir, "reports")
)
```

This reference covers all major configuration aspects of the Multi-Format Document Engine. For specific use cases, refer to the guides and examples in the documentation.
