# Code Quality Guidelines

## Overview

This document provides guidelines for maintaining high code quality in the PDF Layout Extractor and Rebuilder project, with specific focus on avoiding common linting violations and maintaining clean, maintainable code.

## Import Management

### Avoiding Unused Imports

**Problem**: Unused imports create code clutter and can trigger linting violations.

**Best Practices**:

1. **Regular Cleanup**: Periodically review and remove unused imports
2. **IDE Configuration**: Configure your IDE to highlight unused imports
3. **Import Organization**: Group imports logically and remove unused ones during code review

**Common Patterns to Avoid**:

```python
# BAD: Importing Optional but never using it
from typing import Optional, Any

def process_data(data: Any) -> str:
    return str(data)
```

```python
# GOOD: Only import what you need
from typing import Any

def process_data(data: Any) -> str:
    return str(data)
```

### Handling Required but Unused Parameters

**Problem**: Some function signatures (like pytest hooks) require specific parameters even if unused.

**Solution**: Use appropriate suppression comments:

```python
# GOOD: Proper handling of required but unused parameters
def pytest_runtest_teardown(item, nextitem):  # noqa: ARG001
    """Teardown after each test item"""
    # nextitem is required by pytest hook interface but not used
    pass
```

## Variable Management

### Avoiding Unused Variables

**Best Practices**:

1. **Prefix with underscore**: For intentionally unused variables
2. **Remove completely**: If the variable serves no purpose
3. **Use meaningful names**: Even for temporary variables

**Examples**:

```python
# BAD: Unused variable
def process_items(items):
    result = []
    temp_var = "unused"  # This will trigger linting
    for item in items:
        result.append(item.upper())
    return result

# GOOD: Remove unused variable
def process_items(items):
    result = []
    for item in items:
        result.append(item.upper())
    return result

# GOOD: Prefix with underscore if needed for clarity
def process_items(items):
    result = []
    _debug_info = "processing started"  # Intentionally unused
    for item in items:
        result.append(item.upper())
    return result
```

## Linting Tools Integration

### Ruff Configuration

The project uses `ruff` for linting. Key rules for code quality:

- `F401`: Unused imports
- `F841`: Unused variables
- `ARG001`: Unused function arguments

### Pre-commit Hooks

Ensure your changes pass pre-commit checks:

```bash
# Run pre-commit on all files
hatch run pre-commit run --all-files

# Run specific linting checks
hatch run ruff check .
```

## IDE Integration

### VS Code Configuration

Add to your `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.ruffArgs": ["--select", "F401,F841,ARG001"]
}
```

### PyCharm Configuration

1. Go to Settings → Tools → External Tools
2. Add ruff as an external tool
3. Configure to run on file save

## Common Scenarios

### Test Fixtures

When working with pytest fixtures, be careful about unused parameters:

```python
# BAD: Fixture parameter not used
def test_something(mock_database):
    assert True  # mock_database is unused

# GOOD: Either use the fixture or remove it
def test_something():
    assert True

# GOOD: Or use it properly
def test_something(mock_database):
    mock_database.setup()
    assert True
```

### Mock Objects

Remove unused mock imports and objects:

```python
# BAD: Importing MagicMock but only using Mock
from unittest.mock import MagicMock, Mock, patch

@patch('module.function')
def test_function(mock_func):
    mock_obj = Mock()  # MagicMock is unused
    assert mock_obj is not None

# GOOD: Only import what you need
from unittest.mock import Mock, patch

@patch('module.function')
def test_function(mock_func):
    mock_obj = Mock()
    assert mock_obj is not None
```

## Maintenance Checklist

### Before Committing

- [ ] Run `hatch run ruff check .` to check for unused imports/variables
- [ ] Run `hatch run pre-commit run --all-files` to ensure all checks pass
- [ ] Review import statements for unused imports
- [ ] Check for unused variables in test files

### During Code Review

- [ ] Verify all imports are necessary
- [ ] Check for proper handling of unused but required parameters
- [ ] Ensure consistent import organization
- [ ] Validate that linting suppressions are justified

### Regular Maintenance

- [ ] Monthly review of import statements across the codebase
- [ ] Update linting configuration as needed
- [ ] Review and update this guide based on new patterns

## Troubleshooting

### Common Issues

1. **"Module not found" after removing imports**: Verify the import was truly unused
2. **Test failures after cleanup**: Check if removed imports were used in fixtures
3. **Pre-commit failures**: Run individual linting tools to identify specific issues

### Getting Help

- Check the project's linting configuration in `pyproject.toml`
- Review existing code for patterns and best practices
- Consult the ruff documentation for specific rule explanations

## Conclusion

Maintaining clean imports and variables is essential for code quality. By following these guidelines and using the provided tools, you can ensure your contributions maintain the project's high standards while avoiding common linting violations.
