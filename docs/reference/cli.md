# Command Line Interface Reference

This document provides a comprehensive reference for all command-line interfaces in the Multi-Format Document Engine.

## Main Application CLI

### Basic Usage

```bash
python main.py [OPTIONS]
```

### Options

#### Input/Output Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--input` | PATH | `input/sample.pdf` | Input document file path |
| `--output` | PATH | Auto-resolved | Output document file path |
| `--config` | PATH | `layout_config.json` | Configuration file path |
| `--debugoutput` | PATH | Auto-resolved | Debug output file path for layer visualization |

#### Processing Mode Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--mode` | CHOICE | `full` | Processing mode: extract, generate, debug, full |

#### Output Directory Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output-dir` | PATH | `./output` | Base output directory for all generated files |
| `--test-output-dir` | PATH | `<output-dir>/tests` | Output directory for test files and reports |
| `--reports-output-dir` | PATH | `<output-dir>/reports` | Output directory for reports and logs |

#### Extraction Control Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--extract-text` | FLAG | `True` | Include text blocks in extraction |
| `--no-extract-text` | FLAG | - | Exclude text blocks from extraction |
| `--extract-images` | FLAG | `True` | Include image blocks in extraction |
| `--no-extract-images` | FLAG | - | Exclude image blocks from extraction |
| `--extract-drawings` | FLAG | `True` | Include non-background vector drawings |
| `--no-extract-drawings` | FLAG | - | Exclude non-background vector drawings |
| `--extract-raw-backgrounds` | FLAG | `False` | Include raw background drawings (debugging) |
| `--no-extract-raw-backgrounds` | FLAG | - | Exclude raw background drawings |

#### Logging Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--log-level` | CHOICE | `INFO` | Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |

#### Help Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |

### Processing Modes

#### Extract Mode

Extract layout information from input document to JSON configuration.

```bash
# Extract PDF layout to JSON
python main.py --mode extract --input document.pdf --config layout.json

# Extract with verbose output
python main.py --mode extract --input document.pdf --verbose
```

#### Generate Mode

Generate output document from existing JSON configuration.

```bash
# Generate PDF from configuration
python main.py --mode generate --config layout.json --output result.pdf

# Generate with custom overrides
python main.py --mode generate --config layout.json --output result.pdf
```

#### Debug Mode

Generate debug visualization showing document layers.

```bash
# Create debug visualization
python main.py --mode debug --config layout.json --debugoutput debug.pdf

# Debug with verbose logging
python main.py --mode debug --config layout.json --debugoutput debug.pdf --verbose
```

#### Full Mode (Default)

Complete pipeline: extract layout and generate output document.

```bash
# Full processing pipeline
python main.py --input document.pdf --output result.pdf

# Full pipeline with custom config location
python main.py --input document.pdf --output result.pdf --config custom_layout.json
```

### Examples

#### Basic Document Processing

```bash
# Process a PDF document
python main.py --input input/sample.pdf --output output/processed.pdf

# Process with verbose output
python main.py --input input/sample.pdf --output output/processed.pdf --verbose
```

#### Advanced Processing

```bash
# Extract layout only
python main.py --mode extract --input complex_document.pdf --config extracted_layout.json

# Generate from existing layout with modifications
python main.py --mode generate --config extracted_layout.json --output modified_output.pdf

# Create debug visualization
python main.py --mode debug --config extracted_layout.json --debugoutput debug_layers.pdf
```

#### Batch Processing

```bash
# Process multiple files
for file in input/*.pdf; do
    python main.py --input "$file" --output "output/$(basename "$file")"
done

# Process with consistent configuration
for file in input/*.pdf; do
    python main.py --mode generate --config template_layout.json --output "output/$(basename "$file")"
done
```

## Documentation Validation CLI

### Basic Usage

```bash
python scripts/validate_docs.py
```

The validation script automatically validates all documentation files in the `docs/` directory and provides comprehensive results with status indicators.

### Features

- **Code Examples**: Validates that code examples execute correctly
- **API References**: Validates that API references match actual implementation
- **Configuration Examples**: Validates JSON/JSON5 configuration examples
- **Comprehensive Reporting**: Provides detailed results with file paths and line numbers

### Output Format

The script provides formatted output with status indicators:

- ✅ Passed validation
- ❌ Failed validation
- ⚠️ Warning (non-critical issue)
- ⏭️ Skipped validation

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All validations passed |
| 1 | One or more validations failed |

## Additional CLI Scripts

### Batch Modification Validation

```bash
python scripts/validate_batch_modification.py
```

Validates the batch modification engine functionality including:

- Batch text replacement functionality
- Variable substitution capabilities
- Font validation system
- Substitution statistics generation

### Documentation Testing Framework

```bash
python scripts/test_docs_framework.py
```

Runs comprehensive documentation testing including:

- Code example execution
- API reference validation
- Configuration file validation
- Cross-reference checking

### Cleanup Script

```bash
python scripts/cleanup_old_files.py
```

Performs maintenance tasks:

- Removes temporary files
- Cleans up old output files
- Maintains font cache
- Preserves important directories

### Examples

#### Basic Validation

```bash
# Validate all documentation
python scripts/validate_docs.py --all

# Validate specific file
python scripts/validate_docs.py --file docs/README.md --all

# Validate only code examples
python scripts/validate_docs.py --examples
```

#### Advanced Validation

```bash
# Verbose validation with detailed output
python scripts/validate_docs.py --all --verbose

# Validate specific documentation type
python scripts/validate_docs.py --api-refs --verbose

# Stop on first failure for quick feedback
python scripts/validate_docs.py --all --fail-fast
```

#### Continuous Integration Usage

```bash
# CI-friendly validation
python scripts/validate_docs.py --all --quiet || exit 1

# Generate validation report
python scripts/validate_docs.py --all --verbose > validation_report.txt 2>&1
```

## Visual Comparison CLI

### Basic Usage

```bash
python -m src.compare_pdfs_visual [OPTIONS] ORIGINAL RECREATED
```

### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `ORIGINAL` | PATH | Original PDF file path |
| `RECREATED` | PATH | Recreated PDF file path |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output` | PATH | comparison.pdf | Output comparison file |
| `--threshold` | FLOAT | 0.95 | Similarity threshold (0.0-1.0) |
| `--show-differences` | FLAG | False | Highlight differences in output |
| `--page-range` | RANGE | All | Page range to compare (e.g., 1-5) |

### Examples

```bash
# Basic comparison
python -m src.compare_pdfs_visual original.pdf recreated.pdf

# Custom output and threshold
python -m src.compare_pdfs_visual original.pdf recreated.pdf \
  --output detailed_comparison.pdf --threshold 0.90

# Show differences with highlighting
python -m src.compare_pdfs_visual original.pdf recreated.pdf \
  --show-differences --output highlighted_diff.pdf

# Compare specific page range
python -m src.compare_pdfs_visual original.pdf recreated.pdf \
  --page-range 1-3 --output pages_1_3_comparison.pdf
```

## Schema Tools CLI

### Basic Usage

```bash
python -m src.tools.schema_tools [COMMAND] [OPTIONS]
```

### Commands

#### validate-config

Validate configuration file against schema.

```bash
python -m src.tools.schema_tools validate-config CONFIG_FILE

# Options:
#   --schema PATH    Custom schema file
#   --verbose        Detailed validation output
```

#### migrate-config

Migrate configuration file to newer schema version.

```bash
python -m src.tools.schema_tools migrate-config INPUT_FILE [OUTPUT_FILE]

# Options:
#   --backup         Create backup of original file
#   --force          Overwrite existing output file
#   --target-version VERSION  Target schema version
```

#### check-version

Check schema version of configuration file.

```bash
python -m src.tools.schema_tools check-version CONFIG_FILE

# Options:
#   --verbose        Show detailed version information
```

### Examples

```bash
# Validate configuration
python -m src.tools.schema_tools validate-config layout_config.json

# Migrate with backup
python -m src.tools.schema_tools migrate-config old_config.json new_config.json --backup

# Check version
python -m src.tools.schema_tools check-version layout_config.json --verbose
```

## Debug PDF Generator CLI

### Basic Usage

```bash
python -m src.generate_debug_pdf_layers [OPTIONS] CONFIG_FILE
```

### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `CONFIG_FILE` | PATH | Layout configuration file |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output` | PATH | debug_layers.pdf | Output debug PDF file |
| `--layers` | LIST | All | Specific layers to include |
| `--page-range` | RANGE | All | Page range to process |

### Examples

```bash
# Generate debug PDF for all layers
python -m src.generate_debug_pdf_layers layout_config.json

# Custom output file
python -m src.generate_debug_pdf_layers layout_config.json --output custom_debug.pdf

# Specific layers only
python -m src.generate_debug_pdf_layers layout_config.json --layers text,images

# Specific page range
python -m src.generate_debug_pdf_layers layout_config.json --page-range 1-3
```

## Batch Processing CLI

### Basic Usage

```bash
python -m src.engine.batch_modifier [OPTIONS] INPUT_DIR OUTPUT_DIR
```

### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `INPUT_DIR` | PATH | Directory containing input documents |
| `OUTPUT_DIR` | PATH | Directory for output documents |

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--pattern` | GLOB | File pattern to match (default: *.pdf) |
| `--config` | PATH | Configuration template file |
| `--parallel` | INT | Number of parallel processes |
| `--overwrite` | FLAG | Overwrite existing output files |

### Examples

```bash
# Process all PDFs in directory
python -m src.engine.batch_modifier input_docs/ output_docs/

# Process with specific pattern
python -m src.engine.batch_modifier input_docs/ output_docs/ --pattern "*.pdf"

# Parallel processing
python -m src.engine.batch_modifier input_docs/ output_docs/ --parallel 4

# Use configuration template
python -m src.engine.batch_modifier input_docs/ output_docs/ --config template.json
```

## Testing CLI

### Run Tests

```bash
# Run all tests
hatch run test

# Run specific test file
hatch run pytest tests/test_specific.py

# Run with coverage
hatch run test-cov

# Run tests with verbose output
hatch run pytest -v

# Run specific test class or method
hatch run pytest tests/test_file.py::TestClass::test_method
```

### Test Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Verbose output |
| `-s` | Don't capture output (show print statements) |
| `-x` | Stop on first failure |
| `--tb=short` | Short traceback format |
| `--cov` | Generate coverage report |
| `-k PATTERN` | Run tests matching pattern |

### Examples

```bash
# Run tests with coverage and verbose output
hatch run pytest -v --cov=src tests/

# Run only documentation tests
hatch run pytest -k "documentation" tests/

# Run tests and stop on first failure
hatch run pytest -x tests/

# Run specific test with output
hatch run pytest -s tests/test_specific.py::test_function
```

## Linting and Formatting CLI

### Code Formatting

```bash
# Format code with Black
hatch run style

# Check formatting without changes
hatch run black --check src/ tests/

# Format specific files
hatch run black src/specific_file.py
```

### Linting

```bash
# Run Ruff linter
hatch run lint:lint

# Check specific files
hatch run ruff check src/specific_file.py

# Auto-fix issues
hatch run ruff check --fix src/
```

### Combined Quality Checks

```bash
# Run all quality checks
hatch run lint:lint && hatch run style

# Check everything before commit
hatch run test && hatch run lint:lint && hatch run style
```

## Environment Management CLI

### Hatch Environment Commands

```bash
# Create environment
hatch env create

# Show environment info
hatch env show

# Remove environment
hatch env prune

# Enter environment shell
hatch shell

# Run command in environment
hatch run COMMAND
```

### Package Management

```bash
# Install package in environment
hatch run pip install PACKAGE

# Install in development mode
hatch run pip install -e .

# List installed packages
hatch run pip list

# Show package information
hatch run pip show PACKAGE
```

## Exit Codes

All CLI tools use standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Misuse of shell command |
| 126 | Command invoked cannot execute |
| 127 | Command not found |
| 128+n | Fatal error signal "n" |

### Application-Specific Exit Codes

| Code | Meaning |
|------|---------|
| 10 | Configuration error |
| 11 | Input file error |
| 12 | Output file error |
| 13 | Processing error |
| 14 | Validation error |

## Configuration Files for CLI

### Default Configuration Locations

The CLI tools look for configuration files in this order:

1. Command-line specified path
2. Current directory
3. User home directory
4. System-wide configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PDF_ENGINE_CONFIG` | Default configuration file | layout_config.json |
| `PDF_ENGINE_DEBUG` | Enable debug mode | False |
| `PDF_ENGINE_VERBOSE` | Enable verbose output | False |

## Shell Completion

### Bash Completion

```bash
# Add to ~/.bashrc
eval "$(_MAIN_COMPLETE=bash_source python main.py)"
```

### Zsh Completion

```bash
# Add to ~/.zshrc
eval "$(_MAIN_COMPLETE=zsh_source python main.py)"
```

## Makefile Commands

The project includes a comprehensive Makefile with predefined commands for common tasks.

### Documentation Commands

| Command | Description |
|---------|-------------|
| `make docs` | Run all documentation tasks (validate + test) |
| `make docs-validate` | Validate documentation accuracy |
| `make docs-validate-examples` | Validate only code examples |
| `make docs-validate-api` | Validate only API references |
| `make docs-validate-config` | Validate only configuration examples |
| `make docs-test` | Run documentation validation tests |
| `make docs-test-framework` | Run comprehensive documentation testing |
| `make docs-build` | Build complete documentation |
| `make docs-workflow` | Run complete documentation workflow |
| `make docs-clean` | Clean generated documentation files |

### Development Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-docs` | Run only documentation-related tests |
| `make lint` | Run linting with ruff |
| `make format` | Format code with black |

### Setup and Maintenance Commands

| Command | Description |
|---------|-------------|
| `make install` | Install project dependencies |
| `make clean` | Clean build artifacts |
| `make help` | Show available commands |

### Usage Examples

```bash
# Run complete documentation workflow
make docs-workflow

# Quick validation of documentation
make docs-validate

# Run tests and linting
make test lint

# Clean and reinstall
make clean install
```

## Integration Examples

### Makefile Integration

```makefile
# Process documents
process-docs:
 python main.py --input input/document.pdf --output output/processed.pdf

# Validate documentation
validate-docs:
 python scripts/validate_docs.py --all

# Run quality checks
quality-check:
 hatch run test && hatch run lint:lint && python scripts/validate_docs.py --all
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Process Documents
  run: |
    python main.py --input test_document.pdf --output processed.pdf

- name: Validate Documentation
  run: |
    python scripts/validate_docs.py --all --fail-fast
```

This CLI reference covers all command-line interfaces available in the Multi-Format Document Engine. For detailed usage examples, see the guides and examples in the documentation.
