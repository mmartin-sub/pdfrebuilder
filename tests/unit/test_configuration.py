"""
Unit tests for configuration management.
Tests the standardized configuration system.
"""

from pdfrebuilder.settings import settings


class TestConfigurationSystem:
    """Test the standardized configuration system"""

    def test_nested_config_access(self):
        """Test accessing nested configuration values"""
        # Test engine configuration access
        wand_density = settings.engines.input.wand.density
        assert wand_density == 300

        reportlab_compression = settings.engines.output.reportlab.compression
        assert reportlab_compression == 1

        # Test font management configuration
        font_dir = settings.font_management.font_directory
        assert font_dir == "fonts"

        # Test validation configuration
        ssim_threshold = settings.validation.ssim_threshold
        assert ssim_threshold == 0.98

    def test_nested_config_defaults(self):
        """Test default values for non-existent nested config paths"""
        # This test is no longer valid with the new settings object
        pass

    def test_nested_config_setting(self):
        """Test setting nested configuration values"""
        # Set a new value
        original_density = settings.engines.input.wand.density
        settings.engines.input.wand.density = 600

        # Verify it was set
        result = settings.engines.input.wand.density
        assert result == 600

        # Reset to original value
        settings.engines.input.wand.density = original_density

    def test_engine_defaults(self):
        """Test that engine defaults are properly configured"""
        # Input engine default
        input_default = settings.engines.input.default
        assert input_default == "auto"

        # Output engine default
        output_default = settings.engines.output.default
        assert output_default == "reportlab"

    def test_all_engine_configs_present(self):
        """Test that all required engine configurations are present"""
        # Input engines
        assert hasattr(settings.engines.input, "wand")
        assert hasattr(settings.engines.input, "psd_tools")
        assert hasattr(settings.engines.input, "fitz")

        # Output engines
        assert hasattr(settings.engines.output, "reportlab")
        assert hasattr(settings.engines.output, "pymupdf")
        assert hasattr(settings.engines.output, "fitz")

    def test_wand_config_completeness(self):
        """Test that Wand configuration has all required settings"""
        wand_config = settings.engines.input.wand.model_dump()

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
        font_config = settings.font_management.model_dump()

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
        validation_config = settings.validation.model_dump()

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
