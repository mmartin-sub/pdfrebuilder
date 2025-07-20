# Duplicate Module Resolution

## Issue

The project had duplicate `run_tests.py` files causing a module naming conflict:

- `tests/run_tests.py` (current location)
- `scripts/run_tests.py` (moved to tests/)

This was resolved by moving the script to the tests/ directory where it belongs.

## Analysis

### `tests/run_tests.py` (Removed)

**Purpose**: Legacy integration test runner for PDF/PSD files
**Issues**:

- Used insecure subprocess calls (even with `# nosec` comments)
- Duplicated functionality now handled by pytest
- Created HTML reports that weren't used elsewhere
- Hardcoded to specific test files
- Not integrated with modern hatch/pytest workflow
- Predated the current project structure

### `tests/run_tests.py` (Current Location)

**Purpose**: Modern convenience wrapper for hatch/pytest
**Benefits**:

- Uses secure subprocess execution via `SecureSubprocessRunner`
- Integrates with pyproject.toml configuration
- Supports modern pytest workflow
- Provides convenient verbosity controls
- Aligns with project's current testing approach

## Resolution

1. **Removed** `tests/run_tests.py` - The legacy test runner
2. **Updated** `tests/README.md` - Removed references to the old test runner
3. **Updated** `.kiro/steering/structure.md` - Updated project structure documentation
4. **Moved** `scripts/run_tests.py` to `tests/run_tests.py` to follow Python conventions

## Current Testing Approach

The project now uses a unified testing approach:

### Standard pytest commands (via hatch)

```bash
hatch run test                    # Run all tests
hatch run test-cov               # Run with coverage
hatch run test tests/specific.py # Run specific tests
```

### Convenience script with verbosity control

```bash
python tests/run_tests.py                    # Default quiet mode
python tests/run_tests.py --verbose         # Verbose mode
python tests/run_tests.py --debug           # Debug mode
python tests/run_tests.py --coverage        # With coverage
python tests/run_tests.py tests/test_specific.py  # Specific tests
```

## Benefits of Resolution

1. **No Module Conflicts**: Eliminated duplicate module naming
2. **Improved Security**: Removed legacy code with security issues
3. **Simplified Maintenance**: Single test runner approach
4. **Better Integration**: Aligns with modern Python project standards
5. **Consistent Workflow**: All testing goes through pytest/hatch

## Verification

- ✅ Security scans pass (`bandit`)
- ✅ No import conflicts
- ✅ Modern test runner works correctly
- ✅ Documentation updated
- ✅ Project structure cleaned up

The duplicate module issue is now resolved, and the project has a clean, secure, and modern testing setup.
