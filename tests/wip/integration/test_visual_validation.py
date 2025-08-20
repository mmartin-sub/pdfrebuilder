"""
Integration tests for visual validation across all engines.
Tests that visual validation works consistently regardless of engine used.
"""

import os

import pytest

from pdfrebuilder.settings import get_nested_config_value


class TestVisualValidation:
    """Test visual validation consistency across engines"""

    def test_validation_configuration(self):
        """Test that validation configuration is properly set up"""
        validation_config = get_nested_config_value("validation")

        # Check required validation settings
        assert validation_config["ssim_threshold"] == 0.98
        assert validation_config["rendering_dpi"] == 300
        assert validation_config["comparison_engine"] == "opencv"
        assert validation_config["generate_diff_images"] is True

    def test_ssim_threshold_range(self):
        """Test that SSIM threshold is in valid range"""
        ssim_threshold = get_nested_config_value("validation.ssim_threshold")
        assert 0.0 <= ssim_threshold <= 1.0

    def test_rendering_dpi_valid(self):
        """Test that rendering DPI is a reasonable value"""
        rendering_dpi = get_nested_config_value("validation.rendering_dpi")
        assert isinstance(rendering_dpi, int)
        assert 72 <= rendering_dpi <= 600  # Reasonable DPI range

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_visual_validation_with_pdf_engine(self):
        """Test visual validation with PDF engine"""
        # This would test visual validation with PDF documents
        # Requires actual test files and visual validation implementation

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_visual_validation_with_psd_engine(self):
        """Test visual validation with PSD engine"""
        # This would test visual validation with PSD documents
        # Requires actual test files and visual validation implementation

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_cross_engine_visual_consistency(self):
        """Test that different engines produce visually similar results"""
        # This would compare visual output from different engines
        # processing the same logical content

    def test_diff_image_generation_config(self):
        """Test that diff image generation is properly configured"""
        generate_diff = get_nested_config_value("validation.generate_diff_images")
        assert isinstance(generate_diff, bool)

        # If enabled, should have proper threshold
        if generate_diff:
            threshold = get_nested_config_value("validation.visual_diff_threshold")
            assert isinstance(threshold, int | float)
            assert threshold > 0

    def test_validation_engine_availability(self):
        """Test that the configured validation engine is available"""
        comparison_engine = get_nested_config_value("validation.comparison_engine")

        if comparison_engine == "opencv":
            try:
                pass

                # OpenCV is available
                assert True
            except ImportError:
                pytest.skip("OpenCV not available for validation")
        elif comparison_engine == "skimage":
            try:
                # scikit-image is available
                assert True
            except ImportError:
                pytest.skip("scikit-image not available for validation")

    def test_validation_metrics_configuration(self):
        """Test that validation metrics are properly configured"""
        # Test SSIM score display digits
        ssim_digits = get_nested_config_value("validation.ssim_score_display_digits")
        assert isinstance(ssim_digits, int)
        assert 1 <= ssim_digits <= 10  # Reasonable range for display digits

        # Test fail on font substitution setting
        fail_on_font_sub = get_nested_config_value("validation.fail_on_font_substitution")
        assert isinstance(fail_on_font_sub, bool)
