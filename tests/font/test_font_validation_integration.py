"""
Integration tests for font validation in document processing.

This module tests the integration of font validation with the document
validation system, including font availability checking, substitution
tracking, and validation reporting.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.engine.validation_report import generate_validation_report
from pdfrebuilder.font.font_validator import FontSubstitution, FontValidationResult, FontValidator
from pdfrebuilder.font_utils import _track_font_substitution, set_font_validator


class TestFontValidationIntegration(unittest.TestCase):
    """Test font validation integration with document processing"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.fonts_dir = os.path.join(self.temp_dir, "fonts")
        os.makedirs(self.fonts_dir, exist_ok=True)

        # Create sample layout config
        self.sample_layout_config = {
            "version": "1.0",
            "engine": "fitz",
            "metadata": {"title": "Test Document"},
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": "page_0_base_layer",
                            "content": [
                                {
                                    "type": "text",
                                    "id": "text_0",
                                    "text": "Hello World",
                                    "font_details": {"name": "Arial-Bold", "size": 12},
                                },
                                {
                                    "type": "text",
                                    "id": "text_1",
                                    "text": "Missing Font Text",
                                    "font_details": {
                                        "name": "NonExistentFont",
                                        "size": 14,
                                    },
                                },
                            ],
                        }
                    ],
                }
            ],
        }

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_font_validator_initialization(self):
        """Test FontValidator initialization"""
        validator = FontValidator(self.fonts_dir)

        self.assertEqual(validator.fonts_dir, self.fonts_dir)
        self.assertEqual(len(validator.substitution_tracker), 0)
        self.assertIsInstance(validator.available_fonts, dict)

    def test_font_validation_result_creation(self):
        """Test FontValidationResult creation and methods"""
        result = FontValidationResult()

        # Test adding substitution
        substitution = FontSubstitution(original_font="Arial", substituted_font="Helvetica", reason="Font not found")
        result.add_substitution(substitution)

        self.assertEqual(len(result.fonts_substituted), 1)
        self.assertIn("Arial", result.fonts_missing)

        # Test adding coverage issue
        result.add_coverage_issue("Times", "Hello", ["ñ"], "text_0")

        self.assertEqual(len(result.font_coverage_issues), 1)
        self.assertEqual(result.font_coverage_issues[0]["font_name"], "Times")

        # Test adding validation message
        result.add_validation_message("Test message", "warning")

        self.assertEqual(len(result.validation_messages), 1)
        self.assertIn("[WARNING]", result.validation_messages[0])

    def test_extract_fonts_from_config(self):
        """Test font extraction from layout configuration"""
        validator = FontValidator(self.fonts_dir)
        fonts_used = validator._extract_fonts_from_config(self.sample_layout_config)

        expected_fonts = {"Arial-Bold", "NonExistentFont"}
        self.assertEqual(fonts_used, expected_fonts)

    def test_font_availability_checking(self):
        """Test font availability checking"""
        validator = FontValidator(self.fonts_dir)
        result = FontValidationResult()

        fonts_used = {"helv", "NonExistentFont"}  # helv is standard PDF font
        validator._check_font_availability(fonts_used, result)

        self.assertIn("helv", result.fonts_available)
        self.assertIn("NonExistentFont", result.fonts_missing)

    @patch("pdfrebuilder.font.font_validator.font_covers_text")
    @patch("pdfrebuilder.font.font_validator.os.path.exists")
    def test_font_coverage_checking(self, mock_exists, mock_covers_text):
        """Test font coverage checking for text elements"""
        validator = FontValidator(self.fonts_dir)
        result = FontValidationResult()

        # Mock font file existence
        mock_exists.return_value = True
        # Mock coverage failure
        mock_covers_text.return_value = False

        # Mock _find_missing_characters to return some missing chars
        with patch.object(validator, "_find_missing_characters", return_value=["ñ", "ü"]):
            validator._check_font_coverage(self.sample_layout_config, result)

        # Should have coverage issues for fonts that don't cover text
        self.assertGreater(len(result.font_coverage_issues), 0)

    def test_document_font_validation(self):
        """Test complete document font validation"""
        validator = FontValidator(self.fonts_dir)
        result = validator.validate_document_fonts(self.sample_layout_config)

        # Should have extracted fonts
        self.assertGreater(len(result.fonts_required), 0)

        # Should have validation messages
        self.assertGreater(len(result.validation_messages), 0)

        # Should have missing fonts (since we don't have the fonts in temp dir)
        self.assertGreater(len(result.fonts_missing), 0)

    def test_font_substitution_tracking(self):
        """Test font substitution tracking"""
        validator = FontValidator(self.fonts_dir)

        # Track a substitution
        validator.track_font_substitution(
            original_font="Arial",
            substituted_font="Helvetica",
            reason="Font not found",
            text_content="Hello",
            element_id="text_0",
            page_number=0,
        )

        self.assertEqual(len(validator.substitution_tracker), 1)
        substitution = validator.substitution_tracker[0]
        self.assertEqual(substitution.original_font, "Arial")
        self.assertEqual(substitution.substituted_font, "Helvetica")
        self.assertEqual(substitution.reason, "Font not found")

    def test_font_validator_global_instance(self):
        """Test global font validator instance for tracking"""
        validator = FontValidator(self.fonts_dir)
        set_font_validator(validator)

        # Track a substitution using the global function
        _track_font_substitution("Times", "Helvetica", "Test substitution", "Hello World")

        self.assertEqual(len(validator.substitution_tracker), 1)
        substitution = validator.substitution_tracker[0]
        self.assertEqual(substitution.original_font, "Times")

    def test_font_validation_report_generation(self):
        """Test font validation report generation"""
        validator = FontValidator(self.fonts_dir)

        # Add some test data
        validator.track_font_substitution("Arial", "Helvetica", "Test", "Hello")

        report = validator.get_font_validation_report()

        self.assertIn("fonts_directory", report)
        self.assertIn("available_fonts_count", report)
        self.assertIn("substitutions_tracked", report)
        self.assertIn("substitutions", report)
        self.assertEqual(len(report["substitutions"]), 1)

    @patch("pdfrebuilder.engine.validation_report.ValidationReport")
    def test_validation_report_with_font_data(self, mock_validation_report):
        """Test validation report generation with font validation data"""
        # Create mock validation result
        mock_result = Mock()
        mock_result.timestamp = "2024-01-01T00:00:00"

        # Create font validation data
        font_validation_data = {
            "fonts_required": ["Arial", "Times"],
            "fonts_available": ["Arial"],
            "fonts_missing": ["Times"],
            "fonts_substituted": [
                {
                    "original_font": "Times",
                    "substituted_font": "Helvetica",
                    "reason": "Font not found",
                }
            ],
            "validation_passed": False,
            "validation_messages": ["Font validation failed"],
        }

        # Generate report with font validation data
        with patch("os.makedirs"):
            _ = generate_validation_report(
                original_path="test_original.pdf",
                generated_path="test_generated.pdf",
                validation_result=mock_result,
                output_dir=self.temp_dir,
                report_formats=["json"],
                font_validation_result=font_validation_data,
            )

        # Verify that ValidationReport was called with font validation in metadata
        mock_validation_report.assert_called_once()
        call_args = mock_validation_report.call_args
        metadata = call_args[1]["metadata"]

        self.assertIn("font_validation", metadata)
        self.assertEqual(metadata["font_validation"], font_validation_data)

    def test_font_validation_html_report_generation(self):
        """Test HTML report generation with font validation data"""
        from pdfrebuilder.engine.validation_report import ValidationReport

        # Create validation report with font validation data
        font_validation_data = {
            "fonts_required": ["Arial", "Times"],
            "fonts_available": ["Arial"],
            "fonts_missing": ["Times"],
            "fonts_substituted": [
                {
                    "original_font": "Times",
                    "substituted_font": "Helvetica",
                    "reason": "Font not found",
                    "element_id": "text_0",
                    "page_number": 0,
                }
            ],
            "font_coverage_issues": [
                {
                    "font_name": "Arial",
                    "element_id": "text_1",
                    "missing_characters": ["ñ"],
                    "severity": "medium",
                }
            ],
            "validation_passed": False,
            "validation_messages": ["Font validation failed due to missing fonts"],
        }

        mock_result = Mock()
        mock_result.passed = True
        mock_result.ssim_score = 0.95
        mock_result.threshold = 0.9
        mock_result.original_path = "test.pdf"
        mock_result.generated_path = "test_gen.pdf"
        mock_result.diff_image_path = None
        mock_result.details = {}
        mock_result.failure_analysis = {}
        mock_result.additional_metrics = {}
        mock_result.timestamp = "2024-01-01T00:00:00"

        report = ValidationReport(
            document_name="test_document",
            results=[mock_result],
            metadata={"font_validation": font_validation_data},
        )

        # Generate HTML report
        html_path = os.path.join(self.temp_dir, "test_report.html")
        report.generate_html_report(html_path)

        # Verify HTML file was created
        self.assertTrue(os.path.exists(html_path))

        # Read and verify HTML content contains font validation information
        with open(html_path, encoding="utf-8") as f:
            html_content = f.read()

        self.assertIn("Font Validation", html_content)
        self.assertIn("Font Substitutions", html_content)
        self.assertIn("Times", html_content)  # Original font
        self.assertIn("Helvetica", html_content)  # Substituted font
        self.assertIn("Font Coverage Issues", html_content)

    def test_font_validation_error_handling(self):
        """Test font validation error handling"""
        validator = FontValidator("/nonexistent/path")

        # Should handle missing fonts directory gracefully
        result = validator.validate_document_fonts(self.sample_layout_config)

        # Should still return a result object
        self.assertIsInstance(result, FontValidationResult)

        # Should have validation messages about errors
        self.assertGreater(len(result.validation_messages), 0)

    def test_font_validation_with_empty_config(self):
        """Test font validation with empty configuration"""
        validator = FontValidator(self.fonts_dir)

        empty_config = {"version": "1.0", "document_structure": []}

        result = validator.validate_document_fonts(empty_config)

        self.assertEqual(len(result.fonts_required), 0)
        self.assertEqual(len(result.fonts_missing), 0)
        self.assertTrue(result.validation_passed)

    def test_font_validation_messages_formatting(self):
        """Test font validation message formatting"""
        result = FontValidationResult()

        # Test different message levels
        result.add_validation_message("Info message", "info")
        result.add_validation_message("Warning message", "warning")
        result.add_validation_message("Error message", "error")

        self.assertEqual(len(result.validation_messages), 3)
        self.assertIn("[INFO]", result.validation_messages[0])
        self.assertIn("[WARNING]", result.validation_messages[1])
        self.assertIn("[ERROR]", result.validation_messages[2])

        # Error should set validation_passed to False
        self.assertFalse(result.validation_passed)


if __name__ == "__main__":
    unittest.main()
