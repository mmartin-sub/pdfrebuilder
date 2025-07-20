# Human Review Tests for PDF Processing Pipeline

This directory contains tests specifically designed for human review of the PDF processing pipeline. These tests generate input and output files that require manual comparison to validate visual fidelity and processing accuracy.

## Quick Start

### Run All Human Review Tests

```bash
# Using the dedicated runner (recommended)
hatch run run-human-review

# Or using pytest directly
hatch run test-human-review
```

### Run Specific Test Types

```bash
# Text processing only
hatch run run-human-review --test-type TEXT_ONLY

# Drawing/vector graphics only
hatch run run-human-review --test-type DRAWINGS_ONLY

# Mixed content
hatch run run-human-review --test-type MIXED
```

### Advanced Options

```bash
# Clean up files after review
hatch run run-human-review --clean-outputs

# Attempt to open PDFs automatically
hatch run run-human-review --open-outputs

# Run with pytest filters
hatch run test -m human_review -k "text_elements" -v -s
```

## Generated Files

All test outputs are saved in `tests/human_review_outputs/` with unique identifiers:

### File Types

- **`*_input_*.pdf`** - Original input PDFs created for testing
- **`*_output_*.pdf`** - Generated output PDFs from the pipeline
- **`*_config_*.json`** - Extracted configuration data
- **`*_debug_*.pdf`** - Layer-by-layer debug visualizations
- **`*_comparison_*.json`** - Automated comparison reports

### Naming Convention

Files include unique timestamps and test identifiers:

```
text_input_1643723400_abc123.pdf
text_output_1643723400_abc123.pdf
text_config_1643723400_abc123.json
```

## Test Categories

### 1. Text Elements (`test_text_elements_human_review`)

**Focus**: Text extraction, font handling, positioning

- Tests various font styles, sizes, and colors
- Validates text positioning and spacing
- Checks for font rendering consistency

**Review Checklist**:

- [ ] Text content matches between input and output
- [ ] Font rendering is consistent
- [ ] Text positioning is accurate
- [ ] No missing or corrupted characters

### 2. Drawing Elements (`test_drawing_elements_human_review`)

**Focus**: Vector graphics, shapes, paths

- Tests rectangles, ellipses, bezier curves
- Validates stroke and fill properties
- Checks complex path rendering

**Review Checklist**:

- [ ] All drawing elements are visible
- [ ] Colors match expected values
- [ ] Stroke widths are correct
- [ ] Fill patterns are applied properly
- [ ] Bezier curves are smooth
- [ ] No rendering artifacts

### 3. Full Pipeline (`test_full_pipeline_human_review`)

**Focus**: Complete processing workflow

- Tests mixed content (text + drawings)
- Validates entire extract → generate pipeline
- Provides comprehensive comparison data

**Review Checklist**:

- [ ] Content fidelity preserved
- [ ] Layout accuracy maintained
- [ ] Technical quality acceptable
- [ ] SSIM score > 0.95 (if available)

### 4. Parametrized Tests (`test_parametrized_human_review`)

**Focus**: Systematic testing of different content types

- Runs separate tests for text-only, drawings-only, and mixed content
- Provides focused validation for specific element types

## Manual Review Process

### 1. Visual Comparison

1. Open input PDF: `*_input_*.pdf`
2. Open output PDF: `*_output_*.pdf`
3. Compare side-by-side for visual differences
4. Note any discrepancies in content, positioning, or rendering

### 2. Technical Analysis

1. Check debug PDF: `*_debug_*.pdf`
   - Verify layer separation
   - Confirm element categorization
2. Review config JSON: `*_config_*.json`
   - Validate extracted data completeness
   - Check for missing elements

### 3. Quality Assessment

1. **Excellent** (SSIM ≥ 0.99): Visually identical
2. **Good** (SSIM ≥ 0.95): Minor acceptable differences
3. **Acceptable** (SSIM ≥ 0.90): Noticeable but functional
4. **Poor** (SSIM < 0.90): Significant issues requiring investigation

## Common Issues to Look For

### Text Issues

- Missing or corrupted characters
- Incorrect font rendering
- Text positioning errors
- Color/style inconsistencies

### Drawing Issues

- Missing vector elements
- Incorrect colors or fills
- Stroke width problems
- Path rendering artifacts
- Shape distortions

### Layout Issues

- Element overlap or spacing problems
- Incorrect page dimensions
- Layer ordering issues
- Background color problems

## Integration with Existing Tests

The human review tests leverage the existing e2e test infrastructure:

- **Reuses**: `create_pdf_with_elements()`, `run_pipeline()`, `validate_documents()`
- **Extends**: Adds human-focused output formatting and instructions
- **Maintains**: Same test data and pipeline logic for consistency

## Automation Integration

While these tests require human review, they can be integrated into CI/CD:

```bash
# Run tests and generate artifacts for review
hatch run test-human-review --tb=short

# Archive outputs for later review
tar -czf human_review_$(date +%Y%m%d_%H%M%S).tar.gz tests/human_review_outputs/
```

## Troubleshooting

### No Output Files Generated

- Check that the pipeline runs without errors
- Verify output directory permissions
- Ensure all dependencies are installed

### Low SSIM Scores

- Review debug PDFs for rendering issues
- Check font availability and loading
- Validate color space conversions

### Test Failures

- Check pytest output for specific error messages
- Verify input file creation succeeded
- Ensure pipeline configuration is correct

## Contributing

When adding new human review tests:

1. Follow the existing naming conventions
2. Include clear review instructions
3. Provide specific checklists for validation
4. Reuse existing infrastructure where possible
5. Document expected outputs and common issues
