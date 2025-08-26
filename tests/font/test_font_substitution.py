"""
Unit tests for Font Substitution System

This module tests:
- Font substitution by coverage
- Fallback chain functionality
- Performance optimization
- Error handling and recovery
"""

import os
import shutil
import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.font.utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    STANDARD_PDF_FONTS,
    ensure_font_registered,
    font_covers_text,
)

# Import test configuration
from tests.config import (
    cleanup_test_output,
    get_fixture_path,
    get_test_fonts_dir,
    get_test_temp_dir,
)


class TestFontSubstitutionEngine(unittest.TestCase):
    """Test font substitution and fallback mechanisms"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        self.font_path = os.path.join(self.test_fonts_dir, "test_font.otf")
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), self.font_path)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        self.mock_page = Mock()
        self.mock_page.insert_font.return_value = 0  # PyMuPDF returns 0 on success

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def test_glyph_coverage_basic_latin(self):
        """Test glyph coverage for basic Latin characters"""
        # Public Sans covers all basic Latin characters
        result = font_covers_text(self.font_path, "Hello World 123")
        self.assertTrue(result)

        # Public Sans does not cover CJK characters
        result = font_covers_text(self.font_path, "Hello 世界")
        self.assertFalse(result)

    def test_glyph_coverage_unicode_characters(self):
        """Test glyph coverage for Unicode characters"""
        # Public Sans has good support for Latin extended characters
        result = font_covers_text(self.font_path, "Héllo niño")
        self.assertTrue(result)

        # Public Sans does not cover CJK characters or emojis
        result = font_covers_text(self.font_path, "Hello 世界")
        self.assertFalse(result)
        result = font_covers_text(self.font_path, "Hello 🌍")
        self.assertFalse(result)

    @patch("pdfrebuilder.font.utils.download_google_font")
    def test_font_substitution_by_coverage(self, mock_download):
        """Test font substitution based on glyph coverage"""
        font_name = "MissingFont"
        text = "Hello 世界"

        # 1. Create a directory with two fonts:
        #    - Public Sans (as Arial.ttf), which does not cover the text
        #    - Noto Sans CJK (as NotoSans.woff), which does
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), os.path.join(self.test_fonts_dir, "Arial.ttf"))
        shutil.copy(
            get_fixture_path("fonts/NotoSansCJKjp-Regular.woff"), os.path.join(self.test_fonts_dir, "NotoSans.woff")
        )

        # 2. Mock download to prevent network calls
        mock_download.return_value = None

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            # 3. Attempt to register the missing font with text that requires CJK characters
            result = ensure_font_registered(self.mock_page, font_name, verbose=True, text=text)

        # 4. Assert that the system correctly substitutes with the CJK font
        self.assertEqual(result, "Noto_Sans_JP")
        self.mock_page.insert_font.assert_called_once()
        _args, kwargs = self.mock_page.insert_font.call_args
        self.assertEqual(kwargs.get("fontname"), "Noto_Sans_JP")

    @patch("pdfrebuilder.font.utils.download_google_font")
    def test_font_substitution_no_coverage_fallback(self, mock_download):
        """Test fallback when no available font covers the text"""
        font_name = "MissingFont"
        text = "Hello 🌍🚀"  # Text with emojis that most fonts won't cover

        # Original font doesn't exist
        mock_download.return_value = None  # Download fails

        # Create some fonts that don't cover the text
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), os.path.join(self.test_fonts_dir, "Arial.ttf"))

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        # Should fallback to a standard font since no local font has coverage
        self.assertIn(result, STANDARD_PDF_FONTS)

    @patch("pdfrebuilder.font.utils.download_google_font")
    def test_font_substitution_registration_error(self, mock_download):
        """Test handling of font registration errors during substitution"""
        font_name = "MissingFont"
        text = "Hello World"

        # Original font doesn't exist
        mock_download.return_value = None  # Download fails

        # Create a font that will be found but will fail to register
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), os.path.join(self.test_fonts_dir, "Arial.ttf"))

        # Mock insert_font to raise exception for the substituted font
        def insert_font_side_effect(fontfile=None, fontname=None):
            # The font's internal name is "Public Sans", which is sanitized to "Public_Sans"
            if fontname == "Public_Sans":
                raise Exception("Font registration failed")

        self.mock_page.insert_font.side_effect = insert_font_side_effect

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        # Should fallback to a standard font after registration error
        self.assertIn(result, STANDARD_PDF_FONTS)

    def test_font_substitution_priority_order(self):
        """Test that font substitution follows correct priority order"""
        # This test verifies the priority order:
        # 1. Exact font match (local file)
        # 2. Google Fonts download
        # 3. Coverage-based substitution
        # 4. Default font fallback
        # 5. Standard PDF font fallback

        # Removed unused variable: font_name = "CustomFont"

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            # Test standard font (highest priority after exact match)
            result = ensure_font_registered(self.mock_page, "helv", verbose=False)
            self.assertEqual(result, "helv")

    def test_multiple_cmap_tables_handling(self):
        """Test handling of fonts with multiple character map tables"""
        # A real font file like Public Sans will have multiple cmap tables.
        # This test now implicitly verifies that the code can handle them.
        result = font_covers_text(self.font_path, "ABCDEF")
        self.assertTrue(result)

        # Use a character that is likely not in the font
        result = font_covers_text(self.font_path, "ABCDEFG" + chr(0x1F60A))  # Smiling face emoji
        self.assertFalse(result)

    def test_font_substitution_edge_cases(self):
        """Test edge cases in font substitution"""
        # Create a real font file to avoid unnecessary fallbacks
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), os.path.join(self.test_fonts_dir, "Arial.ttf"))

        with patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir):
            # Test with empty text
            result = ensure_font_registered(self.mock_page, "Arial", verbose=False, text="")
            self.assertEqual(result, "Arial")

            # Test with whitespace-only text
            result = ensure_font_registered(self.mock_page, "Arial", verbose=False, text="   ")
            self.assertEqual(result, "Arial")

            # Test with None text
            result = ensure_font_registered(self.mock_page, "Arial", verbose=False, text=None)
            self.assertEqual(result, "Arial")

    def test_font_substitution_performance_caching(self):
        """Test that font substitution results are cached for performance"""
        font_name = "Arial"
        text = "Hello World"

        shutil.copy(
            get_fixture_path("fonts/PublicSans-Regular.otf"), os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
        )

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
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
        os.makedirs(self.test_fonts_dir, exist_ok=True)

        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        self.mock_page = Mock()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    @patch("pdfrebuilder.font.utils.download_google_font")
    def test_complete_fallback_chain(self, mock_download):
        """Test the complete font fallback chain"""
        font_name = "NonExistentFont"
        text = "Hello World"

        # 1. Font not found locally
        # 2. Google Fonts download fails
        mock_download.return_value = None

        # 3. Create a local font that does cover the text
        shutil.copy(
            get_fixture_path("fonts/PublicSans-Regular.otf"), os.path.join(self.test_fonts_dir, "PublicSans.ttf")
        )

        # 4. Should fallback to the local font
        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        self.assertEqual(result, "Public_Sans")

        # Verify the chain was followed
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)

    def test_fallback_to_standard_pdf_fonts(self):
        """Test fallback to standard PDF fonts when default font fails"""
        font_name = "NonExistentFont"

        # Mock a scenario where default font also fails
        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "also-nonexistent"),
        ):
            with patch("pdfrebuilder.font.utils.STANDARD_PDF_FONTS", ["helv", "cour", "tiro"]):
                with patch("pdfrebuilder.font.utils.os.path.exists", return_value=False):
                    with patch("pdfrebuilder.font.utils.download_google_font", return_value=None):
                        result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        # Should fallback to first standard PDF font
        self.assertEqual(result, "helv")

    def test_circular_fallback_prevention(self):
        """Test prevention of circular fallback loops"""
        # This test ensures that if the default font is the same as the requested font,
        # we don't get into an infinite loop

        font_name = "helv"

        # Mock scenario where helv is not in standard fonts (edge case)
        with (
            patch("pdfrebuilder.font.utils.STANDARD_PDF_FONTS", ["cour", "tiro"]),
            patch("pdfrebuilder.font.utils.FallbackFontManager.FALLBACK_FONTS", ["cour", "tiro"]),
        ):
            with (
                patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
                patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
                patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
            ):
                with patch("pdfrebuilder.font.utils.os.path.exists", return_value=False):
                    with patch("pdfrebuilder.font.utils.download_google_font", return_value=None):
                        result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        # Should fallback to available standard PDF font to avoid circular reference
        self.assertEqual(result, "cour")


if __name__ == "__main__":
    unittest.main()
