# Input Engines API Reference

This document provides comprehensive API reference for all input engines in the Multi-Format Document Engine.

## Overview

Input engines are responsible for parsing different document formats and converting them into the Universal Document Structure. Each engine implements the `DocumentParser` interface and provides format-specific extraction capabilities.

## DocumentParser Interface

All input engines implement the following interface:

```python
class DocumentParser(ABC):
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        pass

    @abstractmethod
    def parse(self, file_path: str, extraction_flags: Optional[Dict[str, bool]] = None) -> UniversalDocument:
        """Parse document into Universal IDM"""
        pass

    @abstractmethod
    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        """Extract and save images, fonts, and other assets"""
        pass
```

## Available Input Engines

### PDF Engine (PyMuPDF/Fitz)

**Engine Name**: `fitz`
**Supported Formats**: PDF
**Implementation**: `PDFParser`

#### Configuration

```python
"engines": {
    "input": {
        "fitz": {
            "extract_text": True,
            "extract_images": True,
            "extract_drawings": True,
            "extract_raw_backgrounds": False
        }
    }
}
```

#### Features

- **Text Extraction**: Full font information, positioning, and styling
- **Image Extraction**: High-resolution image extraction with metadata
- **Vector Graphics**: Complex shape extraction and conversion
- **Metadata**: Document properties and creation information

#### Usage Example

```python
from pdfrebuilder.engine.document_parser import PDFParser

# Initialize the parser
parser = PDFParser()

# Check if the parser can handle the file
if parser.can_parse("document.pdf"):
    # Define extraction flags
    flags = {
        "extract_text": True,
        "extract_images": True,
        "extract_drawings": True
    }
    # Parse the document
    document = parser.parse("document.pdf", extraction_flags=flags)
```

### PSD Engine (psd-tools) (Legacy)

**Engine Name**: `psd-tools`
**Supported Formats**: PSD, PSB
**Implementation**: `PSDParser`

**Note:** While `psd-tools` is available for processing PSD files, the **`wand` engine is the recommended and more modern option**. It offers broader format support and more advanced features.

#### Configuration

```python
"engines": {
    "input": {
        "psd_tools": {
            "extract_text_layers": True,
            "extract_image_layers": True,
            "extract_shape_layers": True,
            "preserve_layer_effects": True
        }
    }
}
```

#### Features

- **Layer Hierarchy**: Complete layer structure with groups and nesting
- **Layer Properties**: Visibility, opacity, blend modes, and positioning
- **Text Layers**: Font information and text content extraction
- **Image Layers**: Raster content with transparency and masks
- **Shape Layers**: Vector shapes and paths
- **Layer Effects**: Drop shadows, bevels, and other effects

#### Usage Example

```python
from pdfrebuilder.engine.document_parser import PSDParser

# Initialize the parser
parser = PSDParser()

# Check if the parser can handle the file
if parser.can_parse("design.psd"):
    # Define extraction flags
    flags = {
        "extract_text_layers": True,
        "extract_image_layers": True,
        "extract_shape_layers": True
    }
    # Parse the document
    document = parser.parse("design.psd", extraction_flags=flags)
```

### Wand Engine (Python-Wand/ImageMagick)

**Engine Name**: `wand`
**Supported Formats**: PSD, PSB, TIFF, AI, XCF, SVG, and other formats supported by ImageMagick.
**Implementation**: `WandParser`

#### Configuration

```python
"engines": {
    "input": {
        "wand": {
            "density": 300,
            "use_ocr": False,
            "tesseract_lang": "eng",
            "image_format": "png",
            "color_management": True,
            "memory_limit_mb": 1024
        }
    }
}
```

#### Features

- **Multi-Format Support**: Wide range of image formats
- **Color Management**: Advanced color profile handling
- **OCR Integration**: Optional text extraction via Tesseract
- **Image Enhancement**: Deskewing, noise reduction, and optimization
- **Memory Management**: Configurable memory limits and streaming

#### Usage Example

```python
from pdfrebuilder.engine.document_parser import WandParser

# Initialize the parser
parser = WandParser()

# Check if the parser can handle the file
if parser.can_parse("design.psd"):
    # Define extraction flags
    flags = {
        "use_ocr": True,
        "tesseract_lang": "eng"
    }
    # Parse the document
    document = parser.parse("design.psd", extraction_flags=flags)
```

## Engine Selection

### Automatic Selection

The system can automatically select the appropriate engine based on file format:

```python
from src.engine.document_parser import parse_document

# Automatically selects the right engine
document = parse_document("document.pdf")
```

### Manual Selection

You can also manually select a specific engine:

```python
from src.engine.document_parser import get_parser_for_file

parser = get_parser_for_file("document.pdf")
if parser:
    document = parser.parse("document.pdf")
```

### Configuration-Based Selection

Set the default engine in configuration:

```python
from src.settings import set_nested_config_value

# Set default input engine
set_nested_config_value('engines.input.default', 'fitz')
```

## Extraction Flags

All engines support extraction flags to control what content is extracted:

| Flag | Description | Default |
|------|-------------|---------|
| `extract_text` | Extract text elements | `True` |
| `extract_images` | Extract image elements | `True` |
| `extract_drawings` | Extract vector graphics | `True` |
| `extract_raw_backgrounds` | Extract background elements | `False` |
| `extract_text_layers` | Extract text layers (PSD) | `True` |
| `extract_image_layers` | Extract image layers (PSD) | `True` |
| `extract_shape_layers` | Extract shape layers (PSD) | `True` |
| `preserve_layer_effects` | Preserve layer effects (PSD) | `True` |

## Asset Management

All engines provide asset extraction capabilities through the `AssetManifest` class:

```python
from src.engine.document_parser import AssetManifest

# Extract assets
manifest = parser.extract_assets("document.pdf", "output/assets/")

# Access extracted assets
for image in manifest.images:
    print(f"Image: {image['path']}")

for font in manifest.fonts:
    print(f"Font: {font['font_name']} at {font['path']}")
```

## Error Handling

All engines provide consistent error handling:

```python
try:
    document = parse_document("document.pdf")
except ValueError as e:
    print(f"Unsupported format: {e}")
except NotImplementedError as e:
    print(f"Engine not available: {e}")
except Exception as e:
    print(f"Parsing error: {e}")
```

## Performance Considerations

### Memory Usage

- Configure memory limits for resource-intensive engines
- Use streaming processing for large documents
- Enable garbage collection for batch processing

### Processing Speed

- Choose the appropriate engine for your use case
- Use extraction flags to limit processing to required content
- Enable parallel processing when available

### Caching

- Engines support asset caching for improved performance
- Font metrics are cached across operations
- Template reuse for similar documents

## Best Practices

1. **Engine Selection**: Choose the most appropriate engine for your format
2. **Extraction Flags**: Only extract the content you need
3. **Error Handling**: Always handle engine-specific errors
4. **Resource Management**: Configure appropriate memory limits
5. **Asset Organization**: Use consistent asset extraction patterns
6. **Performance Monitoring**: Monitor memory usage and processing time

## Troubleshooting

### Common Issues

1. **Engine Not Available**: Install required dependencies
2. **Memory Issues**: Reduce memory limits or use streaming
3. **Format Not Supported**: Check engine capabilities
4. **Extraction Failures**: Verify file integrity and format

### Debug Mode

Enable debug mode for detailed extraction information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

document = parse_document("document.pdf")
```

## See Also

- [Output Engines API](output_engines.md)
- [Configuration Reference](../reference/configuration.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
