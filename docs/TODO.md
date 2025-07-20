# TODO List

## High Priority

### Validation Report Improvements

- [ ] **Convert HTML report generation to use Jinja2 templates**
  - Current HTML generation uses string formatting which is error-prone
  - Jinja2 templates would provide better separation of concerns
  - Easier to maintain and extend HTML report functionality
  - Better security through template auto-escaping
  - More flexible for custom report themes

### Documentation Enhancements

- [x] **Create comprehensive Makefile documentation guide** ✅
  - Added detailed guide at `docs/MAKEFILE_GUIDE.md`
  - Includes examples, git hooks setup, and CI/CD integration
  - Covers all documentation targets and best practices
  - Updated `docs/README.md` to reference the new guide

### File Organization Improvements

- [x] **Move test_file.json to proper location** ✅
  - Moved `test_file.json` from root to `tests/test_sample_config.json`
  - Follows project structure conventions for test files
  - Maintains proper organization of sample/test files

### Security Enhancements

- [ ] **Add Content Security Policy (CSP) headers to HTML reports**
  - Prevent inline script execution
  - Restrict resource loading to trusted sources
  - Add nonce-based script execution if needed

### Performance Optimizations

- [ ] **Implement caching for font downloads**
  - Cache downloaded Google Fonts to avoid re-downloading
  - Add cache invalidation strategy
  - Consider using `functools.lru_cache` for in-memory caching

## Medium Priority

### Code Quality Improvements

- [ ] **Add comprehensive type annotations**
  - Ensure all functions have proper type hints
  - Use `typing` module for complex types
  - Add type checking to CI/CD pipeline

### Testing Enhancements

- [ ] **Increase test coverage to 90%+**
  - Add unit tests for edge cases
  - Implement integration tests for complex workflows
  - Add property-based testing for data validation

### User Experience

- [ ] **Improve error messages and logging**
  - Add more descriptive error messages
  - Implement structured logging
  - Add debug mode with verbose output

## Low Priority

### Documentation Improvements

- [ ] **Add video tutorials for complex workflows**
  - Screen recordings of common use cases
  - Step-by-step visual guides
  - Interactive examples

### Performance Monitoring

- [ ] **Add performance metrics collection**
  - Monitor memory usage during processing
  - Track processing time for different document types
  - Implement performance regression testing

### Integration Features

- [ ] **Add support for more document formats**
  - Microsoft Word (.docx) support
  - OpenDocument (.odt) support
  - Rich Text Format (.rtf) support

## Completed Tasks

### ✅ **Fixed Issues (Previous Session):**

1. **Google Fonts Integration** (`src/font/googlefonts.py`):
   - ✅ Added missing `get_config_value` import
   - ✅ Fixed test URL pattern to match expected regex
   - ✅ All 13 Google Fonts tests now passing

2. **HTML Report XSS Prevention** (`src/engine/validation_report.py`):
   - ✅ Added `html` module import
   - ✅ Created `html_escape()` helper function
   - ✅ Applied HTML escaping to all user content in HTML generation
   - ✅ All XSS prevention tests now passing

3. **XML Security and Pretty Printing** (`src/engine/validation_report.py`):
   - ✅ Fixed XML pretty printing to wrap `testsuite` in `testsuites`
   - ✅ Improved error handling for malformed XML
   - ✅ Enhanced XML security monitoring
   - ✅ All XML security tests now passing

4. **Documentation Management**:
   - ✅ Created comprehensive Makefile guide (`docs/MAKEFILE_GUIDE.md`)
   - ✅ Added git hooks setup instructions
   - ✅ Included CI/CD integration examples
   - ✅ Updated docs README with quick commands

## Notes

- All critical test failures have been resolved
- Documentation generation workflow is now fully documented
- Security improvements implemented for HTML reports
- XML processing is now more robust and secure
