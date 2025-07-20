# Design Document

## Overview

The logging improvements will refactor the current system to display engine version information only when relevant and at appropriate log levels. The design focuses on moving version information from module-level display to contextual, engine-specific logging that respects user-configured log levels.

## Architecture

### Current Issues

1. **Module-level version display**: PyMuPDF version information is displayed at import time in `main.py` (lines 46-67)
2. **No log level respect**: Version information shows regardless of user's log level preference
3. **Engine-agnostic display**: Shows PyMuPDF info even when other engines are used
4. **Inconsistent patterns**: Different engines handle version information differently

### Proposed Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   main.py       │    │  Engine Manager  │    │  Engine Logger  │
│                 │    │                  │    │                 │
│ - Clean startup │───▶│ - Engine         │───▶│ - Version info  │
│ - No version    │    │   selection      │    │   at DEBUG      │
│   display       │    │ - Initialization │    │ - Load path     │
│                 │    │   logging        │    │   at DEBUG      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Components and Interfaces

### 1. Engine Version Logger

**Location**: `src/engine/engine_logger.py`

```python
class EngineLogger:
    """Centralized engine logging with version information management."""
    
    @staticmethod
    def log_engine_info(engine_name: str, engine_version: str, 
                       load_path: str = None, log_level: int = logging.DEBUG) -> None:
        """Log engine version information at appropriate level."""
        
    @staticmethod
    def log_engine_selection(engine_name: str, reason: str = "user_selected") -> None:
        """Log engine selection at INFO level."""
        
    @staticmethod
    def log_engine_fallback(from_engine: str, to_engine: str, reason: str) -> None:
        """Log engine fallback with version info regardless of log level."""
```

### 2. Engine Interface Updates

**Base Engine Class**: `src/engine/pdf_rendering_engine.py`

```python
class PDFRenderingEngine:
    """Base class for PDF rendering engines."""
    
    def log_initialization(self) -> None:
        """Log engine initialization with version info at DEBUG level."""
        
    def get_version_info(self) -> Dict[str, str]:
        """Get comprehensive version information for this engine."""
```

### 3. Main Application Updates

**File**: `main.py`

- Remove module-level version display (lines 46-67)
- Add engine-specific logging in `run_pipeline()` function
- Integrate with engine selection logic

### 4. Console Output Manager

**Enhancement**: Existing console_print function

```python
def console_print(message: str, style: str = "default", 
                 log_level: int = None) -> None:
    """Enhanced console print with log level awareness."""
```

## Data Models

### Engine Version Information

```python
@dataclass
class EngineVersionInfo:
    """Structured engine version information."""
    engine_name: str
    engine_version: str
    library_version: str
    load_path: str
    python_executable: str
    supported_features: Dict[str, bool]
```

### Logging Configuration

```python
@dataclass
class LoggingConfig:
    """Enhanced logging configuration."""
    log_level: int
    show_engine_versions: bool
    show_load_paths: bool
    show_python_executable: bool
```

## Error Handling

### Engine Initialization Failures

When engine initialization fails, version information will be displayed regardless of log level to aid troubleshooting:

```python
try:
    engine.initialize(config)
except Exception as e:
    # Always show version info on engine failures
    EngineLogger.log_engine_info(engine_name, engine_version, 
                                load_path, logging.ERROR)
    logger.error(f"Engine initialization failed: {e}")
```

### Missing Engine Dependencies

When required engine dependencies are missing, the system will:

1. Log the missing dependency at ERROR level
2. Display available engines at INFO level
3. Show installation instructions at INFO level

## Testing Strategy

### Unit Tests

1. **Engine Logger Tests**: Verify correct log level behavior
2. **Console Output Tests**: Ensure clean output at different log levels
3. **Engine Selection Tests**: Verify version logging during selection

### Integration Tests

1. **Full Pipeline Tests**: Test logging behavior across complete workflows
2. **Engine Fallback Tests**: Verify fallback logging behavior
3. **Multi-Engine Tests**: Test logging when multiple engines are used

### Manual Testing Scenarios

1. **Default Behavior**: Run with default settings, verify clean output
2. **Debug Mode**: Run with DEBUG level, verify version information appears
3. **Engine Failures**: Test with missing dependencies, verify error logging
4. **Multiple Engines**: Test workflows using different input/output engines

## Implementation Details

### Phase 1: Remove Module-Level Display

1. Remove lines 46-67 from `main.py`
2. Move fitz import to engine-specific locations
3. Update imports to be conditional on engine usage

### Phase 2: Create Engine Logger

1. Implement `EngineLogger` class
2. Add version information methods to base engine class
3. Update existing engines to use new logging system

### Phase 3: Integrate with Engine Selection

1. Update engine selection logic to use new logging
2. Add DEBUG-level logging for engine initialization
3. Implement fallback logging behavior

### Phase 4: Console Output Enhancement

1. Update `console_print` function for log level awareness
2. Ensure consistent behavior with/without rich console
3. Add configuration options for logging verbosity

## Configuration Changes

### Settings Updates

Add to `src/settings.py`:

```python
CONFIG = {
    # ... existing config ...
    "logging": {
        "show_engine_versions": False,  # Only at DEBUG level
        "show_load_paths": False,       # Only at DEBUG level
        "show_python_executable": False, # Only at DEBUG level
        "engine_selection_level": "INFO",
        "engine_fallback_level": "WARNING",
    }
}
```

### Environment Variables

Support environment variables for logging control:

- `PDF_ENGINE_LOG_LEVEL`: Override engine logging level
- `PDF_ENGINE_SHOW_VERSIONS`: Force version display
- `PDF_ENGINE_QUIET`: Suppress all engine logging

## Backward Compatibility

### Deprecated Behavior

The module-level version display will be removed, but the information will still be available:

- At DEBUG log level when engines are used
- In engine metadata for programmatic access
- In error messages when engines fail

### Migration Path

Users relying on version information can:

1. Use `--log-level DEBUG` to see version information
2. Access version info programmatically through engine interfaces
3. Use new CLI flags for version display (if needed)

## Performance Considerations

### Lazy Loading

Engine imports will be moved to usage points to avoid unnecessary imports:

```python
# Instead of module-level import
import fitz

# Use conditional import
def get_fitz_engine():
    import fitz
    return FitzEngine(fitz)
```

### Logging Overhead

Version information gathering will be optimized:

- Cache version information after first access
- Skip expensive operations at non-DEBUG levels
- Use lazy evaluation for path resolution