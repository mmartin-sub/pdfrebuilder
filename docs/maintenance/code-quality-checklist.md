# Code Quality Maintenance Checklist

## Overview

This checklist provides a systematic approach to maintaining code quality in the PDF Layout Extractor and Rebuilder project, with specific focus on preventing and addressing linting violations.

## Pre-Commit Checklist

Before committing any code changes:

- [ ] **Run linting checks**: `hatch run ruff check .`
- [ ] **Fix auto-fixable issues**: `hatch run ruff check . --fix`
- [ ] **Run full pre-commit**: `hatch run pre-commit run --all-files`
- [ ] **Run tests**: `hatch run pytest`
- [ ] **Check for unused imports**: `hatch run ruff check . --select F401`
- [ ] **Check for unused variables**: `hatch run ruff check . --select F841`

## Monthly Maintenance Tasks

### Import Cleanup

- [ ] **Scan for unused imports**: `hatch run ruff check . --select F401`
- [ ] **Review models/**init**.py**: Ensure **all** list is up to date
- [ ] **Check test utilities**: Review test helper imports for unused items
- [ ] **Validate API modules**: Ensure public API imports are properly exported

### Variable Cleanup

- [ ] **Scan for unused variables**: `hatch run ruff check . --select F841`
- [ ] **Review test fixtures**: Check for unused fixture parameters
- [ ] **Check function arguments**: Look for unused parameters that should be prefixed with `_`
- [ ] **Validate pytest hooks**: Ensure required parameters are properly handled

### Documentation Updates

- [ ] **Update code quality guidelines**: Reflect any new patterns or issues found
- [ ] **Review IDE configurations**: Ensure VS Code and PyCharm settings are current
- [ ] **Update this checklist**: Add new maintenance tasks as needed

## Issue Resolution Patterns

### Unused Imports

**Pattern**: `F401 'module.item' imported but unused`

**Solutions**:

1. **Remove completely** if truly unused
2. **Add to **all**** if part of public API
3. **Use explicit re-export** for API modules: `item as item`
4. **Add # noqa: F401** with justification if intentionally unused

### Unused Variables

**Pattern**: `F841 Local variable 'name' is assigned to but never used`

**Solutions**:

1. **Remove variable** if not needed
2. **Prefix with underscore** if intentionally unused: `_name`
3. **Use the variable** if it serves a purpose

### Unused Function Arguments

**Pattern**: `ARG001 Unused function argument: 'param'`

**Solutions**:

1. **Remove parameter** if not needed
2. **Prefix with underscore** if required by interface: `_param`
3. **Add # noqa: ARG001** for required interface parameters (like pytest hooks)

## Special Cases

### Pytest Hooks

Pytest hooks often require specific parameter names even if unused:

```python
def pytest_runtest_teardown(item, nextitem):  # noqa: ARG001
    """nextitem is required by pytest interface but not used"""
    pass
```

### API Modules

Public API modules should use **all** to define exports:

```python
from .module import item1, item2, item3

__all__ = ["item1", "item2", "item3"]
```

### Mock Functions in Tests

Test mocks often have unused parameters:

```python
def mock_function(*args, **kwargs):  # noqa: ARG001
    """Mock function for testing"""
    return "mocked"
```

## Validation Commands

### Quick Check

```bash
# Check specific files for common issues
hatch run ruff check src/font_utils.py tests/conftest.py --select F401,F841,ARG001
```

### Full Scan

```bash
# Comprehensive code quality check
hatch run ruff check . --select F401,F841,ARG001,E,W
```

### Auto-Fix

```bash
# Fix automatically fixable issues
hatch run ruff check . --fix
```

### Pre-Commit Validation

```bash
# Run all pre-commit hooks
hatch run pre-commit run --all-files
```

## Troubleshooting

### Common Issues

1. **"Module not found" after removing imports**
   - Check if import was used in type hints
   - Verify import wasn't used in string annotations
   - Look for usage in docstrings or comments

2. **Tests fail after cleanup**
   - Check if removed imports were used in fixtures
   - Verify mock objects are still properly imported
   - Ensure test utilities are still accessible

3. **Pre-commit hooks fail**
   - Run individual tools to identify specific issues
   - Check for new linting rules that weren't previously enforced
   - Verify all dependencies are properly installed

### Recovery Steps

If cleanup breaks functionality:

1. **Revert changes**: `git checkout -- <file>`
2. **Identify actual usage**: Search codebase for import/variable usage
3. **Apply targeted fixes**: Fix only confirmed unused items
4. **Test incrementally**: Verify each change doesn't break functionality

## Automation

### IDE Integration

Configure your IDE to show unused imports/variables in real-time:

- **VS Code**: Use the provided `.vscode/settings.json`
- **PyCharm**: Use the provided `.idea/` configuration files

### Pre-Commit Hooks

The project uses pre-commit hooks to catch issues early:

```yaml
# .pre-commit-config.yaml includes ruff checks
- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
    - id: ruff
      args: [--fix, --exit-non-zero-on-fix]
```

## Metrics and Tracking

### Success Metrics

- [ ] Zero F401 (unused import) violations
- [ ] Zero F841 (unused variable) violations
- [ ] Minimal ARG001 violations (only justified cases)
- [ ] All pre-commit hooks passing
- [ ] All tests passing after cleanup

### Regular Reporting

Monthly code quality report should include:

- Number of violations fixed
- New patterns identified
- Documentation updates made
- IDE configuration improvements

## Conclusion

Regular maintenance of code quality prevents technical debt accumulation and ensures a clean, maintainable codebase. Following this checklist systematically will help maintain high standards while avoiding common pitfalls.
