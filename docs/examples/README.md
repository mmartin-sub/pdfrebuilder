# Documentation Examples

This directory contains working code examples for the Multi-Format Document Engine.

## Structure

- **basic/**: Simple examples for getting started
- **advanced/**: Complex scenarios and advanced usage
- **integration/**: Integration examples with other systems

## Example Categories

### Basic Examples

Simple, self-contained examples that demonstrate core functionality:

- **basic_pdf_processing.py**: Extract and recreate PDF documents
- **configuration_example.py**: Working with configuration files
- **font_management.py**: Managing fonts and typography
- **image_extraction.py**: Extracting and processing images

### Advanced Examples

Complex examples showing real-world usage patterns:

- **batch_processing.py**: Processing multiple documents
- **custom_validation.py**: Implementing custom validation rules
- **template_mode.py**: Using template mode for complex layouts
- **performance_optimization.py**: Optimizing for large documents

### Integration Examples

Examples showing integration with other tools and systems:

- **ci_cd_integration.py**: Continuous integration workflows
- **web_service_integration.py**: REST API integration
- **database_integration.py**: Storing and retrieving document data
- **cloud_storage.py**: Working with cloud storage services

## Running Examples

All examples are designed to be executable and include proper error handling:

```bash
# Run a basic example
python docs/examples/basic/basic_pdf_processing.py

# Run with sample data
python docs/examples/advanced/batch_processing.py --input input/ --output output/
```

## Validation

All examples are automatically validated to ensure they work with the current codebase:

```bash
# Validate all examples
make docs-validate-examples

# Run comprehensive testing
python scripts/test_docs_framework.py --examples
```

## Contributing Examples

When adding new examples:

1. **Make them executable**: Include proper main() function and error handling
2. **Add documentation**: Clear comments and docstrings
3. **Include sample data**: Provide or reference test files
4. **Test thoroughly**: Ensure examples work in clean environment
5. **Follow naming conventions**: Use descriptive, consistent names

### Example Template

```python
#!/usr/bin/env python3
"""
Example: [Brief Description]

This example demonstrates [detailed description of what it shows].

Requirements:
- Python 3.8+
- Multi-Format Document Engine
- [Any additional requirements]

Usage:
    python example_name.py [arguments]
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Your imports here
from src.engine.document_parser import DocumentParser


def main():
    """Main example function."""
    print("Example: [Brief Description]")
    print("=" * 50)

    try:
        # Your example code here
        parser = DocumentParser()
        result = parser.parse("sample.pdf")

        print(f"✅ Example completed successfully")
        print(f"Result: {result}")
        return True

    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Testing Examples

Examples are tested in multiple ways:

1. **Syntax validation**: Code is parsed for syntax errors
2. **Execution testing**: Examples are run to ensure they work
3. **Output validation**: Expected outputs are verified
4. **Integration testing**: Examples are tested with real data

## Maintenance

Examples are maintained through:

- **Automated testing** in CI/CD pipelines
- **Regular validation** against current codebase
- **User feedback** and issue reports
- **Version updates** when APIs change

For questions about examples, see the [Troubleshooting Guide](../guides/troubleshooting.md) or [Contributing Guide](../CONTRIBUTING.md).
