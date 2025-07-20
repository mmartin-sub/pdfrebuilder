# Comprehensive API Guide

This guide provides a complete overview of the Multi-Format Document Engine API, with practical examples and best practices.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Universal IDM Data Model](#universal-idm-data-model)
4. [Document Parsing](#document-parsing)
5. [Document Rendering](#document-rendering)
6. [Configuration Management](#configuration-management)
7. [Visual Validation](#visual-validation)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Advanced Usage](#advanced-usage)

## Getting Started

### Basic Document Processing

The simplest way to get started is with the universal document parser:

```python
from src.engine.document_parser import parse_document

# Parse any supported document format
document, manifest = parse_document("input/sample.pdf")

# Access document information
print(f"Document has {len(document.document_structure)} pages")
print(f"Extracted {len(manifest.images)} images")
```

### Working with Extracted Content

```python
# Iterate through document structure
for page in document.document_structure:
    print(f"Page {page.page_number}: {page.size}")

    for layer in page.layers:
        print(f"  Layer: {layer.layer_name}")

        for element in layer.content:
            if hasattr(element, 'text'):
                print(f"    Text: {element.text}")
            elif hasattr(element, 'image_file'):
                print(f"    Image: {element.image_file}")
```

## Core Concepts

### Document Hierarchy

The Multi-Format Document Engine uses a hierarchical structure:

```
UniversalDocument
├── DocumentMetadata (title, author, etc.)
└── DocumentStructure (list of document units)
    ├── PageUnit (for PDF, Word, etc.)
    │   └── Layers
    │       └── Elements (Text, Image, Drawing)
    └── CanvasUnit (for PSD, Illustrator, etc.)
        └── Layers
            └── Elements (Text, Image, Shape)
```

### Element Types

- **TextElement**: Text content with font information
- **ImageElement**: Raster images with metadata
- **DrawingElement**: Vector graphics and shapes
- **ShapeElement**: Complex PSD shapes (future)

### Coordinate System

- Origin (0,0) is at bottom-left for PDF compatibility
- X increases rightward, Y increases upward
- All measurements in document units (typically 72 units per inch)

## Universal IDM Data Model

### Creating Documents Programmatically

```python
from src.models.universal_idm import (
    UniversalDocument, PageUnit, Layer, TextElement,
    BoundingBox, Color, FontDetails, LayerType
)

# Create a new document
document = UniversalDocument(
    engine="custom_engine",
    engine_version="1.0"
)

# Create a page
page = PageUnit(size=(612, 792))  # Letter size

# Create a layer
layer = Layer(
    layer_id="content",
    layer_name="Main Content",
    layer_type=LayerType.BASE,
    bbox=BoundingBox(0, 0, 612, 792)
)

# Create text element
font = FontDetails(
    name="Arial",
    size=12.0,
    color=Color.from_rgb_tuple((0, 0, 0)),
    ascender=10.0,
    descender=-2.0,
    is_bold=False,
    is_italic=False,
    is_serif=False,
    is_monospaced=False,
    is_superscript=False,
    original_flags=0
)

text = TextElement(
    id="text_1",
    bbox=BoundingBox(50, 700, 300, 720),
    raw_text="Hello World",
    text="Hello World",
    font_details=font
)

# Assemble document
layer.content = [text]
page.layers = [layer]
document.document_structure = [page]

# Serialize to JSON
json_str = document.to_json()
```

### Loading and Modifying Documents

```python
# Load from JSON file
with open("layout_config.json") as f:
    document = UniversalDocument.from_json(f.read())

# Modify text content
for page in document.document_structure:
    for layer in page.layers:
        for element in layer.content:
            if isinstance(element, TextElement):
                element.text = element.text.upper()

# Save modified document
with open("modified_config.json", "w") as f:
    f.write(document.to_json())
```

## Document Parsing

### Supported Formats

- **PDF**: Full support via PyMuPDF (fitz)
- **PSD**: Basic support via psd-tools
- **Future**: Word, PowerPoint, Illustrator

### PDF Parsing

```python
from src.engine.extract_pdf_content_fitz import extract_pdf_content

# Extract PDF with default settings
document = extract_pdf_content("input/sample.pdf")

# Extract with custom image directory
from src.settings import set_config_value
set_config_value('image_dir', 'custom_images/')
document = extract_pdf_content("input/sample.pdf")
```

### PSD Parsing

```python
from src.engine.extract_psd_content import extract_psd_content

# Check PSD compatibility first
from src.models.psd_validator import check_psd_compatibility
if check_psd_compatibility("input/design.psd"):
    document = extract_psd_content("input/design.psd")
else:
    print("PSD file not compatible")
```

### Custom Parser Implementation

```python
from src.engine.document_parser import DocumentParser, AssetManifest
from src.models.universal_idm import UniversalDocument

class MyFormatParser(DocumentParser):
    def can_parse(self, file_path: str) -> bool:
        return file_path.lower().endswith('.myformat')

    def parse(self, file_path: str, **kwargs) -> tuple[UniversalDocument, AssetManifest]:
        document = UniversalDocument(
            engine="my_parser",
            engine_version="1.0"
        )
        manifest = AssetManifest()

        # Implement parsing logic here
        # ...

        return document, manifest

# Register custom parser
from src.engine.document_parser import register_parser
register_parser(MyFormatParser())
```

## Document Rendering

### PDF Rendering

```python
from src.recreate_pdf_from_config import recreate_pdf_from_config

# Render document to PDF
recreate_pdf_from_config(
    config_file="layout_config.json",
    output_file="output/result.pdf"
)
```

### Image Rendering

```python
from src.engine.document_renderer import ImageRenderer, RenderConfig

# Configure rendering
config = RenderConfig(
    output_dpi=300,
    output_format="png",
    color_space="RGB"
)

# Render to images
renderer = ImageRenderer()
result = renderer.render(document, "output/page_{}.png", config)

if result.success:
    print(f"Rendered {len(result.output_paths)} images")
else:
    print(f"Rendering failed: {result.error_message}")
```

## Configuration Management

### Accessing Configuration

```python
from src.settings import CONFIG, get_config_value, set_config_value

# Get configuration values
image_dir = get_config_value('image_dir')
threshold = get_config_value('visual_diff_threshold')

# Set configuration values
set_config_value('visual_diff_threshold', 10)
set_config_value('debug_mode', True)

# Access CONFIG dictionary directly
fonts_dir = CONFIG['fonts_dir']
```

### Dynamic Path Configuration

```python
from src.settings import OutputConfig

# Configure output paths
output_config = OutputConfig(base_dir="custom_output")

# Paths are resolved dynamically
image_path = get_config_value('image_dir')  # Returns custom_output/images
```

### Environment-Specific Configuration

```python
import os
from src.settings import set_config_value

# Configure for different environments
if os.getenv('ENVIRONMENT') == 'production':
    set_config_value('debug_mode', False)
    set_config_value('visual_diff_threshold', 5)
elif os.getenv('ENVIRONMENT') == 'development':
    set_config_value('debug_mode', True)
    set_config_value('visual_diff_threshold', 10)
```

## Visual Validation

### Basic Visual Comparison

```python
from src.compare_pdfs_visual import compare_pdfs_visual

# Compare two PDF files
result = compare_pdfs_visual(
    "original.pdf",
    "rebuilt.pdf",
    output_diff="diff.png"
)

if result:
    print("PDFs are visually similar")
else:
    print("PDFs have significant differences")
```

### Advanced Visual Validation

```python
from src.engine.visual_validator import VisualValidator

# Create validator with custom settings
validator = VisualValidator(
    threshold=5,
    ssim_threshold=0.95,
    ignore_regions=[(0, 0, 100, 50)]  # Ignore header region
)

# Validate document reconstruction
is_valid = validator.validate_reconstruction(
    original_pdf="original.pdf",
    rebuilt_pdf="rebuilt.pdf"
)

print(f"Validation result: {is_valid}")
```

### Batch Visual Validation

```python
import glob
from src.engine.visual_validator import VisualValidator

validator = VisualValidator()
results = []

# Validate all PDF pairs
for original in glob.glob("originals/*.pdf"):
    rebuilt = original.replace("originals/", "rebuilt/")
    if os.path.exists(rebuilt):
        result = validator.validate_reconstruction(original, rebuilt)
        results.append((original, result))

# Summary
passed = sum(1 for _, result in results if result)
print(f"Validation: {passed}/{len(results)} passed")
```

## Error Handling

### Parsing Errors

```python
from src.engine.document_parser import parse_document, DocumentParsingError

try:
    document, manifest = parse_document("problematic.pdf")
except DocumentParsingError as e:
    print(f"Parsing failed: {e}")
    print(f"Error details: {e.details}")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Validation Errors

```python
from src.models.schema_validator import validate_schema, ValidationError

try:
    # Validate document against schema
    validate_schema(document.to_dict())
except ValidationError as e:
    print(f"Schema validation failed: {e}")
    for error in e.errors:
        print(f"  - {error}")
```

### Rendering Errors

```python
from src.engine.document_renderer import RenderingError

try:
    result = renderer.render(document, output_path, config)
    if not result.success:
        print(f"Rendering failed: {result.error_message}")
except RenderingError as e:
    print(f"Rendering error: {e}")
```

## Best Practices

### Memory Management

```python
# For large documents, process pages individually
def process_large_document(file_path):
    document, manifest = parse_document(file_path)

    for i, page in enumerate(document.document_structure):
        # Process page
        process_page(page)

        # Clear processed content to save memory
        page.layers = []

        if i % 10 == 0:  # Periodic cleanup
            import gc
            gc.collect()
```

### Error Recovery

```python
def robust_document_processing(file_paths):
    results = []

    for file_path in file_paths:
        try:
            document, manifest = parse_document(file_path)
            # Process document
            result = process_document(document)
            results.append(('success', file_path, result))

        except Exception as e:
            # Log error but continue processing
            logger.error(f"Failed to process {file_path}: {e}")
            results.append(('error', file_path, str(e)))

    return results
```

### Performance Optimization

```python
# Use batch processing for multiple files
from concurrent.futures import ThreadPoolExecutor

def process_file(file_path):
    return parse_document(file_path)

# Process files in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_file, f) for f in file_paths]
    results = [future.result() for future in futures]
```

### Configuration Management

```python
# Save and restore configuration
from src.settings import CONFIG

def with_temporary_config(**temp_config):
    """Context manager for temporary configuration changes"""
    original_config = {}

    try:
        # Save original values
        for key, value in temp_config.items():
            original_config[key] = CONFIG.get(key)
            CONFIG[key] = value

        yield

    finally:
        # Restore original values
        for key, value in original_config.items():
            if value is not None:
                CONFIG[key] = value
            elif key in CONFIG:
                del CONFIG[key]

# Usage
with with_temporary_config(debug_mode=True, visual_diff_threshold=15):
    # Process with temporary settings
    result = process_document(document)
```

## Advanced Usage

### Custom Element Types

```python
from src.models.universal_idm import Element
from dataclasses import dataclass

@dataclass
class CustomElement(Element):
    custom_property: str

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'type': 'custom',
            'custom_property': self.custom_property
        })
        return base_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            bbox=BoundingBox.from_list(data['bbox']),
            custom_property=data['custom_property']
        )
```

### Plugin System

```python
# Plugin interface
class DocumentPlugin:
    def process_document(self, document: UniversalDocument) -> UniversalDocument:
        raise NotImplementedError

    def process_element(self, element: Element) -> Element:
        raise NotImplementedError

# Example plugin
class TextNormalizationPlugin(DocumentPlugin):
    def process_document(self, document):
        for page in document.document_structure:
            for layer in page.layers:
                for i, element in enumerate(layer.content):
                    layer.content[i] = self.process_element(element)
        return document

    def process_element(self, element):
        if hasattr(element, 'text'):
            element.text = element.text.strip().title()
        return element

# Apply plugin
plugin = TextNormalizationPlugin()
processed_document = plugin.process_document(document)
```

### Custom Validation Rules

```python
from src.models.schema_validator import ValidationRule

class CustomValidationRule(ValidationRule):
    def validate(self, document: UniversalDocument) -> list[str]:
        errors = []

        # Custom validation logic
        for page in document.document_structure:
            if not page.layers:
                errors.append(f"Page {page.page_number} has no layers")

        return errors

# Register custom rule
from src.models.schema_validator import register_validation_rule
register_validation_rule(CustomValidationRule())
```

This comprehensive guide covers the major aspects of the Multi-Format Document Engine API. For specific implementation details, refer to the individual module documentation in the [API Reference](README.md).
