# Multi-Format Document Engine

[![PyPI version](https://badge.fury.io/py/pdfrebuilder.svg)](https://badge.fury.io/py/pdfrebuilder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)

A Python tool for deconstructing document layouts into human-readable JSON format and rebuilding visually similar documents from that data. The primary purpose is to enable programmatic modification of document content while preserving original layout and visual fidelity.

## Test Results

All tests are currently passing. For the latest test results, please see the [GitHub Actions page](https://github.com/mmartin-sub/pdfrebuilder/actions).

## Dependencies

For a complete list of dependencies, please see the `pyproject.toml` file.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Batch Modification Engine](#batch-modification-engine)
- [Multi-Engine Rendering System](#multi-engine-rendering-system)
- [Font Management and Validation](#font-management-and-validation)
- [Advanced Features](#advanced-features)
- [Configuration](#configuration)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Document Processing

- **Layout Extraction**: Extracts text blocks, raster images, and vector graphics from document pages
- **Universal Document Model**: Format-agnostic representation supporting PDF and PSD files
- **JSON Configuration**: Saves layout information in structured, human-readable JSON format
- **Document Reconstruction**: Generates new documents from JSON configuration with high visual fidelity
- **Intelligent Text Handling**: Automatically detects and normalizes text with unnatural character spacing

### Advanced Processing Capabilities

- **Batch Modification Engine**: Advanced text replacement, variable substitution, and font validation
- **Multi-Engine Rendering**: PyMuPDF (Fitz) and ReportLab engines with enhanced precision
- **Visual Validation**: Automated visual comparison between original and reconstructed documents
- **Template System**: Template-based document generation with variable substitution
- **Font Management**: Comprehensive font validation, embedding, and licensing checks

### Development and Debugging Tools

- **Visual Debugging**: Multi-page debug PDFs showing vector graphics layer-by-layer
- **CLI Interface**: Command-line tools for batch processing and automation
- **Override System**: Manual corrections via `manual_overrides.json5` for extraction errors
- **Validation Framework**: Comprehensive document and font validation with detailed reporting

## Project Structure

The project is organized into the following main directories:

- `src/pdfrebuilder`: Contains the main source code for the project.
  - `cli`: Command-line interface logic.
  - `core`: Core document processing and rendering logic.
  - `engine`: PDF engine implementations (PyMuPDF, ReportLab).
  - `font`: Font management, validation, and substitution logic.
  - `models`: Data models for the universal document representation.
  - `security`: Security-related utilities.
- `tests`: Contains all the tests for the project.
- `docs`: Contains the documentation for the project.
- `examples`: Contains example scripts and usage demonstrations.
- `scripts`: Contains utility scripts for development and maintenance.

## Quick Start

### Installation

PDFRebuilder can be installed using multiple methods to suit different use cases:

#### Method 1: Global Tool Installation (Recommended)

Install as a global command-line tool using `uv`:

```bash
# Install globally with uv tool install
uv tool install pdfrebuilder

# Use directly from anywhere
pdfrebuilder --help
pdfrebuilder --generate-config
```

#### Method 2: Isolated Execution

Run without permanent installation using `uvx`:

```bash
# Run directly without installing
uvx pdfrebuilder --help
uvx pdfrebuilder --mode extract --input document.pdf
```

#### Method 3: Development Installation

For development or when you need the full source code:

```bash
# Clone the repository
git clone <repository-url>
cd pdfrebuilder

# Using hatch (recommended for development)
hatch env create
hatch shell

# Verify installation
pdfrebuilder --help
```

#### Method 4: Library Installation

Install as a Python library for programmatic use:

```bash
# Install as library dependency
uv add pdfrebuilder
# or
pip install pdfrebuilder
```

**Quick Install**: See [QUICK_INSTALL.md](docs/QUICK_INSTALL.md) for a summary of all installation methods.

For detailed installation instructions and troubleshooting, see [INSTALLATION.md](docs/INSTALLATION.md).

**Optional Dependencies**: For PSD support, image validation, and OCR functionality, see [OPTIONAL_DEPENDENCIES.md](docs/OPTIONAL_DEPENDENCIES.md) for installation instructions.

### First-time fonts setup

To ensure sensible defaults for font fallback and reduce first-run warnings, download essential fonts:

```bash
pdfrebuilder download-fonts
```

This will populate `fonts/auto/` (configured via `downloaded_fonts_dir`) with commonly used families like `Noto Sans`.

### Basic Usage

```bash
# Extract layout from a PDF
pdfrebuilder extract --input input/document.pdf --config layout.json

# Generate a new PDF from the layout file
pdfrebuilder generate --config layout.json --output output/rebuilt.pdf

# Perform a full extract and generate cycle
pdfrebuilder full --input input/document.pdf --output output/rebuilt.pdf

# Configuration management
pdfrebuilder generate-config  # Create sample configuration
pdfrebuilder show-config      # Show current settings
pdfrebuilder --config-file myconfig.toml extract --input document.pdf
```

## Batch Modification Engine

The Multi-Format Document Engine includes a powerful batch modification system for programmatic document transformation and template-based generation.

### Key Features

- **Batch Text Replacement**: Replace multiple text patterns across entire documents
- **Variable Substitution**: Template-based generation with `${VARIABLE_NAME}` syntax
- **Font Validation**: Comprehensive font availability and licensing checks
- **CLI Interface**: Command-line tools for automation and scripting
- **Filtering**: Target specific elements or pages for modifications

### CLI Usage

```bash
# Variable substitution
pdfrebuilder substitute \
  --input templates/invoice_template.json \
  --variables "COMPANY_NAME:Acme Corp" "INVOICE_NUMBER:INV-001" \
  --output output/personalized_invoice.json

# Batch text replacement
pdfrebuilder replace \
  --input input/document.json \
  --replacements "old text:new text" "another:replacement" \
  --output output/modified_document.json

# Font validation
pdfrebuilder validate-fonts \
  --input input/document.json \
  --output validation_report.json \
  --detailed-report
```

### Python API

```python
from pdfrebuilder.engine.batch_modifier import BatchModifier, VariableSubstitution
from pdfrebuilder.models.universal_idm import UniversalDocument

# Load template document
with open("templates/invoice_template.json", "r") as f:
    template = UniversalDocument.from_json(f.read())

# Create batch modifier
modifier = BatchModifier()

# Variable substitution
variables = [
    VariableSubstitution(variable_name="COMPANY_NAME", replacement_value="Acme Corporation"),
    VariableSubstitution(variable_name="INVOICE_NUMBER", replacement_value="INV-2024-001"),
]

result = modifier.variable_substitution(
    document=template,
    variables=variables,
)

print(f"Modified elements: {result.modified_elements}")

# Save personalized document
with open("output/personalized_invoice.json", "w") as f:
    f.write(template.to_json(indent=2))
```

## Multi-Engine Rendering System

The Multi-Format Document Engine supports multiple rendering engines for different use cases and enhanced capabilities.

### Available Engines

- **PyMuPDF (Fitz)**: Default engine with comprehensive PDF support and fast processing
- **ReportLab**: Enhanced precision, proper font embedding, and licensing verification

### Engine Selection

```python
from pdfrebuilder.engine.pdf_engine_selector import get_pdf_engine

# Use ReportLab engine for enhanced precision
engine = get_pdf_engine("reportlab")
engine.generate(document_config, "output.pdf")

# Use PyMuPDF engine (default)
engine = get_pdf_engine("pymupdf")
engine.generate(document_config, "output.pdf")
```

### Engine Comparison

```python
from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector

selector = get_engine_selector()
comparison = selector.compare_engines("reportlab", "pymupdf")

print("Feature differences:")
for feature, diff in comparison["differences"].items():
    print(f"  {feature}: ReportLab={diff['engine1']}, PyMuPDF={diff['engine2']}")
```

### Testing

The project includes comprehensive testing with configurable verbosity levels to reduce noise from third-party libraries like fontTools.

#### Running Tests

```bash
# Default quiet mode (recommended)
hatch run test

# With coverage reporting
hatch run test-cov

# Verbose mode for debugging
hatch run test-verbose
```

To keep logs minimal during tests, configure pytest logging to show WARNING and above only (INFO/DEBUG hidden):

```ini
# pytest.ini
[pytest]
log_level = WARNING
# optionally, disable live log printing
log_cli = false
```

#### Verbosity Levels

- **Quiet (default)**: Suppresses fontTools debug output, shows only warnings and errors
- **Verbose**: Shows INFO level logging but still suppresses fontTools noise
- **Debug**: Shows all logging including fontTools debug output

#### CLI Testing

```bash
# Test ReportLab engine capabilities
pdfrebuilder test-engine reportlab --info
pdfrebuilder test-engine reportlab --generate --output test.pdf
pdfrebuilder test-engine reportlab --compare
```

### Example Workflow

1. **Extract Template**: Convert document to JSON template

   ```bash
   pdfrebuilder extract --input invoice_template.pdf --config templates/invoice.json
   ```

2. **Personalize Content**: Apply variable substitutions

   ```bash
   pdfrebuilder substitute \
     --input templates/invoice.json \
     --variables "COMPANY_NAME:Acme Corp" "INVOICE_NUMBER:INV-001" \
     --output output/personalized_invoice.json
   ```

3. **Generate Document**: Convert back to PDF

   ```bash
   pdfrebuilder generate --config output/personalized_invoice.json --output final_invoice.pdf
   ```

## Font Management and Validation

The system includes comprehensive font management with validation, licensing checks, and automatic font discovery.

### Font Validation

```python
from pdfrebuilder.engine.batch_modifier import BatchModifier

modifier = BatchModifier()

# Validate fonts in document
validation_result = modifier.validate_document_fonts(
    document=document,
    check_licensing=True,
)

print(f"Overall status: {validation_result['overall_status']}")
print(f"Fonts missing: {validation_result['fonts_missing']}")
print(f"Fonts unlicensed: {validation_result['fonts_unlicensed']}")
```

### Font Directory Structure

```
fonts/
├── auto/          # Automatically downloaded fonts
├── manual/        # Manually added font files
└── README.md      # Font management documentation
```

## Advanced Features

### Visual Validation

The system includes automated visual comparison between original and reconstructed documents:

```python
from pdfrebuilder.core.compare_pdfs_visual import compare_pdfs_visual

# Compare original and rebuilt documents
compare_pdfs_visual(
    original_path="input/document.pdf",
    rebuilt_path="output/rebuilt.pdf",
    diff_output_path="output/visual_diff.png"
)
```

### Template-Based Generation

Create reusable templates from extracted documents:

```python
from pdfrebuilder.engine.document_parser import parse_document
from pdfrebuilder.models.universal_idm import UniversalDocument

# Extract document to template
document = parse_document("input/invoice_template.pdf")
with open("templates/invoice_template.json", "w") as f:
    f.write(document.to_json(indent=2))

# Use template for batch generation
for customer in customers:
    # Load template
    with open("templates/invoice_template.json", "r") as f:
        template = UniversalDocument.from_json(f.read())

    # Apply substitutions
    modifier.variable_substitution(template, [
        VariableSubstitution("CUSTOMER_NAME", customer.name),
        VariableSubstitution("INVOICE_AMOUNT", customer.amount),
    ])

    # Generate PDF
    engine.generate(template.to_dict(), f"output/invoice_{customer.id}.pdf")
```

### Batch Processing

Process multiple documents with consistent modifications:

```bash
#!/bin/bash
# Batch process all documents in directory
for doc_file in input/*.pdf; do
    filename=$(basename "$doc_file" .pdf)

    # Extract to JSON
    pdfrebuilder extract --input "$doc_file" --config "configs/${filename}.json"

    # Apply modifications
    pdfrebuilder replace \
      --input "configs/${filename}.json" \
      --replacements "old company:new company" \
      --output "configs/${filename}_modified.json"

    # Generate modified document
    pdfrebuilder generate \
      --config "configs/${filename}_modified.json" \
      --output "output/${filename}_modified.pdf"
done
```

## Configuration

### Manual Overrides

Create `manual_overrides.json5` for extraction corrections:

```json5
{
  "text_block_overrides": {
    "block_135_1409": {
      "font": "DancingScript-Regular",
      "color": 4209970,
      "text": "Corrected text content"
    }
  },
  "use_original_as_template": true,
  "image_bboxes": {
    "image_1_fbc04c5c.jpeg": [270.0, 265.0, 965.0, 1308.0]
  }
}
```

### Output Directory Configuration

Configure output directories for organized file management:

```bash
# Configure custom output directories
pdfrebuilder \
  --output-dir ./custom_output \
  --test-output-dir ./test_results \
  --reports-output-dir ./reports \
  --input input/document.pdf
```

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd multi-format-document-engine

# Create development environment
hatch env create
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Code formatting and linting
hatch run lint:style
hatch run lint:lint
hatch run lint:typing

### Running CI Checks Locally

To run the same checks that are executed in the CI pipeline, you can use the `make ci` command:

```bash
make ci
```

This will run all linting and testing checks, ensuring that your changes will pass the CI pipeline on GitHub.

```

### Running Examples

```bash
# Run batch modification example
hatch run python examples/batch_modification_example.py

# Run PDF extraction example
hatch run python examples/extract_sample.py

# Test full pipeline with visual comparison
pdfrebuilder full --input input/sample.pdf --output output/rebuilt.pdf
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [Security Guidelines](docs/SECURITY.md) - Security considerations and best practices
- [Getting Started Guide](docs/guides/getting-started.md) - Basic usage tutorial
- [API Reference](docs/api/) - Detailed API documentation
- [Configuration Reference](docs/reference/configuration.md) - Complete configuration options
- [CLI Reference](docs/reference/cli.md) - Command-line interface documentation

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
