"""
Integration tests for the Wand input engine.

This module tests the complete workflow of the Wand engine with actual image processing.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from pdfrebuilder.engine.document_parser import WandParser


class TestWandIntegration(unittest.TestCase):
    """Integration test cases for the Wand input engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = WandParser()

    def test_wand_engine_selection(self):
        """Test that the Wand engine can be selected and initialized."""
        from pdfrebuilder.engine.document_parser import get_parser_by_engine

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            # Create a simple 1x1 pixel PNG
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13"
                b"\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```"
                b"bPPP\x00\x02\xac\xea\x05\x1b\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            temp_file.write(png_data)
            temp_path = temp_file.name

        try:
            # Mock the file format detection to return 'png'
            with patch("src.engine.document_parser.detect_file_format", return_value="png"):
                # Test that we can get the Wand parser for this file
                parser = get_parser_by_engine("wand", temp_path)
                self.assertIsInstance(parser, WandParser)

                # Test that auto-selection also works
                auto_parser = get_parser_by_engine("auto", temp_path)
                # Should get some parser (could be Wand or another that supports PNG)
                self.assertIsNotNone(auto_parser)

        finally:
            os.unlink(temp_path)

    def test_wand_config_validation(self):
        """Test that Wand configuration validation works correctly."""
        from pdfrebuilder.engine.extract_wand_content import get_wand_config, validate_wand_config

        # Get default config
        config = get_wand_config()

        # Should be valid by default
        is_valid, errors = validate_wand_config(config)
        self.assertTrue(is_valid, f"Default config should be valid, but got errors: {errors}")

        # Test invalid config
        invalid_config = config.copy()
        invalid_config["density"] = -100  # Invalid negative density

        is_valid, errors = validate_wand_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)

    def test_wand_availability_check(self):
        """Test that Wand availability check works."""
        from pdfrebuilder.engine.extract_wand_content import check_wand_availability

        is_available, info = check_wand_availability()

        # On this system, Wand should be available
        if is_available:
            self.assertIn("wand_version", info)
            self.assertIn("imagemagick_version", info)
            self.assertEqual(info["status"], "available")
        else:
            # If not available, should have error information
            self.assertIn("error", info)

    def test_engine_registration(self):
        """Test that the Wand engine is properly registered."""
        from pdfrebuilder.engine.document_parser import _PARSERS

        # Check that WandParser is in the registry
        wand_parsers = [p for p in _PARSERS if isinstance(p, WandParser)]
        self.assertEqual(len(wand_parsers), 1, "Should have exactly one WandParser registered")

    def test_cli_integration(self):
        """Test that the CLI properly recognizes the Wand engine."""
        import subprocess
        import sys

        # Test that the help shows the wand option
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )  # nosec B607

        self.assertEqual(result.returncode, 0)
        self.assertIn("wand", result.stdout.lower())
        self.assertIn("python-wand", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
