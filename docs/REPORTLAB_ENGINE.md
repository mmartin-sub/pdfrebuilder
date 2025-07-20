# ReportLab Engine Documentation

## Overview

The ReportLab Engine is an enhanced PDF rendering engine that provides better precision, proper font embedding, and licensing verification capabilities. It implements the `PDFEngineBase` interface and can be used as an alternative to the PyMuPDF (fitz) engine.

## Features

### Enhanced Capabilities

- **Font Embedding**: Proper font embedding with licensing verification
- **Transparency Support**: Full support for transparency and alpha channels
- **Vector Graphics**: Advanced vector graphics rendering
- **Rotation Support**: Text and element rotation capabilities
- **Precision Positioning**: Enhanced precision for text and element positioning

### Supported Features

| Feature | ReportLab | PyMuPDF |
|---------|-----------|---------|
| Font Embedding | ✅ | ❌ |
| Transparency | ✅ | ❌ |
| Vector Graphics | ✅ | ❌ |
| Rotation | ✅ | ❌ |
| Images | ✅ | ✅ |
| Drawings | ✅ | ✅ |
| Text | ✅ | ✅ |

## Usage

### Basic Usage

```python
from src.engine.pdf_engine_selector import get_pdf_engine
from src.models.universal_idm import UniversalDocument

# Get ReportLab engine
engine = get_pdf_engine("reportlab")

# Generate PDF
engine.generate(document_config, "output.pdf")
```

### Engine Selection

```python
from src.engine.pdf_engine_selector import get_engine_selector

# Get engine selector
selector = get_engine_selector()

# List available engines
engines = selector.list_available_engines()
print(f"Available engines: {list(engines.keys())}")

# Compare engines
comparison = selector.compare_engines("reportlab", "pymupdf")
print(f"Feature differences: {comparison['differences']}")
```

### Font Validation

```python
from src.engine.reportlab_engine import ReportLabEngine

engine = ReportLabEngine()

# Validate font licensing
result = engine.validate_font_licensing("Helvetica")
print(f"Font available: {result['available']}")
print(f"Font embeddable: {result['embeddable']}")
print(f"Status: {result['status']}")
```

## CLI Testing

The ReportLab engine includes a comprehensive CLI testing interface:

```bash
# Show engine information
hatch run python -m src.cli.reportlab_test_cli info

# Test font validation
hatch run python -m src.cli.reportlab_test_cli fonts

# Generate test PDF
hatch run python -m src.cli.reportlab_test_cli generate --output test.pdf

# Compare engines
hatch run python -m src.cli.reportlab_test_cli compare
```

## Architecture

### Engine Components

1. **ReportLabEngine**: Main engine class implementing PDF generation
2. **PDFEngineSelector**: Factory for selecting and managing engines
3. **FontValidator**: Font availability and licensing verification
4. **Canvas Rendering**: Direct canvas-based rendering for precision

### Key Methods

#### ReportLabEngine

- `generate()`: Generate PDF from universal document
- `validate_font_licensing()`: Check font availability and licensing
- `get_engine_info()`: Get engine capabilities and information
- `_render_page_canvas()`: Render page using ReportLab canvas
- `_render_text_element_canvas()`: Render text elements with precision

#### PDFEngineSelector

- `get_engine()`: Get specific engine instance
- `get_default_engine()`: Get default engine (ReportLab)
- `list_available_engines()`: List all available engines
- `compare_engines()`: Compare engine capabilities
- `validate_engine_config()`: Validate engine configuration

## Configuration

### Engine Configuration

```python
config = {
    "default_engine": "reportlab",
    "reportlab": {
        "compression": 1,
        "page_mode": "portrait",
        "embed_fonts": True
    }
}
```

### Font Configuration

The engine automatically searches for fonts in the following locations:

- `downloaded_fonts/` directory
- System font directories
- Custom font paths

Supported font formats:

- TrueType (.ttf)
- OpenType (.otf)
- Web Open Font Format (.woff)

## Testing

### Running Tests

```bash
# Run all ReportLab engine tests
hatch run python -m pytest tests/test_reportlab_engine.py -v

# Run specific test
hatch run python -m pytest tests/test_reportlab_engine.py::TestReportLabEngine::test_pdf_generation -v
```

### Test Coverage

The test suite covers:

- Engine initialization and configuration
- Font validation and licensing
- PDF generation functionality
- Engine selector integration
- Engine comparison capabilities
- Document serialization
- Error handling
- Color conversion

## Integration

### With Batch Modification

The ReportLab engine integrates with the batch modification system:

```python
from src.engine.batch_modifier import BatchModifier
from src.engine.reportlab_engine import ReportLabEngine

# Create batch modifier with ReportLab engine
modifier = BatchModifier()
engine = ReportLabEngine()

# Process document
result = modifier.variable_substitution(document, variables)

# Generate PDF with ReportLab
engine.generate(result.modified_document, "output.pdf")
```

### With Visual Validation

```python
from src.engine.visual_validator import VisualValidator
from src.engine.reportlab_engine import ReportLabEngine

# Generate PDF with ReportLab
engine = ReportLabEngine()
engine.generate(document, "generated.pdf")

# Validate against original
validator = VisualValidator()
result = validator.validate("original.pdf", "generated.pdf")
```

## Performance

### Advantages

- **Precision**: Enhanced positioning and rendering precision
- **Font Quality**: Better font embedding and rendering
- **Transparency**: Full support for transparency effects
- **Vector Graphics**: Advanced vector graphics capabilities

### Considerations

- **Memory Usage**: Higher memory usage compared to PyMuPDF
- **Processing Time**: Slightly slower for simple documents
- **Font Loading**: Requires font files for custom fonts

## Troubleshooting

### Common Issues

1. **Font Not Found**

   ```
   WARNING: Font file not found for: CustomFont
   ```

   Solution: Ensure font files are in the `downloaded_fonts/` directory

2. **Font Licensing Issues**

   ```
   Status: restricted
   Reason: Font not available or restricted
   ```

   Solution: Use system fonts or properly licensed fonts

3. **Canvas Rendering Errors**

   ```
   Error rendering text element: ...
   ```

   Solution: Check text content and positioning parameters

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

engine = ReportLabEngine()
engine.generate(document, "output.pdf")
```

## Future Enhancements

### Planned Features

1. **Advanced Vector Graphics**: Enhanced vector graphics support
2. **Multi-page Documents**: Improved multi-page document handling
3. **Template System**: Integration with template management
4. **Performance Optimization**: Memory and processing optimizations
5. **Additional Font Formats**: Support for more font formats

### Extensibility

The ReportLab engine is designed for extensibility:

```python
class CustomReportLabEngine(ReportLabEngine):
    def _render_custom_element(self, canvas, element):
        # Custom rendering logic
        pass
```

## Examples

### Complete Example

```python
from src.engine.pdf_engine_selector import get_pdf_engine
from src.models.universal_idm import (
    BoundingBox, Color, DocumentMetadata, FontDetails,
    Layer, LayerType, PageUnit, TextElement, UniversalDocument
)

# Create test document
text_element = TextElement(
    id="test",
    bbox=BoundingBox(50, 50, 550, 100),
    raw_text="Hello ReportLab!",
    text="Hello ReportLab!",
    font_details=FontDetails(name="Helvetica", size=24, color=Color(0, 0, 0)),
    z_index=1,
)

layer = Layer(
    layer_id="main",
    layer_name="Main",
    layer_type=LayerType.BASE,
    bbox=BoundingBox(0, 0, 600, 400),
    visibility=True,
    opacity=1.0,
    blend_mode="normal",
    children=[],
    content=[text_element],
)

page = PageUnit(
    size=(600, 400),
    background_color=None,
    layers=[layer],
    page_number=0,
)

document = UniversalDocument(
    metadata=DocumentMetadata(format="pdf", title="Test"),
    document_structure=[page],
)

# Generate PDF with ReportLab
engine = get_pdf_engine("reportlab")
engine.generate(document.to_dict(), "tests/output/test_reportlab.pdf")
```

This example demonstrates the complete workflow from document creation to PDF generation using the ReportLab engine.
