# Project Structure

## Directory Organization

```
project_root/
├── main.py                     # Main entry point and CLI interface
├── src/                        # Core application modules
│   ├── __init__.py
│   ├── settings.py             # Configuration constants and settings
│   ├── extract_pdf_content.py  # PDF content extraction logic
│   ├── recreate_pdf_from_config.py # PDF reconstruction from JSON
│   ├── render.py               # Element rendering utilities
│   ├── tools.py                # Utility functions and helpers
│   ├── compare_pdfs_visual.py  # Visual comparison tools
│   └── generate_debug_pdf_layers.py # Debug visualization
├── examples/                   # Example scripts and demonstrations
│   ├── README.md              # Documentation for examples
│   ├── extract_sample.py      # PDF extraction example
│   ├── batch_modification_example.py # Batch modification demo
│   └── output/                # Example output files
├── input/                      # Input PDF files
├── output/                     # Generated output files
├── images/                     # Extracted images (auto-generated)
├── downloaded_fonts/           # Custom font files (.ttf)
├── tests/                      # Test suite and utilities
│   ├── demos/                  # Test-related demonstration scripts
│   ├── fixtures/               # Test configuration files
│   ├── output/                 # Test output files and artifacts
│   └── test_*.py              # Individual test files
├── scripts/                    # Utility and maintenance scripts
├── docs/                       # Project documentation
├── book/                       # Reference materials/documentation
├── layout_config.json         # Main layout configuration (generated)
├── manual_overrides.json5     # Manual corrections file
├── requirements.txt           # Python dependencies
└── pyproject.toml            # Tool configurations
```

## Core Modules

### `src/` Package Structure

- **settings.py**: Central configuration with `CONFIG` dict and `STANDARD_PDF_FONTS`
- **extract_pdf_content.py**: PDF parsing and content extraction
- **recreate_pdf_from_config.py**: PDF generation from JSON configuration
- **render.py**: Element rendering with `_render_element()` and `json_serializer()`
- **tools.py**: Utilities like `normalize_text_spacing()`, color helpers
- **compare_pdfs_visual.py**: Visual diff generation between PDFs
- **generate_debug_pdf_layers.py**: Layer-by-layer debug visualization

## Key Files

### Configuration Files

- `layout_config.json`: Structured layout data with metadata, pages, and elements
- `manual_overrides.json5`: Override system for fonts, colors, and text corrections
- `settings.py`: Application constants and default configurations

### Data Flow

1. **Input**: PDF files in `input/` directory
2. **Extraction**: Content parsed to `layout_config.json`
3. **Processing**: Optional manual overrides applied
4. **Output**: Rebuilt PDFs in `output/` directory
5. **Assets**: Images extracted to `images/`, fonts in `downloaded_fonts/`

## Naming Conventions

- **Files**: snake_case for Python modules
- **Functions**: snake_case following Python conventions
- **Constants**: UPPER_CASE in settings.py
- **JSON keys**: snake_case for consistency
- **Element IDs**: Format like `text_0`, `image_1` for uniqueness
