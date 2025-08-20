"""
Unit tests for configuration management.
Tests the standardized configuration system.
"""

from pdfrebuilder.settings import CONFIG, get_config_value, get_nested_config_value, set_nested_config_value


class TestConfigurationSystem:
    """Test the standardized configuration system"""

    def test_nested_config_access(self):
        """Test accessing nested configuration values"""
        # Test engine configuration access
        wand_density = get_nested_config_value("engines.input.wand.density")
        assert wand_density == 300

        reportlab_compression = get_nested_config_value("engines.output.reportlab.compression")
        assert reportlab_compression == 1

        # Test font management configuration
        font_dir = get_nested_config_value("font_management.font_directory")
        assert font_dir == "fonts"

        # Test validation configuration
        ssim_threshold = get_nested_config_value("validation.ssim_threshold")
        assert ssim_threshold == 0.98

    def test_nested_config_defaults(self):
        """Test default values for non-existent nested config paths"""
        # Non-existent path should return default
        result = get_nested_config_value("nonexistent.path.here", default="default_value")
        assert result == "default_value"

        # Non-existent path without default should return None
        result = get_nested_config_value("nonexistent.path.here")
        assert result is None

    def test_nested_config_setting(self):
        """Test setting nested configuration values"""
        # Set a new value
        set_nested_config_value("engines.input.wand.density", 600)

        # Verify it was set
        result = get_nested_config_value("engines.input.wand.density")
        assert result == 600

        # Reset to original value
        set_nested_config_value("engines.input.wand.density", 300)

    def test_legacy_config_compatibility(self):
        """Test that legacy configuration keys still work"""
        # Legacy keys should still be accessible
        fonts_dir = get_config_value("fonts_dir")
        assert fonts_dir == "fonts"

        default_font = get_config_value("default_font")
        assert default_font == "Noto Sans"

        visual_diff_threshold = get_config_value("visual_diff_threshold")
        assert visual_diff_threshold == 5

    def test_engine_defaults(self):
        """Test that engine defaults are properly configured"""
        # Input engine default
        input_default = get_nested_config_value("engines.input.default")
        assert input_default == "auto"

        # Output engine default
        output_default = get_nested_config_value("engines.output.default")
        assert output_default == "reportlab"

    def test_all_engine_configs_present(self):
        """Test that all required engine configurations are present"""
        # Input engines
        assert "wand" in CONFIG["engines"]["input"]
        assert "psd_tools" in CONFIG["engines"]["input"]
        assert "fitz" in CONFIG["engines"]["input"]

        # Output engines
        assert "reportlab" in CONFIG["engines"]["output"]
        assert "pymupdf" in CONFIG["engines"]["output"]
        assert "fitz" in CONFIG["engines"]["output"]

    def test_wand_config_completeness(self):
        """Test that Wand configuration has all required settings"""
        wand_config = get_nested_config_value("engines.input.wand")

        required_keys = [
            "density",
            "use_ocr",
            "tesseract_lang",
            "image_format",
            "color_management",
            "memory_limit_mb",
        ]

        for key in required_keys:
            assert key in wand_config, f"Missing required Wand config key: {key}"

    def test_font_management_config_completeness(self):
        """Test that font management configuration has all required settings"""
        font_config = get_nested_config_value("font_management")

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
            assert key in font_config, f"Missing required font management config key: {key}"

    def test_validation_config_completeness(self):
        """Test that validation configuration has all required settings"""
        validation_config = get_nested_config_value("validation")

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
            assert key in validation_config, f"Missing required validation config key: {key}"
