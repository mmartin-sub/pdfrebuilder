"""
Visual validator module for the Multi-Format Document Engine.

This module provides functionality for visually comparing documents
and generating validation reports.
"""

import logging
import os
import tempfile
from typing import Any

# Import optional dependencies
try:
    import cv2
    from PIL import Image

    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import fitz

    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    from skimage.metrics import structural_similarity

    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False

from pdfrebuilder.engine.validation_report import (
    ValidationReport,
    ValidationResult,
    create_validation_report,
    create_validation_result,
)

logger = logging.getLogger(__name__)


class VisualValidationError(Exception):
    """Raised when visual validation fails"""


class VisualValidator:
    """Visual validator for comparing documents"""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the visual validator

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.ssim_threshold = self.config.get("ssim_threshold", 0.98)
        self.rendering_dpi = self.config.get("rendering_dpi", 300)
        self.comparison_engine = self.config.get("comparison_engine", "opencv")
        self.generate_diff_images = self.config.get("generate_diff_images", True)

        # Check dependencies
        if self.comparison_engine == "opencv" and not HAS_CV2:
            logger.warning("OpenCV not available, falling back to pixel-by-pixel comparison")
            self.comparison_engine = "pixel"

        if not HAS_FITZ:
            logger.warning("PyMuPDF not available, PDF rendering will not work")

    def validate(
        self,
        original_path: str,
        generated_path: str,
        diff_image_path: str | None = None,
    ) -> ValidationResult:
        """
        Validate a generated document against the original

        Args:
            original_path: Path to original document
            generated_path: Path to generated document
            diff_image_path: Path to save difference image

        Returns:
            ValidationResult object

        Raises:
            VisualValidationError: If validation fails
        """
        try:
            # Render documents to images
            original_image_path = self._render_document_to_image(original_path)
            generated_image_path = self._render_document_to_image(generated_path)

            # Compare images
            ssim_score = self._compare_images(original_image_path, generated_image_path)

            # Generate difference image if requested
            if self.generate_diff_images and diff_image_path:
                self._generate_diff_image(original_image_path, generated_image_path, diff_image_path)

            # Create validation result
            return create_validation_result(
                ssim_score=ssim_score,
                threshold=self.ssim_threshold,
                original_path=original_path,
                generated_path=generated_path,
                diff_image_path=diff_image_path,
                details={
                    "rendering_dpi": self.rendering_dpi,
                    "comparison_engine": self.comparison_engine,
                },
            )

        except Exception as e:
            raise VisualValidationError(f"Validation failed: {e!s}")

    def _render_document_to_image(self, document_path: str) -> str:
        """
        Render a document to an image

        Args:
            document_path: Path to document

        Returns:
            Path to rendered image

        Raises:
            VisualValidationError: If rendering fails
        """
        # Check file extension
        _, ext = os.path.splitext(document_path.lower())

        if ext == ".pdf":
            return self._render_pdf_to_image(document_path)
        elif ext in [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"]:
            # Already an image, just return the path
            return document_path
        else:
            raise VisualValidationError(f"Unsupported document format: {ext}")

    def _render_pdf_to_image(self, pdf_path: str) -> str:
        """
        Render a PDF to an image

        Args:
            pdf_path: Path to PDF

        Returns:
            Path to rendered image

        Raises:
            VisualValidationError: If rendering fails
        """
        if not HAS_FITZ:
            raise VisualValidationError("PyMuPDF not available, cannot render PDF")

        try:
            # Create temporary file for the image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            # Open PDF
            doc = fitz.open(pdf_path)

            # For now, we only render the first page
            # TODO: Support multi-page validation
            page = doc[0]

            # Calculate zoom factor based on DPI
            zoom = self.rendering_dpi / 72.0  # 72 DPI is the PDF default

            # Create pixmap
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))

            # Save pixmap as PNG
            pix.save(tmp_path)

            return tmp_path

        except Exception as e:
            raise VisualValidationError(f"Failed to render PDF: {e!s}")

    def _compare_images(self, image1_path: str, image2_path: str) -> float:
        """
        Compare two images and return SSIM score

        Args:
            image1_path: Path to first image
            image2_path: Path to second image

        Returns:
            SSIM score (0.0-1.0)

        Raises:
            VisualValidationError: If comparison fails
        """
        if self.comparison_engine == "opencv":
            return self._compare_images_opencv(image1_path, image2_path)
        else:
            return self._compare_images_pixel(image1_path, image2_path)

    def _compare_images_opencv(self, image1_path: str, image2_path: str) -> float:
        """
        Compare two images using SSIM (Structural Similarity Index)

        Args:
            image1_path: Path to first image
            image2_path: Path to second image

        Returns:
            SSIM score (0.0-1.0)

        Raises:
            VisualValidationError: If comparison fails
        """
        if not HAS_CV2:
            raise VisualValidationError("OpenCV not available")

        try:
            # Load images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)

            # Check if images were loaded
            if img1 is None:
                raise VisualValidationError(f"Failed to load image: {image1_path}")
            if img2 is None:
                raise VisualValidationError(f"Failed to load image: {image2_path}")

            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Resize if dimensions don't match
            if gray1.shape != gray2.shape:
                logger.warning("Image dimensions don't match, resizing")
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))

            # Calculate SSIM using scikit-image if available, otherwise fallback
            if HAS_SKIMAGE:
                # Use scikit-image's structural_similarity (modern approach)
                ssim_score, _ = structural_similarity(gray1, gray2, full=True, gradient=False)
            else:
                # Fallback to a simple correlation-based similarity measure
                logger.warning("scikit-image not available, using correlation-based similarity")
                # Normalize images to 0-1 range
                gray1_norm = gray1.astype(float) / 255.0
                gray2_norm = gray2.astype(float) / 255.0

                # Calculate correlation coefficient as a similarity measure
                correlation = cv2.matchTemplate(gray1_norm, gray2_norm, cv2.TM_CCOEFF_NORMED)
                ssim_score = float(correlation[0, 0])

                # Ensure score is in valid range
                ssim_score = max(0.0, min(1.0, ssim_score))

            return float(ssim_score)

        except Exception as e:
            raise VisualValidationError(f"Failed to compare images: {e!s}")

    def _compare_images_pixel(self, image1_path: str, image2_path: str) -> float:
        """
        Compare two images pixel by pixel

        Args:
            image1_path: Path to first image
            image2_path: Path to second image

        Returns:
            Similarity score (0.0-1.0)

        Raises:
            VisualValidationError: If comparison fails
        """
        try:
            # Load images
            img1 = Image.open(image1_path).convert("RGB")
            img2 = Image.open(image2_path).convert("RGB")

            # Resize if dimensions don't match
            if img1.size != img2.size:
                logger.warning("Image dimensions don't match, resizing")
                img2 = img2.resize(img1.size)

            # Get pixel data
            pixels1 = list(img1.getdata())
            pixels2 = list(img2.getdata())

            # Calculate pixel-by-pixel similarity
            total_pixels = len(pixels1)
            matching_pixels = 0

            for i in range(total_pixels):
                # Calculate color distance
                r1, g1, b1 = pixels1[i]
                r2, g2, b2 = pixels2[i]

                # Simple Euclidean distance in RGB space
                distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

                # Consider pixels matching if distance is small
                if distance < 10:  # Threshold for "matching" pixels
                    matching_pixels += 1

            return matching_pixels / total_pixels

        except Exception as e:
            raise VisualValidationError(f"Failed to compare images pixel by pixel: {e!s}")

    def _generate_diff_image(self, image1_path: str, image2_path: str, output_path: str) -> None:
        """
        Generate a difference image

        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            output_path: Path to save difference image

        Raises:
            VisualValidationError: If generation fails
        """
        if not HAS_CV2:
            logger.warning("OpenCV not available, skipping diff image generation")
            return

        try:
            # Load images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)

            # Check if images were loaded
            if img1 is None:
                raise VisualValidationError(f"Failed to load image: {image1_path}")
            if img2 is None:
                raise VisualValidationError(f"Failed to load image: {image2_path}")

            # Resize if dimensions don't match
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

            # Calculate absolute difference
            diff = cv2.absdiff(img1, img2)

            # Enhance difference for visibility
            diff_enhanced = cv2.convertScaleAbs(diff, alpha=5.0)

            # Apply color map for better visualization
            diff_color = cv2.applyColorMap(diff_enhanced, cv2.COLORMAP_JET)

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            # Save difference image
            cv2.imwrite(output_path, diff_color)

        except Exception as e:
            raise VisualValidationError(f"Failed to generate difference image: {e!s}")


def validate_documents(
    original_path: str,
    generated_path: str,
    diff_image_path: str | None = None,
    config: dict[str, Any] | None = None,
) -> ValidationResult:
    """
    Validate a generated document against the original

    Args:
        original_path: Path to original document
        generated_path: Path to generated document
        diff_image_path: Path to save difference image
        config: Configuration dictionary

    Returns:
        ValidationResult object
    """
    validator = VisualValidator(config)
    return validator.validate(original_path, generated_path, diff_image_path)


def batch_validate_documents(
    document_pairs: list[tuple[str, str]],
    output_dir: str,
    report_name: str = "validation_report",
    config: dict[str, Any] | None = None,
    generate_formats: list[str] | None = None,
) -> ValidationReport:
    """
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
    """
    validator = VisualValidator(config)
    results = []

    # Default formats if none specified
    if generate_formats is None:
        generate_formats = ["json", "html"]

    # Validate each document pair
    for i, (original_path, generated_path) in enumerate(document_pairs):
        diff_image_path = os.path.join(output_dir, f"{report_name}_diff_{i}.png")
        result = validator.validate(original_path, generated_path, diff_image_path)
        results.append(result)

    # Create validation report
    report = create_validation_report(
        document_name=report_name,
        results=results,
        metadata={
            "config": config,
        },
    )

    # Save report
    report_path = os.path.join(output_dir, f"{report_name}.json")
    report.save_report(report_path)

    # Generate HTML report
    html_report_path = os.path.join(output_dir, f"{report_name}.html")
    report.generate_html_report(html_report_path)

    return report
