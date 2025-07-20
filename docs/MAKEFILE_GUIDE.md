# Makefile Documentation Guide

This guide explains how to use the Makefile to generate, validate, and maintain documentation for the Multi-Format Document Engine.

## Overview

The Makefile provides a comprehensive set of targets for documentation management, from validation and testing to building complete documentation sets. This ensures documentation quality and consistency across the project.

## Quick Start

```bash
# Show all available documentation commands
make help

# Run complete documentation workflow
make docs-workflow

# Validate documentation accuracy
make docs-validate

# Build complete documentation
make docs-build
```

## Documentation Targets

### Core Documentation Commands

| Target | Description | Use Case |
|--------|-------------|----------|
| `make docs` | Run all documentation tasks (validate + test) | Daily development workflow |
| `make docs-workflow` | Complete documentation workflow | Before releases |
| `make docs-build` | Build complete documentation | Generate final docs |
| `make docs-clean` | Clean generated documentation files | Maintenance |

### Validation Commands

| Target | Description | Use Case |
|--------|-------------|----------|
| `make docs-validate` | Validate all documentation | Quality assurance |
| `make docs-validate-examples` | Validate only code examples | Example testing |
| `make docs-validate-api` | Validate only API references | API documentation |
| `make docs-validate-config` | Validate only configuration examples | Config documentation |

### Testing Commands

| Target | Description | Use Case |
|--------|-------------|----------|
| `make docs-test` | Run documentation validation tests | Automated testing |
| `make docs-test-framework` | Run comprehensive documentation testing framework | Deep testing |

## Detailed Usage Examples

### 1. Daily Development Workflow

```bash
# Start your day with documentation validation
make docs-validate

# If validation passes, run tests
make docs-test

# Build documentation if needed
make docs-build
```

### 2. Pre-Release Documentation Check

```bash
# Run complete documentation workflow
make docs-workflow

# This runs:
# 1. docs-validate - Validates all documentation
# 2. docs-test - Runs documentation tests
# 3. docs-build - Builds complete documentation
```

### 3. Focused Validation

```bash
# Validate only code examples (faster for development)
make docs-validate-examples

# Validate only API references
make docs-validate-api

# Validate only configuration examples
make docs-validate-config
```

### 4. Documentation Testing

```bash
# Run basic documentation tests
make docs-test

# Run comprehensive testing framework
make docs-test-framework
```

### 5. Maintenance Tasks

```bash
# Clean generated documentation files
make docs-clean

# Clean all build artifacts (includes docs)
make clean
```

## Git Hooks Setup

To automatically validate documentation on commits and pushes, set up git hooks:

### 1. Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "🔍 Running documentation validation..."

# Run documentation validation
make docs-validate

if [ $? -ne 0 ]; then
    echo "❌ Documentation validation failed!"
    echo "Please fix documentation issues before committing."
    exit 1
fi

echo "✅ Documentation validation passed!"
exit 0
```

### 2. Pre-push Hook

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash

echo "🧪 Running complete documentation workflow..."

# Run complete documentation workflow
make docs-workflow

if [ $? -ne 0 ]; then
    echo "❌ Documentation workflow failed!"
    echo "Please fix documentation issues before pushing."
    exit 1
fi

echo "✅ Documentation workflow completed successfully!"
exit 0
```

### 3. Make Hooks Executable

```bash
# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### 4. Alternative: Using Husky (if using Node.js)

If your project uses Node.js, you can use Husky for git hooks:

```bash
# Install Husky
npm install --save-dev husky

# Initialize Husky
npx husky install

# Add pre-commit hook
npx husky add .husky/pre-commit "make docs-validate"

# Add pre-push hook
npx husky add .husky/pre-push "make docs-workflow"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Documentation Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  docs-validation:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install hatch
        hatch env create

    - name: Validate documentation
      run: make docs-validate

    - name: Test documentation
      run: make docs-test

    - name: Build documentation
      run: make docs-build
```

### GitLab CI Example

```yaml
documentation:
  stage: test
  image: python:3.12
  before_script:
    - pip install hatch
    - hatch env create
  script:
    - make docs-workflow
  only:
    - main
    - develop
    - merge_requests
```

## Troubleshooting

### Common Issues

1. **Validation Fails**: Check that all code examples are up-to-date
2. **API References Missing**: Ensure all public APIs are documented
3. **Configuration Examples Invalid**: Verify configuration examples match current schema
4. **Build Fails**: Check for syntax errors in documentation files

### Debug Commands

```bash
# Run validation with verbose output
hatch run python scripts/validate_docs.py --all --verbose

# Run specific validation with debug info
hatch run python scripts/validate_docs.py --examples --verbose --debug

# Check documentation builder directly
hatch run python -c "
from src.docs.validation import DocumentationBuilder
builder = DocumentationBuilder()
results = builder.build_complete_docs()
print('Build results:', results)
"
```

## Best Practices

### 1. Regular Validation

- Run `make docs-validate` before committing changes
- Use git hooks to automate validation
- Include documentation validation in CI/CD pipelines

### 2. Incremental Updates

- Use focused validation commands for faster feedback
- Validate only changed sections when possible
- Run full workflow before releases

### 3. Documentation Maintenance

- Keep examples up-to-date with code changes
- Update API references when interfaces change
- Validate configuration examples when schema changes

### 4. Team Collaboration

- Share documentation validation results in PRs
- Use consistent documentation standards
- Document new features with examples

## Advanced Usage

### Custom Validation Scripts

You can extend the Makefile with custom validation scripts:

```makefile
# Add to Makefile
docs-validate-custom:  ## Run custom validation
 @echo "Running custom validation..."
 hatch run python scripts/custom_validation.py

docs-validate-all: docs-validate docs-validate-custom  ## Run all validations
```

### Documentation Metrics

Track documentation quality with metrics:

```bash
# Count documentation files
find docs/ -name "*.md" | wc -l

# Check documentation coverage
hatch run python scripts/docs_coverage.py

# Generate documentation report
hatch run python scripts/docs_report.py
```

## Related Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [API.md](API.md) - API documentation
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

## Support

For issues with documentation generation or validation:

1. Check the troubleshooting section above
2. Review the validation scripts in `scripts/`
3. Check the documentation builder in `src.docs.validation`
4. Open an issue with detailed error information
