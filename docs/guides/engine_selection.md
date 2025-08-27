# Engine Selection Guide

This guide helps you choose the right engines for your document processing needs and configure them properly.

## Overview

The Multi-Format Document Engine supports multiple input and output engines, each with different strengths and use cases. This guide will help you understand when to use each engine and how to configure them for optimal results.

## Input Engine Selection

### PDF Documents

For PDF documents, you have one primary option:

#### PyMuPDF (Fitz) Engine

- **Best for**: All PDF processing tasks
- **Strengths**: Mature, fast, comprehensive PDF support
- **Use when**: Processing any PDF document

```python
# Example configuration for the fitz engine in your pdfrebuilder.toml
[engines.input.fitz]
extract_text = true
extract_images = true
extract_drawings = true
extract_raw_backgrounds = false
```

### PSD Documents

For PSD documents, there are two available input engines: `psd-tools` and `wand`. While both can process PSD files, the **`wand` engine is the recommended and more modern option**, offering broader format support and more advanced features.

#### psd-tools Engine (Legacy)

- **Best for**: Basic PSD processing when you cannot install system dependencies for `wand`.
- **Strengths**: Pure Python, no external dependencies.
- **Use when**: You need a simple, self-contained solution for PSD files and cannot install ImageMagick.

#### psd-tools Engine

- **Best for**: Standard PSD processing with good layer support
- **Strengths**: Pure Python, reliable layer extraction
- **Use when**: You need reliable PSD processing without external dependencies

```python
# Example configuration for the psd-tools engine in your pdfrebuilder.toml
[engines.input.psd_tools]
extract_text_layers = true
extract_image_layers = true
extract_shape_layers = true
preserve_layer_effects = true
```

#### Wand Engine (ImageMagick)

- **Best for**: Advanced image processing and multiple format support
- **Strengths**: Powerful image processing, wide format support, OCR capabilities
- **Use when**: You need advanced image processing or support for multiple formats
- **Requirements**: ImageMagick system installation

For more detailed information on the `wand` engine, see the [Image Processing with Wand](./image-processing-wand.md) guide.

```python
# Example configuration for the wand engine in your pdfrebuilder.toml
[engines.input.wand]
density = 300
use_ocr = false
tesseract_lang = "eng"
image_format = "png"
color_management = true
memory_limit_mb = 1024
```

### Decision Matrix: PSD Engines

| Factor | psd-tools | Wand |
|--------|-----------|------|
| **Installation** | Easy (pip only) | Complex (ImageMagick required) |
| **Performance** | Good | Excellent |
| **Format Support** | PSD only | PSD + many others |
| **Layer Fidelity** | Excellent | Good |
| **Text Extraction** | Good | OCR-based |
| **Memory Usage** | Moderate | Configurable |
| **Dependencies** | Minimal | System dependencies |

## Output Engine Selection

For PDF output, you have two main options:

### ReportLab Engine

- **Best for**: Professional documents, precise text layout
- **Strengths**: Excellent text control, smaller files, professional features
- **Use when**: Text-heavy documents, precise layout requirements, file size matters

```python
# Example configuration for the reportlab engine in your pdfrebuilder.toml
[engines.output.reportlab]
compression = 1
page_mode = "portrait"
embed_fonts = true
color_space = "RGB"
output_dpi = 300
```

### PyMuPDF Engine

- **Best for**: Fast rendering, complex graphics, template-based generation
- **Strengths**: High performance, excellent vector graphics, template support
- **Use when**: Graphics-heavy documents, performance is critical, using templates

```python
# Example configuration for the pymupdf engine in your pdfrebuilder.toml
[engines.output.pymupdf]
overlay_mode = false
annotation_mode = "ignore"
compression = "flate"
embed_fonts = true
```

### Decision Matrix: Output Engines

| Factor | ReportLab | PyMuPDF |
|--------|-----------|---------|
| **Text Precision** | Excellent | Good |
| **Vector Graphics** | Good | Excellent |
| **Rendering Speed** | Slower | Faster |
| **File Size** | Smaller | Larger |
| **Font Support** | Extensive | Good |
| **Template Support** | Limited | Excellent |
| **Professional Features** | Excellent | Good |

## Use Case Recommendations

### Document Type-Based Selection

#### Text-Heavy Documents

- **Input**: PyMuPDF (fitz)
- **Output**: ReportLab
- **Reason**: Precise text layout and font handling

#### Graphics-Heavy Documents

- **Input**: Wand (for PSD) or PyMuPDF (for PDF)
- **Output**: PyMuPDF
- **Reason**: Better vector graphics support and performance

#### Template-Based Generation

- **Input**: Any appropriate engine
- **Output**: PyMuPDF
- **Reason**: Excellent template overlay support

#### Multi-Format Processing

- **Input**: Wand
- **Output**: Based on content type
- **Reason**: Wide format support

### Performance-Based Selection

#### High-Volume Processing

- **Input**: PyMuPDF or Wand
- **Output**: PyMuPDF
- **Configuration**: Enable parallel processing, increase memory limits

#### Memory-Constrained Environments

- **Input**: psd-tools (for PSD) or PyMuPDF (for PDF)
- **Output**: ReportLab
- **Configuration**: Reduce memory limits, disable caching

#### Quality-Critical Applications

- **Input**: psd-tools (for PSD) or PyMuPDF (for PDF)
- **Output**: ReportLab
- **Configuration**: Enable all extraction flags, high DPI settings

## Configuration Examples

### High-Performance Setup

```python
CONFIG = {
    "engines": {
        "input": {
            "default": "auto",
            "wand": {
                "density": 300,
                "memory_limit_mb": 2048,
                "color_management": True
            }
        },
        "output": {
            "default": "pymupdf",
            "pymupdf": {
                "compression": "flate",
                "embed_fonts": True
            }
        }
    },
    "processing": {
        "enable_parallel_processing": True,
        "max_memory_mb": 4096
    }
}
```

### Quality-Focused Setup

```python
CONFIG = {
    "engines": {
        "input": {
            "default": "auto",
            "psd_tools": {
                "extract_text_layers": True,
                "extract_image_layers": True,
                "extract_shape_layers": True,
                "preserve_layer_effects": True
            }
        },
        "output": {
            "default": "reportlab",
            "reportlab": {
                "compression": 0,  # No compression for quality
                "embed_fonts": True,
                "output_dpi": 600
            }
        }
    },
    "validation": {
        "ssim_threshold": 0.99,
        "rendering_dpi": 600
    }
}
```

### Memory-Efficient Setup

```python
CONFIG = {
    "engines": {
        "input": {
            "default": "auto",
            "wand": {
                "memory_limit_mb": 512,
                "density": 150
            }
        },
        "output": {
            "default": "reportlab",
            "reportlab": {
                "compression": 9,  # Maximum compression
                "output_dpi": 150
            }
        }
    },
    "processing": {
        "max_memory_mb": 1024,
        "enable_parallel_processing": False
    }
}
```

## Command Line Usage

### Specifying Input Engine

```bash
# Use specific input engine
python main.py --input-engine wand --input design.psd

# Auto-detect engine (default)
python main.py --input design.psd
```

### Specifying Output Engine

```bash
# Use specific output engine
python main.py --engine reportlab --output document.pdf

# Use default engine
python main.py --output document.pdf
```

### Combined Engine Selection

```bash
# Specify both input and output engines
python main.py --input-engine wand --engine pymupdf --input design.psd --output document.pdf
```

## Performance Tuning

### Memory Optimization

1. **Reduce Memory Limits**: Lower memory limits for constrained environments
2. **Disable Caching**: Turn off caching if memory is limited
3. **Process in Batches**: Break large operations into smaller chunks

```python
# Memory-optimized configuration
"wand": {
    "memory_limit_mb": 256,
    "density": 150
},
"processing": {
    "max_memory_mb": 512,
    "enable_parallel_processing": False
}
```

### Speed Optimization

1. **Enable Parallel Processing**: Use multiple cores when available
2. **Increase Memory Limits**: Allow more memory for faster processing
3. **Choose Fast Engines**: Use PyMuPDF for output, Wand for input

```python
# Speed-optimized configuration
"wand": {
    "memory_limit_mb": 2048,
    "density": 300
},
"processing": {
    "max_memory_mb": 4096,
    "enable_parallel_processing": True
}
```

### Quality Optimization

1. **High DPI Settings**: Use higher resolution for better quality
2. **Preserve All Content**: Enable all extraction flags
3. **Disable Compression**: Reduce compression for better quality

```python
# Quality-optimized configuration
"reportlab": {
    "compression": 0,
    "output_dpi": 600,
    "embed_fonts": True
},
"validation": {
    "ssim_threshold": 0.99,
    "rendering_dpi": 600
}
```

## Troubleshooting Engine Issues

### Common Problems

#### Engine Not Available

```
Error: Engine 'wand' not available
```

**Solution**: Install required dependencies (ImageMagick for Wand)

#### Memory Issues

```
Error: Memory limit exceeded
```

**Solution**: Increase memory limits or reduce document complexity

#### Performance Issues

```
Warning: Processing taking too long
```

**Solution**: Switch to faster engine or enable parallel processing

### Debug Mode

Enable debug logging to troubleshoot engine issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run your processing
document = parse_document("input.psd")
```

### Engine Information

Get information about available engines:

```python
from src.engine.document_parser import get_parser_for_file
from src.engine.pdf_engines import PDFEngineSelector

# Check input engine
parser = get_parser_for_file("document.pdf")
print(f"Selected parser: {parser.__class__.__name__}")

# Check output engines
selector = PDFEngineSelector()
for engine_name in ["reportlab", "pymupdf"]:
    try:
        engine = selector.get_engine(engine_name, {})
        info = engine.get_engine_info()
        print(f"{engine_name}: {info}")
    except Exception as e:
        print(f"{engine_name}: Not available - {e}")
```

## Best Practices

1. **Test Both Options**: Always test both engines for your use case
2. **Monitor Performance**: Track processing time and memory usage
3. **Validate Output**: Use visual validation to ensure quality
4. **Document Choices**: Document your engine selection rationale
5. **Plan for Scale**: Consider performance at production scale
6. **Keep Fallbacks**: Have backup engine configurations ready

## Migration Between Engines

When switching engines:

1. **Backup Current Setup**: Save working configurations
2. **Test Incrementally**: Start with small test documents
3. **Compare Results**: Use visual validation to compare outputs
4. **Update Documentation**: Document the changes and reasons
5. **Monitor Production**: Watch for issues after deployment

## See Also

- [Input Engines API](../api/engines/input_engines.md)
- [Output Engines API](../api/engines/output_engines.md)
- [Configuration Reference](../reference/configuration.md)
- [Performance Guide](performance.md)
- [Troubleshooting Guide](troubleshooting.md)
