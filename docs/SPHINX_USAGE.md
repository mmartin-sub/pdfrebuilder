# Sphinx Documentation System Usage

This document explains how to use the new Sphinx-based documentation system for the Multi-Format Document Engine.

## Overview

The documentation system uses Sphinx with the Read the Docs theme to generate professional documentation from reStructuredText files and Python docstrings.

## Available Commands

### Build Documentation

```bash
# Build HTML documentation
hatch run docs:build

# Clean previous builds
hatch run docs:clean

# Build and clean in one command
hatch run docs:clean && hatch run docs:build
```

### Live Preview

```bash
# Start live preview server (auto-opens browser)
hatch run docs:live

# The server will automatically:
# - Rebuild documentation when files change
# - Refresh the browser
# - Watch both RST files and Python source code
```

### Multi-format Output

```bash
# Build PDF documentation
hatch run docs:build-pdf

# Build EPUB documentation
hatch run docs:build-epub

# Check for broken links
hatch run docs:linkcheck
```

## Documentation Structure

```
docs/
├── source/                 # Sphinx source files
│   ├── conf.py            # Sphinx configuration
│   ├── index.rst          # Main documentation index
│   ├── api/               # API documentation
│   ├── guides/            # User guides
│   ├── examples/          # Code examples
│   ├── reference/         # Reference documentation
│   └── _static/           # Static assets
└── build/                 # Generated documentation
    ├── html/              # HTML output
    ├── latex/             # LaTeX output (for PDF)
    └── epub/              # EPUB output
```

## Writing Documentation

### reStructuredText Basics

The documentation uses reStructuredText (RST) format. Here are common patterns:

#### Headers

```rst
Main Title
==========

Section Title
-------------

Subsection Title
~~~~~~~~~~~~~~~~
```

#### Code Blocks

```rst
.. code-block:: python

   from pdfrebuilder.engine import DocumentEngine

   engine = DocumentEngine()
   layout = engine.extract("input.pdf")
```

#### Cross-references

```rst
# Link to other documents
:doc:`getting-started`

# Link to API documentation
:class:`pdfrebuilder.engine.DocumentEngine`
:meth:`pdfrebuilder.engine.DocumentEngine.extract`
```

#### Notes and Warnings

```rst
.. note::
   This is an informational note.

.. warning::
   This is a warning message.

.. code-block:: bash
   :caption: Example command

   hatch run docs:build
```

### API Documentation

API documentation is automatically generated from Python docstrings using Sphinx autodoc. To document a new module:

1. Add the module to the appropriate API file in `docs/source/api/`
2. Use the `automodule` directive:

```rst
New Module
----------

.. automodule:: pdfrebuilder.new_module
   :members:
   :undoc-members:
   :show-inheritance:
```

### Adding New Sections

To add a new documentation section:

1. Create the RST file in the appropriate directory
2. Add it to the relevant `index.rst` file's toctree:

```rst
.. toctree::
   :maxdepth: 2

   existing-page
   new-page
```

## Configuration

### Sphinx Configuration

The main configuration is in `docs/source/conf.py`. Key settings:

- **Extensions**: Controls which Sphinx extensions are enabled
- **Theme options**: Customizes the appearance
- **Autodoc options**: Controls API documentation generation

### Hatch Environment

The documentation environment is configured in `pyproject.toml`:

```toml
[tool.hatch.envs.docs]
detached = true
dependencies = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=2.0.0",
    # ... other dependencies
]

[tool.hatch.envs.docs.scripts]
build = "sphinx-build docs/source docs/build/html"
live = "sphinx-autobuild docs/source docs/build/html --open-browser --watch src/"
# ... other scripts
```

## Troubleshooting

### Common Issues

#### Import Errors in API Documentation

If you see warnings about failed imports:

1. Check that the module exists and is importable
2. Verify dependencies are installed in the docs environment
3. Add missing dependencies to the docs environment in `pyproject.toml`

#### Missing Files Warnings

If you see "toctree contains reference to nonexisting document":

1. Create the missing RST file
2. Or remove the reference from the toctree

#### Build Failures

If the build fails:

1. Check the error message for specific issues
2. Ensure all RST syntax is correct
3. Verify all cross-references are valid

### Debugging

Enable verbose output:

```bash
# Build with verbose output
sphinx-build -v docs/source docs/build/html

# Build with even more verbose output
sphinx-build -vv docs/source docs/build/html
```

## Best Practices

### Writing Style

- Use clear, concise language
- Include practical examples
- Provide context for code snippets
- Use consistent terminology

### Code Examples

- Test all code examples to ensure they work
- Include necessary imports
- Show expected output when relevant
- Use realistic data in examples

### Organization

- Group related content together
- Use consistent file naming
- Keep individual files focused on specific topics
- Cross-reference related content

### Maintenance

- Update documentation when code changes
- Review and update examples regularly
- Check for broken links periodically
- Keep dependencies up to date

## Integration with Development

### Pre-commit Hooks

Consider adding documentation builds to pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: docs-build
        name: Build documentation
        entry: hatch run docs:build
        language: system
        pass_filenames: false
```

### CI/CD Integration

Add documentation building to your CI/CD pipeline:

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Hatch
        run: pip install hatch
      - name: Build documentation
        run: hatch run docs:build
      - name: Check links
        run: hatch run docs:linkcheck
```

## Advanced Features

### Custom Directives

You can add custom Sphinx directives for specialized content:

```rst
.. custom-directive::
   :option: value

   Content here
```

### Internationalization

Sphinx supports multiple languages. To add translations:

1. Configure locales in `conf.py`
2. Generate translation files
3. Translate content
4. Build localized versions

### Custom Themes

To customize the appearance beyond theme options:

1. Create custom CSS in `docs/source/_static/`
2. Add custom templates
3. Configure in `conf.py`

This Sphinx documentation system provides a professional, maintainable foundation for the project's documentation needs.
