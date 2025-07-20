# API Documentation

This section contains comprehensive API documentation for the Multi-Format Document Engine.

## Getting Started

- **[Comprehensive API Guide](COMPREHENSIVE_GUIDE.md)** - Complete guide with examples and best practices
- **[API Usage Examples](../examples/api_usage_examples.py)** - Executable code examples

## Categories

- [Core Modules](core/) - Core functionality and base classes
- [Engines](engines/) - Document parsing and rendering engines
- [Models](models/) - Data models and schemas
- [Tools](tools/) - Utility functions and helpers

## Quick Reference

### Core Data Models

- [`UniversalDocument`](models/universal_idm.md#UniversalDocument) - Main document model containing all document data
- [`PageUnit`](models/universal_idm.md#PageUnit) - Represents a single page in paginated documents
- [`CanvasUnit`](models/universal_idm.md#CanvasUnit) - Represents a canvas in design documents
- [`Layer`](models/universal_idm.md#Layer) - Hierarchical content organization within document units
- [`TextElement`](models/universal_idm.md#TextElement) - Text content with formatting information
- [`ImageElement`](models/universal_idm.md#ImageElement) - Image content with metadata
- [`DrawingElement`](models/universal_idm.md#DrawingElement) - Vector graphics and shapes

### Parser Interfaces

- [`DocumentParser`](engine/document_parser.md#DocumentParser) - Abstract base class for format parsers
- [`PDFParser`](engine/document_parser.md#PDFParser) - PDF-specific parser implementation
- [`PSDParser`](engine/document_parser.md#PSDParser) - PSD-specific parser implementation
- [`parse_document`](engine/document_parser.md#parse_document) - Universal document parsing function

### Renderer Interfaces

- [`DocumentRenderer`](engine/document_renderer.md#DocumentRenderer) - Abstract base class for renderers
- [`PDFRenderer`](engine/document_renderer.md#PDFRenderer) - PDF output renderer
- [`ImageRenderer`](engine/document_renderer.md#ImageRenderer) - Image output renderer

### Key Functions

- [`extract_pdf_content`](engine/extract_pdf_content_fitz.md#extract_pdf_content) - PDF content extraction using PyMuPDF
- [`extract_psd_content`](engine/extract_psd_content.md#extract_psd_content) - PSD content extraction using psd-tools
- [`recreate_pdf_from_config`](recreate_pdf_from_config.md#recreate_pdf_from_config) - PDF reconstruction from Universal IDM
- [`compare_pdfs_visual`](compare_pdfs_visual.md#compare_pdfs_visual) - Visual PDF comparison

### Utility Functions

- [`normalize_text_spacing`](tools/generic.md#normalize_text_spacing) - Text spacing normalization
- [`detect_file_format`](tools/generic.md#detect_file_format) - Automatic file format detection
- [`validate_schema`](models/schema_validator.md#validate_schema) - Universal IDM schema validation

## Usage Examples

### Basic Document Processing

```python
from src.engine.document_parser import parse_document
from src.engine.document_renderer import render_document

# Parse any supported document
document, manifest = parse_document("input/sample.pdf")

# Render to different formats
render_document(document, "output/result.pdf", format="pdf")
render_document(document, "output/result.png", format="image")
```

### Working with Universal IDM

```python
from src.models.universal_idm import UniversalDocument

# Load from JSON
with open("layout_config.json") as f:
    document = UniversalDocument.from_json(f.read())

# Access document structure
for unit in document.document_structure:
    if unit.type == DocumentType.PAGE:
        print(f"Page {unit.page_number}: {unit.size}")

        for layer in unit.layers:
            print(f"  Layer: {layer.layer_name}")

            for element in layer.content:
                if isinstance(element, TextElement):
                    print(f"    Text: {element.text}")
```

### Custom Parser Implementation

```python
from src.engine.document_parser import DocumentParser
from src.models.universal_idm import UniversalDocument

class CustomParser(DocumentParser):
    def can_parse(self, file_path: str) -> bool:
        return file_path.lower().endswith('.custom')

    def parse(self, file_path: str, **kwargs):
        # Implement custom parsing logic
        document = UniversalDocument()
        manifest = AssetManifest()
        return document, manifest
```

See the [examples directory](../examples/) for complete usage examples and tutorials.
