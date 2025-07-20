"""
Tests for the visual PDF comparison functionality.

This module tests the compare_pdfs_visual.py functionality including:
- Visual comparison of PDF documents
- Error handling for missing files
- Threshold-based comparison logic
- Error code returns
- Font validation integration
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.compare_pdfs_visual import ERROR_CODES, compare_pdfs_visual


class TestComparePDFsVisual(unittest.TestCase):
    """Test cases for visual PDF comparison functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

        # Create temporary test files
        self.original_pdf = os.path.join(self.temp_dir, "original.pdf")
        self.generated_pdf = os.path.join(self.temp_dir, "generated.pdf")
        self.diff_image_base = os.path.join(self.temp_dir, "diff")

        # Create dummy PDF files
        with open(self.original_pdf, "w") as f:
            f.write("dummy original pdf content")
        with open(self.generated_pdf, "w") as f:
            f.write("dummy generated pdf content")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_original_pdf_not_found(self):
        """Test error handling when original PDF is missing"""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.pdf")

        result = compare_pdfs_visual(non_existent_path, self.generated_pdf, self.diff_image_base)

        self.assertEqual(result, ERROR_CODES["ORIGINAL_PDF_NOT_FOUND"])

    def test_generated_pdf_not_found(self):
        """Test error handling when generated PDF is missing"""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.pdf")

        result = compare_pdfs_visual(self.original_pdf, non_existent_path, self.diff_image_base)

        self.assertEqual(result, ERROR_CODES["REBUILT_PDF_NOT_FOUND"])

    @patch("src.compare_pdfs_visual.validate_documents")
    @patch("src.compare_pdfs_visual.generate_validation_report")
    def test_successful_comparison(self, mock_generate_report, mock_validate):
        """Test successful visual comparison"""
        # Mock validation result with high SSIM score (passing)
        mock_result = Mock()
        mock_result.ssim_score = 0.99
        mock_result.diff_image_path = None
        mock_validate.return_value = mock_result

        # Mock report generation
        mock_generate_report.return_value = {"html": "report.html"}

        result = compare_pdfs_visual(
            self.original_pdf,
            self.generated_pdf,
            self.diff_image_base,
            visual_diff_threshold=5,
        )

        self.assertEqual(result, ERROR_CODES["SUCCESS"])
        mock_validate.assert_called_once()
        mock_generate_report.assert_called_once()

    @patch("src.compare_pdfs_visual.validate_documents")
    @patch("src.compare_pdfs_visual.generate_validation_report")
    def test_visual_difference_found(self, mock_generate_report, mock_validate):
        """Test handling when visual differences are found"""
        # Mock validation result with low SSIM score (failing)
        mock_result = Mock()
        mock_result.ssim_score = 0.5
        mock_result.diff_image_path = "diff.png"
        mock_validate.return_value = mock_result

        # Mock report generation
        mock_generate_report.return_value = {"html": "report.html"}

        result = compare_pdfs_visual(
            self.original_pdf,
            self.generated_pdf,
            self.diff_image_base,
            visual_diff_threshold=5,
        )

        self.assertEqual(result, ERROR_CODES["VISUAL_DIFFERENCE_FOUND"])

    @patch("src.compare_pdfs_visual.validate_documents")
    def test_exception_handling(self, mock_validate):
        """Test exception handling during comparison"""
        # Mock validation to raise an exception
        mock_validate.side_effect = Exception("Test exception")

        result = compare_pdfs_visual(self.original_pdf, self.generated_pdf, self.diff_image_base)

        self.assertEqual(result, ERROR_CODES["EXCEPTION_OCCURRED"])

    @patch("src.compare_pdfs_visual.CONFIG", {"visual_diff_threshold": 10})
    @patch("src.compare_pdfs_visual.validate_documents")
    @patch("src.compare_pdfs_visual.generate_validation_report")
    def test_default_threshold_from_config(self, mock_generate_report, mock_validate):
        """Test using default threshold from CONFIG when not specified"""
        mock_result = Mock()
        mock_result.ssim_score = 0.99
        mock_result.diff_image_path = None
        mock_validate.return_value = mock_result

        mock_generate_report.return_value = {"html": "report.html"}

        result = compare_pdfs_visual(
            self.original_pdf,
            self.generated_pdf,
            self.diff_image_base,
            # No visual_diff_threshold specified - should use CONFIG value
        )

        self.assertEqual(result, ERROR_CODES["SUCCESS"])

        # Verify ValidationConfig was created with correct threshold
        # (CONFIG value of 10 should convert to SSIM threshold of 0.9)
        call_args = mock_validate.call_args
        config = call_args[1]["config"]  # keyword argument
        expected_ssim_threshold = 1.0 - (10 / 100.0)  # 0.9
        self.assertAlmostEqual(config.ssim_threshold, expected_ssim_threshold, places=2)

    @patch("src.compare_pdfs_visual.validate_documents")
    @patch("src.compare_pdfs_visual.generate_validation_report")
    @patch("src.compare_pdfs_visual.FontValidator")
    @patch("os.path.exists")
    def test_font_validation_integration(
        self,
        mock_exists,
        mock_font_validator_class,
        mock_generate_report,
        mock_validate,
    ):
        """Test integration with font validation when layout config exists"""
        # Mock layout config file exists
        mock_exists.side_effect = lambda path: path == "layout_config.json" or path in [
            self.original_pdf,
            self.generated_pdf,
        ]

        # Mock validation result
        mock_result = Mock()
        mock_result.ssim_score = 0.99
        mock_result.diff_image_path = None
        mock_validate.return_value = mock_result

        # Mock font validator
        mock_font_validator = Mock()
        mock_font_validation = Mock()
        mock_font_validation.fonts_required = {"Arial", "Times"}
        mock_font_validation.fonts_available = {"Arial"}
        mock_font_validation.fonts_missing = {"Times"}
        mock_font_validation.fonts_substituted = []
        mock_font_validation.font_coverage_issues = []
        mock_font_validation.validation_passed = False
        mock_font_validation.validation_messages = ["Times font missing"]

        mock_font_validator.validate_document_fonts.return_value = mock_font_validation
        mock_font_validator_class.return_value = mock_font_validator

        # Mock report generation
        mock_generate_report.return_value = {"html": "report.html"}

        # Mock json.load for layout config
        with (
            patch("builtins.open"),
            patch("json.load", return_value={"test": "config"}),
        ):
            result = compare_pdfs_visual(self.original_pdf, self.generated_pdf, self.diff_image_base)

        self.assertEqual(result, ERROR_CODES["SUCCESS"])
        mock_font_validator.validate_document_fonts.assert_called_once()

    def test_error_codes_completeness(self):
        """Test that all expected error codes are defined"""
        expected_codes = [
            "SUCCESS",
            "ORIGINAL_PDF_NOT_FOUND",
            "REBUILT_PDF_NOT_FOUND",
            "ONE_PDF_EMPTY",
            "VISUAL_DIFFERENCE_FOUND",
            "EXCEPTION_OCCURRED",
        ]

        for code in expected_codes:
            self.assertIn(code, ERROR_CODES)
            self.assertIsInstance(ERROR_CODES[code], int)

    def test_threshold_conversion_logic(self):
        """Test the pixel threshold to SSIM threshold conversion"""
        # Test various threshold values
        test_cases = [
            (0, 1.0),  # 0% pixel diff = 100% SSIM
            (5, 0.95),  # 5% pixel diff = 95% SSIM
            (50, 0.5),  # 50% pixel diff = 50% SSIM
            (100, 0.0),  # 100% pixel diff = 0% SSIM
        ]

        for pixel_threshold, expected_ssim in test_cases:
            with patch("src.compare_pdfs_visual.validate_documents") as mock_validate:
                with patch("src.compare_pdfs_visual.generate_validation_report"):
                    mock_result = Mock()
                    mock_result.ssim_score = 0.99
                    mock_result.diff_image_path = None
                    mock_validate.return_value = mock_result

                    compare_pdfs_visual(
                        self.original_pdf,
                        self.generated_pdf,
                        self.diff_image_base,
                        visual_diff_threshold=pixel_threshold,
                    )

                    # Check that ValidationConfig was created with correct SSIM threshold
                    call_args = mock_validate.call_args
                    config = call_args[1]["config"]
                    self.assertAlmostEqual(config.ssim_threshold, expected_ssim, places=2)


if __name__ == "__main__":
    unittest.main()
