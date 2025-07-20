# Engine Configuration Examples

This directory contains example configurations for different use cases and optimization scenarios.

## Available Configurations

### 1. Balanced Configuration (`balanced.json`)

- **Use Case**: General-purpose document processing
- **Characteristics**: Good balance of speed, quality, and resource usage
- **Best For**: Production environments with mixed content types
- **Engine**: ReportLab (default)

```bash
python main.py --config examples/engine_configurations/balanced.json
```

### 2. Speed Optimized (`speed_optimized.json`)

- **Use Case**: High-volume batch processing
- **Characteristics**: Maximum rendering speed, reduced quality settings
- **Best For**: Processing large numbers of documents quickly
- **Engine**: PyMuPDF (default)

```bash
python main.py --config examples/engine_configurations/speed_optimized.json
```

### 3. Quality Optimized (`quality_optimized.json`)

- **Use Case**: Professional document generation
- **Characteristics**: Maximum quality, no compression, high precision
- **Best For**: Professional reports, publications, archival documents
- **Engine**: ReportLab (default)

```bash
python main.py --config examples/engine_configurations/quality_optimized.json
```

### 4. Memory Optimized (`memory_optimized.json`)

- **Use Case**: Resource-constrained environments
- **Characteristics**: Minimal memory usage, maximum compression
- **Best For**: Embedded systems, cloud functions, limited memory environments
- **Engine**: ReportLab (default)

```bash
python main.py --config examples/engine_configurations/memory_optimized.json
```

## Configuration Structure

Each configuration file contains the following sections:

### Engine Selection

```json
{
  "default_engine": "reportlab",  // or "pymupdf"
  "description": "Human-readable description",
  "use_case": "Intended use case"
}
```

### ReportLab Engine Settings

```json
{
  "reportlab": {
    "compression": 3,           // PDF compression level (0-9)
    "page_mode": "portrait",    // Page orientation
    "embed_fonts": true,        // Font embedding
    "font_subsetting": true,    // Font subsetting
    "image_compression": "jpeg", // Image compression method
    "color_space": "rgb",       // Color space
    "precision": 1.0           // Coordinate precision
  }
}
```

### PyMuPDF Engine Settings

```json
{
  "pymupdf": {
    "overlay_mode": false,           // Overlay rendering
    "annotation_mode": "ignore",     // Annotation handling
    "compression": "flate",          // PDF compression
    "image_quality": 85,             // JPEG quality
    "text_rendering_mode": "fill",   // Text rendering
    "anti_aliasing": true,           // Anti-aliasing
    "optimize_for_web": false        // Web optimization
  }
}
```

### Performance Settings

```json
{
  "performance": {
    "enable_caching": true,      // Engine caching
    "cache_size": 100,           // Cache size
    "parallel_rendering": false, // Parallel processing
    "max_workers": 4            // Worker threads
  }
}
```

### Debugging Settings

```json
{
  "debugging": {
    "enable_metrics": true,           // Performance metrics
    "log_rendering_details": false,   // Detailed logging
    "save_intermediate_files": false  // Save intermediate files
  }
}
```

## Usage Examples

### Using Configuration Files

```bash
# Use a specific configuration
python main.py --config examples/engine_configurations/speed_optimized.json --input document.pdf

# Override engine selection
python main.py --config examples/engine_configurations/balanced.json --output-engine pymupdf --input document.pdf
```

### Programmatic Usage

```python
from src.engine.config_loader import load_engine_config
from src.engine.pdf_engine_selector import get_pdf_engine

# Load configuration
config = load_engine_config("examples/engine_configurations/quality_optimized.json")

# Get engine
engine = get_pdf_engine(config['default_engine'], config)

# Generate PDF
engine.generate(document_config, "output.pdf")
```

### Environment Variable Override

```bash
# Override default engine via environment
export PDF_ENGINE_DEFAULT=pymupdf
python main.py --config examples/engine_configurations/balanced.json

# Override specific settings
export PDF_ENGINE_REPORTLAB_COMPRESSION=5
export PDF_ENGINE_PYMUPDF_IMAGE_QUALITY=95
python main.py --config examples/engine_configurations/balanced.json
```

## Performance Comparison

| Configuration | Speed | Quality | Memory | File Size | Use Case |
|---------------|-------|---------|--------|-----------|----------|
| Speed Optimized | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Batch processing |
| Quality Optimized | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | Professional docs |
| Memory Optimized | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Constrained environments |
| Balanced | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | General purpose |

## Customization

To create your own configuration:

1. Copy one of the existing configurations as a starting point
2. Modify the settings based on your requirements
3. Test with your specific documents
4. Monitor performance and adjust as needed

### Custom Configuration Template

```json
{
  "description": "Your custom configuration",
  "use_case": "Your specific use case",
  "default_engine": "reportlab",
  "reportlab": {
    "compression": 1,
    "embed_fonts": true,
    "precision": 1.0
  },
  "pymupdf": {
    "image_quality": 85,
    "anti_aliasing": true
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 100
  },
  "debugging": {
    "enable_metrics": true
  }
}
```

## Troubleshooting

### Configuration Validation

```python
from src.engine.engine_config_schema import validate_engine_config

# Load and validate configuration
with open("your_config.json") as f:
    config = json.load(f)

result = validate_engine_config(config)
if not result['valid']:
    print("Configuration errors:", result['errors'])
```

### Performance Testing

```python
from examples.engine_selection_examples import example_3_performance_comparison

# Run performance comparison with your configuration
example_3_performance_comparison()
```

## See Also

- [Engine Selection Guide](../../docs/guides/output_engine_selection.md)
- [Configuration Reference](../../docs/reference/configuration.md)
- [Performance Guide](../../docs/guides/performance.md)
- [API Documentation](../../docs/api/engines/output_engines.md)
