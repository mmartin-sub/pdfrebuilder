# Multi-Format Document Engine Documentation

This directory contains comprehensive documentation for the Multi-Format Document Engine project.

## Documentation Structure

### Core Documentation

- [README.md](../README.md) - Project overview and quick start
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [SECURITY.md](SECURITY.md) - Security considerations and guidelines
- [MIGRATION.md](MIGRATION.md) - Version migration guides
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

### API Documentation

- [api/](api/) - Complete API documentation
  - [core/](api/core/) - Core API documentation
  - [engines/](api/engines/) - Engine-specific APIs
  - [models/](api/models/) - Data model documentation
  - [tools/](api/tools/) - Utility APIs

### User Guides

- [guides/](guides/) - User guides and tutorials
  - [getting-started.md](guides/getting-started.md) - Basic usage guide
  - [advanced-usage.md](guides/advanced-usage.md) - Advanced features
  - [batch-processing.md](guides/batch-processing.md) - Batch operations
  - [visual-validation.md](guides/visual-validation.md) - Validation procedures
  - [troubleshooting.md](guides/troubleshooting.md) - Common issues and solutions

### Code Examples

- [examples/](examples/) - Code examples and samples
  - [basic/](examples/basic/) - Basic usage examples
  - [advanced/](examples/advanced/) - Advanced scenarios
  - [integration/](examples/integration/) - Integration examples

### Reference Documentation

- [reference/](reference/) - Reference documentation
  - [configuration.md](reference/configuration.md) - Configuration reference
  - [cli.md](reference/cli.md) - CLI reference
  - [error-codes.md](reference/error-codes.md) - Error reference

## Documentation Generation and Validation

This documentation includes automated validation and generation tools to ensure accuracy and consistency:

- Code examples are tested against the current codebase
- API references are validated against actual implementation
- Configuration examples are verified for correctness
- Links and cross-references are checked automatically

### Documentation Management

See [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) for complete instructions on:

- Using Makefile targets for documentation management
- Setting up git hooks for automatic validation
- CI/CD integration examples
- Troubleshooting and best practices

### Quick Commands

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

## Contributing to Documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on updating and maintaining documentation.
