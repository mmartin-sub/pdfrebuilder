# Multi-Format Document Engine Usage Examples

This document provides practical examples for using the Multi-Format Document Engine in various scenarios, from basic document processing to advanced programmatic modifications.

## Table of Contents

1. [Basic Document Processing](#basic-document-processing)
2. [Format-Specific Examples](#format-specific-examples)
3. [Visual Validation](#visual-validation)
4. [Font Management](#font-management)
5. [Template-Based Generation](#template-based-generation)
6. [Batch Processing](#batch-processing)
7. [Advanced Customization](#advanced-customization)
8. [Error Handling](#error-handling)
9. [Batch Modification Engine](#batch-modification-engine)

## Basic Document Processing

### Extract and Rebuild PDF

```bash
# Full pipeline: extract layout and rebuild PDF
hatch run python main.py --input input/document.pdf --output output/rebuilt.pdf

# With debug visualization
hatch run python main.py --input input/document.pdf --output output/rebuilt.pdf \
  --debugoutput output/debug_layers.pdf
```

### Extract Only (Create Universal IDM)

```bash
# Extract document structure to JSON
hatch run python main.py --mode extract --input input/document.pdf --config layout.json

# Extract with specific features
hatch run python main.py --mode extract --input input/document.pdf --config layout.json \
  --extract-text --no-extract-images --extract-drawings
```

### Generate from Configuration

```bash
# Generate PDF from existing configuration
hatch run python main.py --mode generate --config layout.json --output output/result.pdf

# Generate with custom settings
hatch run python main.py --mode generate --config layout.json --output output/result.pdf \
  --log-level DEBUG
```

## Format-Specific Examples

### PDF Processing

```python
from src.engine.document_parser import PDFParser
from src.models.universal_idm import UniversalDocument

# Initialize PDF parser
parser = PDFParser()

# Parse PDF with all features
document = parser.parse("input/report.pdf", {
    "include_text": True,
    "include_images": True,
    "include_drawings": True,
    "include_raw_background_drawings": False
})

# Access document structure
print(f"Document has {len(document.document_structure)} pages")
for i, page in enumerate(document.document_structure):
    print(f"Page {i}: {len(page.layers[0].content)} elements")

    # Count element types
    text_count = sum(1 for elem in page.layers[0].content if elem.type.value == "text")
    image_count = sum(1 for elem in page.layers[0].content if elem.type.value == "image")
    drawing_count = sum(1 for elem in page.layers[0].content if elem.type.value == "drawing")

    print(f"  - Text elements: {text_count}")
    print(f"  - Image elements: {image_count}")
    print(f"  - Drawing elements: {drawing_count}")

# Save as JSON template
with open("templates/report_template.json", "w") as f:
    f.write(document.to_json(indent=2))
```

### PSD Processing

```python
from src.engine.document_parser import PSDParser

# Check if PSD tools are available
parser = PSDParser()
if parser.can_parse("input/design.psd"):
    # Parse PSD file
    document = parser.parse("input/design.psd", {
        "include_text": True,
        "include_images": True,
        "include_drawings": True
    })

    # Access canvas structure
    canvas = document.document_structure[0]  # PSD has one canvas
    print(f"Canvas: {canvas.canvas_name}")
    print(f"Size: {canvas.size[0]} x {canvas.size[1]}")

    # Explore layer hierarchy
    def print_layer_hierarchy(layer, indent=0):
        prefix = "  " * indent
        print(f"{prefix}Layer: {layer.layer_name} ({layer.layer_type.value})")
        print(f"{prefix}  Visible: {layer.visibility}, Opacity: {layer.opacity}")
        print(f"{prefix}  Content: {len(layer.content)} elements")

        # Print child layers
        for child in layer.children:
            print_layer_hierarchy(child, indent + 1)

    for layer in canvas.layers:
        print_layer_hierarchy(layer)
else:
    print("PSD parsing not available. Install psd-tools: pip install psd-tools")
```

## Visual Validation

### Basic Validation

```python
from src.engine.visual_validator import VisualValidator
from src.engine.validation_strategy import ValidationConfig

# Create validator with custom threshold
config = ValidationConfig(
    ssim_threshold=0.98,
    rendering_dpi=300,
    generate_diff_images=True
)

validator = VisualValidator(config)

# Validate document
result = validator.validate(
    original_path="input/original.pdf",
    generated_path="output/rebuilt.pdf",
    diff_image_path="output/visual_diff.png"
)

# Check results
if result.passed:
    print(f"✅ Validation passed! SSIM score: {result.ssim_score:.4f}")
else:
    print(f"❌ Validation failed. SSIM score: {result.ssim_score:.4f}")
    print(f"   Threshold: {result.threshold}")
    print(f"   Diff image: {result.diff_image_path}")

# Access detailed metrics
print(f"Rendering DPI: {result.details['rendering_dpi']}")
print(f"Comparison engine: {result.details['comparison_engine']}")
```

### Batch Validation

```python
from src.engine.visual_validator import batch_validate_documents

# Define document pairs for validation
document_pairs = [
    ("input/doc1.pdf", "output/doc1_rebuilt.pdf"),
    ("input/doc2.pdf", "output/doc2_rebuilt.pdf"),
    ("input/doc3.pdf", "output/doc3_rebuilt.pdf"),
]

# Run batch validation
report = batch_validate_documents(
    document_pairs=document_pairs,
    output_dir="validation_results",
    report_name="batch_validation_report",
    config={
        "ssim_threshold": 0.95,
        "rendering_dpi": 300,
        "generate_diff_images": True
    }
)

# Analyze results
print(f"Batch validation complete:")
print(f"  Total documents: {len(report.results)}")
print(f"  Passed: {sum(1 for r in report.results if r.passed)}")
print(f"  Failed: {sum(1 for r in report.results if not r.passed)}")
print(f"  Success rate: {report.success_rate:.2%}")

# Print individual results
for i, result in enumerate(report.results):
    status = "✅ PASS" if result.passed else "❌ FAIL"
    print(f"  Document {i+1}: {status} (SSIM: {result.ssim_score:.4f})")
```

### Custom Validation Metrics

```python
from src.engine.validation_manager import ValidationManager

# Initialize validation manager with multiple engines
manager = ValidationManager(primary_engine="scikit-image")

# Validate with failover
result = manager.validate_with_failover(
    image1_path="original_page.png",
    image2_path="rebuilt_page.png",
    threshold=0.98
)

print(f"Validation engine used: {result.engine_used}")
print(f"Score: {result.score:.4f}")
print(f"Passed: {result.passed}")
```

## Font Management

### Basic Font Operations

```python
from src.font.font_manager import FontManager, FontConfig

# Configure font manager
config = FontConfig(
    font_directory="./downloaded_fonts",
    download_directory="./downloaded_fonts",
    enable_google_fonts=True,
    fallback_font="Arial",
    cache_file="font_cache.json"
)

font_manager = FontManager(config)

# Register local font
success = font_manager.register_font("CustomFont-Bold", "./fonts/custom-bold.ttf")
if success:
    print("Font registered successfully")

# Get font information
font_info = font_manager.get_font("Arial-Bold")
if font_info:
    print(f"Font found: {font_info.name} at {font_info.path}")
    print(f"Family: {font_info.family}, Style: {font_info.style}")

# Check glyph coverage
font_info = font_manager.get_font("Arial", "Hello 世界")
if font_info:
    print("Font supports the required text")
else:
    print("Font does not support all characters")
```

### Font Discovery and Download

```python
from src.font.font_discovery import FontDiscoveryService

# Initialize discovery service
discovery = FontDiscoveryService()

# Scan for local fonts
local_fonts = discovery.scan_directory("./downloaded_fonts")
print(f"Found {len(local_fonts)} local fonts")

# Search for specific font
font_path = discovery.search_font("Open Sans")
if font_path:
    print(f"Open Sans found at: {font_path}")
else:
    # Try to download from Google Fonts
    print("Attempting to download Open Sans from Google Fonts...")
    downloaded_path = discovery.download_font("Open Sans")
    if downloaded_path:
        print(f"Downloaded to: {downloaded_path}")
    else:
        print("Download failed")

# Get font metadata
if font_path:
    font_info = discovery.get_font_info(font_path)
    print(f"Font info: {font_info.name}, Format: {font_info.format}")
```

### Font Substitution

```python
from src.font.font_substitution import FontSubstitutionEngine

# Initialize substitution engine
substitution = FontSubstitutionEngine()

# Check glyph coverage
has_coverage = substitution.check_glyph_coverage(
    font_path="./fonts/arial.ttf",
    text="Hello World! 你好世界"
)

if not has_coverage:
    # Find fallback font
    fallback = substitution.find_fallback(
        font_name="Arial",
        text="Hello World! 你好世界"
    )
    if fallback:
        print(f"Using fallback font: {fallback}")
    else:
        print("No suitable fallback found")
```

## Template-Based Generation

### Creating and Using Templates

```python
from src.engine.document_parser import parse_document
from src.models.universal_idm import UniversalDocument

# Parse document to create template
template_document = parse_document("input/invoice_template.pdf")

# Save as reusable template
with open("templates/invoice_template.json", "w") as f:
    f.write(template_document.to_json(indent=2))

# Load template for modification
with open("templates/invoice_template.json", "r") as f:
    template = UniversalDocument.from_json(f.read())

# Modify template content
def update_text_element(document, element_id, new_text):
    """Update text content by element ID"""
    for unit in document.document_structure:
        for layer in unit.layers:
            for element in layer.content:
                if hasattr(element, 'id') and element.id == element_id:
                    if hasattr(element, 'text'):
                        element.text = new_text
                        return True
    return False

# Update invoice details
update_text_element(template, "invoice_number", "INV-2024-001")
update_text_element(template, "client_name", "Acme Corporation")
update_text_element(template, "invoice_date", "2024-01-15")
update_text_element(template, "total_amount", "$1,250.00")

# Save customized version
with open("output/invoice_001.json", "w") as f:
    f.write(template.to_json(indent=2))

# Generate PDF from customized template
# (Use document renderer to create final PDF)
```

### Batch Template Generation

```python
import json
from src.models.universal_idm import UniversalDocument

# Load base template
with open("templates/certificate_template.json", "r") as f:
    base_template = UniversalDocument.from_json(f.read())

# Certificate data
certificates = [
    {"name": "John Doe", "course": "Python Programming", "date": "2024-01-15"},
    {"name": "Jane Smith", "course": "Data Science", "date": "2024-01-16"},
    {"name": "Bob Johnson", "course": "Web Development", "date": "2024-01-17"},
]

# Generate certificates
for i, cert_data in enumerate(certificates):
    # Create copy of template
    template_copy = UniversalDocument.from_dict(base_template.to_dict())

    # Update certificate content
    update_text_element(template_copy, "recipient_name", cert_data["name"])
    update_text_element(template_copy, "course_name", cert_data["course"])
    update_text_element(template_copy, "completion_date", cert_data["date"])

    # Save customized certificate
    output_file = f"output/certificate_{i+1:03d}.json"
    with open(output_file, "w") as f:
        f.write(template_copy.to_json(indent=2))

    print(f"Generated certificate for {cert_data['name']}")
```

### Advanced Batch Modification with Variable Substitution

```python
from src.engine.batch_modifier import BatchModifier, VariableSubstitution
from src.models.universal_idm import UniversalDocument

# Load template
with open("templates/invoice_template.json", "r") as f:
    template = UniversalDocument.from_json(f.read())

# Create batch modifier
modifier = BatchModifier()

# Define variable substitutions
variables = [
    VariableSubstitution(variable_name="COMPANY_NAME", replacement_value="Acme Corporation"),
    VariableSubstitution(variable_name="INVOICE_NUMBER", replacement_value="INV-2024-001"),
    VariableSubstitution(variable_name="INVOICE_DATE", replacement_value="2024-01-15"),
    VariableSubstitution(variable_name="TOTAL_AMOUNT", replacement_value="$1,250.00"),
]

# Perform variable substitution
result = modifier.variable_substitution(
    document=template,
    variables=variables,
    template_mode=True,
)

print(f"Modified elements: {result.modified_elements}")
print(f"Skipped elements: {result.skipped_elements}")
print(f"Font warnings: {len(result.font_warnings)}")

# Save personalized document
with open("output/personalized_invoice.json", "w") as f:
    f.write(template.to_json(indent=2))
```

### Batch Text Replacement

```python
from src.engine.batch_modifier import BatchModifier

# Load document
with open("input/document.json", "r") as f:
    document = UniversalDocument.from_json(f.read())

# Create batch modifier
modifier = BatchModifier()

# Define text replacements
replacements = [
    ("old company name", "new company name"),
    ("old address", "new address"),
    ("old phone", "new phone"),
]

# Perform batch replacement
result = modifier.batch_text_replacement(
    document=document,
    replacements=replacements,
    element_ids=["header", "footer"],  # Target specific elements
    page_numbers=[0, 1],  # Target specific pages
    validate_fonts=True,
)

print(f"Modified elements: {result.modified_elements}")
print(f"Skipped elements: {result.skipped_elements}")
print(f"Font warnings: {len(result.font_warnings)}")

# Save modified document
with open("output/modified_document.json", "w") as f:
    f.write(document.to_json(indent=2))
```

### Font Validation and Compliance

```python
from src.engine.batch_modifier import BatchModifier

# Load document
with open("input/document.json", "r") as f:
    document = UniversalDocument.from_json(f.read())

# Create batch modifier
modifier = BatchModifier()

# Validate fonts
validation_result = modifier.validate_document_fonts(
    document=document,
    check_licensing=True,
)

print(f"Overall status: {validation_result['overall_status']}")
print(f"Fonts used: {validation_result['fonts_used']}")
print(f"Fonts missing: {validation_result['fonts_missing']}")
print(f"Fonts unlicensed: {validation_result['fonts_unlicensed']}")

if validation_result['elements_with_issues']:
    print("\nIssues found:")
    for issue in validation_result['elements_with_issues']:
        print(f"  - Element {issue['element_id']}: {issue['issue']} - {issue['font_name']}")
```

### CLI Usage for Batch Modification

```bash
# Variable substitution
hatch run python -m src.cli.batch_modifier_cli substitute \
  --input templates/invoice_template.json \
  --variables "COMPANY_NAME:Acme Corp" "INVOICE_NUMBER:INV-001" \
  --output output/personalized_invoice.json

# Batch text replacement
hatch run python -m src.cli.batch_modifier_cli replace \
  --input input/document.json \
  --replacements "old text:new text" "another:replacement" \
  --output output/modified_document.json

# Font validation
hatch run python -m src.cli.batch_modifier_cli validate \
  --input input/document.json \
  --output validation_report.json \
  --detailed-report

# Get substitution statistics
hatch run python -m src.cli.batch_modifier_cli stats \
  --input templates/document.json \
  --output stats.json \
  --substitution-stats
```

### Integration with UV Package Manager

```bash
# Install dependencies with uv
uv add PyMuPDF fonttools psd-tools opencv-python

# Run batch modification with uv
uv run python -m src.cli.batch_modifier_cli substitute \
  --input templates/invoice_template.json \
  --variables "COMPANY_NAME:Acme Corp" \
  --output output/personalized_invoice.json

# Run tests with uv
uv run pytest tests/test_batch_modifier.py -v

# Run example with uv
uv run python examples/batch_modification_example.py
```

## Batch Processing

### Process Multiple Documents

```bash
#!/bin/bash
# Batch processing script

INPUT_DIR="input"
OUTPUT_DIR="output"
CONFIG_DIR="configs"

# Create output directories
mkdir -p "$OUTPUT_DIR" "$CONFIG_DIR"

# Process all PDF files
for pdf_file in "$INPUT_DIR"/*.pdf; do
    if [ -f "$pdf_file" ]; then
        filename=$(basename "$pdf_file" .pdf)
        config_file="$CONFIG_DIR/${filename}_config.json"
        output_file="$OUTPUT_DIR/${filename}_rebuilt.pdf"

        echo "Processing: $pdf_file"

        # Extract and rebuild
        hatch run python main.py \
            --input "$pdf_file" \
            --config "$config_file" \
            --output "$output_file" \
            --log-level INFO

        if [ $? -eq 0 ]; then
            echo "✅ Successfully processed: $filename"
        else
            echo "❌ Failed to process: $filename"
        fi
    fi
done

echo "Batch processing complete!"
```

### Python Batch Processing

```python
import os
import glob
from pathlib import Path
from src.engine.document_parser import parse_document
from src.tools import serialize_pdf_content_to_config

def batch_extract_documents(input_dir, output_dir, config_dir):
    """Extract multiple documents to Universal IDM format"""

    # Create output directories
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(config_dir).mkdir(parents=True, exist_ok=True)

    # Find all supported documents
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    psd_files = glob.glob(os.path.join(input_dir, "*.psd"))
    all_files = pdf_files + psd_files

    results = []

    for file_path in all_files:
        try:
            filename = Path(file_path).stem
            config_path = os.path.join(config_dir, f"{filename}_config.json")

            print(f"Processing: {file_path}")

            # Parse document
            document = parse_document(file_path, {
                "include_text": True,
                "include_images": True,
                "include_drawings": True
            })

            # Serialize to config
            serialize_pdf_content_to_config(document, config_path)

            results.append({
                "file": file_path,
                "config": config_path,
                "status": "success"
            })

            print(f"✅ Extracted: {filename}")

        except Exception as e:
            print(f"❌ Failed to process {file_path}: {str(e)}")
            results.append({
                "file": file_path,
                "config": None,
                "status": "failed",
                "error": str(e)
            })

    return results

# Run batch extraction
results = batch_extract_documents("input", "output", "configs")

# Print summary
successful = sum(1 for r in results if r["status"] == "success")
failed = sum(1 for r in results if r["status"] == "failed")

print(f"\nBatch extraction complete:")
print(f"  Successful: {successful}")
print(f"  Failed: {failed}")
print(f"  Total: {len(results)}")
```

## Advanced Customization

### Custom Element Processing

```python
from src.models.universal_idm import UniversalDocument, TextElement, Color

def apply_custom_styling(document):
    """Apply custom styling to all text elements"""

    for unit in document.document_structure:
        for layer in unit.layers:
            for element in layer.content:
                if isinstance(element, TextElement):
                    # Make all text bold and blue
                    element.font_details.is_bold = True
                    element.font_details.color = Color(0, 0, 1, 1)  # Blue

                    # Increase font size by 20%
                    element.font_details.size *= 1.2

                    # Add prefix to text
                    if not element.text.startswith("[MODIFIED]"):
                        element.text = f"[MODIFIED] {element.text}"

# Load document
with open("input_config.json", "r") as f:
    document = UniversalDocument.from_json(f.read())

# Apply custom styling
apply_custom_styling(document)

# Save modified document
with open("output_config.json", "w") as f:
    f.write(document.to_json(indent=2))
```

### Content Analysis

```python
from src.models.universal_idm import UniversalDocument
from collections import Counter

def analyze_document_content(document):
    """Analyze document content and generate statistics"""

    stats = {
        "pages": len(document.document_structure),
        "layers": 0,
        "elements": {"text": 0, "image": 0, "drawing": 0},
        "fonts": Counter(),
        "colors": Counter(),
        "text_content": []
    }

    for unit in document.document_structure:
        stats["layers"] += len(unit.layers)

        for layer in unit.layers:
            for element in layer.content:
                # Count element types
                element_type = element.type.value
                stats["elements"][element_type] += 1

                # Analyze text elements
                if element_type == "text":
                    stats["fonts"][element.font_details.name] += 1
                    color_hex = element.font_details.color.to_hex()
                    stats["colors"][color_hex] += 1
                    stats["text_content"].append(element.text)

    return stats

# Load and analyze document
with open("document_config.json", "r") as f:
    document = UniversalDocument.from_json(f.read())

stats = analyze_document_content(document)

# Print analysis
print("Document Analysis:")
print(f"  Pages: {stats['pages']}")
print(f"  Layers: {stats['layers']}")
print(f"  Elements: {dict(stats['elements'])}")
print(f"  Unique fonts: {len(stats['fonts'])}")
print(f"  Most common font: {stats['fonts'].most_common(1)[0] if stats['fonts'] else 'None'}")
print(f"  Unique colors: {len(stats['colors'])}")
print(f"  Text elements: {len(stats['text_content'])}")
```

### Document Comparison

```python
from src.models.universal_idm import UniversalDocument

def compare_documents(doc1, doc2):
    """Compare two documents and identify differences"""

    differences = []

    # Compare structure
    if len(doc1.document_structure) != len(doc2.document_structure):
        differences.append(f"Page count differs: {len(doc1.document_structure)} vs {len(doc2.document_structure)}")

    # Compare content
    for i, (unit1, unit2) in enumerate(zip(doc1.document_structure, doc2.document_structure)):
        if len(unit1.layers) != len(unit2.layers):
            differences.append(f"Page {i}: Layer count differs")

        for j, (layer1, layer2) in enumerate(zip(unit1.layers, unit2.layers)):
            if len(layer1.content) != len(layer2.content):
                differences.append(f"Page {i}, Layer {j}: Element count differs")

            for k, (elem1, elem2) in enumerate(zip(layer1.content, layer2.content)):
                if elem1.type != elem2.type:
                    differences.append(f"Page {i}, Layer {j}, Element {k}: Type differs")

                if hasattr(elem1, 'text') and hasattr(elem2, 'text'):
                    if elem1.text != elem2.text:
                        differences.append(f"Page {i}, Layer {j}, Element {k}: Text differs")

    return differences

# Load documents
with open("doc1_config.json", "r") as f:
    doc1 = UniversalDocument.from_json(f.read())

with open("doc2_config.json", "r") as f:
    doc2 = UniversalDocument.from_json(f.read())

# Compare documents
differences = compare_documents(doc1, doc2)

if differences:
    print("Documents differ:")
    for diff in differences:
        print(f"  - {diff}")
else:
    print("Documents are structurally identical")
```

## Error Handling

### Robust Document Processing

```python
import logging
from src.engine.document_parser import parse_document, DocumentEngineError, ParseError
from src.engine.visual_validator import VisualValidator, VisualValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_document_safely(input_path, output_path):
    """Process document with comprehensive error handling"""

    try:
        # Parse document
        logger.info(f"Parsing document: {input_path}")
        document = parse_document(input_path)

        # Validate document structure
        if not document.document_structure:
            raise ValueError("Document has no content")

        logger.info(f"Successfully parsed {len(document.document_structure)} pages")

        # Save configuration
        config_path = input_path.replace(".pdf", "_config.json")
        with open(config_path, "w") as f:
            f.write(document.to_json(indent=2))

        logger.info(f"Configuration saved to: {config_path}")

        # Generate output (placeholder - would use actual renderer)
        logger.info(f"Generating output: {output_path}")
        # renderer.render(document, output_path)

        # Validate output
        validator = VisualValidator()
        result = validator.validate(input_path, output_path)

        if result.passed:
            logger.info(f"✅ Validation passed (SSIM: {result.ssim_score:.4f})")
        else:
            logger.warning(f"⚠️ Validation failed (SSIM: {result.ssim_score:.4f})")

        return True

    except ParseError as e:
        logger.error(f"Parse error: {str(e)}")
        return False

    except VisualValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return False

    except DocumentEngineError as e:
        logger.error(f"Engine error: {str(e)}")
        return False

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.exception("Full traceback:")
        return False

# Process multiple documents with error handling
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = []

for doc in documents:
    success = process_document_safely(f"input/{doc}", f"output/{doc}")
    results.append((doc, success))

# Summary
successful = sum(1 for _, success in results if success)
print(f"\nProcessing complete: {successful}/{len(documents)} successful")
```

### Graceful Degradation

```python
from src.engine.document_parser import parse_document
from src.models.universal_idm import UniversalDocument

def extract_with_fallback(file_path):
    """Extract document content with graceful degradation"""

    extraction_flags = {
        "include_text": True,
        "include_images": True,
        "include_drawings": True,
        "include_raw_background_drawings": False
    }

    try:
        # Try full extraction
        return parse_document(file_path, extraction_flags)

    except Exception as e:
        print(f"Full extraction failed: {str(e)}")

        # Try without drawings
        print("Retrying without vector drawings...")
        extraction_flags["include_drawings"] = False
        try:
            return parse_document(file_path, extraction_flags)
        except Exception as e:
            print(f"Extraction without drawings failed: {str(e)}")

            # Try text only
            print("Retrying with text only...")
            extraction_flags["include_images"] = False
            try:
                return parse_document(file_path, extraction_flags)
            except Exception as e:
                print(f"Text-only extraction failed: {str(e)}")
                raise

# Use fallback extraction
try:
    document = extract_with_fallback("problematic_document.pdf")
    print("✅ Document extracted successfully (possibly with reduced features)")
except Exception as e:
    print(f"❌ All extraction attempts failed: {str(e)}")
```

## Batch Modification Engine

### Overview

The Multi-Format Document Engine includes a powerful batch modification engine that allows you to apply transformations to multiple documents simultaneously. This engine is designed to be highly configurable and can handle various document types (PDF, PSD, etc.) and complex modifications.

### CLI Usage

```bash
# Apply a transformation to all PDF files in a directory
hatch run python main.py --mode modify --input input/documents --output output/modified_documents \
  --config modify_config.json --log-level INFO

# Apply a specific transformation (e.g., change text color)
hatch run python main.py --mode modify --input input/documents --output output/modified_documents \
  --config modify_config.json --transformation "change_text_color" --value "red" --log-level INFO
```

### Configuration

The `modify_config.json` file defines the batch modification rules. Here's an example:

```json
{
    "transformations": [
        {
            "type": "change_text_color",
            "target": "text",
            "value": "blue"
        },
        {
            "type": "change_font_size",
            "target": "text",
            "value": 14
        },
        {
            "type": "add_text",
            "target": "image",
            "value": "Watermark"
        }
    ]
}
```

### Python Integration

```python
import os
import glob
from pathlib import Path
from src.engine.document_parser import parse_document
from src.tools import serialize_pdf_content_to_config

def batch_modify_documents(input_dir, output_dir, config_dir):
    """Apply batch modifications to multiple documents"""

    # Create output directories
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(config_dir).mkdir(parents=True, exist_ok=True)

    # Find all supported documents
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    psd_files = glob.glob(os.path.join(input_dir, "*.psd"))
    all_files = pdf_files + psd_files

    results = []

    for file_path in all_files:
        try:
            filename = Path(file_path).stem
            config_path = os.path.join(config_dir, f"{filename}_config.json")

            print(f"Processing: {file_path}")

            # Parse document
            document = parse_document(file_path)

            # Load configuration
            with open(config_path, "r") as f:
                config = json.load(f)

            # Apply transformations
            for transformation in config["transformations"]:
                if transformation["type"] == "change_text_color":
                    apply_text_color_transformation(document, transformation["target"], transformation["value"])
                elif transformation["type"] == "change_font_size":
                    apply_font_size_transformation(document, transformation["target"], transformation["value"])
                elif transformation["type"] == "add_text":
                    apply_add_text_transformation(document, transformation["target"], transformation["value"])
                else:
                    print(f"Skipping unknown transformation type: {transformation['type']}")

            # Serialize modified document
            serialize_pdf_content_to_config(document, config_path)

            results.append({
                "file": file_path,
                "config": config_path,
                "status": "success"
            })

            print(f"✅ Modified: {filename}")

        except Exception as e:
            print(f"❌ Failed to process {file_path}: {str(e)}")
            results.append({
                "file": file_path,
                "config": None,
                "status": "failed",
                "error": str(e)
            })

    return results

def apply_text_color_transformation(document, target_type, value):
    """Applies a text color transformation to all text elements of a given type."""
    for unit in document.document_structure:
        for layer in unit.layers:
            for element in layer.content:
                if isinstance(element, TextElement):
                    if element.type.value == target_type:
                        element.font_details.color = Color(value) # Assuming value is a hex color string

def apply_font_size_transformation(document, target_type, value):
    """Applies a font size transformation to all text elements of a given type."""
    for unit in document.document_structure:
        for layer in unit.layers:
            for element in layer.content:
                if isinstance(element, TextElement):
                    if element.type.value == target_type:
                        element.font_details.size = value

def apply_add_text_transformation(document, target_type, value):
    """Applies an add text transformation to all elements of a given type."""
    for unit in document.document_structure:
        for layer in unit.layers:
            for element in layer.content:
                if isinstance(element, TextElement):
                    if element.type.value == target_type:
                        element.text += f" ({value})"

# Run batch modification
results = batch_modify_documents("input", "output", "configs")

# Print summary
successful = sum(1 for r in results if r["status"] == "success")
failed = sum(1 for r in results if r["status"] == "failed")

print(f"\nBatch modification complete:")
print(f"  Successful: {successful}")
print(f"  Failed: {failed}")
print(f"  Total: {len(results)}")
```

These examples demonstrate the comprehensive capabilities of the Multi-Format Document Engine, from basic usage to advanced customization scenarios. The engine's modular architecture allows for flexible integration into various workflows while maintaining robust error handling and validation capabilities.
