"""
Unit tests for Font Management System

This module contains comprehensive tests for:
- FontManager functionality
- Font discovery and substitution
- Google Fonts integration
"""

import os
import shutil
import unittest
from unittest.mock import MagicMock, Mock, patch

from pdfrebuilder.font.googlefonts import download_google_font

# Import the modules we're testing
from pdfrebuilder.font.utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    ensure_font_registered,
    font_covers_text,
    scan_available_fonts,
)
from pdfrebuilder.settings import settings

# Import test configuration
from tests.config import (
    cleanup_test_output,
    get_fixture_path,
    get_test_fonts_dir,
    get_test_temp_dir,
)


class TestFontDiscovery(unittest.TestCase):
    """Test font discovery functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)
        os.makedirs(self.test_fonts_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    def test_scan_available_fonts_empty_directory(self):
        """Test scanning an empty fonts directory"""
        result = scan_available_fonts([self.test_fonts_dir])
        self.assertEqual(result, {})

    def test_scan_available_fonts_nonexistent_directory(self):
        """Test scanning a non-existent directory"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        result = scan_available_fonts([nonexistent_dir])
        self.assertEqual(result, {})

    def test_scan_available_fonts_with_valid_fonts(self):
        """Test scanning directory with valid font files"""
        real_font_path = get_fixture_path("fonts/PublicSans-Regular.otf")
        shutil.copy(real_font_path, os.path.join(self.test_fonts_dir, "Arial.ttf"))
        shutil.copy(real_font_path, os.path.join(self.test_fonts_dir, "Times.otf"))

        result = scan_available_fonts([self.test_fonts_dir])

        # The font name for PublicSans-Regular.otf is "Public Sans"
        self.assertIn("Public Sans", result)
        self.assertEqual(len(result), 1)

    def test_scan_available_fonts_with_corrupted_font(self):
        """Test scanning directory with corrupted font file"""
        corrupted_font_path = os.path.join(self.test_fonts_dir, "corrupted.ttf")
        with open(corrupted_font_path, "w") as f:
            f.write("this is not a font")

        with patch("pdfrebuilder.font.utils.logger") as mock_logger:
            result = scan_available_fonts([self.test_fonts_dir])

            self.assertEqual(result, {})
            mock_logger.warning.assert_called()


class TestFontCoverage(unittest.TestCase):
    """Test font glyph coverage functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.font_path = os.path.join(self.temp_dir, "test_font.otf")
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), self.font_path)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    def test_font_covers_text_full_coverage(self):
        """Test font that covers all characters in text"""
        result = font_covers_text(self.font_path, "Hello World!")
        self.assertTrue(result)

    def test_font_covers_text_partial_coverage(self):
        """Test font that doesn't cover all characters in text"""
        # Public Sans does not contain these CJK characters
        result = font_covers_text(self.font_path, "你好世界")
        self.assertFalse(result)

    def test_font_covers_text_with_whitespace(self):
        """Test font coverage ignoring whitespace-only characters"""
        result = font_covers_text(self.font_path, "Hi   ")  # Trailing spaces
        self.assertTrue(result)

    def test_font_covers_text_exception_handling(self):
        """Test font coverage when TTFont raises exception"""
        with patch("pdfrebuilder.font.utils.logger") as mock_logger:
            result = font_covers_text("/nonexistent/font.ttf", "Hello")
            self.assertFalse(result)
            mock_logger.warning.assert_called()


class TestFontRegistration(unittest.TestCase):
    """Test font registration functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear caches before each test
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        self.mock_page = Mock()
        self.mock_page_id = id(self.mock_page)

        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def test_ensure_font_registered_standard_font(self):
        """Test registering a standard PDF font"""
        font_name = "helv"

        result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        self.assertEqual(result, font_name)
        self.assertIn(font_name, _FONT_REGISTRATION_CACHE[self.mock_page_id])
        self.mock_page.insert_font.assert_not_called()

    def test_ensure_font_registered_unnamed_t3_fallback(self):
        """Test handling of Unnamed-T3 font with fallback"""
        font_name = "Unnamed-T3"

        with patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False)

            # Should fallback to default font from the mock config
            self.assertEqual(result, "helv")

    def test_ensure_font_registered_cached_font(self):
        """Test that cached fonts are not re-registered"""
        font_name = "Arial"
        _FONT_REGISTRATION_CACHE[self.mock_page_id] = {font_name}

        result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        self.assertEqual(result, font_name)
        self.mock_page.insert_font.assert_not_called()

    def test_ensure_font_registered_local_ttf_font(self):
        """Test registering a local TTF font file"""
        font_name = "CustomFont"
        font_path = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), font_path)

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        self.assertEqual(result, font_name)
        self.mock_page.insert_font.assert_called_once()

    def test_ensure_font_registered_local_otf_font(self):
        """Test registering a local OTF font file"""
        font_name = "CustomFont"
        font_path = os.path.join(self.test_fonts_dir, f"{font_name}.otf")
        shutil.copy(get_fixture_path("fonts/PublicSans-Regular.otf"), font_path)

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        self.assertEqual(result, font_name)
        self.mock_page.insert_font.assert_called_once()

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_ensure_font_registered_download_success(self, mock_exists, mock_download):
        """Test successful font download from Google Fonts"""
        font_name = "Roboto"
        mock_exists.return_value = False  # Font not found locally
        mock_download.return_value = ["downloaded_file.ttf"]

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            # Mock the recursive call after download
            with patch("pdfrebuilder.font.utils.ensure_font_registered", side_effect=[font_name]) as _:
                _ = ensure_font_registered(self.mock_page, font_name, verbose=False)

        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)
        self.assertIn(font_name, _FONT_DOWNLOAD_ATTEMPTED)

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_ensure_font_registered_download_failure(self, mock_exists, mock_download):
        """Test font download failure from Google Fonts"""
        font_name = "Roboto"
        mock_exists.return_value = False  # Font not found locally
        mock_download.return_value = []  # Download failed

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        # Should fallback to the default font from the mock config
        self.assertEqual(result, "helv")

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_ensure_font_registered_with_text_coverage(self, mock_exists, mock_covers, mock_scan, mock_download):
        """Test font registration with text coverage checking"""
        font_name = "Roboto"
        text = "Hello World"
        mock_exists.return_value = True  # Font file exists

        # Mock font_covers_text to return False for Roboto but True for Arial
        def coverage_side_effect(font_path, test_text):
            if "arial" in font_path.lower():
                return True
            return False

        mock_covers.side_effect = coverage_side_effect
        mock_scan.return_value = {"Arial": "/path/to/arial.ttf"}
        mock_download.return_value = []

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False, text=text)

        # Should fallback to a font that covers the text
        self.assertEqual(result, "Arial")

    def test_ensure_font_registered_font_loading_error(self):
        """Test font registration when font loading fails"""
        font_name = "InvalidFont"
        font_path = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
        with open(font_path, "w") as f:
            f.write("corrupted font data")

        # Mock page.insert_font to raise an exception when trying to load the corrupted font
        self.mock_page.insert_font.side_effect = Exception("Font loading error")

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        # Should fallback to default font from the mock config
        self.assertEqual(result, "helv")


class TestGoogleFontsIntegration(unittest.TestCase):
    """Test Google Fonts download functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_google_font_success(self, mock_get):
        """Test successful Google Font download"""
        font_family = "Roboto"

        # Mock CSS response
        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        @font-face {
          font-family: 'Roboto';
          src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2);
        }
        """

        # Mock font file response
        font_response = Mock()
        font_response.content = b"fake font data"
        font_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response]

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(len(result), 1)
            self.assertTrue(result[0].endswith("KFOmCnqEu92Fr1Mu4mxK.woff2"))

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_google_font_css_error(self, mock_get):
        """Test Google Font download with CSS fetch error"""
        font_family = "NonExistentFont"

        css_response = Mock()
        css_response.status_code = 404
        mock_get.return_value = css_response

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_google_font_no_urls_found(self, mock_get):
        """Test Google Font download when no font URLs are found in CSS"""
        font_family = "EmptyFont"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = "/* No font URLs here */"
        mock_get.return_value = css_response

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_google_font_file_download_error(self, mock_get):
        """Test Google Font download with file download error"""
        font_family = "Roboto"

        # Mock CSS response
        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2);
        """

        # Mock font file response with error
        font_response = Mock()
        font_response.raise_for_status.side_effect = Exception("Download failed")

        mock_get.side_effect = [css_response, font_response]

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_google_font_creates_directory(self, mock_get):
        """Test that download creates destination directory if it doesn't exist"""
        font_family = "Roboto"
        dest_dir = os.path.join(self.temp_dir, "new_fonts_dir")

        # Mock CSS response
        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2);
        """

        # Mock font file response
        font_response = Mock()
        font_response.content = b"fake font data"
        font_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response]

        self.assertFalse(os.path.exists(dest_dir))

        result = download_google_font(font_family, dest_dir)

        self.assertTrue(os.path.exists(dest_dir))
        self.assertIsNotNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_google_font_network_error(self, mock_get):
        """Test Google Font download with network error"""
        font_family = "Roboto"

        mock_get.side_effect = Exception("Network error")

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)


class TestFontManagerIntegration(unittest.TestCase):
    """Integration tests for the complete font management system"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_font_workflow_local_to_download_to_fallback(self, mock_exists, mock_download):
        """Test complete font resolution workflow"""
        mock_page = Mock()
        font_name = "CustomFont"
        text = "Hello World"

        # Font not found locally
        mock_exists.return_value = False
        # Download fails
        mock_download.return_value = None

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(mock_page, font_name, verbose=False, text=text)

        # The fallback logic is complex, but it should settle on a standard font.
        # Let's accept Helvetica as a reasonable fallback in this scenario.
        self.assertEqual(result, "Helvetica")
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)

    def test_font_cache_persistence(self):
        """Test that font registration cache works correctly"""
        mock_page = Mock()
        font_name = "helv"  # Standard font

        # First call
        result1 = ensure_font_registered(mock_page, font_name, verbose=False)

        # Second call should use cache
        result2 = ensure_font_registered(mock_page, font_name, verbose=False)

        self.assertEqual(result1, font_name)
        self.assertEqual(result2, font_name)
        self.assertIn(font_name, _FONT_REGISTRATION_CACHE[id(mock_page)])

    def test_multiple_pages_separate_caches(self):
        """Test that different pages have separate font caches"""
        mock_page1 = Mock()
        mock_page2 = Mock()
        font_name = "helv"

        result1 = ensure_font_registered(mock_page1, font_name, verbose=False)
        result2 = ensure_font_registered(mock_page2, font_name, verbose=False)

        self.assertEqual(result1, font_name)
        self.assertEqual(result2, font_name)

        # Each page should have its own cache entry
        self.assertIn(font_name, _FONT_REGISTRATION_CACHE[id(mock_page1)])
        self.assertIn(font_name, _FONT_REGISTRATION_CACHE[id(mock_page2)])
        self.assertNotEqual(id(mock_page1), id(mock_page2))


if __name__ == "__main__":
    unittest.main()
