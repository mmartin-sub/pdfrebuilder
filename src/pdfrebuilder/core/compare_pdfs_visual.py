import logging
import os
import traceback

from pdfrebuilder.engine.validation_report import generate_validation_report
from pdfrebuilder.engine.visual_validator import validate_documents
from pdfrebuilder.font.font_validator import FontValidator
from pdfrebuilder.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Define error codes
ERROR_CODES = {
    "SUCCESS": 0,
    "ORIGINAL_PDF_NOT_FOUND": 1,
    "REBUILT_PDF_NOT_FOUND": 2,
    "ONE_PDF_EMPTY": 3,
    "VISUAL_DIFFERENCE_FOUND": 4,
    "EXCEPTION_OCCURRED": 5,
}


def compare_pdfs_visual(original_path, generated_path, diff_image_base_path, visual_diff_threshold=None):
    """
    Compare two documents visually using the advanced visual validation system.

    Args:
        original_path: Path to the original document
        generated_path: Path to the generated document
        diff_image_base_path: Base path for saving difference images
        visual_diff_threshold: Optional threshold for visual difference detection
                              (if None, use the value from CONFIG)

    Returns:
        int: Error code indicating the result of the comparison
    """
    logger.info("\n--- Running Visual Comparison ---")

    if not os.path.exists(original_path):
        logger.error(f"Original document not found for comparison: {original_path}")
        return ERROR_CODES["ORIGINAL_PDF_NOT_FOUND"]

    if not os.path.exists(generated_path):
        logger.error(f"Generated document not found for comparison: {generated_path}")
        return ERROR_CODES["REBUILT_PDF_NOT_FOUND"]

    try:
        # Get threshold from settings if not specified
        if visual_diff_threshold is None:
            visual_diff_threshold = settings.validation.visual_diff_threshold

        # Convert pixel threshold to SSIM threshold (inverse relationship)
        # Higher pixel threshold = lower SSIM threshold
        ssim_threshold = max(0.0, min(1.0, 1.0 - (visual_diff_threshold / 100.0)))

        # Create validation config (as dict expected by validate_documents)
        config = {
            "ssim_threshold": ssim_threshold,
            "rendering_dpi": 300,
            "generate_diff_images": True,
            "pixel_threshold": visual_diff_threshold,
        }

        # Get output directory from diff_image_base_path
        output_dir = os.path.dirname(diff_image_base_path) or "."

        # Run validation
        result = validate_documents(
            original_path=original_path,
            generated_path=generated_path,
            config=config,
        )

        # Perform font validation if layout config is available
        font_validation_result = None
        try:
            layout_config_path = "layout_config.json"
            if os.path.exists(layout_config_path):
                import json

                with open(layout_config_path, encoding="utf-8") as f:
                    layout_config = json.load(f)

                font_validator = FontValidator()
                font_validation = font_validator.validate_document_fonts(layout_config)

                # Convert FontValidationResult to dict for serialization
                font_validation_result = {
                    "fonts_required": list(font_validation.fonts_required),
                    "fonts_available": list(font_validation.fonts_available),
                    "fonts_missing": list(font_validation.fonts_missing),
                    "fonts_substituted": [
                        {
                            "original_font": sub.original_font,
                            "substituted_font": sub.substituted_font,
                            "reason": sub.reason,
                            "text_content": sub.text_content,
                            "element_id": sub.element_id,
                            "page_number": sub.page_number,
                        }
                        for sub in font_validation.fonts_substituted
                    ],
                    "font_coverage_issues": font_validation.font_coverage_issues,
                    "validation_passed": font_validation.validation_passed,
                    "validation_messages": font_validation.validation_messages,
                }

                logger.info(
                    f"Font validation completed: {len(font_validation.fonts_required)} fonts required, "
                    f"{len(font_validation.fonts_missing)} missing, "
                    f"{len(font_validation.fonts_substituted)} substituted"
                )
        except Exception as e:
            logger.warning(f"Font validation failed: {e}")

        # Generate comprehensive validation reports
        reports_dir = os.path.join(output_dir, "reports")
        report_paths = generate_validation_report(
            original_path=original_path,
            generated_path=generated_path,
            validation_result=result,
            output_dir=reports_dir,
            report_formats=["json", "html", "ci"],
            font_validation_result=font_validation_result,
        )

        # TASK 3.3: Enhanced console output with file paths and scores
        print(f"Comparing: {original_path} vs {generated_path}")
        print("Method: SSIM")
        print(f"Score: {result.ssim_score:.4f} (Threshold: {ssim_threshold:.4f})")

        # Determine pass/fail based on threshold
        passed = result.ssim_score >= ssim_threshold
        result_status = "PASS" if passed else "FAIL"
        print(f"Result: {result_status}")

        if not passed:
            print(f"Reason: SSIM below threshold ({result.ssim_score:.4f} < {ssim_threshold:.4f})")
            if result.diff_image_path:
                print(f"Diagnostic image saved to: {result.diff_image_path}")

        # TASK 3.3: Actionable diagnostic information (requirement 7.3)
        if not passed:
            logger.error("=== VALIDATION FAILED ===")
            logger.error(f"Average SSIM: {result.ssim_score:.4f}")
            logger.error(f"Threshold: {ssim_threshold:.4f}")
            logger.error(f"Difference: {ssim_threshold - result.ssim_score:.4f}")

            # Provide actionable diagnostic information
            if result.ssim_score < 0.5:
                logger.error("DIAGNOSTIC: Major visual differences detected. Check for:")
                logger.error("  - Missing or incorrect fonts")
                logger.error("  - Layout rendering issues")
                logger.error("  - Image processing problems")
            elif result.ssim_score < 0.8:
                logger.error("DIAGNOSTIC: Moderate visual differences detected. Check for:")
                logger.error("  - Minor font rendering differences")
                logger.error("  - Slight layout variations")
                logger.error("  - Color profile differences")
            else:
                logger.error("DIAGNOSTIC: Minor visual differences detected. Check for:")
                logger.error("  - Anti-aliasing differences")
                logger.error("  - Compression artifacts")
                logger.error("  - Rounding errors in positioning")

            logger.error(f"Validation report: {report_paths.get('html', '')}")
            return ERROR_CODES["VISUAL_DIFFERENCE_FOUND"]
        else:
            logger.info("=== VALIDATION PASSED ===")
            logger.info(f"Average SSIM: {result.ssim_score:.4f}")
            logger.info(f"Validation report: {report_paths.get('html', '')}")
            return ERROR_CODES["SUCCESS"]

    except Exception as e:
        logger.error(f"An error occurred during document comparison: {e}")
        traceback.print_exc()  # Print detailed traceback for debugging
        return ERROR_CODES["EXCEPTION_OCCURRED"]
