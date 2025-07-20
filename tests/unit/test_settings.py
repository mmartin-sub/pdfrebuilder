"""
Tests for settings and configuration management.
"""

from unittest.mock import patch

from pdfrebuilder.settings import (
    CONFIG,
    STANDARD_PDF_FONTS,
    configure_logging,
    get_config_value,
    get_nested_config_value,
    set_nested_config_value,
)


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

    def test_config_structure(self):
        """Test that CONFIG has the expected structure"""
        assert isinstance(CONFIG, dict)

        # Check for main configuration sections
        expected_sections = ["engines", "font_management", "validation", "debug"]

        for section in expected_sections:
            assert section in CONFIG, f"Missing config section: {section}"

    def test_engines_config_structure(self):
        """Test that engines configuration is properly structured"""
        engines = CONFIG["engines"]

        assert "input" in engines
        assert "output" in engines

        # Check input engines
        input_engines = engines["input"]
        assert "default" in input_engines
        assert "wand" in input_engines
        assert "psd_tools" in input_engines
        assert "fitz" in input_engines

        # Check output engines
        output_engines = engines["output"]
        assert "default" in output_engines
        assert "reportlab" in output_engines
        assert "pymupdf" in output_engines

    def test_font_management_config_structure(self):
        """Test that font management configuration is properly structured"""
        font_config = CONFIG["font_management"]

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
            assert key in font_config, f"Missing font config key: {key}"

    def test_validation_config_structure(self):
        """Test that validation configuration is properly structured"""
        validation_config = CONFIG["validation"]

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
            assert key in validation_config, f"Missing validation config key: {key}"

    def test_get_config_value_existing_key(self):
        """Test getting existing configuration values"""
        # Test direct key access
        fonts_dir = get_config_value("fonts_dir")
        assert fonts_dir is not None

        # Test existing key
        default_font = get_config_value("default_font")
        assert default_font is not None

    def test_get_config_value_nonexistent_key(self):
        """Test getting non-existent configuration values"""
        # Without default - should return None
        result = get_config_value("nonexistent_key")
        assert result is None

    def test_get_nested_config_value_existing_path(self):
        """Test getting existing nested configuration values"""
        # Test engine configuration
        wand_density = get_nested_config_value("engines.input.wand.density")
        assert wand_density == 300

        # Test validation configuration
        ssim_threshold = get_nested_config_value("validation.ssim_threshold")
        assert ssim_threshold == 0.98

    def test_get_nested_config_value_nonexistent_path(self):
        """Test getting non-existent nested configuration values"""
        # Without default
        result = get_nested_config_value("nonexistent.path.here")
        assert result is None

        # With default
        result = get_nested_config_value("nonexistent.path.here", "default")
        assert result == "default"

    def test_set_nested_config_value(self):
        """Test setting nested configuration values"""
        # Set a new value
        original_value = get_nested_config_value("engines.input.wand.density")
        new_value = 600

        set_nested_config_value("engines.input.wand.density", new_value)

        # Verify it was set
        result = get_nested_config_value("engines.input.wand.density")
        assert result == new_value

        # Reset to original value
        set_nested_config_value("engines.input.wand.density", original_value)

    def test_set_nested_config_value_new_path(self):
        """Test setting nested configuration values for new paths"""
        # Set a value in a new nested path
        set_nested_config_value("test.new.path", "test_value")

        # Verify it was set
        result = get_nested_config_value("test.new.path")
        assert result == "test_value"

        # Clean up
        if "test" in CONFIG:
            del CONFIG["test"]

    @patch("src.settings.logging.basicConfig")
    @patch("src.settings.logging.FileHandler")
    def test_configure_logging_with_file(self, mock_file_handler, mock_basic_config):
        """Test logging configuration with file output"""
        log_file = "/tmp/test.log"
        log_level = "DEBUG"
        log_format = "%(message)s"

        configure_logging(log_file=log_file, log_level=log_level, log_format=log_format)

        # Verify file handler was created (with encoding parameter)
        mock_file_handler.assert_called_once_with(log_file, encoding="utf-8")

        # Verify basic config was called
        mock_basic_config.assert_called_once()

    @patch("src.settings.logging.basicConfig")
    def test_configure_logging_console_only(self, mock_basic_config):
        """Test logging configuration for console only"""
        log_level = "INFO"
        log_format = "%(levelname)s: %(message)s"

        configure_logging(log_level=log_level, log_format=log_format)

        # Verify basic config was called
        mock_basic_config.assert_called_once()

    def test_config_value_types(self):
        """Test that configuration values have expected types"""
        # Test boolean values
        enable_google_fonts = get_nested_config_value("font_management.enable_google_fonts")
        assert isinstance(enable_google_fonts, bool)

        # Test numeric values
        wand_density = get_nested_config_value("engines.input.wand.density")
        assert isinstance(wand_density, int | float)

        # Test string values
        default_font = get_nested_config_value("font_management.default_font")
        assert isinstance(default_font, str)

    def test_config_immutability_protection(self):
        """Test that critical config values are protected"""
        # Store original value
        original_value = get_nested_config_value("validation.ssim_threshold")

        # Modify the value
        set_nested_config_value("validation.ssim_threshold", 0.5)

        # Verify it was changed
        modified_value = get_nested_config_value("validation.ssim_threshold")
        assert modified_value == 0.5

        # Reset to original
        set_nested_config_value("validation.ssim_threshold", original_value)

        # Verify it was reset
        reset_value = get_nested_config_value("validation.ssim_threshold")
        assert reset_value == original_value

    def test_legacy_config_keys_mapping(self):
        """Test that legacy configuration keys are properly mapped"""
        # Test legacy keys that should still work
        legacy_mappings = {
            "fonts_dir": "font_management.font_directory",
            "default_font": "font_management.default_font",
            "visual_diff_threshold": "validation.visual_diff_threshold",
        }

        for legacy_key, nested_path in legacy_mappings.items():
            legacy_value = get_config_value(legacy_key)
            nested_value = get_nested_config_value(nested_path)

            # They should have the same value
            assert legacy_value == nested_value, f"Legacy key {legacy_key} doesn't match {nested_path}"
