# Design Document

## Overview

This design addresses the immediate pytest fixture dependency issue by implementing the missing `log_file` fixture and adding a pre-commit hook to prevent similar issues in the future. The solution focuses on minimal changes to fix the current problem while establishing a safety net.

## Architecture

### Component Overview

```
tests/
├── conftest.py              # Add log_file fixture
├── test_engine_logging.py   # Uses log_file fixture (no changes needed)
└── test_font_error_handling.py # Uses log_file fixture (no changes needed)

.kiro/hooks/
└── pytest-validation-check.json # New pre-commit hook

.pytest_cache/               # Temporary log files location
└── log_files/              # Isolated directory for test log files
```

### Fixture Design

The `log_file` fixture will be implemented as a session-scoped fixture that provides unique temporary log files for each test that needs one.

## Components and Interfaces

### 1. Log File Fixture (`conftest.py`)

**Purpose**: Provide temporary log files for tests that need file-based logging

**Interface**:
```python
@pytest.fixture
def log_file(tmp_path_factory) -> str:
    """Provide a temporary log file path for tests."""
    # Returns: Absolute path to a temporary log file
```

**Implementation Details**:
- Uses pytest's `tmp_path_factory` for proper temporary file management
- Creates unique log files per test to avoid conflicts
- Automatically cleaned up by pytest's temporary file system
- Returns string path (not Path object) for compatibility with existing test code

### 2. Pre-commit Hook

**Purpose**: Validate pytest configuration before commits

**Configuration**:
```json
{
  "name": "pytest-validation-check",
  "description": "Validate pytest configuration and fixture dependencies",
  "trigger": "pre-commit",
  "command": "hatch run pytest --collect-only -q",
  "timeout": 30,
  "fail_on_error": true
}
```

**Behavior**:
- Runs `pytest --collect-only` to validate test collection without execution
- Fails fast if any fixtures are missing or configuration is invalid
- Provides clear error output for debugging
- Times out after 30 seconds to prevent hanging commits

## Data Models

### Log File Path Structure

```
{tmp_path_factory.getbasetemp()}/
└── pytest-logs-{session_id}/
    ├── test_engine_logging_{timestamp}.log
    ├── test_font_error_handling_{timestamp}.log
    └── ...
```

**Path Format**: `{base_temp_dir}/pytest-logs-{session_id}/{test_name}_{timestamp}.log`

### Hook Configuration Schema

```json
{
  "name": "string",           // Hook identifier
  "description": "string",    // Human-readable description
  "trigger": "pre-commit",    // When to run the hook
  "command": "string",        // Command to execute
  "timeout": "number",        // Timeout in seconds
  "fail_on_error": "boolean"  // Whether to block commit on failure
}
```

## Error Handling

### Fixture Creation Errors

- **Temporary directory creation fails**: Fall back to system temp directory
- **Permission errors**: Log warning and use pytest's default tmp_path
- **Disk space issues**: Fail gracefully with clear error message

### Hook Execution Errors

- **Command not found**: Provide clear message about hatch/pytest installation
- **Timeout exceeded**: Kill process and report timeout error
- **Collection errors**: Display pytest's error output directly to user

## Testing Strategy

### Fixture Testing

1. **Unit Tests**: Verify fixture returns valid file paths
2. **Integration Tests**: Confirm existing tests work with new fixture
3. **Isolation Tests**: Ensure multiple tests get unique log files

### Hook Testing

1. **Success Case**: Verify hook passes when pytest collection succeeds
2. **Failure Case**: Verify hook blocks commit when fixtures are missing
3. **Timeout Case**: Verify hook fails appropriately on timeout

### Validation Approach

1. Run existing failing tests to confirm they now pass
2. Temporarily break a fixture reference to verify hook catches it
3. Test hook performance to ensure it meets 30-second timeout requirement

## Implementation Notes

### Minimal Changes Principle

- Only add the missing `log_file` fixture to `conftest.py`
- No changes needed to existing test files
- Hook is additive and doesn't modify existing workflow

### Compatibility Considerations

- Fixture returns string path for compatibility with existing code
- Uses pytest's standard temporary file mechanisms
- Hook uses existing hatch/pytest commands

### Performance Considerations

- Session-scoped fixture minimizes file creation overhead
- Hook runs collection only (no test execution) for speed
- Temporary files are automatically cleaned up by pytest