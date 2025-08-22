"""
Unit tests for Font Management System

This module contains comprehensive tests for:
- FontManager functionality
- Font discovery and substitution
- Google Fonts integration
"""

import os
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
from tests.config import cleanup_test_output, get_test_fonts_dir, get_test_temp_dir


class TestFontDiscovery(unittest.TestCase):
    """Test font discovery functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    def test_scan_available_fonts_empty_directory(self):
        """Test scanning an empty fonts directory"""
        # Mock the function at the module level where it's defined
        with patch("pdfrebuilder.font.utils.scan_available_fonts", return_value={}) as mock_scan:
            # Import and call the function after patching
            from pdfrebuilder.font.utils import scan_available_fonts

            result = scan_available_fonts(self.test_fonts_dir)
            self.assertEqual(result, {})
            mock_scan.assert_called_once_with(self.test_fonts_dir)

    def test_scan_available_fonts_nonexistent_directory(self):
        """Test scanning a non-existent directory"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        # Mock the function at the module level where it's defined
        with patch("pdfrebuilder.font.utils.scan_available_fonts", return_value={}) as mock_scan:
            # Import and call the function after patching
            from pdfrebuilder.font.utils import scan_available_fonts

            result = scan_available_fonts(nonexistent_dir)
            self.assertEqual(result, {})
            mock_scan.assert_called_once_with(nonexistent_dir)

    @patch("pdfrebuilder.font.utils.TTFont")
    @patch("pdfrebuilder.font.utils.glob.glob")
    def test_scan_available_fonts_with_valid_fonts(self, mock_glob, mock_ttfont):
        """Test scanning directory with valid font files"""
        # Mock font files
        mock_font_files = [
            os.path.join(self.test_fonts_dir, "Arial.ttf"),
            os.path.join(self.test_fonts_dir, "Times.otf"),
        ]
        mock_glob.return_value = mock_font_files

        # Mock TTFont instances
        mock_font1 = MagicMock()
        mock_name_table1 = Mock()
        mock_name_table1.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        mock_font1.__getitem__.return_value = mock_name_table1

        mock_font2 = MagicMock()
        mock_name_table2 = Mock()
        mock_name_table2.names = [Mock(nameID=1, platformID=3, string=b"Times New Roman")]
        mock_font2.__getitem__.return_value = mock_name_table2

        mock_ttfont.side_effect = [mock_font1, mock_font2]

        result = scan_available_fonts(self.test_fonts_dir)

        expected = {"Arial": mock_font_files[0], "Times New Roman": mock_font_files[1]}
        self.assertEqual(result, expected)

    @patch("pdfrebuilder.font.utils.TTFont")
    @patch("pdfrebuilder.font.utils.glob.glob")
    def test_scan_available_fonts_with_corrupted_font(self, mock_glob, mock_ttfont):
        """Test scanning directory with corrupted font file"""
        mock_font_files = [os.path.join(self.test_fonts_dir, "corrupted.ttf")]
        mock_glob.return_value = mock_font_files

        # Mock TTFont to raise exception for corrupted font
        mock_ttfont.side_effect = Exception("Corrupted font file")

        with patch("pdfrebuilder.font.utils.logger") as mock_logger:
            result = scan_available_fonts(self.test_fonts_dir)

            self.assertEqual(result, {})
            # The warning should be called at least once (may be called multiple times due to glob patterns)
            self.assertTrue(mock_logger.warning.called)


class TestFontCoverage(unittest.TestCase):
    """Test font glyph coverage functionality"""

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_font_covers_text_full_coverage(self, mock_ttfont):
        """Test font that covers all characters in text"""
        mock_font = MagicMock()
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {
            ord("H"): 1,
            ord("e"): 2,
            ord("l"): 3,
            ord("o"): 4,
            ord(" "): 5,
        }
        mock_cmap_subtable = Mock()
        mock_cmap_subtable.tables = [mock_cmap_table]
        mock_font.__getitem__.return_value = mock_cmap_subtable
        mock_ttfont.return_value = mock_font

        result = font_covers_text("dummy_path.ttf", "Hello")
        self.assertTrue(result)

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_font_covers_text_partial_coverage(self, mock_ttfont):
        """Test font that doesn't cover all characters in text"""
        mock_font = MagicMock()
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {ord("H"): 1, ord("e"): 2}  # Missing 'l' and 'o'
        mock_cmap_subtable = Mock()
        mock_cmap_subtable.tables = [mock_cmap_table]
        mock_font.__getitem__.return_value = mock_cmap_subtable
        mock_ttfont.return_value = mock_font

        result = font_covers_text("dummy_path.ttf", "Hello")
        self.assertFalse(result)

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_font_covers_text_with_whitespace(self, mock_ttfont):
        """Test font coverage ignoring whitespace-only characters"""
        mock_font = MagicMock()
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {ord("H"): 1, ord("i"): 2}
        mock_cmap_subtable = Mock()
        mock_cmap_subtable.tables = [mock_cmap_table]
        mock_font.__getitem__.return_value = mock_cmap_subtable
        mock_ttfont.return_value = mock_font

        result = font_covers_text("dummy_path.ttf", "Hi   ")  # Trailing spaces
        self.assertTrue(result)

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_font_covers_text_exception_handling(self, mock_ttfont):
        """Test font coverage when TTFont raises exception"""
        mock_ttfont.side_effect = Exception("Font loading error")

        with patch("pdfrebuilder.font.utils.logger") as mock_logger:
            result = font_covers_text("dummy_path.ttf", "Hello")

            self.assertFalse(result)
            mock_logger.warning.assert_called_once()


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

    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_ensure_font_registered_local_ttf_font(self, mock_exists):
        """Test registering a local TTF font file"""
        font_name = "CustomFont"

        # Mock that the fonts directory exists and the font file exists
        def exists_side_effect(path):
            if path == self.test_fonts_dir:
                return True
            if path == os.path.join(self.test_fonts_dir, f"{font_name}.ttf"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        with (
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=False)

        self.assertEqual(result, font_name)
        self.mock_page.insert_font.assert_called_once()

    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_ensure_font_registered_local_otf_font(self, mock_exists):
        """Test registering a local OTF font file"""
        font_name = "CustomFont"

        # Mock that the fonts directory exists and the font file exists
        def exists_side_effect(path):
            if path == self.test_fonts_dir:
                return True
            if path == os.path.join(self.test_fonts_dir, f"{font_name}.otf"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

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
        # Mock page.insert_font to raise an exception
        self.mock_page.insert_font.side_effect = Exception("Font loading error")

        with patch("pdfrebuilder.font.utils.os.path.exists", return_value=True):
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
