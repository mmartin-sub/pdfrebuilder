"""
Tests for debug PDF layer generation functionality.
"""

import os
import tempfile
from unittest.mock import Mock, patch

from pdfrebuilder.core.generate_debug_pdf_layers import (
    _get_element_info_text,
    _render_debug_element,
    generate_debug_pdf_layers,
)


class TestGenerateDebugPdfLayers:
    """Test debug PDF layer generation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        self.output_path = os.path.join(self.temp_dir, "debug_output.pdf")

        # Sample configuration with layers
        self.sample_config = {
            "version": "1.0",
            "engine": "fitz",
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": "layer_1",
                            "layer_name": "Test Layer",
                            "content": [
                                {
                                    "type": "text",
                                    "id": "text_1",
                                    "text": "Test text",
                                    "bbox": [100, 100, 200, 120],
                                    "font_details": {
                                        "name": "Tangerine",
                                        "size": 12,
                                        "color": 0,
                                    },
                                },
                                {
                                    "type": "drawing",
                                    "id": "drawing_1",
                                    "bbox": [50, 50, 150, 100],
                                    "color": [1.0, 0.0, 0.0],
                                    "fill": [0.0, 1.0, 0.0],
                                    "drawing_commands": [
                                        {"cmd": "M", "pts": [50, 50]},
                                        {"cmd": "L", "pts": [150, 100]},
                                        {"cmd": "H"},
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        }

    @patch("pdfrebuilder.core.generate_debug_pdf_layers.fitz.open")
    def test_generate_debug_pdf_layers_success(self, mock_fitz_open):
        """Test successful debug PDF generation"""
        # Mock PyMuPDF document and context manager
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.rect.width = 612
        mock_page.rect.height = 792
        mock_doc.new_page.return_value = mock_page
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        # Write config to file
        import json

        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        result = generate_debug_pdf_layers(self.config_path, self.output_path)

        assert result is True
        mock_fitz_open.assert_called_once()
        mock_doc.new_page.assert_called()
        mock_doc.save.assert_called_once_with(self.output_path, garbage=4, deflate=True)

    def test_generate_debug_pdf_layers_file_not_found(self):
        """Test error when config file doesn't exist"""
        non_existent_config = os.path.join(self.temp_dir, "nonexistent.json")

        result = generate_debug_pdf_layers(non_existent_config, self.output_path)

        assert result is False

    @patch("pdfrebuilder.core.generate_debug_pdf_layers.fitz.open")
    def test_generate_debug_pdf_layers_exception(self, mock_fitz_open):
        """Test exception handling during debug PDF generation"""
        # Mock the document but make save() raise an exception
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.rect.width = 612
        mock_page.rect.height = 792
        mock_doc.new_page.return_value = mock_page
        mock_doc.save.side_effect = Exception("Save failed")
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        # Write config to file
        import json

        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        result = generate_debug_pdf_layers(self.config_path, self.output_path)

        assert result is False

    def test_render_debug_element_text(self):
        """Test rendering debug information for text elements"""
        mock_page = Mock()

        text_element = {
            "type": "text",
            "id": "text_1",
            "text": "Test text",
            "bbox": [100, 100, 200, 120],
            "font_details": {"name": "Tangerine", "size": 12, "color": 0},
        }

        _render_debug_element(mock_page, text_element, "layer_1", 0)

        # Verify drawing operations were called
        mock_page.draw_rect.assert_called()
        mock_page.insert_text.assert_called()

    def test_render_debug_element_drawing(self):
        """Test rendering debug information for drawing elements"""
        mock_page = Mock()

        drawing_element = {
            "type": "drawing",
            "id": "drawing_1",
            "bbox": [50, 50, 150, 100],
            "color": [1.0, 0.0, 0.0],
            "fill": [0.0, 1.0, 0.0],
            "drawing_commands": [
                {"cmd": "M", "pts": [50, 50]},
                {"cmd": "L", "pts": [150, 100]},
                {"cmd": "H"},
            ],
        }

        _render_debug_element(mock_page, drawing_element, "layer_1", 0)

        # Verify drawing operations were called
        mock_page.draw_rect.assert_called()
        mock_page.insert_text.assert_called()

    def test_render_debug_element_image(self):
        """Test rendering debug information for image elements"""
        mock_page = Mock()

        image_element = {
            "type": "image",
            "id": "image_1",
            "bbox": [200, 200, 400, 300],
            "image_file": "./images/test.jpg",
        }

        _render_debug_element(mock_page, image_element, "layer_1", 0)

        # Verify drawing operations were called
        mock_page.draw_rect.assert_called()
        mock_page.insert_text.assert_called()

    def test_get_element_info_text_text_element(self):
        """Test getting info text for text elements"""
        text_element = {
            "type": "text",
            "id": "text_1",
            "text": "Test text",
            "font_details": {"name": "Tangerine", "size": 12},
        }

        info_text = _get_element_info_text(text_element, "layer_1", 0)

        assert "text_1" in info_text
        assert "Test text" in info_text
        assert "Tangerine" in info_text
        assert "12" in info_text

    def test_get_element_info_text_drawing_element(self):
        """Test getting info text for drawing elements"""
        drawing_element = {
            "type": "drawing",
            "id": "drawing_1",
            "drawing_commands": [
                {"cmd": "M", "pts": [50, 50]},
                {"cmd": "L", "pts": [150, 100]},
            ],
        }

        info_text = _get_element_info_text(drawing_element, "layer_1", 0)

        assert "drawing_1" in info_text
        assert "2 commands" in info_text

    def test_get_element_info_text_image_element(self):
        """Test getting info text for image elements"""
        image_element = {
            "type": "image",
            "id": "image_1",
            "image_file": "./images/test.jpg",
        }

        info_text = _get_element_info_text(image_element, "layer_1", 0)

        assert "image_1" in info_text
        assert "test.jpg" in info_text

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
