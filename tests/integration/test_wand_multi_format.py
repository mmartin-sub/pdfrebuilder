"""
Tests for Wand multi-format support (tasks 6.1 and 6.2).

This module tests the JPEG/PNG/GIF support and TIFF multi-page handling.
"""

import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.engine.extract_wand_content import (
    _create_single_image_structure,
    _detect_image_format,
    _extract_single_image_content,
    _is_multi_page_tiff,
)


class TestWandMultiFormat(unittest.TestCase):
    """Test cases for Wand multi-format support."""

    def test_detect_image_format(self):
        """Test image format detection."""
        # Test common formats
        self.assertEqual(_detect_image_format("test.jpg"), "jpeg")
        self.assertEqual(_detect_image_format("test.jpeg"), "jpeg")
        self.assertEqual(_detect_image_format("test.png"), "png")
        self.assertEqual(_detect_image_format("test.gif"), "gif")
        self.assertEqual(_detect_image_format("test.tiff"), "tiff")
        self.assertEqual(_detect_image_format("test.tif"), "tiff")
        self.assertEqual(_detect_image_format("test.bmp"), "bmp")
        self.assertEqual(_detect_image_format("test.psd"), "psd")

        # Test case insensitive
        self.assertEqual(_detect_image_format("TEST.PNG"), "png")
        self.assertEqual(_detect_image_format("TEST.JPEG"), "jpeg")

        # Test unknown format
        self.assertEqual(_detect_image_format("test.xyz"), "xyz")
        self.assertEqual(_detect_image_format("test"), "unknown")

    def test_single_image_structure_creation(self):
        """Test creation of single image structure for simple formats."""
        # Mock Wand Image object
        mock_img = Mock()
        mock_img.size = (800, 600)

        extraction_flags = {
            "include_images": True,
            "include_text": False,
            "include_drawings_non_background": False,
        }

        # Test PNG structure creation
        with patch("src.engine.extract_wand_content._extract_single_image_content") as mock_extract:
            mock_extract.return_value = {
                "type": "image",
                "id": "png_image_test",
                "bbox": [0, 0, 800, 600],
                "image_file": "test.png",
            }

            layers = _create_single_image_structure(mock_img, 800, 600, extraction_flags, "png")

            self.assertEqual(len(layers), 1)
            layer = layers[0]
            self.assertEqual(layer.layer_name, "PNG Image")
            self.assertEqual(layer.layer_id, "png_base_layer")
            self.assertEqual(len(layer.content), 1)
            self.assertEqual(layer.content[0]["type"], "image")

    def test_single_image_structure_no_images(self):
        """Test single image structure when images are disabled."""
        mock_img = Mock()
        mock_img.size = (800, 600)

        extraction_flags = {
            "include_images": False,
            "include_text": False,
            "include_drawings_non_background": False,
        }

        layers = _create_single_image_structure(mock_img, 800, 600, extraction_flags, "jpeg")

        self.assertEqual(len(layers), 1)
        layer = layers[0]
        self.assertEqual(layer.layer_name, "JPEG Image")
        self.assertEqual(len(layer.content), 0)  # No content when images disabled

    @patch("src.engine.extract_wand_content.get_wand_config")
    @patch("src.settings.get_config_value")
    @patch("os.makedirs")
    def test_extract_single_image_content(self, _mock_makedirs, mock_get_config_value, mock_get_wand_config):
        """Test extraction of single image content."""
        # Setup mocks
        mock_get_wand_config.return_value = {
            "image_format": "png",
            "density": 300,
            "enhance_images": False,
            "color_management": True,
        }
        mock_get_config_value.return_value = "/tmp/images"

        # Mock Wand Image object
        mock_img = Mock()
        mock_clone = Mock()
        mock_img.clone.return_value.__enter__ = Mock(return_value=mock_clone)
        mock_img.clone.return_value.__exit__ = Mock(return_value=None)

        mock_clone.size = (800, 600)
        mock_clone.alpha_channel = True
        mock_clone.colorspace = "srgb"

        # Mock the enhancement functions
        with (
            patch("src.engine.extract_wand_content._apply_image_enhancements"),
            patch("src.engine.extract_wand_content._apply_color_profile_management"),
            patch("src.engine.extract_wand_content._optimize_image_for_output"),
            patch("src.engine.extract_wand_content._record_image_metadata") as mock_record,
        ):
            mock_record.return_value = {"test": "metadata"}

            result = _extract_single_image_content(mock_img, "png", [0, 0, 800, 600])

            self.assertIsNotNone(result)
            self.assertEqual(result["type"], "image")
            self.assertEqual(result["bbox"], [0, 0, 800, 600])
            self.assertEqual(result["original_format"], "PNG")
            self.assertEqual(result["has_transparency"], True)
            self.assertEqual(result["color_space"], "SRGB")

    def test_is_multi_page_tiff_detection(self):
        """Test multi-page TIFF detection."""
        # Mock single-page TIFF
        mock_single_img = Mock()
        mock_single_img.iterator_reset = Mock()
        mock_single_img.iterator_next = Mock(side_effect=[True, False])  # One page then end

        self.assertFalse(_is_multi_page_tiff(mock_single_img))

        # Mock multi-page TIFF
        mock_multi_img = Mock()
        mock_multi_img.iterator_reset = Mock()
        mock_multi_img.iterator_next = Mock(side_effect=[True, True, False])  # Two pages then end

        self.assertTrue(_is_multi_page_tiff(mock_multi_img))

        # Mock image without iterator support
        mock_no_iter_img = Mock()
        del mock_no_iter_img.iterator_reset  # Remove iterator methods

        self.assertFalse(_is_multi_page_tiff(mock_no_iter_img))


class TestWandMultiFormatIntegration(unittest.TestCase):
    """Integration tests for multi-format support."""

    def test_format_specific_canvas_names(self):
        """Test that different formats get appropriate canvas names."""
        from pdfrebuilder.engine.extract_wand_content import _create_canvas_structure

        # Mock image
        mock_img = Mock()
        mock_img.size = (800, 600)

        extraction_flags = {"include_images": True}

        # Test different formats
        formats_and_names = [
            ("png", "Extracted PNG"),
            ("jpeg", "Extracted JPEG"),
            ("gif", "Extracted GIF"),
            ("psd", "Extracted PSD"),
            ("unknown", "Extracted Canvas"),
        ]

        for file_format, expected_name in formats_and_names:
            with (
                patch("src.engine.extract_wand_content._create_single_image_structure") as mock_create_single,
                patch("src.engine.extract_wand_content._extract_layers_from_image") as mock_extract_layers,
            ):
                # Mock return values
                mock_layer = Mock()
                mock_layer.layer_name = f"Test {file_format}"

                if file_format.lower() in ["png", "jpeg", "gif", "bmp"]:
                    mock_create_single.return_value = [mock_layer]
                    mock_extract_layers.return_value = []
                else:
                    mock_create_single.return_value = []
                    mock_extract_layers.return_value = [mock_layer]

                canvas = _create_canvas_structure(mock_img, extraction_flags, file_format)

                self.assertEqual(canvas.canvas_name, expected_name)

    def test_extraction_flags_respected(self):
        """Test that extraction flags are properly respected for different formats."""
        from pdfrebuilder.engine.extract_wand_content import _create_single_image_structure

        mock_img = Mock()
        mock_img.size = (800, 600)

        # Test with images disabled
        extraction_flags = {"include_images": False}

        with patch("src.engine.extract_wand_content._extract_single_image_content") as mock_extract:
            layers = _create_single_image_structure(mock_img, 800, 600, extraction_flags, "png")

            # Should not call image extraction when images are disabled
            mock_extract.assert_not_called()

            # Should still create layer structure
            self.assertEqual(len(layers), 1)
            self.assertEqual(len(layers[0].content), 0)


if __name__ == "__main__":
    unittest.main()
