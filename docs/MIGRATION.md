# Migration Guide

This document provides guidance for migrating between versions of the Multi-Format Document Engine. Since this project is currently in pre-release development (version 0.1.0), most migration scenarios are related to development workflow changes rather than production deployments.

## Development Status: Pre-Release (0.1.0)

**Important Note**: This project is currently in active development and has not been released for production use. The migration procedures documented here are primarily for:

- Development environment updates
- Configuration format changes during development
- Dependency updates and Python version changes
- Workflow improvements and tooling changes

## Current Development Migration Scenarios

## Development Environment Migration

### Switching to Hatch + UV (Current Development Standard)

If you're working with an older development setup, here's how to migrate to the current development environment:

#### From pip + venv to Hatch + UV

**Old development setup:**

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**New development setup:**

```bash
# Install hatch and uv globally
pip install hatch uv

# Create and activate environment
hatch shell

# All dependencies are managed through pyproject.toml
```

#### Benefits of the Migration

- **Faster dependency resolution** with UV
- **Reproducible environments** with lock files
- **Integrated tooling** for testing, linting, and formatting
- **Better dependency management** with optional dependency groups

### Configuration Schema Evolution

The project uses a Universal Document Structure Schema that may evolve during development. The schema migration tools are designed to handle these changes:

#### Using Schema Migration Tools

```bash
# Check if your configuration needs migration
python -c "
from src.models.schema_migration import get_schema_version
import json

with open('layout_config.json', 'r') as f:
    config = json.load(f)

version = get_schema_version(config)
print(f'Current schema version: {version}')

if version != '1.0':
    print('Migration may be needed')
else:
    print('Schema is current')
"

# Migrate configuration if needed
python -c "
from src.models.schema_migration import migrate_document_file

try:
    migrate_document_file('layout_config.json', 'layout_config_migrated.json')
    print('Migration successful')
except Exception as e:
    print(f'Migration failed: {e}')
"
```

#### Configuration Format Evolution

The current schema (v1.0) uses a layered document structure. If you have older configuration files, they can be automatically migrated:

**Current Format (v1.0):**

```json
{
  "version": "1.0",
  "engine": "fitz",
  "engine_version": "PyMuPDF 1.26.23",
  "metadata": {},
  "document_structure": [
    {
      "type": "page",
      "page_number": 0,
      "size": [1058.0, 1688.0],
      "layers": [
        {
          "layer_id": "page_0_base_layer",
          "layer_name": "Page Content",
          "layer_type": "base",
          "content": [
            {
              "type": "text",
              "text": "Sample text",
              "bbox": [100, 100, 200, 120],
              "id": "text_0"
            }
          ]
        }
      ]
    }
  ]
}
```

## Dependency Updates During Development

### Updating Dependencies

Since this is a development project, dependency updates are straightforward:

```bash
# Update all dependencies
hatch env prune
hatch env create

# Test after updates
hatch run test

# Check for any issues
hatch run python main.py --input input/sample.pdf --mode extract
```

### Key Dependencies to Monitor

- **PyMuPDF**: Core PDF processing - test thoroughly after updates
- **Pillow**: Image processing - verify image extraction still works
- **psd-tools**: PSD processing - test PSD functionality if using
- **defusedxml**: Security - keep updated for security fixes

### Python Version Updates

The project currently targets Python 3.12. To update:

1. Update `pyproject.toml`:

   ```toml
   [tool.hatch.envs.default]
   python = "3.13"  # or desired version
   ```

2. Test compatibility:

   ```bash
   hatch env create
   hatch run test
   ```

## Development Workflow Changes

### Current Development Workflow

The project uses modern Python tooling:

```bash
# Setup (one time)
pip install hatch uv
hatch shell

# Daily development
hatch run python main.py --input sample.pdf    # Run application
hatch run test                                  # Run tests
hatch run lint:lint                            # Lint code
hatch run style                                # Format code
```

### CI/CD Configuration

The project includes GitHub Actions for automated testing. The current workflow:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install UV
        run: pip install uv
      - name: Install Hatch
        run: pip install hatch
      - name: Run tests
        run: hatch run test
```

### Docker Development

For containerized development:

```dockerfile
FROM python:3.12-slim
RUN pip install hatch uv
COPY pyproject.toml .
COPY src/ src/
RUN hatch env create
CMD ["hatch", "run", "python", "main.py"]
```

## Common Development Migration Scenarios

### Updating Configuration Files

If you have existing `layout_config.json` files that need updating:

```bash
# Check if migration is needed
python -c "
from src.models.schema_migration import get_schema_version
import json

with open('layout_config.json', 'r') as f:
    config = json.load(f)

version = get_schema_version(config)
print(f'Schema version: {version}')
"

# Migrate if needed
python -c "
from src.models.schema_migration import migrate_document_file
migrate_document_file('layout_config.json', 'layout_config_updated.json')
print('Migration complete')
"
```

### Font Directory Organization

The project expects fonts in specific directories:

```bash
# Current structure
fonts/
├── cache/          # Font cache (auto-generated)
├── downloaded/     # Downloaded fonts
└── README.md       # Font documentation

# If you have fonts elsewhere, move them:
mkdir -p fonts/downloaded
mv your_fonts/*.ttf fonts/downloaded/
```

## Development Best Practices

### Before Making Changes

1. **Backup your work**: Use git to commit your current state
2. **Test current functionality**: Run `hatch run test` to ensure everything works
3. **Document changes**: Note what you're changing and why

### After Updates

1. **Test thoroughly**: Run the full test suite
2. **Check examples**: Verify that examples still work
3. **Update documentation**: If you change APIs or configuration formats

### Configuration Validation

Always validate configuration files after changes:

```bash
# Test configuration loading
python -c "
import json
with open('layout_config.json', 'r') as f:
    config = json.load(f)
print('Configuration loaded successfully')
"

# Test with actual processing
hatch run python main.py --config layout_config.json --mode extract --input input/sample.pdf
```

## Troubleshooting Common Issues

### Environment Issues

**Problem**: Dependencies not installing correctly

**Solution**:

```bash
# Clean and recreate environment
hatch env prune
hatch env create

# Verify installation
hatch run python -c "import src; print('Success')"
```

**Problem**: Import errors

**Solution**:

```bash
# Check if you're in the right directory
ls src/  # Should show engine/, models/, etc.

# Make sure you're using hatch
hatch shell
python -c "import src.engine.document_parser"
```

### Configuration Issues

**Problem**: Configuration file not loading

**Solution**:

```bash
# Check JSON syntax
python -c "
import json
with open('layout_config.json', 'r') as f:
    json.load(f)
print('JSON is valid')
"

# Check schema version
python -c "
from src.models.schema_migration import get_schema_version
import json
with open('layout_config.json', 'r') as f:
    config = json.load(f)
print('Schema version:', get_schema_version(config))
"
```

### Font Issues

**Problem**: Fonts not found

**Solution**:

```bash
# Check font directories
ls fonts/downloaded/  # Should contain .ttf files

# Test font manager
python -c "
from src.font.font_manager import FontManager
fm = FontManager()
print('Font manager initialized')
"
```

## Getting Help

### Documentation Resources

- [Installation Guide](INSTALLATION.md) - Setup instructions
- [Troubleshooting Guide](guides/troubleshooting.md) - Common issues
- [Configuration Reference](reference/configuration.md) - Configuration options
- [API Documentation](api/README.md) - Code reference

### Validation Tools

```bash
# Validate configuration
python -c "
import json
with open('layout_config.json', 'r') as f:
    config = json.load(f)
print('Configuration is valid')
"

# Test basic functionality
hatch run python main.py --input input/sample.pdf --mode extract

# Run tests
hatch run test
```

## Development Status and Roadmap

### Current Status (0.1.0)

This is a **pre-release development version**. The project includes:

- PDF extraction and reconstruction
- Basic PSD support
- Engine abstraction layer
- Font management system
- Comprehensive test suite

### Future Development

As the project evolves, migration procedures will be added for:

- **Configuration format changes**: When the Universal Document Structure Schema evolves
- **API changes**: When interfaces are updated or improved
- **Dependency updates**: When major dependencies are updated
- **Feature additions**: When new engines or capabilities are added

### Contributing to Migration Documentation

If you encounter migration scenarios not covered here:

1. Document the issue and solution
2. Test the solution thoroughly
3. Add examples to help other developers
4. Update this guide with your findings

For a pre-release project, the focus is on **development workflow** rather than production migration scenarios.
