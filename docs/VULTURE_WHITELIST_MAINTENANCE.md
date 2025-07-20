# Vulture Whitelist Maintenance Guide

This document describes the process for maintaining the `.vulture_whitelist.py` file and managing dead code detection in the project.

## Overview

Vulture is a tool for finding unused code (dead code) in Python programs. The `.vulture_whitelist.py` file contains patterns and symbols that should be ignored by vulture, typically because they are:

- Part of public APIs that may be used externally
- Used dynamically or through reflection
- Required for future functionality
- Part of configuration or constants that appear unused but are necessary

## Vulture Configuration

### Pre-commit Hook Configuration

The pre-commit hook runs vulture with these settings:

- **Confidence threshold**: 85% (conservative, fewer false positives)
- **Files scanned**: `src`, `tests`, `scripts`, `examples`, `main.py`
- **Whitelist**: `.vulture_whitelist.py`

### On-Demand Vulture Commands

Use these hatch commands for more aggressive scanning:

```bash
# Standard check (80% confidence)
hatch run vulture-check

# Strict check (60% confidence) - finds more potential issues
hatch run vulture-strict

# Very aggressive (40% confidence) - many false positives
hatch run vulture-aggressive

# Source code only (70% confidence)
hatch run vulture-src-only
```

## Whitelist Maintenance Process

### 1. Regular Review Schedule

- **Monthly**: Run `hatch run vulture-strict` to identify potential dead code
- **Before releases**: Run `hatch run vulture-check` to ensure clean state
- **After major refactoring**: Review and update whitelist patterns

### 2. Adding New Whitelist Entries

When adding entries to `.vulture_whitelist.py`:

1. **Document the reason**: Always include a comment explaining why the entry is whitelisted
2. **Use specific patterns**: Prefer specific names over broad wildcards when possible
3. **Group by category**: Keep related patterns together
4. **Test the change**: Ensure pre-commit still passes after adding entries

#### Example of Good Whitelist Entry

```python
# Engine abstraction patterns
_.extract  # Engine extraction methods - part of public API
_.render   # Engine rendering methods - used by external consumers
```

#### Example of Poor Whitelist Entry

```python
# Don't do this - too broad and no explanation
_.*  # Everything
```

### 3. Removing Whitelist Entries

Before removing entries:

1. **Run vulture-strict**: Ensure the symbol is actually unused
2. **Check git history**: Understand why it was originally whitelisted
3. **Search codebase**: Verify it's not used dynamically or in strings
4. **Test thoroughly**: Run full test suite after removal

### 4. Handling False Positives

Common false positive patterns:

#### Dynamic Usage

```python
# Code that uses getattr, setattr, or string-based access
method_name = "process_data"
getattr(obj, method_name)()  # vulture won't see this usage
```

#### Configuration/Constants

```python
# Constants that appear unused but are part of public API
class EngineType:
    FITZ = "fitz"        # May appear unused but needed for config
    REPORTLAB = "reportlab"
```

#### Test Fixtures

```python
# Test variables that are used by pytest fixtures
def test_something():
    test_data = create_test_data()  # May appear unused if used in assertions
    assert process(test_data) == expected
```

## Whitelist Categories

### Current Categories in `.vulture_whitelist.py`

1. **PDF/PSD Processing Patterns**: Document-specific attributes
2. **Test-Related Patterns**: Test fixtures, mock objects, test variables
3. **Configuration Patterns**: Settings and configuration objects
4. **CLI Patterns**: Command-line interface functions
5. **Engine Abstraction Patterns**: Multi-engine support methods
6. **Data Model Patterns**: Serialization and data conversion methods
7. **Security Patterns**: Security-related functions and utilities
8. **Documentation Patterns**: API documentation and examples
9. **Magic Methods**: Python special methods that may appear unused
10. **Common Properties**: Standard object properties
11. **Engine-Specific Attributes**: Engine implementation details

## Best Practices

### DO

- ✅ Add specific, well-documented whitelist entries
- ✅ Use the strictest vulture check that passes in CI
- ✅ Review whitelist entries during code reviews
- ✅ Remove entries when code is actually deleted
- ✅ Group related patterns together with clear comments

### DON'T

- ❌ Add broad wildcard patterns without justification
- ❌ Whitelist everything to make vulture pass
- ❌ Ignore vulture failures without investigation
- ❌ Add entries without understanding why they're flagged
- ❌ Leave outdated entries in the whitelist

## Troubleshooting

### Vulture Reports False Positive

1. Verify the code is actually used (check for dynamic usage)
2. Add specific whitelist entry with clear documentation
3. Consider if the code should actually be removed

### Vulture Misses Real Dead Code

1. Lower the confidence threshold temporarily
2. Use `hatch run vulture-strict` for more aggressive scanning
3. Manually review suspicious patterns

### Pre-commit Vulture Fails

1. Check if new dead code was introduced
2. Verify whitelist entries are correct
3. Consider if the flagged code should be removed or whitelisted

## Integration with Development Workflow

### Code Review Checklist

- [ ] No new vulture violations introduced
- [ ] Any new whitelist entries are documented and justified
- [ ] Removed code has corresponding whitelist entries removed
- [ ] Pre-commit vulture check passes

### CI/CD Integration

The vulture check is integrated into:

- Pre-commit hooks (blocks commits with violations)
- CI pipeline (ensures clean state in all branches)
- Code quality metrics (tracks dead code over time)

## Maintenance Commands

```bash
# Check current vulture status
pre-commit run vulture --all-files

# Find potential dead code with different confidence levels
hatch run vulture-check        # 80% confidence
hatch run vulture-strict       # 60% confidence
hatch run vulture-aggressive   # 40% confidence

# Update pre-commit hooks
pre-commit autoupdate

# Install/update vulture
hatch run pip install --upgrade vulture
```

## Contact and Support

For questions about vulture configuration or whitelist maintenance:

1. Check this documentation first
2. Review existing whitelist entries for similar patterns
3. Consult the team during code review
4. Update this documentation when adding new patterns or processes
