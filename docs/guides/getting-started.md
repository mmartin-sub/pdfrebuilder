# Getting Started Guide

Welcome to the Multi-Format Document Engine! This guide will help you get up and running quickly with document processing and layout extraction.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- [Hatch](https://hatch.pypa.io/) for environment management
- [uv](https://github.com/astral-sh/uv) for fast package management

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/multi-format-document-engine.git
cd multi-format-document-engine
```

### 2. Set Up Environment

```bash
# Create and activate the environment
hatch env create
hatch shell

# Verify installation
pdfrebuilder --help
```

### 3. Verify Installation

Test your installation with a simple command:

```bash
# Check PyMuPDF version and system info
pdfrebuilder --input input/sample.pdf --mode extract --config test_config.json
```

You should see output similar to:

```
PyMuPDF (fitz) version in use: 1.26.23
PyMuPDF (fitz) loaded from: /path/to/site-packages/fitz
Python executable: /path/to/python
[PIPELINE] Entering extract mode...
```

## Your First Document Processing

### Basic PDF Processing

Let's start with a simple PDF extraction and reconstruction:

```bash
# Extract layout from a PDF
pdfrebuilder --mode extract --input input/sample.pdf --config layout_config.json

# Recreate PDF from extracted layout
pdfrebuilder --mode generate --config layout_config.json --output output/recreated.pdf

# Full pipeline (extract + generate + visual comparison)
pdfrebuilder --mode full --input input/sample.pdf --output output/result.pdf

# Debug mode to visualize layers
pdfrebuilder --mode debug --config layout_config.json --debugoutput output/debug_layers.pdf
```

### Understanding the Modes

The system supports four main operation modes:

1. **Extract Mode** (`--mode extract`): Only extracts content to JSON
2. **Generate Mode** (`--mode generate`): Only generates PDF from existing JSON
3. **Full Mode** (`--mode full`): Complete pipeline with visual comparison
4. **Debug Mode** (`--mode debug`): Creates layer-by-layer visualization

### Working with Real Documents

Place your PDF file in the `examples/sample/` directory and process it:

```bash
# Copy your document
cp /path/to/your/document.pdf examples/sample/my_document.pdf

# Process with full pipeline
pdfrebuilder --input examples/sample/my_document.pdf --output output/my_document_recreated.pdf

# Check the results
ls -la output/
# You'll see:
# - my_document_recreated.pdf (recreated document)
# - diff.png (visual comparison)
# - layout_config.json (extracted structure)
```

### Understanding the Output

After processing, you'll find several files and directories:

1. **layout_config.json**: Structured layout data in Universal IDM format
2. **images/**: Extracted images from the document (auto-generated)
3. **fonts/auto/**: Font files downloaded automatically.
4. **fonts/manual/**: Directory for user-added custom fonts.
5. **output/**: Generated PDFs and comparison images
6. **manual_overrides.json5**: Optional manual corrections file

### Directory Structure After Processing

```
project_root/
├── layout_config.json          # Main extracted layout
├── manual_overrides.json5      # Manual corrections (optional)
├── images/                     # Extracted images
│   ├── img_abc123.jpeg
│   └── img_def456.png
├── fonts/                      # Font files
│   ├── auto/                   # Auto-downloaded fonts
│   │   └── Arial-Bold.ttf
│   └── manual/                 # Manually added fonts
│       └── Times-Roman.ttf
└── output/                     # Generated outputs
    ├── recreated.pdf           # Recreated document
    ├── diff.png               # Visual comparison
    └── debug_layers.pdf       # Debug visualization
```

### Basic Configuration Structure

The `layout_config.json` follows the Universal Document Structure Schema v1.0:

```json
{
  "version": "1.0",
  "engine": "fitz",
  "engine_version": "PyMuPDF 1.26.23",
  "metadata": {
    "format": "PDF 1.4",
    "title": "Sample Document",
    "author": "Author Name",
    "creationDate": "D:20250717183732+00'00'"
  },
  "document_structure": [
    {
      "type": "page",
      "page_number": 0,
      "size": [612.0, 792.0],
      "page_background_color": [1.0, 1.0, 1.0],
      "layers": [
        {
          "layer_id": "page_0_base_layer",
          "layer_name": "Page Content",
          "layer_type": "base",
          "bbox": [0, 0, 612.0, 792.0],
          "visibility": true,
          "opacity": 1.0,
          "blend_mode": "Normal",
          "children": [],
          "content": [
            {
              "type": "text",
              "text": "Hello World",
              "raw_text": "H e l l o   W o r l d",
              "bbox": [100, 700, 200, 720],
              "font_details": {
                "name": "Arial-Bold",
                "size": 12.0,
                "color": 0,
                "is_bold": true,
                "is_italic": false
              },
              "id": "text_0"
            },
            {
              "type": "image",
              "image_file": "./images/img_abc123.jpeg",
              "bbox": [50, 400, 250, 600],
              "id": "image_1"
            },
            {
              "type": "drawing",
              "bbox": [300, 500, 400, 550],
              "color": null,
              "fill": [0.0, 0.0, 1.0],
              "width": 1.0,
              "drawing_commands": [
                {"cmd": "rect", "bbox": [300, 500, 400, 550]}
              ],
              "id": "drawing_0"
            }
          ]
        }
      ]
    }
  ]
}
```

## Common Use Cases

### 1. Text Extraction and Modification

Extract text content and modify it programmatically:

```bash
# Extract text content only
pdfrebuilder --mode extract --input document.pdf --extract-text --no-extract-images --no-extract-drawings

# Modify text in layout_config.json or use manual overrides
# Then regenerate
pdfrebuilder --mode generate --config layout_config.json --output modified.pdf
```

**Programmatic Text Modification Example:**

```python
import json

# Load the extracted configuration
with open('layout_config.json', 'r') as f:
    config = json.load(f)

# Find and modify text elements
for page in config['document_structure']:
    for layer in page['layers']:
        for element in layer['content']:
            if element['type'] == 'text':
                # Replace specific text
                if 'old text' in element['text']:
                    element['text'] = element['text'].replace('old text', 'new text')

# Save modified configuration
with open('layout_config.json', 'w') as f:
    json.dump(config, f, indent=2)

# Regenerate PDF
# pdfrebuilder --mode generate --config layout_config.json --output modified.pdf
```

### 2. Template Mode for Complex Documents

For documents with complex graphics, use template mode to preserve visual fidelity:

```json5
// Create manual_overrides.json5
{
  "use_original_as_template": true,

  // You can still override specific elements
  "text_block_overrides": {
    "block_100_200": {
      "text": "Updated text content",
      "font": "Arial-Bold",
      "color": 0
    }
  }
}
```

```bash
# Generate with template mode
pdfrebuilder --mode generate --config layout_config.json --output templated.pdf
```

### 3. Font Management

The system automatically handles fonts, but you can customize:

```bash
# Check what fonts are being used
python -c "
import json
with open('layout_config.json') as f:
    config = json.load(f)
fonts = set()
for page in config['document_structure']:
    for layer in page['layers']:
        for element in layer['content']:
            if element['type'] == 'text':
                fonts.add(element['font_details']['name'])
print('Fonts used:', fonts)
"

# Add custom fonts to fonts/manual/
cp /path/to/custom-font.ttf fonts/manual/

# Override font mappings in manual_overrides.json5
{
  "text_fonts": {
    "ProblematicFont": "Arial.ttf",
    "CustomFont": "custom-font.ttf"
  }
}
```

### 4. Visual Validation and Comparison

Compare original and recreated documents:

```bash
# Full pipeline includes automatic visual comparison
pdfrebuilder --mode full --input original.pdf --output recreated.pdf
# Creates diff.png automatically

# Manual visual comparison
python -m pdfrebuilder.core.compare_pdfs_visual original.pdf recreated.pdf output/comparison.png

# Adjust comparison sensitivity
python -m pdfrebuilder.core.compare_pdfs_visual original.pdf recreated.pdf output/comparison.png --threshold 0.95
```

### 5. Batch Processing Multiple Documents

Process multiple documents efficiently:

```bash
# Process multiple files
for pdf in examples/sample/*.pdf; do
    basename=$(basename "$pdf" .pdf)
    pdfrebuilder --input "$pdf" --output "output/${basename}_processed.pdf"
done

# Or use the batch modification engine
python -c "
from pdfrebuilder.engine.batch_modifier import BatchModifier
from pdfrebuilder.models.universal_idm import UniversalDocument

# Load document
with open('layout_config.json') as f:
    import json
    config = json.load(f)

doc = UniversalDocument.from_dict(config)
modifier = BatchModifier()

# Batch text replacement
result = modifier.replace_text_batch(doc, [
    ('old text 1', 'new text 1'),
    ('old text 2', 'new text 2')
])

print(f'Modified {result.modified_elements} elements')
"
```

### 6. Selective Content Extraction

Extract only specific types of content:

```bash
# Extract only text (no images or drawings)
pdfrebuilder --mode extract --input document.pdf --extract-text --no-extract-images --no-extract-drawings

# Extract only images
pdfrebuilder --mode extract --input document.pdf --no-extract-text --extract-images --no-extract-drawings

# Extract everything including background drawings (for debugging)
pdfrebuilder --mode extract --input document.pdf --extract-raw-backgrounds
```

## Manual Overrides

Use `manual_overrides.json5` for corrections:

```json5
{
  // Fix text content
  "text_block_overrides": {
    "block_100_200": {
      "text": "Corrected text",
      "font": "Arial-Bold",
      "color": 0
    }
  },

  // Use template mode
  "use_original_as_template": true,

  // Custom font mappings
  "text_fonts": {
    "CustomFont": "CustomFont.ttf"
  }
}
```

## Debug Mode

For troubleshooting, use debug mode:

```python
pdfrebuilder --mode debug --config layout_config.json --debugoutput debug_layers.pdf
```

This creates a multi-page PDF showing each layer separately.

## Next Steps

Now that you have the basics working:

1. **Read the Architecture Guide**: [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
2. **Explore Advanced Features**: [docs/guides/advanced-usage.md](advanced-usage.md)
3. **Learn Batch Processing**: [docs/guides/batch-processing.md](batch-processing.md)
4. **Set Up Visual Validation**: [docs/guides/visual-validation.md](visual-validation.md)

## Troubleshooting

### Common Issues

**Issue**: "Font not found" errors
**Solution**: Check that fonts are available in `downloaded_fonts/` or system fonts

**Issue**: Layout differences in output
**Solution**: Use template mode or adjust manual overrides

**Issue**: Import errors
**Solution**: Ensure you're in the hatch environment: `hatch shell`

### Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review [API Documentation](../api/)
- Look at [Examples](../examples/)

## Performance Tips

- Use template mode for complex graphics
- Process documents in batches for efficiency
- Monitor memory usage with large documents
- Use debug mode to identify layout issues

Congratulations! You're now ready to process documents with the Multi-Format Document Engine.
