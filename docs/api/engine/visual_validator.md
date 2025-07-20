# visual_validator

Visual validator module for the Multi-Format Document Engine.

This module provides functionality for visually comparing documents
and generating validation reports.

## Classes

### VisualValidationError

Raised when visual validation fails

### VisualValidator

Visual validator for comparing documents

#### Methods

##### __init__(config)

Initialize the visual validator

Args:
    config: Configuration dictionary

##### validate(original_path, generated_path, diff_image_path)

Validate a generated document against the original

Args:
    original_path: Path to original document
    generated_path: Path to generated document
    diff_image_path: Path to save difference image

Returns:
    ValidationResult object

Raises:
    VisualValidationError: If validation fails

##### _render_document_to_image(document_path)

Render a document to an image

Args:
    document_path: Path to document

Returns:
    Path to rendered image

Raises:
    VisualValidationError: If rendering fails

##### _render_pdf_to_image(pdf_path)

Render a PDF to an image

Args:
    pdf_path: Path to PDF

Returns:
    Path to rendered image

Raises:
    VisualValidationError: If rendering fails

##### _compare_images(image1_path, image2_path)

Compare two images and return SSIM score

Args:
    image1_path: Path to first image
    image2_path: Path to second image

Returns:
    SSIM score (0.0-1.0)

Raises:
    VisualValidationError: If comparison fails

##### _compare_images_opencv(image1_path, image2_path)

Compare two images using SSIM (Structural Similarity Index)

Args:
    image1_path: Path to first image
    image2_path: Path to second image

Returns:
    SSIM score (0.0-1.0)

Raises:
    VisualValidationError: If comparison fails

##### _compare_images_pixel(image1_path, image2_path)

Compare two images pixel by pixel

Args:
    image1_path: Path to first image
    image2_path: Path to second image

Returns:
    Similarity score (0.0-1.0)

Raises:
    VisualValidationError: If comparison fails

##### _generate_diff_image(image1_path, image2_path, output_path)

Generate a difference image

Args:
    image1_path: Path to first image
    image2_path: Path to second image
    output_path: Path to save difference image

Raises:
    VisualValidationError: If generation fails

## Functions

### validate_documents(original_path, generated_path, diff_image_path, config)

Validate a generated document against the original

Args:
    original_path: Path to original document
    generated_path: Path to generated document
    diff_image_path: Path to save difference image
    config: Configuration dictionary

Returns:
    ValidationResult object

### batch_validate_documents(document_pairs, output_dir, report_name, config, generate_formats)

Validate multiple document pairs and generate a comprehensive report

Args:
    document_pairs: List of (original_path, generated_path) tuples
    output_dir: Directory to save difference images and report
    report_name: Base name for report files
    config: Configuration dictionary
    generate_formats: List of report formats to generate (json, html, junit, markdown)
                     If None, generates json and html formats

Returns:
    ValidationReport object
