# Output Engine Selection Guide

This guide provides detailed information about the output engine selection system, including configuration, performance optimization, and troubleshooting.

## Overview

The Multi-Format Document Engine now supports a sophisticated engine selection system that allows you to choose between different PDF rendering backends based on your specific needs. Each engine has unique characteristics and is optimized for different use cases.

## Available Output Engines

### ReportLab Engine (`reportlab`)

**Best for**: Professional documents, precise text layout, font-heavy content

**Key Features**:

- Excellent font embedding and subsetting capabilities
- Precise coordinate positioning and text layout
- Smaller output file sizes through advanced compression
- Professional-grade typography control
- Extensive configuration options

**Ideal Use Cases**:

- Business reports and invoices
- Text-heavy documents
- Professional publications
- Documents requiring precise font control
- Applications where file size matters

**Performance Characteristics**:

- Slower rendering for complex vector graphics
- Lower memory usage
- Better compression ratios
- More precise text positioning

### PyMuPDF Engine (`pymupdf` or `fitz`)

**Best for**: Fast rendering, complex graphics, image-heavy documents

**Key Features**:

- Very fast rendering performance
- Excellent vector graphics support
- Superior image handling capabilities
- Built-in template overlay support
- Good annotation handling

**Ideal Use Cases**:

- Graphics-heavy documents
- Image processing workflows
- Template-based PDF generation
- High-volume document processing
- Applications where speed is critical

**Performance Characteristics**:

- Fast rendering for all content types
- Higher memory usage
- Larger output files in some cases
- Excellent graphics performance

## Engine Selection Methods

### 1. Command Line Interface

The most straightforward way to select an engine:

```bash
# Use ReportLab engine
python main.py --output-engine reportlab --input document.pdf --output result.pdf

# Use PyMuPDF engine
python main.py --output-engine pymupdf --input document.pdf --output result.pdf

# Use automatic selection (uses configured default)
python main.py --output-engine auto --input document.pdf --output result.pdf
```

### 2. Configuration Files

Create a comprehensive engine configuration file:

```json
{
  "default_engine": "reportlab",
  "reportlab": {
    "compression": 1,
    "page_mode": "portrait",
    "embed_fonts": true,
    "font_subsetting": true,
    "image_compression": "jpeg",
    "color_space": "rgb",
    "precision": 1.0
  },
  "pymupdf": {
    "overlay_mode": false,
    "annotation_mode": "ignore",
    "compression": "flate",
    "image_quality": 85,
    "text_rendering_mode": "fill",
    "anti_aliasing": true,
    "optimize_for_web": false
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 100,
    "parallel_rendering": false,
    "max_workers": 4
  },
  "debugging": {
    "enable_metrics": true,
    "log_rendering_details": false,
    "save_intermediate_files": false
  }
}
```

### 3. Environment Variables

Configure engines using environment variables:

```bash
# Set default engine
export PDF_ENGINE_DEFAULT=pymupdf

# Configure ReportLab settings
export PDF_ENGINE_REPORTLAB_COMPRESSION=2
export PDF_ENGINE_REPORTLAB_EMBED_FONTS=true
export PDF_ENGINE_REPORTLAB_PRECISION=1.5

# Configure PyMuPDF settings
export PDF_ENGINE_PYMUPDF_OVERLAY_MODE=false
export PDF_ENGINE_PYMUPDF_IMAGE_QUALITY=90
export PDF_ENGINE_PYMUPDF_COMPRESSION=flate
```

### 4. Programmatic API

Use the engine selection API directly in your code:

```python
from src.engine.pdf_engine_selector import get_pdf_engine, get_engine_selector
from src.engine.config_loader import load_engine_config

# Method 1: Direct engine selection
config = load_engine_config("engine_config.json")
engine = get_pdf_engine("reportlab", config)

# Method 2: Using the selector
selector = get_engine_selector()
engine = selector.get_engine("pymupdf", config)

# Method 3: Get default engine
default_engine = selector.get_default_engine(config)

# Generate PDF
engine.generate(document_config, "output.pdf", "template.pdf")
```

## Detailed Configuration Options

### ReportLab Engine Configuration

```json
{
  "reportlab": {
    "compression": 1,
    "page_mode": "portrait",
    "embed_fonts": true,
    "font_subsetting": true,
    "image_compression": "jpeg",
    "color_space": "rgb",
    "precision": 1.0
  }
}
```

**Configuration Details**:

- **compression** (0-9): Higher values = smaller files, slower processing
- **page_mode**: "portrait" or "landscape" for default orientation
- **embed_fonts**: Embeds fonts for consistent rendering across systems
- **font_subsetting**: Only includes used characters to reduce file size
- **image_compression**: "none", "jpeg", or "flate" for image handling
- **color_space**: "rgb" for screen, "cmyk" for print, "gray" for monochrome
- **precision**: Multiplier for coordinate precision (higher = more precise)

### PyMuPDF Engine Configuration

```json
{
  "pymupdf": {
    "overlay_mode": false,
    "annotation_mode": "ignore",
    "compression": "flate",
    "image_quality": 85,
    "text_rendering_mode": "fill",
    "anti_aliasing": true,
    "optimize_for_web": false
  }
}
```

**Configuration Details**:

- **overlay_mode**: Renders content over existing PDF pages
- **annotation_mode**: "preserve", "ignore", or "remove" existing annotations
- **compression**: "none", "flate", or "lzw" for PDF compression
- **image_quality**: JPEG quality from 1 (lowest) to 100 (highest)
- **text_rendering_mode**: "fill", "stroke", "fill_stroke", or "invisible"
- **anti_aliasing**: Smooths edges for better visual quality
- **optimize_for_web**: Enables fast web view optimization

### Performance Configuration

```json
{
  "performance": {
    "enable_caching": true,
    "cache_size": 100,
    "parallel_rendering": false,
    "max_workers": 4
  }
}
```

### Debugging Configuration

```json
{
  "debugging": {
    "enable_metrics": true,
    "log_rendering_details": false,
    "save_intermediate_files": false
  }
}
```

## Performance Optimization

### Choosing the Right Engine

**Use ReportLab when**:

- Text quality and precision are paramount
- Output file size is a concern
- You need extensive font control
- Processing primarily text-based documents
- Professional document standards are required
- Memory usage needs to be minimized

**Use PyMuPDF when**:

- Rendering speed is the primary concern
- Working with graphics-heavy documents
- Processing large volumes of documents
- Using template overlays or existing PDFs
- Handling complex vector graphics
- Image processing is involved

### Performance Tuning Examples

#### Speed-Optimized Configuration

```json
{
  "default_engine": "pymupdf",
  "pymupdf": {
    "compression": "none",
    "image_quality": 75,
    "anti_aliasing": false,
    "optimize_for_web": false
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 200,
    "parallel_rendering": true,
    "max_workers": 8
  }
}
```

#### Quality-Optimized Configuration

```json
{
  "default_engine": "reportlab",
  "reportlab": {
    "compression": 0,
    "embed_fonts": true,
    "font_subsetting": false,
    "image_compression": "none",
    "precision": 2.0
  },
  "pymupdf": {
    "image_quality": 100,
    "anti_aliasing": true,
    "text_rendering_mode": "fill_stroke"
  }
}
```

#### Memory-Optimized Configuration

```json
{
  "default_engine": "reportlab",
  "reportlab": {
    "compression": 9,
    "font_subsetting": true,
    "image_compression": "jpeg",
    "precision": 0.5
  },
  "performance": {
    "enable_caching": false,
    "parallel_rendering": false,
    "max_workers": 1
  }
}
```

## Performance Monitoring

### Enable Performance Metrics

```json
{
  "debugging": {
    "enable_metrics": true
  }
}
```

### Programmatic Performance Monitoring

```python
from src.engine.performance_metrics import (
    get_performance_collector,
    generate_performance_report,
    get_engine_performance_stats
)

# Get performance collector
collector = get_performance_collector()

# Generate a document to collect metrics
recreate_pdf_from_config("config.json", "output.pdf", "reportlab")

# Get latest metrics
latest_metrics = collector.get_latest_metrics()
print(f"Rendering time: {latest_metrics.duration:.3f}s")
print(f"Memory used: {latest_metrics.memory_used / 1024 / 1024:.2f}MB")
print(f"Pages processed: {latest_metrics.page_count}")
print(f"Elements rendered: {latest_metrics.element_count}")

# Get engine statistics
stats = get_engine_performance_stats("reportlab")
print(f"Average rendering time: {stats.get('avg_duration_ms', 0):.2f}ms")
print(f"Success rate: {stats.get('success_rate', 0):.2%}")

# Generate comprehensive report
report = generate_performance_report("performance_report.json")
print(f"Total runs: {report['summary']['total_runs']}")
```

### Benchmarking Different Engines

```python
from src.engine.pdf_engine_selector import get_engine_selector

selector = get_engine_selector()

# Compare engine capabilities
comparison = selector.compare_engines("reportlab", "pymupdf")

print("Engine Comparison:")
print(f"ReportLab features: {len(comparison['engine1']['features'])}")
print(f"PyMuPDF features: {len(comparison['engine2']['features'])}")
print(f"Feature differences: {len(comparison['differences'])}")

# List all available engines
engines = selector.list_available_engines()
for name, info in engines.items():
    if 'error' not in info:
        print(f"{name}: {info['engine_name']} v{info['engine_version']}")
```

## Advanced Usage

### Custom Engine Configuration Loading

```python
from src.engine.config_loader import EngineConfigLoader

loader = EngineConfigLoader()

# Load from multiple sources
config = loader.load_complete_config(
    config_file="engine_config.json",
    cli_args={"output_engine": "pymupdf"},
    env_prefix="PDF_ENGINE_"
)

# Validate configuration
validation_result = loader.validate_config(config)
if not validation_result['valid']:
    print("Configuration errors:", validation_result['errors'])

# Get engine-specific configuration
reportlab_config = loader.get_engine_config(config, "reportlab")
```

### Engine Fallback Implementation

```python
from src.engine.pdf_engine_selector import get_pdf_engine
from src.engine.pdf_rendering_engine import EngineNotFoundError, EngineInitializationError

def get_engine_with_fallback(preferred_engine, config, fallback_engine="reportlab"):
    """Get an engine with automatic fallback."""
    try:
        return get_pdf_engine(preferred_engine, config)
    except (EngineNotFoundError, EngineInitializationError) as e:
        print(f"Primary engine {preferred_engine} failed: {e}")
        print(f"Falling back to {fallback_engine}")
        return get_pdf_engine(fallback_engine, config)

# Usage
engine = get_engine_with_fallback("pymupdf", config, "reportlab")
```

### Custom Performance Metrics

```python
from src.engine.performance_metrics import measure_engine_performance

# Custom performance measurement
with measure_engine_performance("custom_engine", "1.0.0") as metrics:
    # Your custom rendering code here
    metrics['page_count'] = 5
    metrics['element_count'] = 100
    metrics['warnings'].append("Custom warning message")

    # Simulate some work
    time.sleep(0.1)

    # The context manager automatically collects timing and memory metrics
```

## Troubleshooting

### Common Issues and Solutions

#### Engine Not Found Error

```
EngineNotFoundError: Unknown PDF rendering engine: xyz. Available engines: reportlab, pymupdf
```

**Solutions**:

1. Check engine name spelling
2. Verify engine is properly installed
3. List available engines: `python -c "from src.engine.pdf_engine_selector import get_engine_selector; print(list(get_engine_selector().list_available_engines().keys()))"`

#### Engine Initialization Error

```
EngineInitializationError: Failed to initialize engine reportlab: Module not found
```

**Solutions**:

1. Install missing dependencies: `pip install reportlab`
2. Check Python environment
3. Verify configuration syntax
4. Check file permissions

#### Configuration Validation Errors

```
Configuration validation errors: ['compression must be between 0 and 9']
```

**Solutions**:

1. Check configuration values against documentation
2. Use configuration validation tools
3. Review JSON syntax for errors

#### Performance Issues

**Slow Rendering**:

1. Switch to PyMuPDF for faster rendering
2. Enable parallel processing
3. Increase cache size
4. Reduce precision settings

**High Memory Usage**:

1. Switch to ReportLab for lower memory usage
2. Disable caching
3. Reduce cache size
4. Process documents in smaller batches

**Large Output Files**:

1. Increase compression settings
2. Enable font subsetting
3. Reduce image quality
4. Use appropriate compression methods

### Debugging Tools

#### Configuration Validation

```python
from src.engine.engine_config_schema import validate_engine_config

config = {
    "reportlab": {
        "compression": 15,  # Invalid - should be 0-9
        "embed_fonts": "yes"  # Invalid - should be boolean
    }
}

result = validate_engine_config(config)
if not result['valid']:
    print("Validation errors:")
    for error in result['errors']:
        print(f"  - {error}")
```

#### Engine Availability Check

```python
from src.engine.pdf_engine_selector import get_engine_selector

selector = get_engine_selector()
engines = selector.list_available_engines()

print("Engine Availability:")
for name, info in engines.items():
    if 'error' in info:
        print(f"  {name}: ❌ {info['error']}")
    else:
        print(f"  {name}: ✅ {info['engine_name']} v{info['engine_version']}")
```

#### Performance Diagnostics

```python
from src.engine.performance_metrics import get_performance_collector

collector = get_performance_collector()

# Get engine statistics
for engine_name in ["reportlab", "pymupdf"]:
    stats = collector.get_engine_stats(engine_name)
    if stats['total_runs'] > 0:
        print(f"\n{engine_name} Statistics:")
        print(f"  Total runs: {stats['total_runs']}")
        print(f"  Success rate: {stats['success_rate']:.2%}")
        print(f"  Average time: {stats.get('avg_duration_ms', 0):.2f}ms")
        print(f"  Average memory: {stats.get('avg_memory_mb', 0):.2f}MB")
```

## Best Practices

### Configuration Management

1. **Use Version Control**: Store engine configurations in version control
2. **Environment-Specific Configs**: Use different configurations for development, staging, and production
3. **Document Decisions**: Document why specific engines and configurations were chosen
4. **Regular Reviews**: Periodically review and update configurations

### Performance Optimization

1. **Profile Your Use Case**: Test both engines with your specific documents
2. **Monitor in Production**: Collect performance metrics in production environments
3. **Benchmark Regularly**: Re-benchmark when upgrading engines or changing document types
4. **Consider Trade-offs**: Balance speed, quality, and resource usage based on requirements

### Error Handling

1. **Implement Fallbacks**: Always have a fallback engine configuration
2. **Validate Configurations**: Validate configurations before deployment
3. **Log Performance Metrics**: Monitor engine performance and errors
4. **Test Error Scenarios**: Test what happens when engines fail or are unavailable

### Maintenance

1. **Keep Engines Updated**: Regularly update engine dependencies
2. **Clean Up Resources**: Periodically clean up cached engines and temporary files
3. **Monitor Resource Usage**: Watch memory and CPU usage in production
4. **Review Configurations**: Update configurations based on new features and performance improvements

## Migration Guide

### Migrating from Single Engine

If you're currently using a single engine setup:

1. **Assess Current Usage**: Identify which engine you're currently using
2. **Create Configuration**: Set up an engine configuration file
3. **Test Both Engines**: Compare output quality and performance with your documents
4. **Update Code**: Modify your code to use the engine selection system
5. **Deploy Gradually**: Roll out changes incrementally with monitoring

### Example Migration

**Before (single engine)**:

```python
from src.pdf_engine import FitzPDFEngine

engine = FitzPDFEngine()
engine.generate(config, "output.pdf")
```

**After (engine selection)**:

```python
from src.engine.pdf_engine_selector import get_pdf_engine
from src.engine.config_loader import load_engine_config

# Load engine configuration
engine_config = load_engine_config("engine_config.json")

# Get engine (with fallback)
try:
    engine = get_pdf_engine("pymupdf", engine_config)
except Exception:
    engine = get_pdf_engine("reportlab", engine_config)

# Generate PDF
engine.generate(config, "output.pdf")
```

This comprehensive guide should help you make informed decisions about engine selection and configuration for your specific use cases.
