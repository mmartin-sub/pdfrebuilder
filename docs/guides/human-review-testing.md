# Human Review Testing Guide

This comprehensive guide provides detailed instructions for developers and testers who need to perform manual validation of the PDF processing pipeline through human review tests. It covers technical implementation details, engine-specific behaviors, edge cases, and systematic validation procedures.

## Overview

Human review tests are specialized end-to-end tests that generate visual outputs requiring manual comparison to validate the accuracy and fidelity of the PDF processing pipeline. These tests are essential for ensuring that the extract → regenerate workflow maintains visual consistency and content integrity across different input engines (PyMuPDF/Fitz, Wand) and output engines (PyMuPDF, ReportLab).

### System Architecture Context

The PDF processing pipeline consists of:

- **Input Engines**: PyMuPDF (Fitz), Wand (ImageMagick)
- **Output Engines**: PyMuPDF, ReportLab
- **Universal Document Model**: Standardized intermediate representation
- **Processing Pipeline**: Extract → Transform → Generate workflow

## Quick Start

### Prerequisites

- Ensure the development environment is set up with `hatch` and all dependencies installed
- Have a PDF viewer capable of side-by-side comparison (recommended: Adobe Acrobat, Preview, or similar)

### Running Human Review Tests

```bash
# Run all human review tests (recommended for comprehensive validation)
hatch run run-human-review

# Run specific test categories
hatch run run-human-review --test-type TEXT_ONLY      # Text processing only
hatch run run-human-review --test-type DRAWINGS_ONLY  # Vector graphics only
hatch run run-human-review --test-type MIXED          # Mixed content

# Advanced options
hatch run run-human-review --open-outputs    # Auto-open PDFs for review
hatch run run-human-review --clean-outputs   # Clean up files after review

# Alternative: Use pytest directly
hatch run test -m human_review -v -s tests/test_e2e_human_review.py

# Engine-specific testing (set via environment or config)
INPUT_ENGINE=fitz OUTPUT_ENGINE=reportlab hatch run run-human-review
INPUT_ENGINE=wand OUTPUT_ENGINE=pymupdf hatch run run-human-review
```

## Engine-Specific Behaviors and Considerations

### Input Engines

#### PyMuPDF (Fitz) Input Engine

**Strengths**:

- Excellent PDF parsing capabilities with high accuracy
- Comprehensive text extraction with font metrics (ascender, descender)
- Advanced vector graphics support with path command extraction
- Reliable image extraction with format preservation
- Fast processing performance

**Known Limitations**:

- Font name mapping may use generic names ("Unnamed-T3" for embedded fonts)
- Complex path operations may be simplified during extraction
- Some advanced PDF features (3D, multimedia) not supported
- Bezier curves may be approximated in some cases

**Configuration Options**:

```python
fitz_config = {
    "density": 300,           # DPI for image extraction
    "image_format": "png",    # Output format for extracted images
    "extract_images": True,   # Enable image extraction
    "extract_text": True,     # Enable text extraction
    "extract_drawings": True, # Enable vector graphics extraction
}
```

**Edge Cases to Monitor**:

- **Embedded Fonts**: Check for "Unnamed-T3" in font names, verify fallback behavior
- **Rotated Text**: Verify `writing_direction` and `writing_mode` values
- **Complex Clipping Paths**: May be simplified or ignored
- **Transparency Effects**: Alpha channel handling in images and graphics
- **Color Spaces**: CMYK to RGB conversion accuracy

#### Wand (ImageMagick) Input Engine

**Strengths**:

- Excellent support for PSD and layered image formats
- Advanced image processing with color profile management
- Layer hierarchy preservation with blend modes
- Multi-page document support (TIFF, PDF)
- Comprehensive metadata extraction

**Known Limitations**:

- Limited text extraction (requires OCR for rasterized text)
- Vector graphics converted to raster images
- Dependency on system ImageMagick installation
- Memory intensive for large files

**Configuration Options**:

```python
wand_config = {
    "density": 300,              # DPI for processing
    "image_format": "png",       # Output format
    "color_profile": "sRGB",     # Color profile management
    "enable_ocr": False,         # OCR text extraction
    "layer_extraction": True,    # Extract individual layers
}
```

**Edge Cases to Monitor**:

- **Multi-page TIFF**: Proper page separation and indexing
- **PSD Layer Blend Modes**: Conversion to standard blend modes
- **Color Space Conversions**: CMYK, Lab, RGB handling
- **Large File Memory Usage**: Monitor system resources
- **Layer Visibility**: Hidden layers should be properly handled

### Output Engines

#### PyMuPDF Output Engine

**Strengths**:

- Fast rendering performance with minimal overhead
- Good vector graphics support with native PDF commands
- Compact file sizes with efficient compression
- Native PDF generation without external dependencies

**Known Limitations**:

- Limited font embedding options (uses built-in fonts)
- Bezier curves approximated with line segments
- Some advanced drawing features not supported
- Font mapping relies on system fonts

**Font Mapping**:

```python
font_mappings = {
    "Arial": "helv",           # Helvetica
    "Arial-Bold": "hebo",      # Helvetica-Bold
    "Times-Roman": "tiro",     # Times-Roman
    "Courier": "cour",         # Courier
}
```

**Engine-Specific Validation Points**:

- **Font Mapping Accuracy**: Verify Arial → helv, Times → tiro conversions
- **Vector Path Simplification**: Check if complex paths are simplified
- **Color Conversion Precision**: Integer ↔ RGB tuple accuracy
- **Image Compression Quality**: Verify image quality settings
- **Coordinate System**: Bottom-left origin handling

#### ReportLab Output Engine

**Strengths**:

- Precise positioning and measurements with sub-pixel accuracy
- Excellent font embedding support with TTF/OTF fonts
- Professional PDF output quality with advanced features
- Comprehensive typography and layout capabilities

**Known Limitations**:

- Slower rendering for complex documents
- Larger file sizes due to comprehensive PDF structure
- Canvas-based rendering model differences
- More complex configuration requirements

**Configuration Options**:

```python
reportlab_config = {
    "compression": 1,           # PDF compression level
    "embed_fonts": True,        # Enable font embedding
    "font_subsetting": True,    # Subset embedded fonts
    "precision": 1.0,           # Coordinate precision
    "color_space": "rgb",       # Color space
}
```

**Engine-Specific Validation Points**:

- **Font Registration**: Verify successful font loading and embedding
- **Paragraph Style Application**: Check text formatting accuracy
- **Color Space Handling**: RGB, CMYK color accuracy
- **Canvas Coordinate System**: Top-left vs. bottom-left origin
- **File Size Optimization**: Balance quality vs. size

## Test Categories and Validation Requirements

### 1. Text Elements Test (`test_text_elements_human_review`)

**Purpose**: Validates text extraction, font handling, and positioning accuracy.

**Generated Files**:

- `text_input_[timestamp].pdf` - Original PDF with various text elements
- `text_output_[timestamp].pdf` - Regenerated PDF from extracted data
- `text_config_[timestamp].json` - Extracted configuration data
- `text_debug_[timestamp].pdf` - Layer-by-layer debug visualization

**Technical Implementation**:

```python
# Creates test elements with various font properties
text_elements = [
    {"type": "text", "id": f"text_{i}", "content": f"Sample Text {i} - Font Variation Test"}
    for i in range(1, 6)
]
```

**Engine-Specific Validation**:

**PyMuPDF → PyMuPDF**:

- [ ] Font name preservation (check for "Unnamed-T3" substitutions)
- [ ] Font metrics accuracy (ascender, descender values)
- [ ] Character spacing normalization (`adjust_spacing` flag)
- [ ] Color integer conversion (RGB ↔ integer format)

**PyMuPDF → ReportLab**:

- [ ] Font registration success (check for fallback fonts)
- [ ] Paragraph style creation accuracy
- [ ] Coordinate system conversion (PDF → ReportLab canvas)
- [ ] Text positioning precision

**Wand → PyMuPDF** (if OCR enabled):

- [ ] OCR text accuracy vs. original
- [ ] Bounding box precision
- [ ] Font approximation quality

**Validation Checklist**:

- [ ] **Content Accuracy**: All text content matches exactly between input and output
- [ ] **Font Consistency**: Font families, sizes, and styles are preserved
- [ ] **Positioning**: Text placement and alignment are accurate (±1 pixel tolerance)
- [ ] **Character Integrity**: No missing, corrupted, or extra characters
- [ ] **Spacing**: Letter and word spacing appears natural (check `adjust_spacing` flag)
- [ ] **Color Fidelity**: Text colors match the original (check color conversion)
- [ ] **Font Metrics**: Ascender/descender values preserved for precise positioning

**Critical Edge Cases**:

- **Embedded Fonts**: Check for "Unnamed-T3" in extracted config, verify fallback behavior
- **Unicode Characters**: Test special characters, emojis, non-Latin scripts
- **Font Variations**: Bold, italic, bold-italic combinations
- **Color Formats**: Integer colors (0 = black), RGB arrays, null colors
- **Spacing Issues**: `raw_text` vs. `text` differences, `adjust_spacing` flag behavior

**Common Issues to Watch For**:

- Font substitution (Arial → Helvetica, Times → Times-Roman)
- Character encoding problems (special characters → question marks)
- Spacing irregularities (unnatural character spacing)
- Positioning drift (text offset by font metrics differences)
- Color shifts (integer ↔ RGB conversion errors)

### 2. Drawing Elements Test (`test_drawing_elements_human_review`)

**Purpose**: Validates vector graphics processing, including shapes, paths, and complex drawings.

**Generated Files**:

- `drawing_output_[timestamp].pdf` - PDF with regenerated vector graphics
- `drawing_config_[timestamp].json` - Configuration with drawing commands
- `drawing_debug_[timestamp].pdf` - Debug visualization showing element layers

**Technical Implementation**:
Uses `create_comprehensive_drawing_test_config()` which generates all supported drawing command types:

```python
drawing_commands = [
    {"cmd": "M", "pts": [x, y]},           # Move to point
    {"cmd": "L", "pts": [x, y]},           # Line to point
    {"cmd": "C", "pts": [x1,y1,x2,y2,x3,y3]}, # Cubic Bezier curve
    {"cmd": "H"},                          # Close path
    {"cmd": "rect", "bbox": [x1,y1,x2,y2]}, # Rectangle primitive
    {"cmd": "ellipse", "bbox": [x1,y1,x2,y2]} # Ellipse primitive
]
```

**Expected Elements** (verify all are present and accurate):

- [ ] **Rectangle Primitive**: `{"cmd": "rect"}` with stroke and fill
- [ ] **Rectangle Path**: Built with M, L, H commands, stroke only (red)
- [ ] **Ellipse Primitive**: `{"cmd": "ellipse"}` with fill only (blue)
- [ ] **Complex Bezier Path**: Multiple cubic curves with green stroke/yellow fill
- [ ] **Simple Lines**: Cross pattern using M, L commands (purple)
- [ ] **Triangle Path**: M, L, H commands forming triangle (orange)
- [ ] **Rounded Square**: Complex bezier curves (light blue)
- [ ] **Multiple Disconnected Paths**: Separate shapes in one element
- [ ] **Large Ellipse**: With stroke details (magenta, 4px width)
- [ ] **Invisible Shape**: Both stroke and fill are null (edge case)

**Engine-Specific Behavior**:

**PyMuPDF Output**:

- Bezier curves may be approximated with line segments
- Font mapping: uses built-in PDF fonts (helv, tiro, cour)
- Color handling: RGB tuples converted to PyMuPDF color format

**ReportLab Output**:

- Precise bezier curve rendering
- Canvas-based coordinate system (may require conversion)
- Advanced stroke/fill properties supported

**Critical Edge Cases**:

**Null Color Handling**:

```json
{
  "color": null,
  "fill": [0,0,0]
}
```

- [ ] **Fill-only shapes**: Verify no stroke is rendered
- [ ] **Stroke-only shapes**: Verify no fill is rendered
- [ ] **Both null**: Should log warning "has neither stroke nor fill"
- [ ] **Color conversion**: Integer colors (0 = black) vs RGB arrays

**Path Command Edge Cases**:

- [ ] **Empty path commands**: Should handle gracefully
- [ ] **Invalid coordinates**: Should not crash rendering
- [ ] **Unclosed paths**: H command behavior
- [ ] **Overlapping paths**: Z-order and rendering order

**Validation Checklist**:

- [ ] **Element Presence**: All 10 drawing elements are visible and complete
- [ ] **Color Accuracy**: Fill and stroke colors match expected RGB values
- [ ] **Stroke Properties**: Line widths (1.0, 1.5, 2.0, 2.5, 3.0, 4.0) are correct
- [ ] **Fill Patterns**: Solid fills are applied properly, no gradients
- [ ] **Curve Quality**: Bezier curves are smooth without jagged artifacts
- [ ] **Shape Integrity**: No distortions, scaling issues, or missing segments
- [ ] **Primitive vs Path**: Rectangle/ellipse primitives vs path-based equivalents
- [ ] **Edge Case Handling**: Invisible shape logs warning but doesn't crash

**Common Issues to Watch For**:

- **Missing vector elements**: Check debug PDF for extraction issues
- **Color shifts**: RGB [0.5, 0.0, 0.5] → purple, not gray
- **Stroke width variations**: 1px vs 2px should be visually distinct
- **Path rendering artifacts**: Jagged curves, broken line segments
- **Shape distortions**: Circles becoming ovals, squares becoming rectangles
- **Coordinate system issues**: Flipped or offset shapes

### 3. Full Pipeline Test (`test_full_pipeline_human_review`)

**Purpose**: Comprehensive validation of the complete extract → generate workflow with mixed content.

**Generated Files**:

- `mixed_input_[timestamp].pdf` - Original mixed content PDF
- `mixed_output_[timestamp].pdf` - Regenerated PDF
- `mixed_config_[timestamp].json` - Complete extracted configuration
- `mixed_debug_[timestamp].pdf` - Debug visualization
- `mixed_comparison_[timestamp].json` - Automated comparison report with SSIM score

**Comprehensive Validation Checklist**:

**Content Fidelity**:

- [ ] All text content is preserved exactly
- [ ] Text positioning matches original layout
- [ ] Font styles and formatting are consistent
- [ ] All drawing elements are present and accurate
- [ ] Colors and fills match original values

**Layout Accuracy**:

- [ ] Element spacing and margins are maintained
- [ ] Page dimensions are correct
- [ ] No unintended element overlapping
- [ ] Proper layer ordering (elements appear in correct z-order)
- [ ] Background colors and patterns are preserved

**Technical Quality**:

- [ ] No rendering artifacts or visual glitches
- [ ] Clean vector graphics without pixelation
- [ ] Proper font embedding (text remains selectable)
- [ ] Reasonable file size (not excessively large)
- [ ] PDF structure integrity maintained

### 4. Parametrized Tests (`test_parametrized_human_review`)

**Purpose**: Focused validation of specific content types in isolation.

**Test Variations**:

- `text_only` - Pure text processing validation
- `drawings_only` - Pure vector graphics validation
- `mixed` - Combined content validation

**Generated Files** (per variation):

- `param_input_[type]_[timestamp].pdf`
- `param_output_[type]_[timestamp].pdf`
- `param_config_[type]_[timestamp].json`

## Quality Assessment Framework

### SSIM Score Interpretation

The tests provide Structural Similarity Index (SSIM) scores for automated quality assessment:

| SSIM Range | Quality Level | Action Required |
|------------|---------------|-----------------|
| ≥ 0.99 | **Excellent** | ✅ Visually identical - no action needed |
| 0.95 - 0.98 | **Good** | ✅ Minor acceptable differences - monitor |
| 0.90 - 0.94 | **Acceptable** | ⚠️ Noticeable differences - investigate |
| < 0.90 | **Poor** | ❌ Significant issues - requires fixing |

### Manual Review Process

#### Step 1: Initial Assessment

1. **Run the tests** using the commands above
2. **Check console output** for SSIM scores and any error messages
3. **Verify file generation** - ensure all expected files were created

#### Step 2: Visual Comparison

1. **Open input and output PDFs** side-by-side in your PDF viewer
2. **Compare at 100% zoom** for pixel-perfect accuracy
3. **Scroll through systematically** - don't miss any sections
4. **Note discrepancies** - document any differences found

#### Step 3: Technical Analysis

1. **Review debug PDFs** to understand element processing
2. **Check JSON configs** for data completeness and accuracy
3. **Verify element categorization** (text vs. drawing vs. image)
4. **Assess extraction completeness** - ensure no elements were missed

#### Step 4: Documentation

1. **Record findings** in a structured format
2. **Capture screenshots** of any issues found
3. **Note SSIM scores** and correlate with visual assessment
4. **Prioritize issues** by severity and impact

## File Organization and Naming

All test outputs are saved in `tests/human_review_outputs/` with descriptive naming:

### File Types and Purposes

| File Pattern | Purpose | Review Priority |
|--------------|---------|-----------------|
| `*_input_*.pdf` | Original test PDFs | High - Reference for comparison |
| `*_output_*.pdf` | Generated PDFs | High - Primary validation target |
| `*_config_*.json` | Extracted data | Medium - Verify completeness |
| `*_debug_*.pdf` | Layer visualization | Medium - Understand processing |
| `*_comparison_*.json` | Automated reports | Low - Supporting data |

### Naming Convention

Files include timestamps and test identifiers for traceability:

```
text_input_1643723400_abc123.pdf
text_output_1643723400_abc123.pdf
text_config_1643723400_abc123.json
```

## Common Issues and Troubleshooting

### Test Execution Issues

**No Output Files Generated**:

- Check that the pipeline runs without errors
- Verify output directory permissions (`tests/human_review_outputs/`)
- Ensure all dependencies are installed (`hatch env create`)

**Test Failures**:

- Check pytest output for specific error messages
- Verify input file creation succeeded
- Ensure pipeline configuration is correct

### Quality Issues

**Low SSIM Scores**:

- Review debug PDFs for rendering issues
- Check font availability and loading
- Validate color space conversions
- Investigate element positioning accuracy

**Visual Discrepancies**:

- Compare at different zoom levels
- Check for subtle color shifts
- Verify font rendering consistency
- Look for positioning drift

### Performance Issues

**Slow Test Execution**:

- Tests involve PDF generation and can be slow
- Consider running specific test types instead of all tests
- Ensure adequate system resources

**Large Output Files**:

- Debug PDFs can be large due to layer visualization
- Use `--clean-outputs` flag if disk space is limited
- Archive outputs periodically

## Integration with Development Workflow

### Pre-Release Validation

Run human review tests before major releases:

```bash
# Generate comprehensive test outputs
hatch run run-human-review --test-type ALL

# Archive results with version tag
tar -czf human_review_v$(cat VERSION)_$(date +%Y%m%d).tar.gz tests/human_review_outputs/
```

### Continuous Integration

While these tests require human review, they can be integrated into CI/CD for artifact generation:

```bash
# In CI pipeline - generate artifacts for later review
hatch run test-human-review --tb=short
# Archive outputs for download and review
```

### Issue Reporting

When reporting issues found during human review:

1. **Include SSIM scores** from the test output
2. **Attach comparison screenshots** showing the issue
3. **Reference specific test files** by timestamp
4. **Describe the visual difference** clearly
5. **Assess impact severity** on end-user experience

## Best Practices

### For Testers

- **Use consistent viewing conditions** (same monitor, lighting, zoom level)
- **Take breaks** during long review sessions to maintain accuracy
- **Document systematically** - don't rely on memory
- **Cross-validate** findings with other team members when possible

### For Developers

- **Run tests locally** before submitting changes
- **Address high-severity issues** (SSIM < 0.90) immediately
- **Monitor trends** in SSIM scores over time
- **Update test expectations** when intentional changes are made

### For Project Maintenance

- **Archive test outputs** periodically to track quality trends
- **Update this documentation** when new test types are added
- **Review and refine** quality thresholds based on experience
- **Automate where possible** while preserving human oversight

## Conclusion

Human review testing is a critical component of ensuring the PDF processing pipeline maintains high fidelity and reliability. By following this guide systematically, developers and testers can effectively validate the system's performance and catch issues that automated tests might miss.

The combination of automated SSIM scoring and manual visual inspection provides comprehensive coverage for quality assurance, ensuring that the tool meets the high standards required for production document processing workflows.

## Critical Edge Cases and Known Issues

### Text Processing Edge Cases

#### Font Handling Edge Cases

**Embedded Fonts with Generic Names**:

```json
{
  "font_details": {
    "name": "Unnamed-T3",
    "size": 12,
    "color": 0
  }
}
```

**What to Check**:

- [ ] Fallback font is used (usually Helvetica/Arial)
- [ ] Text remains readable and positioned correctly
- [ ] No rendering errors in console output

**Unicode and Special Characters**:

```json
{
  "text": "Special chars: ñáéíóú, emojis: 🚀📄, symbols: ©®™"
}
```

**What to Check**:

- [ ] All characters render correctly (no question marks or boxes)
- [ ] Character encoding is preserved through pipeline
- [ ] Font supports the character set

#### Text Spacing Issues

**Character Spacing Normalization**:

```json
{
  "raw_text": "S p a c e d   T e x t",
  "text": "Spaced Text",
  "adjust_spacing": true
}
```

**What to Check**:

- [ ] `adjust_spacing: true` indicates normalization occurred
- [ ] Output uses normalized text, not raw_text
- [ ] Spacing appears natural in final PDF

### Vector Graphics Edge Cases

#### Null Color Combinations

**Critical Test Case**: Both stroke and fill are null

```json
{
  "type": "drawing",
  "color": null,
  "fill": null,
  "drawing_commands": [{"cmd": "rect", "bbox": [100,100,200,200]}]
}
```

**Expected Behavior**:

- [ ] Warning logged: "has neither stroke nor fill"
- [ ] No visible shape in output (invisible rectangle)
- [ ] No rendering errors or crashes
- [ ] Element ID included in warning message

**Test Files**:

- `tests/test_drawing_both_null.json`
- `tests/test_both_null_edge_case.py`

#### Complex Path Commands

**Bezier Curve Approximation**:

```json
{
  "cmd": "C",
  "pts": [100, 100, 150, 50, 200, 100]
}
```

**Engine-Specific Behavior**:

- **PyMuPDF**: May approximate with line segments
- **ReportLab**: Supports true bezier curves

**What to Check**:

- [ ] Curves appear smooth (not jagged lines)
- [ ] Shape maintains intended form
- [ ] No sharp corners where curves should be smooth

#### Color Format Variations

**Integer vs RGB Array Colors**:

```json
{
  "color": 0,
  "fill": [0.5, 0.0, 0.5]
}
```

**Conversion Requirements**:

- Integer 0 = RGB [0, 0, 0] (black)
- Integer 16711680 = RGB [1, 0, 0] (red)
- RGB values should be 0.0-1.0 range

### Engine-Specific Edge Cases

#### PyMuPDF Engine Issues

**Font Mapping Edge Cases**:

```python
# Font name not in mapping table
font_name = "CustomFont-Regular"  # Falls back to "helv"
```

**What to Check**:

- [ ] Unmapped fonts fall back to Helvetica
- [ ] Font cache is populated correctly
- [ ] No font loading errors in logs

**Coordinate System Issues**:

- PyMuPDF uses bottom-left origin
- Text positioning may require Y-coordinate adjustment
- Image placement coordinates may be flipped

#### ReportLab Engine Issues

**Font Registration Failures**:

```python
# Font file not found
font_path = "downloaded_fonts/CustomFont.ttf"  # May not exist
```

**What to Check**:

- [ ] Font registration warnings in logs
- [ ] Fallback to system fonts
- [ ] Text still renders (even if with different font)

**Canvas Coordinate Differences**:

- ReportLab uses different coordinate system
- Element positioning may require conversion
- Page size handling differences

#### Wand Engine Issues

**Dependency Problems**:

```python
# ImageMagick not properly installed
ImportError: "Python-Wand is not installed"
```

**What to Check**:

- [ ] ImageMagick system installation
- [ ] Python-Wand package installation
- [ ] Environment variables (MAGICK_HOME)

**Memory Usage with Large Files**:

- PSD files can be memory-intensive
- Monitor system resources during processing
- Consider file size limits for testing

### Performance and Resource Issues

#### Memory Management

**Large Document Processing**:

- Monitor memory usage during tests
- Watch for memory leaks in long-running tests
- Consider pagination for very large documents

**Disk Space Management**:

- Debug PDFs can be large (multiple layers)
- Image extraction creates additional files
- Use `--clean-outputs` for space management

#### Processing Speed

**Expected Processing Times**:

- Text-only documents: < 5 seconds
- Complex vector graphics: 10-30 seconds
- Large images/PSD files: 30+ seconds

**Performance Red Flags**:

- Processing times > 2 minutes
- Memory usage > 2GB for typical documents
- CPU usage consistently at 100%

## Advanced Troubleshooting

### Test Execution Issues

**No Output Files Generated**:

```bash
# Check pipeline execution
hatch run python main.py --mode=extract --input=test.pdf --log-level=DEBUG
```

- [ ] Check that the pipeline runs without errors
- [ ] Verify output directory permissions (`tests/human_review_outputs/`)
- [ ] Ensure all dependencies are installed (`hatch env create`)
- [ ] Check for import errors in console output

**Test Failures with DocumentMetadata Error**:

```python
# Known issue in some configurations
DocumentMetadata() takes no arguments
```

- [ ] Check if using correct DocumentMetadata import
- [ ] Verify Universal Document Model compatibility
- [ ] May need to skip tests with known issues

**Pipeline Configuration Issues**:

```python
# Missing required arguments
args_extract = argparse.Namespace(
    input_engine="fitz",  # Required for extraction
    log_file=None,        # Required parameter
    # ... other required fields
)
```

### Quality Issues

**Low SSIM Scores**:

- [ ] **SSIM < 0.90**: Investigate major rendering differences
- [ ] **SSIM 0.90-0.95**: Check for minor positioning/color issues
- [ ] **SSIM > 0.95**: Generally acceptable quality

**Systematic Quality Checks**:

1. **Review debug PDFs** for layer-by-layer analysis
2. **Check font availability** and loading success
3. **Validate color space conversions** (RGB, CMYK, integer)
4. **Investigate element positioning** accuracy
5. **Verify image compression** settings

**Visual Discrepancies**:

- [ ] Compare at 100%, 200%, and 400% zoom levels
- [ ] Check for subtle color shifts (RGB conversion errors)
- [ ] Verify font rendering consistency across elements
- [ ] Look for positioning drift (±1-2 pixel tolerance)
- [ ] Examine edge cases (null colors, complex paths)

### Performance Issues

**Slow Test Execution**:

- Tests involve PDF generation and can be slow (30+ seconds)
- Consider running specific test types: `--test-type TEXT_ONLY`
- Ensure adequate system resources (4GB+ RAM recommended)
- Check for memory leaks in long-running tests

**Large Output Files**:

- Debug PDFs can be large (10MB+) due to layer visualization
- Use `--clean-outputs` flag if disk space is limited
- Archive outputs periodically: `tar -czf review_$(date +%Y%m%d).tar.gz tests/human_review_outputs/`

**Resource Monitoring**:

```bash
# Monitor resource usage during tests
htop  # or top on macOS/Linux
# Watch for memory usage > 2GB or CPU > 90%
```

## Engine Compatibility Matrix

| Feature | PyMuPDF Input | Wand Input | PyMuPDF Output | ReportLab Output |
|---------|---------------|------------|----------------|------------------|
| **Text Extraction** | ✅ Excellent | ⚠️ OCR Only | ✅ Good | ✅ Excellent |
| **Font Embedding** | ✅ Metadata | ❌ Limited | ⚠️ Built-in Only | ✅ Full TTF/OTF |
| **Vector Graphics** | ✅ Full Support | ❌ Rasterized | ✅ Good | ✅ Excellent |
| **Bezier Curves** | ✅ Extracted | ❌ Rasterized | ⚠️ Approximated | ✅ Native |
| **Color Spaces** | ✅ RGB/CMYK | ✅ Full Support | ✅ RGB | ✅ RGB/CMYK |
| **Transparency** | ✅ Alpha Channel | ✅ Full Support | ✅ Basic | ✅ Advanced |
| **Layer Support** | ❌ Flattened | ✅ Full Hierarchy | ❌ Single Layer | ❌ Single Layer |
| **Performance** | ⚡ Fast | 🐌 Slow | ⚡ Fast | 🐌 Moderate |
| **File Size** | 📦 Compact | 📦 Variable | 📦 Small | 📦 Large |

### Recommended Engine Combinations

**For PDF Processing**:

- **Best Quality**: PyMuPDF → ReportLab
- **Best Performance**: PyMuPDF → PyMuPDF
- **Best Compatibility**: PyMuPDF → PyMuPDF

**For PSD/Image Processing**:

- **Only Option**: Wand → PyMuPDF (ReportLab has limited image support)

**For Mixed Workflows**:

- Use PyMuPDF for PDF inputs, Wand for PSD inputs
- Output to ReportLab for final production quality
- Output to PyMuPDF for draft/preview versions

## Conclusion

Human review testing is a critical component of ensuring the PDF processing pipeline maintains high fidelity and reliability across different engine combinations. This comprehensive guide provides the technical depth needed to:

1. **Understand engine-specific behaviors** and limitations
2. **Identify and validate critical edge cases** systematically
3. **Troubleshoot common issues** effectively
4. **Ensure consistent quality** across different processing paths

The combination of automated SSIM scoring and detailed manual visual inspection provides comprehensive coverage for quality assurance, ensuring that the tool meets the high standards required for production document processing workflows.

By following this guide systematically and understanding the technical implementation details, developers and testers can effectively validate the system's performance and catch issues that automated tests might miss, maintaining the reliability and accuracy of the PDF processing pipeline.
