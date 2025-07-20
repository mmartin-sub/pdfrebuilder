# Product Overview

## PDF Layout Extractor and Rebuilder

A Python tool for deconstructing PDF layouts into human-readable JSON format and rebuilding visually similar PDFs from that data. The primary purpose is to enable programmatic modification of PDF content while preserving original layout.

### Core Capabilities

- **Layout Extraction**: Extracts text blocks, raster images, and vector graphics from PDF pages
- **JSON Configuration**: Saves layout information in structured `layout_config.json` format
- **PDF Reconstruction**: Generates new PDFs from JSON configuration with visual fidelity
- **Intelligent Text Handling**: Automatically detects and normalizes text with unnatural character spacing
- **Advanced Override System**: Manual corrections via `manual_overrides.json5` for extraction errors
- **Template Mode**: Uses original PDF as pixel-perfect background preserving complex graphics
- **Visual Debugging**: Multi-page debug PDFs showing vector graphics layer-by-layer

### Key Use Cases

- Programmatic PDF content modification
- PDF layout analysis and reconstruction
- Template-based PDF generation
- PDF content extraction and transformation
