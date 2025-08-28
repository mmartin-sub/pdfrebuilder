"""
Tests for settings and configuration management.
"""

import logging
from unittest.mock import patch

from pdfrebuilder.settings import STANDARD_PDF_FONTS, configure_logging, settings


class TestSettings:
    """Test settings and configuration functionality"""

    def test_standard_pdf_fonts_defined(self):
        """Test that standard PDF fonts are properly defined"""
        assert isinstance(STANDARD_PDF_FONTS, list)
        assert len(STANDARD_PDF_FONTS) > 0

        # Check for common standard fonts
        expected_fonts = ["helv", "cour", "Helvetica"]
        for font in expected_fonts:
            assert font in STANDARD_PDF_FONTS

    def test_settings_structure(self):
        """Test that settings has the expected structure"""
        # Check for main configuration sections
        expected_sections = ["engines", "font_management", "validation", "debug"]

        for section in expected_sections:
            assert hasattr(settings, section), f"Missing settings section: {section}"

    def test_engines_config_structure(self):
        """Test that engines configuration is properly structured"""
        engines = settings.engines

        assert hasattr(engines, "input")
        assert hasattr(engines, "output")

        # Check input engines
        input_engines = engines.input
        assert hasattr(input_engines, "default")
        assert hasattr(input_engines, "wand")
        assert hasattr(input_engines, "psd_tools")
        assert hasattr(input_engines, "fitz")

        # Check output engines
        output_engines = engines.output
        assert hasattr(output_engines, "default")
        assert hasattr(output_engines, "reportlab")
        assert hasattr(output_engines, "pymupdf")

    def test_font_management_config_structure(self):
        """Test that font management configuration is properly structured"""
        font_config = settings.font_management

        required_keys = [
            "font_directory",
            "downloaded_fonts_dir",
            "manual_fonts_dir",
            "enable_google_fonts",
            "fallback_font",
            "cache_file",
            "default_font",
        ]

        for key in required_keys:
            assert hasattr(font_config, key), f"Missing font config key: {key}"

    def test_validation_config_structure(self):
        """Test that validation configuration is properly structured"""
        validation_config = settings.validation

        required_keys = [
            "ssim_threshold",
            "rendering_dpi",
            "comparison_engine",
            "generate_diff_images",
            "fail_on_font_substitution",
            "visual_diff_threshold",
            "ssim_score_display_digits",
        ]

        for key in required_keys:
            assert hasattr(validation_config, key), f"Missing validation config key: {key}"

    def test_get_nested_config_value_existing_path(self):
        """Test getting existing nested configuration values"""
        # Test engine configuration
        wand_density = settings.engines.input.wand.density
        assert wand_density == 300

        # Test validation configuration
        ssim_threshold = settings.validation.ssim_threshold
        assert ssim_threshold == 0.98

    def test_set_nested_config_value(self):
        """Test setting nested configuration values"""
        # Set a new value
        original_value = settings.engines.input.wand.density
        new_value = 600

        settings.engines.input.wand.density = new_value

        # Verify it was set
        result = settings.engines.input.wand.density
        assert result == new_value

        # Reset to original value
        settings.engines.input.wand.density = original_value

    @patch("pdfrebuilder.settings.logging.basicConfig")
    @patch("pdfrebuilder.settings.logging.FileHandler")
    def test_configure_logging_with_file(self, mock_file_handler, mock_basic_config):
        """Test logging configuration with file output"""
        log_file = "/tmp/test.log"
        log_level = logging.DEBUG
        log_format = "%(message)s"

        configure_logging(log_file=log_file, log_level=log_level, log_format=log_format)

        # Verify file handler was created (with encoding parameter)
        mock_file_handler.assert_called_once_with(log_file, encoding="utf-8")

        # Verify basic config was called
        mock_basic_config.assert_called_once()

    @patch("pdfrebuilder.settings.logging.basicConfig")
    def test_configure_logging_console_only(self, mock_basic_config):
        """Test logging configuration for console only"""
        log_level = logging.INFO
        log_format = "%(levelname)s: %(message)s"

        configure_logging(log_level=log_level, log_format=log_format)

        # Verify basic config was called
        mock_basic_config.assert_called_once()

    def test_config_value_types(self):
        """Test that configuration values have expected types"""
        # Test boolean values
        enable_google_fonts = settings.font_management.enable_google_fonts
        assert isinstance(enable_google_fonts, bool)

        # Test numeric values
        wand_density = settings.engines.input.wand.density
        assert isinstance(wand_density, int)

        # Test string values
        default_font = settings.font_management.default_font
        assert isinstance(default_font, str)
