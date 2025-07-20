# Scripts Directory

This directory contains utility and maintenance scripts for the PDF Layout Extractor and Rebuilder project.

## Available Scripts

### Batch Modification Validation (`validate_batch_modification.py`)

Validation script for testing the batch modification engine functionality.

**Purpose:**

- Validates batch text replacement functionality
- Tests variable substitution capabilities
- Verifies font validation system
- Checks substitution statistics generation

**Usage:**

```bash
# From project root
python scripts/validate_batch_modification.py
```

**Features:**

- Comprehensive testing of batch modification workflows
- Validation of example script functionality
- Error detection and reporting
- Performance verification

## Running Scripts

All scripts should be run from the project root directory to ensure proper path resolution:

```bash
# Correct way to run scripts
cd /path/to/project/root
python scripts/script_name.py
```

## Adding New Scripts

When adding new utility scripts:

1. **Location**: Place the script in this `scripts/` directory
2. **Naming**: Use descriptive names with underscores (snake_case)
3. **Documentation**: Include comprehensive docstrings explaining the script's purpose
4. **Path Handling**: Use proper path resolution for project files
5. **README**: Update this README with details about the new script

## Purpose

These scripts serve various purposes:

- **Validation**: Verify system functionality and performance
- **Maintenance**: Perform routine maintenance tasks
- **Utilities**: Provide helpful tools for development and deployment
- **Testing**: Support testing workflows and validation

## Related Documentation

- **Examples**: See `examples/` directory for usage examples
- **Tests**: See `tests/` directory for test-related scripts
- **Main Documentation**: See the project README for overall system documentation
