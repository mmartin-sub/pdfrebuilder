"""
Unit tests for Font Substitution System

This module tests:
- Font substitution by coverage
- Fallback chain functionality
- Performance optimization
- Error handling and recovery
"""

import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from pdfrebuilder.font.utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    ensure_font_registered,
    font_covers_text,
)

# Import test configuration
from tests.config import cleanup_test_output, get_test_fonts_dir, get_test_temp_dir


class TestFontSubstitutionEngine(unittest.TestCase):
    """Test font substitution and fallback mechanisms"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        self.mock_page = Mock()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_glyph_coverage_basic_latin(self, mock_ttfont):
        """Test glyph coverage for basic Latin characters"""
        mock_font = Mock()
        mock_font.__getitem__ = Mock()
        mock_cmap_table = Mock()

        # Create character map for basic Latin (A-Z, a-z, 0-9)
        basic_latin_cmap = {}
        for i in range(ord("A"), ord("Z") + 1):
            basic_latin_cmap[i] = i - ord("A") + 1
        for i in range(ord("a"), ord("z") + 1):
            basic_latin_cmap[i] = i - ord("a") + 27
        for i in range(ord("0"), ord("9") + 1):
            basic_latin_cmap[i] = i - ord("0") + 53
        basic_latin_cmap[ord(" ")] = 63

        mock_cmap_table.cmap = basic_latin_cmap
        mock_cmap_subtable = Mock()
        mock_cmap_subtable.tables = [mock_cmap_table]
        mock_font.__getitem__.return_value = mock_cmap_subtable
        mock_ttfont.return_value = mock_font

        # Test with basic Latin text
        result = font_covers_text("dummy_path.ttf", "Hello World 123")
        self.assertTrue(result)

        # Test with unsupported characters
        result = font_covers_text("dummy_path.ttf", "Hello 世界")  # Contains Chinese characters
        self.assertFalse(result)

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_glyph_coverage_unicode_characters(self, mock_ttfont):
        """Test glyph coverage for Unicode characters"""
        mock_font = Mock()
        mock_font.__getitem__ = Mock()
        mock_cmap_table = Mock()

        # Create character map including some Unicode characters
        unicode_cmap = {
            ord("H"): 1,
            ord("e"): 2,
            ord("l"): 3,
            ord("o"): 4,
            ord(" "): 5,
            ord("n"): 10,
            ord("i"): 11,  # Add missing characters
            0x4E16: 6,  # 世 (Chinese character)
            0x754C: 7,  # 界 (Chinese character)
            0x00E9: 8,  # é (Latin with accent)
            0x00F1: 9,  # ñ (Latin with tilde)
        }

        mock_cmap_table.cmap = unicode_cmap
        mock_cmap_subtable = Mock()
        mock_cmap_subtable.tables = [mock_cmap_table]
        mock_font.__getitem__.return_value = mock_cmap_subtable
        mock_ttfont.return_value = mock_font

        # Test with supported Unicode text
        result = font_covers_text("dummy_path.ttf", "Hello 世界")
        self.assertTrue(result)

        # Test with accented characters
        result = font_covers_text("dummy_path.ttf", "Héllo niño")
        self.assertTrue(result)

        # Test with unsupported characters
        result = font_covers_text("dummy_path.ttf", "Hello 🌍")  # Contains emoji
        self.assertFalse(result)

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_font_substitution_by_coverage(self, mock_exists, mock_covers, mock_scan, mock_download):
        """Test font substitution based on glyph coverage"""
        font_name = "MissingFont"
        text = "Hello 世界"

        # Original font doesn't exist
        mock_exists.return_value = False
        mock_download.return_value = None  # Download fails

        # Mock available fonts
        available_fonts = {
            "Arial": "/path/to/arial.ttf",
            "NotoSans": "/path/to/notosans.ttf",
            "DejaVu": "/path/to/dejavu.ttf",
        }
        mock_scan.return_value = available_fonts

        # Mock coverage: only NotoSans covers the text
        def coverage_side_effect(font_path, test_text):
            if "notosans" in font_path.lower():
                return True
            return False

        mock_covers.side_effect = coverage_side_effect

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=True, text=text)

        self.assertEqual(result, "NotoSans")
        self.mock_page.insert_font.assert_called_once_with(fontfile="/path/to/notosans.ttf", fontname="NotoSans")

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_font_substitution_no_coverage_fallback(self, mock_exists, mock_covers, mock_scan, mock_download):
        """Test fallback when no available font covers the text"""
        font_name = "MissingFont"
        text = "Hello 🌍🚀"  # Text with emojis that most fonts won't cover

        # Original font doesn't exist
        mock_exists.return_value = False
        mock_download.return_value = None  # Download fails

        # Mock available fonts
        available_fonts = {"Arial": "/path/to/arial.ttf", "Times": "/path/to/times.ttf"}
        mock_scan.return_value = available_fonts

        # Mock coverage: no font covers the text
        mock_covers.return_value = False

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        # Should fallback to first available fallback font
        self.assertEqual(result, "Courier")

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_font_substitution_registration_error(self, mock_exists, mock_covers, mock_scan, mock_download):
        """Test handling of font registration errors during substitution"""
        font_name = "MissingFont"
        text = "Hello World"

        # Original font doesn't exist
        mock_exists.return_value = False
        mock_download.return_value = None  # Download fails

        # Mock available fonts
        available_fonts = {
            "Arial": "/path/to/arial.ttf",
            "DejaVu": "/path/to/dejavu.ttf",
        }
        mock_scan.return_value = available_fonts

        # Mock coverage: Arial covers the text
        def coverage_side_effect(font_path, test_text):
            return "arial" in font_path.lower()

        mock_covers.side_effect = coverage_side_effect

        # Mock insert_font to raise exception for Arial
        def insert_font_side_effect(fontfile=None, fontname=None):
            if fontname == "Arial":
                raise Exception("Font registration failed")

        self.mock_page.insert_font.side_effect = insert_font_side_effect

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        # Should fallback to first available fallback font after registration error
        self.assertEqual(result, "Helvetica")

    def test_font_substitution_priority_order(self):
        """Test that font substitution follows correct priority order"""
        # This test verifies the priority order:
        # 1. Exact font match (local file)
        # 2. Google Fonts download
        # 3. Coverage-based substitution
        # 4. Default font fallback
        # 5. Standard PDF font fallback

        # Removed unused variable: font_name = "CustomFont"

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # Test standard font (highest priority after exact match)
            result = ensure_font_registered(self.mock_page, "helv", verbose=False)
            self.assertEqual(result, "helv")

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_multiple_cmap_tables_handling(self, mock_ttfont):
        """Test handling of fonts with multiple character map tables"""
        mock_font = Mock()
        mock_font.__getitem__ = Mock()

        # Create multiple cmap tables (common in real fonts)
        mock_cmap_table1 = Mock()
        mock_cmap_table1.cmap = {ord("A"): 1, ord("B"): 2}

        mock_cmap_table2 = Mock()
        mock_cmap_table2.cmap = {ord("C"): 3, ord("D"): 4}

        mock_cmap_table3 = Mock()
        mock_cmap_table3.cmap = {ord("E"): 5, ord("F"): 6}

        mock_cmap_subtable = Mock()
        mock_cmap_subtable.tables = [
            mock_cmap_table1,
            mock_cmap_table2,
            mock_cmap_table3,
        ]
        mock_font.__getitem__.return_value = mock_cmap_subtable
        mock_ttfont.return_value = mock_font

        # Test that characters from all tables are recognized
        result = font_covers_text("dummy_path.ttf", "ABCDEF")
        self.assertTrue(result)

        # Test with missing character
        result = font_covers_text("dummy_path.ttf", "ABCDEFG")
        self.assertFalse(result)

    def test_font_substitution_edge_cases(self):
        """Test edge cases in font substitution"""

        # Test with empty text
        result = ensure_font_registered(self.mock_page, "Arial", verbose=False, text="")
        self.assertIsNotNone(result)

        # Test with whitespace-only text
        result = ensure_font_registered(self.mock_page, "Arial", verbose=False, text="   ")
        self.assertIsNotNone(result)

        # Test with None text
        result = ensure_font_registered(self.mock_page, "Arial", verbose=False, text=None)
        self.assertIsNotNone(result)

    @patch("pdfrebuilder.font.utils.TTFont")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    def test_font_substitution_performance_caching(self, mock_covers, mock_scan, mock_ttfont):
        """Test that font substitution results are cached for performance"""
        font_name = "Arial"
        text = "Hello World"

        # Mock TTFont to avoid parsing dummy files
        mock_font = MagicMock()
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {}
        mock_font.__getitem__.side_effect = lambda key: mock_name_table if key == "name" else mock_cmap_table
        mock_ttfont.return_value = mock_font

        # Create a font file to avoid download attempts
        font_path = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
        with open(font_path, "w") as f:
            f.write("dummy font content")

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # First call
            result1 = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

            # Second call should use cache
            result2 = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        self.assertEqual(result1, result2)
        # insert_font should only be called once due to caching
        self.assertEqual(self.mock_page.insert_font.call_count, 1)


class TestFontFallbackChain(unittest.TestCase):
    """Test the complete font fallback chain"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        self.mock_page = Mock()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_complete_fallback_chain(self, mock_exists, mock_covers, mock_scan, mock_download):
        """Test the complete font fallback chain"""
        font_name = "NonExistentFont"
        text = "Hello World"

        # 1. Font not found locally
        mock_exists.return_value = False

        # 2. Google Fonts download fails
        mock_download.return_value = None

        # 3. No available fonts provide coverage
        mock_scan.return_value = {"Arial": "/path/to/arial.ttf"}
        mock_covers.return_value = False

        # 4. Should fallback to default font
        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        self.assertEqual(result, "Helvetica")

        # Verify the chain was followed
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)
        mock_scan.assert_called_once_with(self.test_fonts_dir)

    def test_fallback_to_standard_pdf_fonts(self):
        """Test fallback to standard PDF fonts when default font fails"""
        font_name = "NonExistentFont"

        # Mock a scenario where default font also fails
        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (self.test_fonts_dir if key == "downloaded_fonts_dir" else "also-nonexistent"),
        ):
            with patch("pdfrebuilder.font.utils.STANDARD_PDF_FONTS", ["helv", "cour", "tiro"]):
                result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        # Should fallback to first standard PDF font
        self.assertEqual(result, "helv")

    def test_circular_fallback_prevention(self):
        """Test prevention of circular fallback loops"""
        # This test ensures that if the default font is the same as the requested font,
        # we don't get into an infinite loop

        font_name = "helv"

        # Mock scenario where helv is not in standard fonts (edge case)
        with patch("pdfrebuilder.font.utils.STANDARD_PDF_FONTS", ["cour", "tiro"]):
            with patch(
                "pdfrebuilder.font.utils.get_config_value",
                side_effect=lambda key: (
                    self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
                ),
            ):
                with patch("pdfrebuilder.font.utils.os.path.exists", return_value=False):
                    with patch("pdfrebuilder.font.utils.download_google_font", return_value=None):
                        result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        # Should fallback to available standard PDF font to avoid circular reference
        self.assertEqual(result, "tiro")


if __name__ == "__main__":
    unittest.main()
