# Design Document

## Overview

This design outlines the migration strategy for reorganizing the PDFRebuilder project from a flat `src/` structure to a proper Python package structure under `src/pdfrebuilder/`. The migration will follow Python packaging best practices while maintaining all existing functionality and providing a clear upgrade path for users.

## Architecture

### Current Structure Analysis

```
src/
├── __init__.py                    # Root package init
├── cli.py                        # Main CLI (duplicate)
├── settings.py                   # Configuration constants
├── *.py                         # Core modules (flat structure)
├── cli/                         # CLI subpackage
│   ├── __init__.py
│   ├── batch_modifier_cli.py
│   └── commands/
├── pdfrebuilder/                # Partial new structure (incomplete)
│   ├── __init__.py
│   └── cli.py                   # CLI duplicate
├── config/                      # Configuration management
├── engine/                      # PDF processing engines
├── font/                        # Font utilities
├── models/                      # Data models
├── security/                    # Security utilities
├── tools/                       # General utilities
└── utils/                       # Utility functions
```

### Target Structure Design

```
src/
├── __init__.py                  # Empty or minimal (for build compatibility)
└── pdfrebuilder/                # Main package - ALL code goes here
    ├── __init__.py              # Public API exports
    ├── cli.py                   # Consolidated CLI entry point
    ├── settings.py              # Configuration constants
    ├── fritz.py                 # Fritz utility (moved from src/)
    ├── font_utils.py            # Font utilities (moved from src/)
    ├── core/                    # Core functionality (moved from src/)
    │   ├── __init__.py
    │   ├── extract_pdf_content.py  # (was src/extract_pdf_content.py)
    │   ├── recreate_pdf_from_config.py  # (was src/recreate_pdf_from_config.py)
    │   ├── render.py            # (was src/render.py)
    │   ├── compare_pdfs_visual.py  # (was src/compare_pdfs_visual.py)
    │   ├── generate_debug_pdf_layers.py  # (was src/generate_debug_pdf_layers.py)
    │   └── pdf_engine.py        # (was src/pdf_engine.py)
    ├── cli/                     # CLI subcommands (moved from src/cli/)
    │   ├── __init__.py
    │   ├── commands/
    │   │   └── reportlab_cli.py
    │   └── batch_modifier_cli.py
    ├── config/                  # Configuration management (moved from src/config/)
    │   ├── __init__.py
    │   ├── manager.py
    │   └── models.py
    ├── engine/                  # PDF processing engines (moved from src/engine/)
    │   ├── __init__.py
    │   ├── batch_modifier.py
    │   ├── config_loader.py
    │   ├── document_parser.py
    │   ├── document_renderer.py
    │   ├── extract_pdf_content_fitz.py
    │   ├── extract_psd_content.py
    │   ├── extract_wand_content.py
    │   ├── pdf_engine_selector.py
    │   ├── pymupdf_engine.py
    │   ├── reportlab_engine.py
    │   └── ... (all other engine files)
    ├── font/                    # Font utilities (moved from src/font/)
    │   ├── __init__.py
    │   ├── font_validator.py
    │   └── googlefonts.py
    ├── models/                  # Data models (moved from src/models/)
    │   ├── __init__.py
    │   ├── universal_idm.py
    │   ├── schema_migration.py
    │   ├── schema_validator.py
    │   ├── psd_effects.py
    │   ├── psd_validator.py
    │   └── __init__.py
    ├── security/                # Security utilities (moved from src/security/)
    │   ├── __init__.py
    │   ├── path_utils.py
    │   ├── secure_execution.py
    │   ├── subprocess_compatibility.py
    │   └── subprocess_utils.py
    ├── tools/                   # General utilities (moved from src/tools/)
    │   ├── __init__.py
    │   ├── generic.py
    │   └── schema_tools.py
    └── utils/                   # Utility functions (moved from src/utils/)
        ├── __init__.py
        └── directory_utils.py
```

**Key Changes:**
- **Everything moves to `src/pdfrebuilder/`** - no modules remain directly under `src/`
- `src/__init__.py` becomes empty or minimal (kept only for build system compatibility)
- All current `src/*.py` files move to appropriate locations under `src/pdfrebuilder/`
- All current `src/*/` subdirectories move directly under `src/pdfrebuilder/`
- Remove the duplicate `src/pdfrebuilder/` directory that currently exists

## Components and Interfaces

### 1. Package Root (`src/pdfrebuilder/__init__.py`)

**Purpose:** Define the public API and expose key functionality for external users.

**Design:**
```python
"""PDFRebuilder - Extract and rebuild PDF layouts with high fidelity."""

__version__ = "0.1.0"

# Public API exports
from .core.extract_pdf_content import extract_pdf_content
from .core.recreate_pdf_from_config import recreate_pdf_from_config
from .core.render import render_element
from .core.compare_pdfs_visual import compare_pdfs_visual
from .engine.document_parser import parse_document
from .models.universal_idm import UniversalDocumentModel

# CLI entry point
from .cli import main as cli_main

__all__ = [
    "extract_pdf_content",
    "recreate_pdf_from_config", 
    "render_element",
    "compare_pdfs_visual",
    "parse_document",
    "UniversalDocumentModel",
    "cli_main",
]
```

### 2. CLI Consolidation (`src/pdfrebuilder/cli.py`)

**Purpose:** Single entry point for all CLI functionality, consolidating the duplicate CLI implementations.

**Design:**
- Merge functionality from both `src/cli.py` and `src/pdfrebuilder/cli.py`
- Update all imports to use new package structure
- Maintain all existing CLI arguments and behavior
- Use relative imports within the package

### 3. Core Module Organization (`src/pdfrebuilder/core/`)

**Purpose:** House the main PDF processing functionality in a dedicated namespace.

**Modules:**
- `extract_pdf_content.py` - PDF content extraction
- `recreate_pdf_from_config.py` - PDF reconstruction
- `render.py` - Element rendering utilities
- `compare_pdfs_visual.py` - Visual comparison tools
- `generate_debug_pdf_layers.py` - Debug visualization
- `pdf_engine.py` - Legacy engine compatibility

### 4. Import Strategy

**Internal Imports:** Use relative imports within the package
```python
# Within pdfrebuilder package
from .core.extract_pdf_content import extract_pdf_content
from ..models.universal_idm import UniversalDocumentModel
```

**External Imports:** Use absolute imports from the package root
```python
# From external code
from pdfrebuilder import extract_pdf_content, parse_document
from pdfrebuilder.engine.document_parser import DocumentParser
```

## Data Models

### Migration Mapping

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `src/__init__.py` | `src/__init__.py` | Keep minimal/empty for build compatibility |
| `src/cli.py` | `src/pdfrebuilder/cli.py` | Consolidate with existing duplicate |
| `src/settings.py` | `src/pdfrebuilder/settings.py` | Direct move |
| `src/fritz.py` | `src/pdfrebuilder/fritz.py` | Direct move |
| `src/font_utils.py` | `src/pdfrebuilder/font_utils.py` | Direct move |
| `src/compare_pdfs_visual.py` | `src/pdfrebuilder/core/compare_pdfs_visual.py` | Move to core |
| `src/generate_debug_pdf_layers.py` | `src/pdfrebuilder/core/generate_debug_pdf_layers.py` | Move to core |
| `src/pdf_engine.py` | `src/pdfrebuilder/core/pdf_engine.py` | Move to core |
| `src/recreate_pdf_from_config.py` | `src/pdfrebuilder/core/recreate_pdf_from_config.py` | Move to core |
| `src/render.py` | `src/pdfrebuilder/core/render.py` | Move to core |
| `src/cli/` | `src/pdfrebuilder/cli/` | Direct move (merge with existing) |
| `src/config/` | `src/pdfrebuilder/config/` | Direct move |
| `src/engine/` | `src/pdfrebuilder/engine/` | Direct move |
| `src/font/` | `src/pdfrebuilder/font/` | Direct move |
| `src/models/` | `src/pdfrebuilder/models/` | Direct move |
| `src/security/` | `src/pdfrebuilder/security/` | Direct move |
| `src/tools/` | `src/pdfrebuilder/tools/` | Direct move |
| `src/utils/` | `src/pdfrebuilder/utils/` | Direct move |
| `src/pdfrebuilder/` | DELETE | Remove existing incomplete structure |

### Import Transformation Rules

1. **Absolute imports from src:** `from src.module import func` → `from pdfrebuilder.module import func`
2. **Relative imports within package:** `from .module import func` (no change needed)
3. **Cross-package imports:** `from src.engine.parser import Parser` → `from pdfrebuilder.engine.parser import Parser`
4. **CLI imports:** Update all CLI imports to use new structure

## Error Handling

### Migration Validation

1. **Import Validation:** Automated script to verify all imports resolve correctly
2. **Functionality Testing:** Run full test suite to ensure no regressions
3. **CLI Testing:** Verify all CLI commands work with new structure
4. **Example Validation:** Ensure all examples and scripts work

### Rollback Strategy

1. **Git Branch:** Perform migration in feature branch for easy rollback
2. **Backup:** Keep original structure until migration is fully validated
3. **Incremental Migration:** Move modules in logical groups to minimize risk

## Testing Strategy

### Pre-Migration Testing

1. **Baseline Tests:** Run full test suite to establish baseline
2. **Import Analysis:** Scan all files for import statements to plan updates
3. **Dependency Mapping:** Map all internal dependencies

### Migration Testing

1. **Import Resolution:** Verify all imports resolve after each module move
2. **Functionality Testing:** Run tests after each major component migration
3. **CLI Testing:** Test CLI functionality throughout migration
4. **Integration Testing:** Verify cross-module functionality works

### Post-Migration Validation

1. **Full Test Suite:** Run complete test suite
2. **CLI Validation:** Test all CLI commands and options
3. **Example Execution:** Run all examples and scripts
4. **Package Installation:** Test package installation and import
5. **Documentation Validation:** Verify all documentation examples work

## Implementation Phases

### Phase 1: Preparation and Analysis
- Analyze current import structure
- Create migration scripts
- Set up new directory structure
- Create consolidated CLI

### Phase 2: Core Module Migration
- Move core functionality to `src/pdfrebuilder/core/`
- Update imports in moved modules
- Test core functionality

### Phase 3: Subpackage Migration
- Move subpackages (engine, models, config, etc.)
- Update internal imports
- Test each subpackage

### Phase 4: CLI and Entry Point Updates
- Consolidate CLI implementations
- Update pyproject.toml entry points
- Test CLI functionality

### Phase 5: Test and Script Updates
- Update all test imports
- Update script imports
- Update example imports
- Run full validation

### Phase 6: Documentation and Cleanup
- Update all documentation
- Remove old duplicate files
- Update configuration files
- Final validation

## Configuration Updates

### pyproject.toml Changes

```toml
[project.scripts]
pdfrebuilder = "pdfrebuilder.cli:main"  # Updated entry point

[tool.hatch.build.targets.wheel]
packages = ["src/pdfrebuilder"]  # Already correct

[tool.mypy]
mypy_path = "src"  # Keep existing
# Update module overrides to use new paths

[tool.ruff.lint.isort]
known-first-party = ["pdfrebuilder"]  # Updated from "src"
```

### Test Configuration Updates

```ini
# pytest.ini - may need updates for test discovery
[tool.pytest.ini_options]
testpaths = ["tests"]
python_paths = ["src"]
```

## Migration Scripts

### Automated Import Updater

Create script to automatically update imports:
- Scan all Python files
- Identify import patterns
- Apply transformation rules
- Validate updated imports

### Validation Script

Create comprehensive validation script:
- Test all imports resolve
- Run test suite
- Test CLI commands
- Validate examples

## Backward Compatibility

### Minimal src/ Structure

After migration, `src/` will contain only:
```
src/
├── __init__.py                  # Empty or minimal for build compatibility
└── pdfrebuilder/                # All actual code
    └── ... (everything)
```

### No Compatibility Layer Needed

Since this is a proper package restructure, we won't provide backward compatibility imports from `src/`. Users should import from the package name:
- ✅ `from pdfrebuilder import extract_pdf_content`
- ✅ `from pdfrebuilder.engine import DocumentParser`
- ❌ `from src.extract_pdf_content import ...` (never supported externally)

### Migration Guide

Provide clear migration guide with:
- Before/after import examples for internal development
- Common migration patterns for tests and scripts
- Automated migration script for bulk updates
- Breaking changes documentation for any external users