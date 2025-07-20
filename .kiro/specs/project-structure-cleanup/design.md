# Design Document

## Overview

This design outlines the reorganization of the project structure to move misplaced files from the main directory into appropriate subdirectories. The goal is to create a cleaner, more maintainable project structure that follows Python project best practices.

## Architecture

### Current State Analysis

The main directory currently contains:
- **Demo files**: Previously contained `demo_font_validation.py` (now moved to `tests/demos/`)
- **Log files**: `e2e_debug.log`, `e2e_full.log` - test execution logs
- **Debug artifacts**: `debug_layers.pdf`, `test_text_render.pdf` - generated debug files (now moved to `tests/output/`)
- **Utility scripts**: `extract_sample.py` - sample extraction utility
- **Test configurations**: `manual_overrides.json.test` - test configuration file (now moved to `tests/fixtures/`)

### Target Directory Structure

```
project_root/
├── demos/                      # NEW: Demo and example scripts
│   ├── README.md              # Documentation for demos
│   └── font_validation_demo.py # Already moved to tests/demos/demo_font_validation.py
├── scripts/                    # NEW: Utility scripts
│   ├── README.md              # Documentation for scripts
│   └── extract_sample.py      # Moved from root
├── output/
│   ├── logs/                  # NEW: Log file destination
│   │   ├── e2e_debug.log     # Moved from root
│   │   └── e2e_full.log      # Moved from root
│   └── debug/                 # NEW: Debug artifacts
│       ├── debug_layers.pdf   # Moved from root
│       └── test_text_render.pdf # Already moved to tests/output/
├── tests/
│   └── fixtures/              # NEW: Test configuration files
│       └── manual_overrides.json.test # Already moved to tests/fixtures/
└── [existing structure...]
```

## Components and Interfaces

### Directory Creation Module

**Purpose**: Ensure target directories exist before file operations

**Interface**:
```python
def ensure_directories_exist(directories: List[str]) -> None:
    """Create directories if they don't exist"""
```

### File Migration Module

**Purpose**: Move files from source to target locations with validation

**Interface**:
```python
def migrate_file(source_path: str, target_path: str, update_imports: bool = False) -> bool:
    """Move file and optionally update import paths"""
```

### Import Path Updater

**Purpose**: Update import statements in moved files to work from new locations

**Interface**:
```python
def update_import_paths(file_path: str, old_location: str, new_location: str) -> None:
    """Update relative import paths in Python files"""
```

### Documentation Generator

**Purpose**: Create README files for new directories explaining their contents

**Interface**:
```python
def generate_directory_readme(directory: str, contents: Dict[str, str]) -> None:
    """Generate README.md for directory with file descriptions"""
```

## Data Models

### File Migration Plan

```python
@dataclass
class FileMigration:
    source_path: str
    target_path: str
    file_type: str  # 'demo', 'log', 'debug', 'script', 'test'
    needs_import_update: bool
    description: str
```

### Migration Configuration

```python
MIGRATION_PLAN = [
    # FileMigration for demo_font_validation.py already completed - moved to tests/demos/
    FileMigration(
        source_path="extract_sample.py",
        target_path="scripts/extract_sample.py",
        file_type="script",
        needs_import_update=True,
        description="Utility script to extract content from sample PDF files"
    ),
    FileMigration(
        source_path="e2e_debug.log",
        target_path="output/logs/e2e_debug.log",
        file_type="log",
        needs_import_update=False,
        description="End-to-end test debug log"
    ),
    FileMigration(
        source_path="e2e_full.log",
        target_path="output/logs/e2e_full.log",
        file_type="log",
        needs_import_update=False,
        description="Full end-to-end test execution log"
    ),
    FileMigration(
        source_path="debug_layers.pdf",
        target_path="output/debug/debug_layers.pdf",
        file_type="debug",
        needs_import_update=False,
        description="Debug visualization of PDF layers"
    ),
    # FileMigration for test_text_render.pdf already completed - moved to tests/output/
    # FileMigration for manual_overrides.json.test already completed - moved to tests/fixtures/
]
```

## Error Handling

### File Operation Errors
- **Missing source files**: Log warning and continue with other migrations
- **Permission errors**: Report error and suggest manual intervention
- **Import update failures**: Log warning but complete file move

### Validation Checks
- Verify source file exists before attempting migration
- Check target directory is writable
- Validate import path updates don't break syntax

## Testing Strategy

### Unit Tests
- Test directory creation functionality
- Test file migration with various scenarios
- Test import path updating logic
- Test README generation

### Integration Tests
- Test complete migration process
- Verify moved files work from new locations
- Test that demos and scripts execute correctly after migration

### Validation Tests
- Verify no files are left in main directory that should be moved
- Check that all moved files maintain their functionality
- Validate that import paths are correctly updated

## Implementation Phases

### Phase 1: Directory Structure Setup
1. Create target directories (`demos/`, `scripts/`, `output/logs/`, `output/debug/`, `tests/fixtures/`)
2. Generate README files for new directories

### Phase 2: File Migration
1. Move log files (no import updates needed)
2. Move debug artifacts (no import updates needed)
3. Move test configuration files

### Phase 3: Script Migration with Import Updates
1. Move and update demo files
2. Move and update utility scripts
3. Test functionality from new locations

### Phase 4: Configuration Updates
1. Update .gitignore to prevent future accumulation
2. Update any configuration files that reference moved files
3. Update documentation to reflect new structure

## Configuration Updates

### .gitignore Enhancements
```gitignore
# Prevent temporary files in main directory
/*.log
/*.pdf
/debug_*.pdf
/test_*.pdf
/demo_*.py

# Allow organized files in proper directories
!demos/
!scripts/
!output/logs/
!output/debug/
```

### Documentation Updates
- Update README.md to reference new directory structure
- Update CONTRIBUTING.md with new file organization guidelines
- Create directory-specific README files explaining contents
