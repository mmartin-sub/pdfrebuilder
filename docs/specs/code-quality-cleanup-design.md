# Design Document

## Overview

This design addresses the systematic cleanup of code quality issues flagged by linting tools including vulture (unused imports/variables) and ruff (unused function arguments). The approach focuses on analyzing each violation, determining the appropriate fix, and ensuring all changes are validated through comprehensive testing.

## Architecture

### Code Quality Analysis Pipeline

```
Vulture Detection → Analysis → Fix Strategy → Implementation → Validation
```

1. **Detection Phase**: Run vulture to identify all unused code
2. **Analysis Phase**: Categorize violations by type and determine fix strategy
3. **Implementation Phase**: Apply fixes systematically
4. **Validation Phase**: Ensure pre-commit and pytest pass

### Fix Strategy Decision Tree

```
Unused Import/Variable
├── Truly Unused → Remove
├── Used in Comments/Strings → Keep with vulture ignore
├── Used for Side Effects → Keep with vulture ignore
├── Test Mock/Fixture → Rename with underscore prefix
└── Future Use/API → Keep with vulture ignore comment

Unused Function Arguments (ARG001)
├── Callback/Hook Function → Rename with underscore prefix
├── Interface Compliance → Rename with underscore prefix
├── Future Use → Rename with underscore prefix
├── Truly Unused → Remove from signature
└── Mock Functions → Rename with underscore prefix
```

## Components and Interfaces

### Vulture Configuration Analysis

- **Location**: `.vulture_whitelist.py` and pyproject.toml
- **Purpose**: Understand current exclusions and confidence thresholds
- **Interface**: Configuration file analysis

## Fix Strategy Types

- **Remove unused code**: Delete imports, variables, or arguments that are truly unused
- **Rename with underscore prefix**: For arguments that must remain for interface compliance (pytest hooks, mocks)
- **Add ignore comments**: Only when necessary for legitimate cases that can't be fixed otherwise

## Error Handling

### Import Removal Safety

- **Check**: Verify import is not used in string literals or comments
- **Validation**: Ensure no runtime ImportError after removal
- **Rollback**: Restore import if tests fail

### Variable Cleanup Safety

- **Test Context**: Special handling for test fixtures and mocks
- **Scope Analysis**: Ensure variable removal doesn't affect other code
- **Mock Validation**: Verify mock objects are properly handled

## Testing Strategy

### Pre-Implementation Testing

1. **Baseline Establishment**: Document current vulture violations
2. **Test Suite Validation**: Ensure all tests pass before changes
3. **Pre-commit Status**: Verify current pre-commit hook status

### Post-Fix Validation

1. **Vulture Clean Run**: Verify no violations remain
2. **Full Test Suite**: Run `hatch run pytest` to ensure functionality
3. **Pre-commit Validation**: Run `pre-commit run --all-files`
4. **Import Verification**: Ensure all imports still resolve correctly

### Continuous Validation

- **Per-File Validation**: Test after each file is fixed
- **Incremental Testing**: Run relevant tests for modified modules
- **Final Comprehensive Test**: Complete validation before task completion

## Implementation Phases

### Phase 1: Immediate Fix

1. Run vulture to get complete violation list
2. Fix each violation immediately with appropriate strategy
3. Validate with pre-commit and pytest after each fix
4. Ensure clean state before moving to prevention

### Phase 2: Prevention Methodology

1. **Enhanced Pre-commit Configuration**: Strengthen vulture settings
2. **IDE Integration**: Configure development environment warnings
3. **Code Review Guidelines**: Document patterns to avoid
4. **Automated Enforcement**: Ensure CI/CD catches violations

### Phase 3: Long-term Maintenance

1. Regular vulture audits in CI pipeline
2. Developer education on clean coding practices
3. Automated cleanup scripts for common patterns
4. Documentation of approved vulture ignores

## Prevention Strategy

### Pre-commit Hook Enhancement

- **Stricter Vulture Settings**: Lower confidence threshold for catching more issues
- **Fail-fast Configuration**: Ensure vulture failures block commits
- **Comprehensive Coverage**: Include all Python files in vulture scan

### Development Environment Setup

- **IDE Linting**: Configure VS Code/PyCharm to show vulture warnings
- **Real-time Feedback**: Enable immediate feedback on unused code
- **Auto-cleanup**: Configure IDE to suggest removal of unused imports

### Code Review Process

- **Checklist Items**: Include "no unused imports/variables" in review checklist
- **Automated Comments**: Use tools to flag potential issues in PRs
- **Education**: Document common patterns that lead to vulture violations

### CI/CD Integration

- **Mandatory Checks**: Make vulture passing required for merge
- **Detailed Reporting**: Provide clear feedback on violations
- **Trend Monitoring**: Track code quality metrics over time

## Specific Issue Resolution

### Current Ruff ARG001 Violations

1. **`src/font_utils.py:1379:44: ARG001 Unused function argument: 'text_content'`**
   - **Function**: `_validate_font_before_registration`
   - **Analysis**: Check if argument is needed for interface compliance or future use
   - **Strategy**: Rename to `_text_content` or remove if truly unused

2. **`tests/conftest.py:109:26: ARG001 Unused function argument: 'item'`**
   - **Function**: `pytest_runtest_setup`
   - **Analysis**: Pytest hook function - argument required by pytest interface
   - **Strategy**: Rename to `_item` to indicate intentional non-use

3. **`tests/conftest.py:219:31: ARG001 Unused function argument: 'config'`**
   - **Function**: `pytest_assertrepr_compare`
   - **Analysis**: Pytest hook function - argument required by pytest interface
   - **Strategy**: Rename to `_config` to indicate intentional non-use

4. **`tests/conftest.py:248:31: ARG001 Unused function argument: 'node'`**
   - **Function**: `pytest_exception_interact`
   - **Analysis**: Pytest hook function - argument required by pytest interface
   - **Strategy**: Rename to `_node` to indicate intentional non-use

5. **`tests/conftest.py:248:43: ARG001 Unused function argument: 'report'`**
   - **Function**: `pytest_exception_interact`
   - **Analysis**: Pytest hook function - argument required by pytest interface
   - **Strategy**: Rename to `_report` to indicate intentional non-use

6. **`tests/font_error_test_utils.py:110:31: ARG001 Unused function argument: 'args'`**
   - **Function**: `mock_insert_font` (nested function)
   - **Analysis**: Mock function that needs to accept arbitrary arguments
   - **Strategy**: Rename to `*_args` to indicate intentional non-use

7. **`tests/font_error_test_utils.py:110:39: ARG001 Unused function argument: 'kwargs'`**
   - **Function**: `mock_insert_font` (nested function)
   - **Analysis**: Mock function that needs to accept arbitrary keyword arguments
   - **Strategy**: Rename to `**_kwargs` to indicate intentional non-use

8. **`tests/font_error_test_utils.py:140:41: ARG001 Unused function argument: 'font_name'`**
   - **Function**: `mock_validate_fallback_font` (nested function)
   - **Analysis**: Mock function that needs specific signature for testing
   - **Strategy**: Rename to `_font_name` to indicate intentional non-use

9. **`tests/font_error_test_utils.py:140:57: ARG001 Unused function argument: 'page'`**
   - **Function**: `mock_validate_fallback_font` (nested function)
   - **Analysis**: Mock function that needs specific signature for testing
   - **Strategy**: Rename to `_page` to indicate intentional non-use

### Current Vulture Violations

1. **`src/engine/extract_wand_content.py:66: unused import 'wand'`**
   - **Analysis**: Check if import is used for type hints, side effects, or truly unused
   - **Strategy**: Remove if unused, add ignore comment if needed for future use

2. **`tests/test_wand_multi_format.py:92: unused variable 'mock_makedirs'`**
   - **Analysis**: Test mock variable that may be needed for test setup
   - **Strategy**: Rename to `_mock_makedirs` or remove if truly unused

### ARG001 Violation Handling Strategy

#### Pytest Hook Functions

- **Pattern**: Functions like `pytest_runtest_setup`, `pytest_assertrepr_compare`, `pytest_exception_interact`
- **Strategy**: Rename unused arguments with underscore prefix (e.g., `item` → `_item`)
- **Rationale**: These functions must maintain specific signatures required by pytest interface

#### Mock Functions in Tests

- **Pattern**: Nested mock functions that need to accept arbitrary arguments
- **Strategy**: Rename to indicate intentional non-use (`*args` → `*_args`, `**kwargs` → `**_kwargs`)
- **Rationale**: Mock functions often need to match signatures but don't use all arguments

#### Utility Functions

- **Pattern**: Functions with arguments that may be used in future or for interface compliance
- **Strategy**: Analyze usage context - rename with underscore if keeping for interface, remove if truly unused
- **Rationale**: Maintain clean interfaces while indicating intentional design decisions

#### Validation Requirements

- Every fix must be followed by `pre-commit run --all-files` passing
- Every fix must be followed by `hatch run pytest` passing
- Every fix must be followed by `hatch run ruff check [modified_files] --select ARG001` passing
- No task completion without all validation steps succeeding
