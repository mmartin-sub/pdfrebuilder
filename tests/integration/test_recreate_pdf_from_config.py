"""
Tests for PDF recreation from configuration functionality.

This module tests the recreate_pdf_from_config.py functionality including:
- PDF generation from JSON configuration
- Error handling for invalid configurations
- File I/O operations
- Integration with PDF engines
"""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.core.recreate_pdf_from_config import recreate_pdf_from_config


class TestRecreatePDFFromConfig(unittest.TestCase):
    """Test cases for PDF recreation from configuration"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        self.output_path = os.path.join(self.temp_dir, "output.pdf")

        # Sample configuration
        self.sample_config = {
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
                            "layer_name": "page_0_base_layer",
                            "bbox": [0, 0, 612, 792],
                            "layer_type": "base",
                            "content": [
                                {
                                    "id": "text_element_1",
                                    "type": "text",
                                    "text": "Hello World",
                                    "bbox": [100, 100, 200, 120],
                                    "font_details": {
                                        "name": "Helvetica",
                                        "size": 12,
                                        "color": 0
                                    }
                                }
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

    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_successful_pdf_generation(self, mock_get_engine):
        """Test successful PDF generation from valid configuration"""
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        mock_engine = Mock()
        mock_engine.engine_name = 'fitz'
        mock_get_engine.return_value = mock_engine

        recreate_pdf_from_config(self.config_path, self.output_path)

        mock_get_engine.assert_called_once()
        mock_engine.render.assert_called_once()

    def test_config_file_not_found(self):
        """Test error handling when configuration file doesn't exist"""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.json")

        with self.assertRaises(FileNotFoundError):
            recreate_pdf_from_config(non_existent_path, self.output_path)

    def test_invalid_json_config(self):
        """Test error handling for invalid JSON configuration"""
        with open(self.config_path, "w") as f:
            f.write("{ invalid json content")

        with self.assertRaises(json.JSONDecodeError):
            recreate_pdf_from_config(self.config_path, self.output_path)

    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_engine_generation_error(self, mock_get_engine):
        """Test error handling when PDF engine fails to generate"""
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        mock_engine = Mock()
        mock_engine.render.side_effect = Exception("Engine generation failed")
        mock_get_engine.return_value = mock_engine

        with self.assertRaises(Exception) as context:
            recreate_pdf_from_config(self.config_path, self.output_path)

        self.assertIn("Engine generation failed", str(context.exception))

    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_empty_config_file(self, mock_get_engine):
        """Test handling of empty configuration file"""
        with open(self.config_path, "w") as f:
            json.dump({}, f)

        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine

        recreate_pdf_from_config(self.config_path, self.output_path)

        mock_engine.render.assert_called_once()

    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_complex_config_structure(self, mock_get_engine):
        """Test handling of complex configuration structure"""
        # Using self.sample_config as a complex enough example
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine

        recreate_pdf_from_config(self.config_path, self.output_path)

        mock_engine.render.assert_called_once()

    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_unicode_content_handling(self, mock_get_engine):
        """Test handling of Unicode content in configuration"""
        unicode_config = self.sample_config.copy()
        unicode_config["metadata"]["title"] = "Unicode Test Document 测试文档"
        unicode_config["document_structure"][0]["layers"][0]["content"][0]["text"] = "Hello 世界 🌍"

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(unicode_config, f, ensure_ascii=False)

        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine

        recreate_pdf_from_config(self.config_path, self.output_path)

        mock_engine.render.assert_called_once()

    @patch("pdfrebuilder.core.recreate_pdf_from_config.logger")
    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_logging_on_success(self, mock_get_engine, mock_logger):
        """Test that success is logged appropriately"""
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        mock_engine = Mock()
        mock_engine.engine_name = 'fitz'
        mock_get_engine.return_value = mock_engine

        recreate_pdf_from_config(self.config_path, self.output_path)

        mock_logger.info.assert_any_call(f"Successfully generated PDF: {self.output_path}")

    @patch("pdfrebuilder.core.recreate_pdf_from_config.logger")
    @patch("pdfrebuilder.core.recreate_pdf_from_config.get_default_pdf_engine")
    def test_logging_on_error(self, mock_get_engine, mock_logger):
        """Test that errors are logged appropriately"""
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        mock_engine = Mock()
        mock_engine.render.side_effect = Exception("Test error")
        mock_get_engine.return_value = mock_engine

        with self.assertRaises(Exception):
            recreate_pdf_from_config(self.config_path, self.output_path)

        mock_logger.error.assert_called_with(f"Failed to generate PDF from config {self.config_path}: Test error")

    def test_file_permissions_error(self):
        """Test handling of file permission errors"""
        with open(self.config_path, "w") as f:
            json.dump(self.sample_config, f)

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(PermissionError):
                recreate_pdf_from_config(self.config_path, self.output_path)


if __name__ == "__main__":
    unittest.main()
