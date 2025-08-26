# Implementation Plan

- [x] 1. Immediate vulture violation fixes
  - Fix all current vulture violations in the codebase
  - Validate each fix with pre-commit and pytest
  - Ensure clean vulture run before proceeding
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3_

- [x] 1.1 Fix unused import in extract_wand_content.py
  - Analyze the unused 'wand' import on line 66
  - Remove import if truly unused or add vulture ignore with justification
  - Run pre-commit and pytest to validate fix
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 1.2 Fix unused variable in test_wand_multi_format.py
  - Analyze the unused 'mock_makedirs' variable on line 92
  - Either remove variable or rename with underscore prefix
  - Run pre-commit and pytest to validate fix
  - _Requirements: 2.1, 2.2, 4.1, 4.2, 4.3_

- [x] 1.3 Comprehensive vulture scan and cleanup
  - Run full vulture scan to identify any additional violations
  - Fix any remaining violations using established patterns
  - Validate complete codebase passes vulture checks
  - _Requirements: 1.1, 1.3, 2.1, 2.3, 4.1, 4.2, 4.3_

- [x] 2. Enhance pre-commit vulture configuration
  - Review current vulture configuration in pre-commit hooks
  - Strengthen settings to catch violations earlier
  - Configure appropriate confidence thresholds and exclusions
  - Test enhanced configuration with current codebase
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 2.1 Update vulture pre-commit hook settings
  - Modify .pre-commit-config.yaml to use stricter vulture settings
  - Set appropriate confidence threshold (currently appears to be 90%)
  - Ensure all Python files are included in vulture scan
  - _Requirements: 3.1, 3.2_

- [x] 2.2 Create vulture whitelist maintenance process
  - Review and update .vulture_whitelist.py if it exists
  - Document approved patterns for vulture ignores
  - Create process for reviewing and approving new whitelist entries
  - _Requirements: 3.3_

- [x] 3. Implement prevention methodology
  - Create developer guidelines for avoiding vulture violations
  - Set up automated enforcement in CI/CD pipeline
  - Document best practices for clean code maintenance
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3.1 Create developer guidelines document
  - Write guidelines for avoiding unused imports and variables
  - Document common patterns that lead to vulture violations
  - Include examples of proper import management
  - Add to project documentation or contributing guidelines
  - _Requirements: 3.2, 3.3_

- [x] 3.2 Configure IDE integration recommendations
  - Document how to set up vulture warnings in popular IDEs
  - Create configuration files for VS Code and PyCharm
  - Include real-time linting setup instructions
  - _Requirements: 3.1, 3.2_

- [ ] 4. Fix ruff ARG001 unused function argument violations
  - Systematically address all unused function argument violations
  - Apply appropriate fix strategy for each violation type
  - Validate each fix with pre-commit and pytest
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3_

- [x] 4.1 Fix unused arguments in src/font_utils.py
  - Analyze _validate_font_before_registration function's text_content argument
  - Either rename with underscore prefix or remove if truly unused
  - Run pre-commit and pytest to validate fix
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3_

- [x] 4.2 Fix unused arguments in tests/conftest.py pytest hooks
  - Fix pytest_runtest_setup item argument (rename to _item)
  - Fix pytest_assertrepr_compare config argument (rename to _config)
  - Fix pytest_exception_interact node and report arguments (rename to _node,_report)
  - Run pre-commit and pytest to validate fixes
  - _Requirements: 4.1, 4.2, 4.4, 5.1, 5.2, 5.3_

- [ ] 4.3 Fix unused arguments in tests/font_error_test_utils.py
  - Fix mock_insert_font args and kwargs arguments (rename to *_args, **_kwargs)
  - Fix mock_validate_fallback_font font_name and page arguments (rename to _font_name, _page)
  - Run pre-commit and pytest to validate fixes
  - _Requirements: 4.1, 4.2, 4.4, 5.1, 5.2, 5.3_

- [ ] 4.4 Comprehensive ruff ARG001 scan and cleanup
  - Run full ruff check with ARG001 to identify any additional violations
  - Fix any remaining violations using established patterns
  - Validate complete codebase passes ruff ARG001 checks
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3_

- [ ] 5. Fix ruff UP035/UP038 typing modernization violations
  - Systematically modernize deprecated typing imports to use built-in types
  - Update isinstance calls to use modern union syntax where appropriate
  - Validate each fix with pre-commit and pytest
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3_

- [x] 5.1 Fix typing imports in tests/test_utils.py
  - Replace `from typing import Any, Dict, List, Optional, Union` with modern equivalents
  - Update type annotations to use built-in dict, list instead of typing.Dict, typing.List
  - Update isinstance call on line 356 to use union syntax instead of tuple syntax
  - Also fixed isinstance calls in src/render.py lines 285, 288, 293 to use union syntax
  - Run pre-commit and pytest to validate fixes
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3_

- [ ] 5.2 Comprehensive ruff UP035/UP038 scan and cleanup
  - Run full ruff check with UP035 and UP038 to identify any additional violations
  - Fix any remaining typing modernization issues using established patterns
  - Validate complete codebase passes ruff UP035/UP038 checks
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3_

- [x] 6. Final validation and documentation
  - Ensure all pre-commit hooks pass completely
  - Verify full test suite passes with hatch run pytest
  - Document any intentional linter ignores with justification
  - Create maintenance checklist for future code quality
  - _Requirements: 6.1, 6.2, 6.3_
