# Examples and Demonstrations

This directory contains example scripts and demonstrations that showcase the capabilities of the PDF Layout Extractor and Rebuilder system.

## Available Examples

### Comprehensive Demo (`comprehensive_example.py`)

**🌟 START HERE** - Complete end-to-end demonstration of all major features.

**Features Demonstrated:**

- PDF content extraction with detailed analysis
- Document content modification
- PDF reconstruction and validation
- Performance metrics and quality assessment
- Error handling and reporting

**Usage:**

```bash
python examples/comprehensive_example.py
```

### PDF Processing Examples (`pdf_processing_examples.py`)

Comprehensive PDF processing workflows covering all major PDF operations.

**Features Demonstrated:**

- Basic and advanced PDF extraction
- PDF reconstruction from JSON
- Content modification workflows
- PDF content analysis and statistics
- Error handling and troubleshooting

**Usage:**

```bash
python examples/pdf_processing_examples.py
```

### PSD Processing Examples (`psd_processing_examples.py`)

Demonstrates PSD file processing capabilities (interface demonstration).

**Features Demonstrated:**

- PSD content extraction (when available)
- Layer hierarchy preservation
- PSD to PDF conversion
- Layer manipulation and editing
- Interface documentation for future implementation

**Usage:**

```bash
python examples/psd_processing_examples.py
```

### Batch Processing Examples (`batch_processing_examples.py`)

Advanced batch processing workflows for handling multiple documents.

**Features Demonstrated:**

- Parallel and sequential batch processing
- Batch text replacement across documents
- Variable substitution for template documents
- Batch format conversion
- Comprehensive error handling and reporting

**Usage:**

```bash
python examples/batch_processing_examples.py
```

### Legacy Examples

#### PDF Content Extraction (`extract_sample.py`)

Basic PDF extraction example for simple use cases.

**Usage:**

```bash
python examples/extract_sample.py
```

#### Batch Modification Example (`batch_modification_example.py`)

Basic batch modification demonstration.

**Usage:**

```bash
python examples/batch_modification_example.py
```

## Example Validation System (`validation.py`)

Automated validation system to ensure all examples work correctly with the current codebase.

**Features:**

- Validates all Python example files
- Checks import statements and syntax
- Executes examples and reports results
- Generates detailed validation reports

**Usage:**

```bash
python examples/validation.py
```

**Output:**

- Console summary of validation results
- Detailed report saved to `examples/output/validation_report.md`

## Quick Start Guide

### 1. Run the Comprehensive Demo

Start with the comprehensive example to see all features:

```bash
python examples/comprehensive_example.py
```

### 2. Explore Specific Features

Choose examples based on your needs:

- **PDF Processing**: `python examples/pdf_processing_examples.py`
- **Batch Operations**: `python examples/batch_processing_examples.py`
- **PSD Interface**: `python examples/psd_processing_examples.py`

### 3. Validate Examples

Ensure all examples work with your setup:

```bash
python examples/validation.py
```

## Running Examples

All examples should be run from the project root directory to ensure proper path resolution:

```bash
# Correct way to run examples
cd /path/to/project/root
python examples/comprehensive_example.py
python examples/pdf_processing_examples.py
```

## Output Directory

Examples that generate output files will save them to `examples/output/`. This directory is automatically created when needed.

## Adding New Examples

When adding new example scripts:

1. **Location**: Place the script in this `examples/` directory
2. **Naming**: Use descriptive names ending with `_example.py` or similar
3. **Documentation**: Include comprehensive docstrings explaining the example
4. **Path Handling**: Use the path setup pattern shown in existing examples:

   ```python
   import sys
   from pathlib import Path

   # Add the project root to the Python path
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

5. **Output**: Save any generated files to `examples/output/`
6. **README**: Update this README with details about the new example

## Purpose

These examples serve multiple purposes:

- **Learning**: Help users understand how to use the system
- **Testing**: Provide working examples that can be used to verify functionality
- **Documentation**: Show real-world usage patterns
- **Development**: Serve as templates for new functionality

## Related Documentation

- **Main Documentation**: See the project README for overall system documentation
- **API Documentation**: Check `docs/` directory for detailed API information
- **Test Documentation**: See `tests/README.md` for testing-related examples
