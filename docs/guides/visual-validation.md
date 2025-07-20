# Visual Validation Guide

This guide covers the visual validation system for comparing original and recreated documents, including threshold configuration, validation procedures, and troubleshooting visual differences.

## Overview

The Multi-Format Document Engine includes a comprehensive visual validation system that compares original documents with recreated versions to ensure visual fidelity. The system uses advanced image comparison techniques and provides detailed reports on differences.

## Basic Visual Validation

### Automatic Validation

Visual validation is automatically performed in full mode:

```bash
# Full pipeline includes automatic visual validation
python main.py --mode full --input original.pdf --output recreated.pdf

# This creates:
# - recreated.pdf (the recreated document)
# - diff.png (visual comparison image)
# - validation report (if configured)
```

### Manual Visual Comparison

Compare documents manually using the visual comparison module:

```bash
# Basic comparison
python -m src.compare_pdfs_visual original.pdf recreated.pdf output/comparison.png

# With custom threshold
python -m src.compare_pdfs_visual original.pdf recreated.pdf output/comparison.png --threshold 0.95

# Verbose output with detailed analysis
python -m src.compare_pdfs_visual original.pdf recreated.pdf output/comparison.png --verbose
```

## Understanding Visual Validation

### How Visual Validation Works

The system performs several types of comparisons:

1. **Pixel-by-pixel comparison**: Direct image comparison at the pixel level
2. **Structural similarity**: Compares document structure and layout
3. **Text content validation**: Verifies text accuracy and positioning
4. **Font rendering comparison**: Checks font rendering differences
5. **Color accuracy**: Validates color reproduction

### Validation Metrics

The system provides several metrics:

- **Similarity Score**: Overall similarity percentage (0-100%)
- **Pixel Difference Count**: Number of differing pixels
- **Structural Similarity Index (SSIM)**: Advanced similarity metric
- **Text Accuracy**: Percentage of correctly reproduced text
- **Font Matching**: Font rendering accuracy score

## Threshold Configuration

### Default Thresholds

The system uses these default thresholds:

```python
# Default validation thresholds
DEFAULT_THRESHOLDS = {
    'visual_similarity': 0.95,      # 95% visual similarity required
    'pixel_difference': 0.05,       # Max 5% pixel differences
    'text_accuracy': 0.98,          # 98% text accuracy required
    'font_similarity': 0.90,        # 90% font rendering similarity
    'color_tolerance': 10,          # RGB color difference tolerance
    'position_tolerance': 2.0,      # Pixel position tolerance
}
```

### Configuring Thresholds

#### Via Configuration File

Create a `validation_config.json` file:

```json
{
  "validation_thresholds": {
    "visual_similarity": 0.92,
    "pixel_difference": 0.08,
    "text_accuracy": 0.95,
    "font_similarity": 0.85,
    "color_tolerance": 15,
    "position_tolerance": 3.0
  },
  "validation_options": {
    "ignore_minor_spacing": true,
    "ignore_font_hinting": true,
    "ignore_compression_artifacts": true,
    "generate_detailed_report": true,
    "save_difference_images": true
  }
}
```

#### Programmatic Configuration

```python
from src.engine.validation_strategy import ValidationConfig
from src.engine.visual_validator import validate_documents

# Create custom validation configuration
config = ValidationConfig(
    visual_similarity_threshold=0.90,
    pixel_difference_threshold=0.10,
    text_accuracy_threshold=0.95,
    font_similarity_threshold=0.85,
    color_tolerance=20,
    position_tolerance=5.0,

    # Advanced options
    ignore_minor_spacing=True,
    ignore_font_hinting=True,
    ignore_compression_artifacts=True,
    generate_detailed_report=True
)

# Perform validation with custom config
result = validate_documents('original.pdf', 'recreated.pdf', config)
print(f"Validation passed: {result.passed}")
print(f"Similarity score: {result.similarity_score:.2%}")
```

### Threshold Guidelines

#### Strict Validation (Legal/Financial Documents)

```json
{
  "visual_similarity": 0.98,
  "pixel_difference": 0.02,
  "text_accuracy": 0.999,
  "font_similarity": 0.95,
  "color_tolerance": 5,
  "position_tolerance": 1.0
}
```

#### Standard Validation (Business Documents)

```json
{
  "visual_similarity": 0.95,
  "pixel_difference": 0.05,
  "text_accuracy": 0.98,
  "font_similarity": 0.90,
  "color_tolerance": 10,
  "position_tolerance": 2.0
}
```

#### Lenient Validation (Draft/Template Documents)

```json
{
  "visual_similarity": 0.90,
  "pixel_difference": 0.10,
  "text_accuracy": 0.95,
  "font_similarity": 0.80,
  "color_tolerance": 20,
  "position_tolerance": 5.0
}
```

## Advanced Validation Procedures

### Comprehensive Validation Workflow

```python
from src.engine.visual_validator import validate_documents
from src.engine.validation_report import generate_validation_report
from src.engine.validation_strategy import ValidationConfig

def comprehensive_validation(original_path, recreated_path, output_dir):
    """Perform comprehensive document validation"""

    # Configure validation
    config = ValidationConfig(
        visual_similarity_threshold=0.95,
        generate_detailed_report=True,
        save_difference_images=True,
        create_overlay_comparison=True
    )

    # Perform validation
    result = validate_documents(original_path, recreated_path, config)

    # Generate detailed report
    report_path = f"{output_dir}/validation_report.html"
    generate_validation_report(result, report_path)

    # Print summary
    print(f"Validation Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"Overall Similarity: {result.similarity_score:.2%}")
    print(f"Text Accuracy: {result.text_accuracy:.2%}")
    print(f"Font Similarity: {result.font_similarity:.2%}")

    if not result.passed:
        print("\nValidation Issues:")
        for issue in result.validation_issues:
            print(f"  - {issue}")

    return result

# Usage
result = comprehensive_validation('original.pdf', 'recreated.pdf', 'output/')
```

### Page-by-Page Validation

```python
def validate_by_pages(original_path, recreated_path):
    """Validate documents page by page"""

    import fitz

    original_doc = fitz.open(original_path)
    recreated_doc = fitz.open(recreated_path)

    if original_doc.page_count != recreated_doc.page_count:
        print(f"Page count mismatch: {original_doc.page_count} vs {recreated_doc.page_count}")
        return False

    all_passed = True

    for page_num in range(original_doc.page_count):
        print(f"Validating page {page_num + 1}...")

        # Extract page images
        original_page = original_doc[page_num]
        recreated_page = recreated_doc[page_num]

        original_img = original_page.get_pixmap(matrix=fitz.Matrix(2, 2))
        recreated_img = recreated_page.get_pixmap(matrix=fitz.Matrix(2, 2))

        # Save temporary images
        original_img.save(f"temp_original_page_{page_num}.png")
        recreated_img.save(f"temp_recreated_page_{page_num}.png")

        # Validate page
        config = ValidationConfig(visual_similarity_threshold=0.95)
        result = validate_documents(
            f"temp_original_page_{page_num}.png",
            f"temp_recreated_page_{page_num}.png",
            config
        )

        if not result.passed:
            print(f"  Page {page_num + 1} FAILED validation")
            print(f"  Similarity: {result.similarity_score:.2%}")
            all_passed = False
        else:
            print(f"  Page {page_num + 1} PASSED validation")

        # Clean up temporary files
        import os
        os.remove(f"temp_original_page_{page_num}.png")
        os.remove(f"temp_recreated_page_{page_num}.png")

    original_doc.close()
    recreated_doc.close()

    return all_passed
```

## Validation Reports

### HTML Validation Report

Generate comprehensive HTML reports:

```python
from src.engine.validation_report import generate_validation_report

def create_detailed_report(validation_result, output_path):
    """Create detailed HTML validation report"""

    report_config = {
        'include_thumbnails': True,
        'include_difference_overlay': True,
        'include_metrics_charts': True,
        'include_recommendations': True,
        'template': 'detailed'  # or 'summary', 'technical'
    }

    generate_validation_report(
        validation_result,
        output_path,
        config=report_config
    )

    print(f"Detailed report saved to: {output_path}")
```

### JSON Validation Report

Export validation results as JSON:

```python
import json

def export_validation_json(validation_result, output_path):
    """Export validation results as JSON"""

    report_data = {
        'validation_summary': {
            'passed': validation_result.passed,
            'overall_similarity': validation_result.similarity_score,
            'text_accuracy': validation_result.text_accuracy,
            'font_similarity': validation_result.font_similarity,
            'timestamp': validation_result.timestamp.isoformat()
        },
        'metrics': {
            'pixel_differences': validation_result.pixel_differences,
            'color_differences': validation_result.color_differences,
            'position_differences': validation_result.position_differences,
            'font_differences': validation_result.font_differences
        },
        'issues': validation_result.validation_issues,
        'recommendations': validation_result.recommendations
    }

    with open(output_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"JSON report saved to: {output_path}")
```

## Troubleshooting Visual Differences

### Common Issues and Solutions

#### Issue: Font Rendering Differences

**Symptoms**: Text appears slightly different, font metrics don't match
**Diagnosis**:

```python
# Check font availability
from src.font.font_validator import FontValidator

validator = FontValidator()
result = validator.validate_document_fonts('layout_config.json')

for warning in result.font_warnings:
    print(f"Font issue: {warning}")
```

**Solutions**:

1. **Use template mode** to preserve original font rendering
2. **Install missing fonts** in the system or `downloaded_fonts/`
3. **Override font mappings** in `manual_overrides.json5`
4. **Adjust font similarity threshold** for minor differences

#### Issue: Color Differences

**Symptoms**: Colors appear slightly different between original and recreated
**Diagnosis**:

```python
# Analyze color differences
config = ValidationConfig(
    color_tolerance=5,  # Strict color matching
    generate_color_analysis=True
)

result = validate_documents('original.pdf', 'recreated.pdf', config)
print(f"Color differences found: {len(result.color_differences)}")
```

**Solutions**:

1. **Increase color tolerance** in validation config
2. **Check color space conversion** issues
3. **Use template mode** for pixel-perfect color reproduction
4. **Override specific colors** in manual overrides

#### Issue: Position/Layout Differences

**Symptoms**: Elements appear in slightly different positions
**Diagnosis**:

```python
# Check positioning accuracy
config = ValidationConfig(
    position_tolerance=1.0,  # Strict positioning
    generate_position_analysis=True
)

result = validate_documents('original.pdf', 'recreated.pdf', config)
for diff in result.position_differences:
    print(f"Position difference: {diff}")
```

**Solutions**:

1. **Adjust position tolerance** in validation config
2. **Check font metrics** and line spacing
3. **Use manual overrides** to correct specific positions
4. **Enable template mode** for exact positioning

### Advanced Troubleshooting

#### Debug Mode Validation

```python
def debug_validation_issues(original_path, recreated_path):
    """Debug validation issues with detailed analysis"""

    # Enable debug mode
    config = ValidationConfig(
        debug_mode=True,
        save_intermediate_images=True,
        generate_pixel_map=True,
        create_difference_heatmap=True
    )

    result = validate_documents(original_path, recreated_path, config)

    # Analyze specific issues
    if result.pixel_differences > config.pixel_difference_threshold:
        print("Pixel difference analysis:")
        print(f"  Total different pixels: {result.pixel_differences}")
        print(f"  Difference regions: {len(result.difference_regions)}")

        for region in result.difference_regions:
            print(f"    Region {region.id}: {region.bbox} - {region.difference_type}")

    if result.text_accuracy < config.text_accuracy_threshold:
        print("Text accuracy issues:")
        for text_diff in result.text_differences:
            print(f"  Text element {text_diff.element_id}:")
            print(f"    Expected: '{text_diff.expected}'")
            print(f"    Actual: '{text_diff.actual}'")
            print(f"    Similarity: {text_diff.similarity:.2%}")

    return result
```

#### Validation Metrics Analysis

```python
def analyze_validation_metrics(validation_result):
    """Analyze validation metrics for insights"""

    print("=== Validation Metrics Analysis ===")

    # Overall assessment
    if validation_result.similarity_score >= 0.98:
        print("✓ Excellent reproduction quality")
    elif validation_result.similarity_score >= 0.95:
        print("✓ Good reproduction quality")
    elif validation_result.similarity_score >= 0.90:
        print("⚠ Acceptable reproduction quality")
    else:
        print("✗ Poor reproduction quality - investigation needed")

    # Specific metric analysis
    metrics = {
        'Text Accuracy': validation_result.text_accuracy,
        'Font Similarity': validation_result.font_similarity,
        'Color Accuracy': validation_result.color_accuracy,
        'Position Accuracy': validation_result.position_accuracy
    }

    print("\nDetailed Metrics:")
    for metric, value in metrics.items():
        status = "✓" if value >= 0.95 else "⚠" if value >= 0.90 else "✗"
        print(f"  {status} {metric}: {value:.2%}")

    # Recommendations
    print("\nRecommendations:")
    if validation_result.text_accuracy < 0.95:
        print("  - Check font availability and mappings")
        print("  - Consider using template mode")

    if validation_result.color_accuracy < 0.95:
        print("  - Verify color space handling")
        print("  - Check color profile conversion")

    if validation_result.position_accuracy < 0.95:
        print("  - Review font metrics and spacing")
        print("  - Check manual positioning overrides")
```

## Best Practices

### Validation Workflow Best Practices

1. **Start with lenient thresholds** and gradually tighten them
2. **Use template mode** for documents with complex graphics
3. **Validate incrementally** during development
4. **Document threshold decisions** for your use case
5. **Regular validation** of your processing pipeline

### Performance Optimization

```python
def optimized_validation(original_path, recreated_path):
    """Optimized validation for large documents"""

    # Use sampling for large documents
    config = ValidationConfig(
        sample_pages=True,
        sample_ratio=0.1,  # Validate 10% of pages
        quick_mode=True,   # Skip detailed analysis
        parallel_processing=True
    )

    result = validate_documents(original_path, recreated_path, config)

    # If quick validation fails, do full validation
    if not result.passed:
        print("Quick validation failed, performing full validation...")
        full_config = ValidationConfig(
            generate_detailed_report=True,
            save_difference_images=True
        )
        result = validate_documents(original_path, recreated_path, full_config)

    return result
```

### Continuous Integration

```bash
#!/bin/bash
# validation_ci.sh - CI script for validation

echo "Running document validation tests..."

# Process test documents
python main.py --mode full --input test_docs/sample1.pdf --output output/sample1_recreated.pdf
python main.py --mode full --input test_docs/sample2.pdf --output output/sample2_recreated.pdf

# Run validation with strict thresholds
python -c "
from src.engine.visual_validator import validate_documents
from src.engine.validation_strategy import ValidationConfig

config = ValidationConfig(visual_similarity_threshold=0.98)

results = []
results.append(validate_documents('test_docs/sample1.pdf', 'output/sample1_recreated.pdf', config))
results.append(validate_documents('test_docs/sample2.pdf', 'output/sample2_recreated.pdf', config))

all_passed = all(r.passed for r in results)
print(f'All validations passed: {all_passed}')

if not all_passed:
    exit(1)
"

echo "Validation tests completed"
```

This visual validation guide provides comprehensive coverage of the validation system, from basic usage to advanced troubleshooting and optimization techniques.
