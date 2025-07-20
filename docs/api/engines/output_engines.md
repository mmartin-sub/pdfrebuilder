# Output Engines API Reference

This document provides comprehensive API reference for all output engines in the Multi-Format Document Engine.

## Overview

Output engines are responsible for rendering the Universal Document Structure into various output formats. Each engine implements the `PDFRenderingEngine` interface and provides format-specific rendering capabilities.

## PDFRenderingEngine Interface

All output engines implement the following interface:

```python
class PDFRenderingEngine(ABC):
    @abstractmethod
    def initialize(self, config: dict) -> None:
        """Initialize the engine with configuration"""
        pass

    @abstractmethod
    def create_document(self, metadata: dict) -> Any:
        """Create a new document with the given metadata"""
        pass

    @abstractmethod
    def add_page(self, document: Any, size: Tuple[float, float],
                 background_color: Optional[Color] = None) -> Any:
        """Add a new page to the document"""
        pass

    @abstractmethod
    def render_element(self, page: Any, element: dict,
                      resources: dict) -> dict:
        """Render an element on the page"""
        pass

    @abstractmethod
    def finalize_document(self, document: Any, output_path: str) -> None:
        """Finalize and save the document"""
        pass

    @abstractmethod
    def get_engine_info(self) -> dict:
        """Get information about the engine"""
        pass
```

## Available Output Engines

### ReportLab Engine

**Engine Name**: `reportlab`
**Output Formats**: PDF
**Implementation**: `ReportLabEngine`

#### Configuration

```python
"engines": {
    "output": {
        "reportlab": {
            "compression": 1,
            "page_mode": "portrait",
            "embed_fonts": True,
            "color_space": "RGB",
            "output_dpi": 300
        }
    }
}
```

#### Features

- **Precise Text Layout**: Exact font positioning and spacing
- **Font Embedding**: Comprehensive font embedding with licensing checks
- **Vector Graphics**: High-quality vector shape rendering
- **Compression**: Configurable PDF compression levels
- **Color Management**: RGB and CMYK color space support

#### Strengths

- Precise text layout control
- Extensive font support
- Smaller file sizes
- Professional PDF features

#### Limitations

- Slower for complex vector graphics
- Limited image format support

#### Usage Example

```python
from src.engine.pdf_engines import ReportLabEngine

engine = ReportLabEngine()
engine.initialize({
    "compression": 1,
    "embed_fonts": True,
    "output_dpi": 300
})

document = engine.create_document({"title": "Test Document"})
page = engine.add_page(document, (612, 792))
engine.render_element(page, text_element, resources)
engine.finalize_document(document, "output.pdf")
```

### PyMuPDF Engine

**Engine Name**: `pymupdf` or `fitz`
**Output Formats**: PDF
**Implementation**: `PyMuPDFEngine`

#### Configuration

```python
"engines": {
    "output": {
        "pymupdf": {
            "overlay_mode": False,
            "annotation_mode": "ignore",
            "compression": "flate",
            "embed_fonts": True
        }
    }
}
```

#### Features

- **Fast Rendering**: High-performance document generation
- **Vector Graphics**: Excellent vector graphics support
- **Image Handling**: Superior image processing capabilities
- **Overlay Mode**: Template-based document generation
- **Annotation Support**: PDF annotation preservation and creation

#### Strengths

- Fast rendering performance
- Excellent vector graphics support
- Good image handling
- Template overlay capabilities

#### Limitations

- Less precise text layout control
- Larger file sizes in some cases

#### Usage Example

```python
from src.engine.pdf_engines import PyMuPDFEngine

engine = PyMuPDFEngine()
engine.initialize({
    "overlay_mode": False,
    "compression": "flate",
    "embed_fonts": True
})

document = engine.create_document({"title": "Test Document"})
page = engine.add_page(document, (612, 792))
engine.render_element(page, text_element, resources)
engine.finalize_document(document, "output.pdf")
```

## Engine Selection

### Automatic Selection

The system uses the configured default engine:

```python
from src.engine.pdf_engines import PDFEngineSelector

selector = PDFEngineSelector()
engine = selector.get_default_engine(config)
```

### Manual Selection

You can manually select a specific engine:

```python
from src.engine.pdf_engines import PDFEngineSelector

selector = PDFEngineSelector()
engine = selector.get_engine("reportlab", config)
```

### Command Line Selection

Use the `--engine` parameter:

```bash
python main.py --mode generate --engine reportlab --output document.pdf
```

### Configuration-Based Selection

Set the default engine in configuration:

```python
from src.settings import set_nested_config_value

# Set default output engine
set_nested_config_value('engines.output.default', 'reportlab')
```

## Engine Comparison

| Feature | ReportLab | PyMuPDF |
|---------|-----------|---------|
| Text Layout Precision | Excellent | Good |
| Vector Graphics | Good | Excellent |
| Image Handling | Limited | Excellent |
| Font Support | Extensive | Good |
| File Size | Smaller | Larger |
| Rendering Speed | Slower | Faster |
| Template Support | Limited | Excellent |
| Professional Features | Excellent | Good |

## Performance Metrics

All engines provide performance metrics:

```python
from src.engine.pdf_engines import PDFEngineSelector

selector = PDFEngineSelector()
engine = selector.get_engine("reportlab", config)

# Render document
start_time = time.time()
engine.render_document(document, "output.pdf")
render_time = time.time() - start_time

# Get engine info including performance data
engine_info = engine.get_engine_info()
print(f"Rendering time: {render_time:.2f}s")
print(f"Engine info: {engine_info}")
```

## Element Rendering

### Text Elements

All engines support consistent text element rendering:

```python
text_element = {
    "type": "text",
    "text": "Hello World",
    "font_details": {
        "name": "Arial",
        "size": 12,
        "color": [0, 0, 0],
        "is_bold": False,
        "is_italic": False
    },
    "bbox": [100, 100, 200, 120],
    "align": 0
}

engine.render_element(page, text_element, resources)
```

### Image Elements

```python
image_element = {
    "type": "image",
    "image_file": "path/to/image.png",
    "bbox": [50, 50, 150, 150]
}

engine.render_element(page, image_element, resources)
```

### Drawing Elements

```python
drawing_element = {
    "type": "drawing",
    "drawing_commands": [
        {"cmd": "M", "pts": [100, 100]},
        {"cmd": "L", "pts": [200, 100]},
        {"cmd": "L", "pts": [200, 200]},
        {"cmd": "H"}
    ],
    "color": [0, 0, 0],
    "fill": [1, 0, 0],
    "width": 2.0
}

engine.render_element(page, drawing_element, resources)
```

## Error Handling

All engines provide consistent error handling:

```python
from src.engine.pdf_engines import (
    EngineError,
    EngineNotFoundError,
    RenderingError
)

try:
    engine = selector.get_engine("unknown_engine", config)
except EngineNotFoundError as e:
    print(f"Engine not found: {e}")

try:
    engine.render_element(page, element, resources)
except RenderingError as e:
    print(f"Rendering error: {e}")
```

## Configuration Schema

### ReportLab Configuration

```json
{
  "compression": {
    "type": "integer",
    "minimum": 0,
    "maximum": 9,
    "default": 1
  },
  "page_mode": {
    "type": "string",
    "enum": ["portrait", "landscape"],
    "default": "portrait"
  },
  "embed_fonts": {
    "type": "boolean",
    "default": true
  },
  "color_space": {
    "type": "string",
    "enum": ["RGB", "CMYK"],
    "default": "RGB"
  },
  "output_dpi": {
    "type": "integer",
    "minimum": 72,
    "maximum": 600,
    "default": 300
  }
}
```

### PyMuPDF Configuration

```json
{
  "overlay_mode": {
    "type": "boolean",
    "default": false
  },
  "annotation_mode": {
    "type": "string",
    "enum": ["preserve", "ignore", "remove"],
    "default": "ignore"
  },
  "compression": {
    "type": "string",
    "enum": ["none", "flate", "lzw"],
    "default": "flate"
  },
  "embed_fonts": {
    "type": "boolean",
    "default": true
  }
}
```

## Best Practices

### Engine Selection Guidelines

1. **ReportLab**: Choose for precise text layout, professional documents, smaller file sizes
2. **PyMuPDF**: Choose for fast rendering, complex graphics, template-based generation

### Performance Optimization

1. **Caching**: Enable element caching for repeated content
2. **Parallel Processing**: Use parallel rendering for independent pages
3. **Memory Management**: Configure appropriate memory limits
4. **Asset Optimization**: Optimize images and fonts before rendering

### Quality Assurance

1. **Visual Validation**: Always validate output against original
2. **Font Verification**: Ensure all fonts are properly embedded
3. **Color Accuracy**: Verify color reproduction across engines
4. **Cross-Platform Testing**: Test on different operating systems

## Troubleshooting

### Common Issues

1. **Font Embedding Failures**: Check font licensing and availability
2. **Memory Issues**: Reduce document complexity or increase limits
3. **Rendering Errors**: Verify element structure and resources
4. **Performance Issues**: Choose appropriate engine for use case

### Debug Mode

Enable debug mode for detailed rendering information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

engine.render_document(document, "output.pdf")
```

### Performance Profiling

Profile engine performance:

```python
import cProfile

def render_document():
    engine.render_document(document, "output.pdf")

cProfile.run('render_document()')
```

## Migration Guide

### Switching Engines

When switching between engines:

1. **Test Thoroughly**: Visual validation is essential
2. **Update Configuration**: Adjust engine-specific settings
3. **Performance Testing**: Benchmark both engines
4. **Gradual Migration**: Migrate document types incrementally

### Backward Compatibility

- All engines maintain API compatibility
- Configuration changes are backward compatible
- Existing documents continue to work

## See Also

- [Input Engines API](input_engines.md)
- [Configuration Reference](../reference/configuration.md)
- [Performance Guide](../guides/performance.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
